# Cold Memory Schema Reference

Read this file when creating or modifying notes, index entries, tags.json structure, or retrieval-log format.

## Note template

Use this as `memory/cold/_template.md`:

```markdown
# [Topic title]

## TL;DR
- What this note is
- When it matters
- Key conclusion or takeaway

## Why this matters
1–3 lines explaining the value of preserving this knowledge.

## Memory type
- fact | experience | background

## Semantic context
A 1–2 sentence natural language description of what this note is about and when it
would be useful. Write this as if answering: "If someone were working on ___, this
note would help because ___." This field enables fuzzy matching when exact keyword
triggers miss.

## Triggers
- word or phrase that should make this note worth checking
- another trigger phrase

## Use this when
- scenario where this note materially helps
- another scenario

## Key facts
- stable fact 1
- stable fact 2

## Decisions / lessons
- DO: recommended action and why
- AVOID: anti-pattern and why

## Confidence
- high | medium | low

## Last verified
- YYYY-MM-DD

## Related tags
- tag1
- tag2

## Details
Longer context, history, or explanation if needed.
Keep this section optional — omit it for fact-type notes.

## Source context
- file, conversation, date, or origin note
```

### Field definitions

| Field | Required | Purpose |
|---|---|---|
| Topic title | yes | Clear, searchable title |
| TL;DR | yes | 2–4 bullet summary for cheap retrieval |
| Why this matters | no | Brief justification; useful for background notes |
| Memory type | yes | One of: fact, experience, background |
| Semantic context | yes | 1–2 sentence natural language description for fuzzy matching when triggers miss |
| Triggers | yes | Keywords/phrases that should surface this note during recall |
| Use this when | yes | Concrete scenarios where the note helps |
| Key facts | if applicable | Stable, reusable facts |
| Decisions / lessons | if applicable | DO/AVOID pairs with rationale |
| Confidence | yes | high = reliable; medium = use with caveat; low = needs re-verification |
| Last verified | yes | Date of last accuracy check |
| Related tags | yes | Tags matching tags.json for cross-referencing |
| Details | no | Extended context; keep only if genuinely needed |
| Source context | no | Origin trail for future verification |

### Writing guidelines

- Put the shortest useful summary at the top (TL;DR).
- Write for retrieval, not narrative beauty.
- Preserve lessons and rationale, not raw transcript noise.
- One note per topic. Merge when topics overlap.
- Update existing notes instead of creating near-duplicates.
- Write Semantic context as natural prose, not a keyword list — its purpose is to catch queries that exact triggers would miss.

## index.md format

Use a single consistent Markdown list with one block per note.

```markdown
# Cold Memory Index

- `note-file.md` — one-line summary
  - type: fact | experience | background
  - tags: comma-separated tags
  - triggers: words or phrases that should prompt recall
  - read when: scenarios where this note materially helps
  - confidence: high | medium | low
  - updated: YYYY-MM-DD
```

Guidelines:
- Keep entries sorted by most-recently-updated first.
- Use one block per note.
- If the archive gets large, add simple section headings like `## Experience`, `## Fact`, `## Background`, but keep the same per-note block shape.

## tags.json format

Use an object with metadata plus a `notes` array.

```json
{
  "_meta": {
    "description": "Structured metadata for cold-memory retrieval",
    "version": 3,
    "updated": "YYYY-MM-DD"
  },
  "notes": [
    {
      "title": "string — note title",
      "path": "string — relative path, e.g. memory/cold/postgres-migration.md",
      "type": "string — fact | experience | background",
      "summary": "string — one-sentence summary",
      "semantic_context": "string — 1-2 sentence natural language description for fuzzy matching",
      "tags": ["string array — searchable tags"],
      "triggers": ["string array — recall trigger phrases"],
      "scenarios": ["string array — when-to-use descriptions"],
      "confidence": "string — high | medium | low",
      "last_verified": "string — YYYY-MM-DD",
      "updated": "string — YYYY-MM-DD"
    }
  ]
}
```

### Keeping index.md and tags.json in sync

Every archive or update operation must update both files. If they drift out of sync:

1. Treat the note files as the source of truth.
2. Rebuild `index.md` and `tags.json` from the note files.
3. Verify all paths in `tags.json` point to existing files.
4. Keep `_meta.updated` current after rebuilds.

## retrieval-log.md format

`memory/cold/retrieval-log.md` tracks which notes were recalled and whether they helped.

```markdown
# Retrieval Log

| Date | Query | Matched | Useful | Action |
|---|---|---|---|---|
| 2025-03-20 | postgres migration rollback | postgres-migration.md | yes | — |
| 2025-03-22 | rate limit batch job | api-rate-limits.md | yes | updated Key facts |
| 2025-04-01 | redis cache eviction | (no match) | n/a | created new note |
```

Guidelines:
- Log only cold memory retrievals, not warm or `MEMORY.md` lookups.
- `Useful` = the recalled note materially improved the answer.
- `Action` = any update made to the note, index, or tags after retrieval.
- Review the log during maintenance to identify stale, missing, or weak notes.