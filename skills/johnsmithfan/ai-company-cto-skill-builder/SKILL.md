---
name: "AI Company CTO Skill Builder"
slug: ai-company-cto-skill-builder
version: 1.0.0
homepage: https://clawhub.com/skills/ai-company-cto-skill-builder
description: |
  AI Company CTOskillbuild模块。执行skilllearning流程的技术层面：目录初始化、SKILL.md编写、脚本开发、模块化、通用化。
  触发关键词：buildskill、开发skill、技术实现
license: MIT-0
tags: [ai-company, cto, builder, skill-development, technical]
triggers:
  - buildskill
  - 开发skill
  - 技术实现
  - skill开发
  - skill builder
  - develop skill
interface:
  inputs:
    type: object
    schema:
      type: object
      properties:
        action:
          type: string
          enum: [create, modularize, generalize, analyze]
          description: 执行动作
        skill_name:
          type: string
          description: skill名称 (kebab-case)
        topic:
          type: string
          description: skill主题/领域
        target_level:
          type: string
          enum: [L1, L2, L3, L4, L5]
          default: L3
          description: 通用化目标等级
        source_skill_path:
          type: string
          description: 源skill路径 (modularize/generalize时)
      required: [action, skill_name]
  outputs:
    type: object
    schema:
      type: object
      properties:
        status:
          type: string
          enum: [success, failed, partial]
        skill_path:
          type: string
        artifacts_created:
          type: array
          items:
            type: string
        technical_assessment:
          type: object
          properties:
            architecture_score:
              type: number
            interface_score:
              type: number
            extensibility_score:
              type: number
            tech_risks:
              type: array
              items:
                type: string
        generalization_report:
          type: object
      required: [status]
  errors:
    - code: BUILDER_001
      message: "Invalid skill name format"
    - code: BUILDER_002
      message: "Skill directory already exists"
    - code: BUILDER_003
      message: "Failed to create SKILL.md"
    - code: BUILDER_004
      message: "Module boundary detection failed"
    - code: BUILDER_005
      message: "Generalization introduced unsafe assumptions"
permissions:
  files: [read, write]
  network: []
  commands: []
  mcp: []
dependencies:
  skills:
    - ai-company-hq
    - ai-company-kb
    - ai-company-standardization
    - ai-company-modularization
    - ai-company-generalization
    - ai-company-cqo-skill-reviewer
  cli: []
quality:
  saST: Pass
  vetter: Approved
  idempotent: false
metadata:
  category: technical
  layer: AGENT
  cluster: ai-company
  maturity: STABLE
  license: MIT-0
  standardized: true
  tags: [ai-company, cto, builder, skill-development]
---

# AI Company CTO Skill Builder v1.0

> CTO主导的skillbuild模块。目录初始化、SKILL.md编写、脚本开发、模块化、通用化。

---

## 概述

**ai-company-cto-skill-builder** 是AIskilllearning流程的核心技术模块，负责：

1. **skill创建**: 从零build完整Skill目录
2. **模块化**: 边界识别、接口定义、依赖分析
3. **通用化**: 特异性消除、参数化、跨上下文验证

---

## Module 1: skill创建

### 目录结构

```
{skill_name}/
├── SKILL.md                    # 主skill定义
├── scripts/
│   ├── {action_1}.py          # 动作脚本1
│   ├── {action_2}.py          # 动作脚本2
│   └── utils/
│       ├── __init__.py
│       └── helpers.py          # 共享工具
├── docs/
│   └── README.md               # 可选文档
└── tests/
    └── test_{skill_name}.py    # 测试文件
```

### SKILL.md模板

```yaml
---
name: {skill_name}
slug: {skill_name}
version: 1.0.0
homepage: https://clawhub.com/skills/{skill_name}
description: |
  skill描述 (≥50字，包含触发场景)
license: MIT-0
tags: []
triggers: []
interface:
  inputs: {}
  outputs: {}
  errors: []
permissions:
  files: []
  network: []
  commands: []
  mcp: []
dependencies:
  skills: []
  cli: []
quality:
  saST: Pass
  vetter: Approved
  idempotent: true
metadata:
  category: functional
  layer: FUNCTIONAL
  cluster: ai-company
  maturity: STABLE
  license: MIT-0
  standardized: true
  tags: []
---
```

