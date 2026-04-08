/**
 * 网关配置
 */

module.exports = {
  // ---- 服务基础 ----
  PORT: process.env.PORT || 3092,
  HOST: process.env.HOST || '0.0.0.0',
  NODE_ENV: process.env.NODE_ENV || 'development',

  // ---- 音频资源路径 ----
  AUDIO_BASE_DIR: process.env.AUDIO_BASE_DIR ||
    (process.platform === 'win32'
      ? 'C:\\Users\\龚文瀚\\Desktop\\sleepAudio'
      : '/path/to/sleepAudio'),

  // ---- API Key 配置 ----
  API_KEY_HEADER: 'X-API-Key',
  // 示例：production 环境需通过环境变量注入真实 key
  // 格式：{ 'app_id_001': 'api_key_001', ... }
  API_KEYS: process.env.API_KEYS
    ? JSON.parse(process.env.API_KEYS)
    : {
        // 开发环境默认 key（仅供测试）
        'dev-app-001': 'sk_dev_abcdef1234567890',
        'wechat-mini-app': 'sk_mini_1234567890abcdef',
        'ios-app': 'sk_ios_abcdef1234567890',
        'android-app': 'sk_android_abcdef123456',
      },

  // ---- 限流配置 ----
  RATE_LIMIT: {
    // 是否启用
    enabled: process.env.RATE_LIMIT_ENABLED !== 'false',
    // 窗口时间（毫秒）
    windowMs: parseInt(process.env.RATE_WINDOW_MS || '60000'),
    // 每个 key 的最大请求数
    maxRequests: parseInt(process.env.RATE_MAX_REQUESTS || '100'),
    // 限制返回的响应头
   Headers: {
      remaining: 'X-RateLimit-Remaining',
      reset: 'X-RateLimit-Reset',
      limit: 'X-RateLimit-Limit',
    },
  },

  // ---- 日志配置 ----
  LOG: {
    // 日志文件路径
    accessLog: process.env.LOG_ACCESS || 'logs/access.log',
    errorLog: process.env.LOG_ERROR || 'logs/error.log',
    // 是否打印到控制台
    console: true,
    // 请求体日志（生产环境关闭）
    logBody: process.env.NODE_ENV !== 'production',
  },

  // ---- CORS 配置 ----
  CORS_ORIGINS: process.env.CORS_ORIGINS
    ? process.env.CORS_ORIGINS.split(',')
    : ['*'],

  // ---- Skill 注册表 ----
  // 延迟加载避免循环依赖
  get SKILLS() {
    return {
      sleep: {
        name: '睡眠脑波',
        version: '1.0.0',
        routes: require('../routes/sleep'),
      },
      health: {
        name: '健康管理',
        version: '1.0.0',
        routes: require('../routes/health'),
      },
    };
  },

  // ---- 数据存储路径 ----
  DATA_DIR: process.env.DATA_DIR || 'data',
};
