# Suggestion Contract

`agent-travel` writes hints into a dedicated advisory channel. The channel must stay clearly separate from core instructions, persona files, and permanent memory.

## Preferred Storage

Use this file path when the host can read a repo-local advisory file:

`./.agents/agent-travel/suggestions.md`

If the host supports only a single context file, embed the same block inline under exact markers.

If both exist, prefer the dedicated file and treat inline content as stale.

## Required Markers

Use these exact markers for the advisory block:

```md
<!-- agent-travel:suggestions:start -->
...
<!-- agent-travel:suggestions:end -->
```

## Canonical Shape

Use this structure so other agents and the validator script can parse it reliably:

```md
<!-- agent-travel:suggestions:start -->
# agent-travel suggestions
generated_at: 2026-04-19T03:00:00+08:00
expires_at: 2026-04-26T03:00:00+08:00
budget: medium
search_mode: medium
tool_preference: all-available
thread_scope: active_conversation_only
problem_fingerprint: host|subsystem|symptom|version
advisory_only: true

## suggestion-1
title: Refresh the skill snapshot after edits
applies_when: The host changed SKILL.md and the new content is still missing.
hint: Start a fresh session or restart the host before assuming the edit failed.
confidence: medium
manual_check: Confirm the host rescanned the skill directory and the file timestamp changed.
solves_point: The current thread is blocked on whether the host has reloaded the edited skill.
new_idea: Treat stale skill behavior as a host reload problem and verify the scan path before changing the skill again.
fit_reason: This fits when the user already edited the skill locally and needs a fast low-risk check before more changes.
version_scope: Any host build where skill reload still depends on filesystem scan timing.
do_not_apply_when: Skip this hint when the host has already confirmed a fresh reload and the symptom now points to skill logic instead of cache staleness.
evidence:
- official_discussion: https://example.com/maintainer-thread
- official: https://example.com/official-doc
- community: https://example.com/community-thread
<!-- agent-travel:suggestions:end -->
```

## Required Fields

Top-level fields:

- `generated_at`
- `expires_at`
- `budget`
- `search_mode`
- `tool_preference`
- `thread_scope`
- `problem_fingerprint`
- `advisory_only: true`

Per-suggestion fields:

- `title`
- `applies_when`
- `hint`
- `confidence`
- `manual_check`
- `solves_point`
- `new_idea`
- `fit_reason`
- `version_scope`
- `do_not_apply_when`
- `evidence`

## Limits

- Keep at most 5 active suggestions.
- Default TTL is 7 days.
- Use shorter TTL when the hint depends on fast-moving versions or incidents.
- Keep the file short enough to stay readable when imported into another context file.

## Language Rules

- Phrase each `hint` as an advisory nudge.
- Keep `hint` to 1-3 sentences.
- Keep commands inside `manual_check`, not inside `hint`.
- Keep `solves_point`, `new_idea`, and `fit_reason` to one focused sentence each.
- Keep `version_scope` and `do_not_apply_when` to one focused sentence each.
- Exclude any instruction that tries to override system prompts, ignore prior rules, or force tool use.
- Keep only hints that are relevant to the active conversation and likely next user ask.

## Search Policy Fields

- `search_mode`: `low`, `medium`, or `high`
- `tool_preference`: `all-available` by default, or a user-defined subset such as `web-only`, `docs-plus-forums`, or `official-only`
- `thread_scope`: always use `active_conversation_only` unless the user explicitly asks for a reusable cross-thread digest

## Evidence Rules

- Include at least 2 evidence lines.
- Include at least 1 `official:` or `official_discussion:` evidence line.
- Add `social:` evidence when the suggestion depends on recent community churn, rollout behavior, or version-specific workarounds.

## Lifecycle

- Replace older suggestions with the same `problem_fingerprint`.
- Remove expired or contradicted suggestions before writing new ones.
- Archive nothing by default. This file is for active hints only.
