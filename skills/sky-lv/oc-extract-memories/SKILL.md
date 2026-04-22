---
name: extract-memories
version: 3.1.0
description: "Extract key memories from conversation into topic files. Triggers: extract memories, 提炼记忆, /extract-memories. Auto-triggers on conversation end words."
license: MIT
triggers:
  - 提炼记忆
  - 提取记忆
  - extract-memories
  - "/extract-memories"
---

# extract-memories v3.1.0 — 对话记忆提炼

对话结束时主动分析本轮对话，将值得持久化的信息写入 `memory/topics/` 下的独立 topic 文件，同时更新 `MEMORY.md` 索引。

## 自动触发

检测对话结束词：再见 / bye / 下次见 / 拜拜 / 结束了 / 先这样 / see you / that's all

## 四类记忆类型

| 类型 | 存什么 | 格式要求 |
|------|--------|---------|
| `user` | 用户角色/偏好/知识 | 一段文字 |
| `feedback` | 用户纠正或确认 | 正文 + Why + How to apply |
| `project` | 截止/动机/约束 | 正文 + Why + How to apply |
| `reference` | 外部系统URL/路径 | URL/路径 + 用途 |

## 禁止存储（6条）

1. 代码结构/文件路径（可从源码读）
2. Git 历史（git log 是权威）
3. 调试方案（修复在代码里）
4. AGENTS.md/MEMORY.md 已有内容
5. 临时任务状态
6. PR 列表/活动摘要

## Topic 文件格式

```yaml
---
name: 名称
description: 一句话描述
type: user / feedback / project / reference
---
正文内容

**Why:** 原因（feedback/project 必须）
**How to apply:** 何时适用（feedback/project 必须）
```

## MEMORY.md 更新

追加一行：`- [名称](topics/文件名.md) — 一句话 hook（≤150字符）`

## 输出格式

```
已为您提炼本轮记忆 ✅
写入位置：memory/topics/
提炼结果：N条
```
