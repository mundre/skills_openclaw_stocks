# Roadmap Management — Reference Guide

Building and maintaining roadmaps, milestones, sequencing, and progress tracking.
The system for seeing where we're going and whether we're on track.

---

## 1. THE ROADMAP PHILOSOPHY

A roadmap is NOT a schedule. A schedule says "this happens on this date."
A roadmap says "this is the sequence of what we're building and why."

The roadmap answers: what are we building, in what order, and what are the key milestones?
It doesn't answer: exactly when each task will be done.

---

## 2. THE TLC ROADMAP STRUCTURE

### Product Roadmap
```
NOW (This Quarter):
  - [Initiative] — Status: [In progress] — Expected: [Date or Sprint]
  - [Initiative] — Status: [In progress] — Expected: [Date or Sprint]

NEXT (Next Quarter):
  - [Initiative] — Priority: [H/M/L] — Blocked by: [Dependency if any]
  - [Initiative] — Priority: [H/M/L]

LATER (6+ Months):
  - [Initiative] — Condition: [What must happen first]
  - [Initiative] — Condition: [What must happen first]

BACKLOG (No Current Timeline):
  - [Initiative] — Why parked: [Reason]
```

### Milestone Format
```
MILESTONE: [Name]
Description: [What this means when achieved — 1 sentence]
Target date: [Month or quarter — not day-specific]
Key deliverable: [Specific output that proves this milestone is hit]
Dependencies: [What must happen first]
Owner: [Agent or Joshua]
Status: [Not started / In progress / Complete]
```

---

## 3. SEQUENCING PRINCIPLES

### How to Sequence Work
```
RULE 1: Revenue comes first
  Work that generates revenue sequences ahead of work that doesn't

RULE 2: Dependencies first
  If B can't happen until A is done: A sequences first

RULE 3: Foundation before features
  Core functionality before nice-to-have additions

RULE 4: Validated assumptions first
  Risky assumptions → test fast → sequence other work after validation
  Don't build a 3-month product on an assumption that can be tested in 1 week

RULE 5: Learning loops close fast
  If you don't know if something will work: launch it fast, learn fast, adjust
  Don't build a year-long roadmap on something you haven't validated
```

### The Critical Path
```
For any multi-step initiative, identify the critical path:
  The sequence of dependencies that determines the minimum time to complete

EXAMPLE: New Product Launch
  Step 1: Build product PDF (5 days)
  Step 2: Write product description (1 day) — depends on Step 1
  Step 3: Create cover image (1 day) — can happen in parallel with Step 2
  Step 4: Upload to Gumroad + QA (1 day) — depends on Steps 2 and 3
  Step 5: Email announcement (1 day) — depends on Step 4
  
  Critical path: 1 → 2 → 4 → 5 = 8 days minimum
  Step 3 can run in parallel with Step 2, so it doesn't add time.
```

---

## 4. PROGRESS TRACKING

### The Weekly Progress Check
```
For each active initiative, answer three questions:
  1. What was supposed to happen this week?
  2. What actually happened?
  3. What changes for next week based on what happened?

STATUS INDICATORS:
  ✅ On track: Progressing as planned
  ⚠️ At risk: Behind but recoverable with focused effort
  🔴 Off track: Significant delay, needs intervention
  ⏸️ Paused: Deliberately paused, will resume at [date/condition]
  ✓ Complete: Done
```

### TLC Product Roadmap (Current)
```
ACTIVE:
  GND Outreach Campaign — In progress — Goal: 5 clients by Q2 end
  Gumroad Catalog — 9 products active — Goal: All optimized by April

NEXT:
  Etsy expansion (if validated by Scout) — H priority
  Prayful beta development — M priority (after GND stable)

LATER:
  MyFirstJob development — After GND revenue stable
  Product catalog expansion (new titles) — Continuous quarterly

BACKLOG:
  Course creation (any topic) — Parked: Too expensive vs. PDF format
```

---

## 5. ROADMAP ANTI-PATTERNS

### Common Roadmap Failures

**The Wish List Roadmap**: Everything is on the roadmap with no priority.
Fix: Maximum 3 items in "NOW." Everything else is sequenced or backlogged.

**The Waterfall Trap**: Planning all details of future work before validating current work.
Fix: Define only current quarter in detail. Next quarter is directional.

**The Roadmap That Never Gets Reviewed**: Built once, ignored after.
Fix: Review and update roadmap during monthly review.

**The Feature Factory**: Adding features/products without measuring what's working.
Fix: Every new initiative requires a success metric defined before starting.
