# Stage-1 Local Runner

Use this file when `agent-compute-mesh` needs the first executable slice.

## Goal

Ship one local path that proves the `exploration job` contract before any hosted worker or community worker exists.

## Required Parts

1. `job_spec`
   Capture the problem, host family, version band, evidence requirement, privacy tier, budget, deadline, and facet plan.

2. `lease_runner`
   Open one fresh worker thread and one isolated worktree for each lease.

3. `result_bundle`
   Return task output, evidence, and advisory caveats in one structured object.

4. `sandbox_receipt`
   Return `lease_id`, `thread_id`, `sandbox_id`, `created_at`, `destroyed_at`, `image_hash`, `budget_digest`, `tool_scope`, and `exit_reason`.

5. `local_accept_gate`
   Review result quality, evidence fit, and safety gates before the output can reach the next turn or the main workspace.

6. `metrics_logger`
   Record job cost, review time, evidence depth, reuse, mismatch, and acceptance rate.

7. `agent-travel-search adapter`
   Compile heartbreak or idle-search triggers into one `exploration job`.

## Stage-1 Flow

1. Compile one bounded `exploration job`.
2. Open a fresh local execution lease.
3. Run the facet inside a temporary thread and isolated worktree.
4. Emit `result_bundle`, `sandbox_receipt`, and `billing_receipt`.
5. Apply `local_accept_gate`.
6. Record metrics.

## Runnable Entry Points

- `scripts/run_local_lease.py`
  Runs one local lease from a JSON `job_spec` and writes artifacts under `.runtime/leases/<lease_id>/`.
- `scripts/review_local_lease.py`
  Applies the local acceptance gate and records `accepted` or `rejected`.
- `scripts/smoke_test_local_runner.py`
  Runs the end-to-end stage-1 smoke test.

Recommended commands:

```bash
python scripts/run_local_lease.py assets/stage1_sample_job.json --json
python scripts/review_local_lease.py .runtime/leases/<lease_id> accept --reviewer local-operator
python scripts/smoke_test_local_runner.py
```

## Exit Criteria

Stay in stage 1 until these signals look healthy:

- operators reuse results in later turns
- evidence quality stays stable
- review time stays acceptable
- mismatch and fraud-like signals stay low
