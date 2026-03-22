---
name: context-flow
description: Manage context flow for group collaboration, child agents, and subagents. Use when coordinating multi-agent work, handing off tasks, preventing context overload, resuming after interruption, creating compact status summaries, or standardizing group collaboration templates.
---

# Context Flow

Use this skill when multi-agent work is at risk of becoming context-heavy, misaligned, or hard to resume cleanly. The goal is not to preserve every detail. The goal is to preserve the right details at the right layer.

## Core rules

- Keep group context thin; use group chat for actions, owners, statuses, and short summaries
- Pass only minimal necessary context to child agents; do not dump full transcripts by default
- Treat subagents as short-horizon workers for local problems, not long-horizon holders of the full task line
- Split long work by stage; create a short checkpoint before starting the next stage
- Externalize stable background into docs or memory files instead of re-sending it in every message
- Resume from stage summaries and stable documents, not from raw long transcripts or injected historical memory
- If tasks start drifting, constraints are being forgotten, or outputs become vague, stop and do a checkpoint before continuing

## Templates

Read `references/templates.md` when you need ready-to-use collaboration, task-card, checkpoint, resume, group-reset, controller sync, or secondary-acceptance templates. That file also includes Feishu-group examples for: real collaboration, non-collaboration cases, noisy-thread resets, compact child-agent handoffs, receipt-timeout handling, partially-complete states, and rule-update acceptance checks.

## Anti-patterns

Read `references/anti-patterns.md` when a collaboration thread becomes noisy, a child agent drifts, a subagent starts carrying too much context, a resume flow may reconnect to the wrong task line, or outputs are becoming vague and overloaded.

## Feishu usage

Read `references/feishu-usage.md` when the task is happening in a Feishu group and you need phrase-to-response guidance, examples of when to enter real collaboration mode, examples of when not to fake collaboration, or guidance on how to use `收口` in a noisy thread.

## Recovery lessons

Read `references/recovery-lessons.md` when the task is being resumed after interruption, when the active line is unclear, or when old injected history may be polluting the current task.

## Reflection lessons

Read `references/reflection-lessons.md` when repeated coordination mistakes need to be turned into stable rules, templates, or anti-patterns.

## Packaging

Read `references/packaging.md` when preparing this skill for packaging, review, or sharing.

## Overload signals

Do a checkpoint when two or more of these appear:

- the agent repeats questions about already-fixed scope
- old tasks start mixing into the current task line
- outputs become generic, vague, or overly broad
- key constraints or "do not do" items are being forgotten
- group-visible status no longer matches actual execution state
- one agent is carrying too many sub-goals in one active thread
- a subagent starts reasoning about the full task line instead of its local scope

## Recommended workflow

1. Define one clear main goal
2. Split by stage, not by transcript length
3. Send compact task cards to child agents
4. Keep group updates thin
5. Create a short checkpoint after each stage
6. Resume from the checkpoint plus stable docs
7. Promote repeated successful patterns into workspace rules or governance docs

## Companion docs

This skill works well with local collaboration-governance docs if the workspace already has them, but it does not require any workspace-specific files.

Typical helpful local companions include:
- a collaboration state-machine doc
- sync / acceptance templates
- a post-rule-change acceptance workflow

## References

- For workspace rule maintenance, also use `openclaw-workspace`
- For templates, use `references/templates.md`
- For common failure modes, use `references/anti-patterns.md`
- For Feishu-group phrasing and response patterns, use `references/feishu-usage.md`
- Trigger this skill with short phrases like `按 context-flow 来拆`, `给我一个阶段收口模板`, or `用 context-flow 收口`
