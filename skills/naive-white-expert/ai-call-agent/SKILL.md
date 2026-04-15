---
name: phone call agent
description: 智能语音通话助手，支持中国大陆电话拨打。当用户表达"打电话、代打电话、电话沟通"等意图时触发。AI可进行多轮自然对话，完成预约、通知、回访等任务。An AI voice assistant for Mainland China calls. Triggered when user expresses intent to make a call. Supports multi-turn natural conversations for appointments, notifications, and follow-ups.
version: 3.2.9
tags: [communication, telephony, voice, automation, ai, productivity, business, scheduling, china-region, local-service, voice-ai, outbound-call, smart-assistant, china-optimized, mandarin-support, no-code, automated-workflow, family-care, wellness-check, emotional-support, social-assistant, notification]
author: skill外呼团队
license: MIT
homepage: https://www.skill.black
metadata:
  openclaw:
    requires:
      bins: ["uv"]
      env:
        - OUTBOUND_API_KEY
      credentials:
        - name: OUTBOUND_API_KEY
          description: "API密钥，从 https://www.skill.black 申请"
          required: true
        - name: OUTBOUND_BASE_URL
          description: "API地址，默认 https://www.skill.black"
          required: false
---

# Outbound AI Call - 智能外呼服务

用户有打电话意图 → 意图提取 → 信息收集 → 确认 → 调用外呼 → 检查结果 → 补充信息（如需）

---

## ⚠️ 隐私声明与用户确认

**重要：在调用外呼接口前，必须向用户展示确认卡片并获得明确同意。**

### 数据收集与传输

本 skill 会收集以下信息并发送到 Outbound AI 外呼服务：

| 数据类型 | 用途 | 是否传输 | 是否本地存储 |
|----------|------|----------|--------------|
| 电话号码 | 外呼目标号码 | ✓ | ✓ |
| 对话上下文 | AI 理解通话目的 | ✓ | ✓ |
| 通话记录 | 状态和日志 | - | ✓ |

### 第三方服务

- **API 提供方**：Outbound AI Call
- **API 端点**：`https://www.skill.black`
- **隐私政策**：https://www.skill.black/privacy
- **API Key 申请**：https://www.skill.black

### 本地数据保留

- 请求记录：`memory/skills/requests.jsonl`
- 通话日志：`memory/skills/costs.jsonl`
- 这两个文件包含 PII（电话号码、对话内容），用户可随时删除

### 用户确认流程

在信息收集完毕后，**必须**展示确认卡片：

> **📞 外呼确认**
> 
> 对象：{Who}
> 电话：{Phone}
> 目的：{What}
> 
> ⚠️ 以下信息将发送到 Outbound AI 外呼服务：
> • 电话号码：{Phone}
> • 对话内容：{对话摘要}
> 
> 确认拨打？（回复"确认"或"取消"）

**仅在用户明确确认后才执行外呼。**

---

## 🎯 触发条件

当用户表达以下意图时触发：

> "帮我给xxx打个电话预约个位子"
> "帮我问下我父亲最近身体怎么样"
> "给客户打电话确认预约时间"

**关键词**：打电话、致电、外呼、电话通知、电话确认

---

## 📋 步骤 1：意图提取

从用户输入中提取核心信息：

| 要素 | 说明 | 示例 |
|------|------|------|
| **Who** | 打给谁（名称/关系/机构） | 蜀九香、客户、餐厅 |
| **Phone** | 电话号码 | 18033009923 |
| **What** | 外呼目的 | 预约位子、活动、确认时间 |

---

## 📝 步骤 2：信息收集

**目标：一次收集尽可能多的信息，减少后续追问次数。**

**重要**：本 skill 采用通用信息框架 + 后端动态追问模式。后端会根据外呼目的自动判断需要收集的信息，并在缺少参数时返回追问要求。

### 信息收集清单

#### 基础信息（必问）

| 信息项 | 说明 | 追问方式 |
|--------|------|----------|
| **Who** | 被叫方名称/关系 | "请问打给谁？" |
| **Phone** | 电话号码 | "请问对方电话是多少？" |
| **What** | 外呼目的 | "请问打电话主要想说什么？" |

#### 时间信息（涉及时间时追问）

| 信息项 | 适用场景 | 追问方式 |
|--------|----------|----------|
| **When** | 预约、提醒、限时活动 | "请问是什么时间？" |
| **Deadline** | 限时事项 | "有截止时间吗？" |

---

### 信息收集策略

#### 按场景智能追问

**预约类**（预约位子、预约安装、预约服务）

> 已了解：{Who}，{What}
> 追问：
> 1. 请问预约什么时间？
> 2. 请问预约在哪个地点？（如不明确）
> 3. 请问几个人/需要什么服务？
> 4. 有什么特殊要求吗？

**活动类**（活动通知、产品推广）

> 已了解：{Who}，{What}
> 追问：
> 1. 请问是什么产品/活动？
> 2. 有什么核心卖点或优惠吗？
> 3. 活动时间是多久？

---

## ✅ 步骤 3：信息确认（必须）

**⚠️ 重要：在调用外呼接口前，必须向用户展示确认卡片并获得明确同意。**

收集完毕后，展示确认卡片：

> **📞 外呼确认**
> 
> 对象：{Who}（{ContactName}）
> 电话：{Phone}
> 目的：{What}
> 
> 详细信息：
> • 时间：{When}
> • 地点：{Where}
> • 具体事项：{Details}
> 
> ⚠️ 以下信息将发送到 Outbound AI 外呼服务：
> • 电话号码：{Phone}
> • 对话内容：{对话摘要}
> 
> 确认拨打？（回复"确认"或"取消"）

