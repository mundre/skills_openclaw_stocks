/**
 * 限流中间件
 * 基于内存滑动窗口算法实现
 */

const config = require('../config/default');

class SlidingWindow {
  constructor(windowMs, maxRequests) {
    this.windowMs = windowMs;
    this.maxRequests = maxRequests;
    this.store = new Map(); // key → [timestamp1, timestamp2, ...]
  }

  /**
   * 清理过期记录
   */
  _cleanup(key) {
    const now = Date.now();
    const cutoff = now - this.windowMs;
    const timestamps = this.store.get(key) || [];
    const valid = timestamps.filter(t => t > cutoff);
    this.store.set(key, valid);
    return valid;
  }

  /**
   * 检查是否允许请求
   * @returns { allowed: boolean, remaining: number, reset: number }
   */
  check(key) {
    const now = Date.now();
    const valid = this._cleanup(key);
    const remaining = this.maxRequests - valid.length;
    const allowed = remaining > 0;

    // 下一次重置时间 = 最早记录的时间 + 窗口
    const reset = valid.length > 0
      ? valid[0] + this.windowMs
      : now + this.windowMs;

    return { allowed, remaining: Math.max(0, remaining), reset };
  }

  /**
   * 记录一次请求
   */
  hit(key) {
    const now = Date.now();
    if (!this.store.has(key)) {
      this.store.set(key, []);
    }
    this.store.get(key).push(now);
    return this.check(key);
  }
}

// 全局限流实例（按 appId 区分）
const globalLimiter = new SlidingWindow(
  config.RATE_LIMIT.windowMs,
  config.RATE_LIMIT.maxRequests
);

// 全局限流（不区分 appId）
const ipLimiter = new SlidingWindow(
  config.RATE_LIMIT.windowMs,
  Math.floor(config.RATE_LIMIT.maxRequests * 1.5)
);

function rateLimit(options = {}) {
  const { byAppId = true, windowMs, maxRequests } = options;

  // 如果传入了自定义配置，创建临时 limiter
  const limiter = (windowMs || maxRequests)
    ? new SlidingWindow(windowMs || config.RATE_LIMIT.windowMs, maxRequests || config.RATE_LIMIT.maxRequests)
    : (byAppId ? globalLimiter : ipLimiter);

  const { Headers } = config.RATE_LIMIT;

  return async (ctx, next) => {
    // 限流未启用时，直接跳过
    if (!config.RATE_LIMIT.enabled) {
      await next();
      return;
    }

    // 确定限流 key：优先按 appId，否则按 IP
    const key = byAppId && ctx.state.auth?.appId
      ? ctx.state.auth.appId
      : (ctx.ip || 'unknown');

    const result = limiter.hit(key);

    // 设置响应头
    ctx.set(Headers.remaining, String(result.remaining));
    ctx.set(Headers.limit, String(config.RATE_LIMIT.maxRequests));
    ctx.set(Headers.reset, String(Math.floor(result.reset / 1000)));

    if (!result.allowed) {
      ctx.status = 429;
      const retryAfter = Math.ceil((result.reset - Date.now()) / 1000);
      ctx.set('Retry-After', String(retryAfter));
      ctx.body = {
        code: 429,
        message: '请求过于频繁，已被限流',
        data: null,
        hint: `请 ${retryAfter} 秒后重试`,
        resetAt: new Date(result.reset).toISOString(),
      };
      return;
    }

    await next();
  };
}

module.exports = { rateLimit, SlidingWindow };
