/**
 * WaQuanquaner - 渲染引擎
 * 
 * 将活动数据渲染为不同渠道的输出格式：
 * - 微信文本：适合微信聊天/小程序消息
 * - 飞书消息卡片：适合飞书群聊
 * - 纯文本：适合终端/日志
 */

const config = require('./config');
const { groupByPlatform } = require('./query');

/**
 * 渲染入口
 * @param {Array} activities - 标准化后的活动列表
 * @param {string} format - 渲染格式 (wechat/feishu/text)
 * @returns {string} 渲染后的文本
 */
function render(activities, format = config.FORMATS.WECHAT) {
  if (!activities || activities.length === 0) {
    return renderEmpty(format);
  }

  switch (format) {
    case config.FORMATS.WECHAT:
      return renderWechat(activities);
    case config.FORMATS.FEISHU:
      return renderFeishu(activities);
    case config.FORMATS.TEXT:
    default:
      return renderText(activities);
  }
}

/**
 * 渲染空结果
 */
function renderEmpty(format) {
  const messages = {
    wechat: '🔍 今天暂时没有新的外卖优惠活动，明天再来看看吧！\n\n💡 也可以试试直接在饿了么/美团 App 里搜「外卖红包」',
    feishu: JSON.stringify({
      config: { wide_screen_mode: true },
      header: {
        title: { tag: 'plain_text', content: '🧧 外卖红包速报' },
        template: 'orange',
      },
      elements: [{
        tag: 'markdown',
        content: '今天暂时没有新的外卖优惠活动，明天再来看看吧！\n也可以试试直接在饿了么/美团 App 里搜「外卖红包」',
      }],
    }, null, 2),
    text: '[暂无活动] 今天没有新的外卖优惠活动',
  };
  return messages[format] || messages.text;
}

// ============================================================
// 微信文本渲染
// ============================================================

/**
 * 渲染为微信文本格式（默认格式）
 * 
 * 特点：简洁清晰，emoji 区分平台，活动结构分明，方便长按复制
 */
function renderWechat(activities) {
  const date = new Date().toLocaleDateString('zh-CN', { month: 'long', day: 'numeric' });
  const groups = groupByPlatform(activities);
  
  let output = '🧧 外卖红包速报 (' + date + ')\n\n';
  let isFirst = true;

  // 按平台名称排序：饿了么 > 美团 > 京东
  const sortedKeys = Object.keys(groups).sort((a, b) => {
    const order = { eleme: 0, meituan: 1, jingdong: 2 };
    return (order[a] || 9) - (order[b] || 9);
  });

  for (const key of sortedKeys) {
    const group = groups[key];
    
    if (!isFirst) {
      output += '\n';
    }
    isFirst = false;

    output += group.emoji + ' ' + group.name + ' (' + group.activities.length + '个)\n';
    output += '━━━━━━━━━━\n';

    group.activities.forEach((act, i) => {
      output += (i + 1) + '. ' + act.activity_tag + ' ' + act.act_name + '\n';
      output += '   ' + act.description + '\n';
      if (act.commission_rate) {
        output += '   💰 佣金: ' + act.commission_rate + (typeof act.commission_rate === 'number' && act.commission_rate <= 100 ? '%' : '元') + '\n';
      }
      output += '   📋 复制：' + act.tkl + '\n';
      
      if (i < group.activities.length - 1) {
        output += '\n';
      }
    });
  }

  output += '\n━━━━━━━━━━\n';
  output += '💡 复制淘口令 → 打开对应App → 自动跳转领券\n';
  output += '🎁 更多优惠活动，微信搜索「挖券券儿」';

  return output;
}

// ============================================================
// 飞书消息卡片渲染
// ============================================================

/**
 * 渲染为飞书消息卡片格式（JSON）
 * 
 * 特点：结构化卡片，带颜色标题，字段对齐，支持 markdown
 */
