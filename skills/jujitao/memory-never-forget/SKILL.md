---
name: memory-never-forget
description: "Memory system v4.12: Active Memory + Memory Palace + Dual-Layer Dream Verification. The strongest memory system for OpenClaw agents."
metadata: { "openclaw": { "emoji": "🧠" } }
---

# 🧠 Memory Never Forget v4.12

A full-featured memory system for OpenClaw, integrating Active Memory retrieval, Memory Palace structured views, and a Dual-Layer Dream Verification mechanism — delivering "proactive memory + global view + verifiable consolidation."

**Core Logic: Active Memory = Memory Butler, Memory Palace = Knowledge Palace, Dual-Layer Dream = Verification & Consolidation Expert**

License: MIT-0 | Updated: 2026-04-15 | v4.12 adds Dual-Layer Verification

---

## Overview (v4.12)

This skill turns your OpenClaw agent into a truly "knowing" assistant by managing memory across **two orthogonal dimensions**:

1. **Temporal** (Atkinson-Shiffrin 3-stage model) — what to keep vs. what to prune
2. **Content** (4-type taxonomy from Claude Code) — where to store for fast retrieval

A **Dual-Layer Dream Verification** architecture ensures your agent's memories are reliable, hallucination-free, and continuously validated.

---

## Core Components

### 1. Active Memory — Proactive Retrieval

Before each response, Active Memory automatically retrieves and injects relevant memories into context.

**Retrieval Modes:**
- `message` — current message only
- `recent` — recent conversation
- `full` — full history (recommended)

**Capabilities:**
- Automatic preference learning
- Context inheritance (project background, historical conclusions)
- Real-time memory injection

### 2. Memory Palace — Structured Views

Provides multi-dimensional views of your agent's long-term memory:
- **Timeline** — chronological view of work progress
- **Projects** — aggregated by project
- **Technology** — organized by tech domain
- **Custom** — user-defined dimensions

### 3. Dual-Layer Dream Verification (Core v4.12 Innovation)

**Two independent but cross-verifying layers:**

> **Official Dream (12:30)** — Promotes short-term signals to long-term memory (MEMORY.md)
> ↓ outputs: DREAMS.md, memory/dreaming/deep/, etc.
> ↓
> **Refined Verify (13:00)** — Reads official outputs and cross-checks with independent judgment
> → Detects conflicts, hallucinations, stale entries → writes verify/ report
> → Supplements missed promotions

**Why verification matters:**
- AI memory systems suffer from **hallucination** (inventing facts) and **drift** (memory diverging from reality)
- Two independent systems checking each other = **verifiable, auditable, reliable**

---

## Two Orthogonal Dimensions

|Dimension|Framework|Purpose|
|---|---|---|
|Temporal (how long)|Atkinson-Shiffrin 3-stage model|Decay management — what to keep vs. prune|
|Content (what kind)|4-type taxonomy (Claude Code)|Classification — where to store for retrieval|

### Dimension 1: Temporal Layering

|Stage|Human Equivalent|Implementation|TTL|Action|
|---|---|---|---|---|
|Sensory|~0.25 sec perception|Current input context|Instant|Filter immediately — what deserves attention?|
|Short-term|Recent|Model context window 10 turns|10 turns|Pass through working filters|
|Working|Recent ~7 days|memory/YYYY-MM-DD.md + Active Memory|7 days|Extract signal → promote to long-term or let decay|
|Long-term|Permanent|MEMORY.md (index) + classified files|Permanent|Periodic review, prune when stale|

### Dimension 2: Content Classification (4 Types)

|Type|Directory|Content Example|
|---|---|---|
|user|memory/user/|User profile (role, preferences, knowledge, goals)|
|feedback|memory/feedback/|Lessons (corrections, confirmations, style)|
|project|memory/project/|Project state (work, decisions, reasoning)|
|reference|memory/reference/|External resources (links, tools, locations)|

---

## What to Save / What NOT to Save

### ✅ Save
- User's role, preferences, responsibilities, knowledge
- User corrections ("not like that", "should be this way")
- User confirmations ("yes exactly", "perfect, keep that")
- Project decisions and **the reasoning** (not just what, but why)
- New tools, links, resources
- External system locations and their purpose

