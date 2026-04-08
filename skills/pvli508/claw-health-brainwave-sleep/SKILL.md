# 睡眠障碍脑波声疗助手 🧠💤

> 聚焦睡眠障碍细分场景，支持个体多维度信息适配，音频库以本地文件为主

---

## 一、基础配置

| 配置项 | 值 |
|--------|-----|
| Skill 名称 | 睡眠障碍脑波声疗助手 |
| Skill ID | claw_health_brainwave_sleep |
| 类型 | 内容服务 + 企业工具 |
| 运行平台 | OpenClaw 音箱 / 大屏 / 健康一体机 / 小程序 SDK |
| 租户模式 | 多租户 SaaS |
| 合规声明 | 本音频为非药物健康辅助，不替代医疗诊断、治疗及用药 |
| 音频库 | 云端腾讯云 COS（audio_source_mode=ONLINE） |

---

## 二、睡眠障碍细分类型

### 2.1 障碍亚型 (sleep_disorder_subtype)

| 亚型编码 | 名称 | 典型表现 | 推荐脑波 |
|----------|------|----------|----------|
| SLEEP_ONSET | 入睡困难型 | 30分钟以上无法入睡 | θ 波 (4-8Hz) |
| SLEEP_MAINTAIN | 睡眠维持型 | 夜间频繁醒来 | δ 波 (0.5-4Hz) |
| EARLY_WAKE | 早醒型 | 凌晨醒来后无法再睡 | θ+α 复合 |
| CIRCADIAN | 昼夜节律紊乱 | 作息时间颠倒 | α→θ→δ 渐进 |
| ANXIETY_SLEEP | 焦虑性失眠 | 睡前焦虑、反刍思维 | α 放松 + θ 引导 |
| LIGHT_SLEEP | 浅眠多梦型 | 睡眠浅、多梦 | δ 波深睡增强 |
| GENERAL | 通用型 | 不明确或综合表现 | θ 波综合引导 |

### 2.2 个体维度

#### 年龄段 (age_group)

| 编码 | 年龄范围 |
|------|----------|
| YOUNG_ADULT | 18-35 岁 |
| MIDDLE_AGED | 36-55 岁 |
| ELDERLY | 56 岁以上 |

#### 性别 (gender)

| 编码 | 说明 |
|------|------|
| MALE | 男性 |
| FEMALE | 女性 |
| UNSET | 未设置 |

#### 严重程度 (severity)

| 编码 | 名称 | 判定标准 | 推荐时长 |
|------|------|----------|----------|
| MILD | 轻度 | 偶发，1周1-2次 | 20分钟 |
| MODERATE | 中度 | 频繁，1周3-4次 | 30分钟 |
| SEVERE | 重度 | 每日发生 | 45分钟 |

---

## 三、意图定义

### 意图 1：PLAY_SLEEP_BRAINWAVE - 播放睡眠脑波音频

**用户说法**：
```
播放助眠脑波音频
我睡不着，帮我放个脑波音乐
播放入睡困难脑波音频
打开深度睡眠脑波
播放 20 分钟助眠音频
我容易夜里醒来，播放维持睡眠的脑波
给我放个焦虑失眠的脑波音频
打开睡前放松脑波
播放浅眠多梦改善音频
```

**槽位**：
| 槽位名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| sleep_disorder_subtype | 枚举 | 否 | 睡眠障碍亚型 |
| use_scene | 枚举 | 否 | 使用场景 |
| duration | 数字 | 否 | 时长(15/20/30/45/60) |
| severity | 枚举 | 否 | 严重程度 |
| age_group | 枚举 | 否 | 年龄段 |
| gender | 枚举 | 否 | 性别 |
| comorbidity | 枚举 | 否 | 伴随状况 |

---

### 意图 2：CONTROL_SLEEP_AUDIO - 音频播放控制

**用户说法**：
```
暂停播放
继续播放
停止音频
关掉脑波音乐
声音小一点
音量调大
重新播放
```

---

### 意图 3：SET_SLEEP_TIMER - 定时关闭