function renderFeishu(activities) {
  const groups = groupByPlatform(activities);
  
  const elements = [];
  
  // 按平台排序
  const sortedKeys = Object.keys(groups).sort((a, b) => {
    const order = { eleme: 0, meituan: 1, jingdong: 2 };
    return (order[a] || 9) - (order[b] || 9);
  });

  for (let gi = 0; gi < sortedKeys.length; gi++) {
    const key = sortedKeys[gi];
    const group = groups[key];

    // 平台标题行
    elements.push({
      tag: 'div',
      fields: [
        {
          is_short: true,
          text: { tag: 'lark_md', content: '**' + group.emoji + ' ' + group.name + '**' },
        },
        {
          is_short: true,
          text: { tag: 'lark_md', content: group.activities.length + ' 个活动' },
        },
      ],
    });

    // 每个活动
    group.activities.forEach((act) => {
      let md = '**' + act.activity_tag + ' ' + escapeFeishuMd(act.act_name) + '**\n';
      md += escapeFeishuMd(act.description);
      if (act.tkl) {
        md += '\n`' + escapeFeishuMd(act.tkl) + '`';
      }
      elements.push({
        tag: 'div',
        text: { tag: 'lark_md', content: md },
      });
    });

    // 平台间分割线
    if (gi < sortedKeys.length - 1) {
      elements.push({ tag: 'hr' });
    }
  }

  // 底部提示
  elements.push({ tag: 'hr' });
  elements.push({
    tag: 'note',
    elements: [{
      tag: 'plain_text',
      content: '💡 复制淘口令 → 打开对应App → 自动跳转领券 | 🎁 更多优惠活动，微信搜索「挖券券儿」',
    }],
  });

  const card = {
    config: { wide_screen_mode: true },
    header: {
      title: { tag: 'plain_text', content: '🧧 外卖红包速报' },
      template: 'turquoise',
    },
    elements: elements,
  };

  return JSON.stringify(card, null, 2);
}

/**
 * 转义飞书 markdown 特殊字符
 */
function escapeFeishuMd(text) {
  if (!text) return '';
  return text.replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// ============================================================
// 纯文本渲染（终端/日志）
// ============================================================

/**
 * 渲染为纯文本格式
 * 
 * 特点：紧凑表格，对齐列，适合终端和日志输出
 */
function renderText(activities) {
  const date = new Date().toISOString().split('T')[0];
  const groups = groupByPlatform(activities);
  
  let output = '外卖红包速报 (' + date + ')\n';

  const sortedKeys = Object.keys(groups).sort((a, b) => {
    const order = { eleme: 0, meituan: 1, jingdong: 2 };
    return (order[a] || 9) - (order[b] || 9);
  });

  for (const key of sortedKeys) {
    const group = groups[key];
    
    output += '\n[' + group.name + '] ' + group.activities.length + ' 个活动\n';

    for (const act of group.activities) {
      const name = act.act_name.length > 20 ? act.act_name.substring(0, 20) + '..' : act.act_name;
      const desc = act.description.length > 14 ? act.description.substring(0, 14) + '..' : act.description;
      const tkl = act.tkl.length > 20 ? act.tkl.substring(0, 20) + '..' : act.tkl;
      
      output += '  #' + (group.activities.indexOf(act) + 1) + ' ';
      output += padEnd(name, 22) + ' | ';
      output += padEnd(act.activity_tag, 6) + ' | ';
      output += padEnd(desc, 16) + ' | ';
      output += tkl + '\n';
    }
  }

  output += '\n🎁 更多优惠活动，微信搜索「挖券券儿」';

  return output;
}

/**
 * 字符串右填充（中英文混合兼容）
 */
function padEnd(str, len) {
  if (!str) return ' '.repeat(len);
  // 简单实现：计算显示宽度
  let width = 0;
  for (const ch of str) {
    width += ch.charCodeAt(0) > 127 ? 2 : 1;
  }
  const pad = len - width;
  if (pad <= 0) return str;
  return str + ' '.repeat(pad);
}

// CLI 直接执行
if (require.main === module) {
  const { fetchActivities } = require('./query');
  
  (async () => {
    const format = process.argv[2] || 'wechat';
    console.log('查询中...\n');
    
    const result = await fetchActivities();
    if (!result.success) {
      console.log('查询失败:', result.message);
      process.exit(1);
    }
    
    console.log(render(result.activities, format));
  })();
}

module.exports = {
  render,
  renderWechat,
  renderFeishu,
  renderText,
  renderEmpty,
};
