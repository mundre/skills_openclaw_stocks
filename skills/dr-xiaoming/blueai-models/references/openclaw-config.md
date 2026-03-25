# OpenClaw 模型配置指南

## openclaw.json 配置结构

OpenClaw 通过 `~/.openclaw/openclaw.json` 的 `models` 字段配置模型。

### 基本结构

```json
{
  "models": {
    "mode": "merge",
    "providers": {
      "<provider-name>": {
        "baseUrl": "<api-endpoint>",
        "apiKey": "<api-key>",
        "api": "<api-type>",
        "models": [ ... ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": { "primary": "<provider>/<model-id>" },
      "models": {
        "<provider>/<model-id>": { "alias": "<short-name>" }
      }
    }
  }
}
```

### API 类型（api 字段）

| api 值 | 用于 | 端点 |
|--------|------|------|
| `anthropic-messages` | Claude 系列 | `https://bmc-llm-relay.bluemediagroup.cn` (无/v1) |
| `openai-completions` | GPT/Gemini/DeepSeek/Qwen等 | `https://bmc-llm-relay.bluemediagroup.cn/v1` (带/v1) |

**关键区别**：
- Anthropic 端点的 `baseUrl` **不带** `/v1`
- OpenAI 端点的 `baseUrl` **必须带** `/v1`

### 模型定义字段

```json
{
  "id": "模型ID（必须与API文档一致）",
  "name": "显示名称",
  "api": "anthropic-messages 或 openai-completions",
  "reasoning": true/false,
  "input": ["text"] 或 ["text", "image"],
  "cost": {
    "input": 0.001,
    "output": 0.005,
    "cacheRead": 0.0001,
    "cacheWrite": 0.00125
  },
  "contextWindow": 200000,
  "maxTokens": 64000
}
```

- `reasoning: true` 表示模型支持思维链/扩展思考
- `input` 数组决定模型能否处理图片
- `cost` 单位为 $/1K tokens（用于 OpenClaw dashboard 估算费用）
- `cacheRead`/`cacheWrite` 仅 Anthropic 模型需要

### 别名配置

在 `agents.defaults.models` 中设置别名，方便通过 `/model <alias>` 快速切换：

```json
"models": {
  "blueai/gemini-2.5-flash": { "alias": "flash" },
  "anthropic/claude-sonnet-4-6": { "alias": "sonnet" }
}
```

---

## 完整配置示例

### 场景1：仅添加一个轻量模型（最小改动）

在 `models.providers` 中添加一个 provider：

```json
"blueai": {
  "baseUrl": "https://bmc-llm-relay.bluemediagroup.cn/v1",
  "apiKey": "sk-xxx",
  "api": "openai-completions",
  "models": [
    {
      "id": "gemini-2.5-flash",
      "name": "Gemini 2.5 Flash",
      "api": "openai-completions",
      "reasoning": true,
      "input": ["text", "image"],
      "cost": {"input": 0.00015, "output": 0.0035},
      "contextWindow": 1048576,
      "maxTokens": 65535
    }
  ]
}
```

### 场景2：分层策略（推荐）

```json
"providers": {
  "anthropic": {
    "baseUrl": "https://bmc-llm-relay.bluemediagroup.cn",
    "api": "anthropic-messages",
    "models": [
      {"id": "claude-sonnet-4-6", "name": "Sonnet 4.6", ...},
      {"id": "claude-haiku-4-5-20251001", "name": "Haiku 4.5", ...}
    ]
  },
  "blueai": {
    "baseUrl": "https://bmc-llm-relay.bluemediagroup.cn/v1",
    "apiKey": "sk-xxx",
    "api": "openai-completions",
    "models": [
      {"id": "gemini-2.5-flash", ...},
      {"id": "gpt-4.1-mini", ...},
      {"id": "DeepSeek-V3.2", ...}
    ]
  }
}
```

---

## 常见问题

### MiniMax 模型必须用 OpenAI 端点
MiniMax-M2.x 系列不支持 Claude 端点，`api` 必须设为 `openai-completions`。

### gemini-3-pro-preview 即将弃用
2026-03-26 起弃用，应迁移至 `gemini-3.1-pro-preview`。

### DeepSeek 是纯文本模型
`input` 只能设 `["text"]`，不支持图片。

### 价格查询
访问 `https://bmc-llm-relay.bluemediagroup.cn/pricing` 获取最新价格。

### API Key 申请
通过飞书多维表格申请：搜索"BlueAI 模型代理API Key申请"。
