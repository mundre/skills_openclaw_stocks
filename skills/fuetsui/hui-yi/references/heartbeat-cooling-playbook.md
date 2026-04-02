# Heartbeat Cooling Playbook

Read this file when executing a scheduled cooling pass or heartbeat maintenance.

## When to run cooling

- **Default cadence:** once per week, or when 5+ daily notes have accumulated since the last pass.
- **Check:** read `memory/heartbeat-state.json` and inspect the `coldMemory` section for the last scan / archive timestamps.
- **Ad hoc:** the user explicitly asks to archive, cool, or clean up notes.

## Pre-flight

1. Run `python scripts/cool.py scan` if the helper is available.
2. The helper uses `coldMemory.lastArchive` to show only daily notes newer than the last archive pass.
3. If no helper is available, manually inspect recent `memory/YYYY-MM-DD.md` files.
4. If no new daily notes exist, stop.

## Step-by-step cooling process

### Pass 1 — Scan and triage

For each daily note since the last cooling:

1. Read the note.
2. For each piece of content, ask: is this low-frequency and high-value?
   - NO → skip (one-off status, transient chatter, speculative notes)
   - YES → proceed to routing ↓

### Pass 2 — Route to the correct destination

For each high-value item, determine where it belongs:

| If the content is… | Route to |
|---|---|
| A high-frequency personal/project fact | `MEMORY.md` |
| A machine path, tool quirk, device name | `TOOLS.md` |
| A fresh mistake or correction still being validated | `.learnings/` |
| A workflow rule or agent behavior spec | `AGENTS.md` / `SOUL.md` |
| Low-frequency archival knowledge that stays useful | `memory/cold/` ← proceed to Pass 3 |

Write routed content to the correct file immediately. Do not batch.

### Pass 3 — Archive into cold memory

For each item routed to cold memory:

1. **Check for existing notes.** Search `memory/cold/index.md` for a note on the same topic.
   - EXISTS → open the note, merge the new content in. Update TL;DR, Decisions / lessons, Last verified, and Confidence as needed.
   - DOES NOT EXIST → create a new note from `memory/cold/_template.md`.

2. **Write the note.** Follow the note structure from `references/cold-memory-schema.md`.
   - Strip noise: remove one-off context, transient references, conversation fragments.
   - Compress: the cold note should be shorter and more reusable than the original.
   - Preserve: lessons, rationale, stable facts, and decision context.

3. **Update index.md.** Add or update the entry. Keep entries sorted by most-recently-updated first.

4. **Update tags.json.** Add or update the corresponding object. Ensure path, tags, triggers, scenarios, and confidence are current.

### Pass 4 — Light maintenance (optional)

If you have time or the index is getting large:

- Scan for duplicate or overlapping notes → merge them.
- Check for stale entries (last_verified > 90 days) → flag for review or lower confidence.
- Remove dangling index entries where the note file no longer exists.
- Tighten summaries and triggers based on actual retrieval patterns.
- Review `memory/cold/retrieval-log.md`:
  - Notes never recalled → candidate for removal or better triggers.
  - Queries with no match → candidate for a new note.
  - Notes recalled but marked unhelpful → candidate for rewrite.

## Post-cooling

1. If using automation, run `python scripts/cool.py done <notes_reviewed> <notes_archived> <notes_merged>`.
2. Update the `coldMemory` section of `memory/heartbeat-state.json` with latest timestamps and a short summary.
3. For monthly maintenance, optionally run `python scripts/decay.py --dry-run` first, then `python scripts/decay.py`, then `python scripts/rebuild.py`.
4. Do NOT announce cooling results to the user unless asked.

## What NOT to do during cooling

- Do not read the entire cold archive. Only open notes you are actively merging into.
- Do not surface old notes to the user without a clear trigger.
- Do not archive content that fails the 30-day test.
- Do not create near-duplicate notes. Always check index first.
- Do not store secrets, tokens, or auth material.