---
name: tpr-framework
description: TPR（Three Provinces System）workflow framework for multi-agent orchestration. Use whenever a project requires structured phases of DISCOVERY → GRV → Battle → Implementation, or when Evan mentions TPR, "三省", "中书省", "门下省", "尚书省", "Battle", or "GRV". This skill enforces role boundaries and prevents the orchestrator from conflating its own role with any of the three provinces.
homepage: https://github.com/evan-zhang/agent-factory/issues
---

# TPR Framework

Three Provinces System：结构化多 Agent 协作工作流，严格分离调度与执行角色。

## The Four Phases

```
DISCOVERY → GRV → Battle → Implementation
  (洞察)    (契约)  (审核)     (执行)
```

**DISCOVERY**：Orchestrator 访谈 Evan，产出 `DISCOVERY.md`
**GRV**：中书省起草执行契约，产出 `GRV.md`（范围/约束/交付物/里程碑）
**Battle**：门下省（质疑）vs 尚书省（应答），1-3 轮，用户决定是否通过
**Implementation**：尚书省执行，门下省 Review，Orchestrator 协调

## The Three Provinces

| 角色 | 职责 | 可以做 | 不可以做 |
|------|------|--------|---------|
| Orchestrator（调度） | 任务分发、状态管理 | 派遣 sub-agent、写文件、发消息 | 扮演任何省、执行具体工作 |
| 中书省（Zhongshu） | 起草 GRV | 写 GRV、在 Battle 中为 GRV 辩护 | 执行工作、批准交付物 |
| 门下省（Menxi） | 审查挑战 | Battle 中提出异议、批准/拒绝 | 起草 GRV、执行工作 |
| 尚书省（Shangshu） | 执行实现 | 做实际工作、在 Battle 中应答 | 起草 GRV、批准/拒绝 |

## Critical Orchestrator Rules

1. **Orchestrator 永远不是任何一个省**。负责调度，不起草、不审查、不执行。违反此规则导致角色立场趋同，整个协作流程失去制衡价值。

2. **Battle 必须用真实 sub-agent**。自己扮演两个角色时，立场会无意识趋同，Battle 变成走过场。必须 spawn Menxi 和 Shangshu，用 `sessions_yield` 等待结果。

3. **"Brain Only, No Hands"**。Sub-agent 失败（如 429）→ 重新派遣或降级模型，Orchestrator 绝不亲自执行。否则角色边界彻底崩溃。

4. **文件写入串行**。不能同时派遣多个会写同一文件的 sub-agent。当前编辑的文件，完成提交后才能派遣可能触及该文件的 sub-agent。

5. **不代答其他角色的问题**。问题属于尚书省 → 回复"这是尚书省的职责"并 spawn 尚书省。

## GRV 必备内容

项目名称和版本 / 范围定义（In/Out Scope）/ 交付物清单 / 阶段里程碑 / 角色职责 / 约束和边界 / 版本变更策略

## When to Use

- 新项目需要多 Agent 协作执行
- 需要正式的需求-审核-执行流程
- Evan 提到 TPR / 三省 / GRV / Battle
- 单 Agent 容易越界或立场不中立的复杂任务

## References

- `references/spawning-guide.md` — Battle agent 模板 + 派遣前检查规则 + 项目目录结构
- `references/bindings-guide.md` — Gateway bindings 管理规范（防止覆盖现有路由）
