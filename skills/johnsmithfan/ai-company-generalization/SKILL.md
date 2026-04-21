---
name: "AI Company Generalization"
slug: "ai-company-generalization"
version: "1.0.0"
homepage: "https://clawhub.com/skills/ai-company-generalization"
description: "AI Company 通用化process Skill — 将组织特定或领域特定的 Skill 转换为可在任意组织/行业/平台运行的通用 Skill。包含特异性identify、参数化、抽象边界、通用接口、跨上下文verify5步process。"
license: MIT-0
tags: [generalization, universalization, ai-company, abstraction, portability, cross-org]
triggers:
  - generalize skill
  - universalize skill
  - remove org-specific
  - make skill portable
  - cross-org adaptation
interface:
  inputs:
    type: object
  outputs:
    type: object
  errors:
    - code: GEN_001
      message: "Cannot identify specificity boundaries"
    - code: GEN_002
      message: "Parameterization failed: circular reference"
    - code: GEN_003
      message: "Universalization introduces unsafe assumptions"
    - code: GEN_004
      message: "Context validation failed"
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
  tags: [generalization, universalization, ai-company, abstraction, portability]
---

# AI Company Generalization — ClawHub Schema v1.0

AI Company 通用化process Skill。将组织特定或领域特定的 Skill 转换为可在任意组织、任意行业、任意平台运行的通用 Skill。

---

## Overview

**通用化（Generalization）** 是 Skill 泛化capability的核心。它消除 Skill 中的组织特定内容、行业假设和平台Constraint，使 Skill 成为1个可以适配任何环境的通用工具。

### Goal

- 消除组织特定引用（公司名称、品牌、API 端点）
- 抽象行业特定逻辑（监管framework、商业模式术语）
- 实现跨平台兼容（操作系统、文件系统、Shell 类型）
- establish参数化配置system
- ensure跨上下文verify通过

### 通用化 vs standard化 vs 模块化

| 维度 | standard化 | 模块化 | 通用化 |
|------|--------|--------|--------|
| **关注点** | 格式compliance | 结构分解 | 泛化capability |
| **问题** | Skill 格式不standard | Skill 结构混乱 | Skill 太特殊 |
| **输出** | 格式compliance的 Skill | 模块化的 Skill | 可移植的 Skill |
| **前置条件** | 无 | 可选 | 建议先standard化 |

**推荐process：** standard化 → 模块化 → 通用化

---

## 通用化5步process

### Step 1 — 特异性identify

**Goal：** 找到 Skill 中所有非通用的部分。

**特异性类型：**

| 类型 | 示例 | detect方法 |
|------|------|---------|
| **Org 特异性** | 公司名、品牌名、特定 URL | 正则匹配已知公司列表 |
| **财务特异性** | 具体金额、货币、时区 | 数值 + 货币正则 |
| **监管特异性** | 具体法律名称、条款号 | 已知法规库匹配 |
| **行业特异性** | 领域术语、垂直假设 | 术语库对比 |
| **平台特异性** | Windows/Linux/macOS 假设 | OS detect代码模式 |
| **文化特异性** | 日期格式、语言习惯 | 格式正则 + i18n detect |
| **技术特异性** | 特定 API 版本、ID 格式 | URL/ID 正则模式 |

**identify扫描规则：**

```python
SPECIFICITY_PATTERNS = {
    'org_name': [
        r'DELLIGHT\.AI', r'Acme Corp', r'StartupXYZ',
        # ... known org names
    ],
    'financial': [
        r'\$\d+[,\d]*',           # $1,000
        r'(USD|EUR|GBP|CNY)\s*\d+',  # currency amounts
        r'(AED|SGD|HKD)\s*[\d,]+',   # regional currencies
    ],
    'regulatory': [
        r'GDPR\s+Article\s+\d+',
        r'Data\s+Security\s+Law\s+Article\s+\d+',
        r'CCPA\s+Section\s+\d+',
    ],
    'platform': [
        r'C:\\Users\\', r'~/.ssh/',
        r'/etc/systemd/',
        r'C:/Program Files/',
    ],
    'date_format': [
        r'\d{4}-\d{2}-\d{2}',  # ISO format is ok
        r'\d{1,2}/\d{1,2}/\d{4}',  # ambiguous
    ],
}

def scan_specificity(skill_content: str) -> list[SpecificityItem]:
    findings = []
    for stype, patterns in SPECIFICITY_PATTERNS.items():
        for pattern in patterns:
            matches = re.finditer(pattern, skill_content, re.IGNORECASE)
            for m in matches:
                findings.append(SpecificityItem(
                    type=stype,
                    value=m.group(),
                    position=m.start(),
                    line=skill_content[:m.start()].count('\n') + 1,
                ))
    return findings
```

