/**
 * API Key 鉴权中间件
 */

const config = require('../config/default');

/**
 * 从请求中提取 API Key
 * 支持：Header (X-API-Key) / Query (api_key)
 */
function extractKey(ctx) {
  return (
    ctx.get(config.API_KEY_HEADER) ||
    ctx.query.api_key ||
    ctx.query.apiKey
  );
}

/**
 * 验证 API Key 是否合法
 */
function validateKey(key) {
  if (!key) return { valid: false, reason: 'API Key 为空' };
  const appId = Object.keys(config.API_KEYS).find(id => config.API_KEYS[id] === key);
  if (!appId) return { valid: false, reason: '无效的 API Key' };
  return { valid: true, appId };
}

/**
 * 鉴权中间件
 * 可配置为全局生效或按路由生效
 */
function auth(options = {}) {
  const { required = true } = options;

  return async (ctx, next) => {
    const key = extractKey(ctx);

    if (!required && !key) {
      // 不强制要求时，跳过鉴权
      ctx.state.auth = { authenticated: false };
      await next();
      return;
    }

    const result = validateKey(key);

    if (!result.valid) {
      ctx.status = 401;
      ctx.body = {
        code: 401,
        message: `鉴权失败: ${result.reason}`,
        data: null,
        hint: '请在请求头中携带 X-API-Key 或通过 query 参数 api_key 传入有效的 API Key',
      };
      return;
    }

    // 鉴权通过，写入上下文
    ctx.state.auth = {
      authenticated: true,
      appId: result.appId,
    };

    await next();
  };
}

/**
 * 生成 API Key（管理员用）
 */
function generateKey(appId) {
  const crypto = require('crypto');
  const secret = config.API_KEYS[appId];
  if (!secret) return null;
  return secret;
}

/**
 * 列出所有已注册的应用（不含 key，仅返回 appId 列表）
 */
function listApps() {
  return Object.keys(config.API_KEYS);
}

module.exports = { auth, validateKey, extractKey, generateKey, listApps };
