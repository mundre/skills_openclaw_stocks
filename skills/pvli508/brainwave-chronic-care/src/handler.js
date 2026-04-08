/**
 * 慢病脑波声疗助手 - 意图处理器示例代码
 * 
 * 本文件展示如何实现 Skill 的意图处理逻辑
 * 开发者需要根据实际业务需求完善以下代码
 */

// 慢病类型枚举
const CHRONIC_TYPES = ['高血压', '糖尿病', '睡眠障碍', '心脑血管', '康复通用'];

// 场景枚举
const SCENES = ['睡前', '餐后', '午休', '情绪烦躁', '康复期', '日间放松'];

// 时长选项
const DURATIONS = [10, 15, 20, 30];
const DEFAULT_DURATION = 15;

// 合规声明
const COMPLIANCE_NOTICE = '温馨提示：本音频为非药物健康辅助，不替代医疗诊断与治疗。';

/**
 * 主入口：处理意图
 * @param {Object} params - 请求参数
 * @param {string} params.user_id - 用户ID
 * @param {string} params.tenant_id - 租户ID
 * @param {string} params.intent_id - 意图ID
 * @param {Object} params.slots - 槽位数据
 * @param {Object} params.device_info - 设备信息
 */
async function handleIntent({ user_id, tenant_id, intent_id, slots, device_info }) {
  // 校验租户权限
  const tenant = await getTenant(tenant_id);
  if (!tenant || tenant.status !== 'enabled') {
    return { reply_text: '服务暂不可用，请联系管理员。' + COMPLIANCE_NOTICE };
  }

  switch (intent_id) {
    case 'PLAY_BRAINWAVE_AUDIO':
      return await handlePlayAudio(tenant_id, user_id, slots, device_info);
    case 'CONTROL_AUDIO':
      return await handleControlAudio(slots);
    case 'SET_AUDIO_TIMER':
      return await handleSetTimer(slots);
    case 'SWITCH_AUDIO_SCENE':
      return await handleSwitchScene(tenant_id, user_id, slots, device_info);
    case 'QUERY_SKILL_HELP':
      return handleHelp();
    case 'EXIT_SKILL':
      return handleExit();
    default:
      return { reply_text: '暂不支持该操作。' + COMPLIANCE_NOTICE };
  }
}

/**
 * 处理播放脑波音频
 */
async function handlePlayAudio(tenant_id, user_id, slots, device_info) {
  let { chronic_type, scene, duration } = slots;

  // 处理时长默认值
  if (!duration || !DURATIONS.includes(duration)) {
    duration = DEFAULT_DURATION;
  }

  // 处理无慢病类型 - 交互确认或使用通用音频
  if (!chronic_type || !CHRONIC_TYPES.includes(chronic_type)) {
    // 尝试获取用户最近使用记录
    const recentRecord = await getUserRecentRecord(tenant_id, user_id);
    
    if (recentRecord) {
      chronic_type = recentRecord.chronic_type;
      scene = scene || recentRecord.scene;
    } else {
      // 无记录，返回交互确认话术
      return {
        reply_text: '请问您需要什么类型的脑波音频？有高血压、糖尿病、睡眠障碍、心脑血管等类型。',
        need_confirm: true
      };
    }
  }

  // 如果是交互确认后返回，带有明确的 chronic_type
  if (slots.confirm_chronic_type && CHRONIC_TYPES.includes(slots.confirm_chronic_type)) {
    chronic_type = slots.confirm_chronic_type;
  } else if (!chronic_type) {
    // 交互失败，使用通用音频
    chronic_type = '康复通用';
  }

  // 匹配音频资源
  const audio = await matchAudio(tenant_id, chronic_type, scene, duration);
  
  if (!audio) {
    return {
      reply_text: '暂时无法找到合适音频，请您稍后再试，或联系您的健康管理机构。' + COMPLIANCE_NOTICE
    };
  }

  // 生成带签名的播放地址
  const audio_url = await generateSignedUrl(audio.cdn_url);

  // 更新用户最近使用记录
  await updateUserRecentRecord(tenant_id, user_id, chronic_type, scene);

  // 上报播放日志
  await reportPlayLog(tenant_id, user_id, audio.audio_id, device_info.device_id, duration);

  // 构建回复话术
  const sceneText = scene ? scene + ' ' : '';
  const reply_text = `已为您打开【${chronic_type}】${sceneText}脑波音频，时长 ${duration} 分钟。${COMPLIANCE_NOTICE}`;

  return {
    reply_text,
    audio_url,
    control_cmd: 'play'
  };
}

