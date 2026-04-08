/**
 * 睡眠障碍脑波声疗助手 - 意图处理器
 * 
 * 聚焦睡眠障碍细分场景，支持个体多维度信息适配
 */

// 睡眠障碍亚型
const SLEEP_SUBTYPES = {
  SLEEP_ONSET: { name: '入睡困难型', brainwave: 'theta', defaultScene: 'pre_sleep' },
  SLEEP_MAINTAIN: { name: '睡眠维持型', brainwave: 'delta', defaultScene: 'midnight_wake' },
  EARLY_WAKE: { name: '早醒型', brainwave: 'theta_alpha', defaultScene: 'midnight_wake' },
  CIRCADIAN: { name: '昼夜节律紊乱', brainwave: 'alpha_theta_delta', defaultScene: 'relaxation' },
  ANXIETY_SLEEP: { name: '焦虑性失眠', brainwave: 'alpha_theta', defaultScene: 'pre_sleep' },
  LIGHT_SLEEP: { name: '浅眠多梦型', brainwave: 'delta', defaultScene: 'pre_sleep' },
  GENERAL: { name: '通用型', brainwave: 'theta', defaultScene: 'pre_sleep' }
};

// 严重程度
const SEVERITY_LEVELS = {
  MILD: { name: '轻度', defaultDuration: 20 },
  MODERATE: { name: '中度', defaultDuration: 30 },
  SEVERE: { name: '重度', defaultDuration: 45 }
};

// 年龄组
const AGE_GROUPS = {
  YOUNG_ADULT: { name: '青年', range: '18-35岁' },
  MIDDLE_AGED: { name: '中年', range: '36-55岁' },
  ELDERLY: { name: '老年', range: '56岁以上' }
};

// 性别
const GENDERS = {
  MALE: { name: '男性' },
  FEMALE: { name: '女性' },
  UNSET: { name: '未设置' }
};

// 场景
const USE_SCENES = {
  PRE_SLEEP: { name: '睡前', timeRange: '22:00-24:00' },
  MIDNIGHT_WAKE: { name: '夜醒复眠', timeRange: '00:00-05:00' },
  NAP: { name: '午休', timeRange: '12:00-14:00' },
  RELAXATION: { name: '日间放松', timeRange: '其余时段' }
};

// 伴随状况
const COMORBIDITIES = {
  ANXIETY: { name: '焦虑' },
  DEPRESSION: { name: '抑郁' },
  HYPERTENSION: { name: '高血压' },
  PAIN: { name: '疼痛' },
  NONE: { name: '无' }
};

// 合规声明
const COMPLIANCE_NOTICE = '温馨提示：本音频为非药物健康辅助，不替代医疗诊断与治疗。';

// 本地音频库路径
const AUDIO_LIBRARY_PATH = "C:\\Users\\龚文瀚\\Desktop\\sleepAudio";

// 用户画像存储
let userProfiles = {};
let audioManifest = null;

const PROFILE_FILE = "C:\\Users\\龚文瀚\\.openclaw\\workspace\\skills\\claw_health_brainwave_sleep\\src\\user-profiles.json";

async function loadProfiles() {
  try {
    const fs = require('fs');
    const data = fs.readFileSync(PROFILE_FILE, 'utf-8');
    userProfiles = JSON.parse(data);
  } catch (e) {
    userProfiles = {};
  }
}

async function saveProfiles() {
  try {
    const fs = require('fs');
    fs.writeFileSync(PROFILE_FILE, JSON.stringify(userProfiles, null, 2));
  } catch (e) {
    console.error('Failed to save profiles:', e);
  }
}

async function loadManifest() {
  if (audioManifest) return audioManifest;
  
  try {
    const fs = require('fs');
    const path = require('path');
    const manifestPath = path.join(__dirname, '..', 'audio_library', 'manifest.json');
    const data = fs.readFileSync(manifestPath, 'utf-8');
    audioManifest = JSON.parse(data);
    return audioManifest;
  } catch (e) {
    console.error('Failed to load manifest:', e);
    return null;
  }
}

