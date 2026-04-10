---
name: shared-memory-os
description: Shared memory governance for multi-agent OpenClaw workspaces — with tiered memory, learnings capture, promotion review, lifecycle management, self-maintaining reports, cross-skill collaboration, and bilingual ClawHub-friendly docs.
version: 1.7.1
---

# Shared Memory OS

> English and 中文 are on the same page below. In ClawHub, read the language section directly instead of relying on anchor-jump behavior.

---

# English

Shared Memory OS turns workspace memory into a governed system instead of a pile of notes.

## Core capabilities
- layered memory governance
- active learnings harvesting into `.learnings/`
- review cadence and archive strategy
- conflict resolution order
- health scoring and health history
- duplicate learnings detection with evidence/confidence
- promotion candidate detection with review state
- promotion suggestion and memory patch generation
- weekly review, audit report, and dashboard generation
- stale durable memory detection with lifecycle hints
- validated repeated rule detection
- low-value learning detection
- workflow optimization suggestions
- conflict logging and conflict review reporting
- learning merge suggestions
- skill upgrade candidate detection
- migration guidance and initialization scripts
- self-improving loop
- maintenance runner
- policy profiles and workspace profiles
- cross-skill collaboration governance
- multi-agent write and review guidance
- periodic maintenance-day guidance

## References
- `references/governance-guide.md`
- `references/pattern-harvesting.md`
- `references/archive-strategy.md`
- `references/learnings-template.md`
- `references/health-check.md`
- `references/self-improving-loop.md`
- `references/health-score-model.md`
- `references/conflict-template.md`
- `references/migration-guide.md`
- `references/policy-profiles.md`
- `references/workspace-profiles.md`
- `references/cross-skill-collaboration.md`
- `references/multi-agent-governance.md`
- `references/maintenance-day.md`
- `references/zh-cn-guide.md`

## Scripts
- `scripts/bootstrap-shared-memory-os.js`
- `scripts/ensure-shared-memory-crons.js`
- `scripts/init-shared-memory-os.js`
- `scripts/migrate-notes-into-memory.js`
- `scripts/run-shared-memory-maintenance.js`
- `scripts/check-memory-health.js`
- `scripts/rebuild-learnings-index.js`
- `scripts/find-duplicate-learnings.js`
- `scripts/find-promotion-candidates.js`
- `scripts/find-stale-durable-memory.js`
- `scripts/find-validated-rules.js`
- `scripts/find-low-value-learnings.js`
- `scripts/build-workflow-optimization-suggestions.js`
- `scripts/log-memory-conflict.js`
- `scripts/build-conflict-review-report.js`
- `scripts/build-weekly-review.js`
- `scripts/record-health-snapshot.js`
- `scripts/build-promotion-suggestions.js`
- `scripts/build-learning-merge-suggestions.js`
- `scripts/find-skill-upgrade-candidates.js`
- `scripts/build-memory-patch-candidates.js`
- `scripts/build-audit-report.js`
- `scripts/build-dashboard.js`

## Setup
For first-time setup, run `node skills/shared-memory-os/scripts/bootstrap-shared-memory-os.js` from the workspace root. It initializes memory directories, installs or updates the default daily/weekly/monthly OpenClaw cron jobs, and runs one full maintenance pass.

If you only need to repair or reapply automation, run `node skills/shared-memory-os/scripts/ensure-shared-memory-crons.js`. The cron installer is idempotent: it updates matching jobs by name and creates missing ones.

## Guidance
Use this skill when you want memory to stay useful over time: keep facts durable, keep daily state local, keep lessons reusable, let promotion stay reviewable, let low-value noise get pruned, and let repeated lessons improve other skills too.

---

# 中文

Shared Memory OS 的目标，是把 workspace 里的共享记忆变成“可治理、可维护、可进化、可协同”的系统，而不是零散笔记。

## 核心能力
- 分层记忆治理
- 主动沉淀 `.learnings/`
- review cadence 与 archive strategy
- 冲突处理顺序
- 健康评分与历史趋势
- 带 evidence/confidence 的重复经验检测
- 带 review 状态的 promotion candidate 检测
- promotion 建议与 `MEMORY.md` patch 候选生成
- 周报、审计报告、dashboard 生成
- 带生命周期提示的 stale durable memory 检测
- 反复验证规则检测
- 低价值 learning 检测
- 工作流优化建议生成
- 冲突日志与冲突审查报告
- learning 合并建议
- skill 升级候选检测
- 初始化与迁移脚本
- 自学习进化闭环
- 一键 maintenance runner
- policy profile / workspace profile
- 与其他 skills 的协同治理
- 多 agent 写入与审核边界建议
- 周期性 maintenance day 指南

## 参考文档
- `references/zh-cn-guide.md`
- `references/governance-guide.md`
- `references/pattern-harvesting.md`
- `references/archive-strategy.md`
- `references/learnings-template.md`
- `references/health-check.md`
- `references/self-improving-loop.md`
- `references/health-score-model.md`
- `references/conflict-template.md`
- `references/migration-guide.md`
- `references/policy-profiles.md`
- `references/workspace-profiles.md`
- `references/cross-skill-collaboration.md`
- `references/multi-agent-governance.md`
- `references/maintenance-day.md`

## 脚本
- `scripts/bootstrap-shared-memory-os.js`
- `scripts/ensure-shared-memory-crons.js`
- `scripts/init-shared-memory-os.js`
- `scripts/migrate-notes-into-memory.js`
- `scripts/run-shared-memory-maintenance.js`
- `scripts/check-memory-health.js`
- `scripts/rebuild-learnings-index.js`
- `scripts/find-duplicate-learnings.js`
- `scripts/find-promotion-candidates.js`
- `scripts/find-stale-durable-memory.js`
- `scripts/find-validated-rules.js`
- `scripts/find-low-value-learnings.js`
- `scripts/build-workflow-optimization-suggestions.js`
- `scripts/log-memory-conflict.js`
- `scripts/build-conflict-review-report.js`
- `scripts/build-weekly-review.js`
- `scripts/record-health-snapshot.js`
- `scripts/build-promotion-suggestions.js`
- `scripts/build-learning-merge-suggestions.js`
- `scripts/find-skill-upgrade-candidates.js`
- `scripts/build-memory-patch-candidates.js`
- `scripts/build-audit-report.js`
- `scripts/build-dashboard.js`

## 初始化方式
首次接入时，优先在 workspace 根目录运行：`node skills/shared-memory-os/scripts/bootstrap-shared-memory-os.js`。它会完成目录初始化、创建/更新默认的 daily/weekly/monthly OpenClaw cron 任务，并立即跑一次完整 maintenance。

如果只是补装或修复自动化任务，运行：`node skills/shared-memory-os/scripts/ensure-shared-memory-crons.js`。这个脚本是幂等的：同名任务会被更新，缺失任务会被创建。

## 使用建议
当你希望共享记忆长期可用时，用它来维持：长期事实要稳定、当天状态要就地、经验要可复用、promotion 要可审查、低价值噪音要能被清理、而且反复验证过的经验还应反向推动其他 skills 一起变强。
