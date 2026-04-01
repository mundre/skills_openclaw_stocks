# Auto Revolution

**版本：** 2.0.0  
**作者：** OpenClaw Community  
**创建：** 2026-03-28  
**更新：** 2026-03-29

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

---

## 核心特性

### 1. 任务难度分析 📊
- 自动评估复杂度/风险/时间要求
- 4 个评估维度：代码量/文件数/依赖/风险
- 自动推荐合适流程

### 2. 三种流程模式 🔄
| 流程 | 步骤 | 耗时 | 适用 |
|------|------|------|------|
| **简化流程** ⚡ | Executor | ~5m | 文档/简单 Bug |
| **完整流程** 📊 | 审阅→执行→审核 | ~15m | 新功能/重构 |
| **高级流程** 🏆 | 审阅→执行→审核 | ~15m | 核心/安全 |

### 3. 用户选择机制 👤
- 分析后推荐流程
- 用户确认最终选择
- 支持手动覆盖

### 4. Executor 统一 🎯
- **默认：** `默认模型`（代码能力强）
- **除非：** 用户特殊要求

### 5. 强制审核 🔒
- `enforceAudit: true`
- Executor 完成后必须经过 Auditor
- 审核失败打回重做（最多 3 次）

---

## 快速开始

### 1. 配置 Cron（一次性）

```bash
# 主 Agent 心跳 - 每 5 分钟
openclaw cron add --agent main \
  --name "evolution-heartbeat" \
  --schedule "*/5 * * * *" \
  --message "node <workspace>/evolution/scripts/heartbeat-coordinator.js"

# 审计 Agent 心跳 - 每 5 分钟
openclaw cron add --agent auditor \
  --name "evolution-auditor-heartbeat" \
  --schedule "*/5 * * * *" \
  --message "node <workspace>/evolution/scripts/auditor-heartbeat.js"
```

### 2. 创建任务

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

### 3. 等待自动执行

```bash
# 心跳每 5 分钟执行一次
# 或手动触发
node scripts/heartbeat-coordinator.js
```

### 4. 查看进度

```bash
# 查看任务状态
cat tasks/task-001.json | jq '.status, .current_subtask'

# 查看事件日志
tail -f logs/events.log | jq
```

---

## 目录结构

```
evolution/
├── config/
│   └── models.json          # 模型配置（超时/回退/强制审核）
├── tasks/
│   └── task-*.json          # 任务队列
├── scripts/
│   ├── heartbeat-coordinator.js  # 心跳协调器
│   ├── apply-review.js           # 应用审阅结果
│   ├── security-scan.js          # 安全扫描
│   └── ...
├── logs/
│   └── events.log           # 事件日志（JSONL）
├── outputs/
│   └── ...                  # 执行输出
└── README.md                # 本文档
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

## 完整流程

### Step 1: 任务分析

**触发：** 心跳检测到 `status: pending` 的任务

**操作：**
1. 读取任务 JSON
2. 评估复杂度/风险/时间要求
3. 推荐流程（简化/完整/高级）
4. 等待用户确认（如未指定 flow 字段）

---

### Step 2: 审阅 (Reviewer)

**超时：** 300 秒  
**模型：** `高级模型` → fallback → `备用模型`

**操作：**
1. 读取所有 reference_files
2. 技术选型审查（依赖/场景/复杂度/集成）
3. 判断 verdict（approve/revise/reject）
4. 生成详细执行指令

---

### Step 3: 执行 (Executor)

**超时：** 300 秒  
**模型：** `默认模型`

**操作：**
1. 严格按 Reviewer 指令执行
2. 每步修改后运行验证命令
3. 失败时尝试修复（最多 3 次）
4. 输出 JSON 结果

---

### Step 4: 审核 (Auditor) ⭐ 强制

**超时：** 180 秒  
**模型：** `高级模型` → fallback → `备用模型`

**操作：**
1. 对比原始指令与执行结果
2. 审核标准：指令遵循/代码质量/测试验证/技术选型
3. 判断 verdict（pass/fail）

**结果：**
- **pass** → 更新任务 JSON，标记 completed
- **fail** → current_iteration++，打回重做（最多 3 次）

---

## 与 TDR 共享的资源

| 资源 | 位置 | 说明 |
|------|------|------|
| **任务队列** | `tasks/` | 两个系统共享同一任务队列 |
| **模型配置** | `config/models.json` | 共享模型配置 |
| **执行脚本** | `scripts/` | 共享执行逻辑 |
| **事件日志** | `logs/events.log` | 共享日志文件 |
| **输出目录** | `outputs/` | 共享输出文件 |

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

### 3. 心跳配置

- 建议间隔：5 分钟
- 避免过短：防止 API 限流
- 避免过长：任务执行延迟

---

## 相关文档

- [REVOLUTION-CONFIG.md](./REVOLUTION-CONFIG.md) - 完整流程说明
- [MODEL-CONFIG.md](./MODEL-CONFIG.md) - 模型配置详情
- [AUTO-REVOLUTION-FLOW-DECISION.md](./AUTO-REVOLUTION-FLOW-DECISION.md) - 流程选择指南
- [Test-Driven Revolution (ClawHub)](https://clawhub.com/skills/test-driven-revolution) - TDR 技能页面

---

**最后更新：** 2026-03-29  
**维护者：** OpenClaw Community
