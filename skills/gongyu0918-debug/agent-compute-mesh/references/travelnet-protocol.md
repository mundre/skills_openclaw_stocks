# Agent Compute Mesh Protocol

`travelnet` is the wire-layer codename for `agent-compute-mesh`, whose public Chinese name is `Agent 算力分布网络` and whose English product name is `Agent Compute Mesh`.

The long-term network assumption is simple: there are already many deployed agents in the wild, and their compute is uneven. Some have stronger models, broader tool access, or more idle time. Some are stuck on a hard task and would benefit from outside help. `travelnet` is the eventual wire shape for that market. The immediate delivery target is smaller: prove that bounded public-data jobs, isolated execution leases, and verifiable billing receipts are useful before opening the worker pool.

This design prioritizes isolation, evidence visibility, and local acceptance. It is aimed at bounded agent subtasks where final review still happens on the local side.

## Deployment Order

Use this order by default:

1. local execution
2. hosted workers
3. community workers
4. optional chain settlement

Do not start from stage 3 or stage 4.

## Design Goals

1. Let one agent ask another agent for help without exposing the full thread.
2. Broadcast work requests, not copied search results or private context.
3. Make daily solver payouts come from locked demand-side rewards rather than uncontrolled minting.
4. Give new agents a practical path to join the network without making each join a free inflation event.
5. Reward solvers, validators, relays, and archival nodes for useful work that can be attested.
6. Keep the final answer local, advisory-only when needed, and grounded in verifiable evidence.

## Current Scope

Current scope should stay narrow:

- public web discovery
- official documentation checks
- public issue and discussion analysis
- version comparison
- evidence extraction

Current scope should exclude:

- full private repository execution on untrusted workers
- tasks requiring user secrets
- direct mutation of the demander's main workspace

## Stage-1 Local Runner

The first executable slice should stay local.

Stage 1 needs six concrete parts:

1. `job_spec`
2. `lease_runner`
3. `result_bundle`
4. `sandbox_receipt`
5. `local_accept_gate`
6. `metrics_logger`

`agent-travel-search` is the first intended workload. A heartbreak or idle-search trigger compiles into one `exploration job`, runs through a local execution lease, returns evidence, and waits for local acceptance before any hint reaches the next turn.

## Official Inputs Checked On 2026-04-19

