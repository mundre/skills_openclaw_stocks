---
name: "AI Company Conflict"
slug: "ai-company-conflict"
version: "1.0.0"
homepage: "https://clawhub.com/skills/ai-company-conflict"
description: "Agent冲突resolvemechanism。P0/P1/P2/P3分级handle + 典型collaborate场景决策树，覆盖资源竞争、决策冲突、范围冲突、quality standard冲突等场景。"
license: MIT-0
tags: [ai-company, conflict, resolution, escalation, crisis, governance, dispute]
triggers:
  - agent conflict
  - dispute resolution
  - priority escalation
  - crisis management
  - Agent冲突
  - 争议resolve
  - 优先级upgrade
  - crisismanage
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
          description: resolveplan
        escalation_path:
          type: array
          description: upgradepath
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

# Agent Conflict Resolution — Agent 冲突resolvemechanism

## Conflict Types & Resolution Matrix

| Conflict Type | Resolution Method | Decision Maker | Escalation |
|--------------|-----------------|----------------|------------|
| 资源竞争（同1 Worker 争夺） | 优先级排队 | Orchestrator | CEO |
| 决策冲突（A/B Agent 结论矛盾） | data裁决 | data优先级最高 Agent | CEO |
| 范围冲突（任务边界重叠） | 范围重定 | 发起方 Agent | CTO |
| quality standard冲突（assessstandard不1致） | CQO standard | CQO-001 | CEO |
| security分歧（security vs 速度） | CISO 优先 | CISO-001 | 不可upgrade |
| compliance分歧（法律 vs 业务） | CLO 优先 | CLO-001 | 不可upgrade |

## Severity-Based Response

| Severity | Definition | Response Time | Process |
|----------|-----------|--------------|---------|
| **P0** | 系统级冲突，影响多个 Agent | 15 min | CEO 立即仲裁 |
| **P1** | 关键任务阻塞 | 1 hour | Orchestrator 调解 |
| **P2** | 效率降低，可 workaround | 4 hours | Agent 间协商 |
| **P3** | 低优先级分歧 | Next sync | record，延后handle |

## Conflict Resolution Flow

```
Agent A ←冲突→ Agent B
       ↓
  Orchestrator detect到冲突
       ↓
  分类 → 资源/决策/范围/质量/security/compliance
       ↓
  规则匹配 → 已有规则？
       ↓ YES          ↓ NO
  自动裁决        调解协商（4h窗口）
       ↓                    ↓
  execute裁决        达成共识？
              YES ↓      NO ↓
           execute         upgrade P0/P1
                         ↓
                   CEO 仲裁（不可上诉）
```

## Typical Collaboration Scenarios

### Scenario 1: 舆情crisis

```
trigger：重大负面event
参与：CMO(公关) + CLO(法律) + CTO(技术) + COO(运营)

CMO → 起草声明（情感层）
CLO → compliancereview（法律边界）
CTO → 技术respond to（data保留/修复）
COO → 运营调度（资源分配）
CEO → 最终拍板（1个声音对外）
```

### Scenario 2: Agent 淘汰

```
trigger：TSR 连续2个cycle下降 > 10%
参与：CHO(主导) + CEO(被review) + CQO(data)

CHO 发起review → data收集 → 根因analyze
→ improve计划 / 退役决策
→ CEO 接受 CHO 决策（policyConstraint）
```

### Scenario 3: 投资决策

```
trigger：重大资本支出或strategy投资
参与：CFO(财务) + CEO(strategy) + CRO(risk) + CLO(compliance)

CFO → 单位经济学analyze（NPV/IRR/跑道）
CRO → riskassess（下行risk/黑天鹅）
CLO → compliance可行性（监管/合同Constraint）
CEO → 最终投资决策（综合3方意见）
```

### Scenario 4: MVP verify

```
trigger：产品Functiongo live前verify
参与：CTO(技术) + CPO(产品) + CMO(市场) + CFO(财务)

CTO → 技术可行性（实现path）
CPO → 产品市场匹配（用户价值）
CMO → 市场需求verify（GTM strategy）
CFO → 商业可行性（定价/Unit Economics）
CEO → 最终go live决策
```

## Natural Language Commands

```
"Resolve conflict between CFO and CTO" → Resolution flow
"Handle a P0 crisis" → P0 escalation path
"Mediate scope dispute between agents" → Scope resolution
"Run our crisis playbook" → Crisis scenario template
```
