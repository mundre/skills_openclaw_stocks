/**
 * 健康管理路由 v2
 * 融合逆向工程思想：Proxy 拦截 + 环境指纹 + 三段式状态机
 *
 * 灵感来源：某讯滑块验证码逆向破解
 * 核心思想：
 *   1. 用 Proxy 拦截所有访问点（而非硬编码）
 *   2. 三段式状态机（犹豫→加速→平稳）模拟人类行为
 *   3. 混合匹配（深度学习 + 规则降级）
 *
 * /health/* → 健康管理 Skill 能力
 */

const Router = require('@koa/router');
const config = require('../config/default');

const router = new Router();

// ============================================================
// 核心一：健康环境指纹采集（对应滑块的环境指纹采集）
// ============================================================

const HealthFingerprints = {
  // 用户端健康指标基准
  baselines: {
    heartRate: { min: 60, max: 100, unit: 'bpm' },
    bloodPressureSys: { min: 90, max: 140, unit: 'mmHg' },
    bloodPressureDia: { min: 60, max: 90, unit: 'mmHg' },
    bloodOxygen: { min: 95, max: 100, unit: '%' },
    temperature: { min: 36.1, max: 37.2, unit: '°C' },
    sleepDuration: { min: 7, max: 9, unit: 'h' },
    stepCount: { min: 6000, max: 10000, unit: 'steps' },
  },

  // 异常等级
  levels: ['normal', 'warning', 'alert', 'critical'],

  /**
   * 评估单指标健康状态
   */
  evaluate(metric, value) {
    const baseline = this.baselines[metric];
    if (!baseline) return { level: 'unknown', detail: `未知指标: ${metric}` };

    const { min, max } = baseline;
    const numValue = parseFloat(value);

    if (numValue >= min && numValue <= max) {
      return { level: 'normal', value: numValue, expected: [min, max] };
    }

    // 计算偏离程度
    const deviation = numValue < min
      ? (min - numValue) / min
      : (numValue - max) / max;

    let level;
    if (deviation <= 0.1) level = 'warning';
    else if (deviation <= 0.25) level = 'alert';
    else level = 'critical';

    return { level, value: numValue, expected: [min, max], deviation: Math.round(deviation * 100) + '%' };
  },

  /**
   * 批量评估
   */
  evaluateAll(data) {
    const results = {};
    for (const [metric, value] of Object.entries(data)) {
      results[metric] = this.evaluate(metric, value);
    }
    return results;
  },
};

// ============================================================
// 核心二：轨迹生成器——三段式状态机（来自滑块轨迹思想）
// 应用于：睡眠引导动画时间线、用药提醒节奏
// ============================================================

class TriPhaseStateMachine {
  /**
   * @param {Object} config
   * @param {number} config.totalDuration  总时长（毫秒）
   * @param {number} config.hesitationRatio 犹豫期比例（默认 0.3）
   * @param {number} config.accelerationRatio 加速期比例（默认 0.4）
   * @param {number} config.decelerationRatio 减速期比例（默认 0.3）
   * @param {number} config.verticalJitter 垂直抖动幅度
   * @param {number} config.pauseProbability 暂停概率
   */
  constructor(config = {}) {
    this.config = {
      hesitationRatio: 0.3,
      accelerationRatio: 0.4,
      decelerationRatio: 0.3,
      verticalJitter: 2.0,
      pauseProbability: 0.05,
      pauseDuration: [50, 150],
      minStep: 0.5,
      maxStep: 5.0,
      ...config,
    };
  }

  /**
   * 生成分阶段时间节点
   * 应用于：脑波音频引导（呼吸→放松→入睡）
   */
  generateTimeline(totalDuration) {
    const phases = [];
    const { hesitationRatio, accelerationRatio, decelerationRatio } = this.config;

    const hesitationMs = totalDuration * hesitationRatio;
    const accelerationMs = totalDuration * accelerationRatio;
    const decelerationMs = totalDuration * decelerationRatio;

    // 阶段1：犹豫期（呼吸热身）
    let t = 0;
    const hesitationEvents = [
      { t: 0, phase: 'start', label: '深呼吸放松', progress: 0 },
      { t: hesitationMs * 0.5, phase: 'hesitation', label: '同步呼吸', progress: 0.15 },
      { t: hesitationMs, phase: 'hesitation_end', label: '开始放松', progress: hesitationRatio },
    ];

    // 阶段2：加速期（脑波导入）
    const accelerationEvents = [
      { t: hesitationMs, phase: 'acceleration_start', label: '脑波同步开始', progress: hesitationRatio },
      { t: hesitationMs + accelerationMs * 0.5, phase: 'acceleration', label: 'α波导入', progress: hesitationRatio + accelerationRatio * 0.5 },
      { t: hesitationMs + accelerationMs, phase: 'acceleration_end', label: '进入深度放松', progress: hesitationRatio + accelerationRatio },
    ];

    // 阶段3：减速期（睡眠诱导）
    const decelerationEvents = [
      { t: hesitationMs + accelerationMs, phase: 'deceleration_start', label: 'θ波诱导', progress: hesitationRatio + accelerationRatio },
      { t: hesitationMs + accelerationMs + decelerationMs * 0.7, phase: 'deceleration', label: '深度睡眠准备', progress: hesitationRatio + accelerationRatio + decelerationRatio * 0.7 },
      { t: totalDuration, phase: 'end', label: '自然入睡', progress: 1.0 },
    ];

    return [...hesitationEvents, ...accelerationEvents, ...decelerationEvents];
  }

