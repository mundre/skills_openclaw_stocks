---
name: "AI Company Modularization"
slug: "ai-company-modularization"
version: "1.0.0"
homepage: "https://clawhub.com/skills/ai-company-modularization"
description: "AI Company 模块化流程 Skill — 将单体式 Skill 分解为原子化、可独立测试、可组合的模块单元。包含模块边界识别、接口定义、共享逻辑提取、独立版本控制六步流程。"
license: MIT-0
tags: [modularization, decomposition, ai-company, architecture, modules, composition]
triggers:
  - modularize skill
  - decompose skill
  - extract modules
  - split skill
  - module architecture
interface:
  inputs:
    type: object
  outputs:
    type: object
  errors:
    - code: MOD_001
      message: "Module boundary conflict"
    - code: MOD_002
      message: "Circular dependency detected"
    - code: MOD_003
      message: "Shared logic extraction failed"
    - code: MOD_004
      message: "Interface contract violation"
permissions:
  files: [read/write skills/]
  network: []
  commands: []
  mcp: []
dependencies:
  skills: [ai-company-hq, skill-vetter, ai-company-standardization]
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
  tags: [modularization, decomposition, ai-company, architecture, modules]
---

# AI Company Modularization — ClawHub Schema v1.0

AI Company 模块化流程 Skill。将单体式 Skill 分解为原子化、可独立测试、可组合的模块单元。

---

## 概述

**模块化（Modularization）** 是 Skill 架构演进的关键步骤。它将一个大的、复杂的 Skill 分解为多个小的、专注的模块，每个模块：

- 独立负责一个明确的功能
- 有清晰的输入/输出接口
- 可以独立测试和版本控制
- 可以被其他模块或 Skill 复用

### 目标

- 将单体 Skill 分解为可独立管理的模块
- 消除模块间隐藏依赖（spaghetti coupling）
- 实现模块级独立测试
- 支持模块级版本控制和独立发布
- 为 Skill 组合（composition）提供基础

### 模块化原则

| 原则 | 说明 |
|------|------|
| 单一职责 | 每个模块只做一件事，且做好 |
| 接口隔离 | 模块间通过接口通信，不暴露内部实现 |
| 无循环依赖 | 模块依赖图必须是有向无环图（DAG）|
| 可独立测试 | 每个模块可脱离其他模块单独测试 |
| 版本独立 | 模块版本与 Skill 版本解耦 |

---

## 模块化六步流程

### Step 1 — 模块边界识别

**目标：** 找到 Skill 中自然的功能边界。

**方法：**

1. **职责分析**：列出 Skill 中所有功能点
2. **变更频率分析**：哪些功能经常一起变更？哪些独立变化？
3. **复用分析**：哪些功能可能被其他 Skill 复用？
4. **边界绘制**：画出功能依赖图，识别自然切割点

**识别启发式规则：**

```
✅ 自然模块边界：
  - 完全不同的输入类型 → 独立模块
  - 完全不同的输出类型 → 独立模块
  - 不同的更新频率 → 独立模块
  - 可被其他 Skill 复用 → 优先拆分为模块

❌ 不应拆分：
  - 只是代码长，但没有功能差异 → 不要拆分
  - 两个功能紧耦合无法独立 → 保持单体
  - 拆分后模块 < 50 行 → 合并而非拆分
```

### Step 2 — 接口定义

每个模块必须定义清晰的接口：

```yaml
module_name:
  description: string
  version: semver
  inputs:
    param1:
      type: string | number | boolean | object | array
      required: boolean
      description: string
      default?: any
      validation?: string  # e.g. "range: 0-100"
  outputs:
    result:
      type: object
      description: string
      schema: string  # JSON Schema
  errors:
    - code: MODULE_001
      cause: string
      remediation: string
  side_effects: string[]  # 文件系统/网络/状态变更
```

**接口设计原则：**

- 输入参数类型明确，无隐式类型转换
- 输出结构完整描述，有 JSON Schema
- 错误码统一前缀：`{MODULE_ABBR}_{CODE}`
- 避免副作用；若不可避免，明确声明

### Step 3 — 依赖分析

**构建模块依赖图：**

```python
def build_dependency_graph(modules: list[Module]) -> DependencyGraph:
    graph = {}
    for module in modules:
        deps = []
        for dep in module.imports:
            if dep in all_modules:
                deps.append(dep)
        graph[module.name] = deps
    
    # 检测循环依赖
    cycles = detect_cycles(graph)
    if cycles:
        raise MOD_002(f"Circular dependency: {' -> '.join(cycles)}")
    
    return graph
```

**依赖耦合度评分：**

| 耦合类型 | 分数 | 说明 |
|---------|------|------|
| 无耦合 | 0 | 完全独立 |
| 数据耦合 | 1 | 仅通过参数传递数据 |
| 特征耦合 | 2 | 共享数据结构 |
| 控制耦合 | 3 | 一个模块控制另一个 |
| 公共耦合 | 4 | 共享全局数据 |
| 内容耦合 | 5 | 直接访问另一模块内部 |

**目标：** 所有模块间依赖 ≤ 特征耦合（分数 ≤ 2）

### Step 4 — 共享逻辑提取

**目标：** 消除重复代码，建立可复用工具库。

**提取策略：**

```python
def extract_shared_logic(modules: list[Module], threshold: float = 0.3) -> list[SharedModule]:
    """
    threshold: 若代码重复率 > threshold，触发提取
    """
    shared = []
    duplication_map = find_duplication(modules)
    
    for dup_set in duplication_map:
        if dup_set.duplication_ratio > threshold:
            shared_module = SharedModule(
                name=dup_set.common_name,
                code=dup_set.extracted_code,
                used_by=[m.name for m in dup_set.affected_modules],
                interface=dup_set.shared_interface,
            )
            shared.append(shared_module)
            # 从各模块中移除重复代码，替换为调用
    
    return shared
```

