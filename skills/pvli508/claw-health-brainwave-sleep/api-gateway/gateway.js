/**
 * OpenClaw Gateway - 统一接入层
 *
 * 功能：
 *  - 多 Skill 路由分发（/sleep/*, /health/*）
 *  - API Key 鉴权
 *  - 请求限流
 *  - 访问日志
 *  - 统一错误处理
 *
 * 启动：node gateway.js
 * 默认端口：3092
 */

const Koa = require('koa');
const bodyParser = require('koa-bodyparser');
const cors = require('@koa/cors');

const config = require('./config/default');
const { auth } = require('./middleware/auth');
const { rateLimit } = require('./middleware/rateLimit');
const { logger, errorLogger } = require('./middleware/logger');

// 路由
const sleepRoutes = require('./routes/sleep');
const healthRoutes = require('./routes/health');

// ---- 初始化 App ----
const app = new Koa();

// ---- 基础中间件 ----

// CORS
app.use(cors({
  origin: (ctx) => {
    const origin = ctx.request.headers.origin;
    if (config.CORS_ORIGINS.includes('*') || config.CORS_ORIGINS.includes(origin)) {
      return origin || '*';
    }
    return config.CORS_ORIGINS[0];
  },
  allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowHeaders: ['Content-Type', 'Authorization', 'X-API-Key', 'X-User-Id', 'X-App-Id'],
  credentials: true,
}));

// 请求体解析
app.use(bodyParser({
  enableTypes: ['json', 'form'],
  jsonLimit: '1mb',
}));

// ---- 日志（最早） ----
app.use(errorLogger());
app.use(logger());

// ---- 全局错误处理 ----
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    ctx.status = err.status || 500;
    ctx.body = {
      code: ctx.status,
      message: err.expose ? err.message : '服务器内部错误',
      data: null,
    };
    if (ctx.status === 500) {
      console.error('[Gateway Error]', err);
    }
  }
});

// ---- 路由：公开接口（无需鉴权）----
const publicRouter = new (require('@koa/router'))();

// 健康检查（公开）
publicRouter.get('/health', (ctx) => {
  ctx.body = {
    code: 0,
    message: 'ok',
    data: {
      service: 'OpenClaw Gateway',
      version: '1.0.0',
      timestamp: new Date().toISOString(),
      skills: Object.entries(config.SKILLS).map(([key, v]) => ({
        name: key,
        displayName: v.name,
        version: v.version,
      })),
    },
  };
});

// 根路径
publicRouter.get('/', (ctx) => {
  ctx.body = {
    code: 0,
    message: 'OpenClaw Gateway is running',
    data: {
      gateway: 'OpenClaw Unified API Gateway',
      version: '1.0.0',
      docs: '/docs',
      health: '/health',
    },
  };
});

// API Key 列表（管理员接口，仅开发环境可见）
if (config.NODE_ENV !== 'production') {
  publicRouter.get('/admin/apps', (ctx) => {
    const { listApps } = require('./middleware/auth');
    ctx.body = {
      code: 0,
      message: 'success',
      data: {
        hint: '仅开发环境可见，生产环境请通过环境变量注入真实 API Keys',
        apps: listApps(),
      },
    };
  });
}

// ---- 路由：需鉴权的接口 ----

// 睡眠脑波路由（/sleep/*）
app.use(sleepRoutes.routes());
app.use(sleepRoutes.allowedMethods());

// 健康管理路由（/health/*）
app.use(healthRoutes.routes());
app.use(healthRoutes.allowedMethods());

// 公开路由（放在最后，避免被 skill 路由拦截）
app.use(publicRouter.routes());
app.use(publicRouter.allowedMethods());

// ---- 404 处理 ----
app.use(async (ctx) => {
  if (!ctx.body) {
    ctx.status = 404;
    ctx.body = {
      code: 404,
      message: `接口不存在: ${ctx.method} ${ctx.url}`,
      data: null,
      hint: '请参考 API 文档: /docs',
      availableRoutes: [
        'GET  /health',
        'GET  /sleep/audio/list',
        'GET  /sleep/audio/match?subtype=xxx',
        'GET  /sleep/audio/stream/:audioId',
        'GET  /sleep/profile/:userId',
        'POST /sleep/profile',
        'GET  /sleep/recommend/:userId',
        'GET  /health/status',
      ],
    };
  }
});

// ---- 启动 ----
const PORT = config.PORT;
const HOST = config.HOST;

app.listen(PORT, HOST, () => {
  console.log('');
  console.log('╔════════════════════════════════════════════╗');
  console.log('║    🌙  OpenClaw Gateway  已启动             ║');
  console.log('╠════════════════════════════════════════════╣');
  console.log(`║  本地地址:  http://localhost:${PORT}              ║`);
  console.log(`║  局域网:   http://192.168.3.18:${PORT}         ║`);
  console.log('╠════════════════════════════════════════════╣');
  console.log('║  已注册技能:                                 ║');
  Object.entries(config.SKILLS).forEach(([key, v]) => {
    console.log(`║    /${key.padEnd(10)} ${v.name} (v${v.version})    ║`);
  });
  console.log('╠════════════════════════════════════════════╣');
  console.log('║  限流:  每 60 秒最多 100 次请求/app         ║');
  console.log(`║  环境:  ${config.NODE_ENV.padEnd(36)}║`);
  console.log('╚════════════════════════════════════════════╝');
  console.log('');
  console.log('接口清单:');
  console.log('  GET  /health                       健康检查（公开）');
  console.log('  GET  /                             根路径信息（公开）');
  console.log('');
  console.log('  [睡眠脑波 Skill]');
  console.log('  GET  /sleep/audio/list             音频清单');
  console.log('  GET  /sleep/audio/scenes           场景列表');
  console.log('  GET  /sleep/audio/subtypes         亚型列表');
  console.log('  GET  /sleep/audio/match             智能匹配音频');
  console.log('  GET  /sleep/audio/:id/info         音频详情');
  console.log('  GET  /sleep/audio/:id/url          音频地址');
  console.log('  GET  /sleep/audio/stream/:audioId  流媒体播放（可直接播放）');
  console.log('  GET  /sleep/profile/:userId        用户画像');
  console.log('  POST /sleep/profile                更新画像');
  console.log('  GET  /sleep/recommend/:userId      智能推荐');
  console.log('');
  console.log('  [健康管理 Skill - 即将上线]');
  console.log('  GET  /health/status                 服务状态');
  console.log('  GET  /health/bp/record/:userId     血压记录');
  console.log('  POST /health/bp/record             上报血压');
  console.log('  GET  /health/health-tips            健康贴士');
  console.log('');
});

module.exports = { app };
