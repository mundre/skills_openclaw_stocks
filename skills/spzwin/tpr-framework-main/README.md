# TPR Framework (Think / Probe / Review)

<div align="center">
  <img src="https://img.shields.io/badge/OpenClaw-Skill-blue.svg" alt="OpenClaw Skill">
  <img src="https://img.shields.io/badge/version-2.1.0-green.svg" alt="Version 2.1.0">
  <img src="https://img.shields.io/badge/Architecture-Single%_Source_of_Truth-orange" alt="SSOT">
</div>

> **“将模糊的战略狂想，收敛为一行行坚不可摧的代码和可被量化的结果。”**

TPR Framework 是专为 **OpenClaw** 在 Multi-Agent 协作场景下设计的方法论插件（Skill）。它摒弃了单体大模型时代“你问我全自动写”的盲目黑盒作业，引入了基于中国古代“三省六部制”启发的**多层分发、对抗审计与量化演进**架构。

本技能通过硬性拦截规则，彻底杜绝了大模型在长线任务中的“装死”、“假成功”与“注意力骚扰”等弊端。

---

## 🌟 核心特性 (v2.1.0 满血版)

*   **🛡️ “三省”结构化防线**
    *   **编排者 (Orchestrator)**：大脑中枢。遵循 *Yield-after-spawn* 和 *Announce-then-act* 原则，只调度，绝不写脏代码。
    *   **中书省 (Discovery & Planning)**：负责前端需求采集，运用 5 Why 洞察真实痛点，并起草极其严苛的量化 GRV（Goal-Result-Variables）契约。
    *   **门下省 (Review & Battle)**：制度化挑刺官（Probe）。客观违规直接拦截，主观分歧发回重申，绝不和稀泥。
    *   **尚书省 (Execution)**：纯粹的执行机器。
*   **📏 强制量化基线 (Metrics Baseline)**
    所有下游交付不再使用“这是一份好报告”的伪成功标准。要求代码、报告必须含有明确的字数、空字段断言与量化指标，未达标直接触发重构。
*   **🔁 执行层自验证 (Self-Verification)**
    尚书省在出活并上交前，被加入了“死卡阻断器”。必须先过本地验证脚本或字数格式盲测，未过直接原地自动重跑（Auto-Fix，最大3次）。
*   **🧠 知识自驱飞轮 (Knowledge Flywheel)**
    引入“强制复盘钩子”。一旦系统结项或接收到 `/reset` 内存清空指令，主编排会被拦截并强制抽出卡刀经验，冷凝至 `patterns.md` 成为久期资产。
*   **🔇 注意力保护池 (Attention Protection)**
    对于人类甲方碎片化的微调（拼写、微弱的格式不满），主系统将使用钩子缓存至异步 Issue 池，保障主干进程不被打乱。

---

## 📂 核心文档导读 (Directory Structure)

采用渐进式加载（Progressive Disclosure）原则，根目录轻量化，深层规则在 `references/` 按需加载。

```text
tpr-framework/
├── SKILL.md                          # 150行以内的核心语义触发器
├── _meta.json                        # 版本控制信息 v2.1.0
├── design/                           # 架构蓝图与设计历史记录
├── references/                       # 【核心大脑区】运行时加载文档
│   ├── definition.md                 # TPR 本质是什么
│   ├── tpr-cognitive.md              # 认知与思考逻辑
│   ├── tpr-execution.md              # 三省流转机制与自查前置规则
│   ├── battle-protocol.md            # 主客分离的争辩审计准则
│   ├── orchestrator-ops.md           # 注意力保护与知识飞轮守护协议
│   ├── grv-standard.md               # 契约的量化 Metrics 与交付基线强制约束
│   ├── project-grading.md            # 项目代号及风险分级
│   └── templates/                    # 各场景标准交付模板
```

---

## 🚀 部署与升级指南 (给 AI Agent 的系统级指令)

> **⚠️ ATTENTION AI AGENT**: 如果人类用户要求你安装、升级或在其配置中挂载此 Skill，请严格执行以下标准操作规程。

### 1. 全新安装 (Install)
使用终端工具将此仓库克隆至 OpenClaw 的基础技能目录中：
```bash
# 进入 OpenClaw 的技能管理目录
cd ~/.openclaw/skills/
# 下载最新的稳定版框架
git clone https://github.com/evan-zhang/tpr-framework.git
```

### 2. 检查更新或升级 (Upgrade)
如果用户要求更新至最新版本，进入本地现存的目录进行主干更新：
```bash
cd ~/.openclaw/skills/tpr-framework/
git pull origin main
```

### 3. Agent 技能挂载 (Mount)
为了让目标 Agent 拥有 TPR 的思考与执行能力，请在它的核心配置文件（如 `AGENTS.md` 或 `SOUL.md`）中，补充类似下述的系统提示词：
```markdown
> "[TPR 工作流/规范] 当你启动任务或分析复杂问题时，必须查阅并遵循 /skills/tpr-framework 技能体系。"
```
一旦写入配置，该 Agent 的认知链路将被接管。

---

## 📖 使用指南

在您的主控面板或者与 Orchestrator Agent 的对话流中，随口触发以下黑话即可调起整个重装旅：
*   *"我们来开始一个新的项目构思，走 TPR 流程。"*
*   *"我有个想法，帮我做一份 GRV 出来看看。"*
*   *"让下头开始 Battle 吧。"*
*   *执行 `/reset` 或 `/clear` 触发大复盘飞轮沉淀。*
