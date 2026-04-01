---
name: memory-governor
description: Memory governance core for AI agents. Defines what is worth remembering, where it should go, when it should be promoted, and what should be excluded, while providing a shared memory contract for other skills. 记忆治理内核。统一定义什么值得记、该记到哪、何时升级、什么不要记，并为其他 skill 提供统一的 memory contract。
---

# Memory Governor

Reusable memory-governance core for different host environments.

The OpenClaw integration in this repository is only a reference host profile, not the only host model.

It is not a second-brain system, sync bus, or knowledge manager.  
It governs what should be remembered, where it should go, when it should be promoted, and what should be excluded.

这是一个可复用于不同宿主环境的记忆治理内核。

当前仓库中的 OpenClaw 集成只是它的一个 reference host profile，不是唯一宿主。

它不是 second brain，不是外脑总线，也不是 Obsidian / Notion / OmniFocus 同步器。

它只负责四件事：

1. 定义什么值得记
2. 定义该记到哪
3. 定义什么时候升级 / 提炼
4. 定义什么不要记

如果没有读取顺序、状态更新语义和生命周期规则，记忆治理是不完整的。

## When to Use

Use this skill when:

- you need to decide whether something should enter memory
- you need to choose the right memory layer or target class
- you need to promote daily / correction / working state into durable rules
- multiple skills are starting to define memory differently and need governance

在这些场景使用：

- 需要判断一条信息是否应该进入记忆系统
- 需要决定信息应该写入哪一层
- 需要把 daily / correction / working state 升级为长期规则
- 需要为其他 skill 提供统一的记忆规则
- 发现多个 skill 对“记忆”有不同写法或不同口径，需要治理

## First Reading Path

If this is your first time opening `memory-governor`, start here:

1. `SKILL.md`
2. `references/memory-routing.md`
3. `references/promotion-rules.md`
4. `references/exclusions.md`
5. `references/adapters.md`

如果你是第一次接触 `memory-governor`，先读这些：

1. `SKILL.md`
2. `references/memory-routing.md`
3. `references/promotion-rules.md`
4. `references/exclusions.md`
5. `references/adapters.md`

剩下的 reference 文件按需打开，不必第一次就全读完。

## What Counts as Memory

只有会改善未来判断、恢复、执行质量或协作一致性的信息，才算记忆。

典型包括：

- 长期稳定偏好
- 长期稳定事实
- 当天关键事件
- 明确纠错
- 可复用经验
- 当前推进态
- 临时恢复线索

不属于记忆的内容，见 [references/exclusions.md](references/exclusions.md)。

## Core Rule

统一的是 **memory contract**，不是统一所有 skill 的实现。

这意味着：

- 所有 skill 应该服从同一套记忆分类、路由、升级、排除规则
- 但每个 skill 可以保留自己的内部逻辑、下游工具、交互方式、目录习惯

一句话：

**统一内核，不统一一切。**

## Target Classes

内核优先定义的是抽象目标类型，不是某个可选 skill 的具体路径。

推荐使用这些标准 target classes：

- `long_term_memory`
- `daily_memory`
- `reusable_lessons`
- `proactive_state`
- `working_buffer`
- `project_facts`
- `system_rules`
- `tool_rules`

具体文件路径只是 adapter 的实现细节。

其中：

- `proactive_state` 和 `working_buffer` 是 stateful targets
- 它们不应被写成无穷 append 日志
- 默认需要 freshness、replace / merge、retention 规则

## Routing Order

处理任何一条候选信息时，按这个顺序判断：

1. 这条信息值不值得记？
2. 它属于哪一类记忆？
3. 这类记忆默认属于哪个 target class？
4. 当前环境里，这个 target class 应该由哪个 adapter 落地？
5. 它现在是短存，还是已经值得升格？
6. 它是否命中排除条件？

详细路由见 [references/memory-routing.md](references/memory-routing.md)。

歧义项优先级见 [references/routing-precedence.md](references/routing-precedence.md)。

## Promotion Rules

所有升级都应先提炼，再升格。

禁止：

- 把原始日志直接写进长期层
- 把 working buffer 直接当长期记忆
- 把系统级治理文件当临时记录入口

详细规则见 [references/promotion-rules.md](references/promotion-rules.md)。

状态型 target 的更新语义见 [references/stateful-targets.md](references/stateful-targets.md)。

如果宿主需要更强的结构化约束，见 [references/schema-conventions.md](references/schema-conventions.md)。

生命周期规则见 [references/retention-rules.md](references/retention-rules.md)。

恢复时的读取顺序见 [references/read-order.md](references/read-order.md)。

## Skill Integration

其他 skill 接入本内核时，遵循以下原则：

- skill 可以声明自己会产出哪些信息类型
- skill 可以声明默认把这些类型写到哪里
- skill 不应自行发明新的全局记忆层定义
- skill 不应绕过排除规则
- skill 不应把下游沉淀规则误写成上游记忆规则

接入方式见 [references/skill-integration.md](references/skill-integration.md)。

## Adapters

`memory-governor` 可以提供默认 adapter，但不应把它们当成唯一真理。

例如：

- `long_term_memory` -> `MEMORY.md`
- `daily_memory` -> `memory/YYYY-MM-DD.md`
- `reusable_lessons` -> 如果装了 `self-improving`，则映射到 `~/self-improving/...`
- `reusable_lessons` -> 如果没装 `self-improving`，则映射到本地 fallback 文件

默认 adapter 说明见 [references/adapters.md](references/adapters.md)。

接入检查见 [references/integration-checklist.md](references/integration-checklist.md)。

分发安装与包外集成说明见 [references/installation-integration.md](references/installation-integration.md)。

宿主差异说明见 [references/host-profiles.md](references/host-profiles.md)。

## Never Do

- 不把本 skill 扩展成“大一统自用记忆系统”
- 不把 Obsidian / Notion / OmniFocus 的落地逻辑写进治理内核
- 不强迫所有 skill 共享同一种实现方式
- 不发明新的主干记忆目录，除非治理层已明确批准
- 不把 secrets、原始长日志、短期噪声写入记忆系统

## Phase Boundary

当前只做治理内核。

这意味着：

- 可以定义 contract
- 可以定义 references
- 可以约束其他 skill 的写法
- 不能在这一阶段偷偷长成统一执行总线

如果未来要做整合层或完整自用记忆系统，应在治理层稳定后单独立项。