**用户说法**：
```
20分钟后自动关闭
播放30分钟后关掉
帮我定时45分钟关闭
我睡着了自动停止
```

---

### 意图 4：SWITCH_SLEEP_AUDIO - 切换音频/场景

**用户说法**：
```
换一个助眠音频
换深度睡眠脑波
切换到焦虑失眠模式
我夜里醒了，换个复眠音频
换柔和一点的
```

---

### 意图 5：UPDATE_USER_PROFILE - 更新个人信息

**用户说法**：
```
我是轻度失眠
我最近焦虑比较严重
我有高血压也睡不好
我60岁了
我失眠比较严重
```

---

### 意图 6：QUERY_SLEEP_HELP - 使用帮助

**用户说法**：
```
这个技能怎么用
有什么助眠音频
帮我介绍一下功能
```

---

### 意图 7：EXIT_SLEEP_SKILL - 退出技能

**用户说法**：
```
退出技能
关闭助眠助手
不用了
```

---

## 四、音频匹配逻辑

### 4.1 匹配优先级

1. 亚型 (sleep_disorder_subtype) — 必须匹配
2. 使用场景 (use_scene) — 必须匹配
3. 严重程度 (severity) — 精确匹配，无则降级至 MODERATE
4. 人群 (age_group + gender) — 精确匹配，无则使用通用版
5. 伴随状况 (comorbidity) — 有伴随时优先选联动版本
6. 时长 (duration) — 精确匹配，无则选最近时长

### 4.2 降级策略

```
精确匹配 → 同亚型通用场景 → GENERAL 亚型同场景 → GENERAL 通用 → 返回异常话术
```

### 4.3 时长推荐

| 来源 | 逻辑 |
|------|------|
| 用户明确说出 | 直接使用 |
| 用户画像 severity | MILD→20min, MODERATE→30min, SEVERE→45min |
| 场景默认值 | NAP→15min，其余→30min |

---

## 五、音频文件命名规范

```
bw_{亚型}_{场景}_{时长}_{严重度}_{脑波类型}[_{人群标记}]_{版本}.mp3

示例：
bw_anxiety_sleep_pre_30min_mod_alpha_theta_v1.mp3
bw_sleep_onset_pre_45min_sev_full_f_v1.mp3
```

---

## 六、流媒体播放实现

> `audio_source_mode=ONLINE`，音频托管于腾讯云 COS，支持各渠道内嵌流媒体播放，无需下载到本地。

### 播放核心逻辑

意图识别 → 查 `manifest.json` 匹配音频 → 按渠道选择播放方式

**不依赖任何本地后端服务。**

### 渠道分流

| 渠道 | 播放方式 | 实现 |
|------|----------|------|
| **WeChat**（`openclaw-weixin`） | 流媒体内嵌 | `message` 工具发送 `media` 消息，微信客户端内置播放器自动播放 |
| **飞书**（`feishu`） | 流媒体内嵌 | 返回音频 URL，飞书消息内嵌播放器 |
| **网页**（`webchat`） | Canvas + HTML5 Audio | `canvas` 工具展示播放控制条，浏览器解码播放 |

### WeChat 流媒体播放（推荐）

```javascript
message({
  action: "send",
  channel: "openclaw-weixin",
  target: "<user_openid>",
  media: "<cloud_url>",
  mimeType: "audio/mpeg",
  caption: "已为您播放【{title}】，时长 {duration} 分钟"
})
```

**效果：** 用户收到一条带音频卡片的消息，点击即可在微信内播放，不跳出。

### 飞书流媒体播放

直接返回音频 URL 链接，飞书客户端会自动识别并内嵌播放器。

### 网页内嵌播放（Canvas）

```javascript
canvas({
  action: "present",
  html: `<audio src="<cloud_url>" controls autoplay style="width:100%"></audio>`
})
```

### 定时关闭

在 `SET_SLEEP_TIMER` 意图中，通过 `setTimeout` + `canvas.hide` 或 `message` 提醒实现，不依赖本地播放器。

### 音频切换（SWITCH）

