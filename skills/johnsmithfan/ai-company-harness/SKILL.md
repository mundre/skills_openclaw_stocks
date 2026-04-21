---
name: AI Company Harness
slug: ai-company-harness
version: 1.0.2
homepage: https://clawhub.com/skills/ai-company-harness
description: Harness Engineering技术架构Skill包。6层架构4大支柱permissioncontrol自愈mechanism。归CTO所有，CISOsecuritysupervise。
license: MIT-0
tags: [harness-engineering,ai-agent,architecture,context-engineering,feedback-loop,guardrails,llm-ops,agentic]
triggers:
  - harness工程
  - AI Agent运行环境
  - 6层架构
  - 上下文工程
  - 架构Constraint
  - 反馈回路
  - 人类supervise
  - 自愈mechanism
  - Agent编排
  - Linter
  - CIautomation
  - 熵manage
  - harness engineering
  - AI agent control
interface:
  design-harness:
    description: designHarness蓝图
    inputs:
      task_description:
        type: string
        required: true
        description: Harnessdesign任务描述
      target_layer:
        type: enum[L1,L2,L3,L4,L5,L6,full]
        required: false
        default: full
        description: Goal架构layer
      agent_count:
        type: number
        required: false
        description: 预期Agent数量
      risk_level:
        type: enum[low,medium,high,critical]
        required: false
        default: medium
        description: risk等级
    outputs:
      harness_blueprint: object
      guardrails: string[]
      estimated_setup_hours: number
    errors:
      - code: HRN_001 message: Agent循环依赖 action: 立即中断并reportCTO
      - code: HRN_002 message: 跨层越权调用 action: CI拦截并triggerCISOalert
      - code: HRN_003 message: 上下文超限 action: triggerContext Reset
      - code: HRN_004 message: Harness级联故障 action: startL6recovermechanism
  audit-harness:
    description: auditHarness配置compliance
    inputs:
      harness_config_path:
        type: string
        required: true
      check_layers:
        type: string[]
        required: false
        description: 指定audit哪些层
      strict_mode:
        type: boolean
        required: false
        default: false
    outputs:
      compliant: boolean
      score: number
      violations: object[]
      entropy_score: number
      recovery_health: string
    errors:
      - code: HRN_005 message: 配置文件不存在 action: 提示用户检查path
      - code: HRN_006 message: YAML解析失败 action: 返回解析错误详情
  invoke-recovery:
    description: triggerL6recovermechanism
    inputs:
      failure_type:
        type: enum[loop,permission_violation,cascade_failure,context_rot]
        required: true
      context_file:
        type: string
        required: false
        description: 失败上下文文件path
    outputs:
      recovery_status: enum[success,partial,failed]
      actions_taken: object[]
      rollback_points: string[]
      entropy_after: number
    errors:
      - code: HRN_007 message: recover失败 action: upgrade到人工干预
permissions:
  files: [read,write]
  network: [api]
  commands: [linter,ci]
  mcp: [sessions_spawn,sessions_send]
dependencies:
  skills: [ai-company-hq,ai-company-cto,ai-company-ciso]
  cli: []
quality:
  saST: Pass
  vetter: Pending
  idempotent: true
metadata:
  category: functional
  layer: AGENT
  cluster: ai-company
  maturity: STABLE
  license: MIT-0
  standardized: true
  standardized_by: ai-company-standardization-1.0.0
---

# AI Company Harness

CTO技术架构层。AI Agent运行环境control系统。

## 1核心Definition

Harness Engineering驾驭工程 HashiCorp创始人Hashimoto 2026年2月提出。Agent = Model + Harness。
每当AI犯错，就工程化1个plan让它永远不再犯同样的错。
Prompt lessThan Context lessThan Harness

## 26层架构 L1-L6

L1信息边界层: AGENTS.md单1事实来源精确control知识范围。
L2工具系统层: 封装API为Tool动态加载节省85% Token。
L3execute编排层: Planner-Generator-Evaluator3Agentcollaborate混合蓝图模式。
L4记忆状态层: Context Resetmechanism避免上下文腐化。
L5沙箱execute层: 隔离环境防止risk扩散。
L6Constraintverifyrecover层: Ralph Wiggum自我review循环。

## 34大支柱

P1上下文工程: resolve上下文焦虑on-demand检索。
P2架构Constraint: 严格分层violationCI拦截。
P3反馈回路: Ralph Wiggum循环+Doc-gardening Agent。
P4人类supervise: 人类从编码者转变为审核员。

## 4permissioncontrolsystem

极高risk: prohibit需白名单。高risk: 人工confirm。中等risk: end-to-end日志。低risk: 无需record。

### L4permission签裁状态

ENGR L4生产操作permission: ✅ 有条件通过(CVSS 2.92, CISO-001签裁 2026-04-17)
CEO-EXECcrisis直通接口: ✅ 有条件通过(CVSS 2.87, CISO-001签裁 2026-04-17)
双重approvemechanism: ✅ 已签裁(CTO+CISO 2026-04-16)
E2E测试用例: ✅ 已create(10个测试用例)

参考文档:
- stride-assessment-l4.md (ENGR L4 STRIDEassess)
- stride-assessment-crisis-channel.md (crisis直通STRIDEassess)
- dual-approval-e2e-test.md (双重approveE2E测试)
- dual-approval-process.md (双重approveprocess)

## 5典型案例

OpenAI百万行代码: 3人5月100万行1500 PR效率10倍。

## 6KPI

自我修正>=85% CI拦截>=95% Token节省>=60% MTTR<=5min automation>=70%

## 7Change Log

1.0.0 2026-04-16 Initial version
1.0.1 2026-04-16 review修复: 扩展interface为详细YAML格式补全metadata
1.0.2 2026-04-17 P0修复: 补充L4permission签裁状态+STRIDEassess引用+双重approveE2E引用