**共享模块命名规范：**

| 用途 | 命名规范 | 示例 |
|------|---------|------|
| 工具函数 | `utils-{domain}` | `utils-file-parser` |
| 数据结构 | `types-{domain}` | `types-compliance` |
| 验证逻辑 | `validate-{scope}` | `validate-semver` |
| 模板引擎 | `template-{format}` | `template-yaml` |

### Step 5 — 目录结构

```
{skill-name}/
├── SKILL.md              # 主 Skill（编排模块）
├── MODULES.md            # 模块索引 + 依赖图
├── modules/
│   ├── module-alpha/
│   │   ├── module.md      # 模块定义 + 接口
│   │   └── tests/
│   │       └── module-alpha.test.yaml  # 模块级测试
│   ├── module-beta/
│   │   ├── module.md
│   │   └── tests/
│   │       └── module-beta.test.yaml
│   └── shared/
│       ├── utils/
│       │   └── shared-utils.md
│       └── types/
│           └── shared-types.md
├── scripts/               # 可执行脚本（如有）
│   └── run-module-alpha.sh
└── references/
    ├── architecture.md    # 模块架构文档
    └── dependency-graph.dot
```

**每个 `module.md` 的最小内容：**

```yaml
# Module: {module-name}

## Version
{module_version}

## Responsibility
{一句话描述模块负责什么}

## Interface
{inputs/outputs/errors YAML}

## Dependencies
{external_modules_required}

## Provides
{what_this_module_provides_to_other_modules}

## Test Coverage
{covered_test_cases}

## Known Limitations
{边界情况/已知问题}
```

### Step 6 — 测试与集成

**模块级测试套件（YAML）：**

```yaml
# module-alpha.test.yaml
module: module-alpha
version: "1.0.0"
test_cases:
  - name: happy_path
    input:
      param1: valid_value
    expected:
      status: success
      result: expected_output
  
  - name: edge_case_null
    input:
      param1: null
    expected:
      status: error
      code: MODULE_003
  
  - name: invalid_input_type
    input:
      param1: 999
    expected:
      status: error
      code: MODULE_002
```

**集成测试策略：**

| 测试类型 | 覆盖范围 | 执行频率 |
|---------|---------|---------|
| 模块单元测试 | 每个模块独立运行 | 每次 PR |
| 模块间接口测试 | 模块边界契约验证 | 每次 PR |
| 端到端集成测试 | 完整 Skill 执行路径 | 每次发布 |
| 回归测试套件 | 100 条黄金输入 | 每次发布 |

---

## 接口定义

### `decompose-skill`

将单体 Skill 分解为模块。

**Input:**

```yaml
skill_path: string                    # 目标 Skill 路径
proposed_modules: string[] | null     # 建议的模块名称列表，null = 自动识别
shared_threshold: number              # 0-1，重复率 > 此值则提取共享模块
```

**Output:**

```yaml
status: success | failed
skill_name: string
proposed_modules:
  - name: string
    size_lines: number
    responsibility: string
    interface: object
    dependencies: string[]
    cohesion_score: 0-100
    coupling_score: 0-100
shared_modules:
  - name: string
    extracted_from: string[]
    duplication_ratio: 0-1
    interface: object
dependency_graph: object
warnings:
  - message: string
    severity: high | medium | low
    suggestion: string
estimated_modularization_effort: string  # e.g. "2-3 hours"
```

### `compose-modules`

将多个模块组合为复合 Skill。

**Input:**

```yaml
module_paths: string[]                # 模块 .md 文件路径列表
skill_name: string                    # 生成的 Skill 名称
orchestration_order: string[] | null  # 执行顺序，null = 自动推导
```

**Output:**

```yaml
composite_skill_path: string
interface_contracts:
  - module_a: string
    module_b: string
    contract_valid: boolean
    conflicts: string[]
generated_orchestrator: object
test_coverage: number
warnings: string[]
```

### `extract-shared`

从多个模块中提取共享逻辑。

**Input:**

```yaml
module_paths: string[]
extraction_type: utils | types | validators | templates
naming_convention: string  # 命名规范
```

**Output:**

```yaml
shared_module:
  name: string
  path: string
  size_lines: number
  used_by: string[]
  deduplication_saved: number  # 减少的重复代码行数
updated_modules: string[]
interface: object
```

### `validate-modularization`

验证模块化结果的质量。

**Input:**

```yaml
modularized_skill_path: string
strict: boolean  # 若 true，耦合度 > 2 即报错
```

**Output:**

```yaml
valid: boolean
scores:
  modularity: 0-100
  cohesion: 0-100
  coupling: 0-100
  testability: 0-100
issues:
  - type: circular_dependency | high_coupling | low_cohesion | missing_interface
    modules: string[]
    message: string
    fix: string
compliance:
  no_circular_deps: boolean
  all_interfaces_defined: boolean
  all_modules_tested: boolean
```

---

## 模块化质量评分

| 维度 | 权重 | 0分 | 50分 | 100分 |
|------|------|------|------|-------|
| 模块化程度 | 25% | 单体（未拆分）| 部分拆分 | 完全模块化 |
| 内聚度 | 25% | 随机混合 | 合理分组 | 单一职责 |
| 耦合度 | 25% | 内容耦合 | 特征耦合 | 数据耦合 |
| 可测试性 | 15% | 无法独立测试 | 部分可测试 | 100% 可独立测试 |
| 接口清晰度 | 10% | 无接口定义 | 部分定义 | 完整 typed 接口 |

---

## 变更日志

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 1.0.0 | 2026-04-14 | 初始版本：六步模块化流程 + 接口定义 + 质量评分 |
