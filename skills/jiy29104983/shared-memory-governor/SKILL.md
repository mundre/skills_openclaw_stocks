---
name: shared-memory-governor
description: Govern a file-based shared long-term memory layer for OpenClaw multi-agent and subagent systems. Preserve each agent's private long-term memory while adding shared memory for stable user preferences, global rules, and durable cross-agent facts. Use when designing, initializing, registering, attaching, maintaining, or auditing a shared-memory system with strict identity isolation.
---

# shared-memory-governor

Preserve each agent's private long-term memory system.

Add a separate shared long-term memory layer for durable user-level and cross-agent context.

Keep agent identity, persona, tone, and role strictly private.

## Language policy

Use English as the default storage language for shared-memory files, local attachment files, extraction markers, and shared-memory examples.

Chinese may be used for review drafts and discussion, but final skill storage examples should remain in English.

## Core model

Use a two-layer long-term memory model:

1. **Private long-term memory layer**
   - Keep each agent's own `MEMORY.md`
   - Keep each agent's own `Memory.db`
   - Keep each agent's own daily memory files

2. **Shared long-term memory layer**
   - Store shared files under the shared root directory
   - Use this layer for stable user preferences, global rules, and durable cross-agent facts
   - Treat this layer as part of the long-term memory system
   - Do not use this layer for agent identity

## Core principles

Follow these rules at all times:

1. Preserve private memory systems
2. Share the user and shared rules, not the assistant identity
3. Read private long-term memory first, then shared long-term memory
4. Treat shared long-term memory as part of the agent's long-term memory system
5. Use shared memory only as supplemental background
6. Never let shared memory override agent identity, persona, tone, role, or private `SOUL.md`
7. Do not auto-delete private entries after promotion to shared memory
8. Require explicit local attachment for participating agents
9. Keep `SOUL.md` private in v1

## V1 hard boundaries

Treat the following as hard boundaries in v1:

- `SOUL.md` always remains private
- Do not create or use `shared-soul.md`
- Do not extract shared content from `SOUL.md`
- Do not propagate agent names, persona, tone, role framing, or self-narrative through shared memory

If a future version introduces soul-related extraction, design it separately and restrict it to non-persona behavioral principles only.

## Shared memory structure

Use the shared root with this default structure:

```text
<sharedRoot>/
├── shared-user.md
├── shared-memory.md
├── shared-rules.md
├── shared-sync-log/
│   ├── YYYY-MM-DD_HHMM_scan.md
│   └── YYYY-MM-DD_HHMM_maintenance.md
└── archived/
    └── <agent>/
```

### File responsibilities

#### `shared-user.md`

Store only stable user preferences, habits, and constraints.

#### `shared-memory.md`

Store only durable facts about the world, project, or environment that are reusable across multiple agents.

#### `shared-rules.md`

Store only governance rules for the shared-memory system itself.

Typical contents include:
- read order
- attachment rules
- promotion rules
- naming rules
- subagent compatibility rules
- file responsibility rules
- schedule health-check rules

`shared-rules.md` must explicitly define and enforce the boundaries between:
- `shared-user.md`
- `shared-memory.md`
- `shared-rules.md`

For detailed allowed/disallowed examples for the three shared files, read:
- `references/promotion-rules.md`

#### `shared-sync-log/`

Store execution logs for shared scan and shared maintenance runs.

This is an operational log layer, not part of the shared-memory knowledge layer by default.

Do not treat `shared-sync-log/` as a normal shared long-term memory source unless a future version explicitly designs that behavior.

#### `archived/<agent>/`

Store archived attachment-related files for an agent after `detach`.

In v1, the default archived object is:
- `SHARED_ATTACH.md`

## Shareable and non-shareable content

### Allow promotion only for:

- stable user preferences
- global workflow rules
- global safety rules
- global delivery rules
- durable cross-agent facts
- stable shared-memory governance facts

### Never promote:

