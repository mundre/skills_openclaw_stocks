# LEARNINGS.md — 经验教训 / 最佳实践 / 洞察

> 由 self-improvement-loop skill 管理。手动编辑请保持 `## [ID] category` 标题行格式完整。

---

## 模板格式

```markdown
## [LRN-YYYYMMDD-NNN] correction|best_practice|insight
**Logged**: ISO-8601
**Status**: pending | active | in_progress | resolved | promoted | dormant
**Pattern-Key**: <source>.<type>.<identifier>

### 发生了什么
[具体场景，1-2句话，说清楚在什么情况下、哪个环节出了问题]

### 根因是什么
[为什么会发生，不是表面现象，是结构性原因]

### 下次如何避免
[抽象成一条可操作的原则，可以迁移到类似情况]

*---*
```

---

## 示例（可删除）

## [LRN-20260401-001] correction
**Logged**: 2026-04-01T00:00:00+08:00
**Status**: pending
**Pattern-Key**: workflow.redundancy.multi_path_different_oversight

### 发生了什么
为同一功能设计了两条路径：一条由 AI 在 memory-daily-distill 中直接升华，另一条走 A/B/C/D 用户确认路径。

### 根因是什么
没有在设计阶段识别"同一结果只有一条路径"的原则，导致监督层级不统一。

### 下次如何避免
新增工作流路径前，先问"这条路径和现有路径是否做同一件事？用户监督层级是否一致？"如果答案是"是" → 合并路径。

*---*