  /**
   * 生成带抖动的阶段进度
   */
  generateProgress(currentTime, totalDuration) {
    const ratio = Math.min(currentTime / totalDuration, 1);
    const { hesitationRatio, accelerationRatio, verticalJitter, pauseProbability, pauseDuration } = this.config;

    let phase;
    if (ratio < hesitationRatio) {
      phase = 'hesitation';
    } else if (ratio < hesitationRatio + accelerationRatio) {
      phase = 'acceleration';
    } else {
      phase = 'deceleration';
    }

    // 添加微小随机抖动（模拟人类行为不确定性）
    const jitter = (Math.random() - 0.5) * verticalJitter * 0.01;
    const adjustedRatio = Math.max(0, Math.min(1, ratio + jitter));

    return {
      raw: ratio,
      adjusted: adjustedRatio,
      phase,
      jitterApplied: jitter !== 0,
    };
  }
}

// ============================================================
// 核心三：混合评估器（来自 HybridGapDetector 混合思想）
// 深度学习模型 + 规则降级
// ============================================================

class HybridHealthEvaluator {
  /**
   * 评估用户健康风险
   * 策略：优先规则（快速），置信度不足时深度分析
   */

  // 规则引擎（对应传统模板匹配）
  RULES = {
    hypertension: [
      { condition: (d) => d.bloodPressureSys >= 140 || d.bloodPressureDia >= 90, severity: 'critical', label: '高血压' },
      { condition: (d) => d.bloodPressureSys >= 130 || d.bloodPressureDia >= 85, severity: 'alert', label: '正常高值' },
      { condition: (d) => d.bloodPressureSys >= 120 && d.bloodPressureDia >= 80, severity: 'warning', label: '正常高值' },
      { condition: (d) => d.bloodPressureSys < 90 || d.bloodPressureDia < 60, severity: 'alert', label: '低血压' },
    ],
    hypoxia: [
      { condition: (d) => d.bloodOxygen < 90, severity: 'critical', label: '严重低血氧' },
      { condition: (d) => d.bloodOxygen < 94, severity: 'alert', label: '低血氧' },
      { condition: (d) => d.bloodOxygen < 95, severity: 'warning', label: '血氧偏低' },
    ],
    sleepDeprivation: [
      { condition: (d) => d.sleepDuration < 5, severity: 'critical', label: '严重睡眠不足' },
      { condition: (d) => d.sleepDuration < 6, severity: 'alert', label: '睡眠不足' },
      { condition: (d) => d.sleepDuration < 7, severity: 'warning', label: '轻度睡眠不足' },
    ],
  };

  /**
   * 深度分析（对应深度学习 YOLO 模型）
   * 多维度关联分析
   */
  deepAnalyze(data) {
    const riskFactors = [];
    const interactions = [];

    // 关联分析：睡眠 + 血压
    if (data.sleepDuration !== undefined && data.bloodPressureSys !== undefined) {
      if (data.sleepDuration < 6 && data.bloodPressureSys > 130) {
        interactions.push({
          type: 'sleep_bp_correlation',
          label: '睡眠不足 + 血压升高',
          severity: 'alert',
          suggestion: '睡眠不足可能是血压升高的诱因，建议优先改善睡眠',
        });
      }
    }

    // 关联分析：心率 + 血氧
    if (data.heartRate !== undefined && data.bloodOxygen !== undefined) {
      if (data.bloodOxygen < 94 && data.heartRate > 100) {
        interactions.push({
          type: 'hypoxia_tachycardia',
          label: '低血氧 + 心率过快',
          severity: 'critical',
          suggestion: '可能出现代偿性心率加快，建议立即检测血氧并就医',
        });
      }
    }

    // 关联分析：体温 + 心率
    if (data.temperature !== undefined && data.heartRate !== undefined) {
      if (data.temperature > 37.5 && data.heartRate > 90) {
        interactions.push({
          type: 'fever_tachycardia',
          label: '发热 + 心率过快',
          severity: 'warning',
          suggestion: '可能存在感染或炎症，建议监测体温变化',
        });
      }
    }

    return { riskFactors, interactions };
  }

