# 脑波音频类型与个性化适配规则

## 音频分类体系

### 脑波音频类型

| 音频ID | 类型 | 频率范围 | 主要刺激脑区 | 目标睡眠问题 |
|--------|------|----------|-------------|-------------|
| `delta-enhanced` | Delta增强型 | 0.5-4 Hz | 前额叶皮层、丘脑 | 深睡不足 |
| `delta-low` | 低频Delta | 0.5-2 Hz | 前额叶皮层 | 老年人深睡不足 |
| `theta-relaxation` | Theta放松型 | 4-8 Hz | 杏仁核、VLPO | 入睡困难、焦虑 |
| `alpha-theta` | Alpha-Theta混合 | 8-12 Hz + 4-8 Hz | SCN、VLPO | 睡眠过渡、入睡困难 |
| `alpha-steady` | Alpha稳态 | 8-12 Hz 纯音 | 枕叶皮层、SCN | REM不足、日间嗜睡 |
| `theta-alpha-transition` | Theta-Alpha过渡 | 6-10 Hz | 杏仁核、扣带回 | 焦虑失眠、情绪性失眠 |
| `delta-continuity` | Delta延续型 | 0.5-4 Hz（连续）| 皮层广泛 | 早醒、睡眠片段化 |
| `sleep-spindle` | 睡眠纺锤波 | 12-14 Hz | 丘脑 | 浅睡过多、记忆巩固 |
| `gamma-motor` | 低频Gamma | 30-40 Hz（低强度）| 运动皮层 | 不宁腿综合征 |
| `breathing-entrain` | 呼吸 entrain型 | 4-7 Hz（随呼吸调节）| 迷走神经、杏仁核 | 焦虑、觉醒过多 |

---

## 音频库清单（参照现有 manifest.json）

> 注：以下为音频标签体系，实际音频文件托管于云端COS。音频通过 `claw-health-brainwave` 技能播放，调用 manifest.json 中的URL映射。

### 按场景分类

**睡前（Sleep Onset）**
| 标签 | 时长 | 适用问题 | 脑波类型 |
|------|------|---------|---------|
| `sleep-onset-theta` | 20min | 入睡困难 | Theta 4-8Hz |
| `sleep-onset-alpha-theta` | 30min | 过渡期长 | Alpha-Theta |
| `relaxation-pre-sleep` | 15min | 焦虑、过度思考 | Theta-Alpha 6-10Hz |

**睡眠维持（Sleep Continuity）**
| 标签 | 时长 | 适用问题 | 脑波类型 |
|------|------|---------|---------|
| `deep-sleep-delta` | 30min | 深睡不足 | Delta 0.5-4Hz |
| `deep-sleep-enhanced` | 45min | 严重深睡不足 | Delta + 低Theta |
| `continuity-support` | 整夜 | 片段化、早醒 | Delta连续波 |
| `early-morning-extend` | 20min | 早醒后 | Delta延续 |

**深度恢复（Recovery）**
| 标签 | 时长 | 适用问题 | 脑波类型 |
|------|------|---------|---------|
| `rem-support` | 30min | REM不足 | Alpha稳态 |
| `memory-consolidation` | 30min | 记忆巩固 | Sleep Spindle 12-14Hz |

---

## 个性化适配规则

### 1. 按年龄适配

| 年龄段 | 适配规则 | 原因 |
|--------|----------|------|
| < 30岁 | 可适度增加Theta比例（4-8Hz）| 年轻人Theta反应更活跃 |
| 30-60岁 | 标准Delta-Alpha配比 | 均衡方案 |
| > 60岁 | 增加低频Delta（0.5-2Hz）比例 | 随年龄深睡自然衰退，需更强刺激 |

### 2. 按性别适配（荷尔蒙影响）

| 情况 | 适配规则 | 原因 |
|------|----------|------|
| 女性（一般）| 可适度增加Theta | 雌激素对睡眠结构有调节作用 |
| 女性（围绝经期）| 增加Alpha-Theta，辅助呼吸引导 | 潮热/盗汗影响睡眠连续性 |
| 男性（一般）| 标准方案 | — |

### 3. 按问题严重度适配

| 严重度 | 得分范围 | 适配规则 |
|--------|----------|----------|
| 轻度 | 15-30 | 单频脑波即可，避免过度刺激 |
| 中度 | 30-70 | 复合频率，选择主导频率 |
| 重度 | > 70 | 纯单频 + 较长时长（45-60min）|

### 4. 按历史反馈适配

查询路径：`memory/*-sleep-feedback.json`

```json
{
  "date": "2026-04-01",
  "problems": ["深睡不足"],
  "audio_id": "delta-enhanced-30min",
  "feedback": "positive",
  "note": "深睡感明显增强"
}
```

**反馈适配规则**：
| 历史反馈 | 适配动作 |
|----------|----------|
| positive（≥3次同一类型）| 优先推荐同类音频 |
| neutral | 尝试调整频率或增加时长 |
| negative | 切换到不同脑波类型 |

### 5. 按数据特征适配（华为指标组合）

