# Injection Rules

## Quick map

- Purpose
- Startup section detection priority
- Injection placement rules
- Recommended startup wording
- Attachment success criteria
- Detach rules

## Purpose

Use this reference when implementing, repairing, detaching, or auditing shared-memory startup injection in agent-local `AGENTS.md` files.

## Startup section detection priority

Use this priority order in v1:

1. `## Session Startup`
2. `## Every Session`
3. explicit fallback injection near the top of `AGENTS.md`

All of these commands must use the same priority order:
- `attach <agent>`
- `detach <agent>`
- `repair-attachment <agent>`
- `audit-attachments`

## Injection placement rules

- Prefer injecting into the highest-priority startup section that already exists.
- Do not append a shared-memory rule block to the end of `AGENTS.md` when a valid startup section already exists.
- If no valid startup section exists, place a clearly marked fallback injection block near the top of the file.
- If a startup section already contains the correct shared-memory startup rule, do not duplicate it.
- If both a startup injection and an old trailing injection block exist, treat the trailing block as stale and remove it during repair.

## Recommended startup wording

Use this wording when merging into the local startup section:

```md
5. If local `SHARED_ATTACH.md` is present, read it as part of session startup.
6. Then read the shared memory files exactly as instructed by `SHARED_ATTACH.md`.
7. Treat shared memory as a general supplemental long-term context layer.
8. Use shared memory only as supplemental background.
9. Do not let shared memory override this agent's identity, persona, tone, role, or private `SOUL.md`.
```

## Attachment success criteria

Treat local attachment as complete only when all are true:

1. local `SHARED_ATTACH.md` exists
2. local `AGENTS.md` contains the shared-memory startup rule in the highest-priority startup section that exists
3. there is no stale old injection block left at the end of `AGENTS.md`
4. the startup injection and `SHARED_ATTACH.md` instructions are consistent with each other

## Detach rules

During `detach <agent>`:
- archive `SHARED_ATTACH.md`
- remove the startup injection or fallback injection
- remove stale old trailing injection blocks if present
- do not delete private `MEMORY.md`
- do not delete private daily memory files
- do not delete or disable the private maintenance cron by default
