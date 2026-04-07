/**
 * WaQuanquaner Skill 配置文件
 * 
 * 所有可配置项集中管理，方便自定义部署
 */

module.exports = {
  /** 服务器端 API 地址（生产环境） */
  SERVER_URL: process.env.WAIMAI_SERVER_URL || 'https://waquanquaner.cn',

  /** API 路径前缀 */
  API_PREFIX: '/api/v1',

  /** 默认用户标识符（用于 CPS 订单归因） */
  DEFAULT_LOBSTER_ID: process.env.WAIMAI_LOBSTER_ID || 'lobster-claw-default',

  /** 每个平台最多返回的活动数量 */
  TOP_N: 3,

  /** API 请求超时时间（毫秒） */
  TIMEOUT: 15000,

  /** 活动类型自动分类关键词（仅外卖相关，顺序决定优先级） */
  ACTIVITY_TYPES: {
    '新人': ['新人', '新用户', '首单'],
    '返利': ['返利', '返现', 'cashback'],
    '红包': ['红包', '天天领', '红包节', '领红包', '赚现金'],
    '优惠': [], // 默认分类（神券包、满减等通用优惠）
  },

  /** 平台映射 */
  PLATFORMS: {
    eleme: {
      name: '饿了么',
      emoji: '🔵',
      keywords: ['饿了么', 'eleme', '饿了'],
    },
    meituan: {
      name: '美团',
      emoji: '🟡',
      keywords: ['美团', 'meituan', '点评'],
    },
    jingdong: {
      name: '京东',
      emoji: '🔴',
      keywords: ['京东', 'jingdong', 'JD'],
    },
  },

  /** 触发关键词（用户输入匹配） */
  TRIGGER_KEYWORDS: [
    '外卖红包', '外卖优惠', '外卖券', '外卖优惠券',
    '省钱', '点外卖省钱', '外卖省钱',
    '淘口令', '外卖淘口令',
    '领券', '外卖领券', '领红包',
    '红包', '优惠活动',
    '点外卖', '叫外卖', '外卖', '外卖神券',
    '满减红包', '美团外卖', '饿了么外卖', '京东外卖',
    '挖券券', '挖券券儿', '吃什么',
  ],

  /** 平台+类型组合触发词 */
  PLATFORM_TRIGGERS: {
    eleme: ['饿了么红包', '饿了么优惠', '饿了么券', '饿了么领券'],
    meituan: ['美团红包', '美团优惠', '美团券', '美团领券', '美团外卖'],
    jingdong: ['京东红包', '京东优惠', '京东券', '京东外卖'],
  },

  /** 渲染格式 */
  FORMATS: {
    WECHAT: 'wechat',      // 微信文本
    FEISHU: 'feishu',      // 飞书消息卡片
    TEXT: 'text',          // 纯文本（终端/日志）
  },
};
