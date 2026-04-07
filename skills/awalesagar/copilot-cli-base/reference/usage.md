---
title: "Usage Guide"
source:
  - https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference
  - https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli-agents/overview
  - https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference
category: reference
---

Interactive mode, programmatic mode, commands, shortcuts, and all usage patterns for Copilot CLI.

## Starting a Session

```bash
copilot                   # interactive session
copilot -i "PROMPT"       # interactive with initial prompt
copilot --continue        # resume most recent session
copilot --resume          # pick from session list
```

On first launch: trust directory → `/login` for OAuth.

## Two Modes

**Interactive:** `copilot` — starts terminal session with tool approval prompts.
**Programmatic:** `copilot -p "PROMPT"` — execute and exit. Use `-s` for clean output. Pipe: `echo "..." | copilot`.

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Esc` | Cancel current operation |
| `Ctrl+C` | Cancel / clear / exit (press twice) |
| `Ctrl+D` | Shutdown |
| `Ctrl+L` | Clear screen |
| `@FILE` | Include file in context |
| `!COMMAND` | Run shell command directly |
| `/` | Show slash commands |
| `Shift+Tab` | Cycle modes (standard/plan/autopilot) |
| `Ctrl+O` | Expand recent timeline items |
| `Ctrl+E` | Expand all timeline items |
| `Ctrl+T` | Toggle reasoning visibility |
| `Ctrl+G` | Edit prompt in external editor |
| `Ctrl+Y` | Edit plan in default editor |

## Slash Commands

**Session:** `/clear` `/new` `/resume` `/rename NAME` `/session` `/share file|gist` `/usage` `/exit`
**Navigation:** `/add-dir PATH` `/cwd PATH` `/list-dirs`
**Auth:** `/login` `/logout` `/user`
**Config:** `/model` `/theme` `/experimental` `/terminal-setup` `/allow-all` `/reset-allowed-tools`
**Features:** `/plan PROMPT` `/review PROMPT` `/delegate PROMPT` `/fleet PROMPT` `/research TOPIC` `/diff` `/compact` `/context`
**Customization:** `/agent` `/skills` `/plugin` `/mcp` `/lsp` `/init`
**Help:** `/help` `/feedback`

## Key CLI Options

| Option | Purpose |
|--------|---------|
| `-p PROMPT` | Programmatic prompt (exit after) |
| `-s` / `--silent` | Output only response |
| `-i PROMPT` | Interactive with initial prompt |
| `--model=MODEL` | Set AI model |
| `--agent=AGENT` | Use custom agent |
| `--resume=ID` / `--continue` | Resume session |
| `--allow-all` / `--yolo` | All permissions |
| `--allow-all-tools` | Skip tool approval |
| `--allow-tool=TOOL` / `--deny-tool=TOOL` | Tool permission control |
| `--autopilot` | Autonomous continuation |
| `--max-autopilot-continues=N` | Limit autopilot iterations |
| `--no-ask-user` | Disable user questions |
| `--no-custom-instructions` | Skip loading AGENTS.md etc. |
| `--output-format=FORMAT` | `text` (default) or `json` (JSONL) |
| `--share=PATH` / `--share-gist` | Export session transcript |
| `--secret-env-vars=VAR` | Redact env var values |
| `--additional-mcp-config=JSON` | Add MCP server for session |

## File Context (@)

```
Explain @config/ci/ci-required-checks.yml
Fix the bug in @src/app.js
```

Tab-completion works. Drag-and-drop images for visual references.

## Session Management

| Command | Purpose |
|---------|---------|
| `/clear`, `/new` | Reset context |
| `/resume` | Resume previous session |
| `/session` | Show session info |
| `/session checkpoints` | List compaction checkpoints |
| `/rename NAME` | Rename session |
| `/share file [PATH]` | Export to Markdown |
| `/compact` | Compress history manually |
| `/context` | Visualize token usage |

Auto-compaction triggers at 95% token limit. Session data at `~/.copilot/session-state/{session-id}/`.

## Plan Mode

Press `Shift+Tab` to cycle into plan mode, or `/plan PROMPT`.

1. Copilot analyzes request and codebase
2. Asks clarifying questions
3. Creates structured plan with checkboxes
4. Waits for approval before implementing

**Use for:** complex multi-file changes, refactoring, new features. **Skip for:** quick fixes, single file changes.

## Model Selection

| Model | Best for |
|-------|----------|
| Claude Opus 4.5 | Complex architecture, deep debugging |
| Claude Sonnet 4.5 (default) | Day-to-day coding |
| GPT-5.2 Codex | Code generation, code review |

Switch: `/model` (interactive) or `--model=MODEL` (CLI).

**Precedence:** custom agent def > `--model` > `COPILOT_MODEL` env > `config.json` > default.

**Availability:** Only GitHub-routed models work (e.g., `claude-opus-4.6`, `claude-sonnet-4`). For others, use BYOK env vars.

## Code Review

```
/review                                    # review all changes
/review Focus on security issues in @src/  # scoped
/review Use Opus 4.5 and Codex 5.2 to review changes against main  # multi-model
```

## Steering Agents

- **Queue messages** while Copilot is thinking to redirect
- **Inline feedback on rejection** — explain why so Copilot adapts
- Press `Esc` to stop a running operation

## Tool Availability Values

**Shell:** `bash`, `read_bash`, `write_bash`, `stop_bash`, `list_bash`
**File:** `view`, `create`, `edit`, `apply_patch`
**Agent:** `task`, `read_agent`, `list_agents`
**Other:** `grep`/`rg`, `glob`, `web_fetch`, `skill`, `ask_user`, `show_file`, `store_memory`, `task_complete`, `exit_plan_mode`

## Permission Approval Keys

| Key | Effect |
|-----|--------|
| `y` | Allow once |
| `n` | Deny once |
| `!` | Allow all similar for session |
| `#` | Deny all similar for session |
| `?` | Show details |
