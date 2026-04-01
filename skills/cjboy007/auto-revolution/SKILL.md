# Auto Revolution Skill

**Version:** 2.0.1  
**AgentSkills:** v1.1.0  
**Author:** OpenClaw Community  
**Created:** 2026-03-28  
**Updated:** 2026-03-29

---

## 描述

Auto Revolution 是一个**自动化的 AI 自动进化系统**，通过 Cron 心跳定时执行任务队列：

```
任务创建 → Cron 心跳 → 审阅→执行→审核 → 循环迭代 → 任务完成
```

**与 Test-Driven Revolution (TDR) 的关系：**
- **Auto Revolution** = 底层执行引擎（Cron 心跳自动执行）
- **TDR** = 用户 interface（AgentSkills 技能包，手动触发）
- **两者共享同一套配置和脚本**，只是触发方式不同

**触发方式对比：**
| 系统 | 触发方式 | 适用场景 |
|------|----------|----------|
| **Auto Revolution** | Cron 定时任务（每 5 分钟） | 后台自动执行任务队列 |
| **TDR** | 用户说"用 TDR 创建 XX" | 主动开发新功能 |

核心工作流：
1. **任务分析** - 分析任务难度/风险/时间要求，推荐流程
2. **用户选择** - 用户确认流程类型（简化/完整/高级）
3. **执行流程** - 按选择的流程执行（审阅→执行→审核）
4. **循环迭代** - 审核通过→下一轮；审核失败→打回重做

**角色说明：**
- **Planner** - 负责任务分析和流程推荐（主 Agent）
- **Reviewer** - 负责技术选型审查和指令生成（高级模型）
- **Executor** - 负责代码执行和文件操作（默认模型）⭐
- **Auditor** - 负责质量审核和验证（高级模型）

系统特性：
- 📊 **任务难度分析** - 自动评估复杂度/风险/时间要求
- 🎯 **流程推荐** - 根据任务类型推荐简化/完整/高级流程
- 👤 **用户选择** - 推荐后由用户确认最终流程
- 🔒 **原子锁**：`mkdir` 原子操作，防止并发竞态
- 🛡️ **安全扫描**：执行前检测危险命令模式
- 📝 **事件日志**：所有操作追加 JSONL 日志
- 🔗 **依赖激活**：依赖完成后自动激活下游任务
- 💰 **成本控制**：Executor 统一使用默认模型

---

## 触发方式

**Auto Revolution 是后台自动执行系统，通过 Cron 心跳触发：**

```bash
# 配置 Cron（一次性）
openclaw cron add --agent main \
  --name "evolution-heartbeat" \
  --schedule "*/5 * * * *" \
  --message "node <workspace>/evolution/scripts/heartbeat-coordinator.js"
```

**手动触发：**
```bash
node scripts/heartbeat-coordinator.js
```

---

## 三种流程模式

### 1. 简化流程 ⚡

**步骤：** Executor 直连（无审阅/审核）

**模型：** Executor = `默认模型`

**耗时：** ~5 分钟/任务

**成本：** 🆓 免费（使用包月额度）

**适用场景：**
- 文档更新（SKILL.md、参考文档）
- 简单 Bug 修复（紧急）
- 批量改进（低风险）
- 代码量 <100 行

---

### 2. 完整流程 📊

**步骤：** Reviewer → Executor → Auditor

**模型：**
- Reviewer: `高级模型` → fallback → `备用模型`
- Executor: `默认模型`
- Auditor: `高级模型` → fallback → `备用模型`

**耗时：** ~15 分钟/任务

**成本：** 🆓 免费（使用包月额度）

**适用场景：**
- 新功能实现
- 代码重构（中等风险）
- 多文件修改
- 代码量 100-500 行

---

### 3. 高级流程 🏆

**步骤：** Reviewer → Executor → Auditor

**模型：**
- Reviewer: `顶级模型`
- Executor: `默认模型`
- Auditor: `顶级模型`

**耗时：** ~15 分钟/任务

**成本：** 💰$$（按量计费，约 $0.5-2/任务）

**适用场景：**
- 核心功能开发
- 安全相关修复
- 生产发布前验证
- 代码量 >500 行

---

## 任务难度评估

### 评估维度

| 维度 | 简单 | 中等 | 复杂 |
|------|------|------|------|
| **代码量** | <100 行 | 100-500 行 | >500 行 |
| **文件数** | 1-2 个 | 3-5 个 | >5 个 |
| **依赖** | 无 | 部分 | 跨模块 |
| **风险** | 低 | 中 | 高 |
| **可回滚** | 是 | 部分 | 否 |

### 自动推荐规则

| 任务类型 | 默认流程 | 例外情况 |
|----------|----------|----------|
| 文档更新 | 简化流程 | 大规模重构→完整 |
| Bug 修复 | 简化流程 | 安全漏洞→高级 |
| 新功能 | 完整流程 | 核心功能→高级 |
| 代码重构 | 完整流程 | 核心架构→高级 |
| 安全修复 | 高级流程 | - |
| 批量改进 | 简化流程 | 影响核心→完整 |

---