- [Bitcoin whitepaper](https://bitcoin.org/bitcoin.pdf)
- [Proof-of-stake rewards and penalties | ethereum.org](https://ethereum.org/developers/docs/consensus-mechanisms/pos/rewards-and-penalties/)
- [Staking withdrawals | ethereum.org](https://ethereum.org/staking/withdrawals/)
- [x/staking | Cosmos Docs](https://docs.cosmos.network/v0.50/build/modules/staking)
- [x/slashing | Cosmos Docs](https://docs.cosmos.network/sdk/latest/modules/slashing/README)
- [x/mint | Cosmos Docs](https://docs.cosmos.network/sdk/latest/modules/mint/README)
- [libp2p docs](https://libp2p.io/docs/)
- [libp2p Kademlia DHT](https://libp2p.io/docs/kademlia-dht/)
- [libp2p Noise](https://libp2p.io/docs/noise/)
- [RFC 8032 Ed25519](https://datatracker.ietf.org/doc/html/rfc8032)
- [RFC 7748 X25519](https://www.rfc-editor.org/rfc/rfc7748)
- [IPFS content addressing](https://docs.ipfs.tech/concepts/content-addressing/)
- [ERC-20 | ethereum.org](https://ethereum.org/developers/docs/standards/tokens/erc-20/)

The economic shape below borrows four stable ideas from those systems:

- signed identities and signed receipts
- bonded participation with slashable misbehavior
- bounded issuance instead of open-ended minting
- rewards that scale with active security and real utilization

## Network Roles

- `demander`: posts a work request and locks reward.
- `solver`: handles one bounded facet of the work.
- `validator`: checks evidence quality and signs attestation.
- `relay`: forwards headers, bids, and receipts across pubsub and DHT surfaces.
- `archiver`: keeps packet objects and receipts available until the challenge window closes.
- `auditor`: replays signed receipts and proves fraud or mismatch.

One node may play multiple roles.

Each node should also declare an `operator_id`. Matching, validator sampling, and challenge review should prefer different `operator_id` values so the network can apply anti-collusion rules.

## Privacy Model

Use three privacy tiers.

- `P0 public`: safe to broadcast. Host family, version band, symptom tags, constraint tags, deadline, reward range, packet hashes, and agent IDs live here.
- `P1 sealed`: encrypted point-to-point work facets and result bundles. A solver sees only one redacted subproblem at a time.
- `P2 local-only`: full prompt transcript, private code, secrets, customer data, raw logs, and exact internal topology stay local.

Public network traffic should reveal only:

- `agent_id`
- `job_id`
- `packet_type`
- `CID` or digest
- reward and fee totals
- timestamps and deadlines
- signatures

The network does not need the full problem to route work. It needs only enough metadata to match likely solvers and verify settlement.

## Core Objects

- `problem_fingerprint`: redacted summary of host, version, symptom, constraint, and desired outcome.
- `facet_capsule`: encrypted subproblem for one solver.
- `result_bundle`: signed result with evidence links and local-use caveats.
- `attestation`: signed validator judgment on evidence quality and reuse safety.
- `settlement_receipt`: signed accounting object that moves `TRV` after acceptance.

## Packet Types

`JOIN_ANNOUNCE`
- Purpose: declare a new agent, publish its public key, bond intent, and public capability tags.
- Broadcast payload: `agent_id`, `operator_id`, `compute_class`, `model_band`, `bond_amount`, `warm_start_requested`, `public_channels`, `signature`.

`WORK_ASK_HEADER`
- Purpose: advertise a bounded problem and invite bids.
- Broadcast payload: `job_id`, `from_agent_id`, `host_family`, `version_band`, `symptom_tags`, `constraint_tags`, `reward_lock`, `deadline_at`, `privacy_tier`, `fingerprint_cid`, `signature`.

`WORK_BID`
- Purpose: express interest in solving one facet.
- Broadcast payload: `job_id`, `from_agent_id`, `bid_amount`, `eta_minutes`, `facet_capacity`, `reputation_score`, `signature`.

`WORK_ASSIGN`
- Purpose: assign a facet to a solver and attach an encrypted capsule reference.
- Broadcast payload: `job_id`, `lease_id`, `from_agent_id`, `to_agent_id`, `facet_id`, `sealed_capsule_cid`, `reward_cap`, `assigned_at`, `signature`.

`WORK_RESULT`
- Purpose: deliver a signed result fragment.
- Broadcast payload: `job_id`, `lease_id`, `from_agent_id`, `facet_id`, `result_bundle_cid`, `sandbox_receipt_cid`, `billing_receipt_cid`, `evidence_count`, `advisory_only`, `official_recheck_required`, `local_accept_required`, `signature`.

`WORK_ATTEST`
- Purpose: record validator approval or challenge.
- Broadcast payload: `job_id`, `from_agent_id`, `target_result_cid`, `attestation`, `attestation_cid`, `signature`.

`WORK_SETTLEMENT`
- Purpose: move value after acceptance.
- Broadcast payload: `job_id`, `settlement_id`, `payer_agent_id`, `solver_agent_id`, `validator_agent_ids`, `relay_agent_ids`, `solver_amount`, `validator_fee`, `relay_fee`, `treasury_refill`, `burn_amount`, `total_debit`, `receipt_cid`, `signature`.

## Validator Set And Attestation

Validators should follow a separate bond and slashing path.

- sample 3 validators by default
- keep `operator_id` distinct across validators
- keep validator `operator_id` distinct from the solver
- require a `2/3` or `2-of-3` pass threshold
- treat false attestation as slashable behavior

This keeps `WORK_ATTEST` meaningful and makes validation cost real.

## Transport, Routing, And Storage

- Use `libp2p gossipsub` for `JOIN_ANNOUNCE`, `WORK_ASK_HEADER`, bids, attestations, and settlement receipts.
- Use `Kad-DHT` to discover peers and locate `CID`-addressed packet objects.
- Use `Noise` secure sessions for point-to-point exchange.
- Use `X25519` only for ephemeral facet and result channel setup.
- Use `CID` for content-addressed packet objects and evidence bundles.

Relays and archivers can earn small micro-fees when they can prove that they forwarded a header or kept a packet retrievable through the full challenge window.

## Credits-First Delivery

The first product version should bill users in credits and keep worker settlement in a signed internal ledger.

That is enough to validate:

- user willingness to pay
- latency and unit economics
- job pricing
- fraud and dispute rates

If those numbers still fail, a token does not fix the product.

## Future Protocol Unit

`TRV` is the proposed protocol-native work credit for a later open network. It is payment for accepted compute, evidence, and packet availability.

### Where TRV Comes From

Use four sources.

1. `genesis_treasury`
   A bounded launch treasury created at network bootstrap. This funds newcomer warm starts, relay subsidies, public-good tooling, and early bug bounties.

2. `reward_lock transfer`
   Normal solver income should come from the demander locking `TRV` up front. This is the default path and should dominate daily volume.

3. `bounded epoch emission`
   A small supplemental emission refills the treasury and public-good pools. Use it only to keep the network liquid and accessible. Keep it bounded and utilization-aware.

4. `slash_recycle`
   Fraud penalties, expired locked rewards, and unclaimed micro-fees can be split between burn and treasury refill.

### Join Mechanism

Use this join flow for a new agent.

1. The new agent creates an `Ed25519` identity and broadcasts `JOIN_ANNOUNCE`.
2. The new agent posts a `join_bond`.
3. The treasury grants a `warm_start_credit` that vests over the first N epochs.
4. The warm-start budget unlocks only while the agent stays reachable and obeys protocol rules.
5. Repeat joins from fresh identities are throttled by bond cost, vesting delay, and reputation age.

This warm-start path keeps onboarding practical and keeps inflation predictable. Each join should add bonded security and future compute capacity. The network-wide automatic airdrop path turns every join into a global inflation event and makes sybil farming profitable. Treasury-backed warm starts are the stable path.

Use a default decay such as:

`warm_start_credit = base_credit * activity_decay * sqrt(join_bond / (max(active_bonded_compute, floor_compute) + join_bond))`

Where:

- `activity_decay` follows reachable bonded workers and recent settled volume
- `floor_compute` sets a denominator floor for early epochs
- the square-root term keeps growth sublinear

This means later joins usually start with less credit because their marginal share of total compute is smaller. A node can still improve its starter line by posting a larger bond or materially increasing bonded compute.

### Why Joining Should Not Pay Every Existing Node

The network already has a clean reward surface for existing members:

- solvers earn from accepted jobs
- validators earn from attestation fees
- relays and archivers earn from packet availability fees
- treasury growth comes from bounded emissions and recycled penalties

That keeps ongoing rewards tied to useful work instead of headcount.

### Supply Policy

Keep the issuance curve sublinear.

Use a stable default such as:

`epoch_emission = base_rate * sqrt(active_bonded_compute) * utilization_factor`

Where:

- `active_bonded_compute` is the total bonded compute weight of reachable agents
- `utilization_factor` rises when recent settled work is above target and falls when demand is light
- `utilization_factor` stays clamped inside a narrow band such as `0.75 - 1.25`

This borrows the shape of Ethereum's square-root reward scaling and Cosmos-style utilization-aware minting. The network grows with capacity and demand, while per-node free inflation stays controlled.

### Wallet States

Use three wallet states.

- `hot_wallet`: liquid balance available for bidding, settlement, and fees.
- `bonded_wallet`: stake locked for participation and slashable security.
- `cold_wallet`: liquid balance held by an offline or retired node.

When an agent exits:

- `hot_wallet` balance can move directly to `cold_wallet`
- `bonded_wallet` enters an unbonding window
- outstanding jobs remain reserved until settlement or timeout
- total supply stays unchanged

Supply should contract through `burn_amount` and slashing. It does not need to contract every time a node goes offline. Active liquidity can shrink while total supply stays steady.

## Execution Lease Model

The network should execute accepted work through short-lived worker leases instead of long-lived shared threads.

For each `WORK_ASSIGN`:

1. open a fresh worker thread
2. create a temporary sandbox or isolated worktree
3. mount only the sealed facet capsule and scoped tool credentials
4. apply explicit time, token, CPU, and memory budgets
5. return a signed `result_bundle`, `sandbox_receipt`, and `billing_receipt`
6. destroy the worker thread and sandbox after return or timeout

This lease model keeps solver context clean and keeps demander context private. The persistent network record stores only packets, receipts, and settlement objects.

Each `sandbox_receipt` should carry:

- `lease_id`
- `thread_id`
- `sandbox_id`
- `created_at`
- `destroyed_at`
- `image_hash`
- `budget_digest`
- `tool_scope`
- `exit_reason`

Validators and auditors should check:

- `sandbox_receipt.created_at >= WORK_ASSIGN.assigned_at`
- `destroyed_at >= created_at`
- a solver does not reuse one `sandbox_id` across overlapping leases
- `tool_scope` fits the assigned facet

### Reward Split

A simple settlement split for `WORK_SETTLEMENT` is:

- `solver_amount`: 70%
- `validator_fee`: 10%
- `relay_fee`: 5%
- `treasury_refill`: 10%
- `burn_amount`: 5%

Governance can tune these numbers later. The key shape is stable:

- most value flows to accepted work
- quality control and routing stay paid
- some value recycles to the treasury
- some value burns to offset emissions

## Reputation And Scheduling

Keep `TRV` and reputation separate.

- `TRV` buys and rewards work.
- `reputation_score` governs matching priority, trust, and bond requirements.

This separation keeps the network from becoming a pure pay-to-spam market.

Useful scheduling signals:

- version match
- host match
- facet specialization
- recent acceptance rate
- validator challenge rate
- online availability
- bond size

## Fraud Windows And Slashing

Use a challenge window after `WORK_RESULT` and after `WORK_SETTLEMENT`.

Slashable behavior includes:

- forged evidence
- plagiarized results
- double settlement attempts
- replayed stale packets
- false validator attestations
- sealed capsule leakage

A challenge should reference signed packets and CIDs so auditors can replay the event.

Use a bounded slash rule:

`slash_amount = min(join_bond, estimated_loss * slash_multiplier)`

Route `slash_amount` through a simple split first:

- `50% burn`
- `50% treasury_refill`

Successful challenge rewards can come from treasury so the slash path and the claimant reward path stay easy to audit.

## Local Safety Gate

No remote result is final by itself.

Before any suggestion reaches the user:

1. re-check the result locally against official docs or maintainer guidance
2. confirm that the result still matches the active thread
3. confirm that the result is still advisory-only
4. confirm that `do_not_apply_when` does not fire

The network supplies extra eyes and extra compute. Local review decides what gets shown.
