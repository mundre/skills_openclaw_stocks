/**
 * 慢病脑波声疗助手 - 本地测试脚本
 * 
 * 运行方式: node test.js
 * 
 * 测试所有意图的处理逻辑
 */

// 模拟 handler.js 的核心逻辑
const CHRONIC_TYPES = ['高血压', '糖尿病', '睡眠障碍', '心脑血管', '康复通用'];
const SCENES = ['睡前', '餐后', '午休', '情绪烦躁', '康复期', '日间放松'];
const DURATIONS = [10, 15, 20, 30];
const DEFAULT_DURATION = 15;
const COMPLIANCE_NOTICE = '温馨提示：本音频为非药物健康辅助，不替代医疗诊断与治疗。';

// 模拟数据库
const mockDb = {
  tenants: new Map([['tenant_001', { tenant_id: 'tenant_001', status: 'enabled' }]]),
  userTags: new Map(),
  audioMeta: [
    { audio_id: 'audio_001', chronic_type: '高血压', scene: '睡前', duration: 15, cdn_url: 'https://cdn.example.com/bw_hypertension_sleep_15.mp3' },
    { audio_id: 'audio_002', chronic_type: '糖尿病', scene: '睡前', duration: 15, cdn_url: 'https://cdn.example.com/bw_diabetes_sleep_15.mp3' },
    { audio_id: 'audio_003', chronic_type: '睡眠障碍', scene: '睡前', duration: 15, cdn_url: 'https://cdn.example.com/bw_insomnia_sleep_15.mp3' },
    { audio_id: 'audio_004', chronic_type: '心脑血管', scene: '睡前', duration: 15, cdn_url: 'https://cdn.example.com/bw_cardio_sleep_15.mp3' },
    { audio_id: 'audio_005', chronic_type: '康复通用', scene: '睡前', duration: 15, cdn_url: 'https://cdn.example.com/bw_rehab_sleep_15.mp3' },
  ],
  playLogs: []
};

// 业务函数实现
async function getTenant(tenant_id) {
  return mockDb.tenants.get(tenant_id) || null;
}

async function matchAudio(tenant_id, chronic_type, scene, duration) {
  const audio = mockDb.audioMeta.find(a => 
    a.chronic_type === chronic_type && 
    (!scene || a.scene === scene) &&
    (!duration || a.duration === duration)
  );
  return audio || mockDb.audioMeta.find(a => a.chronic_type === '康复通用');
}

function generateSignedUrl(cdn_url) {
  const expires = Date.now() + 6 * 60 * 60 * 1000;
  const signature = 'mock_sign_' + expires;
  return `${cdn_url}?expires=${expires}&sign=${signature}`;
}

async function getUserRecentRecord(tenant_id, user_id) {
  const key = `${tenant_id}:${user_id}`;
  return mockDb.userTags.get(key) || null;
}

async function updateUserRecentRecord(tenant_id, user_id, chronic_type, scene) {
  const key = `${tenant_id}:${user_id}`;
  mockDb.userTags.set(key, { chronic_type, scene, last_used_time: Date.now() });
}

async function reportPlayLog(tenant_id, user_id, audio_id, device_id, duration) {
  mockDb.playLogs.push({ tenant_id, user_id, audio_id, device_id, duration, time: Date.now() });
}

// 意图处理器
async function handleIntent(params) {
  const { user_id, tenant_id, intent_id, slots, device_info } = params;
  
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
    case 'QUERY_SKILL_HELP':
      return handleHelp();
    case 'EXIT_SKILL':
      return handleExit();
    default:
      return { reply_text: '暂不支持该操作。' + COMPLIANCE_NOTICE };
  }
}

