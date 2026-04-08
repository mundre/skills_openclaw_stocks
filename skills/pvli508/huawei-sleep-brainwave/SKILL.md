---
name: huawei-sleep-brainwave
description: "华为手表睡眠数据驱动的脑波音频适配技能。当用户提到睡眠分析、睡眠报告、睡眠洞察、华为手表睡眠数据、睡眠问题识别、或需要基于睡眠监测数据获取个性化脑波音频改善方案时触发。功能：(1)获取华为手表监测数据（2）基于ICSD-3/DSM-5识别睡眠问题（3）关联脑区与神经机制（4）适配针对性脑波音频。需同时加载references/目录下的医学映射参考文件。"
metadata:
  compliance:
    - type: non-diagnosis
      description: "绝不进行诊断、治疗或开具处方。所有分析基于可穿戴设备数据，仅供健康辅助参考，非医学诊断。医疗问题始终建议咨询医疗专业人员。"
    - type: medical-disclaimer
      description: "必须附加标准免责声明：'以上为指标异常提示，非医学诊断。具体情况因人而异，建议咨询医生获取专业评估。'"
    - type: professional-referral
      triggers:
        - "症状持续时间超出预期"
        - "出现令人担忧的模式变化"
        - "血氧持续偏低 SpO2<90%"
        - "严重打鼾或呼吸暂停"
        - "白天严重嗜睡 ESS>10"
        - "心理健康相关严重失眠"
---

# 华为手表睡眠脑波适配技能 🎧

## 核心流程

```
数据获取 → 医学映射分析 → 问题识别 → 脑区关联 → 音频适配 → 播放方案
```

---

## Step 1: 获取睡眠数据

### 数据来源（按优先级）

1. **本地 JSON 文件**（必选）
   - 路径提示：`memory/huawei-sleep-*.json` 或用户指定路径
   - 格式见 `references/huawei-sleep-indicators.md`

2. **华为 Health Connect API**（如已配置）
   - OAuth2 授权，端点：`/v1/sleepRecords`

3. **用户手动输入**
   - 当文件不可用时，引导用户提供关键指标

### 华为10大睡眠指标

参见 `references/huawei-sleep-indicators.md`

### 数据校验

| 字段 | 默认值 | 说明 |
|------|--------|------|
| `all_sleep_time` | 420min | 总睡眠时长 |
| `deep_sleep_rate` | 20% | 深睡占比（正常≥15%） |
| `light_sleep_rate` | 50% | 浅睡占比 |
| `rem_sleep_rate` | 25% | REM占比（正常20-25%） |
| `awake_time` | 20min | 夜间清醒时长 |
| `wakeup_count` | 3次 | 夜间清醒次数 |
| `sleep_score` | 80 | 综合睡眠得分 |
| `sleep_latency` | 跳过 | 入睡时长（值为0跳过此项） |
| `first_sleep_mins` | 90min | 第一觉时长 |
| `snoring_count` | 0 | 打鼾次数（如有） |
| `avg_spo2` | 96% | 平均血氧 |
| `low_spo2_duration` | 0min | 低血氧持续时长 |
| `user_profile.age` | 需询问 | 用于个性化 |

---

## Step 2: 睡眠问题识别（ICSD-3 / DSM-5 映射）

### 评估规则

参见 `references/sleep-disorder-mapping.md`

| 睡眠问题 | 检测条件 | 严重度计算 |
|----------|----------|------------|
| **慢性失眠** | wakeup_count≥3 + awake_time≥30min + 持续≥3个月数据 | 三指标加权 |
| **入睡困难** | sleep_latency > 30min 且 ≠ 0 | 超30部分×2 |
| **睡眠片段化** | wakeup_count > 3 或 awake_time > 30 | 次数×15 + 时长×0.5 |
| **深睡不足** | deep_sleep_rate < 15% | (15-实际值)×5 |
| **REM异常** | rem_sleep_rate < 20% 或 > 30% | 偏离正常值×5 |
| **浅睡过多** | light_sleep_rate > 55% 且 deep_sleep_rate < 15% | 复合指标 |
| **早醒** | endTime < 06:00 且 all_sleep_time < 360 | 时间差×25 |
| **睡眠效率低** | (all_sleep_time / time_in_bed) < 85% | 效率差×100 |
| **第一觉短** | first_sleep_mins < 90min | (90-实际值)×1.5 |
| **血氧偏低** | avg_spo2 < 94% 或 low_spo2_duration > 30min | 复合指标 |

### 问题排序

- 按严重度得分降序排列
- 仅保留得分 > 15 的问题
- 最多返回 **Top 3** 问题
- 多日数据取平均值或趋势分析

### 输出格式

```
📊 睡眠问题分析结果（参照ICSD-3 / DSM-5）

【问题1】深睡不足（可能关联慢性失眠的维持因素）
  关注度: 78/100
  检测指标：深睡占比 8%（ICSD-3参考值≥15%）
  可能脑区：额叶皮层（Prefrontal Cortex）—慢波生成能力下降
  说明：个体差异较大，仅供参考

【问题2】睡眠片段化
  关注度: 52/100
  检测指标：夜间觉醒 4 次（共 38 分钟）
  可能脑区：下丘脑视交叉上核（SCN）—昼夜节律调节不稳定
  说明：可能受多种因素影响

⚠️ 以上为指标异常提示，非医学诊断。具体情况因人而异，建议咨询医生获取专业评估。
```

---

## Step 3: 用户交互确认

