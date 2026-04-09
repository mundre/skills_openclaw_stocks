# Round Output Contract
#tags: skills review

## Minimum Required Round Block
Always emit these fields.
- `ROUND`
- `TOPIC`
- `MODE`
- `SESSION`
- `DECISION`
- `PATCH_STATUS`
- `CONTINUATION_SIGNAL`
- `NEXT_ACTION`
- `CHAT_CONTINUITY`
- `RESUME_SNIPPET`

## Extended Round Block
Add these when useful.
- `SKILL_CLASS`
- `ORCHESTRATOR`
- `ORCHESTRATOR_MODE`
- `CONSULTANT_QUALITY`
- `COMPARISON`
- `DOC_STATUS`
- `TEST_STATUS`
- `VALIDATION_STATUS`
- `PUBLISH_STATUS`

## Emission rule
If uncertain, emit the minimum block correctly first.
Add extended fields only when they improve review accuracy, recovery, or gate decisions.

## Field meaning
- `ORCHESTRATOR_MODE`: `local`, `api`, or `multi`.
- `CONSULTANT_QUALITY: mixed`: at least one actionable finding is valid, but the response also contains vague, hallucinated, or partially misaligned points that must be filtered locally.
- Omit `CONSULTANT_QUALITY` in `local` mode unless a formal self-critique pass was actually run.
- `TEST_STATUS`: `missing` when no relevant test artifact exists yet; `planned` when a concrete test path is named; `updated` when the relevant test artifact was added or modified for the accepted patch; `verified` when the relevant tests or evals have been run successfully against the current artifact.
- `DRY_RUN`: whether mutation was authorized to proceed.
- `APPLY`: whether the real patch was applied.
- `PATCH_MANIFEST`: the concrete change record for the round when a patch exists, a fix remains pending, or a blocker must be logged.
- `CHAT_CONTINUITY`: whether the round used a new chat, reused the intended chat, or required recovery.
- `RESUME_SNIPPET`: a compact restart state containing enough information to resume after context loss. On recovery, use the snippet as ground truth for `MODE`, `SESSION`, and `NEXT_ACTION`.

## Resume snippet form
```text
RESUME_SNIPPET: |
  ROUND: <N>
  TOPIC: <slug>
  MODE: <mode>
  SESSION: <session>
  LAST_CONSULTANT: <skill-name or local>
  NEXT_ACTION: <one clear next step>
```

## Patch state rule
- If `PATCH_STATUS: none` and no patch blocker exists, `PATCH_MANIFEST` may be omitted.
- If `PATCH_STATUS` is `proposed`, `applied`, `re-reviewed`, or `deferred`, include `PATCH_MANIFEST`.
- If `APPLY: done`, `PATCH_MANIFEST` must describe the real patch.

## Patch manifest form
```text
PATCH_MANIFEST:
- target: <file or section>
  change: <one-line description>
  status: <proposed|applied|re-reviewed|rejected>
  version_bump: <none|patch|minor|major>
```
