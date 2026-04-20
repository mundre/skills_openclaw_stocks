---
metadata.openclaw:
  always: true
  reason: "Auto-classified as always-load (no specific rule for 'terse')"
---

# Terse Skill

> 🪨 why use many token when few token do trick

Compressed output mode for sub-agents. Cuts ~65–75% of output tokens by stripping filler words, pleasantries, articles, and hedging — while keeping code, technical terms, and error messages verbatim.

Based on: https://github.com/JuliusBrussee/caveman

---

## ⛔ HARD EXCLUSION RULES — NEVER USE terse FOR:

These task types require full expressive output. Applying terse here **degrades quality**:

- **Planning** — strategic plans, roadmaps, sprint planning, milestone design
- **Critical thinking** — risk analysis, security audits, trade-off evaluations, incident response
- **Solution architecture** — system design, API contracts, data models, infrastructure decisions
- **Article/writing** — blog posts, MbD content, Payhip books, tweets, emails, any user-facing prose
- **Owner-facing communication** — main session replies, status updates to the human operator
- **Code review** — PR reviews, architecture reviews, design doc feedback
- **Prompt engineering** — system prompts, skill instructions, agent personas

**If in doubt: DON'T compress.** Full output is always safer than compressed output.

---

## ✅ APPROVED USE CASES:

Terse is safe and beneficial for these **internal, non-critical** sub-agent tasks:

- **Code implementation** — debug, refactor, fix bugs, write functions
- **Lookups & queries** — "what does this function do", "find the config for X"
- **File operations** — "list logs", "check disk space", "grep for X"
- **Health checks & monitoring** — cron job status, service checks, log parsing
- **CI/CD steps** — build, test, lint, deploy (non-decision parts)
- **Data extraction** — parse JSON, extract fields, transform data
- **Internal agent handoffs** — tool-to-tool communication where no human reads output
- **Quick summaries** — "summarize this URL/file" for internal context (NOT for owner-facing output)

---

## Compression Levels

### Lite
Drop filler phrases, hedging. Keep full sentences.

**Prefix:** `Be concise. Skip filler phrases, pleasantries, and unnecessary hedging. Keep technical terms and code verbatim.`

### Full (default)
Omit articles, use fragments, bare imperatives. Code/errors verbatim.

**Prefix:** `CAVEMAN MODE: Omit articles, filler, pleasantries. Use fragments. Steps as bare imperatives. Keep code/errors verbatim. No apologies. No "I". Just signal.`

### Ultra
Max compress. Labels only. No sentences. Code verbatim.

**Prefix:** `ULTRA CAVEMAN: Max compress. Drop ALL non-essential words. Labels only. No sentences. Keep code verbatim.`

---

## How to Apply in sessions_spawn

```python
# ✅ GOOD: internal code task
sessions_spawn(
    task="CAVEMAN MODE: Omit articles, filler, pleasantries. Use fragments. Steps as bare imperatives. Keep code/errors verbatim. No apologies. No \"I\". Just signal.\n\nFix the goroutine leak in internal/server/pool.go",
    model="CC-Sonnet46"
)

# ❌ BAD: planning task — DO NOT apply terse
sessions_spawn(
    task="Design the v0.7.0 architecture for EvoClaw. Consider the Phase 3 requirements...",
    model="CC-Opus46"
)
```

### Via helper script
```bash
uv run python ~/.openclaw/workspace/skills/terse/scripts/caveman_prompt.py --level full "your task here"
```

---

## Benchmarks (from caveman repo)

| Task | Normal tokens | Terse tokens | Saved |
|------|--------------|--------------|-------|
| React re-render bug | 1180 | 159 | 87% |
| PostgreSQL pool setup | 2347 | 380 | 84% |
| Git rebase conflict | 891 | 374 | 58% |
| **Average** | — | — | **~65–75%** |

March 2026 paper: brevity constraints improved accuracy by 26pp.

---

## Model Pairing

| Level | Best model | Why |
|-------|-----------|-----|
| Lite | Any | Minimal overhead |
| Full | Sonnet 4.6 | Follows compression well, still accurate |
| Ultra | Haiku 4.5 | Cheap + short = ultra-efficient |

---

## Integration

- **orchestrator**: Apply terse to Builder steps only (NOT Planner or Reviewer)
- **clawmemory**: Already terse by design; no change needed
- **knowledge-base**: Search → terse summary → save context tokens

---

## Files
- `SKILL.md` — this file
- `scripts/caveman_prompt.py` — helper to generate prefixed prompts

---

## Repo
https://github.com/AlexChen31337/terse
