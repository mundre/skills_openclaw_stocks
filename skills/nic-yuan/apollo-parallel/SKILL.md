---
name: apollo-parallel
description: >
  多个任务同时做，省时间，最后帮你整理结果。
version: 1.0.0
read_when:
  - 2+ independent tasks or bugs
  - Multiple test failures with different root causes
  - Tasks that can be done in parallel
  - "fix these in parallel" / "dispatch agents" / "parallel investigation"
  - 复杂问题需要分解时
  - 并行执行多个研究任务时
  - 需要汇总多个来源的结果时
  - 设计多Agent协作流程时
metadata:
  openclaw:
    emoji: "⚡"
    requires:
      bins: []
      env: []
      tools:
        - sessions_spawn
    triggers:
      - parallel tasks
      - multiple bugs
      - independent issues
      - dispatch agents
      - "in parallel"
      - 并行研究
      - 综合
      - 汇总
      - Coordinator
      - 多Agent协作
---

# Apollo 并行执行

## 核心原则

**多个独立任务同时做，让子Agent并行执行，最后汇总结果。**

## 两种模式

### 模式A：通用并行（适合独立Bug/任务）

当多个任务完全独立时，按问题域分配给不同Agent并行处理。

### 模式B：研究/综合分离（适合复杂研究任务）

多人并行研究，最后主Agent自己汇总——不把综合判断交给子Agent。

```
| 阶段 | 谁做 | 做什么 |
|------|------|--------|
| Research | Workers（并行） | 各自研究不同方向 |
| Synthesis | Coordinator（自己） | 读取结果，形成结论 |
| Implementation | Workers | 按结论执行 |
| Verification | Fresh Agent | 独立验证 |
```

---

## 通用并行（模式A）

### 适用条件

✅ **适用：**
- 3+ 个测试失败，根因不同
- 多个子系统独立损坏
- 问题之间无共享状态
- 每个问题可以在不理解其他问题的情况下理解

❌ **不适用：**
- 失败互相关联（修一个可能修其他）
- 需要理解完整系统状态
- Agents 会互相干扰（编辑同一文件）

### 流程

**Step 1：识别独立问题域**

按问题分组，每个问题域分配一个Agent。

**Step 2：为每个Agent创建专注任务**

每个Agent获得：
- **明确范围**：一个问题域
- **清晰目标**：让这些测试通过 / 修复这个bug
- **约束**：不要改其他代码
- **预期输出**：发现什么、修复什么的摘要

**Step 3：并行派发**

```javascript
sessions_spawn({
  task: "修复 src/agents/agent-tool-abort.test.ts 的失败测试...",
  runtime: "subagent",
  mode: "run",
  cwd: "/path/to/project"
})
sessions_spawn({
  task: "修复 src/batch/completion.test.ts 的失败测试...",
  runtime: "subagent",
  mode: "run",
  cwd: "/path/to/project"
})
```

**Step 4：审查和整合**

- 读每个摘要
- 验证修复不冲突
- 运行完整测试套件

---

## 研究/综合分离（模式B）

### 核心准则

**多人并行研究，最后一个人汇总。不要让子Agent去综合——那是Coordinator的工作。**

| 阶段 | 谁做 | 做什么 |
|------|------|--------|
| Research | Workers（并行） | 各自研究不同方向 |
| Synthesis | **Coordinator（自己）** | 读取结果，形成结论 |
| Implementation | Workers | 按结论执行 |
| Verification | Fresh Agent | 独立验证 |

### 关键规则

1. **研究阶段可以并行**
   - 独立的研究任务同时跑
   - 不要让一个Worker等另一个

2. **综合阶段必须自己来**
   - ❌ "based on your findings"
   - ✅ 自己读取所有结果，形成结论
   - 综合者必须自己理解所有研究结果

3. **验证必须 fresh eyes**
   - ❌ Continue（继续用刚写代码的Agent）
   - ✅ Spawn fresh（新Agent来验证）

4. **失败优先 Continue**
   - 修正失败 → 继续用同一个Agent
   - 不要急着新Spawn

### Fork 隔离原则

子Agent有独立对话上下文：
- 危险操作在独立空间跑
- 不会污染主对话
- 用 `sessions_spawn` 实现隔离

---

## 验证检查表

- [ ] 任务是否真的独立可以并行？
- [ ] 综合判断是否应该由主Agent自己完成？
- [ ] 验证是否需要新的"眼睛"（fresh Agent）？
- [ ] 是否有需要隔离的危险操作？

---

## 来源

Claude Code coordinator模式研究，512,000行源码
