# Job Spec

Use this file when `agent-compute-mesh` needs to decide task size, price, and split strategy.

## Preferred Unit

Use one `exploration job` as the preferred unit.

Each job should contain:

- one problem statement
- one host or product family
- one version band
- one evidence requirement
- one search or execution budget
- one deadline
- one privacy tier
- one local acceptance rule

## Minimum Schema

Use this minimum shape when a local runner or scheduler compiles one job:

- `job_id`
- `problem_statement`
- `host_family`
- `version_band`
- `evidence_requirement`
- `privacy_tier`
- `search_budget`
- `deadline_at`
- `local_accept_required`
- `official_recheck_required`
- `redundancy_mode`
- `facet_plan`

`facet_plan` should stay small in stage 1. A simple local runner can start with one facet, then expand to `discovery / validation / synthesis` only when the evidence path is stable.

## Facet Types

- `discovery`: find candidate sources or paths
- `validation`: check source quality, version fit, and official grounding
- `synthesis`: convert accepted evidence into a usable operator result

## Too Large

Do not ship these as one external job:

- full-agent session replay
- unrestricted codebase mutation
- cross-product incident investigation with many moving parts

## Too Small

Do not ship these as standalone priced jobs:

- one search query
- one fetch call
- one short summarization call

These are better as internal steps inside a larger `exploration job`.

## Pricing Inputs

- estimated latency
- evidence depth
- number of facets
- redundancy level
- review overhead
- privacy level

## Acceptance Contract

Each job should also define:

- `manual_merge_check`
- `do_not_apply_when`
- `expected_evidence_types`
- `result_visibility`

That keeps the execution lease, the result contract, and the local acceptance gate aligned.
