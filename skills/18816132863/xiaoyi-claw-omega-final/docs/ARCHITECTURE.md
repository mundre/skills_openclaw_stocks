# 六层主架构 - 唯一真源

## V2.8.0 - 2026-04-10

本文档是架构的唯一权威定义，所有运行逻辑以此为准。

---

## 架构定义

| 层级 | 名称 | 职责 | 入口模块 |
|------|------|------|----------|
| L1 | Core | 核心认知、提示词 | core/prompt_integration.py |
| L2 | Memory | 记忆上下文 | memory_context/memory_manager.py |
| L3 | Orchestration | 任务编排 | orchestration/task_engine.py |
| L4 | Execution | 技能执行 | execution/skill_adapter_gateway.py |
| L5 | Governance | 治理审计 | governance/security/auth_integration.py |
| L6 | Infrastructure | 基础设施 | infrastructure/integration.py |

---

## 唯一真源清单

### 主架构定义
- **本文档**: core/ARCHITECTURE.md

### 运行入口
- **统一入口**: infrastructure/integration.py

### 注册体系
- **技能注册**: infrastructure/inventory/skill_registry.json
- **组件注册**: infrastructure/COMPONENT_REGISTRY.json

### 主运行时读取源
- core/AGENTS.md
- core/TOOLS.md
- core/IDENTITY.md
- core/SOUL.md
- core/USER.md
- core/HEARTBEAT.md

---

## 兼容/废弃层（不参与主运行）

以下内容已废弃，仅作兼容保留：

- infrastructure/SKILL_REGISTRY.json → 已被 inventory/skill_registry.json 替代
- infrastructure/CAPABILITY_REGISTRY.json → 已废弃
- README.md 旧架构口径 → 已废弃
- core/clean_arch/ → 已废弃
- core/ddd/ → 已废弃
- core/hexagonal/ → 已废弃
- core/microservice/ → 已废弃
- core/service_mesh/ → 已废弃

---

## 层级编号规则

统一使用 L1-L6 编号：
- L1 = Core（核心层）
- L2 = Memory（记忆层）
- L3 = Orchestration（编排层）
- L4 = Execution（执行层）
- L5 = Governance（治理层）
- L6 = Infrastructure（基建层）

禁止使用其他层级编号体系。

---

**版本**: V2.8.0
**更新**: 2026-04-10
**状态**: 唯一真源
