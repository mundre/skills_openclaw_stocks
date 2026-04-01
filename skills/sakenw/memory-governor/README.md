# Memory Governor

Memory governance core for AI agents.  
AI agent 的记忆治理内核。

`memory-governor` helps you decide:

- what is worth remembering
- where it should go
- when it should be promoted
- what should be excluded

It is designed for agents that already have multiple memory layers, multiple skills that write memory, or optional memory-related adapters.

It is **not** a second-brain platform, sync bus, or universal knowledge manager.  
It is a governance layer.

## 中文摘要

`memory-governor` 给 agent 一套共享的记忆 contract。

它帮助宿主判断：

- 什么应该记
- 该先路由到哪个 target class
- 该由哪个 adapter 落地
- 哪些短期信息值得升格
- 什么根本不该进入记忆

它特别适合：

- 已经有多层记忆的宿主
- 有多个会写记忆的 skill
- optional adapter 越来越多、边界开始变乱的系统

它 **不会** 在安装时静默重写宿主。  
推荐用这三种状态来理解它：

- `Installed`：治理内核已可用
- `Integrated`：宿主已显式接线
- `Validated`：checker 已确认接线状态

## English Summary

`memory-governor` gives agents a shared memory contract.

It helps a host decide:

- what should be remembered
- which target class it belongs to
- which adapter should store it
- when short-term information should be promoted
- what should never enter memory at all

It works best for hosts that already have multiple memory layers, optional memory-related skills, or growing routing ambiguity.

It does **not** silently rewrite the host on install.  
The intended model is:

- `Installed`: the governance core is available
- `Integrated`: the host is explicitly wired to it
- `Validated`: the host checker confirms the wiring

## At a Glance

- Standard target classes for agent memory
- `memory type -> target class -> adapter / fallback`
- Stateful target rules for current-task and recovery memory
- Explicit `Installed / Integrated / Validated` readiness model
- Host manifest support via `memory-governor-host.toml`
- Generic host example, bootstrap script, and host checker
- OpenClaw-compatible reference profile without making OpenClaw the default world

## 一眼看懂

- 标准化的 agent memory target classes
- `memory type -> target class -> adapter / fallback`
- 面向 current-task / recovery memory 的 stateful target 规则
- 明确的 `Installed / Integrated / Validated` readiness 模型
- 通过 `memory-governor-host.toml` 声明宿主 contract
- 自带 generic host 示例、bootstrap 脚本和 host checker
- 兼容 OpenClaw，但不把 OpenClaw 写成默认世界观

`memory-governor` 是一个给 AI agent 用的记忆治理内核。

它解决的不是“怎么把所有东西都存起来”，而是更基础的问题：

- 什么值得记
- 该记到哪
- 什么时候升级成长期规则
- 什么根本不该记

如果你的 agent 已经开始有多层记忆，或者多个 skill 都会“写点东西”，这个问题迟早会出现。  
一开始看起来都能用，后面就会越来越乱。

`memory-governor` 的目标，就是先把这层宪法立住。

这个包由两部分组成：

- generic core
- host profiles

当前仓库里的 OpenClaw 集成是 reference profile，不是唯一默认宿主。

Current version:

- `0.2.4-beta`

## It Is Not

In short, it is not:

- a second-brain platform
- a Notion / Obsidian sync engine
- a universal sync bus
- an auto-archiving system
- a catch-all knowledge manager

它不是：

- second brain
- Notion / Obsidian 同步器
- 外脑总线
- 自动归档系统
- 大而全知识管理平台

它只负责治理。

## What It Gives You

安装后，你会得到：

- 一套统一的记忆分类规则
- 一组标准 target classes
- adapter / fallback 模型
- stateful target 规则
- 轻量 schema conventions + validator
- retention / read-order 规则
- 轻量 bootstrap 入口
- 路由规则
- 升级 / 提炼规则
- 排除规则
- 其他 skill 的接入模板

这意味着你的系统可以统一这些问题：

- “长期记忆”和“临时状态”怎么区分
- `reusable_lessons` 怎么稳定进入恢复路径
- optional skill 没装时怎么办
- 不同 skill 要不要共享同一套记忆口径
- 哪些规则属于全局，哪些只是下游工具自己的写法

## Core Model

`memory-governor` 用的是三层模型：

### 1. Memory Types

先判断一条信息是什么。

比如：

- key progress update
- reusable lesson
- recovery hint

### 2. Target Classes

再把它路由到抽象目标类型。

当前标准 target classes：

- `long_term_memory`
- `daily_memory`
- `reusable_lessons`
- `proactive_state`
- `working_buffer`
- `project_facts`
- `system_rules`
- `tool_rules`

### 3. Adapters

最后再由当前环境里的 adapter 决定具体落到哪个文件。

比如：

- `daily_memory` -> `memory/YYYY-MM-DD.md`
- `proactive_state` -> `proactivity` if resolved
- `proactive_state` -> packaged fallback template if not
- `reusable_lessons` -> `self-improving` if resolved
- `reusable_lessons` -> packaged fallback template if not

这让内核不必依赖某个具体插件。

其中 `proactive_state` 默认应理解为一个抽象 state family。
它可以由一个 combined fallback 文件实现，也可以像 `proactivity` 一样由 `memory.md + session-state.md` 联合实现。

## Why This Design Matters

很多 agent 记忆设计一开始就犯一个错：

直接把某个具体路径、具体插件、具体外脑工具，当成记忆系统本身。

这会导致三个问题：

1. optional skill 变成 hidden dependency
2. 不同 skill 各自发明自己的记忆口径
3. 一旦换工具，整套记忆模型都要重写

`memory-governor` 反过来做：

