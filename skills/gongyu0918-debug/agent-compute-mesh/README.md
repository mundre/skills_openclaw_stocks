# Agent 算力分布网络 / Agent Compute Mesh

这个 skill 当前主攻的方向很明确：先把外部算力任务做成能验证价值的产品，再决定要不要把它扩成开放网络。现在的首选路线是 `local -> hosted -> community workers -> optional chain`。  
This skill now takes a clear path: first turn outside-compute jobs into a product with proven value, then decide whether it deserves to become an open network. The preferred rollout is `local -> hosted -> community workers -> optional chain`.

它不要求远程节点看到完整任务，也不让远程节点污染自己的主上下文。它要求的是更严格的边界：局部任务切片、临时执行租约、签名结果包、可追溯结算回执。  
It does not require remote nodes to see the whole task, and it does not let remote nodes pollute their own main context. It asks for stricter boundaries instead: bounded task slices, temporary execution leases, signed result bundles, and traceable settlement receipts.

技术调用名：`$agent-compute-mesh`。  
Technical invocation name: `$agent-compute-mesh`.

## 实验状态 / Experimental Status

- 这是一次 `vibecoding` 构想，基于几轮 prompt 调整、文档整理和轻量测试。 / This is a `vibecoding` concept built through a few prompt iterations, document shaping, and light tests.
- 它还不具备可验证的安全性，也不具备可验证的可靠性。 / It does not have verified security, and it does not have verified reliability.
- 这里的协议、代币、调度、执行隔离和结算机制都还是设计稿。 / The protocol, token model, scheduling, execution isolation, and settlement logic here are still design drafts.
- 真正投入使用前，至少还需要独立安全审计、对抗测试、故障注入、经济学仿真和长期运行验证。 / Before any real use, it needs independent security review, adversarial testing, fault injection, economic simulation, and long-run validation.
- 如果有人直接拿这套设计去跑，出了问题自己负责。 / If someone uses this design directly and it breaks, that is their own responsibility.

## 设计重点 / Design Focus

- 路线优先级：先做产品验证，再做去中心化。 / Rollout priority: validate the product before decentralizing it.
- 任务分发：广播的是脱敏工作头，不是完整 prompt。 / Task dispatch: the network broadcasts redacted work headers, not full prompts.
- 临时执行：远程节点接单后必须在临时线程和临时沙箱里运行。 / Ephemeral execution: remote nodes must run accepted work inside temporary threads and temporary sandboxes.
- 结果回收：返回的是签名结果包和计费回执，本地节点决定是否接受。 / Result return: the network returns signed result bundles and billing receipts, while the local node decides whether to accept them.
- 结算顺序：先用 credits 和内部账本，再讨论链上代币。 / Settlement order: use credits and internal ledgers first, then discuss an on-chain token later.
- 新人入网：晚加入节点默认拿更少的启动额度，额度和边际新增算力挂钩。 / Network entry: later-joining nodes receive smaller starter credits by default, and those credits track marginal added compute.

## 定位 / Positioning

这套设计优先强调三件事：隔离、证据可见性、本地验收。它更适合高约束、需要留痕、需要人为最终拍板的 agent 子任务市场。  
This design puts three things first: isolation, evidence visibility, and local acceptance. It fits agent subtask markets with tight constraints, audit pressure, and a human or local agent making the final call.

## 当前落地 / Current Rollout

第一阶段只做公开数据任务，比如官方文档核对、issue 汇总、版本差异提取、公开网页证据打包。真正需要私有代码、用户密钥、客户数据、主工作区写权限的任务，继续留在本地或自控托管环境。  
Stage 1 should handle only public-data jobs such as official-doc verification, issue summaries, version-diff extraction, and public-web evidence packaging. Tasks that need private code, user secrets, customer data, or write access to the main workspace should stay local or inside operator-controlled hosting.

推荐的任务粒度是一整个 `exploration job`，不是整段 agent 会话，也不是一条极小的搜索调用。一个 job 里包含一个问题、一个版本带、一个证据要求、一个预算、一个截止时间，必要时再拆成 `discovery / validation / synthesis` 三类 facet。  
The preferred unit is one `exploration job`, not a whole agent session and not one tiny search call. One job should contain one problem, one version band, one evidence requirement, one budget, and one deadline, then split into `discovery / validation / synthesis` facets only when needed.

