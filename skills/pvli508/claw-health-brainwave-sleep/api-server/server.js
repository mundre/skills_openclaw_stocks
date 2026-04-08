/**
 * 睡眠脑波音频 API 服务
 * 支持本地音频文件 + HTTP 远程音频
 *
 * 启动：node server.js
 * 默认端口：3092
 */

const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const cors = require('@koa/cors');
const path = require('path');
const fs = require('fs');
const send = require('koa-send');

const { AudioService } = require('./services/audioService');
const { ProfileService } = require('./services/profileService');

const PORT = process.env.PORT || 3092;
const HOST = process.env.HOST || '0.0.0.0';

// 本地音频目录（Windows / Unix 通用）
const AUDIO_BASE_DIR = process.env.AUDIO_BASE_DIR ||
  (process.platform === 'win32'
    ? 'C:\\Users\\龚文瀚\\Desktop\\sleepAudio'
    : '/Users/username/sleepAudio');

// -------- 初始化 --------
const app = new Koa();
const router = new Router();

// 服务实例（单例）
const audioService = new AudioService();
const profileService = new ProfileService();

// -------- 中间件 --------
app.use(cors({
  origin: '*',
  allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowHeaders: ['Content-Type', 'Authorization', 'X-User-Id'],
}));

app.use(bodyParser());

// 请求日志
app.use(async (ctx, next) => {
  const start = Date.now();
  await next();
  const ms = Date.now() - start;
  console.log(`${ctx.method} ${ctx.url} - ${ctx.status} - ${ms}ms`);
});

// 全局错误处理
app.use(async (ctx, next) => {
  try {
    await next();
  } catch (err) {
    ctx.status = err.status || 500;
    ctx.body = {
      code: ctx.status,
      message: err.message || '服务器内部错误',
      data: null,
    };
    if (ctx.status === 500) {
      console.error('Unhandled Error:', err);
    }
  }
});

// -------- 静态音频流服务 --------

/**
 * GET /audio-stream/:audioId
 * 以流媒体方式播放本地音频文件
 * 小程序 / APP 可直接传入此 URL 进行播放
 */
router.get('/audio-stream/:audioId', async (ctx) => {
  const { audioId } = ctx.params;
  const audioInfo = audioService.getAudioInfo(audioId);

  if (!audioInfo) {
    ctx.status = 404;
    ctx.body = { code: 404, message: `音频不存在: ${audioId}`, data: null };
    return;
  }

  const localFilePath = audioInfo.file_path;

  // 验证文件是否存在
  if (!fs.existsSync(localFilePath)) {
    ctx.status = 404;
    ctx.body = { code: 404, message: `音频文件未找到: ${localFilePath}`, data: null };
    return;
  }

  const stat = fs.statSync(localFilePath);
  const fileSize = stat.size;
  const range = ctx.request.headers.range;

  ctx.set('Content-Type', 'audio/mpeg');
  ctx.set('Accept-Ranges', 'bytes');
  ctx.set('Access-Control-Allow-Origin', '*');
  ctx.set('Content-Length', fileSize);
  ctx.set('Cache-Control', 'public, max-age=3600');

  if (range) {
    // 支持范围请求（拖动播放）
    const parts = range.replace(/bytes=/, '').split('-');
    const start = parseInt(parts[0], 10);
    const end = parts[1] ? parseInt(parts[1], 10) : fileSize - 1;
    const chunkSize = end - start + 1;

    ctx.status = 206;
    ctx.set('Content-Range', `bytes ${start}-${end}/${fileSize}`);
    ctx.set('Content-Length', chunkSize);

    ctx.body = fs.createReadStream(localFilePath, { start, end });
  } else {
    // 完整文件
    ctx.status = 200;
    ctx.body = fs.createReadStream(localFilePath);
  }
});

/**
 * GET /audio-stream/:audioId/info
 * 获取指定音频的流媒体地址信息
 */
router.get('/audio-stream/:audioId/info', async (ctx) => {
  const { audioId } = ctx.params;
  const audioInfo = audioService.getAudioInfo(audioId);

  if (!audioInfo) {
    ctx.status = 404;
    ctx.body = { code: 404, message: `音频不存在: ${audioId}`, data: null };
    return;
  }

  const streamUrl = `http://${HOST === '0.0.0.0' ? 'localhost' : HOST}:${PORT}/audio-stream/${audioId}`;

  ctx.body = {
    code: 0,
    message: 'success',
    data: {
      ...audioInfo,
      streamUrl,
    },
  };
});