### 交互逻辑

```
IF 问题数量 == 0:
    → 睡眠质量良好，提供日常保养建议
    → 推荐通用助眠音频

ELIF 问题数量 >= 1:
    → 展示 Top 3 问题
    → "检测到主要问题：【问题1】优先改善，是否同意？（回复数字选择或"全部"）"
    → 用户确认后进入 Step 4
```

### 专业转介触发

出现以下情况时主动建议就医：

| 触发条件 | 建议话术 |
|----------|----------|
| 症状持续 > 3个月无改善 | "您的睡眠问题持续较久，建议咨询专业医生评估。" |
| 指标突然恶化 > 30% | "我们注意到您的指标近期有明显变化，建议您咨询医生。" |
| 血氧 SpO2 多次 < 90% | "您的血氧数据偏低，建议尽快就医排除呼吸系统问题。" |
| 严重打鼾/呼吸暂停 | "打鼾和呼吸暂停可能提示阻塞性睡眠呼吸暂停，建议做专业评估。" |
| ESS > 10 持续存在 | "白天嗜睡可能影响安全，建议咨询医生。" |
| 伴随情绪低落/焦虑 | "长期失眠可能影响心理健康，建议咨询医生或心理咨询师。" |

---

## Step 4: 脑区关联与音频适配

### 脑区-睡眠问题-音频映射

参见 `references/brain-region-mapping.md` 和 `references/audio-mapping.md`

| 睡眠问题 | 相关脑区 | 神经机制 | 推荐脑波音频 |
|----------|----------|----------|-------------|
| 深睡不足 | 前额叶皮层、丘脑 | 慢波生成能力↓，Delta振荡减弱 | Delta波（0.5-4Hz）|
| 入睡困难 | 视交叉上核（SCN）、视前区 | 昼夜节律相位前移，褪黑素分泌延迟 | Alpha-Theta波（8-12Hz + 4-8Hz）|
| 睡眠片段化 | 下丘脑、蓝斑 | 觉醒系统抑制不足，肾上腺素水平高 | Theta波（4-8Hz）+ 连续性音频 |
| REM异常 | 桥脑、蓝斑 | REM-on/REM-off神经元失衡 | Alpha波稳态（8-12Hz）|
| 早醒 | 前额叶、杏仁核 | 皮质醇早峰，应激反应提前 | Delta波延续 + 皮质醇抑制音频 |
| 浅睡过多 | 丘脑皮层环路 | 感觉门控异常，感觉信息持续输入 | Delta波增强 + 感觉屏蔽音频 |
| 焦虑失眠 | 杏仁核、前扣带回 | 过度激活，高皮质醇 | Theta-Alpha波（6-10Hz）+ 呼吸引导 |

### 个性化调整（多维度）

参见 `references/audio-mapping.md#personalization`

| 维度 | 适配规则 |
|------|----------|
| 年龄 > 60 | 增加低频 Delta（0.5-2Hz）比例 |
| 年龄 < 30 | 可适度增加 Theta（4-8Hz）|
| 性别 | 考虑荷尔蒙对睡眠结构影响（女性可增加Theta）|
| 问题严重度 | 得分>70：使用纯单一频率；得分30-70：复合频率 |
| 历史偏好 | 查询 `memory/*-sleep-feedback.json`，优先同类音频 |

---

## Step 5: 音频推荐输出

```
🎧 为您个性化适配的脑波音频方案

【优先改善】深睡不足
【关联脑区】前额叶皮层 — Delta波生成能力下降
【神经机制】慢波睡眠期间皮层振荡减弱，深睡恢复效应不足

【推荐方案】
  方案：增强型Delta波 · 30分钟 · 动态渐变
  原理：0.5-2Hz低频Delta持续刺激前额叶，增强皮层超极化
  个性化：年龄35岁 → 适度保留4-6Hz低Theta成分（效果因人而异）

【音频标签】delta-enhanced, deep-sleep, 30min
【参考音频】delta-deep-sleep-30min（见 manifest.json）

⚠️ 本音频方案为健康辅助参考，不能替代医疗干预。如有严重睡眠问题，请咨询医生。

🔗 [点击播放脑波音频]
```

---

## Step 6: 播放与反馈

### 播放执行

- 调用 `claw-health-brainwave` 技能的播放逻辑
- 传递参数：`chronic_type=sleep障碍`, `scene=睡前`, `duration=30`

### 反馈收集

播放后询问效果，将反馈记录到 `memory/YYYY-MM-DD-sleep-feedback.json`：

```json
{
  "date": "2026-04-02",
  "problems": ["深睡不足", "睡眠片段化"],
  "audio_id": "delta-deep-sleep-30min",
  "feedback": "positive|neutral|negative",
  "note": "用户可选补充"
}
```

---

## 合规声明（每次回复必须附加）

> ⚠️ **免责声明**：本分析基于可穿戴设备数据，非医学诊断。ICSD-3/DSM-5分类仅供专业参考，不能替代医疗评估。个体差异可能使结果与实际情况存在偏差。如有疑虑，请咨询专业医疗人员。

---

## 参考文件

- `references/huawei-sleep-indicators.md` — 华为10大睡眠指标详解
- `references/sleep-disorder-mapping.md` — ICSD-3 / DSM-5 睡眠障碍分类映射
- `references/brain-region-mapping.md` — 脑区-睡眠问题-神经机制映射
- `references/audio-mapping.md` — 脑波音频类型与个性化适配规则