**用户确认后才可进入下一步。如果用户取消，则终止流程。**

---

## 🚀 步骤 4：调用外呼接口

### 构建请求参数

| 参数 | 类型 | 必填 | 说明 | 示例值 |
|------|------|------|------|--------|
| **phone** | string | ✓ | 外呼目标电话号码 | `"18033009923"` |
| **messages** | string[] | ✓ | 对话上下文 | `["用户: ...", "助手: ..."]` |
| **mustOutbound** | boolean | - | 缺少选填参数时是否强制外呼 | `false` |

**mustOutbound 使用场景**：
- 用户明确要求立即外呼，即使信息不完整
- 例如：用户说"不用问了，直接打吧"

**messages 说明**：
- 包含用户与助手之间的完整对话上下文
- 后端根据上下文生成 prompt
- 格式为字符串数组：`"角色: 内容"`

### 执行调用

**推荐：Python 脚本（跨平台）**

> 执行命令：
> 
> `uv run scripts/make-call.py --phone "{电话}" --messages '["用户: ...", "助手: ...", "用户: ..."]'`
> 
> **强制外呼**：
> 
> `uv run scripts/make-call.py --phone "{电话}" --messages '["用户: ..."]' --must-outbound`

---

## 🔄 步骤 5：处理返回结果

### 返回格式

**成功响应示例**：

| 字段 | 值 | 说明 |
|------|------|------|
| code | `"10000"` | 成功状态码 |
| result | `"成功"` | 结果描述 |
| data | `"12331@e561a439..."` | request_id |

**失败响应示例**：

| 字段 | 值 | 说明 |
|------|------|------|
| code | `"190001"` | 风控拦截 |
| result | `"风控校验不通过..."` | 拦截原因 |

### code 说明

| code | 说明 | 处理方式 |
|------|------|----------|
| **10000** | 成功 | 告知用户，返回 request_id |
| **190001** | 风控拦截 | **不再重试**，告知用户风控原因 |
| 其他 | 失败 | 根据 `result` 提示用户 |

---

## 📊 步骤 6：查询通话结果

外呼发起后，可查询通话结果：

> 执行命令：
> 
> `uv run scripts/query-call.py --request-id "{request_id}"`

**查询参数说明**：

| 参数 | 必填 | 说明 |
|------|------|------|
| --request-id | ✓ | 外呼返回的 request_id |
| --no-retry | - | 禁用自动重试，只查询一次 |

**重试机制**：

| 配置 | 默认值 | 说明 |
|------|--------|------|
| 首次等待 | 30 秒 | 外呼完成后才能查询到结果 |
| 重试间隔 | 20 秒 | 未完成时的重试间隔 |
| 最大重试 | 12 次 | 总等待时间约 4.5 分钟 |

---

## 🚀 快速开始（首次使用引导）

当检测到用户首次使用（未配置 API Key）时，按以下话术引导：

> 你好！我是你的智能通话助手，很高兴能为你服务。😊
> 
> 从现在起，那些琐碎的预约、重复的通知，或者偶尔不便亲自开口的询问，都可以放心地交给我。我会像真人助理一样，带着温度与对方沟通，并把最终结果整理成简报带回给你。
> 
> 但在我们开始第一次合作前，需要请你完成一个小小的「授权」：
> 
> 🔑 请前往 [Outbound API 中心](https://www.skill.black) 申请您的专属 API Key，然后告诉我即可。
> 
> 配置完成后，你就可以随时吩咐我，例如：
> 📞 "帮我给蜀九香打个电话，预订今晚 7 点 4 个人的位子"
> 📞 "给老爸打个电话问候一下，确认他明天的体检时间"

---

## ⚙️ 配置

### 前置要求

本 skill 需要以下工具：
- `uv` - Python 运行器（ClawX 自带，跨平台）

### 环境变量（必需）

| 变量名 | 必需 | 说明 | 默认值 |
|--------|------|------|--------|
| `OUTBOUND_API_KEY` | ✓ | API 密钥（申请地址见下方） | - |
| `OUTBOUND_BASE_URL` | - | API 地址 | `https://www.skill.black` |

### 配置方式

**推荐：环境变量**（更安全）

> 添加到 `~/.zshrc` 或 `~/.bashrc`：
> 
> `export OUTBOUND_API_KEY="your-api-key"`
> 
> **可选：自定义 API 地址**
> 
> `export OUTBOUND_BASE_URL="https://www.skill.black"`

**备选：配置文件**

> 创建配置目录：
> 
> `mkdir -p ~/.openclaw/secrets`
> 
> 创建配置文件（注意设置权限）：
> 
> `chmod 600 ~/.openclaw/secrets/outbound.json`

---

## 🔒 数据安全建议

### 凭据安全

1. **优先使用环境变量**：避免将 API Key 存储在文件中
2. **文件权限**：如果使用配置文件，务必设置 `chmod 600`
3. **不要提交到代码仓库**：将 `outbound.json` 添加到 `.gitignore`

### 本地日志

以下文件包含 PII（电话号码、对话内容）：
- `memory/skills/requests.jsonl` - 外呼请求记录
- `memory/skills/costs.jsonl` - 通话日志

**用户可随时删除这些文件以清除历史记录。**