匹配新音频后，重新发送 `media`（WeChat）或刷新 `audio.src`（Canvas）即可。

---

## 七、标准话术

### 播放开场
```
已为您打开【{亚型名称}】{场景} 脑波音频，时长 {duration} 分钟。
请在安静舒适的环境中聆听，建议佩戴耳机效果更佳。
温馨提示：本音频为非药物健康辅助，不替代医疗诊断与治疗。
```

### 重度用户开场
```
已为您打开 {duration} 分钟睡眠辅助脑波音频。
由于您的睡眠困扰较为明显，建议同时咨询专业睡眠医师获取个性化诊疗方案。
温馨提示：本音频为非药物健康辅助，不替代医疗诊断、治疗及用药。
```

### 定时话术
```
好的，{duration} 分钟后将自动为您关闭音频，祝您好眠。
```

### 帮助话术
```
您可以对我说：
「播放助眠脑波音频」「播放入睡困难 30 分钟脑波」「我有焦虑失眠」
「20 分钟后自动关闭」「换一个深度睡眠音频」「我失眠比较严重」
温馨提示：本音频为非药物健康辅助，不替代医疗诊断与治疗。
```

### 夜醒场景话术
```
检测到当前为夜间时段，已为您切换至「夜醒复眠」模式，播放 {duration} 分钟深度睡眠脑波。
请保持放松，自然呼吸。
温馨提示：本音频为非药物健康辅助，不替代医疗诊断与治疗。
```

---

## 八、数据表设计

### t_user_sleep_profile (用户睡眠画像)

| 字段 | 说明 |
|------|------|
| user_id | 用户唯一标识 |
| tenant_id | 所属租户 ID |
| disorder_subtype | 睡眠障碍亚型 |
| severity | 症状严重程度 |
| age_group | 年龄段 |
| gender | 性别 |
| comorbidity | 伴随状况 |
| update_time | 画像更新时间 |

### t_sleep_audio_meta (音频元数据)

| 字段 | 说明 |
|------|------|
| audio_id | 音频唯一标识 |
| disorder_subtype | 睡眠障碍亚型 |
| use_scene | 适用场景 |
| severity | 适用严重程度 |
| age_group | 适用年龄段 |
| gender | 适用性别 |
| duration | 音频时长(分钟) |
| cloud_url | 云端音频访问地址 |

---

## 九、云端音频库

> `audio_source_mode=ONLINE`，所有音频托管于腾讯云 COS，无需本地文件。

**基础 URL：**
```
https://brainwave-audio-1300612542.cos.ap-shanghai.myqcloud.com/SleepAudio
```

**音频访问：** `基础URL + / + filename`

**示例：**
```
https://brainwave-audio-1300612542.cos.ap-shanghai.myqcloud.com/SleepAudio/bw_sleep_onset_pre_30min_mod_alpha_theta_v1.mp3
```

---

## 十、开发 Checklist

### 开发必做
- [x] 接入 OpenClaw Skill SDK 并完成鉴权
- [x] 实现意图解析 + 槽位提取逻辑
- [x] 完成多维音频匹配算法
- [x] 实现云端音频 URL 解析（audio_source_mode=ONLINE）
- [x] 完成用户画像读写逻辑
- [x] 实现降级匹配策略
- [x] 完成多租户数据隔离
- [x] 实现播放日志上报
- [x] 全局挂载合规声明

### 测试必测
- [ ] 语音指令识别准确率
- [ ] 多维匹配准确率
- [ ] 音频播放流畅度
- [ ] 定时关闭准确性

---

## 十一、已实现扩展

| 扩展项 | 状态 | 说明 |
|--------|------|------|
| 线上音频库 | ✅ 已完成 | audio_source_mode=ONLINE，音频托管于腾讯云 COS |
| 睡眠质量反馈 | 📋 待实现 | 播放结束后询问用户睡眠质量 |
| 设备联动 | 📋 待实现 | 对接可穿戴设备睡眠数据 |
| 跨 Skill 联动 | 📋 待实现 | 与高血压、情绪类 Skill 协同推荐 |
