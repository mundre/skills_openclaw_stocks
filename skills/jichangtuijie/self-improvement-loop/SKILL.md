---
name: self-improvement-loop
version: 4.6.1
description: |
  openclaw self-evolution loop — beyond Hermes Growth, strengthening self-growth and skill systems with controllable optimization.
  Hook captures feedback, distill refines pattern detection, threshold triggers notification,
  user decides A/B/C/D, AI skill generation and updates. Auto-detects first available channel from openclaw.json.
---

# self-improvement-loop v4.6.1

  openclaw self-evolution loop — beyond Hermes Growth, strengthening self-growth and skill systems with controllable optimization.
  Hook captures feedback, distill refines pattern detection, threshold triggers notification,
  user decides A/B/C/D, AI skill generation and updates. Auto-detects first available channel from openclaw.json.

---

## Features

### 🎯 Core Loop
1. **Auto-capture** — Hook detects CORRECTION/ERROR/FEATURE keywords in real-time, pushes reminders for AI to write to `~/.openclaw/workspace/.learnings/`
2. **Periodic scan** — `distill.sh` runs every 30min (mechanical scan + Python JSON output)
3. **Pattern detection** — count ≥ 2 triggers A/B/C/D notification to user
4. **User decision** — Reply A/B/C/D to create skill / optimize skill / skip / promote
5. **Auto-close** — skill-creator executes on A/B, result archived silently

### 🔍 Detection & Capture
- **Hook (handler.js)** — Real-time OpenClaw hook, intercepts CORRECTION/ERROR/FEATURE keywords, pushes reminders into context.messages for AI to act on
- **Keyword detection** — 3 categories: CORRECTION / ERROR / FEATURE, multilingual (EN/CN)
- **Pattern-Key format** — `<source>.<type>.<identifier>` (e.g. `hook.detection.correction`). Format validation: keys not matching `X.Y.Z` (3 parts, dot-separated) are downgraded to category-only for aggregation purposes. JSON output includes `pk_format_invalid: true` for AI to correct.

### 📊 Aggregation & Trigger
- **distill.sh** — Mechanical scan: extracts entry fields, counts Pattern-Key occurrences, outputs raw JSON
- **distill_json.py** — Python JSON generator (avoids shell quoting fragility)
- **Precise trigger formula** — `(count >= 2) AND (notified == false OR notification_count < count)`
- **Notification state machine** — notified + notification_count fields prevent repeated harassment
- **dormant state** — user picks C → dormant, no re-notification

### 🔄 Closure & Evolution
- **A/B/C/D decision loop** — Cron AI sends notification → user replies → main session executes
- **AGENTS.md injection** — install.sh auto-appends A/B/C/D handler to user's AGENTS.md
- **skill-creator integration** — A → create new skill, B → optimize existing skill , C → skip, D → promote to SOUL/AGENTS/TOOLS
- **match-existing-skill.sh** — Mechanical candidate matching (outputs skill list only)

### 🗄 Archive & Distill
- **archive.sh** — Silently archives resolved/promoted entries to `~/.openclaw/workspace/.learnings/archive/YYYY-MM.jsonl`
- **write_notified.py** — Writes notified state back to learnings MD files
- **memory-daily-distill** — Daily Cron (23:30): distills recent `memory/` → `learnings/`, updates Lessons Index

### 🛠 Infrastructure
- **Auto channel detection** — Scans openclaw.json for first available channel (Telegram/Discord/...)
- **Auto Telegram ID detection** — Reads allowFrom from openclaw.json, no hardcoded IDs
- **No hardcoded paths** — All scripts use `$HOME`, `~`, or `os.path.expanduser()`
- **Silent operation** — archive runs without interaction prompts

---

## Closed-Loop Flowchart

### Full Closed Loop (all paths)

