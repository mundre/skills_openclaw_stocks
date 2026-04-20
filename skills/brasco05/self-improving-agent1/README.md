# 🧠 Self-Improving Agent

**Make your AI agent learn from every mistake — automatically.**

Most AI agents repeat the same mistakes. They forget corrections, ignore errors, and start fresh every session. This skill changes that.

Self-Improving Agent captures every learning, correction, and error into structured log files that persist across sessions. Your agent gets smarter with every interaction.

---

## What It Does

- **Logs corrections** — when you say "no, that's wrong", it's captured
- **Tracks errors** — failed commands, broken APIs, unexpected behavior
- **Records feature gaps** — when you ask for something the agent can't do yet
- **Promotes to memory** — important learnings get elevated to AGENTS.md, SOUL.md, or CLAUDE.md automatically
- **Detects patterns** — recurring issues trigger promotion to permanent rules

## When It Triggers

| Situation | Action |
|-----------|--------|
| Command fails | → Logged to ERRORS.md |
| User says "that's wrong" | → Logged to LEARNINGS.md |
| User asks for missing feature | → Logged to FEATURE_REQUESTS.md |
| Same issue occurs 3+ times | → Promoted to permanent memory |

## Works With

- ✅ Claude Code
- ✅ OpenClaw
- ✅ Codex CLI
- ✅ GitHub Copilot
- ✅ Any agent that reads markdown files

## Quick Start

1. Install via ClawhHub or manually copy to your skills folder
2. The skill activates automatically when errors or corrections occur
3. Learnings are stored in `.learnings/` in your workspace
4. Review and promote high-value learnings to permanent memory files

## File Structure

```
.learnings/
├── LEARNINGS.md      # Corrections, insights, best practices
├── ERRORS.md         # Command failures, integration errors
└── FEATURE_REQUESTS.md  # Requested capabilities
```

## Why This Matters

Without this skill, your agent resets every session. With it, every mistake becomes institutional knowledge that makes future sessions better.

**Your agent remembers. Your agent improves. Your agent gets smarter.**

---

*Built for OpenClaw. Compatible with all major AI coding agents.*