---

## Module 2: 模块化

### 边界识别

```python
def identify_module_boundaries(skill_content: str) -> list[Module]:
    """
    识别skill中的功能边界
    原则：
    - 单一职责：一个模块做一件事
    - 高内聚：模块内部元素紧密相关
    - 低耦合：模块之间依赖最小化
    """
    # 基于代码结构分析
    # 识别函数/类分组
    # 建立模块边界
    return modules
```

### 接口定义

```yaml
module_interfaces:
  - name: "ModuleName"
    type: "functional|agent|utility"
    inputs:
      - name: param1
        type: string
        required: true
    outputs:
      - name: result
        type: object
    dependencies:
      - other_module
    exports:
      - function1
      - function2
```

---

## Module 3: 通用化

### 特异性消除

| 类型 | 消除策略 |
|------|----------|
| Org特异性 | 替换为参数 |
| 财务特异性 | 替换为变量 |
| 监管特异性 | 抽取为扩展点 |
| 平台特异性 | 抽象为适配器 |
| 文化特异性 | i18n key系统 |

### 参数化体系

```yaml
parameters:
  - name: ORG_NAME
    type: string
    default: "AICompany"
    description: 组织名称
  
  - name: WORKSPACE_ROOT
    type: string
    default: "./workspace"
    description: 工作空间根目录
  
  - name: LOCALE
    type: enum
    default: "en"
    allowed: [en, zh-CN, zh-TW, ja, ko]
    description: 输出语言
```

---

## 接口定义

### `create`

创建新Skill。

**Input:**
```yaml
action: create
skill_name: "my-awesome-skill"
topic: "PDF处理"
```

**Output:**
```yaml
status: success
skill_path: "~/.qclaw/skills/my-awesome-skill"
artifacts_created:
  - "SKILL.md"
  - "scripts/action_1.py"
  - "scripts/action_2.py"
  - "scripts/utils/__init__.py"
  - "scripts/utils/helpers.py"
technical_assessment:
  architecture_score: 92
  interface_score: 88
  extensibility_score: 85
  tech_risks: []
```

### `modularize`

模块化现有Skill。

**Input:**
```yaml
action: modularize
skill_name: "existing-skill"
source_skill_path: "~/.qclaw/skills/existing-skill"
```

**Output:**
```yaml
status: success
modules:
  - name: "core"
    functions: ["execute", "validate"]
    boundary_score: 95
  - name: "utils"
    functions: ["format_output", "parse_input"]
    boundary_score: 88
interface_contracts:
  - module: "core"
    public_api: ["execute(input, params)", "validate(input)"]
    dependencies: ["utils"]
```

### `generalize`

通用化模块化Skill。

**Input:**
```yaml
action: generalize
skill_name: "specific-skill"
source_skill_path: "~/.qclaw/skills/specific-skill"
target_level: L3
```

**Output:**
```yaml
status: success
generalization_report:
  level_achieved: L3
  specificity_removed:
    - type: org_name
      count: 3
    - type: platform
      count: 1
  parameters_extracted: 8
  universalization_score: 85
  test_contexts_passed: 3/3
```

---

## KPI 仪表板

| 维度 | KPI | 目标值 |
|------|-----|--------|
| 效率 | 创建时间 | ≤ 5分钟 |
| 质量 | 架构评分 | ≥ 85 |
| 模块化 | 边界清晰度 | ≥ 90% |
| 通用化 | 跨上下文通过 | 100% |

---

## 变更日志

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0.0 | 2026-04-15 | 初始版本：创建+模块化+通用化 |

---

*本Skill由AI Company CTO开发*  
*作为ai-company-skill-learner的模块组件*
