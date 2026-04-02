---
name: hui-yi
description: >
  Manage a file-based cold-memory archive under memory/cold/. Use this skill when:
  (1) cooling recent daily notes into long-term archival storage,
  (2) recalling historical context that would materially improve the current answer,
  (3) maintaining, merging, or pruning the cold-memory index.
  Trigger on phrases like "do you remember", "how did we handle that", "archive this",
  "cool this down", or any task where low-frequency historical context would noticeably
  improve correctness or continuity. Do NOT use for fresh daily notes (→ memory/YYYY-MM-DD.md),
  high-frequency user profile facts (→ MEMORY.md), tool/environment setup (→ TOOLS.md),
  or recent lessons still being validated (→ .learnings/).
---

# Hui Yi — Cold Memory System

Archive low-frequency, high-value knowledge. Recall it only when it materially helps.

**Guiding principle:** archive less, but archive better.

## Memory layers

This skill operates on the **cold** layer. Know all three:

- **Active** — current chat, current task, immediate working notes. Keep minimal.
- **Warm** — recent daily files (`memory/YYYY-MM-DD.md`), active project notes, near-term context. Check this first for anything recent or ongoing. (High-frequency project context that persists across weeks belongs in `MEMORY.md`, not here.)
- **Cold** — older but still valuable knowledge (`memory/cold/`). Stable facts, reusable lessons, historical decisions, durable background. This is what Hui Yi manages.

## Storage layout

```text
memory/
├── cold/
│   ├── index.md             # human-readable index (primary retrieval surface)
│   ├── tags.json            # structured metadata for targeted lookup
│   ├── retrieval-log.md     # tracks recall events for quality feedback
│   ├── _template.md         # starter note template
│   ├── <topic-slug>.md      # one note per topic (default namespace)
│   └── <project>/           # optional: project-specific namespace
│       └── <topic-slug>.md
├── heartbeat-state.json     # maintenance timestamps and cold-memory stats
scripts/
├── search.py                # keyword search across index and tags
├── rebuild.py               # regenerate index.md + tags.json from notes
├── decay.py                 # auto-decay confidence by last_verified age
└── cool.py                  # scan pending daily notes + update heartbeat
```

### Multi-project namespaces (optional)

For users with multiple distinct projects, notes can be organized into subdirectories under `memory/cold/<project>/`. The global `index.md` and `tags.json` aggregate all namespaces. Helper scripts automatically scan subdirectories.

Use namespaces only when project isolation genuinely helps retrieval. Default: keep all notes flat in `memory/cold/`.

## Cross-platform helper scripts

Use the Python helpers when you want to automate mechanical file operations. They are intended to run on Linux, macOS, and Windows with a normal `python` installation.

| Script | Purpose | Usage |
|---|---|---|
| `scripts/search.py <keyword>` | Search index + tags by keyword | Retrieval when manual scan is insufficient |
| `scripts/rebuild.py` | Regenerate index.md + tags.json from note files | Use after manual edits or when index drifts |
| `scripts/decay.py [--dry-run]` | Auto-decay confidence by last_verified age | Run during monthly maintenance; preview with `--dry-run` |
| `scripts/cool.py scan` | List daily notes pending cooling | Run at start of each cooling pass |
| `scripts/cool.py done <reviewed> <archived> <merged>` | Update heartbeat cold-memory stats | Run after completing a cooling pass |
| `scripts/cool.py status` | Show current cold-memory heartbeat state | Quick check anytime |

If the helper scripts are unavailable, follow the same workflow manually. The skill must still work without automation.

## First-time setup

If `memory/cold/` does not exist, bootstrap it:

1. Create `memory/cold/` directory.
2. Create an `index.md` that matches the flat format in `references/cold-memory-schema.md`.
3. Create a `tags.json` that matches the schema in `references/cold-memory-schema.md`.
4. Create `memory/cold/retrieval-log.md` with the retrieval log header shown in the schema reference.
5. Extract the note template from `references/cold-memory-schema.md` and save it as `memory/cold/_template.md`. Do not copy the whole reference file.
6. If `memory/heartbeat-state.json` does not exist, create it with an object that includes a top-level `coldMemory` section.

## When to archive

Archive ONLY if at least one condition is true:

- The content will likely still matter after 30 days.
- It contains a reusable lesson or workflow.
- It would noticeably improve a future answer or decision.
- The user explicitly asks to preserve it.

IF none apply → do not archive.

### Boundary check before archiving

Before writing to `memory/cold/`, confirm the content does not belong elsewhere:

