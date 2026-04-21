# AI-Company Agent Factory — 设计规范汇总

## 生成时间
2026-04-16 18:48 GMT+8

## 设计来源
- skill-structure-design ✅ 完整
- ciso-security-design ⚠️ 部分（超时）
- cto-layer-design ⚠️ 部分（超时）

## 四层架构定义

### 工具层 (Tool Layer) — L0
原子能力单元，无状态，可复用。符合 Harness Engineering 三原则。

**5步生成流程：**
1. 需求原子化 — 分解为最小不可分割单元
2. 接口标准化 — 定义统一 schema、错误码
3. 实现与单元测试 — 覆盖率 ≥90%，黄金测试集 ≥50条
4. 质量门禁审查 — lint + 安全扫描 + 依赖审计
5. 发布与注册 — 语义化版本，Registry 可发现

**必填字段：**
- skill_id, version, description
- input_schema, output_schema
- error_codes, dependencies, permissions
- sla, stateless, test_coverage_pct
- golden_test_count, license, changelog

**质量门禁 (G0-1~G0-5)：**
- 无状态验证（100% 幂等）
- 接口合规性（0缺失字段）
- 测试覆盖率（≥90%，黄金100%）
- 安全扫描（Critical/High=0）
- 性能基准（P95≤500ms，可用性≥99.9%）

**示例：** pdf, xlsx, weather, ai-skill-optimizer, ai-skill-maintainer

---

### 执行层 (Execution Layer) — L1
执行具体业务任务的 Worker Agent。调用工具层 Skills 完成原子任务。

**5步生成流程：**
1. 任务域定义 — 明确边界、输入输出契约
2. Prompt 工程与技能绑定 — System Prompt + Skills 绑定
3. 集成测试与幂等验证 — 端到端测试，重复执行一致性
4. 质量门禁审查 — KPI + 幻觉率 + 安全合规 + 并发安全
5. 部署与注册 — 声明依赖、SLA、监控指标、熔断阈值

**必填字段：**
- agent_id, version, layer='execution'
- role, objective_kpi, behavior_rules
- tool_permissions, error_handling
- idempotent, parallel_safe
- input_contract, output_contract
- sla, monitoring

**质量门禁 (G1-1~G1-6)：**
- 单一职责验证（职责域数=1）
- 幂等性验证（一致性100%）
- 集成测试通过率（≥95%）
- 幻觉率检测（≤3%）
- 并发安全（0异常）
- KPI达标（非阻断）

**示例：** content-writer-agent, data-analyst-agent, code-reviewer-agent

---

### 管理层 (Management Layer) — L2
协调执行层 Worker Agent，管理任务生命周期。Prompt Chaining / 状态机 / 错误恢复。

**关键能力：**
- 任务分解策略
- 状态机模型（初始→运行→成功/失败/超时）
- 结果聚合
- 错误恢复路径

---

### 决策层 (Decision Layer) — L3
战略决策，跨部门协调。数据驱动，权威引用，闭环反馈。

**C-Suite Agents：**
- CEO — 战略决策
- CTO — 技术决策
- CISO — 安全决策
- CFO — 财务决策
- CMO — 营销决策
- CLO — 法务决策
- COO — 运营决策

---

## Harness Engineering 三原则

1. **标准化** — 统一接口、格式、命名规范
2. **模块化** — 组件独立可替换，低耦合高内聚
3. **通用化** — 适用于所有四层，不针对特定业务

---

## 安全审查规范（CISO-001）

### VirusTotal 合规
- 禁止模式：eval, exec, hardcoded keys, 未白名单的外部API调用
- 允许模式：标准库调用，已声明的依赖
- 自动检测：6类规则

### ClawHub 代码审查
- SKILL.md 结构合规（8项检查）
- 权限声明完整性（6项检查）
- 依赖安全检查（7项检查）

### 四层安全门禁
- 工具层：最小权限，无副作用
- 执行层：输入验证，输出脱敏
- 管理层：状态隔离，权限边界
- 决策层：审计日志，人工接管通道

---

## 下一步
整合以上规范，生成 ai-company-agent-factory Skill 文件结构。