// -------- 路由定义 --------

// 健康检查
router.get('/health', (ctx) => {
  ctx.body = {
    code: 0,
    message: 'ok',
    data: {
      service: 'sleep-brainwave-api',
      version: '1.0.0',
      audioSourceMode: 'LOCAL',
      audioBaseDir: AUDIO_BASE_DIR,
      timestamp: new Date().toISOString(),
    },
  };
});

// ---- 音频相关 ----

/**
 * GET /api/audio/list
 * 获取音频库清单（支持过滤）
 */
router.get('/api/audio/list', (ctx) => {
  const { subtype, scene, duration, severity, page = 1, pageSize = 20 } = ctx.query;

  const filters = {};
  if (subtype) filters.sleep_subtype_code = subtype;
  if (scene) filters.use_scene = scene;
  if (duration) filters.duration = parseInt(duration);
  if (severity) filters.severity = severity;

  const result = audioService.listAudio(filters, parseInt(page), parseInt(pageSize));

  // 补充流媒体地址
  const hostPrefix = `http://${HOST === '0.0.0.0' ? 'localhost' : HOST}:${PORT}`;
  result.items = result.items.map(item => ({
    ...item,
    streamUrl: `${hostPrefix}/audio-stream/${item.audioId}`,
  }));

  ctx.body = {
    code: 0,
    message: 'success',
    data: result,
  };
});

/**
 * GET /api/audio/scenes
 * 获取所有可用场景列表
 */
router.get('/api/audio/scenes', (ctx) => {
  const scenes = audioService.getAvailableScenes();
  ctx.body = { code: 0, message: 'success', data: scenes };
});

/**
 * GET /api/audio/subtypes
 * 获取所有可用睡眠亚型列表
 */
router.get('/api/audio/subtypes', (ctx) => {
  const subtypes = audioService.getAvailableSubtypes();
  ctx.body = { code: 0, message: 'success', data: subtypes };
});

/**
 * GET /api/audio/match
 * 根据条件匹配最佳音频
 */
router.get('/api/audio/match', (ctx) => {
  const { subtype, scene, duration, severity, userId } = ctx.query;

  if (!subtype) {
    ctx.status = 400;
    ctx.body = { code: 400, message: '缺少必填参数：subtype', data: null };
    return;
  }

  let finalSeverity = severity;
  if (userId && !severity) {
    const profile = profileService.getProfile(userId);
    if (profile && profile.severity) finalSeverity = profile.severity;
  }

  const matchResult = audioService.matchAudio({
    subtype,
    scene: scene || null,
    duration: duration ? parseInt(duration) : null,
    severity: finalSeverity || null,
  });

  if (matchResult) {
    const hostPrefix = `http://${HOST === '0.0.0.0' ? 'localhost' : HOST}:${PORT}`;
    matchResult.streamUrl = `${hostPrefix}/audio-stream/${matchResult.audioId}`;
  }

  ctx.body = {
    code: 0,
    message: matchResult ? 'success' : '未找到匹配的音频',
    data: matchResult,
  };
});

/**
 * GET /api/audio/:audioId/url
 * 获取音频地址信息（本地路径 + 流媒体地址）
 */
router.get('/api/audio/:audioId/url', (ctx) => {
  const { audioId } = ctx.params;
  const audioInfo = audioService.getAudioInfo(audioId);

  if (!audioInfo) {
    ctx.status = 404;
    ctx.body = { code: 404, message: `音频不存在: ${audioId}`, data: null };
    return;
  }

  const hostPrefix = `http://${HOST === '0.0.0.0' ? 'localhost' : HOST}:${PORT}`;

  ctx.body = {
    code: 0,
    message: 'success',
    data: {
      audioId,
      filename: audioInfo.filename,
      localPath: audioInfo.file_path,
      streamUrl: `${hostPrefix}/audio-stream/${audioId}`,
      duration: audioInfo.duration,
      sleepSubtype: audioInfo.sleepSubtype,
    },
  };
});

