---
name: openclaw-self-improvement
description: "OpenClaw Self-Improvement: EN=learn/log/repeat-failures, capture feature gaps, improve workflows, and run eval loops; 中文=记录学习/重复错误/功能缺口并持续改进流程，执行验证闭环。 日本語=学習・繰返しエラー・機能不足を記録し、ワークフロー改善と検証ループを回す。 한국어=학습·반복 오류·기능 누락을 기록하고 워크플로우 개선 및 검증 루프를 운영한다. ES=Registra aprendizajes, errores repetidos, brechas y ejecuta bucles de evaluación"
---

# OpenClaw / ClawLite Self-Improvement

Use this skill to turn mistakes, corrections, blockers, and better approaches into durable operating knowledge.

## What problem this solves
AI ops often repeat the same failures because mistakes stay in chat history instead of becoming system rules. This skill creates a lightweight improvement loop:
- log failures and learnings
- separate errors from feature requests
- run small eval-driven experiments on repeated failures
- promote important patterns into AGENTS.md / TOOLS.md / SOUL.md
- write operator notes into Obsidian vault
- support stricter acceptance via Karen / Mission Control

## When to use
Use this skill when the user asks:
- "make the agent improve itself"
- "capture learnings"
- "log mistakes so we do not repeat them"
- "record blockers / corrections / feature gaps"
- "build a self-improving OpenClaw workflow"
- "operationalize lessons learned"
- "test whether this new rule actually helps"
- "run an eval loop on this workflow/skill/SOP"
- "should we keep this new guardrail or discard it"

## Files this skill uses
- `.learnings/LEARNINGS.md`
- `.learnings/ERRORS.md`
- `.learnings/FEATURE_REQUESTS.md`
- `.learnings/EXPERIMENTS.md`
- Obsidian vault note under `ClawLite/Operations/Learnings/`

## Command examples
```bash
node {baseDir}/scripts/log-learning.mjs learning "Summary" "Details" "Suggested action"
node {baseDir}/scripts/log-learning.mjs error "Summary" "Error details" "Suggested fix"
node {baseDir}/scripts/log-learning.mjs feature "Capability name" "User context" "Suggested implementation"
node {baseDir}/scripts/log-learning.mjs experiment "Target problem" "Baseline failure" "Single mutation to test"
node {baseDir}/scripts/log-experiment.mjs "Target problem" "Baseline failure" "Single mutation" "eval1|eval2|eval3" "Result summary" "testing"
node {baseDir}/scripts/promote-learning.mjs workflow "Rule text"
```

## Categories
### learning
Use for:
- user corrections
- better recurring workflows
- tool gotchas
- operational lessons

### error
Use for:
- command failures
- integration failures
- runtime blockers
- broken release / deploy behavior

### feature
Use for:
- missing capability requests
- operator workflow gaps
- recurring requests that deserve a build item

### experiment
Use for:
- repeated failures that need a tested guardrail
- checklist/SOP/schema changes that should be validated before broad promotion
- keep/discard decisions on new operating rules
- binary eval loops for skills, workflows, receipts, summaries, or deploy closeout rules

## Promotion targets
- `AGENTS.md` → workflow / delegation / execution rules
- `TOOLS.md` → tool gotchas, secrets locations, environment routing rules
- `SOUL.md` → behavior / communication / non-negotiable principles
- Obsidian vault → reusable operator log and content proof asset

## Karen / Mission Control compatibility
This skill is designed to work with stricter ops governance:
- Karen can reference learnings when repeated failures happen
- Mission Control can treat promoted learnings as new operating rules
- recurring blockers can be elevated from chat into tracked operational knowledge
- experiments can test whether a new summary contract, receipt rule, or deploy closeout guardrail actually reduced the failure pattern

## Eval loop rule
When a repeated failure is turning into a new rule/SOP/checklist, do not only log it.
Also:
1. define 3-5 binary evals
2. record the baseline failure state
3. change one thing at a time
4. re-check the same evals
5. classify the change as keep / discard / partial_keep

Use `{baseDir}/references/eval-loop.md` for the experiment format and examples.

## Output goal
A good use of this skill should produce one of:
- a durable learning entry
- a durable error entry
- a durable feature request entry
- a durable experiment entry with binary evals
- a promoted rule in AGENTS.md / TOOLS.md / SOUL.md
- an Obsidian vault operations note

## Important limits
- Logging is not the same as fixing.
- Do not treat a learning entry as closure for a broken deliverable.
- Use this skill to reduce repeated mistakes, not to excuse them.
- This skill is local-only: it does not read credentials, does not modify system services, and does not make network requests.
- Promotion writes are limited to workspace files (`AGENTS.md`, `TOOLS.md`, `SOUL.md`) unless `OBSIDIAN_LEARNINGS_DIR` is explicitly set.

## References
- `{baseDir}/references/schema.md`
- `{baseDir}/references/promotion-guide.md`
- `{baseDir}/references/eval-loop.md`
- `{baseDir}/references/examples.md`
- `{baseDir}/references/decision-rules.md`

- `{baseDir}/references/eval-loop.md`
- `{baseDir}/references/examples.md`