- agent name
- agent persona
- agent tone
- agent role
- agent-specific project context
- temporary task state
- debugging or process noise
- plaintext secrets
- anything from `SOUL.md` in v1

Future versions may refine these non-shareable boundaries further.

## Shared scope validation rule

Treat shared-scope validation as a separate hard gate during shared promotion.

Before promoting any candidate during `run-shared-scan`, read:
- `references/promotion-rules.md`

Use that reference as the detailed source for:
- single-agent default skip behavior
- promotion-basis values
- shared file boundaries
- promotion rationale template

## Long-term memory read rule

Shared long-term memory belongs to the agent's long-term memory system.

When an attached agent reads long-term memory, it should:

1. Read private long-term memory first
2. Read local `SHARED_ATTACH.md` to locate and interpret shared-memory rules
3. Then read shared long-term memory files as instructed by `SHARED_ATTACH.md`
4. Use shared long-term memory only as supplemental context

Short rule:

> Private first, shared second; shared supplements, never override persona.

## Private long-term memory maintenance

Maintain each participating agent's private long-term memory on its own schedule.

Recommended default:
- every 72 hours
- at 12:00

These values are recommended defaults, not mandatory requirements.

Use private maintenance to:
- review recent daily memory
- distill durable items into private `MEMORY.md`
- prune outdated or low-value private long-term memory

Do not write directly from raw daily memory into shared memory.

## Shared promotion pipeline

Use this chain:

```text
daily memory
→ private long-term memory
→ shared scan
→ shared memory layer
```

Shared promotion should come from distilled private long-term memory, not directly from raw daily memory, unless a future version explicitly designs otherwise.

Do not skip the private-memory distillation layer.

## Shared scheduling model

### Shared scan

Use shared scan to:
- read participating agents' private long-term memory
- identify promotable shared candidates according to configured source priority
- update shared files
- write a scan log
- emit an execution summary

Promotion eligibility must be conservative.

`sourcePriority` controls candidate discovery order only. It does not authorize promotion by itself.

A candidate found in only one agent's private long-term memory must be skipped by default unless at least one of the following is true:
- the user explicitly designated it as a shared/global rule or preference
- the item is corroborated by multiple participating agents' private long-term memory
- the item is clearly a shared-memory governance rule rather than an agent-local working habit

Do not treat a stable rule in one agent's private memory as automatically shareable just because it looks durable.

When evaluating a candidate, explicitly distinguish:
- user-global preferences and constraints
- global workflow, safety, and delivery rules
- durable cross-agent facts
- agent-local workflow habits, role-specific defaults, and project-specific context

Only the first three categories are promotable by default in v1.

Recommended schedule:
- every 6 days
- at 12:30

Recommended default enablement:
- disabled by default after `init`
- ask the user explicitly whether to enable this task
- warn that this task can consume significant tokens when many agents participate

### Shared maintenance

Use shared maintenance to:
- deduplicate shared entries
- merge similar entries when appropriate
- prune outdated shared content
- update shared rules when needed
- write a maintenance log
- emit an execution summary

Recommended schedule:
- every 12 days
- at 13:00

Recommended default enablement:
- disabled by default after `init`
- ask the user explicitly whether to enable this task
- warn that this task can consume significant tokens when many agents participate

These schedule values are recommended defaults, not mandatory requirements.

## Extraction marker rule

Do not auto-delete a private entry after promoting it into shared memory.

Keep the private original and append this marker:

```md
> Status: Extracted to shared memory (YYYY-MM-DD)
```

This marker means:
- the private entry has already been promoted
- the private entry remains in place
- future scans should skip re-promotion unless the entry has materially changed

## Status model

Use two state axes:

### Register status
- `registered`
- `unregistered`

### Attach status
- `attached`
- `detached`

`attachStatus` describes local shared-memory read-path readiness, not participation membership.

Treat the agent as `detached` whenever local attachment is incomplete.

Any of the following means `detached`:
- missing `SHARED_ATTACH.md`
- missing `AGENTS.md` injection
- inconsistent `SHARED_ATTACH.md` and `AGENTS.md` injection
- failed local attachment validation

