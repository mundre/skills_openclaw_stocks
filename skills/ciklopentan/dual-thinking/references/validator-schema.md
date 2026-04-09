# Validator Schema
#tags: skills review

Use this minimal contract when checking whether a round block is structurally valid.

## Minimum required block fields
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

Note: this is the minimal structural floor only. Full round validation must also satisfy the shared field set in `references/round-output-contract.md`.

## Manual validation checklist
- the round block includes every minimum required field
- the `MODE` matches the routed task type
- the `SESSION` is stable for the current topic
- if `PATCH_STATUS` is `proposed`, `applied`, `re-reviewed`, or `deferred`, a `PATCH_MANIFEST` exists
- if `PATCH_STATUS` is `none` and no patch blocker exists, `PATCH_MANIFEST` may be omitted
- if `CONTINUATION_SIGNAL` is `stop`, no accepted but unpatched fix remains
- if `VALIDATION_STATUS: failed`, packaging and publishing stay blocked

## Pass rule
Validation passes only if every line above is true.