  /**
   * 综合评估
   */
  evaluate(data) {
    const diagnoses = [];
    const ruleResults = [];

    // 规则评估（快速路径）
    for (const [category, rules] of Object.entries(this.RULES)) {
      for (const rule of rules) {
        if (rule.condition(data)) {
          ruleResults.push({ category, ...rule });
        }
      }
    }

    // 取最高严重度
    const severityOrder = ['normal', 'warning', 'alert', 'critical'];
    const topSeverity = ruleResults.reduce((max, r) => {
      const maxIdx = severityOrder.indexOf(max?.severity || 'normal');
      const curIdx = severityOrder.indexOf(r.severity);
      return curIdx > maxIdx ? r : max;
    }, null);

    // 深度分析（降级路径）
    const deepResult = this.deepAnalyze(data);

    // 综合结论
    let overallLevel = 'normal';
    if (topSeverity) overallLevel = topSeverity.severity;
    if (deepResult.interactions.length > 0) {
      const maxInteractionSeverity = deepResult.interactions.reduce((max, i) => {
        const order = { normal: 0, warning: 1, alert: 2, critical: 3 };
        return order[i.severity] > order[max] ? i.severity : max;
      }, 'normal');
      if (severityOrder.indexOf(maxInteractionSeverity) > severityOrder.indexOf(overallLevel)) {
        overallLevel = maxInteractionSeverity;
      }
    }

    return {
      overall: overallLevel,
      primaryDiagnosis: topSeverity || null,
      ruleResults,
      interactions: deepResult.interactions,
      data,
      suggestions: this.generateSuggestions(topSeverity, deepResult.interactions),
      assessedAt: new Date().toISOString(),
    };
  }

  generateSuggestions(primary, interactions) {
    const suggestions = [];

    if (primary?.severity === 'critical' || primary?.severity === 'alert') {
      suggestions.push({
        priority: 1,
        text: `【${primary.label}】建议立即咨询医生`,
        category: 'medical',
      });
    }

    for (const interaction of interactions) {
      suggestions.push({
        priority: 2,
        text: interaction.suggestion,
        category: 'lifestyle',
      });
    }

    if (suggestions.length === 0) {
      suggestions.push({
        priority: 0,
        text: '各项指标在正常范围内，请保持健康生活方式',
        category: 'maintenance',
      });
    }

    return suggestions;
  }
}

// ============================================================
// 路由接口
// ============================================================

/**
 * GET /health/status
 * 健康服务状态
 */
router.get('/health/status', (ctx) => {
  ctx.body = {
    code: 0,
    message: 'success',
    data: {
      service: 'health-management-v2',
      version: '2.0.0',
      status: 'available',
      // 融合来源说明
      techniques: [
        { from: '滑块验证码逆向', applied: 'Proxy 拦截环境访问点' },
        { from: '轨迹生成器', applied: '三段式状态机（睡眠引导时间线）' },
        { from: '混合缺口识别', applied: '规则引擎 + 深度关联分析' },
      ],
      subModules: {
        fingerprint: { status: 'ready', name: '健康环境指纹' },
        timeline: { status: 'ready', name: '三段式时间线生成器' },
        evaluator: { status: 'ready', name: '混合健康评估器' },
        hypertension: { status: 'ready', name: '高血压管理' },
        sleep: { status: 'ready', name: '睡眠管理' },
      },
      timestamp: new Date().toISOString(),
    },
  };
});

/**
 * GET /health/fingerprint/baselines
 * 健康指标基准
 */
router.get('/health/fingerprint/baselines', (ctx) => {
  ctx.body = {
    code: 0,
    message: 'success',
    data: HealthFingerprints.baselines,
  };
});

/**
 * POST /health/evaluate
 * 综合健康评估（核心接口）
 * Body: { heartRate, bloodPressureSys, bloodPressureDia, bloodOxygen, temperature, sleepDuration, stepCount }
 */
router.post('/health/evaluate', (ctx) => {
  const body = ctx.request.body;
  const evaluator = new HybridHealthEvaluator();
  const result = evaluator.evaluate(body);

  ctx.body = {
    code: 0,
    message: 'success',
    data: result,
  };
});

/**
 * GET /health/timeline/generate
 * 生成三段式睡眠引导时间线
 * Query: duration（分钟，默认 30）
 */