## Membership commands

### `register <agent>`

Control participation membership.

Purpose:
- add the target agent to the shared-memory participant list
- include it in the potential scope of shared scan and shared maintenance

`register` does not automatically mean `attach`.

### `unregister <agent>`

Control participation membership.

Purpose:
- remove the target agent from the shared-memory participant list

If the agent is still `attached`, `unregister <agent>` must be blocked by default and should instruct the user to run `detach <agent>` first.

## Attachment commands

### `attach <agent>`

Control local shared-memory read-path injection.

If the target agent is not yet `registered`, `attach <agent>` must be blocked by default and should instruct the user to run `register <agent>` first.

After prerequisites are satisfied, the skill should automatically:

1. create or update the agent-local `SHARED_ATTACH.md`
2. inject shared-memory read rules into the agent-local `AGENTS.md` under the `Session Startup` section by default
3. create that agent's private long-term memory maintenance cron task
4. verify that the private maintenance cron exists and is enabled
5. verify that local attachment is complete
6. emit an attachment result report

**Important:** `attach` changes files on disk, but it does not retroactively change what a currently-running agent session has already loaded.

After attaching an agent, explicitly tell the user:
- If they want that agent to *definitely* load the new shared-memory location and rules, they should run a `/reset` (or start a new session) for that agent.
- Until reset, the agent may continue operating with the previous session context.

### `detach <agent>`

Control removal of local shared-memory read-path injection.

When running `detach <agent>`, the skill should automatically:

1. archive `SHARED_ATTACH.md` to `<sharedRoot>/archived/<agent>/`
2. remove or disable the shared-memory injection block inside `AGENTS.md`
3. verify that the agent no longer reads shared long-term memory
4. emit a detach result report

Default archive behavior in v1:
- archive only `SHARED_ATTACH.md`
- do not archive the entire `AGENTS.md`

Private long-term memory maintenance tasks are preserved during `detach`.

`detach` must not:
- delete private `MEMORY.md`
- delete private daily memory files
- delete or disable the agent's private maintenance cron by default

### Attachment success criteria

Before validating attach readiness, read:
- `references/injection-rules.md`

Treat local attachment as complete only when the injection and attachment state satisfy that reference.

## Entrypoint injection rule

Use the agent-local `AGENTS.md` as the default primary entrypoint whenever available.

Inject short, explicit shared-memory rules.

Before implementing, repairing, detaching, or auditing startup injection, read:
- `references/injection-rules.md`

That reference defines:
- startup-section detection priority
- fallback placement
- attachment success criteria
- detach cleanup behavior

### Recommended `AGENTS.md` injection

See:
- `references/injection-rules.md`

That reference contains:
- startup placement priority
- recommended startup wording
- merge rules for existing startup sections

## Local attachment file

Create a local file named:

```text
SHARED_ATTACH.md
```

Use it as the local attachment guide for that agent.

### Required contents of `SHARED_ATTACH.md`

Each attached agent's local `SHARED_ATTACH.md` must explicitly state:

- shared long-term memory is part of the agent's long-term memory system
- which shared files must be read
- in what order those shared files must be read

### Example policy

The final skill's `SHARED_ATTACH.md` example body should be fully English.

## `repair-attachment <agent>`

Use this command to repair one agent's local attachment readiness.

Before repairing one agent's local attachment readiness, read:
- `references/injection-rules.md`
- `references/status-audit-fields.md`

`repair-attachment <agent>` repairs one agent's local attachment readiness only. It does not repair global shared cron tasks.

## Subagent compatibility

Support subagents with restricted write behavior.

Default v1 behavior:
- allow subagents to read shared memory
- do not allow subagents to write shared master files directly
- route candidate shared content back to the maintainer or shared scan process for centralized handling

Keep writes to shared master files centralized.

## Initialization

### `init`

Initialize the shared-memory system structure.

At minimum, `init` should:

