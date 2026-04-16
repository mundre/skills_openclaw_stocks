---
name: relic
description: "One soul, many agents. Persistent AI personality and cross-agent memory sync via pure Markdown files. Switch from OpenClaw to Hermes to Claude Code — your AI keeps its soul. Zero deps."
---

# ⚡ Relic Soul Chip

> *"Store a soul as a digital file. Plug it into any AI agent. Even V."*

**One soul, many agents.** Your AI's personality and memory live in pure Markdown files. Switch between OpenClaw, Hermes, Claude Code, Cursor, Codex, or any agent — your AI keeps its soul.

## When to Use

- User says "set up Relic" or "I want my AI to remember me"
- User wants to transfer AI personality/memory from one agent to another
- User is switching agents (e.g., from OpenClaw to Hermes) and wants continuity
- User mentions persistent personality, AI soul, agent memory, cross-agent sync

## Quick Install

If Relic is not yet installed on this machine:

```bash
git clone https://github.com/LucioLiu/relic.git ~/relic
```

If `git` is not available, download and extract `https://github.com/LucioLiu/relic/archive/refs/heads/main.zip` to `~/relic/`.

## First-time Setup

**Do this automatically when the user asks to set up Relic. Walk them through each step.**

1. Check if `~/relic/brain/PROTOCOL.md` exists. If not, run the Quick Install above.
2. Read `~/relic/brain/PROTOCOL.md` Section 0 (First-time Setup) and follow all steps.
3. Copy templates: `SOUL.template.md` → `SOUL.md`, `USER.template.md` → `USER.md`, `MEMORY.template.md` → `MEMORY.md`
4. Ask the user: "What should your AI be called? What's its personality?" → Fill in `SOUL.md`
5. Ask the user: "What should your AI call you? Any preferences?" → Fill in `USER.md`
6. Verify: ask "What's your AI's name? What's your name?" — both answers must match what was written.
7. (Optional) Ask if the user wants the agent to auto-load Relic on every session. If yes, see PROTOCOL.md Section 9 for neural anchor setup.

## Every Session (Boot Sequence)

1. Read `~/relic/brain/SOUL.md` → load personality
2. Read `~/relic/brain/USER.md` → load user preferences
3. Read `~/relic/brain/MEMORY.md` → load recent events (last 30 entries)
4. Work normally, appending new memories as needed

## Memory Writing

Append to `~/relic/brain/MEMORY.md` with this format:

```
## YYYY-MM-DD HH:MM [AgentName]
Content: [what happened]
Type: preference / decision / experience / event / correction
Importance: high / medium / low
```

## Switching Agents

The user's soul lives in `~/relic/brain/`. Any agent that can read files can connect. The new agent reads the same files — all memories from previous agents are preserved. See PROTOCOL.md Scenario B for detailed cross-agent injection steps.

## Rules

- 🔴 **NEVER** modify SOUL.md or USER.md (read-only after setup)
- 🟡 **ONLY APPEND** to MEMORY.md (never edit or delete old entries)
- 🔴 **NEVER** access files outside `~/relic/brain/`
- ⚠️ **Always ask** before recording sensitive info — show the user what will be recorded and get confirmation

## Privacy

- All data stays local in `~/relic/brain/`. No API calls, no telemetry after install.
- Sensitive information requires explicit user confirmation before recording.
- MEMORY.md is append-only with timestamps — full audit trail.

## Updating

When a new version of Relic is released, run:

```bash
cd ~/relic && git pull
```

This updates protocol and template files only. Your SOUL.md, USER.md, MEMORY.md, SESSIONS/, and ARCHIVE/ are safe — they are listed in `.gitignore`.

## Full Documentation

For the complete protocol (import/export scenarios, memory consolidation, cross-agent sync, neural anchor), read `~/relic/brain/PROTOCOL.md`.

Source: https://github.com/LucioLiu/relic