### Step 2 — 参数化

**Goal：** 将硬编码值替换为可配置的参数。

**参数化strategy：**

```
硬编码值 → 参数Definition
────────────────────────────────────────────────────────
"DELLIGHT.AI" → {ORG_NAME} 或完全删除
"$5,000" → {MIN_TRANSACTION_AMOUNT: default: 1000}
"US/EU/CN" → {JURISDICTION: allowed: [US, EU, CN, GLOBAL]}
"/home/user/data" → {WORKSPACE_ROOT: default: ./workspace}
```

**参数Definitionstandard：**

```yaml
parameters:
  - name: string              # 参数名称（SCREAMING_SNAKE_CASE）
    type: string | number | boolean | enum | object
    required: boolean
    default: any              # 若非必须，必须有 default
    allowed: string[] | range  # 若为 enum，列出allow值
    description: string        # 参数用途Description
    example: any              # 示例值
    validation: string         # verify规则
    deprecation_notice: string # 若参数即将废弃
```

**参数化质量检查：**

| 检查项 | standard |
|--------|------|
| 所有硬编码值已参数化 | 0 remaining hardcoded values |
| 参数有默认值 | 100% of optional params |
| 参数命名无歧义 | SCREAMING_SNAKE_CASE |
| 参数类型明确 | 有 type + validation |
| 参数示例合理 | 有 example |

### Step 3 — 抽象边界

**Goal：** 区分通用规则与情境化规则，establish扩展点。

**抽象tier：**

| tier | 内容 | 可否移除 |
|------|------|---------|
| **通用核心** | 放之4海皆准的逻辑 | ❌ 不可 |
| **配置层** | 参数化后的配置 | ✅ 可替换 |
| **扩展模块** | 情境化规则（可选）| ✅ 可选 |
| **适配器** | 平台特定适配代码 | ✅ 条件编译 |

**扩展点design：**

```python
# 通用核心（不可修改）
def execute_skill_core(input_data, parameters):
    # 这里只包含通用的业务逻辑
    result = process(input_data, parameters)
    return result

# 扩展点（可选插件）
EXTENSION_POINTS = {
    'pre_process': [],       # 前置handle钩子
    'post_process': [],     # 后置handle钩子
    'validate': [],          # verify钩子
    'format_output': [],    # 输出格式化钩子
}

def execute_with_extensions(input_data, parameters, extensions=None):
    # execute通用核心
    result = execute_skill_core(input_data, parameters)
    
    # execute后置扩展
    if extensions:
        for ext in extensions.get('post_process', []):
            result = ext(result)
    
    return result
```

**通用规则（必须保留）：**

- ✅ 错误handleprinciple
- ✅ 日志recordstandard
- ✅ 接口契约（输入/输出格式）
- ✅ permission边界
- ✅ data脱敏要求

**情境化规则（应抽取为扩展）：**

- ❌ 具体监管条款文本
- ❌ 特定行业的 KPI threshold
- ❌ 特定文化的沟通Style
- ❌ 特定平台的命令语法

### Step 4 — 通用接口design

**Goal：** 接口本身不依赖任何特定上下文。

**平台中立principle：**

| 维度 | ❌ 避免 | ✅ 推荐 |
|------|--------|--------|
| 文件系统 | `C:\`, `/home/` | `{WORKSPACE}/`, `./` |
| 时间 | 硬编码时区 | UTC + 参数化时区 |
| 货币 | 固定货币符号 | `{CURRENCY}` 参数 |
| 数量 | 固定单位 | `{UNIT}` 参数 |
| 日期 | MM/DD/YYYY | ISO 8601 |
| 语言 | 硬编码中文/英文 | i18n key 系统 |
| API | 硬编码 URL | `{API_BASE_URL}` 参数 |

**通用输出格式：**

```yaml
output:
  status: success | error
  data: any           # 泛型，不依赖具体结构
  metadata:
    timestamp: ISO8601  # UTC 时间戳
    skill_version: semver
    context_id: string  # 本次execute唯1 ID
    locale: string       # 输出语言标记
  errors:
    - code: string
      message: string   # 国际化 key，非硬编码文本
      context: object   # 调试上下文