### ❌ Don't Save
- ❌ Code patterns, architecture, file paths (derivable from codebase)
- ❌ Git history (`git log` is the authoritative source)
- ❌ Debugging solutions (the fix is in the code)
- ❌ Anything already documented elsewhere
- ❌ Ephemeral task state (write to `todos.md` instead)
- ❌ Raw conversation content

---

## MEMORY.md = Long-Term Index Only

MEMORY.md is the **index of long-term memories only**, never content. Format:
```
- [Title](path) — one-line description (<150 chars)
```

## Memory File Format

Every classified memory file must have frontmatter:

```yaml
---
name: Memory name
description: One-line description (used to judge relevance)
type: user|feedback|project|reference
created: YYYY-MM-DD
---

## Rule / Fact
(the content)

## Why
(reason / motivation)

## How to apply
(when and how to use this memory)
```

---

## Memory Drift Caveat

Memories can become stale. Rules:

1. **Verify first**: When referencing a file, function, or path — check it still exists
2. **Trust current state**: If memory conflicts with current observation, trust what you see now
3. **Update or delete**: When a memory is outdated, fix or remove it immediately
4. **Absolute dates**: Convert relative dates ("yesterday", "last week") to absolute dates

---

## Memory → Knowledge Sublimation

Not all mature memories should decay. Some **evolve into knowledge**.

### When to Sublimate

| Trigger | Detection Signal | Result |
|---------|-----------------|--------|
| **Project complete** | All tasks marked done, 3+ related project memories | Merge into `knowledge/project-postmortem.md` |
| **Feedback patterns** | 3+ related feedback entries (e.g., all about reply style) | Merge into `knowledge/user-work-style-guide.md` |
| **User depth** | User memory accumulates role, preferences, habits over time | Expand to `knowledge/user-playbook.md` |
| **Periodic review** | Dream detects high density of related memories in one category | Suggest: "Found 5 related feedback entries → merge into knowledge?" |

---

## Dual-Layer Dream Architecture

### Layer 1: Official Dream (12:30)

Triggered via cron `30 12 * * *` (your timezone). Produces:

| File/Directory | Contents | Read by Refined Verify? |
|---|---|---|
| `MEMORY.md` | Promoted long-term entries | ✅ |
| `DREAMS.md` | Human-readable Dream diary | ✅ |
| `memory/dreaming/deep/YYYY-MM-DD.md` | Deep phase report | ✅ |
| `memory/dreaming/light/YYYY-MM-DD.md` | Light phase output | ✅ |
| `memory/dreaming/rem/YYYY-MM-DD.md` | REM reflections | ✅ |
| `memory/.dreams/` | Internal machine data (program use only) | ❌ |

**Phases:**
1. **Light** — Sort and stage recent short-term material, dedupe
2. **Deep** — Score and promote durable candidates (6 weighted signals) to MEMORY.md
3. **REM** — Extract themes and reflection summaries

### Layer 2: Refined Verify (13:00)

Triggered via cron `0 13 * * *` (your timezone). Acts as the **verification layer**:

**Verification Dimensions:**
| Check | Content | On Conflict |
|---|---|---|
| Project status | Official Dream says "Project X done" but diary shows still in progress | ⚠️ Flag conflict |
| Decision conclusions | Recorded decision has since changed in reality | ⚠️ Flag stale |
| User preferences | Does Dream's user profile match USER.md? | ⚠️ Flag for review |
| Dates | Were relative dates converted to absolute? | ✅/❌ |
| Decay decisions | Is Dream's decision to let an entry decay reasonable? | ⚠️ Flag suspicious |

**Verification Report** (written to `memory/dreaming/verify/YYYY-MM-DD.md`):
```markdown
# Verification Report - YYYY-MM-DD

## Official Dream Status
- Entries promoted: X
- Top entry: X (score X)
- Disputed entries: X

## Conflict Log (⚠️)
| Entry | Official Dream | Refined Verify | Difference |
|---|---|---|---|
| ... | ... | ... | ... |

## Supplement Suggestions
- Additional promotions: X (missed by Official Dream)
- Needs user confirmation: X

## Verification Conclusion
- Consistency score: X/10
- Memory reliability: ✅ Reliable / ⚠️ Uncertain
```

