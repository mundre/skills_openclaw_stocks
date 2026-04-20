---
name: ontology-kg
description: Typed knowledge graph for AI agent memory. Create entities, link relations, enforce constraints. JSONL append-only storage, zero dependencies. Use when agent needs structured memory beyond flat files.
---

# Ontology KG — 给你的 AI 一个结构化大脑

## Story

你的 AI agent 记住了 200 条信息，全塞在一个 MEMORY.md 里。找东西靠 grep，关系靠脑补。

"Alice 负责哪个项目？" —— grep Alice，翻 10 条记录，猜。
"什么任务 block 了发布？" —— 没法回答，因为依赖关系没存。
"上次会议谁参加了？" —— 运气好能找到，运气不好淹在 200 行里。

**问题不是记忆太少，是记忆没有结构。**

Ontology KG 给 agent 的记忆加上类型、关系和约束。Person 有 name，Task 有 status 和 blocker，Project 有 owner。entity 之间用 relation 连接，约束自动校验。

存储是 JSONL append-only 文件，零依赖，git 友好。

## Core Concept

```
Entity = { id, type, properties }
Relation = { from → rel_type → to }
Constraint = { type rules, relation rules, acyclic checks }
```

## Types

| Category | Types |
|----------|-------|
| People | Person, Organization |
| Work | Project, Task, Goal |
| Time | Event, Location |
| Info | Document, Message, Note |
| Resources | Account, Device, Credential |
| Meta | Action, Policy |

## Quick Start

```bash
# Init storage
mkdir -p memory/ontology
touch memory/ontology/graph.jsonl

# Create entities
python3 scripts/ontology.py create --type Person --props '{"name":"Alice"}'
python3 scripts/ontology.py create --type Project --props '{"name":"Website","status":"active"}'

# Link them
python3 scripts/ontology.py relate --from proj_001 --rel has_owner --to p_001

# Query
python3 scripts/ontology.py query --type Task --where '{"status":"open"}'
python3 scripts/ontology.py related --id proj_001 --rel has_task

# Validate all constraints
python3 scripts/ontology.py validate
```

## Storage Format (JSONL)

```jsonl
{"op":"create","entity":{"id":"p_001","type":"Person","properties":{"name":"Alice"}}}
{"op":"relate","from":"proj_001","rel":"has_owner","to":"p_001"}
```

Append-only. Git-friendly. Migrate to SQLite for big graphs.

## Key Constraints

- `Credential` cannot store secrets directly (must use `secret_ref`)
- `blocks` relation is acyclic (no circular dependencies)
- `Event.end >= Event.start`
- `Task` requires `title` + `status`

## When to Use

| Trigger | Action |
|---------|--------|
| "Remember that..." | Create/update entity |
| "What do I know about X?" | Query graph |
| "Link X to Y" | Create relation |
| "What depends on X?" | Traverse dependencies |
| "Show project status" | Aggregate by relations |
| Skills need shared state | Read/write entities |

## References

- `references/schema.md` — Full type definitions, relation types, constraints
- `references/queries.md` — Query patterns, traversal examples, aggregations

## Credits

Inspired by [oswalpalash/ontology](https://github.com/oswalpalash/ontology). Optimized for practical agent use with streamlined schema and better defaults.
