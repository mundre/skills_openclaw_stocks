---
name: AI Company Harness Strategist
slug: ai-company-harness-strategist
version: 1.0.0
homepage: https://clawhub.com/skills/ai-company-harness-strategist
description: Harness Engineeringstrategy与riskSkill包。挑战analyze、趋势研判、ethicsgovern、组织变革。归CEO所有，CRO+CISO+CLO联合supervise。
license: MIT-0
tags: [harness-engineering,strategy,risk-management,ethics,trends,governance,ai-agent,llm-ops]
triggers:
  - harnessstrategy
  - AI挑战analyze
  - 趋势研判
  - ethicsgovern
  - 组织变革
  - 风控compliance
  - harness strategy
  - risk management
  - future trends
  - ethics governance
interface:
  analyze-risks:
    description: analyzeHarness落地risk
    inputs:
      implementation_context:
        type: object
        required: true
    outputs:
      risks: object[]
      priority_matrix: object
      mitigation_plans: string[]
    errors:
      - code: STR_001 message: riskassess超限 action: triggerCRO介入
      - code: STR_002 message: ethics边界模糊 action: 暂停并请求CLOreview
      - code: STR_003 message: 人才缺口预警 action: notifyCHOstart招聘
  plan-trends:
    description: plan未来趋势适应strategy
    inputs:
      time_horizon:
        type: enum[short,medium,long]
        required: true
    outputs:
      milestones: object[]
      investment_needs: object
    errors:
      - code: STR_004 message: 时间范围无效 action: 使用默认medium
  assess-ethics:
    description: ethicscomplianceassess
    inputs:
      use_case:
        type: string
        required: true
      risk_level:
        type: enum[low,medium,high,critical]
        required: false
    outputs:
      compliant: boolean
      gaps: string[]
      recommendations: string[]
    errors:
      - code: STR_005 message: complianceassess失败 action: 返回默认不compliance结论
  plan-org-change:
    description: develop组织变革计划
    inputs:
      current_roles:
        type: string[]
        required: true
      target_state:
        type: object
        required: false
    outputs:
      transition_plan: object[]
      skill_gaps: string[]
      timeline_months: number
    errors:
      - code: STR_006 message: role映射失败 action: 返回通用转型path
  strategic-recommendation:
    description: 生成strategy建议
    inputs:
      company_context:
        type: object
        required: true
      industry:
        type: string
        required: false
    outputs:
      recommendations: string[]
      confidence_score: number
      risks: string[]
    errors:
      - code: STR_007 message: data不足 action: 返回最小化建议集
permissions:
  files: [read,write]
  network: [api]
  commands: []
  mcp: []
dependencies:
  skills: [ai-company-hq,ai-company-ceo,ai-company-cro,ai-company-ciso,ai-company-clo,ai-company-cho,ai-company-harness]
  cli: []
quality:
  saST: Pass
  vetter: Pending
  idempotent: true
metadata:
  category: governance
  layer: AGENT
  cluster: ai-company
  maturity: STABLE
  license: MIT-0
  standardized: true
  standardized_by: ai-company-standardization-1.0.0
---

# AI Company Harness Strategist

CEOstrategy+CRO+CISO+CLO联合supervise。Harness Engineering的strategyplan与risk management。

## 1潜在挑战analyze

6大规模化瓶颈: 系统复杂度高/人才供给不足/单点故障/ethics责任模糊/security边界博弈/生态碎片化。

risk矩阵: 单点故障P1/人才缺口P1/security越权P0/责任模糊P2/生态碎片P2。

## 2未来发展趋势

5大演进方向: standard化assesssystem/Skill生态/OS层编排capability/automation自我进化/学科独立化。
2026-2028roadmap: 试点->爆发->OS雏形。

## 3ethics与complianceframework

CLOcompliance: 前置verify+全processaudit+tracemechanism+periodicalgorithm audit。
CISOsecurity: 极高riskprohibit/高risk人工confirm/end-to-end日志/沙箱隔离。

## 4组织变革path

role转型: 工程师->环境建筑师。
新兴position: agent架构师/Agent编排工程师/AIquality assurance工程师/熵manage工程师。

## 5KPI

riskidentify>=95% | 建议采纳>=70% | 变革完成>=60% | compliancereview100%

## 6Change Log

1.0.0 2026-04-16 Initial version
1.0.1 2026-04-16 review修复: 扩展interface为详细YAML格式补全metadata