---

## Session Lifecycle

### Session Start
```
1. Sensory: Read current input
2. Short-term: Last 10 turns from context window
3. Working: Read memory/today.md + memory/yesterday.md
4. Long-term: Read MEMORY.md index
```

### During Conversation
```
- New info → write to working memory (today's daily log)
- Learned something worth remembering → update MEMORY.md index + save classified file
- User preference → update USER.md + memory/user/
- Need to retrieve → find in MEMORY.md index → read classified file
```

### Session End
```
- Summarize → write to memory/today.md (working memory)
- Identify items for long-term → update classified files
- Update MEMORY.md index
- Mark items for Dream review (decay candidates)
```

---

## Workspace Structure

```
workspace/
├── MEMORY.md              # long-term memory index
├── USER.md                # user info
├── SOUL.md                # AI identity
├── todos.md               # task tracking
├── HEARTBEAT.md           # daily reminders
├── memory/
│   ├── memory-types.md    # this file (or link to SKILL.md)
│   ├── user/              # long-term user memories
│   ├── feedback/          # long-term feedback
│   ├── project/           # long-term project memories
│   ├── reference/         # long-term references
│   ├── palace/            # Memory Palace views
│   │   ├── timeline.md
│   │   ├── projects.md
│   │   ├── technology.md
│   │   └── custom.md
│   ├── dreaming/
│   │   ├── deep/          # Deep phase reports
│   │   ├── light/          # Light phase output
│   │   ├── rem/           # REM reflections
│   │   └── verify/        # Verification reports (v4.12)
│   └── YYYY-MM-DD.md     # working memory (daily logs)
└── knowledge/             # knowledge layer (detailed content)
```

---

## Example Interactions

**User provides important info:**
> User: "I'm a data analyst, mostly working with Python"
→ Working: log in today's daily log
→ Long-term: save to `memory/user/user-profile.md`, update MEMORY.md index

**User corrects you:**
> User: "Don't use Markdown tables, use lists"
→ Working: log in today's daily log
→ Long-term: save to `memory/feedback/no-tables.md`, update MEMORY.md index

**Project decision:**
> Decision: approach A over B because lower cost
→ Working: log decision context
→ Long-term: save to `memory/project/decision.md` with reasoning

**Looking up a past date:**
> User: "What did we do last Tuesday?"
→ Working memory: read `memory/YYYY-MM-DD.md` for that date

---

## References

- **Atkinson-Shiffrin model** (1968): Sensory → Short-term → Long-term memory stages
- Claude Code `memoryTypes.ts` — 4-type taxonomy
- Claude Code `extractMemories.ts` — auto-extraction system
- Claude Code `autoDream.ts` — background consolidation system
- OpenClaw `dreaming.md` — Dreaming experimental documentation

---

## OpenClaw Commands

```bash
# Check Active Memory status
openclaw plugins list | grep active-memory

# Check Memory Palace status
openclaw memory palace status

# Test Active Memory
openclaw memory test active

# Manually trigger Dream Consolidation
openclaw memory dream
```

---

## Changelog

| Version | Changes |
|---|---|
| v4.12 | Dual-Layer Dream Verification: Official Dream (12:30) + Refined Verify (13:00) cross-checking. Verification reports in memory/dreaming/verify/. Hallucination and drift prevention. |
| v4.11 | Full integration with OpenClaw 4.11 ecosystem, Active Memory + Memory Palace + Dream Consolidation |
| v3.2 | Memory sublimation system, 5-phase consolidation |
| v2.2 | Memory-Knowledge layering + Atkinson-Shiffrin integration |
| v1.0 | Initial release — Atkinson-Shiffrin three-stage model |

---

*Version: v4.12 | Updated: 2026-04-15 | Dual-Layer Dream Verification prevents hallucination and memory drift*