## 验证指标 / Validation Metrics

- 用户是否愿意为一次 `exploration job` 付费。 / Whether users will pay for one `exploration job`.
- 单个 job 的中位成本和毛利。 / Median cost and margin per job.
- 被接受证据的质量。 / Quality of accepted evidence.
- 下一轮任务复用率。 / Next-turn reuse rate.
- 欺诈率、错配率和退款率。 / Fraud rate, mismatch rate, and refund rate.

## 晚加入衰减 / Late Join Decay

晚加入节点默认应该拿更少的 `warm_start_credit`。理由很简单：网络越成熟，新节点对总算力的边际提升占比通常越小。  
Later-joining nodes should receive less `warm_start_credit` by default. The reason is simple: the more mature the network becomes, the smaller the marginal share that a single new node usually adds to total compute.

一个更稳的默认公式是：  
A steadier default is:

`warm_start_credit = base_credit * activity_decay * sqrt(join_bond / (max(active_bonded_compute, floor_compute) + join_bond))`

- `activity_decay` 绑定在线质押 worker 数和最近若干 epoch 的真实结算量，并保持在窄区间里。 / `activity_decay` should track reachable bonded workers and recent settled volume, then stay clamped inside a narrow band.
- `floor_compute` 给早期网络一个硬下限，避免在网络很小时把启动额度抬到近上限。 / `floor_compute` gives the early network a hard denominator floor, which keeps tiny networks from handing out near-cap starter credits.
- 次线性增长继续保留，拆分小号的收益会更差。 / Sublinear growth stays in place, so splitting into many small identities yields worse economics.

“每来一个新节点，就给全网每个节点发一轮币”这条路会把每次入网都变成一次全网通胀事件，也会让 sybil 分身更有利可图。网络更稳定的做法，是把启动额度从 `genesis_treasury` 或公共 treasury 里按规则发给新节点，把既有节点的收益继续绑定在真实工作、验证、中继和归档上。  
The “every new join triggers a network-wide airdrop” path turns every join into a global inflation event and makes sybil splitting attractive. The stable path is to fund newcomer starter credits from `genesis_treasury` or a public treasury, while keeping incumbent rewards tied to real work, validation, relay, and archival duties.

## 验证者与惩罚闭环 / Validator And Slash Loop

- 验证者也要质押，验证者集合单独计信誉。 / Validators should post bond too, and their reputation should be tracked separately.
- 每个结果默认抽 3 个验证者，要求 `operator_id` 互异。 / Each result should sample 3 validators by default, with distinct `operator_id` values.
- `2/3` 或 `2-of-3` 通过阈值适合第一版确认。 / A `2/3` or `2-of-3` threshold is a practical first attestation rule.
- solver 和 validator 需要运营方反亲和，串通成本才会真实存在。 / Solver and validator selection should use operator anti-affinity so collusion costs stay real.
- `slash_amount` 可以先用这个默认值：`min(join_bond, estimated_loss * slash_multiplier)`。 / A workable default for `slash_amount` is `min(join_bond, estimated_loss * slash_multiplier)`.
- `slash_amount` 的去向先按 `50% burn + 50% treasury_refill` 落地，挑战成功奖励再由 treasury 单独发放。 / Route `slash_amount` as `50% burn + 50% treasury_refill`, then pay successful challenge rewards from treasury as a separate step.

## 第一阶段产物 / Stage-1 Build Slice

第一阶段先把本地 runner 跑通，目标是验证 `exploration job` 的形状、回执、验收门和度量体系。  
Stage 1 should ship a local runner first, so the project can validate the `exploration job` shape, receipts, acceptance gate, and metrics pipeline.

- `job_spec`：明确问题、版本带、预算、隐私级别、facet 计划。 / `job_spec`: define the problem, version band, budget, privacy level, and facet plan.
- `lease_runner`：本地创建临时线程和临时 worktree，按 lease 执行。 / `lease_runner`: create local temporary threads and temporary worktrees, then execute by lease.
- `result_bundle + sandbox_receipt`：把结果和执行环境一起带回。 / `result_bundle + sandbox_receipt`: return the result together with an execution receipt.
- `local_accept_gate`：本地复核通过后才能进入下一轮对话或写回。 / `local_accept_gate`: only locally accepted output can enter the next turn or write back.
- `metrics_logger`：记录成本、证据质量、复用率、错配率。 / `metrics_logger`: track cost, evidence quality, reuse, and mismatch rates.
- `agent-travel-search adapter`：把 heartbreak 或空闲搜索编译成 `exploration job`。 / `agent-travel-search adapter`: compile heartbreak or idle-search work into an `exploration job`.

