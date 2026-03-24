---
name: dr-context-pipeline
description: "Deterministic memory/context pipeline for agents: route a user message, retrieve relevant memory snippets, compress into a cited Context Pack (sources are snippet IDs), lint, and fall back safely. Prerequisite: a file-based memory layout with memory/always_on.md + topic files (works out-of-the-box with dr-memory-foundation). Use when building or standardizing agent memory, reducing prompt bloat, implementing retrieval+compression, creating a context pack, designing a memory pipeline, adding lint gates, or setting up golden regression tests for agent context. After install, users can simply say: Apply dr-context-pipeline as default behavior." 
---

# DR Context Pipeline (retrieval + compression + lint)

Use this skill to standardize how an agent loads memory into its prompt **for correctness**.

## Prerequisites
- A file-based memory layout that includes `memory/always_on.md` (policy header + topic catalog) and topic files under `memory/topics/`.
- Recommended: install **dr-memory-foundation** (or implement an equivalent structure).

## Apply to this workspace
When the user asks to **apply** this skill (for example: `Apply dr-context-pipeline as default behavior`), do this:
1) Ensure the pipeline files/references are present.
2) Inspect `AGENTS.md`.
3) Patch `AGENTS.md` so the context pipeline becomes the default workflow.
4) Preserve existing content; patch surgically.
5) Confirm what changed.

This apply flow should be idempotent: do not duplicate sections if already applied.

## Operating procedure (default)
1) Load the always-on policy + topic catalog (your `memory/always_on.md`).
2) Route the message deterministically (task type + caps) using `references/router.yml`.
3) Retrieve top relevant snippets from your memory store; emit a **Retrieval Bundle JSON** (see schema).
4) Compress Retrieval Bundle → **Context Pack JSON** using `references/compressor_prompt.txt`.
   - **IMPORTANT:** Context Pack `sources` MUST be **snippet IDs only** (`S1`, `S2`, …).
5) Lint the Context Pack. If lint fails, **skip compression** and fall back to raw retrieved snippets.
6) Call the main reasoning model with: always-on policy header + Context Pack (+ raw snippets for high-stakes tasks) + user message.

## What to read / use
- Router + caps: `references/router.yml`
- Compressor prompt: `references/compressor_prompt.txt`
- Retrieval Bundle schema: `references/schemas/retrieval_bundle.schema.json`
- Context Pack schema: `references/schemas/context_pack.schema.json`
- Golden tests starter suite: `references/tests/golden.json`

## Notes
- Keep “always-on policy header” tiny (invariants only). Put everything else behind retrieval.
- If you need deterministic snippet IDs, follow the stable ordering guidance in `references/deterministic_ids.md`.
