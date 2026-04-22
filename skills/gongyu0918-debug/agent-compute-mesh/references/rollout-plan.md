# Rollout Plan

Use this file when `agent-compute-mesh` needs a practical deployment path.

## Principle

Do product validation before decentralization.

The network idea is valid only if the underlying job is useful, priced well, and cheap enough to verify.

## Stage 1: Local

Goal:
- prove that `exploration job` is a useful unit
- prove that evidence packaging improves next-turn outcomes

Execution:
- jobs stay on the local machine
- no third-party workers
- no token settlement
- one fresh worker thread per lease
- one isolated worktree or sandbox per lease
- local acceptance before any result enters the next turn

Build slice:
- `job_spec`
- `lease_runner`
- `result_bundle`
- `sandbox_receipt`
- `local_accept_gate`
- `metrics_logger`
- `agent-travel-search adapter`

Measure:
- job creation rate
- user reuse rate
- average evidence count
- average operator review time
- sandbox receipt completeness
- local acceptance pass rate

## Stage 2: Hosted

Goal:
- prove that users will pay for outsourced public-data jobs
- measure job latency, unit economics, and fraud rate

Execution:
- central scheduler
- hosted workers
- credits-first billing
- signed internal ledger for worker payouts
- validator sampling with operator anti-affinity

Measure:
- gross margin per job
- worker utilization
- refund rate
- duplicate or low-quality result rate

## Stage 3: Community Workers

Goal:
- open the worker market without breaking job quality

Execution:
- keep scheduler centralized
- let approved third-party workers claim jobs
- use execution leases, challenge windows, and attestation
- keep validator and solver `operator_id` values distinct

Measure:
- fill rate
- challenge rate
- payout disputes
- worker retention

## Stage 4: Optional Chain

Only consider this stage when all of these are true:

- multiple independent operators are active
- off-platform trust is the bottleneck
- cross-border settlement is frequent
- ordinary database ledger is now the wrong abstraction

If any of those is still false, stay off-chain.