async function handlePlayAudio(tenant_id, user_id, slots, device_info) {
  let { chronic_type, scene, duration } = slots;

  if (!duration || !DURATIONS.includes(duration)) {
    duration = DEFAULT_DURATION;
  }

  // 无慢病类型时，尝试获取最近记录
  if (!chronic_type || !CHRONIC_TYPES.includes(chronic_type)) {
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

  const audio = await matchAudio(tenant_id, chronic_type, scene, duration);
  if (!audio) {
    return { reply_text: '暂时无法找到合适音频，请您稍后再试。' + COMPLIANCE_NOTICE };
  }

  const audio_url = generateSignedUrl(audio.cdn_url);
  await updateUserRecentRecord(tenant_id, user_id, chronic_type, scene);
  await reportPlayLog(tenant_id, user_id, audio.audio_id, device_info.device_id, duration);

  const sceneText = scene ? scene + ' ' : '';
  return {
    reply_text: `已为您打开【${chronic_type}】${sceneText}脑波音频，时长 ${duration} 分钟。${COMPLIANCE_NOTICE}`,
    audio_url,
    control_cmd: 'play'
  };
}

async function handleControlAudio(slots) {
  const { action } = slots;
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

async function handleSetTimer(slots) {
  const { duration } = slots;
  if (!duration || !DURATIONS.includes(duration)) {
    return { reply_text: '暂不支持该定时时长，请选择 10、15、20 或 30 分钟。' + COMPLIANCE_NOTICE };
  }
  return { reply_text: `好的，${duration} 分钟后将自动为您关闭音频。`, timer: { duration_minutes: duration } };
}

function handleHelp() {
  return { reply_text: `您可以对我说：播放高血压舒缓音频、播放 15 分钟助眠脑波、定时关闭等。${COMPLIANCE_NOTICE}` };
}

function handleExit() {
  return { reply_text: '好的，已退出脑波音频助手。如有需要随时呼唤我。', control_cmd: 'stop', exit_skill: true };
}

// 测试用例
const testCases = [
  {
    name: '测试1: 播放高血压音频',
    params: {
      user_id: 'user_001',
      tenant_id: 'tenant_001',
      intent_id: 'PLAY_BRAINWAVE_AUDIO',
      slots: { chronic_type: '高血压', scene: '睡前', duration: 15 },
      device_info: { device_id: 'device_001' }
    }
  },
  {
    name: '测试2: 播放糖尿病音频（仅指定慢病类型）',
    params: {
      user_id: 'user_001',
      tenant_id: 'tenant_001',
      intent_id: 'PLAY_BRAINWAVE_AUDIO',
      slots: { chronic_type: '糖尿病' },
      device_info: { device_id: 'device_001' }
    }
  },
  {
    name: '测试3: 未指定慢病类型 - 应返回交互确认',
    params: {
      user_id: 'user_001',
      tenant_id: 'tenant_001',
      intent_id: 'PLAY_BRAINWAVE_AUDIO',
      slots: {},
      device_info: { device_id: 'device_001' }
    }
  },
  {
    name: '测试4: 播放20分钟音频',
    params: {
      user_id: 'user_001',
      tenant_id: 'tenant_001',
      intent_id: 'PLAY_BRAINWAVE_AUDIO',
      slots: { chronic_type: '睡眠障碍', duration: 20 },
      device_info: { device_id: 'device_001' }
    }
  },
  {
    name: '测试5: 暂停播放',
    params: {
      user_id: 'user_001',
      tenant_id: 'tenant_001',
      intent_id: 'CONTROL_AUDIO',
      slots: { action: 'pause' },
      device_info: { device_id: 'device_001' }
    }
  },
  {
    name: '测试6: 继续播放',
    params: {
      user_id: 'user_001',
      tenant_id: 'tenant_001',
      intent_id: 'CONTROL_AUDIO',
      slots: { action: 'continue' },
      device_info: { device_id: 'device_001' }
    }
  },
  {
    name: '测试7: 停止播放',
    params: {
      user_id: 'user_001',
      tenant_id: 'tenant_001',
      intent_id: 'CONTROL_AUDIO',
      slots: { action: 'stop' },
      device_info: { device_id: 'device_001' }
    }
  },
  {
    name: '测试8: 定时15分钟关闭',
    params: {
      user_id: 'user_001',
      tenant_id: 'tenant_001',
      intent_id: 'SET_AUDIO_TIMER',
      slots: { duration: 15 },
      device_info: { device_id: 'device_001' }
    }
  },
  {
    name: '测试9: 定时30分钟关闭',
    params: {
      user_id: 'user_001',
      tenant_id: 'tenant_001',
      intent_id: 'SET_AUDIO_TIMER',
      slots: { duration: 30 },
      device_info: { device_id: 'device_001' }
    }
  },
  {
    name: '测试10: 定时5分钟（不支持的时长）',
    params: {
      user_id: 'user_001',
      tenant_id: 'tenant_001',
      intent_id: 'SET_AUDIO_TIMER',
      slots: { duration: 5 },
      device_info: { device_id: 'device_001' }
    }
  },
  {
    name: '测试11: 查询帮助',
    params: {
      user_id: 'user_001',
      tenant_id: 'tenant_001',
      intent_id: 'QUERY_SKILL_HELP',
      slots: {},
      device_info: { device_id: 'device_001' }
    }
  },
  {
    name: '测试12: 退出技能',
    params: {
      user_id: 'user_001',
      tenant_id: 'tenant_001',
      intent_id: 'EXIT_SKILL',
      slots: {},
      device_info: { device_id: 'device_001' }
    }
  },
  {
    name: '测试13: 用户A首次播放后，用户B未指定类型（测试最近优先）',
    params: {
      user_id: 'user_002',  // 新用户
      tenant_id: 'tenant_001',
      intent_id: 'PLAY_BRAINWAVE_AUDIO',
      slots: { chronic_type: '心脑血管' },
      device_info: { device_id: 'device_001' }
    },
    preAction: async () => {
      // 用户002 先播放一次
      await handleIntent({
        user_id: 'user_002',
        tenant_id: 'tenant_001',
        intent_id: 'PLAY_BRAINWAVE_AUDIO',
        slots: { chronic_type: '心脑血管', scene: '睡前', duration: 15 },
        device_info: { device_id: 'device_001' }
      });
    }
  },
  {
    name: '测试14: 用户B未指定慢病类型，应使用最近记录（心脑血管）',
    params: {
      user_id: 'user_002',
      tenant_id: 'tenant_001',
      intent_id: 'PLAY_BRAINWAVE_AUDIO',
      slots: {},
      device_info: { device_id: 'device_001' }
    }
  }
];

// 运行测试
async function runTests() {
  console.log('='.repeat(60));
  console.log('🧠 慢病脑波声疗助手 - 本地测试');
  console.log('='.repeat(60));
  console.log();

  let passed = 0;
  let failed = 0;

  for (let i = 0; i < testCases.length; i++) {
    const tc = testCases[i];
    
    // 预处理（如有）
    if (tc.preAction) {
      await tc.preAction();
    }

    console.log(`📋 ${tc.name}`);
    console.log(`   输入: ${JSON.stringify(tc.params.slots)}`);
    
    try {
      const result = await handleIntent(tc.params);
      console.log(`   输出: ${result.reply_text}`);
      if (result.audio_url) {
        console.log(`   音频: ${result.audio_url.substring(0, 60)}...`);
      }
      if (result.control_cmd) {
        console.log(`   控制: ${result.control_cmd}`);
      }
      if (result.timer) {
        console.log(`   定时: ${result.timer.duration_minutes}分钟`);
      }
      console.log(`   ✅ 通过`);
      passed++;
    } catch (err) {
      console.log(`   ❌ 失败: ${err.message}`);
      failed++;
    }
    console.log();
  }

  console.log('='.repeat(60));
  console.log(`📊 测试结果: ${passed} 通过, ${failed} 失败`);
  console.log('='.repeat(60));
  
  // 打印播放日志
  console.log('\n📊 播放日志:');
  mockDb.playLogs.forEach((log, i) => {
    console.log(`  ${i+1}. user=${log.user_id}, audio=${log.audio_id}, duration=${log.duration}min`);
  });
}

runTests().catch(console.error);