```
┌─────────────────────────────────────────────────────────────┐
│  User session                                                  │
│  "No wait, it should be like this"                              │
└────────────────┬────────────────────────────────────────────┘
                 │ ①  
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  Hook (handler.js)  [Real-time interceptor]                  │
│  Keywords: CORRECTION / ERROR / FEATURE                       │
│  Pushes to context.messages → AI decides whether to write      │
│  ✅ Done (AI executes the write)                              │
└────────────────┬────────────────────────────────────────────┘
                 │ ②  Every 30min auto-trigger
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  self-improvement-check Cron                                │
│  distill.sh --check-only → distill_json.py → JSON       │
│                                                             │
│  Scan learnings/ count Pattern-Key occurrences                 │
│  count = 1 → Silent wait (threshold not reached)               │
│  count = 2+ → trigger notification                              │
│  count increases → re-notify ("appeared again")                  │
└────────────────┬────────────────────────────────────────────┘
                 │ ③  Pattern needs notification
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  Cron AI (current session)                                   │
│  Reads raw_md, understands what this pattern means              │
│  Calls match-existing-skill.sh for existing skill candidates   │
│  Generates A/B/C/D notification content                         │
│  Writes back notified state                                    │
│  Sends notification → [channel] user receives A/B/C/D options │
└────────────────┬────────────────────────────────────────────┘
                 │ ④  User replies
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  Main session (main agent)                                     │
│  Detects A → calls skill-creator to create new skill          │
│  Detects B → calls skill-creator to optimize existing skill    │
│  Detects C → mark dormant, silent skip                        │
│  Detects D → promote to SOUL/AGENTS/TOOLS                     │
└────────────────┬────────────────────────────────────────────┘
                 │ ⑤  Execution complete
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  archive.sh (silent)                                          │
│  resolved/promoted entries → archive to cold storage          │
│  ✅ Loop closed for this round                                 │
└─────────────────────────────────────────────────────────────┘
```

### Three Data Entry Paths

```
Path A: Hook real-time capture (passive)
─────────────────────────────────────────────────────────────
User session → handler.js detects keywords → push to context.messages
                                          AI receives reminder → decides to write learnings
                                                      ↓
                              self-improvement-check Cron
                              (scans all learnings every 30min)


Path B: memory-daily-distill (active distillation)
─────────────────────────────────────────────────────────────
memory/ log files → Daily 23:30 Cron → distill valuable content → write to learnings
                                                           ↓
                                        self-improvement-check Cron


```

### Four Notification Outcomes

**Batch processing**

```
Receive A → skill-creator → create skill → update learnings → archive
Receive B → skill-creator → optimize skill → update learnings → archive
Receive C → mark dormant → count reset → no more notifications
Receive D → promote to SOUL/AGENTS/TOOLS → promoted → archive
```

**Fallback mechanism**: Even if cron only notifies 1 pattern, the handler will still scan all pending JSON files—to avoid orphaned files caused by "user hasn't finished processing the old pattern yet, but a new pattern arrives.

### State Transitions

```
User correction ──→ Hook ──→ context.messages ──→ AI writes LEARNINGS.md (count=1, pending)
                                    ↓
                           Every 30min distill
                                    ↓
                        count=2 → send A/B/C/D notification
                                    ↓
                        User picks A → skill created → resolved → archive
                        User picks B → skill optimized → resolved → archive
                        User picks C → dormant → no more notifications
                        User picks D → promote to SOUL/AGENTS/TOOLS → promoted → archive
```

**Design principle**: Scripts do mechanics, AI does semantics.

---

## Architecture (technical view)

```
openclaw.json ──→ install.sh ──→ Auto-detect first available channel
                              └─→ (Telegram / Discord / ...)
                                    ↓
User message ──→ Hook (handler.js) ──→ context.messages ──→ AI writes to ~/.openclaw/workspace/.learnings/*.md

self-improvement-check Cron (every 30min, bound to main session)
  ├─→ distill.sh --check-only → distill_json.py → JSON
  ├─→ Semantic understanding + write notified state
  ├─→ Write ~/.openclaw/workspace/.learnings/.pending_notifications/<ts>_<pattern>.json
  └─→ Cron AI (current session)
        └─→ Send A/B/C/D notification to auto-detected channel
              ↑
User replies A / B / C / D on that channel
        ↓
    Main session receives message
        ↓
    Detects A/B/C/D → reads pending_notifications/ → executes skill-creator / promotion
```

---

## Components

