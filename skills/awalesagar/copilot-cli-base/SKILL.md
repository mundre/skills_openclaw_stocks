---
name: copilot-cli
description: >
  Reference knowledge base for GitHub Copilot CLI. Use when answering questions about
  Copilot CLI features, commands, configuration, plugins, hooks, skills, MCP servers,
  custom agents, automation, or troubleshooting CLI workflows.
---

# Copilot CLI Reference Skill

GitHub Copilot CLI is a terminal-native AI coding agent. This skill provides reference docs for all features, commands, and operational patterns.

## Quick Reference

**Interactive:** `copilot` → trust directory → `/login` → prompt
**Programmatic:** `copilot -p "PROMPT" --yolo --no-ask-user -s`
**With permissions:** `copilot -p "PROMPT" --allow-tool='shell(git:*), write' --no-ask-user`
**Custom agent:** `copilot -p "PROMPT" --agent=my-agent`
**Model override:** `copilot -p "PROMPT" --model claude-opus-4.6`

## When to Use Copilot CLI vs Claude Code

- **Rate-limited on Claude Code?** → Use Copilot CLI as fallback
- **CI/CD automation?** → Copilot CLI (built-in Actions support)
- **Clean stdout needed?** → Claude Code (no PTY/ANSI issues)
- **Long iterative reviews?** → Copilot CLI (better for many iterations)

See `reference/patterns-and-best-practices.md` for the full decision matrix.

## Key Gotchas

- Always use `-p` (not `-i`) for automation — `-i` hangs
- `--yolo` does NOT skip folder trust — pre-trust in `~/.copilot/config.json`
- No `copilot config set` — edit config JSON manually
- Size timeouts by complexity: 120s (simple) → 1800s (large)
- Background servers die between exec spawns — restart each time

See `reference/troubleshooting.md` for all issues and fixes.

## Reference Documents

Full index: `reference/index.md`

| File | Contents |
|------|----------|
| `getting-started.md` | Installation, auth, config, permissions, env vars |
| `usage.md` | Interactive & programmatic modes, commands, shortcuts, model selection |
| `automation-and-delegation.md` | CI/CD, GitHub Actions, autopilot, delegate, fleet, custom agents |
| `customization.md` | Custom instructions, plugins, MCP servers, enterprise governance |
| `hooks.md` | Hook types, config, denial responses, policy scripts |
| `integrations.md` | VS Code integration, ACP server |
| `research.md` | `/research` reports, `/chronicle` session history |
| `troubleshooting.md` | Auth, rate limits, SIGTERM, PTY, trust, config gotchas |
| `patterns-and-best-practices.md` | Decision matrix, prompt engineering, anti-patterns |

All files in `reference/` directory.
