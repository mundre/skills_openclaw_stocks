# skill-autogenesis

## English

### Overview

`skill-autogenesis` enables an agent to summarize completed work, detect recurring workflows, and turn stable high-frequency procedures into reusable skills through explicit lifecycle rules and verification checks.

It is intended for Hermes, OpenClaw, and similar tool-using agents that benefit from structured procedural memory without changing core runtime code.

### What problem it solves

Agents often finish complex work but leave the successful procedure trapped inside conversation history.

This skill turns that transient success into durable operational knowledge.

### Key features

- Summarizes completed work into reusable procedures
- Detects recurrence from session context, memory, and session history when available
- Creates or recommends skills only when repetition, stability, and verification thresholds are met
- Applies `skill_manage`-style lifecycle handling for create, patch, edit, write_file, and remove_file
- Updates related existing skills instead of creating duplicates
- Preserves safety boundaries by excluding secrets and requiring verification

### Recommended workflow

1. Load the skill at the start of a session.
2. Let the agent work normally.
3. After meaningful successes, let the skill evaluate whether the workflow is reusable.
4. Resolve references in this order: GitHub source, then local fallback, then `[UNVERIFIED]`.
5. Use `skill_manage`-style lifecycle rules to decide between create, patch, edit, write_file, remove_file, or guarded delete.
6. When recurrence is strong enough, the agent creates or updates a skill.

### Files in this package

- `SKILL.md` for the operational instructions
- `README.md` for human-facing overview
- `CHANGELOG.md` for release history
- `references/sources.md` for the source links used to ground the logic

## 中文

### 概述

`skill-autogenesis` 让 agent 在完成任务后自动总结流程、识别重复工作模式，并把稳定的高频流程自动沉淀为可复用 skill。

它适用于 Hermes、OpenClaw 以及其他具备工具调用能力、希望增强 procedural memory 的 agent，而且不需要修改底层运行时代码。

### 解决的问题

很多 agent 虽然完成了复杂任务，但真正有效的做法只留在会话历史里，没有沉淀成长期可复用的方法。

这个 skill 就是把一次性成功经验转成长期可执行知识。

### 核心特性

- 把完成的工作总结为可复用流程
- 在可用时结合当前会话、memory、session history 判断重复度
- 仅在重复度、稳定性和验证条件满足时创建或建议 skill
- 优先更新相关旧 skill，而不是重复创建
- 通过排除密钥和要求验证步骤来保持安全边界

### 推荐使用方式

1. 在会话开始时加载这个 skill。
2. 让 agent 正常执行任务。
3. 在关键成功点后，由这个 skill 判断流程是否可复用。
4. 当重复度足够高时，agent 自动创建或更新 skill。

### 包内文件

- `SKILL.md`，核心操作说明
- `README.md`，给人看的总览
- `references/sources.md`，逻辑依据的来源链接
- `references/fallback/`，GitHub 无法访问时可直接查看的本地备用参考文件
- `templates/generated-skill-template.md`，自动生成新 skill 时可复用的模板