/**
 * GET /api/audio/:audioId/info
 * 获取音频详细信息
 */
router.get('/api/audio/:audioId/info', (ctx) => {
  const { audioId } = ctx.params;
  const info = audioService.getAudioInfo(audioId);

  if (!info) {
    ctx.status = 404;
    ctx.body = { code: 404, message: `音频不存在: ${audioId}`, data: null };
    return;
  }

  const hostPrefix = `http://${HOST === '0.0.0.0' ? 'localhost' : HOST}:${PORT}`;

  ctx.body = {
    code: 0,
    message: 'success',
    data: {
      ...info,
      streamUrl: `${hostPrefix}/audio-stream/${audioId}`,
    },
  };
});

// ---- 用户画像相关 ----

/**
 * GET /api/profile/:userId
 * 获取用户睡眠画像
 */
router.get('/api/profile/:userId', (ctx) => {
  const { userId } = ctx.params;
  ctx.body = { code: 0, message: 'success', data: profileService.getProfile(userId) };
});

/**
 * POST /api/profile
 * 创建或更新用户睡眠画像
 */
router.post('/api/profile', (ctx) => {
  const body = ctx.request.body;

  if (!body || !body.userId) {
    ctx.status = 400;
    ctx.body = { code: 400, message: '缺少必填参数：userId', data: null };
    return;
  }

  profileService.updateProfile(body.userId, {
    disorderSubtype: body.disorderSubtype,
    severity: body.severity,
    ageGroup: body.ageGroup,
    gender: body.gender,
    comorbidity: body.comorbidity,
  });

  ctx.body = {
    code: 0,
    message: 'success',
    data: profileService.getProfile(body.userId),
  };
});

/**
 * GET /api/recommend/:userId
 * 根据用户画像智能推荐音频
 */
router.get('/api/recommend/:userId', (ctx) => {
  const { userId } = ctx.params;
  const { scene } = ctx.query;
  const profile = profileService.getProfile(userId);

  const hostPrefix = `http://${HOST === '0.0.0.0' ? 'localhost' : HOST}:${PORT}`;

  if (!profile) {
    const result = audioService.matchAudio({ subtype: 'general', scene: scene || '睡前', duration: null, severity: '轻度' });
    if (result) result.streamUrl = `${hostPrefix}/audio-stream/${result.audioId}`;
    ctx.body = { code: 0, message: '无用户画像，返回通用推荐', data: { profile: null, audio: result } };
    return;
  }

  const result = audioService.matchAudio({
    subtype: profile.disorderSubtype || 'general',
    scene: scene || profile.scene || null,
    duration: null,
    severity: profile.severity || null,
  });

  if (result) result.streamUrl = `${hostPrefix}/audio-stream/${result.audioId}`;

  ctx.body = { code: 0, message: 'success', data: { profile, audio: result } };
});

// -------- 启动 --------
app.use(router.routes());
app.use(router.allowedMethods());

app.listen(PORT, HOST, () => {
  console.log(`🌙 睡眠脑波 API 服务已启动`);
  console.log(`   地址: http://${HOST === '0.0.0.0' ? 'localhost' : HOST}:${PORT}`);
  console.log(`   音频源: ${AUDIO_BASE_DIR}`);
  console.log(`\n可用接口:`);
  console.log(`  GET  /health                        健康检查`);
  console.log(`  GET  /audio-stream/:audioId         流媒体播放（直接可播放）`);
  console.log(`  GET  /audio-stream/:audioId/info   流媒体地址信息`);
  console.log(`  GET  /api/audio/list                音频清单（支持过滤）`);
  console.log(`  GET  /api/audio/scenes              场景列表`);
  console.log(`  GET  /api/audio/subtypes            亚型列表`);
  console.log(`  GET  /api/audio/match               智能匹配音频`);
  console.log(`  GET  /api/audio/:id/url              音频地址信息`);
  console.log(`  GET  /api/audio/:id/info            音频详细信息`);
  console.log(`  GET  /api/profile/:userId           用户画像`);
  console.log(`  POST /api/profile                   创建/更新画像`);
  console.log(`  GET  /api/recommend/:userId          智能推荐`);
});

module.exports = { app };
