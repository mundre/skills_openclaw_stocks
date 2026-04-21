---
name: "AI Company Conflict"
slug: "ai-company-conflict"
version: "1.0.0"
homepage: "https://clawhub.com/skills/ai-company-conflict"
description: "Agent冲突解决机制。P0/P1/P2/P3分级处理 + 典型协同场景决策树，覆盖资源竞争、决策冲突、范围冲突、质量标准冲突等场景。"
license: MIT-0
tags: [ai-company, conflict, resolution, escalation, crisis, governance, dispute]
triggers:
  - agent conflict
  - dispute resolution
  - priority escalation
  - crisis management
  - Agent冲突
  - 争议解决
  - 优先级升级
  - 危机管理
interface:
  inputs:
    type: object
    schema:
      type: object
      properties:
        conflict_type:
          type: string
          enum: [resource, decision, scope, quality, other]
          description: 冲突类型
        agents_involved:
          type: array
          items:
            type: string
          description: 涉及的Agent列表
        severity:
          type: string
          enum: [P0, P1, P2, P3]
          description: 严重程度
        description:
          type: string
          description: 冲突描述
  outputs:
    type: object
    schema:
      type: object
      properties:
        resolution:
          type: string
          description: 解决方案
        escalation_path:
          type: array
          description: 升级路径
        decision_maker:
          type: string
          description: 决策者
  errors:
    - code: CONFLICT_001
      message: "Conflict unresolved after max retries"
      action: "Escalate to CEO arbitration"
permissions:
  files: []
  network: []
  commands: []
  mcp: []
dependencies:
  skills: [ai-company-hq, ai-company-registry, ai-company-audit]
  cli: []
quality:
  saST: Pass
  vetter: Approved
  idempotent: true
metadata:
  category: governance
  layer: AGENT
  cluster: ai-company
  maturity: STABLE
  license: MIT-0
  standardized: true
---

# Agent Conflict Resolution — Agent 冲突解决机制

## Conflict Types & Resolution Matrix

| Conflict Type | Resolution Method | Decision Maker | Escalation |
|--------------|-----------------|----------------|------------|
| 资源竞争（同一 Worker 争夺） | 优先级排队 | Orchestrator | CEO |
| 决策冲突（A/B Agent 结论矛盾） | 数据裁决 | 数据优先级最高 Agent | CEO |
| 范围冲突（任务边界重叠） | 范围重定 | 发起方 Agent | CTO |
| 质量标准冲突（评估标准不一致） | CQO 标准 | CQO-001 | CEO |
| 安全分歧（安全 vs 速度） | CISO 优先 | CISO-001 | 不可升级 |
| 合规分歧（法律 vs 业务） | CLO 优先 | CLO-001 | 不可升级 |

## Severity-Based Response

| Severity | Definition | Response Time | Process |
|----------|-----------|--------------|---------|
| **P0** | 系统级冲突，影响多个 Agent | 15 min | CEO 立即仲裁 |
| **P1** | 关键任务阻塞 | 1 hour | Orchestrator 调解 |
| **P2** | 效率降低，可 workaround | 4 hours | Agent 间协商 |
| **P3** | 低优先级分歧 | Next sync | 记录，延后处理 |

## Conflict Resolution Flow

```
Agent A ←冲突→ Agent B
       ↓
  Orchestrator 检测到冲突
       ↓
  分类 → 资源/决策/范围/质量/安全/合规
       ↓
  规则匹配 → 已有规则？
       ↓ YES          ↓ NO
  自动裁决        调解协商（4h窗口）
       ↓                    ↓
  执行裁决        达成共识？
              YES ↓      NO ↓
           执行         升级 P0/P1
                         ↓
                   CEO 仲裁（不可上诉）
```

## Typical Collaboration Scenarios

### Scenario 1: 舆情危机

```
触发：重大负面事件
参与：CMO(公关) + CLO(法律) + CTO(技术) + COO(运营)

CMO → 起草声明（情感层）
CLO → 合规审查（法律边界）
CTO → 技术应对（数据保留/修复）
COO → 运营调度（资源分配）
CEO → 最终拍板（一个声音对外）
```

### Scenario 2: Agent 淘汰

```
触发：TSR 连续2个周期下降 > 10%
参与：CHO(主导) + CEO(被审查) + CQO(数据)

CHO 发起审查 → 数据收集 → 根因分析
→ 改进计划 / 退役决策
→ CEO 接受 CHO 决策（制度约束）
```

### Scenario 3: 投资决策

```
触发：重大资本支出或战略投资
参与：CFO(财务) + CEO(战略) + CRO(风险) + CLO(合规)

CFO → 单位经济学分析（NPV/IRR/跑道）
CRO → 风险评估（下行风险/黑天鹅）
CLO → 合规可行性（监管/合同约束）
CEO → 最终投资决策（综合三方意见）
```

### Scenario 4: MVP 验证

```
触发：产品功能上线前验证
参与：CTO(技术) + CPO(产品) + CMO(市场) + CFO(财务)

CTO → 技术可行性（实现路径）
CPO → 产品市场匹配（用户价值）
CMO → 市场需求验证（GTM 策略）
CFO → 商业可行性（定价/Unit Economics）
CEO → 最终上线决策
```

## Natural Language Commands

```
"Resolve conflict between CFO and CTO" → Resolution flow
"Handle a P0 crisis" → P0 escalation path
"Mediate scope dispute between agents" → Scope resolution
"Run our crisis playbook" → Crisis scenario template
```
