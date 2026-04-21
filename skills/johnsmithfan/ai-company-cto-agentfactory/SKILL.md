---
name: AI-COMPANY-CTO-AgentFactory
slug: ai-company-cto-agentfactory
version: 1.0.0
description: AI-Company四层Agent标准化生成工具。遵循Harness Engineering三原则，生成符合ClawHub安全规范的Tool/Execution/Management/Decision层Agent。
layer: all
interface:
  input_format: YAML配置文件
  output_format: Agent目录 + SKILL.md + 配置文件
  cli_command: python scripts/generate_agent.py --config <path>
permissions:
  file_write: true
  file_read: true
  network: false
  execute_scripts: false
dependencies:
  runtime:
    - python3.9+
    - pyyaml>=6.0
    - jinja2>=3.0
  skills: []
quality:
  test_coverage: 80
  documentation_score: comprehensive
  validation_gates:
    - schema_validation
    - lint_check
    - security_scan
    - integration_test
metadata:
  standardized: true
  harness_engineering: true
  clawhub_compliant: true
---

# AI-COMPANY-CTO-AgentFactory

## When to Use
- 创建新的AI Agent（任意层级）
- 生成标准化Agent岗位说明书（五要素）
- 设计符合Harness Engineering的Agent架构
- 批量生成四层架构Agent团队

## Core Rules
1. **必须指定Agent层级** — tool/execution/management/decision 四选一
2. **必须包含五要素** — 角色/目标/行为规则/工具权限/容错机制
3. **文件命名kebab-case** — 如 `content-writer-agent`
4. **配置文件YAML格式** — 结构化、可读、可验证
5. **生成后通过质量关卡** — 4道门禁（schema/lint/security/integration）

## Quick Reference
| 文件 | 用途 |
|------|------|
| templates/*-layer.md | 四层模板（Tool/Execution/Management/Decision） |
| scripts/generate_agent.py | Agent生成主脚本 |
| scripts/validate_agent.py | 质量门禁验证脚本 |
| references/*.md | Harness Engineering、质量门禁、安全合规 |

## Usage
```bash
# 生成Agent
python scripts/generate_agent.py --config ./agent-config.yaml --output ./agents/

# 验证质量
python scripts/validate_agent.py --agent-dir ./agents/my-agent/
```

## 四层架构
| 层级 | 职责 | 关键属性 |
|------|------|----------|
| **Tool** | 原子能力 | 无状态、幂等、可复用 |
| **Execution** | 任务执行 | 单一职责、绑定Skills |
| **Management** | 任务编排 | 状态机、错误恢复 |
| **Decision** | 战略决策 | 数据驱动、权威引用 |

## 版本历史
| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-04-16 | 初始版本 |
