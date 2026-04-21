# Harness Engineering Principles

> AI-Company Agent Factory 的设计哲学

## 三原则

### 1. 标准化 (Standardization)

**定义**: 统一的接口、格式、命名规范

**实践**:
- 所有Agent使用统一的Frontmatter Schema
- 统一的错误码体系
- 统一的输入输出JSON Schema
- 统一的命名规范（kebab-case）

**收益**:
- 降低学习成本
- 提高可维护性
- 便于工具链集成

---

### 2. 模块化 (Modularity)

**定义**: 每个组件独立可替换，低耦合高内聚

**实践**:
- Tool层：原子能力，单一职责
- Execution层：Worker绑定特定Skills
- Management层：Orchestrator协调Workers
- Decision层：C-Suite跨部门协调

**收益**:
- 独立开发、测试、部署
- 故障隔离
- 灵活组合

---

### 3. 通用化 (Generalization)

**定义**: 适用于所有四层Agent，不针对特定业务

**实践**:
- 模板参数化，配置驱动
- 禁止硬编码业务逻辑
- 抽象通用模式

**收益**:
- 复用性高
- 适应变化
- 减少重复开发

---

## 四层架构映射

| 层级 | 标准化 | 模块化 | 通用化 |
|------|--------|--------|--------|
| **Tool** | 统一接口Schema | 原子能力 | 领域无关 |
| **Execution** | 五要素模板 | Worker-Skill绑定 | 任务类型无关 |
| **Management** | 状态机规范 | Orchestrator-Worker协调 | 业务流程无关 |
| **Decision** | 决策框架 | C-Suite职责域 | 行业无关 |

---

## 质量门禁

Harness Engineering通过4道质量门禁保障：

| 门禁 | 检查内容 | 工具 |
|------|----------|------|
| G1 | Schema验证 | JSON Schema |
| G2 | Lint检查 | yamllint, markdownlint |
| G3 | 安全扫描 | bandit, safety |
| G4 | 集成测试 | pytest |

---

## 反模式

| 反模式 | 问题 | 正确做法 |
|--------|------|----------|
| 硬编码业务逻辑 | 无法复用 | 配置驱动 |
| 跨层耦合 | 难以维护 | 层间通过接口通信 |
| 状态泄露 | 并发问题 | 状态机管理 |
| 职责不清 | 重复/遗漏 | 单一职责 |

---

## 参考

- [The Twelve-Factor App](https://12factor.net/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