```

### Step 5 — 跨上下文verify

**Goal：** ensure通用化后的 Skill 在至少 2 个不同上下文中可正常运行。

**verifyframework：**

```python
def cross_context_validate(
    generalized_skill_path: str,
    test_contexts: list[TestContext]
) -> ValidationReport:
    
    results = []
    for ctx in test_contexts:
        # 设置上下文参数
        ctx_params = ctx.default_parameters
        
        # execute Skill
        result = execute_skill(
            skill_path=generalized_skill_path,
            test_input=ctx.test_input,
            parameters=ctx_params,
        )
        
        # verify结果
        validation = validate_result(
            result=result,
            expected=ctx.expected_output,
            context=ctx,
        )
        
        results.append({
            'context': ctx.name,
            'compatible': validation.compatible,
            'issues': validation.issues,
            'score': validation.score,
        })
    
    # 汇总
    overall_score = mean([r['score'] for r in results])
    
    return ValidationReport(
        universal_score=overall_score,
        context_results=results,
        compatibility_matrix=build_matrix(results),
        failed_contexts=[r for r in results if not r['compatible']],
    )
```

**测试上下文示例：**

```yaml
test_contexts:
  - name: Startup_US
    description: "美国初创公司，英文，无监管framework"
    parameters:
      LANGUAGE: en
      CURRENCY: USD
      JURISDICTION: US
      REGULATORY_FRAMEWORK: none
    test_input: {sample: data}
    expected_status: success
  
  - name: Enterprise_EU
    description: "欧盟企业，GDPR compliance，欧元"
    parameters:
      LANGUAGE: de
      CURRENCY: EUR
      JURISDICTION: EU
      REGULATORY_FRAMEWORK: GDPR
    test_input: {sample: data}
    expected_status: success
  
  - name: Government_CN
    description: "中国政府机构，中文，人民币"
    parameters:
      LANGUAGE: zh-CN
      CURRENCY: CNY
      JURISDICTION: CN
      REGULATORY_FRAMEWORK: DSL
    test_input: {sample: data}
    expected_status: success
```

---

## 通用化等级

| 等级 | 名称 | Description | 适用场景 |
|------|------|------|---------|
| **L1** | Org-agnostic | 适用于任意组织 | 通用工具类 |
| **L2** | Domain-agnostic | 适用于任意行业 | 平台型 Skill |
| **L3** | Culture-agnostic | 跨语言/文化 | 国际deploy |
| **L4** | Platform-agnostic | 跨操作系统 | 全平台支持 |
| **L5** | 完全 Universal | 无任何外部假设 | 开源publish |

---

## 接口Definition

### `generalize-skill`

通用化Goal Skill。

**Input:**

```yaml
skill_path: string
target_level: L1 | L2 | L3 | L4 | L5
preserve_org_hooks: boolean  # 若 true，保留可选的 org 扩展点
strict_parameterization: boolean  # 若 true，不allow任何硬编码
```

**Output:**

```yaml
status: success | failed
original_skill_path: string
generalization_level: string
specificity_found:
  - type: org_name | financial | regulatory | platform | cultural | technical
    value: string
    location: string
    severity: high | medium | low
parameters_extracted:
  - name: string
    type: string
    default: any
    allowed: any[]
    description: string
org_hooks_preserved: string[]   # 若 preserve_org_hooks=true
remaining_assumptions: string[]
generalization_ratio: 0-1        # 0 = 完全特化, 1 = 完全通用化
```

### `test-generalization`

跨上下文verify通用化结果。

**Input:**

```yaml
generalized_skill_path: string
test_contexts:
  - name: string
    parameters: object
    test_input: object
    expected_output: object
```

**Output:**

```yaml
universal_score: 0-100
context_results:
  - context: string
    compatible: boolean
    score: 0-100
    issues: string[]
    warnings: string[]
compatibility_matrix: object
recommendation: pass | conditional_pass | fail
conditional_requirements: string[]  # 若 conditional_pass
```

### `reverse-generalize`

将通用 Skill 适配到特定组织。

**Input:**

```yaml
generalized_skill_path: string
target_org: string              # Goal组织名称
target_context: object          # Goal上下文参数
```

**Output:**

```yaml
adapted_skill_path: string
parameters_set:
  - name: string
    value: any
    source: original_default | configured | derived
validation_report: object
warnings: string[]
```

---

## KPI 仪表板

| metric | Goal | 测量方式 |
|------|------|---------|
| 通用化率 | ≥ 80% | (1 - 特异性行数/总行数) × 100 |
| 参数coverage | ≥ 90% | (已参数化值/所有配置值) × 100 |
| 跨上下文通过率 | ≥ 3/3 | 测试上下文数量 |
| 无 org 残留 | 100% | 正则扫描 org 名称 |
| 文档完整性 | 100% | 所有参数有 description |

---

## Change Log

| 版本 | 日期 | Changes |
|------|------|---------|
| 1.0.0 | 2026-04-14 | Initial version：5步通用化process + 5级等级system + 跨上下文verify |
