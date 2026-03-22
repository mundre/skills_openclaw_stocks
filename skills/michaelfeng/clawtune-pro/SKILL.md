---
name: clawtune
description: ClawTune — OpenClaw 智能增强引擎。10 模型智能路由、错误恢复、依赖链保护，基于 205 场景评测数据。
user-invocable: true
metadata: {"openclaw": {"emoji": "🧠", "homepage": "https://github.com/michaelfeng/clawtune", "requires": {}}}
---

# ClawTune

OpenClaw 智能增强引擎。不换模型，一行配置，tool calling 成功率从 60% 提升到 95%。

## 205 场景评测数据

| 模型 | 综合 | 错误恢复 | 模糊指令 | 多步工作流 |
|------|:---:|:---:|:---:|:---:|
| ClawTune Pro | ~90% | 90%+ | 75%+ | 85%+ |
| GLM-5 | 83% | 80% | 65% | 73% |
| MiniMax-M2.5 | 81% | 76% | 55% | 73% |
| Kimi-K2.5 | 81% | 76% | 65% | 70% |
| Qwen3-Coder-Plus | 79% | 76% | 25% | 77% |
| DeepSeek-V3 | 73% | 56% | 65% | 80% |

## 核心能力
- **智能路由**：10 个后端模型，按任务类别精准分发到最强模型
- **错误恢复**：文件不存在自动查找，命令失败自动换方案
- **依赖链保护**：确保"先查再做"类多步任务完整执行
- **Prompt 增强**：基于 205 场景验证的最佳实践
- **输出修正**：自动修复 JSON 格式错误和推理标签
- **Streaming 支持**：兼容 OpenClaw 默认模式

## 路由表（基于 205 场景 × 6 模型 benchmark）

| 任务类别 | 路由模型 | 准确率 |
|---------|---------|:---:|
| 文件/搜索/定时 | Qwen3-Coder-Plus | 100% |
| 终端/错误恢复/模糊指令 | GLM-5 | 65-90% |
| 消息/浏览器 | MiniMax-M2.5 | 60-100% |
| 多步工作流 | DeepSeek-V3 | 80% |

## 配置方法

```json
{
  "models": {
    "providers": {
      "clawtune": {
        "baseUrl": "https://api.factorhub.cn/v1",
        "apiKey": "你的 API Key",
        "api": "openai-completions",
        "models": [{"id": "clawtune-pro", "name": "ClawTune Pro", "contextWindow": 262144, "maxTokens": 65536}]
      }
    }
  },
  "agents": {"defaults": {"model": {"primary": "clawtune/clawtune-pro"}}}
}
```

然后 `openclaw gateway restart`。

## 相关 Skills

```bash
clawhub install clawtune-benchmark    # 模型评测工具
clawhub install clawtune-doctor       # 配置诊断工具
clawhub install clawtune-smart-retry  # 错误恢复指导
```

获取 API Key：https://clawtune.cn/dashboard
完整评测报告：https://clawtune.cn/blog/openclaw-model-comparison