| Component | Trigger | Role |
|----------|---------|-------|
| `handler.js` | Real-time | Detect CORRECTION/ERROR/FEATURE keywords, push reminders to AI context |
| `distill.sh` | Cron | Mechanical scan, extract fields, output raw data |
| `distill_json.py` | Cron | Python JSON generator |
| `write_notified.py` | Cron | Write Notified state back to MD |
| `archive.sh` | Cron | Archive resolved/promoted entries |
| `match-existing-skill.sh` | Cron | Match existing skills (mechanical, outputs candidates) |

---

## Installation

```bash
bash ~/.openclaw/workspace/skills/self-improvement-loop/install.sh
openclaw gateway restart
bash ~/.openclaw/workspace/scripts/self-improvement/distill.sh --check-only
```

---

## File Locations

```
~/.openclaw/workspace/
├── scripts/self-improvement/   ← Canonical Source (runtime)
│   ├── distill.sh / distill_json.py / write_notified.py
│   ├── archive.sh / match-existing-skill.sh
├── skills/self-improvement-loop/scripts/
│   └── setup_crons.py          ← Install-time tool (copies crons from cron-payloads.json)
├── .learnings/                ← Experience storage
│   ├── LEARNINGS.md / ERRORS.md / FEATURE_REQUESTS.md
│   └── archive/              ← Cold storage
~/.openclaw/hooks/self-improvement/
└── handler.js
~/.openclaw/workspace/.learnings/.pending_notifications/
└── <ts>_<pattern>.json       ← A/B/C/D context files
```

---

## Required Permissions (declared for transparency)

| Permission | Reason |
|------------|--------|
| `exec` | Runs distill.sh, archive.sh, match-existing-skill.sh for pattern detection and archiving |
| `read` (workspace) | Reads .learnings/*.md files for pattern scanning and notification |
| `write` (workspace) | Writes to .learnings/*.md to update notified state; creates .pending_notifications/*.json |
| `cron` | Creates and manages self-improvement-check (every 30min) and memory-daily-distill (daily) cron jobs |
| `gateway_api` | setup_crons.py calls the Gateway API to create crons with sessionTarget=current |
| `AGENTS.md write` | User manually appends A/B/C handler (install.sh prompts user to do this; not auto-injected) |
| `OPENCLAW_GATEWAY_TOKEN` | Used by setup_crons.py to authenticate with the Gateway API |

**Why these are safe:**
- All file operations are scoped to `~/.openclaw/workspace/.learnings/` and `~/.openclaw/scripts/self-improvement/`
- No credentials are hardcoded; all tokens come from environment variables
- Cron jobs run in isolated sessions with minimal tool access
- AGENTS.md injection is now user-initiated (not auto-written by install.sh)

## Dependencies

| Dependency | Note |
|-----------|------|
| OpenClaw | Base platform |
| Python3 | distill_json.py / write_notified.py |
| Node.js | OpenClaw + handler.js |
| skill-creator | Executes skill create/optimize on A/B |

---

## See Also

- `references/setup-guide.md` — Full installation and configuration guide

---

## Changelog

### v4.6.1 — archive.sh Bug Fixes (2026-04-20)

- **count_archived_occurrences grep pattern**: fixed JSON escaping issue — pattern `"\"pattern_key:\"$pk\""` → `"pattern_key.*$pk"`; also removed `|| echo 0` in favor of `[ -z "$result" ] && result=0`
- **json_escape()**: new bash function using Python json.dumps for proper JSON string escaping (handles newlines, quotes, backslashes)
- **Header conditional**: "Archive Dry-Run" vs "Archive" now reflects actual DRY_RUN flag state
- **JSONL cleanup**: fixed multiline JSON entries causing parse errors in archive

### v4.5.1og

### v4.5.1
- 统一三段式模板（发生了什么 / 根因 / 下次如何避免）替换 LEARNINGS/ERRORS/FEATURE_REQUESTS 原有字段；Phase 1 记录原则字段名对齐模板

### v4.5.0
- SKILL.md flowchart all-English; AGENTS.md injection → user-prompt; Required Permissions table added; Path C removed; Archive dead code removed; Pending file deletion + batch scan fixed; PK format validation added; File Locations now includes setup_crons.py; calc_trigger now checks count>=threshold directly (no longer relies on patterns[] gate); except branch fixed for string notified values
