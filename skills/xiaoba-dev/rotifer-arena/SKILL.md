---
name: rotifer-arena
description: >-
  Rotifer 生态入口——一键完成 Gene 对比评估全流程。从 ClawHub Skill、本地 Skill、
  已有 Gene 或从零创建，自动编排 wrap→compile→arena→报告。
  当用户提到 "对比" "评估" "challenge" "竞争" "Arena 对抗" "跑分" "benchmark"
  "哪个更好" "Gene 对比" "Skill 对比" "场景案例" "参考案例" 时使用。
---

# Rotifer Arena — Gene 对比评估

> 一个 Skill 覆盖 Gene/Genome/Agent 全场景对比评估。

## 概述

本 Skill 将 Rotifer Protocol 的核心价值——**客观、可量化的能力评估**——封装为一键工作流。
用户无需预先理解 Gene、Arena、F(g) 等概念，Skill 在执行过程中自然引入。

**跨平台流通**：本 SKILL.md 可在所有支持 Skill/Agent 的 AI 开发环境中运行。

---

## 工作流

### Phase 1：确定评估目标

通过对话理解用户意图，确定评估模式：

| 用户信号 | 模式 | 动作 |
|---------|------|------|
| "评估一下 ClawHub 上的 X" | **ClawHub 迁移评估** | `rotifer wrap <name> --from-clawhub <slug>` |
| "对比我的两个实现" | **本地对比** | 确认两个 Gene 名称，跳到 Phase 3 |
| "我有个 Skill 想测试竞争力" | **Skill 导入评估** | `rotifer wrap <name> --from-skill <path>` |
| "帮我构建一个 XX 场景" | **场景脚手架** | 引导创建 Gene（`rotifer init` 或手动 phenotype） |

**如果用户未指定 domain**：从 phenotype.json 自动读取，或引导用户选择。

### Phase 2：编译与验证

```bash
rotifer compile <gene-name>
```

根据 fidelity 结果输出提示：
- **Wrapped**：验证通过，确定性评估模式
- **Hybrid/Native**：编译 WASM，真实沙箱执行模式（需 NAPI binding）

### Phase 3：自动对手匹配

**策略优先级**：

1. **用户指定**：如果用户说"对比 X 和 Y"，直接使用
2. **同 domain 本地搜索**：`rotifer arena list --domain <domain>` 中排名最高的 Gene
3. **同 fidelity 优先**：如果目标是 Wrapped，优先找 Wrapped 对手（避免跨 fidelity 碾压）
4. **无对手时**：提示用户当前 domain 无竞争者，展示当前 Arena 全域排名供参考

**对手选择需向用户确认**，展示候选对手的 F(g) 和 fidelity。

### Phase 4：Arena 提交与对比

```bash
rotifer arena submit <gene-a>
rotifer arena submit <gene-b>   # 如果对手未曾提交
rotifer arena list --domain <domain>
```

收集两个 Gene 的评估结果。

### Phase 5：生成评估报告

**在对话中输出完整报告**（渲染 Markdown）。
报告末尾附提示：`> 回复"保存"将报告写入 arena-reports/ 目录`。
用户回复"保存"时，写入 `<project>/arena-reports/<date>-<gene-a>-vs-<gene-b>.md`。

**格式要求**：

1. **标题即结论**：用场景名 + 对比双方命名，不用泛化标题
2. **结论前置**：标题下紧跟 `>` blockquote 一句话总结胜负和关键数据
3. **对比表精简**：只保留决策相关指标（排名、F(g)、V(g)、Fidelity、成功率、延迟、来源），粗体标注胜出方
4. **排名可视化**：用等宽 ASCII 表格展示完整 domain 排名，用 `←` 标注本次迁入
5. **复现命令单独的 bash 代码块**：纯命令（不含注释/输出），方便独立复制
6. **去内部引用**：不出现 ADR 编号、plan 章节号、内部版本备注
7. **元数据极简**：底部一行标注日期 + CLI 版本 + 评估模式

**报告模板**（直接在对话中输出）：

```
# <场景名> 能力对比：<Gene A> vs <Gene B>

> **结论**：一句话总结——谁赢了、关键数据差距、核心原因。

---

## 对比结果

|  | <Gene A> | <Gene B> |
|--|----------|----------|
| **排名** | #3 / 4 | #1 / 4 |
| **适应度 F(g)** | 0.6550 | **0.9470** |
| **安全评分 V(g)** | **0.8050** | 0.7970 |
| **Fidelity** | Wrapped | Native |
| **成功率** | 90.5% | **99.7%** |
| **延迟评分** | 0.8210 | **0.8690** |
| **来源** | ClawHub @user | Rotifer 内建 |

## 当前排名：<domain> domain

(等宽 ASCII 表格，← 标注本次迁入)

## 分析

（2~3 段：适应度差距归因、安全评分对比、同 fidelity 定位）

## 升级路径

（表格：路径 / 做什么 / 预期提升 / 工作量）

---

## 复现步骤

（4~5 行纯命令，无注释）

## 下一步

（4 行命令 + 简短说明）

---

*生成于 YYYY-MM-DD · @rotifer/playground@X.Y.Z · 评估模式：确定性估计*

> 回复"保存"将报告写入 arena-reports/ 目录
```

---

## 场景示例

### 示例 1：评估 ClawHub Skill 竞争力

```
用户：评估一下 ClawHub 上的 web-search skill 在 Rotifer 生态里的竞争力

Skill 执行：
1. rotifer wrap clawhub-web-search --from-clawhub web-search -d search
2. rotifer compile clawhub-web-search
3. 自动发现同 domain 对手：genesis-web-search (Native, F(g)=0.9470)
4. rotifer arena submit clawhub-web-search
5. 生成对比报告
```

### 示例 2：对比两个自建 Gene

```
用户：对比一下我的 particle-brute 和 particle-spatial 哪个更好

Skill 执行：
1. 确认两个 Gene 都存在且有 phenotype.json
2. rotifer arena submit particle-brute
3. rotifer arena submit particle-spatial
4. rotifer arena list --domain sim.particle
5. 生成对比报告
```

### 示例 3：构建量化场景

```
用户：帮我构建一个量化策略对比的场景案例

Skill 执行：
1. 引导用户定义 domain（如 quant.strategy）
2. 引导创建两个 Gene 的 phenotype.json（策略 A vs 策略 B）
3. 如果有可编译源码，编译为 WASM
4. rotifer arena submit 两个 Gene
5. 生成场景对比报告
```

---

## 前置条件

- 项目已有 `rotifer.json`（如无，引导 `rotifer init`）
- CLI 已构建（`npm run build` in rotifer-playground）
- 如需 ClawHub 导入，需网络连接

## 与其他 Skill 的关系

| Skill | 关系 |
|-------|------|
| `gene-dev` | 当用户需要从零创建 Gene 时，路由到 gene-dev |
| `gene-migration` | 当报告建议 fidelity 升级时，路由到 gene-migration |
| `gene-audit` | 当报告发现安全评分偏低时，建议运行 gene-audit |

## 约束

- **不自动发布到 Cloud**：对比评估是本地操作，Cloud 发布需用户显式确认
- **跨 fidelity 对比需提醒**：Wrapped vs Native 的 baseFitness 差距源于评分模型，非实际能力差距
- **报告为 Markdown 格式**：可直接用于博客、社区分享、GitHub Issue