/**
 * 主入口：处理意图
 */
async function handleIntent({ user_id, intent_id, slots, context }) {
  await loadProfiles();
  await loadManifest();

  const userProfile = userProfiles[user_id] || {};

  switch (intent_id) {
    case 'PLAY_SLEEP_BRAINWAVE':
      return await handlePlayAudio(user_id, slots, userProfile, context);
    case 'CONTROL_SLEEP_AUDIO':
      return await handleControlAudio(slots);
    case 'SET_SLEEP_TIMER':
      return await handleSetTimer(slots);
    case 'SWITCH_SLEEP_AUDIO':
      return await handleSwitchAudio(user_id, slots, userProfile);
    case 'UPDATE_USER_PROFILE':
      return await handleUpdateProfile(user_id, slots, userProfile);
    case 'QUERY_SLEEP_HELP':
      return handleHelp();
    case 'EXIT_SLEEP_SKILL':
      return handleExit();
    default:
      return { reply_text: '暂不支持该操作。' + COMPLIANCE_NOTICE };
  }
}

/**
 * 处理播放睡眠脑波音频
 */
async function handlePlayAudio(user_id, slots, userProfile, context) {
  let { 
    sleep_disorder_subtype, 
    use_scene, 
    duration, 
    severity, 
    age_group, 
    gender,
    comorbidity 
  } = slots;

  // 合并用户画像
  sleep_disorder_subtype = sleep_disorder_subtype || userProfile.sleep_disorder_subtype;
  severity = severity || userProfile.severity;
  age_group = age_group || userProfile.age_group;
  gender = gender || userProfile.gender;
  comorbidity = comorbidity || userProfile.comorbidity;

  // 如果没有亚型，尝试从用户画像获取，或询问用户
  if (!sleep_disorder_subtype && userProfile.sleep_disorder_subtype) {
    sleep_disorder_subtype = userProfile.sleep_disorder_subtype;
  }

  // 自动推断场景
  if (!use_scene) {
    const hour = new Date().getHours();
    if (hour >= 0 && hour < 5) {
      use_scene = 'MIDNIGHT_WAKE';
    } else if (hour >= 12 && hour < 14) {
      use_scene = 'NAP';
    } else if (hour >= 22 || hour < 0) {
      use_scene = 'PRE_SLEEP';
    } else {
      use_scene = 'RELAXATION';
    }
  }

  // 如果没有严重程度，使用默认值
  if (!severity) {
    severity = 'MODERATE';
  }

  // 时长推荐逻辑
  if (!duration) {
    const severityConfig = SEVERITY_LEVELS[severity];
    duration = severityConfig ? severityConfig.defaultDuration : 30;
  }

  // 如果没有完整信息，返回交互确认
  if (!sleep_disorder_subtype) {
    return {
      reply_text: '请问您的睡眠问题属于哪种类型？\n- 入睡困难（睡不着）\n- 睡眠维持型（容易醒）\n- 早醒型（凌晨醒来）\n- 浅眠多梦型\n- 焦虑性失眠\n- 通用型（不清楚）\n\n告诉我类型后，我会为您匹配最适合的脑波音频。' + COMPLIANCE_NOTICE,
      need_confirm: true
    };
  }

  // 匹配音频
  const audio = await matchAudio(sleep_disorder_subtype, use_scene, duration, severity, age_group, gender);
  
  if (!audio) {
    // 降级到通用版
    const generalAudio = await matchAudio('GENERAL', use_scene, duration, severity, age_group, gender);
    if (generalAudio) {
      return {
        reply_text: `已为您播放通用助眠脑波音频，时长 ${duration} 分钟。${COMPLIANCE_NOTICE}`,
        audio_url: generalAudio.file_path,
        audio_name: generalAudio.filename,
        control_cmd: 'play',
        metadata: { sleep_disorder_subtype: 'GENERAL', use_scene, duration, severity }
      };
    }
    return {
      reply_text: '暂时无法找到适合您的音频，请稍后再试。' + COMPLIANCE_NOTICE
    };
  }

  // 构建回复话术
  const subtypeConfig = SLEEP_SUBTYPES[sleep_disorder_subtype];
  const subtypeName = subtypeConfig ? subtypeConfig.name : sleep_disorder_subtype;
  const sceneConfig = USE_SCENES[use_scene];
  const sceneName = sceneConfig ? sceneConfig.name : use_scene;

  let replyText = `已为您打开【${subtypeName}】${sceneName}脑波音频，时长 ${duration} 分钟。`;
  
  // 重度用户额外提示
  if (severity === 'SEVERE') {
    replyText += '\n由于您的睡眠困扰较为明显，建议同时咨询专业睡眠医师获取个性化诊疗方案。';
  }
  
  replyText += COMPLIANCE_NOTICE;

  return {
    reply_text: replyText,
    audio_url: audio.file_path,
    audio_name: audio.filename,
    control_cmd: 'play',
    metadata: { sleep_disorder_subtype, use_scene, duration, severity, age_group, gender, comorbidity }
  };
}

