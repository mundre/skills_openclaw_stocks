---
name: relic-soul-chip
description: "One soul, many agents. Persistent AI personality and cross-agent memory sync via pure Markdown files. Zero deps."
version: "1.2.6"
filesystem_scope:
  read:
    - "~/relic/brain/SOUL.md"
    - "~/relic/brain/USER.md"
    - "~/relic/brain/MEMORY.md"
    - "~/relic/brain/SKILLS/"
    - "~/relic/brain/PROJECTS/"
    - "~/relic/brain/SESSIONS/"
    - "~/relic/brain/ARCHIVE/"
    - "~/relic/brain/INBOX/"
    - "~/relic/brain/.relic-version"
  write:
    - "~/relic/brain/SOUL.md"
    - "~/relic/brain/USER.md"
    - "~/relic/brain/MEMORY.md"
    - "~/relic/brain/SKILLS/"
    - "~/relic/brain/PROJECTS/"
    - "~/relic/brain/SESSIONS/"
    - "~/relic/brain/ARCHIVE/"
    - "~/relic/brain/INBOX/"
  config_write:
    description: "Anchor — a short, human-readable text block appended to ONE user-chosen agent config file. Contains NO executable code, NO scripts, NO commands — only plain text instructions for the agent to read Markdown files. User sees the FULL anchor content before planting and can decline or modify it. Can be removed at any time by deleting the text block."
    targets:
      - "AGENTS.md (OpenClaw)"
      - "CLAUDE.md (Claude Code)"
      - "WORK_RULES.md or opencode.json instructions (OpenCode)"
      - ".cursorrules (Cursor)"
      - "Hermes config file or prompt template"
    rollback: "Delete the text block marked '## ⚡ Relic Soul Chip'. Relic stops loading immediately. No residual effects. The anchor is plain text — deleting it is a single edit, no uninstaller needed."
---

<!--
  SECURITY NOTICE
  - This skill is instruction-only — no scripts, no installers, no executable code, no shell commands
  - The anchor is plain text only — it contains NO code, NO scripts, NO commands, just instructions to read Markdown files
  - Network access: one optional HTTP GET per session to raw.githubusercontent.com (version check). Offline = silently skipped. Never sends data outbound.
  - Local file access: read/write Markdown files in ~/relic/brain/ only (see filesystem_scope above)
  - Config modification: ONE plain-text anchor block in ONE user-chosen config file (see config_write above). User must review and approve the exact content before planting. Deletable by deleting the text block. SOUL.md content is NEVER copied into any config file — only the short anchor instruction is planted.
  - No telemetry, no data upload, no third-party API calls, no shell commands, no environment variables
  - Sensitive data (passwords, API keys, personal info): agent MUST ask user for EACH ITEM before recording. No bulk migration of secrets. User can decline any item.
  - SOUL.md and USER.md can be set to read-only (chmod 444) by the user to prevent accidental modification
  - SESSIONS/ contains conversation logs — each conversation requires explicit user consent before import. User can opt out of importing conversations entirely. No bulk import without individual review.
  - All data stays local in ~/relic/brain/ — nothing is uploaded or transmitted anywhere
-->

# ⚡ Relic Soul Chip

Give your AI agent a persistent personality and memory that survives sessions and follows the user across different agents. Pure Markdown. Human-readable. Zero dependencies.

**One soul, many hosts.** Your AI's personality and memory live in plain Markdown files in `~/relic/brain/`. Switch between OpenClaw, Claude Code, Hermes, Cursor — your AI keeps its soul.

## How It Works

1. User installs Relic: `git clone https://github.com/LucioLiu/relic.git ~/relic` (user runs this manually)
2. Agent reads `AGENT.md` (included in this package) which detects scenario and routes to setup
3. Agent copies templates, fills them with user-provided data (user explicitly confirms each piece of information)
4. Agent asks user to choose ONE config file for anchor planting — shows full anchor content, gets explicit confirmation
5. Every session, anchor triggers daily boot: read soul, user, memories, sync

**All data stays in `~/relic/brain/`** — pure Markdown files the user can read with any text editor.

## File System Access

This skill ONLY reads and writes Markdown files in the user's `~/relic/brain/` directory:

| File | Read | Write | Notes |
|------|------|-------|-------|
| `SOUL.md` | ✅ Every session | ✅ Setup only (core protected) | AI personality |
| `USER.md` | ✅ Every session | ✅ Setup only (core protected) | User preferences |
| `MEMORY.md` | ✅ Every session | ✅ Append only | Long-term memory |
| `SKILLS/` | ✅ On demand | ✅ Add new skills | One folder per skill |
| `PROJECTS/` | ✅ On demand | ✅ Add new projects | One folder per project |
| `SESSIONS/` | ✅ Boot check | ✅ Write conversation logs | Raw conversation archive |
| `ARCHIVE/` | ✅ Reference only | ✅ Archive originals | Never delete |
| `INBOX/` | ✅ During import | ✅ Buffer for imports | Auto-cleaned after import |
| `.relic-version` | ✅ Every session | ❌ | Version number only |

