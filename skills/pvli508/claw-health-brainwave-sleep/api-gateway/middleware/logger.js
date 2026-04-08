/**
 * 请求日志中间件
 */

const fs = require('fs');
const path = require('path');
const config = require('../config/default');

// 确保日志目录存在
const logDir = path.dirname(config.LOG.accessLog);
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
}

// 日志写入流
const accessStream = fs.createWriteStream(config.LOG.accessLog, { flags: 'a' });
const errorStream = fs.createWriteStream(config.LOG.errorLog, { flags: 'a' });

/**
 * 格式化请求日志
 */
function formatRequest(ctx, durationMs) {
  const { method, url } = ctx.request;
  const { status } = ctx.res;
  const auth = ctx.state.auth;
  const ip = ctx.ip;

  const parts = [
    new Date().toISOString(),
    `${method.padEnd(6)}`,
    `${String(status).padStart(3)}`,
    `${String(durationMs).padStart(4)}ms`,
    `ip=${ip}`,
    auth?.appId ? `app=${auth.appId}` : 'app=anonymous',
    url,
  ];

  return parts.join(' | ');
}

/**
 * 请求日志中间件
 */
function logger(options = {}) {
  const { logBody = config.LOG.logBody } = options;

  return async (ctx, next) => {
    const start = Date.now();

    // 捕获响应后的状态
    await next();

    const durationMs = Date.now() - start;
    const logLine = formatRequest(ctx, durationMs);

    // 控制台输出
    if (config.LOG.console) {
      const status = ctx.res.status;
      const color = status >= 500 ? '\x1b[31m' : status >= 400 ? '\x1b[33m' : status >= 200 ? '\x1b[32m' : '\x1b[0m';
      console.log(`${color}${logLine}\x1b[0m`);
    }

    // 写入文件
    if (ctx.res.status >= 500) {
      errorStream.write(logLine + '\n');
    } else {
      accessStream.write(logLine + '\n');
    }
  };
}

/**
 * 全局错误日志
 */
function errorLogger() {
  return async (ctx, next) => {
    try {
      await next();
    } catch (err) {
      const timestamp = new Date().toISOString();
      const logLine = [timestamp, 'ERROR', err.message, err.stack].join(' | ');

      if (config.LOG.console) {
        console.error(`\x1b[31m${logLine}\x1b[0m`);
      }
      errorStream.write(logLine + '\n');
      throw err;
    }
  };
}

module.exports = { logger, errorLogger, formatRequest };