/**
 * 处理音频控制
 */
async function handleControlAudio(slots) {
  const { action } = slots;
  
  let control_cmd = 'play';
  let reply_text = '';

  // 脚本路径
  const mediaControlScript = "C:\\Users\\龚文瀚\\.openclaw\\workspace\\skills\\claw_health_brainwave_sleep\\scripts\\media_control.py";
  const { exec } = require('child_process');

  switch (action) {
    case 'pause':
      // 发送 Windows 媒体键暂停
      exec(`python "${mediaControlScript}" pause`, (err) => {
        if (err) console.error('Pause error:', err);
      });
      control_cmd = 'pause';
      reply_text = '已暂停播放。' + COMPLIANCE_NOTICE;
      break;
    case 'resume':
    case 'continue':
      // 发送 Windows 媒体键继续
      exec(`python "${mediaControlScript}" play`, (err) => {
        if (err) console.error('Resume error:', err);
      });
      control_cmd = 'resume';
      reply_text = '已继续播放。' + COMPLIANCE_NOTICE;
      break;
    case 'stop':
      // 发送 Windows 媒体键停止
      exec(`python "${mediaControlScript}" stop`, (err) => {
        if (err) console.error('Stop error:', err);
      });
      control_cmd = 'stop';
      reply_text = '已停止播放。' + COMPLIANCE_NOTICE;
      break;
    case 'volume_down':
      exec(`python "${mediaControlScript}" voldown`, (err) => {});
      reply_text = '已调小音量。' + COMPLIANCE_NOTICE;
      break;
    case 'volume_up':
      exec(`python "${mediaControlScript}" volup`, (err) => {});
      reply_text = '已调大音量。' + COMPLIANCE_NOTICE;
      break;
    case 'replay':
      control_cmd = 'replay';
      reply_text = '正在重新播放。' + COMPLIANCE_NOTICE;
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

  if (!duration || duration < 5 || duration > 120) {
    return { reply_text: '暂不支持该定时时长，请选择 15-60 分钟。' + COMPLIANCE_NOTICE };
  }

  return {
    reply_text: `好的，${duration} 分钟后将自动为您关闭音频，祝您好眠。`,
    timer: { duration_minutes: duration, action: 'stop' }
  };
}

/**
 * 处理切换音频
 */
async function handleSwitchAudio(user_id, slots, userProfile) {
  return await handlePlayAudio(user_id, slots, userProfile, {});
}

/**
 * 处理更新用户画像
 */
async function handleUpdateProfile(user_id, slots, userProfile) {
  const { sleep_disorder_subtype, severity, age_group, gender, comorbidity } = slots;
  
  // 更新画像
  const updatedProfile = { ...userProfile };
  
  if (sleep_disorder_subtype) updatedProfile.sleep_disorder_subtype = sleep_disorder_subtype;
  if (severity) updatedProfile.severity = severity;
  if (age_group) updatedProfile.age_group = age_group;
  if (gender) updatedProfile.gender = gender;
  if (comorbidity) updatedProfile.comorbidity = comorbidity;
  
  updatedProfile.update_time = new Date().toISOString();
  
  userProfiles[user_id] = updatedProfile;
  await saveProfiles();

  // 构建确认话术
  const parts = [];
  if (sleep_disorder_subtype) {
    const config = SLEEP_SUBTYPES[sleep_disorder_subtype];
    parts.push(`睡眠类型：${config ? config.name : sleep_disorder_subtype}`);
  }
  if (severity) {
    const config = SEVERITY_LEVELS[severity];
    parts.push(`严重程度：${config ? config.name : severity}`);
  }
  if (age_group) {
    const config = AGE_GROUPS[age_group];
    parts.push(`年龄：${config ? config.name : age_group}`);
  }
  if (gender) {
    const config = GENDERS[gender];
    parts.push(`性别：${config ? config.name : gender}`);
  }

  const reply = '好的，已记录您的信息：\n' + parts.join('，') + '。\n已为您重新匹配更适合的脑波音频。';

  return {
    reply_text: reply + '\n' + COMPLIANCE_NOTICE,
    user_profile: updatedProfile
  };
}

/**
 * 处理帮助查询
 */
function handleHelp() {
  return {
    reply_text: `您可以对我说：
「播放助眠脑波音频」「播放入睡困难脑波」「播放30分钟」
「我有焦虑失眠」「我60岁了」
「20分钟后自动关闭」「换一个音频」
「我失眠比较严重」

首次使用请告诉我您的睡眠问题类型、严重程度、年龄等信息，我会为您匹配合适的音频。
${COMPLIANCE_NOTICE}`
  };
}

/**
 * 处理退出技能
 */
function handleExit() {
  return {
    reply_text: '好的，已退出睡眠脑波声疗助手。如有需要随时呼唤我，祝您今晚好眠！',
    control_cmd: 'stop',
    exit_skill: true
  };
}

/**
 * 多维音频匹配算法
 */
async function matchAudio(subtype, scene, duration, severity, age_group, gender) {
  if (!audioManifest || !audioManifest.audio_files) {
    return null;
  }

  const files = audioManifest.audio_files;
  
  // 构建匹配键
  const subtypeKey = getSubtypeKey(subtype);
  const severityKey = getSeverityKey(severity);
  
  // 1. 精确匹配：亚型 + 严重程度
  let matched = files.filter(f => {
    return f.sleep_type && f.sleep_type.includes(subtypeKey) && 
           f.severity && f.severity.includes(severityKey);
  });

  // 2. 降级匹配：只匹配亚型
  if (matched.length === 0) {
    matched = files.filter(f => {
      return f.sleep_type && f.sleep_type.includes(subtypeKey);
    });
  }

  // 3. 降级到通用
  if (matched.length === 0) {
    matched = files.filter(f => {
      return f.sleep_type && f.sleep_type.includes('通用');
    });
  }

  // 4. 降级到任何睡眠音频
  if (matched.length === 0) {
    matched = files.filter(f => {
      return f.category === 'brainwave';
    });
  }

  return matched.length > 0 ? matched[0] : null;
}

function getSubtypeKey(subtype) {
  const map = {
    'SLEEP_ONSET': '入睡困难',
    'SLEEP_MAINTAIN': '易醒',
    'EARLY_WAKE': '早醒',
    'CIRCADIAN': '昼夜节律',
    'ANXIETY_SLEEP': '焦虑',
    'LIGHT_SLEEP': '浅眠',
    'GENERAL': '通用'
  };
  return map[subtype] || subtype;
}

function getSeverityKey(severity) {
  const map = {
    'MILD': '轻',
    'MODERATE': '中',
    'SEVERE': '重'
  };
  return map[severity] || severity;
}

module.exports = {
  handleIntent,
  SLEEP_SUBTYPES,
  SEVERITY_LEVELS,
  AGE_GROUPS,
  GENDERS,
  USE_SCENES,
  COMORBIDITIES,
  COMPLIANCE_NOTICE,
  AUDIO_LIBRARY_PATH
};