| Content type | Correct destination |
|---|---|
| Today's task notes, status updates | `memory/YYYY-MM-DD.md` |
| High-frequency personal/project context | `MEMORY.md` |
| Machine paths, tool setup, device quirks | `TOOLS.md` |
| Fresh mistakes, corrections, raw lessons | `.learnings/` |
| Workflow rules, agent behavior specs | `AGENTS.md` / `SOUL.md` |
| Secrets, tokens, API keys, passwords | **never store anywhere in cold memory** |

Only after ruling out the above → archive into `memory/cold/`.

## Memory types

Classify each note before writing:

- **fact** — short, stable, directly reusable (a path, URL, naming convention, standing preference)
- **experience** — lessons from doing something (troubleshooting result, decision rationale, workflow that worked). Often the most valuable type.
- **background** — larger context for future synthesis (project history, research summary, long-term context for a system or person)

## Note structure

Keep notes layered so recall is cheap — put the shortest useful summary at the top.

→ `references/cold-memory-schema.md` — full template with field definitions and file formats
→ `references/examples.md` — complete examples for all three types, including matching index and tags.json entries

## Recall workflow

At each step, stop if found; otherwise continue to the next.

```text
1. Current conversation has the answer?       → done.
2. Topic recent? → check warm memory.         → done / continue.
3. Check MEMORY.md.                           → done / continue.
4. Tools/env? → TOOLS.md. Lesson? → .learnings/. → done / continue.
5. Would cold archival context materially help?
   NO  → answer directly.
   YES → cold memory retrieval ↓
```

### Cold memory retrieval

`index.md` is the **primary retrieval surface**. `tags.json` is **secondary**.

1. Scan `index.md` for matching entries by topic, tags, or triggers.
2. Match found → open the note, done.
3. No match and the archive is large enough to justify automation → use `python scripts/search.py <keyword>` if available.
4. Open only the most relevant note(s) — prefer 1, cap at 3.
5. Read TL;DR and Decisions / lessons first. Load Details only if needed.
6. Synthesize for the current task. Do not dump raw notes.
7. If the note was stale or poorly structured, update it after answering.
8. Log the retrieval in `memory/cold/retrieval-log.md`.

### Confidence-based retrieval

- **high** — use directly as reliable context.
- **medium** — use with a caveat that it is older or not recently re-verified.
- **low** — mention only if no better source exists; suggest re-verification.

## Archiving (cooling)

Start with `python scripts/cool.py scan` if the helper exists. Then: strip noise, route each item to the correct file using the boundary table above, archive cold-worthy content by merging into existing notes or creating new ones, and keep `index.md` plus `tags.json` in sync. Finish with `python scripts/cool.py done <reviewed> <archived> <merged>` if using automation.

**Frequency:** weekly, or when 5+ daily notes have accumulated since the last pass.

→ `references/heartbeat-cooling-playbook.md` — full 4-pass cooling workflow

## Maintenance and pruning

Periodically (monthly or when index exceeds 30 entries):

1. Preview confidence decay with `python scripts/decay.py --dry-run` if the helper exists.
2. Merge overlapping notes, remove stale entries, strengthen triggers/tags.
3. Review `retrieval-log.md`: notes never recalled → removal candidate; unmatched queries → new note or better triggers; recalled but unhelpful → rewrite candidate.
4. Rebuild or resync index metadata with `python scripts/rebuild.py` only if the helper exists and the archive format matches the current schema.

Favor a smaller, sharper archive over a large fuzzy one.

## Error handling

- IF `memory/cold/` does not exist → run first-time setup.
- IF `index.md` missing or malformed → rebuild it manually or with `python scripts/rebuild.py`.
- IF `tags.json` missing or malformed → rebuild it manually or with `python scripts/rebuild.py`.
- IF `heartbeat-state.json` missing → create it with a top-level `coldMemory` object, not a conflicting standalone schema.
- IF indexed note file does not exist → remove the dangling entry and update the index / tags.
- IF `retrieval-log.md` missing → recreate it with the standard header row.
- IF unsure where content belongs → ask the user.

## Output behavior

1. Answer the current question first.
2. Mention recalled context only if it adds value — summarize, do not paste.
3. Show raw archive contents only if the user explicitly asks.

## References

Read **only when performing the specified action**:

| File | Read when |
|---|---|
| `references/cold-memory-schema.md` | Creating or modifying note/index/tags structure |
| `references/examples.md` | Need a concrete example of any note type or index/tags format |
| `references/heartbeat-cooling-playbook.md` | Executing a scheduled cooling or maintenance pass |

Helper scripts are optional. Prefer the Python versions listed above when automation is useful and available.