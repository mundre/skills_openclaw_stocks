# 孙子兵法

## ART OF WAR ON AI AGENTS

> 兵者，国之大事，死生之地，存亡之道，不可不察也。
>
> War is a vital matter. It is the province of life or death. It must be thoroughly studied.

---

## 安装 INSTALL

```bash
clawdhub install art-of-war
```

---

## 这是什么 WHAT THIS IS

十三章。

Thirteen chapters.

每章映射到 agent 组织。

Each mapped to agent orchestration.

不是比喻。

Not metaphors.

是实战模式：

Practical patterns for:

- 任务评估 Task assessment
- 部署决策 Deployment decisions
- 多 agent 策略 Multi-agent strategy
- Token 经济 Token economy
- 风险管理 Risk management

---

## 核心原则 FIVE CORE PRINCIPLES

**知彼知己，百战不殆。**

Know the task and know your agent. In a hundred deployments, never defeated.

**先胜后战。**

Win before you deploy. Structure the problem so the solution is obvious.

**速战速决。**

Speed is essential. Prolonged agent runs dull the blade.

**先为不可胜。**

First make yourself undefeatable. Then wait for the opportunity.

**奇正相生。**

Combine orthodox and unorthodox. Seven parts standard. Three parts creative.

---

## 快速决策 QUICK DECISION

```
任务到达 Task arrives
    │
    ↓
5 分钟能搞定吗？Can I do this in 5 min?
    ├── 是 Yes → 自己做 Do it yourself
    └── 否 No → 继续 Continue
    │
    ↓
任务定义清晰吗？Task clearly defined?
    ├── 否 No → 先规划 Plan first
    └── 是 Yes → 继续 Continue
    │
    ↓
Token 预算？Token budget?
    ├── 低 Low → 单 agent Single agent
    └── 高 High → 多 agent Multi-agent
    │
    ↓
风险？Risk if wrong?
    ├── 高 High → 防御 Defense first
    └── 低 Low → 速度 Speed priority
    │
    ↓
部署。监控。验证。Deploy. Monitor. Validate.
```

---

## 十三章 THIRTEEN CHAPTERS

| 章 Chapter | 应用 Application |
|---|---|
| 始计篇 Laying Plans | 任务评估 (五事七计) Task assessment |
| 作战篇 Waging War | Token 经济，速度，迭代限制 Token economy, speed, limits |
| 谋攻篇 Attack by Stratagem | 规划优先级，避免强攻 Planning hierarchy |
| 军形篇 Tactical Dispositions | 防御优先，风险管理 Defense first, risk |
| 兵势篇 Energy | 动量，奇正相生 Momentum, orthodox+unorthodox |
| 虚实篇 Weak Points & Strong | 战略聚焦 Strategic targeting |
| 军争篇 Maneuvering | 间接approach Indirect approaches |
| 九变篇 Variation | 灵活应变，五危 Adaptability, five faults |
| 行军篇 Marching | 读信号，干预 Signal reading, intervention |
| 地形篇 Terrain | 任务分类 Task classification |
| 九地篇 Nine Grounds | 资源分配 Resource allocation |
| 火攻篇 Fire Attack | 工具使用 Tool usage |
| 用间篇 Spies | 情报收集，交叉验证 Intelligence, verification |

---

## 文件 FILES

| 文件 File | 用途 Purpose |
|---|---|
| `SKILL.md` | 十三章全文 Thirteen chapters |
| `references/thirteen-chapters.md` | 详解 Detailed mappings |
| `scripts/assess-task.py` | 五事七计打分 Five constants scoring |
| `scripts/quick-decision.py` | 快速决策 Quick decision |
| `CARD.md` | 可打印决策卡 Printable one-page reference |

---

## 相关 RELATED

- [thinking-skills](https://github.com/wanikua/thinking-skills) — 20 个思维框架 20 thinking frameworks
- [awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) — skill 合集 Skill collection

---

## 许可 LICENSE

MIT