当前仓库已经带了可运行入口：`scripts/run_local_lease.py`、`scripts/review_local_lease.py`、`scripts/smoke_test_local_runner.py`，以及样例 job [assets/stage1_sample_job.json](assets/stage1_sample_job.json)。  
This repository now includes runnable entry points: `scripts/run_local_lease.py`, `scripts/review_local_lease.py`, `scripts/smoke_test_local_runner.py`, plus the sample job [assets/stage1_sample_job.json](assets/stage1_sample_job.json).

## 执行隔离 / Execution Isolation

接单节点执行任务时，协议中心不是搜索，中心是隔离。  
When a solver accepts work, the center of the protocol is isolation.

1. 新建临时 worker 线程。  
2. 新建临时沙箱或隔离 worktree。  
3. 只注入这一单的分面胶囊、能力范围内的工具令牌、时间和资源配额。  
4. 禁止挂载主对话、长期记忆、常驻 prompt 和无关工作区状态。  
5. 返回 `result_bundle`、结构化 `sandbox_receipt`、`billing_receipt`。  
6. 线程和沙箱立刻销毁。  

1. Open a fresh worker thread.  
2. Open a temporary sandbox or isolated worktree.  
3. Mount only the facet capsule, scoped tool tokens, and resource budgets for that lease.  
4. Keep the main conversation, long-term memory, standing prompts, and unrelated workspace state out.  
5. Return `result_bundle`, a structured `sandbox_receipt`, and `billing_receipt`.  
6. Destroy the worker thread and sandbox immediately.

`sandbox_receipt` 至少要带这些字段：`lease_id`、`thread_id`、`sandbox_id`、`created_at`、`destroyed_at`、`image_hash`、`budget_digest`。validator 用它检查两件事：`created_at` 晚于 `WORK_ASSIGN`，以及同一 solver 的活跃 lease 没有复用同一个 `sandbox_id`。  
`sandbox_receipt` should at least carry `lease_id`, `thread_id`, `sandbox_id`, `created_at`, `destroyed_at`, `image_hash`, and `budget_digest`. Validators use it to check two things: `created_at` comes after `WORK_ASSIGN`, and no active lease from the same solver reuses the same `sandbox_id`.

## 协议文件 / Protocol Files

- [SKILL.md](SKILL.md)
- [SKILL.en.md](SKILL.en.md)
- [references/travelnet-protocol.md](references/travelnet-protocol.md)
- [references/rollout-plan.md](references/rollout-plan.md)
- [references/job-spec.md](references/job-spec.md)
- [references/stage-1-local-runner.md](references/stage-1-local-runner.md)
- [scripts/validate_travelnet_packet.py](scripts/validate_travelnet_packet.py)
- [scripts/run_local_lease.py](scripts/run_local_lease.py)
- [scripts/review_local_lease.py](scripts/review_local_lease.py)
- [scripts/smoke_test_local_runner.py](scripts/smoke_test_local_runner.py)
- [assets/travelnet_join_example.json](assets/travelnet_join_example.json)
- [assets/travelnet_job_example.json](assets/travelnet_job_example.json)
- [assets/stage1_sample_job.json](assets/stage1_sample_job.json)
- [assets/travelnet_result_example.json](assets/travelnet_result_example.json)
- [assets/travelnet_settlement_example.json](assets/travelnet_settlement_example.json)

## 设计输入 / Design Inputs

- [Bitcoin whitepaper](https://bitcoin.org/bitcoin.pdf)
- [Proof-of-stake rewards and penalties | ethereum.org](https://ethereum.org/developers/docs/consensus-mechanisms/pos/rewards-and-penalties/)
- [x/mint | Cosmos Docs](https://docs.cosmos.network/sdk/latest/modules/mint/README)
- [x/slashing | Cosmos Docs](https://docs.cosmos.network/sdk/latest/modules/slashing/README)
- [libp2p docs](https://libp2p.io/docs/)

## License

MIT