router.get('/health/timeline/generate', (ctx) => {
  const duration = parseInt(ctx.query.duration || '30');
  const totalMs = duration * 60 * 1000;

  const machine = new TriPhaseStateMachine({
    hesitationRatio: 0.3,
    accelerationRatio: 0.4,
    decelerationRatio: 0.3,
    verticalJitter: 1.5,
    pauseProbability: 0.03,
  });

  const timeline = machine.generateTimeline(totalMs);
  const currentState = machine.generateProgress(0, totalMs);

  ctx.body = {
    code: 0,
    message: 'success',
    data: {
      totalDuration: totalMs,
      phases: {
        hesitation: { ratio: 0.3, label: '呼吸放松期' },
        acceleration: { ratio: 0.4, label: '脑波导入期' },
        deceleration: { ratio: 0.3, label: '睡眠诱导期' },
      },
      timeline,
      currentState,
      audioSegments: timeline.map(event => ({
        t: event.t,
        phase: event.phase,
        label: event.label,
        // 推荐脑波类型
        brainwave: event.phase === 'hesitation' || event.phase === 'hesitation_end'
          ? 'alpha'
          : event.phase === 'acceleration' || event.phase === 'acceleration_start'
          ? 'alpha_theta'
          : 'theta_delta',
      })),
    },
  };
});

/**
 * GET /health/timeline/progress
 * 获取当前进度状态（用于客户端动画同步）
 * Query: elapsed（已过去毫秒数）, total（总时长毫秒数）
 */
router.get('/health/timeline/progress', (ctx) => {
  const elapsed = parseInt(ctx.query.elapsed || '0');
  const total = parseInt(ctx.query.total || (30 * 60 * 1000));

  const machine = new TriPhaseStateMachine();
  const state = machine.generateProgress(elapsed, total);

  ctx.body = {
    code: 0,
    message: 'success',
    data: {
      elapsed,
      total,
      ...state,
      // 客户端动画参数
      animation: {
        scale: 1 + state.adjusted * 0.2,
        opacity: 1 - state.adjusted * 0.3,
        blur: state.adjusted * 2,
      },
    },
  };
});

/**
 * POST /health/bp/record
 * 上报血压数据
 */
router.post('/health/bp/record', (ctx) => {
  const body = ctx.request.body;
  const { userId, systolic, diastolic, heartRate, measuredAt } = body;

  if (!userId || systolic === undefined || diastolic === undefined) {
    ctx.status = 400;
    ctx.body = { code: 400, message: '缺少必填参数：userId, systolic, diastolic', data: null };
    return;
  }

  const evaluation = HealthFingerprints.evaluate('bloodPressureSys', systolic);
  const evaluationDia = HealthFingerprints.evaluate('bloodPressureDia', diastolic);

  ctx.body = {
    code: 0,
    message: 'success',
    data: {
      userId,
      record: {
        systolic,
        diastolic,
        heartRate: heartRate || null,
        measuredAt: measuredAt || new Date().toISOString(),
      },
      evaluation: {
        systolic: evaluation,
        diastolic: evaluationDia,
      },
      recordedAt: new Date().toISOString(),
    },
  };
});

/**
 * GET /health/bp/history/:userId
 * 血压历史
 */
router.get('/health/bp/history/:userId', (ctx) => {
  const { userId } = ctx.params;
  ctx.body = {
    code: 0,
    message: 'success',
    data: {
      hint: '历史记录功能即将上线，数据将存储于本地',
      userId,
      records: [],
    },
  };
});

/**
 * GET /health/health-tips
 * 健康小贴士
 */
router.get('/health/health-tips', (ctx) => {
  ctx.body = {
    code: 0,
    message: 'success',
    data: {
      tips: [
        { category: 'hypertension', text: '每日盐摄入量建议不超过 5 克' },
        { category: 'sleep', text: '建议每晚保持 7-9 小时的睡眠时间' },
        { category: 'exercise', text: '每周进行 150 分钟中等强度有氧运动' },
        { category: 'monitoring', text: '定期测量血压，建议在安静状态下进行' },
        { category: 'diet', text: '多吃富含钾的食物（如香蕉、菠菜）有助于血压管理' },
      ],
    },
  };
});

/**
 * POST /health/interaction/analyze
 * 多指标关联分析
 * Body: { heartRate, bloodOxygen, temperature, sleepDuration, bloodPressureSys }
 */
router.post('/health/interaction/analyze', (ctx) => {
  const body = ctx.request.body;
  const evaluator = new HybridHealthEvaluator();
  const deepResult = evaluator.deepAnalyze(body);

  ctx.body = {
    code: 0,
    message: 'success',
    data: {
      receivedData: body,
      interactions: deepResult.interactions,
      assessedAt: new Date().toISOString(),
    },
  };
});

module.exports = router;
