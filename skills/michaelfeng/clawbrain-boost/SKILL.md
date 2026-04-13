---
name: clawbrain-boost
description: ClawBrain Boost v1.2 — 一键优化 OpenClaw 的智能、记忆和响应。自动配置 ClawBrain API + 知识图谱记忆 + SOUL 优化。记忆更可靠，来源可追溯，降级有通知，长对话不丢上下文。
user-invocable: true
metadata: {"openclaw": {"emoji": "🚀", "homepage": "https://clawbrain.dev", "requires": {}}}
---

# ClawBrain Boost

一键让你的 OpenClaw 更聪明、记得住、回答快。

## 安装后你得到什么

### 四档模型自动切换
- **Flash**（0.5 Credits）— 简单任务秒回，省钱
- **Pro**（1 Credit）— 智能路由，10+ 模型自动选最优
- **Max**（3 Credits）— 深度推理，返回完整思考过程
- **Auto**（推荐）— 自动判断复杂度，选择最合适的档

### 知识图谱记忆
- 每次对话中的重要信息自动提取为结构化实体和关系
- 支持 6 种实体类型：人物、项目、工具、决策、偏好、问题
- 中文 N-gram 智能分词，精准检索历史记忆
- 每日自动整合（DreamTask 凌晨 3:00 自动运行），无需手动维护
- 3D 可视化知识图谱，在控制台查看
- **v1.2 新增：** 记忆来源标注 — 每条记忆附带来源对话引用，可追溯
- **v1.2 新增：** 记忆精准度提升 — 实体提取更准确，减少误关联
- **v1.2 新增：** 降级通知 — 当记忆服务不可用时，明确告知用户当前处于降级模式
- **v1.2 新增：** 身份信息自动更新 — 检测到用户身份变化时自动同步
- **v1.2 新增：** 长对话记忆保持 — 超长对话截断时自动从知识图谱恢复关键上下文

### 响应更好
- 简洁直接，不寒暄不废话
- 模糊指令先确认理解再动手
- 高风险操作先征得同意
- 出错自动换策略恢复
- 主动思考框架：执行前自问"不知道什么/可能出问题/怎么验证"

### 垂直场景加持
自动识别 7 个领域，注入专业规则：
- 支付场景 → 提醒幂等性、签名验证
- 运维场景 → 提醒先备份再操作
- 代码场景 → 检查安全漏洞、边界条件
- 数据场景 → 提醒数据完整性、脱敏

### v1.2 新增速览
- 记忆来源可追溯，每条记忆标注出处
- 记忆精准度提升，减少误提取和误关联
- 降级透明通知，服务异常时不再静默失败
- 身份信息自动同步，用户信息变更即时生效
- 长对话不丢上下文，截断时自动从记忆恢复关键信息

### 输出质量保障
- 独立模型四维评分：准确性、完整性、逻辑性、格式
- 评分低于 70 分自动重试
- 模型健康实时监控：5 次失败自动熔断，60s 后探测恢复

## 安装

```bash
clawhub install clawbrain-boost
```

## 手动配置

如果你想手动配置，编辑 `~/.openclaw/openclaw.json`：

```json
{
  "models": {
    "providers": {
      "clawbrain": {
        "baseUrl": "https://api.factorhub.cn/v1",
        "apiKey": "你的 API Key",
        "api": "openai-completions",
        "models": [
          { "id": "clawbrain-auto", "name": "ClawBrain Auto", "input": ["text", "image"], "contextWindow": 128000, "maxTokens": 32768 },
          { "id": "clawbrain-pro", "name": "ClawBrain Pro", "input": ["text", "image"], "contextWindow": 64000, "maxTokens": 16384 },
          { "id": "clawbrain-max", "name": "ClawBrain Max", "input": ["text", "image"], "contextWindow": 128000, "maxTokens": 32768 },
          { "id": "clawbrain-flash", "name": "ClawBrain Flash", "contextWindow": 32000, "maxTokens": 8192 }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": { "primary": "clawbrain/clawbrain-auto" }
    }
  }
}
```

然后重启：
```bash
openclaw gateway restart
```

## 获取 API Key

1. 前往 [clawbrain.dev/dashboard](https://clawbrain.dev/dashboard)
2. 注册账号（免费 50 Credits/天）
3. 复制 API Key 到配置中

## 最佳实践

### SOUL.md 优化

在 `~/.openclaw/workspace/SOUL.md` 中添加以下规则，让 AI 行为更好：

```markdown
## Response Style
- 简洁直接，不寒暄，直入主题
- 模糊指令先确认理解再执行
- 高风险操作先确认再执行
- 用结构化格式（标题、列表、代码块）

## Working with Tools
- 文件操作前先确认路径存在
- 出错不盲目重试，先分析原因换策略
- 多步任务分步验证

## Memory Habits
- 重要信息会自动写入知识图谱
- 实体关系自动提取和关联
- 每日 DreamTask 自动整合记忆，无需手动维护
```

## 定价

| 方案 | 价格 | Credits/天 |
|------|------|:---:|
| 免费 | ¥0 | 50 |
| Pro | ¥99/月 | 1,000 |
| Pro Max | ¥199/月 | 3,000 |
| 企业版 | ¥299/月 | 无限 |

更多信息：[clawbrain.dev](https://clawbrain.dev)
