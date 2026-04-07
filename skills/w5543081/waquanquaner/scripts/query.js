/**
 * WaQuanquaner - 活动查询引擎
 * 
 * 从服务器端 API 获取外卖优惠活动数据
 * 依赖：Node.js 内置 http/https 模块（无需第三方依赖）
 */

const http = require('http');
const https = require('https');
const { URL } = require('url');
const config = require('./config');

/**
 * 发送 HTTP GET 请求
 * @param {string} urlStr - 请求 URL
 * @param {number} timeout - 超时时间（毫秒）
 * @returns {Promise<object>} 解析后的 JSON 响应
 */
function httpGet(urlStr, timeout = config.TIMEOUT) {
  return new Promise((resolve, reject) => {
    let parsedUrl;
    try {
      parsedUrl = new URL(urlStr);
    } catch (e) {
      return reject(new Error('无效的 URL: ' + urlStr));
    }

    const client = parsedUrl.protocol === 'https:' ? https : http;
    const req = client.get(urlStr, { timeout }, (res) => {
      // 处理重定向
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
        return httpGet(res.headers.location, timeout).then(resolve).catch(reject);
      }

      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          if (res.statusCode >= 400) {
            reject(new Error('API 返回错误 ' + res.statusCode + ': ' + (json.message || data.substring(0, 200))));
          } else {
            resolve(json);
          }
        } catch (e) {
          reject(new Error('JSON 解析失败: ' + e.message));
        }
      });
    });

    req.on('error', reject);
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('请求超时 (' + timeout + 'ms)'));
    });
  });
}

/**
 * 获取外卖优惠活动（Skill 主接口）
 * 
 * @param {object} options
 * @param {string} [options.lobsterId] - 用户标识符（默认使用 config.DEFAULT_LOBSTER_ID）
 * @param {string} [options.serverUrl] - 服务器地址（默认使用 config.SERVER_URL）
 * @returns {Promise<{success: boolean, activities: Array, message: string}>}
 */
async function fetchActivities(options = {}) {
  const serverUrl = options.serverUrl || config.SERVER_URL;
  const lobsterId = options.lobsterId || config.DEFAULT_LOBSTER_ID;

  const apiUrl = serverUrl + config.API_PREFIX + '/activities/skill/' + lobsterId;

  try {
    const response = await httpGet(apiUrl, config.TIMEOUT);

    // API 返回格式: { total, updated_at, skill_id, activities }
    // 也兼容: { success: true, data: [...] }
    let activities = null;

    if (Array.isArray(response.activities)) {
      activities = response.activities;
    } else if (response.success && Array.isArray(response.data)) {
      activities = response.data;
    }

    if (activities && activities.length >= 0) {
      return {
        success: true,
        activities: activities.map(normalizeActivity),
        total: response.total || activities.length,
        updated_at: response.updated_at || '',
        message: '',
      };
    }

    return {
      success: false,
      activities: [],
      total: 0,
      message: response.message || '服务器返回数据格式异常',
    };
  } catch (error) {
    return {
      success: false,
      activities: [],
      total: 0,
      message: error.message,
    };
  }
}

/**
 * 标准化活动数据
 * @param {object} raw - API 返回的原始活动对象
 * @returns {object} 标准化后的活动对象
 */
function normalizeActivity(raw) {
  const platform = raw.platform || detectPlatform(raw.act_name);
  const activityType = detectActivityType(raw.act_name, raw.description);

  return {
    act_id: raw.act_id,
    act_name: raw.act_name || '',
    description: raw.description || '',
    platform: platform,
    platform_name: config.PLATFORMS[platform]?.name || platform,
    platform_emoji: config.PLATFORMS[platform]?.emoji || '⚪',
    commission_rate: raw.commission_rate,
    tkl: raw.tkl || '',
    activity_type: activityType,
    activity_tag: getActivityTag(activityType),
  };
}

/**
 * 根据活动名称检测平台（后备方案）
 * @param {string} name
 * @returns {string}
 */
function detectPlatform(name) {
  for (const [key, info] of Object.entries(config.PLATFORMS)) {
    for (const kw of info.keywords) {
      if (name.includes(kw)) return key;
    }
  }
  return 'other';
}

/**
 * 检测活动类型
 * @param {string} name - 活动名称
 * @param {string} desc - 活动描述
 * @returns {string} 类型标签
 */
function detectActivityType(name, desc) {
  const text = [name, desc].filter(Boolean).join(' ');
  for (const [type, keywords] of Object.entries(config.ACTIVITY_TYPES)) {
    if (type === '优惠') continue; // 默认分类，跳过
    for (const kw of keywords) {
      if (text.includes(kw)) return type;
    }
  }
  return '优惠';
}

/**
 * 获取活动类型的展示标签
 * @param {string} type
 * @returns {string}
 */
function getActivityTag(type) {
  const tags = {
    '红包': '[红包]',
    '返利': '[返利]',
    '新人': '[新人]',
    '优惠': '[优惠]',
  };
  return tags[type] || '[优惠]';
}

/**
 * 按平台分组活动
 * @param {Array} activities - 标准化后的活动列表
 * @returns {object} 按平台分组的对象
 */
function groupByPlatform(activities) {
  const groups = {};
  for (const act of activities) {
    const key = act.platform;
    if (!groups[key]) {
      groups[key] = {
        platform: act.platform,
        name: act.platform_name,
        emoji: act.platform_emoji,
        activities: [],
      };
    }
    groups[key].activities.push(act);
  }
  return groups;
}

// CLI 直接执行
if (require.main === module) {
  (async () => {
    console.log('正在查询外卖优惠活动...\n');
    const result = await fetchActivities();
    
    if (!result.success) {
      console.log('❌ 查询失败:', result.message);
      process.exit(1);
    }

    console.log('✅ 查询成功，共 ' + result.total + ' 个活动\n');

    const groups = groupByPlatform(result.activities);
    for (const [key, group] of Object.entries(groups)) {
      console.log(group.emoji + ' ' + group.name + ' (' + group.activities.length + ' 个活动)');
      for (const act of group.activities) {
        console.log('  ' + act.activity_tag + ' ' + act.act_name);
        console.log('    ' + act.description);
        console.log('    ' + act.tkl);
      }
      console.log();
    }
  })();
}

module.exports = {
  fetchActivities,
  normalizeActivity,
  detectPlatform,
  detectActivityType,
  groupByPlatform,
  httpGet,
};