/**
 * 处理音频控制
 */
async function handleControlAudio(slots) {
  const { action } = slots; // pause/resume/stop
  
  let control_cmd = 'play';
  let reply_text = '';

  switch (action) {
    case 'pause':
      control_cmd = 'pause';
      reply_text = '已暂停播放。' + COMPLIANCE_NOTICE;
      break;
    case 'resume':
    case 'continue':
      control_cmd = 'resume';
      reply_text = '已继续播放。' + COMPLIANCE_NOTICE;
      break;
    case 'stop':
      control_cmd = 'stop';
      reply_text = '已停止播放。' + COMPLIANCE_NOTICE;
      break;
    default:
      return { reply_text: '暂不支持该操作。' + COMPLIANCE_NOTICE };
  }

  return { reply_text, control_cmd };
}

/**
 * 处理定时关闭
 */
async function handleSetTimer(slots) {
  const { duration } = slots;

  if (!duration || !DURATIONS.includes(duration)) {
    return { reply_text: '暂不支持该定时时长，请选择 10、15、20 或 30 分钟。' + COMPLIANCE_NOTICE };
  }

  return {
    reply_text: `好的，${duration} 分钟后将自动为您关闭音频。`,
    timer: { duration_minutes: duration, action: 'stop' }
  };
}

/**
 * 处理切换音频/场景
 */
async function handleSwitchScene(tenant_id, user_id, slots, device_info) {
  // 复用播放逻辑，但使用新的 slots
  return await handlePlayAudio(tenant_id, user_id, slots, device_info);
}

/**
 * 处理帮助查询
 */
function handleHelp() {
  return {
    reply_text: `您可以对我说：播放高血压舒缓音频、播放 15 分钟助眠脑波、定时关闭等。${COMPLIANCE_NOTICE}`
  };
}

/**
 * 处理退出技能
 */
function handleExit() {
  return {
    reply_text: '好的，已退出脑波音频助手。如有需要随时呼唤我。',
    control_cmd: 'stop',
    exit_skill: true
  };
}

// ============== 业务接口模拟 ==============

async function getTenant(tenant_id) {
  // TODO: 实现租户查询
  return { tenant_id, status: 'enabled' };
}

async function matchAudio(tenant_id, chronic_type, scene, duration) {
  // TODO: 实现音频匹配逻辑
  // 查询 t_audio_meta 表，匹配 chronic_type + scene + duration
  return {
    audio_id: 'audio_001',
    cdn_url: 'https://cdn.example.com/bw_hypertension_sleep_15min.mp3'
  };
}

async function generateSignedUrl(cdn_url) {
  // TODO: 实现签名生成 (HMAC-SHA256，时效 6 小时)
  const expires = Date.now() + 6 * 60 * 60 * 1000;
  const signature = 'mock_signature_' + expires;
  return `${cdn_url}?expires=${expires}&sign=${signature}`;
}

async function getUserRecentRecord(tenant_id, user_id) {
  // TODO: 查询 t_user_tag 表，返回 last_used_time 最近的一条记录
  return null;
}

async function updateUserRecentRecord(tenant_id, user_id, chronic_type, scene) {
  // TODO: 更新 t_user_tag 表的 last_used_time 字段
}

async function reportPlayLog(tenant_id, user_id, audio_id, device_id, duration) {
  // TODO: 上报到 t_play_log 表
}

module.exports = {
  handleIntent,
  CHRONIC_TYPES,
  SCENES,
  DURATIONS,
  COMPLIANCE_NOTICE
};