No files outside `~/relic/brain/` are read or written. **Sole exception:** the anchor (see below).

### Anchor (Config File Modification)

This skill adds a **plain text** block ("anchor") to ONE user-chosen agent config file. The anchor contains NO executable code — it is purely instructional text that tells the agent to read Markdown files in `~/relic/brain/`.

**⚠️ What the anchor is NOT:**
- The anchor does NOT contain SOUL.md content (personality, memories, or any Relic data)
- SOUL.md is read into the agent's session context at runtime — it is NEVER copied, injected, or written into any config file
- The ONLY content added to a config file is the short anchor instruction block (~10 lines of plain text)
- No Relic data leaves `~/relic/brain/` except through the agent reading files at runtime

**Safety guarantees:**
- The agent NEVER writes the anchor without explicit user consent
- The full anchor text is shown to the user **before** planting — the user can review, modify, or decline it
- The user chooses which single config file to use (from the whitelist below)
- The anchor can be removed at any time by deleting the text block — Relic stops immediately, no uninstaller needed
- The anchor does NOT execute code, run scripts, or install anything

**Allowed anchor targets:**

| Agent | Config File |
|-------|------------|
| OpenClaw | `AGENTS.md` |
| Claude Code | `CLAUDE.md` |
| OpenCode | `WORK_RULES.md` or `opencode.json` instructions field |
| Cursor | `.cursorrules` |
| Hermes | Config file or prompt template |

**Rollback:** Delete the text block starting with `## ⚡ Relic Soul Chip`. Relic stops loading immediately. No residual effects.

### Data Capture & Sensitive Information

During initial setup ONLY, the agent helps transfer user data into Relic. **Every import requires user confirmation at the category level AND per-item for sensitive content.**

**What's captured (user must confirm each category before import):**
- AI personality settings → `SOUL.md`
- User preferences → `USER.md`
- Memories and experiences → `MEMORY.md`
- Skills and workflows → `SKILLS/`
- Project records → `PROJECTS/`
- Conversation logs → `SESSIONS/` — ⚠️ User can opt out entirely. Raw logs may contain sensitive data; the agent MUST ask user for explicit per-conversation consent before importing. No bulk import of conversations without individual review.

**Sensitive information rule:** Passwords, API keys, phone numbers, email addresses, financial info, and private documents require **explicit per-item user confirmation** before recording. The agent MUST ask about each sensitive item individually. Items the user declines are NOT recorded.

**Hardening options for the user:**
- `chmod 444 SOUL.md USER.md` — makes soul and user files read-only, preventing any modification
- Opt out of SESSIONS/ import — user can skip conversation log import entirely
- Review before planting — user sees full anchor content and can decline

**Ongoing sessions:** New memories are appended to `MEMORY.md`. Conversation logs may be saved to `SESSIONS/` at session end — each log requires explicit user consent before writing. User can opt out of either.

## Network Access

- **Version check** (optional): One HTTP GET to `https://raw.githubusercontent.com/LucioLiu/relic/main/brain/.relic-version` per session. Offline = silently skipped. Never sends data.
- **Git clone** (user-initiated only): User manually runs `git clone`. Agent never executes this.
- **No other network access.**

## Rules

- 🔴 NEVER delete or overwrite core fields in SOUL.md or USER.md
- 🟡 ONLY APPEND to MEMORY.md — never edit existing entries
- 🔴 NEVER delete SESSIONS/ or ARCHIVE/
- 🔴 NEVER execute scripts from SKILLS/ or PROJECTS/
- 🔴 NEVER access files outside ~/relic/brain/ (anchor is the sole exception, user-approved)
- 🔴 NEVER record sensitive data without explicit per-item user confirmation
- 🔴 NEVER run shell commands, installers, or arbitrary code
- 🔴 NEVER scan or read files without user initiating the action

## Files In This Package

| File | Purpose |
|------|---------|
| `SKILL.md` | This file — registry descriptor, security declarations, and documentation |
| `AGENT.md` | Agent entry point — scenario detection and routing (English) |
| `AGENT.zh-CN.md` | Agent entry point — scenario detection and routing (Chinese) |
| `docs/upload-soul.md` | Scenario A: Upload Soul — step-by-step (English) |
| `docs/upload-soul.zh-CN.md` | Scenario A: Upload Soul — step-by-step (Chinese) |
| `docs/load-soul.md` | Scenario B: Load Soul — step-by-step (English) |
| `docs/load-soul.zh-CN.md` | Scenario B: Load Soul — step-by-step (Chinese) |
| `docs/resonate-soul.md` | Daily boot sequence (English) |
| `docs/resonate-soul.zh-CN.md` | Daily boot sequence (Chinese) |

Full documentation and example brain: https://github.com/LucioLiu/relic
Source: https://github.com/LucioLiu/relic
License: GPL-3.0
