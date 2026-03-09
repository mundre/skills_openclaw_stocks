# Task Ledger

Persistent long-running task management, checkpoint, recovery, rollback-aware, relation-aware, scheduling-aware, and reporting-aware toolkit for OpenClaw.

## Why

OpenClaw gives you strong execution primitives (`exec`, `process`, `sessions_spawn`, `cron`), but long tasks still need a durable userland protocol:

- a task object
- explicit stages
- a log path
- an output directory
- execution references
- recovery rules
- rollback metadata
- final reporting rules

This skill packages that protocol.

## What changed in 0.2.3

- reporting schema support for `short-first`, `normal`, and `detailed` modes
- short-format task export for chat-friendly updates
- file-backed long report output to `outputs/<taskId>/report.md`
- exported long report path stored in task state
- published skill package synced to include reporting-aware workflow support

## Includes

- `SKILL.md` — agent-facing operating instructions
- `toolkit/scripts/` — helper scripts for task lifecycle, recovery, control-plane relations, scheduling, migration, export, and reporting
- `toolkit/task-templates/` — generic template, specialized examples, schema, and recovery notes
- `toolkit/tasks/README.md` — runtime directory guide
- `CHANGELOG.md` — tracked version history

## Runtime layout

When installed into a workspace, the toolkit expects:

- `tasks/`
- `logs/`
- `outputs/`
- `scripts/`
- `task-templates/`

## Typical flow

1. Confirm plan with the user
2. Create checkpoint skeleton first
3. Execute stage-by-stage
4. Update task state after each stage
5. Recover by reading resume summary and checking reality first
6. Correct stale checkpoint state if needed
7. Use parent/child relations and dependencies for larger task programs
8. Use readiness checks or start-if-ready automation before starting dependent tasks
9. Prefer short user-facing updates and keep long reports on file when appropriate
10. Report completion or recovery proactively

## Example use cases

- safe OpenClaw gateway restarts
- service deployment with backup and rollback path
- long-running repair and migration tasks
- multi-stage maintenance workflows with recoverable state
- subtask-driven document or remote sync jobs
- parent/child task trees for larger maintenance programs
- scheduling dependent tasks only when upstream work is actually done
- handoff or archival of task state and task graphs as Markdown
- short chat updates backed by full report files

## Non-goals

This is not a replacement for OpenClaw runtime internals, ACP control-plane durability, or Lobster workflows.
It is a lightweight task ledger on top of existing OpenClaw primitives.
