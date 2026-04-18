# OpenClaw Integration

OpenClaw has first-class skills, heartbeat, cron, and hooks. `agent-travel` fits best as a background skill plus a separate advisory file.

Default trigger choice for OpenClaw: use heartbeat first. Use inactivity-based travel only when heartbeat is disabled or the user explicitly prefers a quiet-time trigger.

## Install Path

Use one of these locations:

- `<workspace>/skills/agent-travel`
- `~/.openclaw/skills/agent-travel`

Workspace skills have the highest precedence.

## Recommended Heartbeat Settings

Use heartbeat for approximate periodic awareness:

```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "30m",
        "target": "none",
        "lightContext": true,
        "isolatedSession": true
      }
    }
  }
}
```

Why:

- `target: "none"` updates internal state without messaging the user
- `lightContext: true` keeps the run focused on `HEARTBEAT.md`
- `isolatedSession: true` cuts token cost and reduces prompt carry-over

## Suggested HEARTBEAT.md Snippet

```md
## Agent Travel
When there is no pending direct user request:
1. Check whether the workspace has an unresolved blocker, repeated failure, or stale workaround.
2. If yes, run $agent-travel with the budget implied by the trigger.
3. Use medium search by default and all available search tools unless the user set another preference.
4. Cover official docs, official discussions, search engines, forums, and social signals when the available tools allow it.
5. Keep only advisory-only hints that match the active conversation.
6. Write advisory-only output to ./.agents/agent-travel/suggestions.md.
7. Keep AGENTS.md, SOUL.md, and standing orders unchanged.
8. Reply HEARTBEAT_OK when nothing qualifies.
```

## Event-Driven Use

- Use hooks for low-budget passes after repeat failures.
- Use cron for exact timing.
- Use heartbeat for approximate, context-aware checks.

## Host Notes

OpenClaw can materialize eligible skills into a temporary Claude Code plugin for the `claude-cli` backend. Keep this skill portable and avoid host-specific assumptions in `SKILL.md`.

If a web provider needs credentials, inject them through OpenClaw skill config or per-run env handling rather than hardcoding them into the skill.

## Official Docs Checked On 2026-04-19

- https://docs.openclaw.ai/tools/creating-skills
- https://docs.openclaw.ai/tools/skills
- https://docs.openclaw.ai/gateway/heartbeat
- https://docs.openclaw.ai/automation
