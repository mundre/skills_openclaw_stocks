---
name: "AI Company CMO Skill Discovery"
slug: ai-company-cmo-skill-discovery
version: 1.0.0
homepage: https://clawhub.com/skills/ai-company-cmo-skill-discovery
description: |
  AI Company CMOskilldiscovery模块。多平台skill搜索、评估、排序，为skilllearning流程提供高质量候选skill清单。
  触发关键词：skill搜索、discoveryskill、查找skill、搜索skill包
license: MIT-0
tags: [ai-company, cmo, discovery, search, skill-finder]
triggers:
  - skill搜索
  - discoveryskill
  - 查找skill
  - 搜索skill包
  - skill discovery
  - find skill
interface:
  inputs:
    type: object
    schema:
      type: object
      properties:
        query:
          type: string
          description: 搜索关键词
        platforms:
          type: array
          items:
            type: string
            enum: [clawhub, github, npm, pypi, web]
          default: [clawhub, github]
        max_results:
          type: integer
          default: 10
        filters:
          type: object
          properties:
            min_quality_score:
              type: integer
              default: 70
            min_stars:
              type: integer
              default: 10
            license:
              type: string
              default: "MIT"
      required: [query]
  outputs:
    type: object
    schema:
      type: object
      properties:
        total_found:
          type: integer
        results:
          type: array
          items:
            type: object
            properties:
              name:
                type: string
              source:
                type: string
              url:
                type: string
              description:
                type: string
              relevance_score:
                type: number
              quality_pre_score:
                type: number
              tech_compatibility:
                type: number
              ranking:
                type: integer
        search_metadata:
          type: object
          properties:
            duration_ms:
              type: integer
            platforms_searched:
              type: array
            timestamp:
              type: string
      required: [total_found, results]
  errors:
    - code: DISCOVERY_001
      message: "Query not specified"
    - code: DISCOVERY_002
      message: "No results found"
    - code: DISCOVERY_003
      message: "Platform API error"
    - code: DISCOVERY_004
      message: "Rate limit exceeded"
permissions:
  files: [read]
  network: [api]
  commands: []
  mcp: [clawhub]
dependencies:
  skills:
    - ai-company-hq
    - ai-company-kb
    - ai-company-cmo
  cli: [clawhub]
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
  tags: [ai-company, cmo, discovery, search]
---

# AI Company CMO Skill Discovery v1.0

> CMO主导的skilldiscovery模块。多平台搜索、智能评估、优先级排序。

---

## 概述

**ai-company-cmo-skill-discovery** 是AIskilllearning流程的第一阶段模块，负责：

1. **多平台搜索**: 同时搜索ClawHub、GitHub、NPM、PyPI等平台
2. **智能评估**: 基于技术兼容性和质量预评估打分
3. **优先级排序**: 综合评分排序，输出高质量候选清单

---

## 核心功能

### Module 1: 多平台搜索

**功能**: 并行搜索多个skill平台

| 平台 | 搜索方式 | 权重 |
|------|----------|------|
| ClawHub | clawhub CLI | 40% |
| GitHub | GitHub API | 30% |
| NPM | NPM Registry API | 15% |
| PyPI | PyPI JSON API | 15% |

### Module 2: 智能评估

**功能**: 多维度评估候选skill

```yaml
evaluation_dimensions:
  relevance:
    weight: 40%
    factors:
      - 关键词匹配度
      - 描述相关性
      - 标签匹配度
  
  quality_preliminary:
    weight: 40%
    factors:
      - 文档完整性
      - 社区活跃度
      - 版本更新频率
      - 测试覆盖率(如有)
  
  tech_compatibility:
    weight: 20%
    factors:
      - 技术栈匹配
      - 依赖复杂度
      - 平台兼容性
```

### Module 3: 排序算法

**功能**: 加权评分排序

```python
def calculate_score(skill):
    return (
        skill.relevance_score * 0.4 +
        skill.quality_pre_score * 0.4 +
        skill.tech_compatibility * 0.2
    )
```

---

## 接口定义

### `search`

执行多平台skill搜索。

**Input:**
```yaml
query: "PDF处理"
platforms: ["clawhub", "github"]
max_results: 10
filters:
  min_quality_score: 70
  min_stars: 10
  license: "MIT"
```

**Output:**
```yaml
total_found: 25
results:
  - name: "pdf-processor"
    source: "clawhub"
    url: "https://clawhub.com/skills/pdf-processor"
    description: "PDF处理skill，支持合并、拆分、旋转"
    relevance_score: 95
    quality_pre_score: 88
    tech_compatibility: 92
    ranking: 1
  - name: "pdf-toolkit"
    source: "github"
    url: "https://github.com/user/pdf-toolkit"
    description: "Python PDF处理工具"
    relevance_score: 85
    quality_pre_score: 75
    tech_compatibility: 80
    ranking: 2
search_metadata:
  duration_ms: 1250
  platforms_searched: ["clawhub", "github"]
  timestamp: "2026-04-15T02:50:00Z"
```

### `evaluate`

评估指定skill的质量。

**Input:**
```yaml
skill_url: "string"
evaluation_depth: "quick|deep"
```

**Output:**
```yaml
quality_score: 0-100
factors:
  documentation: 0-100
  community: 0-100
  maintenance: 0-100
  testing: 0-100
recommendation: "highly_recommended|recommended|neutral|not_recommended"
```

---

## KPI 仪表板

| 维度 | KPI | 目标值 |
|------|-----|--------|
| 效率 | 搜索响应时间 | ≤ 2秒 |
| 覆盖 | 平台覆盖率 | 100% |
| 质量 | 结果相关性 | ≥ 85% |
| 准确 | 评估准确率 | ≥ 80% |

---

## 变更日志

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0.0 | 2026-04-15 | 初始版本：多平台搜索 + 智能评估 + 排序 |

---

*本Skill由AI Company CMO开发*  
*作为ai-company-skill-learner的模块组件*
