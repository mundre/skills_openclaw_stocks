# Apply checklist — dr-context-pipeline

Use this when the user says things like:
- Apply dr-context-pipeline as default behavior
- Enable the context pipeline
- Make this the default context-loading workflow

## Goal
Make the retrieval + compression pipeline the default behavior for the workspace.

## Steps
1) Ensure these exist:
- `memory/always_on.md`
- `references/router.yml`
- `references/compressor_prompt.txt`
- `references/schemas/*.json`
- `references/tests/golden.json`

2) Inspect `AGENTS.md`.

3) Add/update a **Default behavior: Context Pipeline** section that instructs the agent to:
- load `memory/always_on.md`
- route via the router
- retrieve snippets into a Retrieval Bundle
- compress into a Context Pack
- lint + fall back if needed

4) Preserve existing `AGENTS.md` content; patch surgically.

5) Confirm what changed.

## Idempotency rule
If already applied, update in place without duplicating sections.