## 使用方法

### 1. 创建任务

在 `tasks/` 目录下创建 JSON 文件：

```bash
cat > tasks/task-001.json << 'EOF'
{
  "task_id": "task-001",
  "title": "创建 HTTP 服务器",
  "description": "创建一个 HTTP 服务器，监听 3000 端口",
  "priority": "P1",
  "status": "pending",
  "flow": "full",
  "subtasks": [
    {"id": 0, "title": "创建 server.js", "description": "基础 HTTP 服务器"},
    {"id": 1, "title": "添加路由", "description": "GET /health, GET /api/data"},
    {"id": 2, "title": "编写测试", "description": "单元测试覆盖率>80%"}
  ]
}
EOF
```

**flow 字段可选值：**
- `simplified` - 简化流程
- `full` - 完整流程
- `advanced` - 高级流程

---

### 2. 等待自动执行

```bash
# Cron 每 5 分钟自动执行
# 或手动触发
node scripts/heartbeat-coordinator.js
```

---

### 3. 查看进度

```bash
# 查看任务状态
cat tasks/task-001.json | jq '.status, .current_subtask'

# 查看事件日志
tail -f logs/events.log | jq
```

---

## 配置文件

**位置：** `config/models.json`

```json
{
  "roles": {
    "reviewer": {
      "primary": "高级模型",
      "fallback": "备用模型"
    },
    "executor": "默认模型",
    "auditor": {
      "primary": "高级模型",
      "fallback": "备用模型"
    }
  },
  "timeouts": {
    "reviewer": 300,
    "executor": 300,
    "auditor": 180
  },
  "enforceAudit": true,
  "executorDefault": "默认模型"
}
```

---

## 流程对比表

| 特性 | 简化流程 | 完整流程 | 高级流程 |
|------|----------|----------|----------|
| **步骤** | Executor | Reviewer→Executor→Auditor | Reviewer→Executor→Auditor |
| **Executor** | 默认模型 | 默认模型 | 默认模型 |
| **Reviewer** | - | 高级模型 | 顶级模型 |
| **Auditor** | - | 高级模型 | 顶级模型 |
| **耗时** | ~5m | ~15m | ~15m |
| **成本** | 🆓 | 🆓 | 💰$$ |
| **成功率** | ~80% | ~90% | ~95% |
| **适用** | 文档/简单 Bug | 新功能/重构 | 核心/安全 |

---

## 安全规则

### 执行前检查

1. **危险命令检测** - 禁止 `rm -rf`、`DROP TABLE` 等
2. **写入路径验证** - 限制在 workspace 目录内
3. **外部 API 调用** - 需要用户确认
4. **大额扣费** - >$100 需要人工审批

### 执行中监控

1. **原子锁** - 防止并发冲突
2. **事件日志** - 所有操作记录到 JSONL
3. **超时保护** - 超时自动终止

### 执行后审核

1. **Auditor 验证** - 完整流程/高级流程必须
2. **测试覆盖** - 关键功能必须通过测试
3. **回滚方案** - 高风险操作必须提供

---

## 错误处理

### 审核失败

```
审核失败 → current_iteration++ → 打回 Executor 重做
最多 3 次迭代 → 标记 failed → 人工介入
```

### 超时处理

```
超时 → 重试（最多 2 次） → 切换 fallback 模型 → 仍失败则标记 failed
```

### 模型认证失败

```
401 认证失败 → 切换 fallback 模型 → 记录错误日志
```

---

## 最佳实践

### 1. 任务拆解

**好：**
```json
{
  "subtasks": [
    {"title": "创建 HTTP 服务器", "description": "监听 3000 端口"},
    {"title": "添加路由", "description": "GET /health, GET /api/data"},
    {"title": "编写测试", "description": "单元测试覆盖率>80%"}
  ]
}
```

**不好：**
```json
{
  "subtasks": [
    {"title": "完成整个项目"}  // 太笼统
  ]
}
```

### 2. 流程选择

- **文档更新** → 简化流程（快速、免费）
- **新功能** → 完整流程（有审核、免费）
- **安全修复** → 高级流程（顶级模型审核、付费）

### 3. 迭代控制

- 单次迭代 <10 分钟
- 最多 3 次迭代
- 3 次失败后人工介入

---

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| 2.0.1 | 2026-03-29 | 脱敏发布版本 |
| 2.0.0 | 2026-03-29 | 添加任务难度分析、三种流程模式、用户选择机制 |
| 1.0.0 | 2026-03-28 | 初始版本 |

---

## 相关文档

- [REVOLUTION-CONFIG.md](./REVOLUTION-CONFIG.md) - 完整流程说明
- [MODEL-CONFIG.md](./MODEL-CONFIG.md) - 模型配置详情
- [AUTO-REVOLUTION-FLOW-DECISION.md](./AUTO-REVOLUTION-FLOW-DECISION.md) - 流程选择指南
- [Test-Driven Revolution (ClawHub)](https://clawhub.com/skills/test-driven-revolution) - TDR 技能页面

---

**最后更新：** 2026-03-29  
**维护者:** OpenClaw Community