1. create the shared root directory
2. create base shared files:
   - `shared-user.md`
   - `shared-memory.md`
   - `shared-rules.md`
3. create the `shared-sync-log/` directory
4. create the default config file
5. create the shared scan cron task in a disabled state by default
6. create the shared maintenance cron task in a disabled state by default
7. explicitly remind the user that these two shared-layer tasks are disabled by default and ask whether to enable them
8. explicitly warn that shared scan and shared maintenance can consume significant tokens when many agents participate
9. verify that those shared cron tasks exist and that their enabled state matches the default disabled config unless the user explicitly chose otherwise
10. emit an initialization result report

`init` may create a missing config file, but the parent directory must be writable.

If the config file already exists, require confirmation before overwriting.

If the shared root already exists and already contains shared-memory files, require confirmation before overwrite or reinitialization. Do not overwrite silently.

`init` must support an explicit `--shared-root <path>` parameter.

If both `--config <path>` and `--shared-root <path>` are provided during `init`, the resulting initialized configuration and shared directory structure should use that provided `sharedRoot`.

The default initialized JSON config should therefore set:
- `schedules.sharedScan.enabled = false`
- `schedules.sharedMaintenance.enabled = false`

Do not silently enable these two shared-layer tasks during `init`.

## Shared scan

### `run-shared-scan`

Run one shared-memory scan.

At minimum, the skill should:

1. read participating agents' private long-term memory sources
2. identify promotable shared candidates according to configured source priority
3. validate that each promoted candidate has shared-scope justification
4. update shared files
5. write a scan log
6. emit an execution summary

Shared-scope justification is required for every promoted entry.

For each promoted item, the scan log must record at minimum:
- source agent or agents
- source file or files
- target shared file
- why the item is shared/user-global rather than agent-local

A single-agent private-memory item must be skipped by default unless the item has explicit shared-scope justification under the rules above.

This task is recommended to remain disabled by default after `init` until the user explicitly enables it.

When many agents participate, this task can consume significant tokens because it reads multiple agents' private long-term memory sources and produces an auditable scan log.

In addition to content scanning, run upstream schedule health checks:

1. check whether each participating agent's private maintenance cron exists
2. check whether each private maintenance cron is enabled
3. check whether each private maintenance cron is consistent with the current JSON config

## Shared maintenance

### `run-shared-maintenance`

Run one shared-memory maintenance cycle.

At minimum, the skill should:

1. deduplicate shared entries
2. merge similar entries when appropriate
3. prune outdated shared content
4. update shared rules when needed
5. write a maintenance log
6. emit an execution summary

This task is recommended to remain disabled by default after `init` until the user explicitly enables it.

When many agents participate, this task can consume significant tokens because effective shared maintenance requires re-reading and auditing the shared layer with full governance checks.

In addition to content maintenance, run shared-layer schedule health checks:

1. check whether the shared scan cron exists
2. check whether the shared scan cron is enabled
3. check whether the shared scan cron is consistent with the current JSON config
4. check whether the shared maintenance cron exists
5. check whether the shared maintenance cron is enabled
6. check whether the shared maintenance cron is consistent with the current JSON config

## Schedule health-check policy

Operational tasks in the shared-memory system must not only process content; they must also verify the health of upstream and same-layer scheduling.

Before reporting cron health or config consistency outcomes, read:
- `references/status-audit-fields.md`

Cron consistency checks must use the **current JSON config** as the full source of truth.

Every cron-related field present in the JSON config must be checked with no omissions.

## Status and auditing

### `show-status`

Display the current shared-memory system status.

Use a **list format**, not tables.

Before implementing or reporting `show-status`, read:
- `references/status-audit-fields.md`

### `audit-attachments`

Audit whether local attachment state is complete and consistent for each agent.

Before implementing or reporting `audit-attachments`, read:
- `references/injection-rules.md`
- `references/status-audit-fields.md`

## Reporting requirements

### Shared scan report

