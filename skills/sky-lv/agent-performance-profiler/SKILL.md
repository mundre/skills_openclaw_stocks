---
name: agent-performance-profiler
slug: skylv-agent-performance-profiler
version: 1.0.2
description: Agent performance analyzer. Analyzes response time, token consumption, and tool call efficiency with optimization recommendations. Triggers: performance profiling, agent speed, token optimization.
author: SKY-lv
license: MIT
tags: [agent, performance, optimization, profiling, token-usage]
keywords: openclaw, skill, automation, ai-agent
triggers: agent performance profiler
---

# Agent Performance Profiler — 性能分析与优化

## 功能说明

深度分析 AI Agent 性能，包括响应时间、Token 消耗、工具调用效率，提供可执行的优化建议。让 Agent 更快、更省、更稳定。

## 核心指标

### 1. 响应时间 (Response Time)

```yaml
metrics:
  - first_token_latency: 首 Token 延迟（目标：<500ms）
  - total_response_time: 总响应时间（目标：<3s）
  - time_to_first_byte: 首字节时间
  - streaming_latency: 流式延迟

benchmarks:
  - simple_query: <1s
  - complex_task: <5s
  - multi_tool: <10s
```

### 2. Token 消耗 (Token Usage)

```yaml
metrics:
  - input_tokens: 输入 Token 数
  - output_tokens: 输出 Token 数
  - total_tokens: 总 Token 数
  - cost_per_request: 单次请求成本

optimization:
  - prompt_compression: 提示词压缩
  - context_pruning: 上下文裁剪
  - response_summarization: 响应摘要
```

### 3. 工具调用效率 (Tool Efficiency)

```yaml
metrics:
  - tool_call_count: 工具调用次数
  - tool_success_rate: 工具成功率（目标：>95%）
  - redundant_calls: 冗余调用数
  - parallel_opportunities: 可并行机会

optimization:
  - batch_calls: 批量调用
  - cache_results: 缓存结果
  - parallel_execution: 并行执行
```

### 4. 错误率 (Error Rate)

```yaml
metrics:
  - api_error_rate: API 错误率（目标：<1%）
  - timeout_rate: 超时率（目标：<2%）
  - retry_rate: 重试率（目标：<5%）

alerts:
  - error_spike: 错误率突增
  - latency_spike: 延迟突增
  - cost_spike: 成本突增
```

## 性能分析流程

### 1. 基线测试

```yaml
test_cases:
  - simple_qa: 简单问答
  - multi_step: 多步任务
  - tool_intensive: 工具密集型
  - context_heavy: 重上下文

metrics_collected:
  - response_time
  - token_usage
  - tool_calls
  - error_rate
```

### 2. 瓶颈识别

```yaml
common_bottlenecks:
  - verbose_prompts: 提示词过长
  - redundant_tool_calls: 冗余工具调用
  - sequential_execution: 顺序执行（可并行）
  - context_bloat: 上下文膨胀
  - inefficient_retries: 低效重试
```

### 3. 优化建议

```yaml
optimization_strategies:
  - prompt_optimization:
      - 移除冗余描述
      - 使用结构化输出
      - 添加示例（few-shot）
  
  - tool_optimization:
      - 批量调用
      - 结果缓存
      - 并行执行
  
  - context_optimization:
      - 相关性过滤
      - 摘要压缩
      - 向量检索
```

## 优化技巧

### 提示词优化

**❌ 低效：**
```
你是一个很有帮助的 AI 助手，你需要帮助用户完成各种任务。
请仔细阅读用户的问题，然后思考如何解决。
你需要考虑各种因素，包括...（冗长描述）
```

**✅ 高效：**
```
角色：{专业角色}
任务：{具体任务}
输出格式：{JSON/Markdown/列表}
约束：{限制条件}
```

**效果：** Token 减少 60%，响应时间减少 40%

### 工具调用优化

**❌ 低效（顺序调用）：**
```
1. 搜索 A
2. 搜索 B
3. 搜索 C
4. 合并结果
```

**✅ 高效（并行调用）：**
```
并行：
  - 搜索 A
  - 搜索 B
  - 搜索 C
合并结果
```

**效果：** 响应时间减少 70%

### 上下文优化

**❌ 低效（完整历史）：**
```
[完整对话历史，5000+ Token]
```

**✅ 高效（相关性过滤）：**
```
[最近 5 轮对话]
[相关记忆摘要，500 Token]
```

**效果：** Token 减少 80%，成本减少 80%

## 工具函数

### profile_agent

```python
def profile_agent(task: str, iterations: int = 10) -> dict:
    """
    Agent 性能分析
    
    Args:
        task: 测试任务
        iterations: 测试迭代次数
    
    Returns:
        {
            "avg_response_time": 1.23,  # 秒
            "p95_response_time": 2.45,
            "avg_tokens": 450,
            "avg_cost": 0.002,  # 美元
            "tool_calls": 3.2,  # 平均每次
            "error_rate": 0.02  # 2%
        }
    """
```

### optimize_prompt

```python
def optimize_prompt(prompt: str) -> dict:
    """
    提示词优化
    
    Args:
        prompt: 原始提示词
    
    Returns:
        {
            "original_tokens": 500,
            "optimized_tokens": 200,
            "reduction": 0.6,
            "optimized_prompt": "优化后的提示词",
            "changes": ["移除冗余", "结构化", "添加示例"]
        }
    """
```

### analyze_tool_calls

```python
def analyze_tool_calls(trace: list) -> dict:
    """
    工具调用分析
    
    Args:
        trace: 工具调用追踪
    
    Returns:
        {
            "total_calls": 15,
            "redundant_calls": 3,
            "parallel_opportunities": 2,
            "cache_hits": 5,
            "optimization_suggestions": [
                "合并 A 和 B 调用",
                "并行执行 C 和 D",
                "缓存 E 的结果"
            ]
        }
    """
```

## 性能基准

### 优秀 Agent 标准

| 指标 | 优秀 | 良好 | 需优化 |
|------|------|------|--------|
| 响应时间 | <1s | 1-3s | >3s |
| Token 效率 | <300 | 300-800 | >800 |
| 工具成功率 | >98% | 95-98% | <95% |
| 成本/请求 | <$0.001 | $0.001-0.005 | >$0.005 |

### 成本计算

```yaml
模型定价（参考）:
  - GPT-4: $0.03/1K input, $0.06/1K output
  - Claude-Sonnet: $0.003/1K input, $0.015/1K output
  - Qwen-Plus: ¥0.004/1K input, ¥0.012/1K output

示例:
  输入 500 Token + 输出 300 Token
  GPT-4 成本：$0.033
  Claude-Sonnet 成本：$0.006
  Qwen-Plus 成本：¥0.0056
```

## 相关文件

- [OpenClaw 性能优化指南](https://docs.openclaw.ai/guides/performance)
- [Token 优化最佳实践](https://docs.openclaw.ai/guides/token-optimization)
- [Agent 调试工具](https://docs.openclaw.ai/tools/debugger)

## 触发词

- 自动：检测 performance、optimize、token、latency、profiling 相关关键词
- 手动：/agent-profiler, /performance-analysis, /optimize-agent
- 短语：性能分析、优化 Agent、Token 消耗、响应时间

## Usage

1. Install the skill
2. Configure as needed
3. Run with OpenClaw
