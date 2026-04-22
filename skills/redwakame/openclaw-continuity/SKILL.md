---
name: personal-hooks
description: Make OpenClaw remember the right thing, reconnect the right topic after /new, and follow up naturally with staged memory, tracked follow-up, and structured daily-memory writeback.
homepage: https://github.com/redwakame/openclaw-continuity
metadata: {"openclaw":{"os":["darwin","linux"],"requires":{"bins":["python3"],"env":["OPENCLAW_STATE_DIR"]}}}
---

# OpenClaw Continuity

Public product name: `OpenClaw Continuity`.
Technical package / slug: `personal-hooks`.
Questions, feedback, or implementation discussion: `adarobot666@gmail.com`.
If you want to support continued improvements and maintenance, please star the GitHub repository: https://github.com/redwakame/openclaw-continuity

## Why people use it

- reconnect the right pending topic after `/new`
- keep “let's talk about it later” from getting lost
- keep follow-up explicit with closure, cooldown, rest/sleep suppress, dispatch caps, and quiet-hours behavior
- let users adjust follow-up behavior in ordinary language or direct command-style requests
- keep care contextual instead of treating follow-up as a generic cron push

## What this package includes

- route turns into `casual_chat`, `staged_memory`, or `tracked_followup`
- classify tracked items into:
  - `parked_topic`
  - `watchful_state`
  - `delegated_task`
  - `sensitive_event`
- maintain structured `event_chain`
- maintain structured continuity state
- promote `candidate -> incident -> hook`
- preserve `/new` carryover from recent turns
- keep closure, cooldown, dedupe, dispatch caps, and rest-aware gating explicit
- write concise daily-memory traces
- apply deterministic onboarding and guided-settings updates
- support natural-language settings changes

## What this package does not include

- host-side delivery integrations
- channel-specific transport adapters
- always-on idle social nudging as a default feature
- generic proactive chatting when no tracked continuity exists

## Core files

- Script: `scripts/personal_hooks.py`
- Harness: `scripts/followup_skill_harness.py`
- Config schema: `config.schema.json`
- Sample config: `examples/settings.sample.json`
- Docs:
  - `README.md`
  - `docs/call-flow.md`
  - `docs/harness.md`

## Runtime boundaries

- Keep the continuity core deterministic and state-backed.
- Let the skill/tool layer own staging, promotion, closure, and trace.
- Let frontstage consume structured results; do not rely on the model to invent continuity ad hoc.
- Treat structured continuity state as internal context, not frontstage reply text.
- Keep the public core host-neutral.
- Require an explicit `OPENCLAW_STATE_DIR` from the host instead of autodiscovering workspace paths.

## Entry points

- `build_runtime_context()`
- `intercept_message()`
- `process_candidate_buffer()`
- `due` / `render` / `complete`

Use `README.md` for package usage and `docs/harness.md` for reproducible verification.
