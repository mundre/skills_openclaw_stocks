# Status and Audit Fields

## Quick map

- Purpose
- Standard per-agent fields
- `show-status` minimum global fields
- `audit-attachments` checks
- Cron consistency outcomes
- Shared maintenance report section order

## Purpose

Use this reference when implementing or reporting `show-status`, `audit-attachments`, shared scan health checks, and shared maintenance health checks.

## Standard per-agent fields

Report these fields consistently when possible:
- `registerStatus`
- `attachStatus`
- `startupInjectionStatus`
- `sharedAttachFileStatus`
- `privateMaintenanceCronStatus`
- `configConsistencyStatus`
- `privateMaintenanceLastRun`
- `privateMaintenanceNextRun`

Use explicit null-style wording such as `none` or `unknown` when a field cannot be resolved.

## `show-status` minimum global fields

- Shared root
- Active config path
- Last shared scan
- Next shared scan
- Last shared maintenance
- Next shared maintenance
- Shared scan cron status
- Shared maintenance cron status

## `audit-attachments` checks

For each agent, check at minimum:
- whether the agent is registered
- whether `SHARED_ATTACH.md` exists
- whether `AGENTS.md` contains startup injection in the correct priority position
- whether a stale old injection block still exists elsewhere in `AGENTS.md`
- whether `SHARED_ATTACH.md` and the startup injection are consistent
- whether the private maintenance cron exists and is consistent with the current JSON config

## Cron consistency outcomes

When comparing task definitions against the JSON config, report one of:
- `exact-match`
- `equivalent-match`
- `mismatch`

Example:
- JSON config: `every: 72h`, `time: 12:00`
- cron job: `0 12 */3 * *`

This should be treated as `equivalent-match`, not `mismatch`, when the effective execution intent is the same.

## Shared maintenance report section order

Use this stable section order when possible:
1. Header
2. Inputs
3. Maintained Files
4. Duplicates Removed
5. Merges
6. Pruned Entries
7. Conflicts / Human Confirmation
8. Schedule Health Check
9. Final Result
10. Follow-up Recommendation
