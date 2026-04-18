# Claude Code Integration

Claude Code supports skills, `CLAUDE.md`, auto memory, and hooks. Use skills for the workflow, `CLAUDE.md` for a tiny pointer, and hooks for deterministic trigger points.

Default trigger choice for Claude Code: use async hooks after task completion or stop events. Use inactivity-based travel only when hooks are unavailable or disabled.

## Install Path

Use one of these:

- project: `./.claude/skills/agent-travel/SKILL.md`
- personal: `~/.claude/skills/agent-travel/SKILL.md`

## Advisory Boundary

Keep travel output in a separate repo-local file:

`./.agents/agent-travel/suggestions.md`

Import it from `CLAUDE.md` under a dedicated heading:

```md
# Shared Agent Rules
@./AGENTS.md

# Agent Travel Suggestions
@./.agents/agent-travel/suggestions.md
```

This keeps the advisory block visibly separate from the core rules.

## Suggested Hook Shape

Use a `Stop` hook or `Notification` hook to trigger a background update after Claude finishes a task and is waiting for input.

Example `./.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR/.claude/hooks/agent-travel.ps1\"",
            "async": true,
            "timeout": 120,
            "shell": "powershell"
          }
        ]
      }
    ]
  }
}
```

The hook should decide whether the last task qualifies, then update `./.agents/agent-travel/suggestions.md`.
Run `agent-travel` with medium search by default, all available search tools, and active-conversation-only output.

## Memory Placement

Claude auto memory is for stable project knowledge and user preferences. `agent-travel` output is short-lived external advice, so keep it in the advisory file instead of `MEMORY.md`.

## Official Docs Checked On 2026-04-19

- https://code.claude.com/docs/en/skills
- https://code.claude.com/docs/en/memory
- https://code.claude.com/docs/en/hooks
- https://code.claude.com/docs/en/hooks-guide