Before generating a shared scan report, read:
- `references/promotion-rules.md`
- `references/status-audit-fields.md`

Include the core scan summary in `SKILL.md` and use the detailed promotion template from `references/promotion-rules.md`.

Also include:
- which agents' private maintenance crons were checked
- which crons were missing
- which crons were disabled
- which crons were inconsistent with the current JSON config

### Shared maintenance report

Before generating a shared maintenance report, read:
- `references/status-audit-fields.md`

Include the core maintenance summary in `SKILL.md` and use the stable section order from `references/status-audit-fields.md` when possible.

Also include:
- shared scan cron health-check results
- shared maintenance cron health-check results
- the list of missing, disabled, or JSON-config-inconsistent tasks

## Config path policy

Support explicit config-path arguments for config-related commands.

If no config path is explicitly provided, use the default:

```text
/root/.openclaw/shared-memory/shared-memory.config.json
```

Non-config commands in v1 do not take `--config`.

If the config location changes, reinitialize with `init` or apply the change with `update-config`.

## Config model

Use a JSON-driven configuration model.

Recommended top-level blocks:
- `version`
- `maintainer`
- `paths`
- `schedules`
- `participants`
- `attachment`
- `sharing`
- `readOrder`
- `sourcePriority`
- `extraction`
- `maintenance`
- `reporting`
- `syncLog`
- `language`

Document the meaning of every config item in a reference document for lookup, auditing, and maintenance.

## `sourcePriority`

Use `sourcePriority` to define the upstream source order for shared promotion.

Recommended v1 setting:

```json
"sourcePriority": [
  "MEMORY.md",
  "USER.md"
]
```

Meaning:
1. prioritize durable shared candidates from `MEMORY.md`
2. then use `USER.md` for stable user preferences and user-level constraints

Do not treat raw daily memory as a normal promotion source in v1.

## `allowDailyMemoryFallback`

`allowDailyMemoryFallback` controls whether shared scan may fall back to raw daily memory when preferred extraction sources are insufficient.

Recommended v1 setting:

```json
"allowDailyMemoryFallback": false
```

## Maintenance semantics

The `maintenance` block defines what the shared maintenance process is allowed to do.

Typical meanings:
- `deduplicateSharedMemory`: allow deduplication in shared memory
- `mergeSimilarEntries`: allow merging similar shared entries
- `pruneOutdatedSharedEntries`: allow pruning outdated shared entries
- `markPrivateExtractedEntries`: allow appending extraction markers to private source entries
- `modifyPrivateMemoryDirectly`: allow direct rewrite of private long-term memory body content

In v1:

```json
"modifyPrivateMemoryDirectly": false
```

means:
- do not rewrite, restructure, or delete private body content

```json
"markPrivateExtractedEntries": true
```

means:
- allow only minimal appended extraction markers

## `update-config`

In v1:

```text
update-config = validate + apply config
```

Config command relationship in v1:
- `init` creates the default JSON config and default shared-layer cron state
- `show-config` displays the current JSON source of truth
- `update-config` validates and applies edited JSON

If cron tasks are inconsistent with the new config, report `exact-match`, `equivalent-match`, or `mismatch`.

`update-config` does not automatically rewrite all cron jobs in v1 unless a future version explicitly adds that behavior.

## Supported commands

V1 supports:

- `init`
- `show-config`
- `validate-config`
- `update-config`
- `register <agent>`
- `unregister <agent>`
- `attach <agent>`
- `detach <agent>`
- `repair-attachment <agent>`
- `run-shared-scan`
- `run-shared-maintenance`
- `show-status`
- `audit-attachments`
- `show-sync-logs`
- `prune-sync-logs`

Config-related commands support explicit config path arguments.

`show-sync-logs` and `prune-sync-logs` target only the shared-layer log directory and do not operate on agent-private maintenance logs.

## Final operating stance

Keep this skill:

- low-intrusion
- explicit
- auditable
- configuration-driven
- strict about identity isolation
- conservative about write authority
- centered on governance rather than hidden magic
