# Feishu Group Usage Guide

## Scope note

This file provides Feishu-specific examples only. Feishu is not required to use `context-flow`; the same patterns can be adapted to any group-chat surface.

## Purpose

This file shows how to use `context-flow` in Feishu group collaboration.
It maps common user phrases to recommended response patterns, and clarifies when to enter real collaboration mode versus when to stay in normal single-agent execution mode.

## Note on "收口"

In this context, `收口` means consolidating scattered discussion, partial results, and intermediate execution into one current valid version that preserves only the main line, completed work, pending work, boundaries, and next step.
It is used to stop drift, reduce noise, and re-anchor the collaboration thread.

## Common Feishu phrases -> recommended response

### 1. User says: `这个任务你分工处理一下`

Recommended response:

```md
分工安排：
- @方案agent：整理执行方案和边界
- @执行agent：执行、收口并统一对外同步

当前状态：
- @方案agent：已派发
- @执行agent：处理中

协作摘要：
目标：先收窄方案，再由主控 agent 执行和收口。
边界：群里不贴长过程，只同步关键状态。
回报：最终只回一版结论。
```

### 2. User says: `这个你自己判断要不要分工`

Recommended response:

```md
我先判断这件事是否需要真实分工。
如果需要，我会先派发再收口；如果不需要，我就直接处理，不伪装成协作模式。
```

### 3. User says: `最后只给我一个结果`

Recommended response:

```md
收到。
中间如果需要分工，我只在群里同步必要状态，最后只给你一版收口结果。
```

### 4. User says: `先让负责方案的 agent 看一下`

Recommended response:

```md
分工安排：
- @方案agent：先看方案、边界和风险
- @执行agent：根据方案结果执行并收口

当前状态：
- @方案agent：已派发
- @执行agent：处理中

协作摘要：
目标：先由方案 agent 收窄判断范围，再进入执行。
边界：方案输出先回主控 agent，不直接在群里发散展开。
回报：我最后统一收口。
```

### 5. User says: `这个任务你派个 agent 只查一个点`

Recommended response:

```md
我会按局部任务卡片派发，只让子 agent 处理一个点，不下发整段聊天历史。
处理完后我再统一给你结论。
```

### 6. User says: `这串有点乱，你先收口`

Recommended response:

```md
协作摘要：
当前以后只以这一版状态为准。

已完成：
- ...

处理中：
- ...

未开始：
- ...

下一步：
- ...

说明：
旧讨论不再作为当前执行依据。
```

### 7. User says: `继续`

Recommended response:

```md
我先做恢复检查，再决定继续哪条主线。
如果当前任务不明确，我会先确认，不直接恢复历史待办。
```

### 8. User says: `别在群里刷太多`

Recommended response:

```md
收到。
后续我只在群里同步薄状态：动作、负责人、状态、下一步，不贴长日志和长推理。
```

### 9. User says: `你直接干，不用分工`

Recommended response:

```md
收到，我直接处理。
这轮不进入协作模式，也不输出分工安排、当前状态、协作摘要。
```

### 10. User says: `把现在谁在干什么给我说清楚`

Recommended response:

```md
当前状态：
- @agent名：已派发 / 处理中 / 已完成 / 失败 / 已跳过

协作摘要：
我只同步当前有效状态，不展开旧过程。
如果你需要，我可以再补一版统一收口说明。
```

## Usage advice

- Enter collaboration mode only when there is real division of work
- Do not fake `分工安排` / `当前状态` / `协作摘要` when only one agent is working
- Keep the group thin even when collaboration is real
- If the Feishu thread becomes noisy, prefer a reset summary before continuing
- If the user only says `继续`, do a resume check first instead of blindly resuming the old task line
