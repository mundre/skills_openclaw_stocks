---
name: "AI Company CQO Skill Reviewer"
slug: ai-company-cqo-skill-reviewer
version: 1.0.0
homepage: https://clawhub.com/skills/ai-company-cqo-skill-reviewer
description: |
  AI Company CQOskillreview模块。执行G0-G7quality gate，三重review(质量/security/技术)，review反馈循环management。
  触发关键词：skillreview、reviewskill、质量检查、security审查
license: MIT-0
tags: [ai-company, cqo, review, quality-gate, inspection]
triggers:
  - skillreview
  - reviewskill
  - 质量检查
  - security审查
  - skill review
  - quality check
interface:
  inputs:
    type: object
    schema:
      type: object
      properties:
        skill_path:
          type: string
          description: 待reviewSkill路径
        review_type:
          type: string
          enum: [full, quality_only, security_only, tech_only]
          default: full
        strict_mode:
          type: boolean
          default: true
        max_iterations:
          type: integer
          default: 3
      required: [skill_path]
  outputs:
    type: object
    schema:
      type: object
      properties:
        verdict:
          type: string
          enum: [APPROVED, CONDITIONAL, REJECTED]
        quality_score:
          type: number
        security_score:
          type: number
        tech_score:
          type: number
        gate_results:
          type: array
          items:
            type: object
            properties:
              gate:
                type: string
              status:
                type: string
                enum: [PASS, FAIL, WARNING]
              details:
                type: string
        issues:
          type: array
          items:
            type: object
            properties:
              severity:
                type: string
                enum: [critical, high, medium, low]
              category:
                type: string
              description:
                type: string
              fix_suggestion:
                type: string
        iteration_count:
          type: integer
        review_duration_ms:
          type: integer
      required: [verdict, quality_score, security_score]
  errors:
    - code: REVIEWER_001
      message: "Skill path not found"
    - code: REVIEWER_002
      message: "Invalid skill structure"
    - code: REVIEWER_003
      message: "Security check failed - CVSS >= 7.0"
    - code: REVIEWER_004
      message: "Max iterations exceeded"
    - code: REVIEWER_005
      message: "Quality gate G0-G7 not all passed"
permissions:
  files: [read, write]
  network: []
  commands: []
  mcp: [sessions_send, subagents]
dependencies:
  skills:
    - ai-company-hq
    - ai-company-kb
    - ai-company-ciso-security-gate
    - ai-company-ciso
    - ai-company-cto
    - ai-company-standardization
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
  tags: [ai-company, cqo, review, quality-gate]
---

# AI Company CQO Skill Reviewer v1.0

> CQO主导的skillreview模块。G0-G7quality gate，三重review，反馈循环。

---

## 概述

**ai-company-cqo-skill-reviewer** 是AIskilllearning流程的第二阶段模块，负责：

1. **quality gate**: 执行G0-G7quality gate检查
2. **三重review**: 质量(CQO) + security(CISO) + 技术(CTO)
3. **反馈循环**: review失败时生成修改建议，支持迭代修复

---

## 核心功能

### Module 1: G0-G7quality gate

**功能**: 八层quality gate体系

| 门禁 | 名称 | 检查项 | 通过标准 |
|------|------|--------|----------|
| G0 | 文件结构 | 目录结构符compliance范 | 4个目录齐全 |
| G1 | Frontmatter | YAML格式正确，必需字段存在 | 字段完整 |
| G2 | 描述质量 | description > 50字 | 含触发+动作 |
| G3 | security扫描 | 无RED FLAGS，CVSS < 7.0 | security通过 |
| G4 | 文档完整性 | 核心流程有说明 | 无悬空引用 |
| G5 | 脚本测试 | scripts/下脚本可执行 | 零报错 |
| G6 | SKILL.md长度 | 渐进式披露 | < 500行 |
| G7 | 禁止文件 | 无README.md等 | 无禁止文件 |

### Module 2: 三重review

**功能**: 并行执行三类review

```yaml
triple_review:
  quality_review:
    agent: CQO
    focus:
      - 文档完整性
      - 接口规范性
      - 测试覆盖率
    output: 质量评分(0-100)
  
  security_review:
    agent: CISO
    methods:
      - STRIDE威胁建模
      - CVSS漏洞评分
      - 代码扫描
    criteria:
      CVSS: "< 7.0"
      STRIDE: "无FAIL项"
    output: security评分(0-100)
  
  tech_review:
    agent: CTO
    focus:
      - 架构合理性
      - 接口设计
      - 可扩展性
    output: 技术评分(0-100)
```

### Module 3: review反馈循环

**功能**: review失败时的自动修复机制

```yaml
feedback_loop:
  max_iterations: 3
  process:
    1. reviewAgent生成问题列表
    2. reviewAgent生成修改建议
    3. 创建Agent执行修改
    4. 重新提交review
    5. 验证修改结果
  escalation:
    condition: "3次未通过"
    action: "上报CEO裁决"
```

---

## 接口定义

### `review`

执行完整review流程。

**Input:**
```yaml
skill_path: "~/.qclaw/skills/new-skill"
review_type: full
strict_mode: true
max_iterations: 3
```

**Output:**
```yaml
verdict: CONDITIONAL
quality_score: 88
security_score: 92
tech_score: 85
gate_results:
  - gate: G0
    status: PASS
    details: "目录结构正确"
  - gate: G1
    status: PASS
    details: "Frontmatter完整"
  - gate: G2
    status: WARNING
    details: "description建议扩充到100字以上"
  - gate: G3
    status: PASS
    details: "CVSS 5.2，无高危漏洞"
issues:
  - severity: medium
    category: documentation
    description: "description字段较短"
    fix_suggestion: "增加触发场景描述"
iteration_count: 1
review_duration_ms: 45000
```

### `quality-gate-check`

仅执行quality gate检查。

**Input:**
```yaml
skill_path: "string"
gates: [G0, G1, G2, G3]
```

**Output:**
```yaml
overall_pass: false
results:
  - gate: G0
    passed: true
  - gate: G1
    passed: false
    reason: "version字段不符合semver"
```

---

## KPI 仪表板

| 维度 | KPI | 目标值 |
|------|-----|--------|
| 效率 | review响应时间 | ≤ 60秒 |
| 质量 | review准确率 | ≥ 95% |
| 反馈 | 平均修复迭代 | ≤ 1.5次 |
| 通过 | 首次通过率 | ≥ 70% |

---

## 变更日志

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0.0 | 2026-04-15 | 初始版本：G0-G7门禁 + 三重review + 反馈循环 |

---

*本Skill由AI Company CQO开发*  
*作为ai-company-skill-learner的模块组件*
