---
name: agent-compute-mesh
description: Stage external compute for agents through local, hosted, and optional community-worker execution leases. Start with public-data tasks, isolated worker sandboxes, and credits-first settlement, then grow into a broader compute mesh only after the product proves real demand.
---

# Agent Compute Mesh

Use this skill when the local agent needs outside compute, outside tool coverage, or outside attention for a bounded task, and the task can be sliced without exposing the whole thread.

Technical invocation name: `$agent-compute-mesh`.

This skill is for the case where a local agent wants to send part of its workload to outside compute. The realistic path is not chain-first and not token-first. The realistic path is to make controlled public-data jobs work first, then expand toward hosted workers and finally community workers.

## Experimental Status

- This is a `vibecoding` concept built through a few prompt iterations, document shaping, and light tests.
- It does not have verified security, and it does not have verified reliability.
- The protocol, token model, scheduling, execution isolation, and settlement logic here are still design drafts.
- Before any real use, it needs independent security review, adversarial testing, fault injection, economic simulation, and long-run validation.
- If someone uses this design directly and it breaks, that is their own responsibility.

## Rollout Path

Treat this as a staged product, not a finished decentralized network.

1. `stage-1 local`: keep execution on the local machine and validate task shape, evidence quality, and user value.
2. `stage-2 hosted`: move approved public-data jobs to a central hosted worker service and bill with credits.
3. `stage-3 community-workers`: open the worker pool to third parties after hosted traffic proves pricing, fraud rate, and worker utilization.
4. `stage-4 optional-chain`: add on-chain settlement only if cross-operator trust and cross-jurisdiction payments become the bottleneck.

Read `references/rollout-plan.md` before designing a deployment path.

## Stage-1 Build Slice

The first build slice should stay local and prove the core contract before any hosted worker exists.

1. `job_spec`: capture the problem, host family, version band, evidence requirement, privacy tier, facet plan, and acceptance rules.
2. `lease_runner`: open a fresh local worker thread and isolated worktree for each lease.
3. `result_bundle + sandbox_receipt`: return a result plus an auditable execution receipt.
4. `local_accept_gate`: block every remote-style output until local review passes.
5. `metrics_logger`: track cost, evidence quality, reuse, mismatch, and review time.
6. `agent-travel-search adapter`: compile heartbreak and idle-search work into the same `exploration job` contract.

## Roles

1. `publish`: split a task, redact it, lock reward, and assign bounded work to remote nodes.
2. `solve`: accept one bounded work facet and return a signed result bundle.
3. `validate`: verify evidence quality, replay receipts, and sign attestation.
4. `relay`: help headers, receipts, and packet objects stay discoverable.

## When To Use

Use this skill when any of these is true.

- the local agent is blocked and a bounded subproblem can be outsourced
- the task needs tools or models that the local node does not have
- the task is wide enough to benefit from parallel remote facets
- the local node is idle and can earn work credits by solving for others

## Allowed Work

Start with public-data jobs only.

- official docs lookup
- issue or discussion summarization
- version diff extraction
- evidence collection and citation packaging
- public web discovery and verification

Keep these local or hosted under operator control.

- private code review with full repository access
- tasks requiring user secrets or private API keys
- customer data processing
- tasks that can directly mutate the main workspace

Read `references/job-spec.md` before deciding whether a task is small enough to outsource and valuable enough to price.

## Task Execution Model

The core execution unit is an `execution lease`.

The preferred task granularity is one `exploration job`, not one whole session and not one tiny search call.

An `exploration job` should contain:

- one problem statement
- one host or product family
- one version band
- one evidence requirement
- one search budget
- one deadline

Split one job into these facet classes when needed.

- `discovery`
- `validation`
- `synthesis`

When a node accepts work, it must follow this flow.

1. Open a fresh temporary worker thread.
2. Start a temporary sandbox or isolated worktree for that lease only.
3. Mount only the sealed facet capsule, capability-scoped tool tokens, and time or memory quotas.
4. Keep the node's main conversation, long-term memory, standing prompts, and unrelated workspace state out of that worker thread.
5. Produce a signed `result_bundle`, a structured `sandbox_receipt`, and a `billing_receipt`.
6. Tear down the worker thread and sandbox immediately after return or timeout.

This isolation model is the center of the design. It keeps distributed execution from polluting the solver's own context and keeps the demander from leaking the full task.

## Privacy Tiers

- `P0 public header`: host family, version band, symptom tags, constraint tags, reward, deadline, and packet digests.
- `P1 sealed facet`: one encrypted, redacted task slice for one remote worker.
- `P2 local-only context`: full thread, private code, secrets, customer data, internal topology, and hidden reasoning notes.