- 先定义抽象内核
- 再用 adapter 接当前环境
- 缺 adapter 时走 fallback

所以它更像操作系统的 memory contract，而不是某个插件的说明书。

## Minimal Example

我们已经用一个最小 demo 验证过这套模型：

- `../demo-memory-consumer/SKILL.md`

这个 demo skill 只做三件事：

- 把当天关键进展路由到 `daily_memory`
- 把可复用经验路由到 `reusable_lessons`
- 把临时恢复线索路由到 `working_buffer`

然后为每个 target class 指定：

- preferred adapter
- fallback 行为

这证明第三方 skill 可以只依赖公开 contract 接入，而不用依赖仓库内私有实现。

如果你想看一个不依赖 OpenClaw 目录结构的完整宿主示例，再看：

- `examples/generic-host/README.md`

## Installation

English quick view:

1. Install `memory-governor`
2. Read `SKILL.md`
3. Decide whether to integrate it into the host

Install does **not** silently modify `AGENTS.md`, other skill files, or existing memory files.

Script compatibility:

- Python 3.11+ works with the standard-library `tomllib`
- Python 3.9 / 3.10 should install `tomli`

最小安装只需要：

1. 安装 `memory-governor`
2. 阅读 `SKILL.md`
3. 决定要不要做包外集成

默认情况下，安装 skill **不会** 自动修改宿主的 `AGENTS.md`、其他 skill 的 `SKILL.md` 或现有记忆文件。

`memory-governor` 当前提供的是：

- 规则
- snippet
- manifest
- checker
- bootstrap

而不是“安装即接管宿主”的副作用式安装器。

## Readiness States

`memory-governor` 的使用状态，建议明确分成三层：

1. `Installed`
   skill 本体已安装，规则、references、snippets、scripts 可用。
2. `Integrated`
   宿主已经完成包外接入，例如：
   - 主入口承认 `memory-governor`
   - 相关 skill 已补 `Memory Contract`
   - 宿主已声明 `memory-governor-host.toml`
3. `Validated`
   宿主已通过 `scripts/check-memory-host.py` 检查。

这意味着：

- `Installed` != 完整生效
- `Integrated` 才表示宿主真的接上了治理规则
- `Validated` 才表示接线已经被工具确认

所以对外不要说“安装后立即完整工作”，更准确的说法是：

- 安装后可立即使用规则层
- 集成后可获得完整治理效果
- 校验通过后可确认宿主 readiness

完整说明见：

- `references/installation-integration.md`
- `references/bootstrap.md`
- `references/adapter-manifest.md`
- `references/schema-conventions.md`
- `references/host-checker.md`
- `references/openclaw-adoption-prompts.md`

## First Reading Path

English quick reading path:

1. `SKILL.md`
2. `references/memory-routing.md`
3. `references/promotion-rules.md`
4. `references/exclusions.md`
5. `references/adapters.md`

如果你是第一次打开这个 skill，推荐按这个顺序读：

1. `SKILL.md`
2. `references/memory-routing.md`
3. `references/promotion-rules.md`
4. `references/exclusions.md`
5. `references/adapters.md`

然后再按需看这些：

- 想接入其他 skill：`references/skill-integration.md`
- 想接宿主：`references/installation-integration.md`
- 想做宿主声明：`references/adapter-manifest.md`
- 想做校验：`references/host-checker.md`
- 想理解恢复读取：`references/read-order.md`
- 想设计 OpenClaw 提示：`references/openclaw-adoption-prompts.md`

## Integration

如果你想让现有系统正式承认这套规则，通常会做这些事：

1. 在 `AGENTS.md` 加一段 `Memory Governance`
2. 为会写记忆的 skill 补 `Memory Contract`
3. 给宿主加 `memory-governor-host.toml`
4. 检查 optional adapters 是否存在
5. 准备 fallback 文件

可复制模板见：

- `assets/snippets/AGENTS-memory-governance.md`
- `assets/snippets/SKILL-memory-contract.md`
- `assets/snippets/ADAPTERS-fallback-note.md`

先看宿主说明：

- `references/host-profiles.md`

注意：

- 这些属于包外集成动作
- 默认不应在安装时静默执行
- 如果以后要自动化，也应该是显式触发的 guided integration

如果你只是 `Installed` 而没有 `Integrated`，skill 仍然可用，但只处于规则参考模式，不应宣称“完整接入”。

## Key References

- `VERSION`
- `CHANGELOG.md`
- `RELEASE-NOTES-0.2.0-beta.md`
- `SKILL.md`
- `examples/generic-host/README.md`
- `references/bootstrap.md`
- `references/adapter-manifest.md`
- `references/schema-conventions.md`
- `references/host-checker.md`
- `references/openclaw-adoption-prompts.md`
- `scripts/validate-memory-frontmatter.py`
- `scripts/check-memory-host.py`
- `references/before-after.md`
- `references/memory-routing.md`
- `references/routing-precedence.md`
- `references/promotion-rules.md`
- `references/stateful-targets.md`
- `references/retention-rules.md`
- `references/read-order.md`
- `references/exclusions.md`
- `references/adapters.md`
- `references/skill-integration.md`
- `references/integration-checklist.md`
- `references/host-profiles.md`

## Current Status

当前状态可以理解为：

- 内核已成型
- demo 接入已验证
- 接入前后对比页已补
- generic host 验证已补
- generic host bootstrap 已补
- manifest-driven host checks 已补
- OpenClaw manifest-driven host checks 已补
- key fallback templates now have machine-checkable frontmatter
- fallback 已定义
- 分发说明已补齐

还没做的：

- 更完整的公开发布包装

## One-Line Summary

`memory-governor` 不帮你多记东西。  
它帮你避免记乱。