| 指标组合 | 推荐音频 | 理由 |
|----------|---------|------|
| 深睡↓ + 第一觉短 | `sleep-onset-alpha-theta`（30min）→ `deep-sleep-delta`（30min）| 先稳定入睡导入，再增强深睡 |
| 深睡↓ + 觉醒多 | `delta-continuity`（整夜或60min）| 连续Delta覆盖夜间，维持深睡 |
| 入睡困难 + 焦虑 | `theta-relaxation` + 呼吸引导（6次/min）| Theta降低杏仁核激活 |
| REM↓ + 深睡正常 | `alpha-steady`（20min）+ `rem-support`（30min）| Alpha稳定REM平衡 |
| 早醒 + 难以再睡 | `delta-continuity`（20min，开始于觉醒前30min）| Delta延续防止早醒 |
| 浅睡过多 | `sleep-spindle`（30min）| 12-14Hz刺激丘脑纺锤波生成 |

---

## 复合问题适配策略

### 问题数量 = 1

直接匹配对应音频（见上表）

### 问题数量 = 2

**优先处理最严重问题**，同时兼顾第二问题：

**示例**：深睡不足（严重度78）+ 睡眠片段化（严重度52）

```
→ 主音频：Delta增强（30min）覆盖深睡
→ 次要优化：在音频后半段增加Theta连续成分（兼顾片段化）
→ 输出：delta-enhanced-30min-with-theta-continuity
```

### 问题数量 = 3

**抓主要矛盾**（最严重的1-2个），避免多音频叠加造成不适：

```
→ 方案：选择针对最主要问题的音频
→ 时长：30-45min
→ 避免同时播放多种脑波频率
→ 如需覆盖多问题，可分夜使用不同音频
```

---

## 音频参数配置

### 基础配置

| 参数 | 默认值 | 可选范围 | 说明 |
|------|--------|---------|------|
| 主频率 | 依问题类型 | 0.5-40Hz | 目标脑波频率 |
| 次频率 | 依问题类型 | 0.5-40Hz | 复合音频第二频率 |
| 频率比例 | 70:30 | 50:50 - 90:10 | 主次频率能量比 |
| 音量 | 舒适音量 | 依用户偏好 | 通常40-60dB |
| 时长 | 15-30min | 10-60min | 单次播放时长 |

### 动态渐变配置

```
Phase 1（0-5min）：导入期
  主频率：Alpha（8-12Hz）
  目的：诱导放松，降低皮层激活

Phase 2（5-20min）：过渡期
  主频率：Theta（4-8Hz）
  目的：进入睡眠过渡阶段

Phase 3（20-结束）：维持期
  主频率：Delta（0.5-4Hz）
  目的：维持深睡（如用于深睡不足）
```

---

## 音频输出标签规范

格式：`{primary_type}-{secondary_type}-{duration}min-{variant}`

**示例**：
- `delta-enhanced-30min-v2` — Delta增强版30分钟，第2版
- `theta-alpha-onset-20min` — Theta-Alpha入睡导入20分钟
- `delta-continuity-60min-night` — Delta延续60分钟整夜版
- `spindle-memory-30min` — 睡眠纺锤波记忆巩固30分钟

---

## 特殊人群适配

### 老年人（> 65岁）

| 问题 | 推荐调整 |
|------|----------|
| 深睡不足 | 增加低频Delta（0.5-2Hz）至70% |
| 入睡困难 | 呼吸引导（4-6次/min）+ Alpha-Theta |
| 认知功能下降 | 增加Sleep Spindle成分（12-14Hz）|

### 围绝经期/绝经后女性

| 问题 | 推荐调整 |
|------|----------|
| 潮热相关片段化 | 增加连续性Delta + 室温建议 |
| 情绪焦虑 | Theta-Alpha（6-10Hz）+ 呼吸引导 |
| REM不足 | Alpha稳态（8-12Hz）|

### 长期压力/焦虑人群

| 问题 | 推荐调整 |
|------|----------|
| 过度觉醒 | 纯Theta（4-8Hz）较长导入（15-20min）|
| 杏仁核激活 | 6Hz Alpha-Theta + 呼吸引导（4-6次/min）|
| 皮质醇晚升 | 睡前90分钟开始播放，避免高峰 |

---

## 效果监测与迭代

### 反馈收集周期

- 首次使用后询问效果
- 连续使用3-5晚后收集趋势反馈
- 每2周复评睡眠指标

### 反馈→适配迭代规则

```
IF feedback == "positive" AND 连续3次:
    → 保持当前方案
    → 可尝试同类型不同版本

IF feedback == "neutral":
    → 调整频率比例或时长
    → 尝试添加次频率成分

IF feedback == "negative":
    → 切换到不同脑波类型
    → 考虑缩短时长（耐受性可能不足）
    → 排除音频本身问题（音量、音质）

IF 指标无改善（连续7晚）:
    → 建议暂停脑波音频（可能不敏感）
    → 建议转介专业睡眠评估
```

---

## manifest.json 参考映射（与 claw-health-brainwave 对接）

音频由 `claw-health-brainwave` 技能的 manifest.json 托管，本技能通过以下标签查询：

```json
{
  "chronic_type": "睡眠障碍",
  "scene": "睡前",
  "duration": 30,
  "problem_tags": ["深睡不足", "焦虑失眠"]
}
```

匹配时使用 problem_tags 中的主要问题查询对应音频标签。