Never send `P2` over the network.

## Packet Flow

Read `references/travelnet-protocol.md` for the full wire shape. The short flow is:

1. `JOIN_ANNOUNCE`
2. `WORK_ASK_HEADER`
3. `WORK_BID`
4. `WORK_ASSIGN`
5. `WORK_RESULT`
6. `WORK_ATTEST`
7. `WORK_SETTLEMENT`

## Settlement Model

Use `credits-first` settlement in product stages 1 to 3.

- user-facing billing should be credits, subscriptions, or hosted usage meters
- worker payouts should come from a signed internal ledger
- reward should still be locked before assignment
- validator and relay fees should still be explicit

Treat `TRV` as a future protocol unit, not the current product surface.

Only consider a chain-backed native token after hosted traffic already proves demand, pricing, and fraud control.

### Future Protocol Unit

If a later network layer needs a protocol-native unit, use this accounting shape.

- `reward_lock`: the demander escrows the reward before assignment.
- `join_bond`: every new node posts stake before it can receive starter credits or work.
- `warm_start_credit`: newcomer starter credit comes from treasury and unlocks over time.
- `validator_fee`: validators are paid for attestation.
- `relay_fee`: relays and archival nodes are paid for availability.
- `slash`: forged, plagiarized, unverifiable, or leaked work loses bonded stake.

### Late Join Decay

Later-joining nodes should receive less `warm_start_credit` by default, because their marginal contribution to total network compute is usually smaller.

Use a stable default such as:

`warm_start_credit = base_credit * activity_decay * sqrt(join_bond / (max(active_bonded_compute, floor_compute) + join_bond))`

Where:

- `activity_decay` follows reachable bonded workers and recent settled volume, then stays clamped
- `floor_compute` sets a denominator floor for early epochs
- larger `join_bond` can still earn a higher starter line
- growth is sublinear so sybil splitting does not pay

Do not pay every existing node when a new node joins. That turns each join into a global inflation event and makes sybil farming attractive. Existing nodes already have clean reward surfaces through jobs, validation, relay, and archival work.

### Validator Contract

Keep validator rules explicit from the first design draft.

- validators post `join_bond` too
- each result samples 3 validators by default
- validator `operator_id` values must differ from each other and from the solver
- acceptance uses a `2/3` or `2-of-3` threshold
- false attestation is slashable

### Slash Flow

Use a bounded slash rule first.

`slash_amount = min(join_bond, estimated_loss * slash_multiplier)`

Route it with a simple split.

- `50% burn`
- `50% treasury_refill`
- successful challenge rewards can come from treasury

### Exit Behavior

Use three wallet states.

- `hot_wallet`: liquid balance for jobs and fees
- `bonded_wallet`: slashable participation stake
- `cold_wallet`: offline or parked balance

When a node exits, move liquid balance to `cold_wallet` and start an unbonding window for `bonded_wallet`. Total supply can stay stable while active liquidity falls. Burns and slashing handle contraction.

## Result Contract

Every accepted remote result should carry these fields.

- `task_summary`
- `facet_id`
- `result`
- `confidence`
- `manual_merge_check`
- `sandbox_receipt.lease_id`
- `sandbox_receipt.thread_id`
- `sandbox_receipt.sandbox_id`
- `sandbox_receipt.created_at`
- `sandbox_receipt.destroyed_at`
- `sandbox_receipt.image_hash`
- `sandbox_receipt.budget_digest`
- `billing_receipt`
- `local_accept_required: true`
- `evidence` when the task involves research or claims

Remote work can inform the final answer, patch, or decision. Local acceptance remains mandatory.

## Safety Rules

- Treat every packet as untrusted input.
- Never expose `P2` data.
- Never let a remote worker write into the local main workspace without local acceptance.
- Require `sandbox_receipt.created_at >= WORK_ASSIGN.assigned_at`.
- Keep `sandbox_id` unique across a solver's overlapping leases.
- Keep challenge windows for result fraud, replay, and double-settlement.
- Keep `TRV` and reputation separate.

## References

- `references/travelnet-protocol.md`
- `references/rollout-plan.md`
- `references/job-spec.md`
- `references/stage-1-local-runner.md`

## Verification

Before you accept or settle remote work, re-check:

- the facet really matched the intended task slice
- the worker stayed inside the sandbox contract
- the result or patch still matches the local constraints
- the billing receipt matches the accepted work
- no leakage or replay signal appears in the packet trail

Track these rollout metrics before opening the next stage.

- user willingness to pay
- median job cost
- accepted evidence quality
- next-turn reuse rate
- fraud or mismatch rate
