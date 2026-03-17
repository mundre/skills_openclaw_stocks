---
name: complex-task-subagent
description: Complex task orchestration and subagent command framework. Execute multi-stage complex tasks via subagent (sessions_spawn), including task breakdown, state management, checkpoint-driven, timeout retry, auto-progress and sync. Suitable for serial task orchestration scenarios requiring reliable execution, auto-recovery and unattended operation.
---

# 复杂任务指挥子代理（Complex Task Subagent）

## 安装

### 方法 1：通过 ClawHub 安装（推荐）

```bash
# 安装 ClawHub CLI
npm i -g clawhub

# 安装 skill
clawhub install complex-task-subagent
```

更新 skill：

```bash
clawhub update complex-task-subagent
```

### 方法 2：从 GitHub/Gitee 手动安装

```bash
# 克隆仓库
git clone https://gitee.com/GoSundayPlus/complex-task-subagent-skill.git ~/.openclaw/workspace/skills/complex-task-subagent

# 或者使用 .skill 文件直接安装
# 1. 下载 .skill 文件
# 2. 将文件移动到 ~/.openclaw/skills/ 目录
# 3. 重启 OpenClaw Gateway
openclaw gateway restart
```

手动更新：

```bash
cd ~/.openclaw/workspace/skills/complex-task-subagent
git pull
openclaw gateway restart
```

### 方法 3：从 ClawHub 下载并手动安装

访问 https://clawhub.com/skills/complex-task-subagent 下载 .skill 文件，然后按照方法 2 的步骤 2-3 进行安装。

## 快速开始

**适用场景**：当你需要通过子代理执行多阶段复杂任务时使用此技能。

**核心价值**：
- 可靠的任务编排和状态管理
- 自动检测和推进已完成的阶段
- 超时和重试机制，提高鲁棒性
- 检查点驱动，支持任务恢复
- 集成 OpenClaw Heartbeat 实现无人值守
- 🌙 **夜间无人模式**：提前收集必要信息，在用户休息时自助决策完成任务
- 🔑 **关键节点确认模式**：重要决策点自动提醒用户，超时自动切换无人模式
- 💾 **智能缓存管理**：子代理临时缓存，正常完成自动回收，异常中断可恢复
- ⚡ **深度工作模式**：完全无人值守的自动化任务执行框架

## 架构概览

```
┌─────────────────────────────────────────────┐
│              主会话（指挥官）                 │
│  - 任务编排和状态管理                         │
│  - 超时检测和重试                             │
│  - 自动推进下一阶段                           │
│  - 同步到 Gitee                              │
└─────────────────────────────────────────────┘
           │
           ├──────────────┬──────────────┐
           ▼              ▼              ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ 子代理 1 │   │ 子代理 2 │   │ 子代理 3 │
    └──────────┘   └──────────┘   └──────────┘
           │              │              │
           └──────────────┴──────────────┘
                          │
                          ▼
                checkpoints/*.json
                (任务完成标记)

                          │
                          ▼
                OpenClaw Heartbeat
                (定期检查和自动推进)
```

## 核心原则

### 1. 单一事实来源（SSOT）

所有状态变更应该更新到一个中心化的文件：`task-progress.json`。

**为什么重要**：
- 避免状态不一致
- 简化调试和恢复
- 确保可追溯性

### 2. 检查点驱动

子代理完成任务后必须写入检查点文件，主会话基于检查点推进。

**为什么重要**：
- 可靠性：同步写入，不会丢失
- 可恢复：任务中断后可以继续
- 可验证：可以检查任务完整性

### 3. 主会话主导

主会话应该掌握控制权，定期检查并推进任务。

**为什么重要**：
- 逻辑清晰，易于维护
- 可以实现自动化
- 避免分布式协调的复杂性

### 4. 超时和重试

每个阶段都应该有超时机制和重试策略。

**为什么重要**：
- 提高系统鲁棒性
- 可以自动恢复临时性故障
- 避免长时间卡死

### 5. 渐进式披露

使用 OpenClaw Heartbeat 实现无人值守的定期检查。

**为什么重要**：
- 不依赖系统权限（如 cron）
- 与 OpenClaw 生态无缝集成
- 内置重试机制

### 6. 夜间无人模式

在任务开始前收集所有必要信息，在用户休息期间自助决策完成任务。

**为什么重要**：
- 充分利用夜间时间
- 避免打扰用户休息
- 提高整体效率

### 7. 关键节点确认模式

在关键决策点自动提醒用户，超时后自动切换到无人模式。

**为什么重要**：
- 平衡控制权和自动化
- 重要决策有人类参与
- 确保关键操作的安全性

### 8. 智能缓存管理

子代理工作期间使用临时缓存，正常完成自动回收，异常中断可恢复。

**为什么重要**：
- 避免重复工作
- 支持任务恢复
- 提高容错性

### 9. 深度工作模式

完全无人值守的自动化任务执行，包括进度监控、自动推进、异常恢复。

**为什么重要**：
- 最大化自动化程度
- 减少人为干预
- 实现真正的无人值守

## 任务结构

### 单一状态文件：task-progress.json

```json
{
  "taskId": "unique-task-id",
  "taskName": "任务名称",
  "status": "in_progress",
  "currentPhase": 3,
  "completedPhases": 2,
  "totalPhases": 4,
  "lastUpdated": "2026-03-10T00:00:00Z",
  "checkpointsDir": "/root/.openclaw/workspace/complex-task-subagent-experience/checkpoints",
  "cacheDir": "/root/.openclaw/workspace/complex-task-subagent-experience/cache",
  "executionMode": "confirmation",
  "userPreferences": {
    "preferredAction": "ask",
    "autoFallbackToUnattended": true,
    "fallbackTimeout": 7200000,
    "nightModeEnabled": false,
    "nightModeStart": "22:00",
    "nightModeEnd": "08:00"
  },
  "notification": {
    "lastReminder": null,
    "reminderCount": 0,
    "remindersSent": []
  },
  "phases": {
    "phase1": {
      "name": "审核现有指南",
      "status": "completed",
      "completedAt": "2026-03-09T16:53:00Z",
      "subagent": "subagent-audit",
      "timeout": 1800000,
      "maxRetries": 3,
      "retries": 0,
      "checkpoint": "phase1-audit.json",
      "output": "/root/.openclaw/workspace/output/phase1-result.md",
      "cacheFile": "phase1-cache.json",
      "requiresConfirmation": false,
      "critical": false
    },
    "phase2": {...},
    "phase3": {
      "name": "创建 CDP 直连方案指南",
      "status": "running",
      "startedAt": "2026-03-09T18:56:00Z",
      "subagent": "subagent-cdp-guide",
      "timeout": 1800000,
      "maxRetries": 3,
      "retries": 0,
      "checkpoint": "phase3-cdp-guide.json",
      "output": "/root/.openclaw/workspace/output/phase3-result.md",
      "cacheFile": "phase3-cache.json",
      "requiresConfirmation": true,
      "critical": true,
      "confirmationTimeout": 3600000,
      "requiresGatewayRestart": false
    },
    "phase4": {...}
  }
}
```

### 字段说明

| 字段 | 说明 | 必需 |
|------|------|------|
| `taskId` | 任务唯一标识 | ✅ |
| `taskName` | 任务名称 | ✅ |
| `status` | 状态：in_progress/completed/failed | ✅ |
| `currentPhase` | 当前阶段编号 | ✅ |
| `completedPhases` | 已完成阶段数 | ✅ |
| `totalPhases` | 总阶段数 | ✅ |
| `lastUpdated` | 最后更新时间 | ✅ |
| `checkpointsDir` | 检查点目录路径 | ✅ |
| `cacheDir` | 子代理缓存目录路径 | ⚠️ |
| `executionMode` | 执行模式：unattended/confirmation | ✅ |
| `userPreferences` | 用户偏好设置 | ⚠️ |
| `notification` | 通知状态追踪 | ⚠️ |
| `phases` | 各阶段详细配置 | ✅ |

### UserPreferences 字段说明

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `preferredAction` | 默认操作：ask/auto/ask-critical | ask |
| `autoFallbackToUnattended` | 是否自动降级到无人模式 | true |
| `fallbackTimeout` | 降级超时时间（毫秒） | 7200000 (2小时) |
| `nightModeEnabled` | 是否启用夜间模式 | false |
| `nightModeStart` | 夜间模式开始时间 | 22:00 |
| `nightModeEnd` | 夜间模式结束时间 | 08:00 |

### Notification 字段说明

| 字段 | 说明 |
|------|------|
| `lastReminder` | 最后一次提醒时间 |
| `reminderCount` | 已发送提醒次数 |
| `remindersSent` | 已发送提醒的列表 |

### Phase 字段说明

| 字段 | 说明 | 必需 |
|------|------|------|
| `name` | 阶段名称 | ✅ |
| `status` | 状态：pending/starting/running/completed/failed | ✅ |
| `startedAt` | 开始时间（running 状态） | ⚠️ |
| `completedAt` | 完成时间（completed 状态） | ⚠️ |
| `subagent` | 子代理标签（用于 sessions_spawn） | ⚠️ |
| `timeout` | 超时时间（毫秒） | ⚠️ |
| `maxRetries` | 最大重试次数 | ⚠️ |
| `retries` | 当前重试次数 | ⚠️ |
| `checkpoint` | 检查点文件名 | ⚠️ |
| `output` | 输出文件路径 | ⚠️ |
| `cacheFile` | 子代理缓存文件名 | ⚠️ |
| `requiresConfirmation` | 是否需要用户确认 | ⚠️ |
| `critical` | 是否为关键操作 | ⚠️ |
| `confirmationTimeout` | 确认超时时间（毫秒） | ⚠️ |
| `requiresGatewayRestart` | 是否需要重启 Gateway | ⚠️ |

## 工作流程

### 阶段 0：模式选择（新增）

1. **选择执行模式**

   **夜间无人模式**：
   - 提前收集所有必要信息
   - 设置 `executionMode: "unattended"`
   - 用户休息期间自助决策

   **关键节点确认模式**：
   - 设置 `executionMode: "confirmation"`
   - 关键操作需要用户确认
   - 超时自动降级到无人模式

2. **收集必要信息（无人模式）**

   ```bash
   # 创建预配置模板
   cat > /root/.openclaw/workspace/task-preferences.json << 'EOF'
   {
     "confirmations": {
       "gatewayRestart": {
         "allowed": false,
         "alternative": "使用缓存或降级方案"
       },
       "fileOperations": {
         "allowed": true,
         "safePaths": ["/root/.openclaw/workspace"]
       },
       "apiCalls": {
         "allowed": true,
         "rateLimit": 100
       }
     },
     "fallbackStrategies": {
       "critical": "ask_user",
       "nonCritical": "auto_proceed"
     }
   }
   EOF
   ```

3. **配置用户偏好**

   编辑 `task-progress.json` 中的 `userPreferences`：

   ```json
   {
     "preferredAction": "ask-critical",
     "autoFallbackToUnattended": true,
     "fallbackTimeout": 7200000,
     "nightModeEnabled": true,
     "nightModeStart": "22:00",
     "nightModeEnd": "08:00"
   }
   ```

### 阶段 1：任务初始化

1. **创建 task-progress.json**
   - 定义所有阶段和配置
   - 设置初始状态为 "in_progress"
   - 所有阶段状态为 "pending"
   - 设置执行模式和用户偏好

2. **创建 checkpoints 目录**
   ```bash
   mkdir -p /root/.openclaw/workspace/complex-task-subagent-experience/checkpoints
   ```

3. **创建 cache 目录（新增）**
   ```bash
   mkdir -p /root/.openclaw/workspace/complex-task-subagent-experience/cache
   ```

4. **配置 OpenClaw Heartbeat**
   - 编辑 `HEARTBEAT.md`（见参考文档）
   - 调整心跳频率（推荐 10 分钟）

### 阶段 2：执行任务

1. **启动子代理**

   ```bash
   # 基础启动
   sessions_spawn \
     --task "任务描述" \
     --label "subagent-name" \
     --runtime "subagent" \
     --mode "run" \
     --timeoutSeconds 3600

   # 带缓存启动（新增）
   sessions_spawn \
     --task "任务描述" \
     --label "subagent-name" \
     --runtime "subagent" \
     --mode "run" \
     --timeoutSeconds 3600 \
     --cwd "/root/.openclaw/workspace/xianyu-automation"
   ```

2. **子代理缓存管理（新增）**

   在子代理任务描述中明确要求使用缓存：

   ```
   执行以下任务：
   1. 使用 /root/.openclaw/workspace/complex-task-subagent-experience/cache/phase3-cache.json 作为临时缓存文件
   2. 任务过程中定期写入缓存（每10分钟或每个重要步骤后）
   3. 缓存格式：{"step": 1, "data": {...}, "timestamp": "2026-03-14T18:00:00Z"}
   4. 任务正常完成后，将最终结果写入检查点文件，并标记缓存可回收
   5. 如果任务异常中断，缓存文件保留用于恢复
   ```

   缓存文件示例：
   ```json
   {
     "phase": "phase3",
     "subagent": "subagent-cdp-guide",
     "status": "in_progress",
     "currentStep": 2,
     "totalSteps": 5,
     "data": {
       "intermediateResults": [],
       "state": {}
     },
     "timestamp": "2026-03-14T18:05:00Z"
   }
   ```

3. **关键节点确认（新增）**

   在需要用户确认的阶段：

   ```
   准备执行需要用户确认的操作：
   - 操作类型：${type}
   - 风险等级：${risk}
   - 需要重启 Gateway：${needsRestart}

   请确认是否继续执行？回复"确认"或"同意"继续，其他回复跳过此操作。
   如果1小时内未回复，将自动降级到无人模式。
   ```

   提醒机制：
   ```bash
   # 第一次提醒（开始等待时）
   echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📌 需要用户确认" >> task-notification.log

   # 1小时后第二次提醒
   if [ $(( $(date +%s) - lastConfirmation )) -gt 3600 ]; then
     echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📌 仍需用户确认（已等待1小时）" >> task-notification.log
   fi

   # 2小时后自动降级
   if [ $(( $(date +%s) - lastConfirmation )) -gt 7200 ]; then
     executionMode="unattended"
     echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🌙 自动切换到无人模式" >> task-notification.log
   fi
   ```

4. **子代理执行任务**
   - 子代理完成任务后写入检查点文件
   - 检查点文件包含任务结果和元数据
   - 正常完成后标记缓存可回收

5. **主会话检测到检查点**
   - Heartbeat 定期检查 checkpoints 目录
   - 发现新检查点 → 验证完整性
   - 更新 task-progress.json

6. **自动推进下一阶段**
   - 检查下一阶段依赖条件
   - 如果需要确认且未收到回复，进入等待状态
   - 如果满足条件，启动下一阶段子代理

7. **缓存回收（新增）**

   在子代理正常完成后：
   ```bash
   # 检查任务状态
   if [ "$phase_status" = "completed" ]; then
     # 回收缓存
     rm -f /root/.openclaw/workspace/complex-task-subagent-experience/cache/$cacheFile
     echo "[$(date '+%Y-%m-%d %H:%M:%S')] ♻️ 缓存已回收: $cacheFile" >> task-cache.log
   fi
   ```

   在子代理异常中断后恢复：
   ```bash
   # 检查缓存文件
   if [ -f "$cacheFile" ]; then
     # 读取缓存
     cache_data=$(cat "$cacheFile")
     echo "[$(date '+%Y-%m-%d %H:%M:%S')] 📦 从缓存恢复: $cacheFile" >> task-cache.log

     # 重新启动子代理并传入缓存
     sessions_spawn \
       --task "任务描述 - 从缓存恢复: $cache_data" \
       --label "subagent-name-retry" \
       --runtime "subagent" \
       --mode "run" \
       --timeoutSeconds 3600
   fi
   ```

### 阶段 3：超时和重试

1. **超时检测**
   ```python
   if phase.status == "running":
       elapsed = now() - phase.startedAt
       if elapsed > phase.timeout:
           if phase.retries < phase.maxRetries:
               # 重试
               phase.retries += 1
               restart_subagent(phase)
           else:
               # 失败
               phase.status = "failed"
               notify_user()
   ```

2. **重新启动子代理**
   - 使用相同的 label 和任务描述
   - 增加重试计数器

### 阶段 4：任务完成

1. **所有阶段完成**
   - 检查所有阶段状态为 "completed"
   - 更新任务状态为 "completed"

2. **同步到 Gitee**
   ```bash
   cd /root/.openclaw

   # 添加所有修改
   git add workspace/output/ workspace/experience/

   # 提交
   COMMIT_MSG="任务完成：$(date '+%Y-%m-%d %H:%M')"
   git commit -m "$COMMIT_MSG"

   # 推送
   git push
   ```

3. **记录日志**
   ```bash
   echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 任务已完成并同步到 Gitee" >> /root/.openclaw/workspace/task-monitor.log
   ```

## 检查点格式

### 检查点文件结构

```json
{
  "checkpointId": "phase1-audit",
  "phase": "phase1",
  "phaseName": "审核现有指南",
  "status": "completed",
  "completedAt": "2026-03-09T16:53:00Z",
  "subagent": "subagent-audit",
  "output": "/root/.openclaw/workspace/output/phase1-result.md",
  "result": {
    "success": true,
    "message": "审核完成，发现 3 个问题",
    "issues": [
      "问题 1",
      "问题 2",
      "问题 3"
    ]
  },
  "metadata": {
    "totalIssues": 3,
    "criticalIssues": 1,
    "warnings": 2
  }
}
```

### 写入检查点

在子代理中：
```python
def write_checkpoint(checkpoint_file, data):
    import json
    from pathlib import Path

    checkpoint_path = Path("/root/.openclaw/workspace/complex-task-subagent-experience/checkpoints") / checkpoint_file

    with open(checkpoint_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"✅ 检查点已写入: {checkpoint_path}")
```

## OpenClaw Heartbeat 集成

### 配置 HEARTBEAT.md

将以下内容添加到 `HEARTBEAT.md`（或创建独立的 `HEARTBEAT-TASK.md`）：

```markdown
# 任务检查清单

1. 读取 task-progress.json
2. 检查 checkpoints/ 目录
3. 比对检查点和任务进度，更新状态
4. 如果阶段完成但下一阶段未启动，自动推进
5. 如果所有阶段完成，同步到 Gitee
6. 记录操作日志
7. 如果没有需要推进的内容，回复 HEARTBEAT_OK
```

### 配置 openclaw.json

```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "10m",
        "target": "last",
        "prompt": "Read HEARTBEAT-TASK.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK."
      }
    }
  }
}
```

### 心跳频率选择

| 频率 | 适用场景 | 说明 |
|------|----------|------|
| 5 分钟 | 高优先级任务 | 快速响应，但消耗更多 token |
| 10 分钟 | 一般任务（推荐） | 平衡响应和成本 |
| 30 分钟 | 低优先级任务 | 节省 token，响应较慢 |
| 1 小时 | 后台任务 | 最小化 token 消耗 |

## 子代理最佳实践

### 子代理任务设计

**好的任务描述**：
- ✅ "审核 /root/.openclaw/workspace/guide.md 文件，对比官方文档，记录所有虚构内容和不准确信息，输出到 /root/.openclaw/workspace/output/audit-report.md"

**不好的任务描述**：
- ❌ "审核指南"
- ❌ "看看这个文件有没有问题"
- ❌ "帮我检查一下"

### 子代理超时设置

| 任务类型 | 超时时间 | 说明 |
|----------|----------|------|
| 文本审核/分析 | 30 分钟 | 读取、分析、输出 |
| 文档编写 | 1 小时 | 可能需要多次迭代 |
| 代码生成 | 45 分钟 | 需要测试和调试 |
| 数据处理 | 2 小时 | 取决于数据量 |
| Gitee 同步 | 5 分钟 | 快速操作 |

### 子代理标签规范

使用描述性的标签，格式：`subagent-<任务简述>`

| 任务 | 标签示例 |
|------|----------|
| 审核指南 | `subagent-audit-guide` |
| 创建文档 | `subagent-create-doc` |
| 测试代码 | `subagent-test-code` |
| 同步 Gitee | `subagent-sync-gitee` |

## 常见问题和解决方案

### 问题 1：子代理完成后未推进下一阶段

**症状**：
- 子代理显示完成
- 但 task-progress.json 状态未更新
- 下一阶段未启动

**原因**：
- 子代理未写入检查点文件
- Heartbeat 未检测到检查点
- 检查点路径配置错误

**解决方案**：
1. 检查 checkpoints 目录是否存在
2. 检查检查点文件是否有效 JSON
3. 检查 Heartbeat 配置是否正确

### 问题 2：子代理超时

**症状**：
- 阶段状态一直是 "running"
- 超时时间已过

**原因**：
- 子代理卡死
- 任务过于复杂
- 网络问题

**解决方案**：
1. 检查子代理日志
2. 增加超时时间
3. 重试机制自动重启

### 问题 3：状态不一致

**症状**：
- task-progress.json 和 checkpoints 不一致
- 已完成的阶段显示为 "running"

**原因**：
- 手动修改了状态文件
- 多个进程同时修改

**解决方案**：
1. 以 task-progress.json 为准（SSOT）
2. 使用检查点验证
3. 避免手动修改状态文件

### 问题 4：Gitee 同步失败

**症状**：
- Git push 返回错误
- 任务标记为失败

**原因**：
- 网络问题
- 认证问题
- 冲突

**解决方案**：
1. 检查网络连接
2. 验证 SSH 密钥
3. 手动解决冲突后重试

## 完整示例

参见以下参考文档获取详细示例：
- [references/quick-start.md](references/quick-start.md) - 快速开始示例
- [references/advanced-patterns.md](references/advanced-patterns.md) - 高级模式
- [references/troubleshooting.md](references/troubleshooting.md) - 故障排查

## 深度工作模式完整配置指南

以 xianyu-automation 项目为例，展示如何完整配置深度工作模式。

### 1. 项目工作区配置

确保所有相关 agent 共享同一个工作区：

```bash
# 工作区路径
WORKSPACE="/root/.openclaw/workspace/xianyu-automation"

# 创建必要的目录结构
cd $WORKSPACE
mkdir -p cache output 配置
```

### 2. 配置绘图模型（第三方 API）

#### 方法 1：手工配置

编辑 `~/.openclaw/openclaw.json`：

```json
{
  "agents": {
    "defaults": {
      "imageModel": "https://your-third-party-api.com/v1/images/generations",
      "imageModelProvider": "openai",
      "imageModelKey": "your-api-key"
    },
    "customAgents": {
      "content-creator": {
        "model": "zai/glm-4.7",
        "imageModel": "https://your-third-party-api.com/v1/images/generations",
        "imageModelKey": "your-specific-api-key"
      }
    }
  }
}
```

#### 方法 2：热加载配置

```bash
# 步骤 1：添加图像模型配置
openclaw config set agents.defaults.imageModel "https://your-third-party-api.com/v1/images/generations"
openclaw config set agents.defaults.imageModelProvider "openai"
openclaw config set agents.defaults.imageModelKey "your-api-key"

# 步骤 2：为特定 agent 配置不同的模型
openclaw config set agents.customAgents.content-creator.imageModel "https://your-specific-api.com/v1/images/generations"
openclaw config set agents.customAgents.content-creator.imageModelKey "your-specific-api-key"

# 步骤 3：重启 Gateway 以应用配置
openclaw gateway restart
```

#### 使用 jq 修改配置

```bash
# 设置默认图像模型
jq '.agents.defaults.imageModel = "https://your-third-party-api.com/v1/images/generations"' \
   ~/.openclaw/openclaw.json > /tmp/openclaw.json
mv /tmp/openclaw.json ~/.openclaw/openclaw.json

# 设置图像模型提供商
jq '.agents.defaults.imageModelProvider = "openai"' \
   ~/.openclaw/openclaw.json > /tmp/openclaw.json
mv /tmp/openclaw.json ~/.openclaw/openclaw.json

# 设置 API 密钥
jq '.agents.defaults.imageModelKey = "your-api-key"' \
   ~/.openclaw/openclaw.json > /tmp/openclaw.json
mv /tmp/openclaw.json ~/.openclaw/openclaw.json

# 为特定 agent 配置
jq '.agents.customAgents["content-creator"] = {"model": "zai/glm-4.7", "imageModel": "https://your-specific-api.com/v1/images/generations", "imageModelKey": "your-specific-api-key"}' \
   ~/.openclaw/openclaw.json > /tmp/openclaw.json
mv /tmp/openclaw.json ~/.openclaw/openclaw.json
```

### 3. 配置多 Agent 共享工作区

在 `~/.openclaw/openclaw.json` 中配置：

```json
{
  "agents": {
    "customAgents": {
      "xianyu-commander": {
        "model": "zai/glm-4.7",
        "cwd": "/root/.openclaw/workspace/xianyu-automation",
        "skills": ["complex-task-subagent", "tavily-search"]
      },
      "xianyu-data-analyst": {
        "model": "zai/glm-4.7",
        "cwd": "/root/.openclaw/workspace/xianyu-automation",
        "skills": ["tavily-search"]
      },
      "xianyu-content-creator": {
        "model": "zai/glm-4.7",
        "cwd": "/root/.openclaw/workspace/xianyu-automation",
        "skills": ["complex-task-subagent"]
      },
      "xianyu-operator": {
        "model": "zai/glm-4.7",
        "cwd": "/root/.openclaw/workspace/xianyu-automation",
        "skills": ["complex-task-subagent", "tavily-search"]
      }
    }
  }
}
```

#### 热加载配置

```bash
# 添加咸鱼总指挥 agent
openclaw config set agents.customAgents.xianyu-commander.model "zai/glm-4.7"
openclaw config set agents.customAgents.xianyu-commander.cwd "/root/.openclaw/workspace/xianyu-automation"
openclaw config set agents.customAgents.xianyu-commander.skills '["complex-task-subagent", "tavily-search"]'

# 添加咸鱼数据分析 agent
openclaw config set agents.customAgents.xianyu-data-analyst.model "zai/glm-4.7"
openclaw config set agents.customAgents.xianyu-data-analyst.cwd "/root/.openclaw/workspace/xianyu-automation"
openclaw config set agents.customAgents.xianyu-data-analyst.skills '["tavily-search"]'

# 添加咸鱼内容创作 agent
openclaw config set agents.customAgents.xianyu-content-creator.model "zai/glm-4.7"
openclaw config set agents.customAgents.xianyu-content-creator.cwd "/root/.openclaw/workspace/xianyu-automation"
openclaw config set agents.customAgents.xianyu-content-creator.skills '["complex-task-subagent"]'

# 添加咸鱼操作员 agent
openclaw config set agents.customAgents.xianyu-operator.model "zai/glm-4.7"
openclaw config set agents.customAgents.xianyu-operator.cwd "/root/.openclaw/workspace/xianyu-automation"
openclaw config set agents.customAgents.xianyu-operator.skills '["complex-task-subagent", "tavily-search"]'

# 重启 Gateway
openclaw gateway restart
```

### 4. 配置 Skill 使用

在 agent 配置中启用需要的 skill：

```json
{
  "agents": {
    "customAgents": {
      "xianyu-commander": {
        "model": "zai/glm-4.7",
        "skills": {
          "complex-task-subagent": {
            "enabled": true,
            "executionMode": "confirmation",
            "userPreferences": {
              "preferredAction": "ask-critical",
              "autoFallbackToUnattended": true,
              "nightModeEnabled": true
            }
          },
          "tavily-search": {
            "enabled": true,
            "apiKey": "your-tavily-api-key"
          }
        }
      }
    }
  }
}
```

### 5. 限制 Agent 调用权限

只允许咸鱼总指挥 agent 调用其他咸鱼相关 agent：

```json
{
  "agents": {
    "accessControl": {
      "xianyu-commander": {
        "canCall": ["xianyu-data-analyst", "xianyu-content-creator", "xianyu-operator"],
        "cannotCall": []
      },
      "xianyu-data-analyst": {
        "canCall": [],
        "cannotCall": ["xianyu-commander", "xianyu-content-creator", "xianyu-operator"]
      },
      "xianyu-content-creator": {
        "canCall": [],
        "cannotCall": ["xianyu-commander", "xianyu-data-analyst", "xianyu-operator"]
      },
      "xianyu-operator": {
        "canCall": [],
        "cannotCall": ["xianyu-commander", "xianyu-data-analyst", "xianyu-content-creator"]
      }
    }
  }
}
```

#### 热加载权限配置

```bash
# 设置咸鱼总指挥的调用权限
openclaw config set agents.accessControl.xianyu-commander.canCall '["xianyu-data-analyst", "xianyu-content-creator", "xianyu-operator"]'
openclaw config set agents.accessControl.xianyu-commander.cannotCall '[]'

# 限制子 agent 的调用权限
openclaw config set agents.accessControl.xianyu-data-analyst.canCall '[]'
openclaw config set agents.accessControl.xianyu-data-analyst.cannotCall '["xianyu-commander", "xianyu-content-creator", "xianyu-operator"]'

openclaw config set agents.accessControl.xianyu-content-creator.canCall '[]'
openclaw config set agents.accessControl.xianyu-content-creator.cannotCall '["xianyu-commander", "xianyu-data-analyst", "xianyu-operator"]'

openclaw config set agents.accessControl.xianyu-operator.canCall '[]'
openclaw config set agents.accessControl.xianyu-operator.cannotCall '["xianyu-commander", "xianyu-data-analyst", "xianyu-content-creator"]'

# 重启 Gateway
openclaw gateway restart
```

### 6. 飞书群聊配置

#### 新建飞书群聊并设置机器人

1. **通过飞书 API 创建群聊**

```bash
# 首先需要飞书 API 的 app_access_token
curl -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "cli_a92f97ca9b799cd4",
    "app_secret": "your-app-secret"
  }'
```

2. **添加机器人到群聊**

```bash
# 使用群聊 ID 和机器人 ID
curl -X POST "https://open.feishu.cn/open-apis/contact/v3/group/add_bot" \
  -H "Authorization: Bearer YOUR_APP_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "group_id": "YOUR_GROUP_ID",
    "bot_id": "ou_xxx"
  }'
```

3. **设置机器人为管理员**

```bash
curl -X POST "https://open.feishu.cn/open-apis/contact/v3/group/set_group_admin" \
  -H "Authorization: Bearer YOUR_APP_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "group_id": "YOUR_GROUP_ID",
    "user_id_list": ["ou_xxx"],
    "user_id_type": "open_id"
  }'
```

4. **配置 OpenClaw 默认机器人**

编辑 `~/.openclaw/openclaw.json`：

```json
{
  "feishu": {
    "defaultAgentForGroup": {
      "oc_2495bf92d31c385fc9818642325fb3d0": "xianyu-commander"
    }
  }
}
```

#### 热加载飞书配置

```bash
# 设置飞书群聊默认 agent
openclaw config set feishu.defaultAgentForGroup.oc_2495bf92d31c385fc9818642325fb3d0 "xianyu-commander"

# 重启 Gateway
openclaw gateway restart
```

### 7. 唤醒 Agent 并获取回应

#### 方法 1：通过飞书群聊

在配置好的飞书群聊中，直接 @ 机器人：

```
@xianyu-commander 启动今日例行任务
```

#### 方法 2：通过 OpenClaw CLI

```bash
# 直接向 agent 发送消息
openclaw agent send --agent xianyu-commander --message "启动今日例行任务"
```

#### 方法 3：通过 API

```bash
curl -X POST "http://localhost:18789/api/agent/send" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "xianyu-commander",
    "message": "启动今日例行任务"
  }'
```

### 8. 深度工作模式完整示例

#### 创建任务配置文件

```bash
cat > /root/.openclaw/workspace/xianyu-automation/task-progress.json << 'EOF'
{
  "taskId": "xianyu-daily-2026-03-14",
  "taskName": "咸鱼每日例行任务",
  "status": "in_progress",
  "currentPhase": 0,
  "completedPhases": 0,
  "totalPhases": 5,
  "lastUpdated": "2026-03-14T18:00:00Z",
  "checkpointsDir": "/root/.openclaw/workspace/xianyu-automation/cache/checkpoints",
  "cacheDir": "/root/.openclaw/workspace/xianyu-automation/cache/temp",
  "executionMode": "confirmation",
  "userPreferences": {
    "preferredAction": "ask-critical",
    "autoFallbackToUnattended": true,
    "fallbackTimeout": 7200000,
    "nightModeEnabled": true,
    "nightModeStart": "22:00",
    "nightModeEnd": "08:00"
  },
  "notification": {
    "lastReminder": null,
    "reminderCount": 0,
    "remindersSent": []
  },
  "phases": {
    "phase1": {
      "name": "数据分析",
      "status": "pending",
      "subagent": "xianyu-data-analyst",
      "timeout": 1800000,
      "maxRetries": 3,
      "retries": 0,
      "checkpoint": "phase1-data-analysis.json",
      "output": "输出/每日复盘报告.md",
      "cacheFile": "phase1-cache.json",
      "requiresConfirmation": false,
      "critical": false
    },
    "phase2": {
      "name": "内容创作",
      "status": "pending",
      "subagent": "xianyu-content-creator",
      "timeout": 1800000,
      "maxRetries": 3,
      "retries": 0,
      "checkpoint": "phase2-content.json",
      "output": {
        "文案": "输出/商品文案.md",
        "图片": "输出/封面图片.png"
      },
      "cacheFile": "phase2-cache.json",
      "requiresConfirmation": false,
      "critical": false
    },
    "phase3": {
      "name": "违禁词审核",
      "status": "pending",
      "subagent": "xianyu-content-creator",
      "timeout": 900000,
      "maxRetries": 3,
      "retries": 0,
      "checkpoint": "phase3-audit.json",
      "output": "输出/违禁词审核报告.md",
      "cacheFile": "phase3-cache.json",
      "requiresConfirmation": false,
      "critical": false
    },
    "phase4": {
      "name": "商品上架",
      "status": "pending",
      "subagent": "xianyu-operator",
      "timeout": 1800000,
      "maxRetries": 3,
      "retries": 0,
      "checkpoint": "phase4-listing.json",
      "output": "输出/上架结果.json",
      "cacheFile": "phase4-cache.json",
      "requiresConfirmation": true,
      "critical": true,
      "confirmationTimeout": 3600000,
      "requiresGatewayRestart": false
    },
    "phase5": {
      "name": "同步到 Gitee",
      "status": "pending",
      "subagent": "xianyu-commander",
      "timeout": 300000,
      "maxRetries": 3,
      "retries": 0,
      "checkpoint": "phase5-sync.json",
      "output": "输出/同步日志.md",
      "cacheFile": "phase5-cache.json",
      "requiresConfirmation": false,
      "critical": false
    }
  }
}
EOF
```

#### 创建 HEARTBEAT-TASK.md

```bash
cat > /root/.openclaw/workspace/xianyu-automation/HEARTBEAT-TASK.md << 'EOF'
# 咸鱼任务检查清单

1. 读取 /root/.openclaw/workspace/xianyu-automation/task-progress.json
2. 检查 /root/.openclaw/workspace/xianyu-automation/cache/checkpoints/ 目录
3. 比对检查点和任务进度，更新状态
4. 如果阶段完成但下一阶段未启动，自动推进
5. 如果下一阶段需要确认，检查是否已收到用户回复
6. 如果确认超时，自动降级到无人模式
7. 如果所有阶段完成，同步到 Gitee
8. 记录操作日志
9. 如果没有需要推进的内容，回复 HEARTBEAT_OK
EOF
```

#### 配置 Heartbeat

```bash
# 在 openclaw.json 中配置
openclaw config set agents.defaults.heartbeat.every "10m"
openclaw config set agents.defaults.heartbeat.target "last"
openclaw config set agents.defaults.heartbeat.prompt "Read /root/.openclaw/workspace/xianyu-automation/HEARTBEAT-TASK.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK."

# 重启 Gateway
openclaw gateway restart
```

### 9. 完整的热加载指令序列

以下是一次性配置整个咸鱼自动化项目的完整指令：

```bash
# ===== 1. 配置绘图模型 =====
openclaw config set agents.defaults.imageModel "https://your-third-party-api.com/v1/images/generations"
openclaw config set agents.defaults.imageModelProvider "openai"
openclaw config set agents.defaults.imageModelKey "your-api-key"

# ===== 2. 配置咸鱼 agents =====
# 咸鱼总指挥
openclaw config set agents.customAgents.xianyu-commander.model "zai/glm-4.7"
openclaw config set agents.customAgents.xianyu-commander.cwd "/root/.openclaw/workspace/xianyu-automation"
openclaw config set agents.customAgents.xianyu-commander.skills '["complex-task-subagent", "tavily-search"]'

# 咸鱼数据分析
openclaw config set agents.customAgents.xianyu-data-analyst.model "zai/glm-4.7"
openclaw config set agents.customAgents.xianyu-data-analyst.cwd "/root/.openclaw/workspace/xianyu-automation"
openclaw config set agents.customAgents.xianyu-data-analyst.skills '["tavily-search"]'

# 咸鱼内容创作
openclaw config set agents.customAgents.xianyu-content-creator.model "zai/glm-4.7"
openclaw config set agents.customAgents.xianyu-content-creator.cwd "/root/.openclaw/workspace/xianyu-automation"
openclaw config set agents.customAgents.xianyu-content-creator.skills '["complex-task-subagent"]'

# 咸鱼操作员
openclaw config set agents.customAgents.xianyu-operator.model "zai/glm-4.7"
openclaw config set agents.customAgents.xianyu-operator.cwd "/root/.openclaw/workspace/xianyu-automation"
openclaw config set agents.customAgents.xianyu-operator.skills '["complex-task-subagent", "tavily-search"]'

# ===== 3. 配置权限控制 =====
openclaw config set agents.accessControl.xianyu-commander.canCall '["xianyu-data-analyst", "xianyu-content-creator", "xianyu-operator"]'
openclaw config set agents.accessControl.xianyu-commander.cannotCall '[]'

openclaw config set agents.accessControl.xianyu-data-analyst.canCall '[]'
openclaw config set agents.accessControl.xianyu-data-analyst.cannotCall '["xianyu-commander", "xianyu-content-creator", "xianyu-operator"]'

openclaw config set agents.accessControl.xianyu-content-creator.canCall '[]'
openclaw config set agents.accessControl.xianyu-content-creator.cannotCall '["xianyu-commander", "xianyu-data-analyst", "xianyu-operator"]'

openclaw config set agents.accessControl.xianyu-operator.canCall '[]'
openclaw config set agents.accessControl.xianyu-operator.cannotCall '["xianyu-commander", "xianyu-data-analyst", "xianyu-content-creator"]'

# ===== 4. 配置飞书群聊默认 agent =====
openclaw config set feishu.defaultAgentForGroup.oc_2495bf92d31c385fc9818642325fb3d0 "xianyu-commander"

# ===== 5. 配置 Heartbeat =====
openclaw config set agents.defaults.heartbeat.every "10m"
openclaw config set agents.defaults.heartbeat.target "last"
openclaw config set agents.defaults.heartbeat.prompt "Read /root/.openclaw/workspace/xianyu-automation/HEARTBEAT-TASK.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK."

# ===== 6. 重启 Gateway =====
openclaw gateway restart
```

### 10. 使用 jq 修改配置的完整指令

```bash
# ===== 1. 备份原配置 =====
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup

# ===== 2. 配置绘图模型 =====
jq '.agents.defaults.imageModel = "https://your-third-party-api.com/v1/images/generations"' \
   ~/.openclaw/openclaw.json > /tmp/openclaw.json && mv /tmp/openclaw.json ~/.openclaw/openclaw.json

jq '.agents.defaults.imageModelProvider = "openai"' \
   ~/.openclaw/openclaw.json > /tmp/openclaw.json && mv /tmp/openclaw.json ~/.openclaw/openclaw.json

jq '.agents.defaults.imageModelKey = "your-api-key"' \
   ~/.openclaw/openclaw.json > /tmp/openclaw.json && mv /tmp/openclaw.json ~/.openclaw/openclaw.json

# ===== 3. 配置咸鱼 agents =====
jq '.agents.customAgents["xianyu-commander"] = {
  "model": "zai/glm-4.7",
  "cwd": "/root/.openclaw/workspace/xianyu-automation",
  "skills": ["complex-task-subagent", "tavily-search"]
}' ~/.openclaw/openclaw.json > /tmp/openclaw.json && mv /tmp/openclaw.json ~/.openclaw/openclaw.json

jq '.agents.customAgents["xianyu-data-analyst"] = {
  "model": "zai/glm-4.7",
  "cwd": "/root/.openclaw/workspace/xianyu-automation",
  "skills": ["tavily-search"]
}' ~/.openclaw/openclaw.json > /tmp/openclaw.json && mv /tmp/openclaw.json ~/.openclaw/openclaw.json

jq '.agents.customAgents["xianyu-content-creator"] = {
  "model": "zai/glm-4.7",
  "cwd": "/root/.openclaw/workspace/xianyu-automation",
  "skills": ["complex-task-subagent"]
}' ~/.openclaw/openclaw.json > /tmp/openclaw.json && mv /tmp/openclaw.json ~/.openclaw/openclaw.json

jq '.agents.customAgents["xianyu-operator"] = {
  "model": "zai/glm-4.7",
  "cwd": "/root/.openclaw/workspace/xianyu-automation",
  "skills": ["complex-task-subagent", "tavily-search"]
}' ~/.openclaw/openclaw.json > /tmp/openclaw.json && mv /tmp/openclaw.json ~/.openclaw/openclaw.json

# ===== 4. 配置权限控制 =====
jq '.agents.accessControl["xianyu-commander"] = {
  "canCall": ["xianyu-data-analyst", "xianyu-content-creator", "xianyu-operator"],
  "cannotCall": []
}' ~/.openclaw/openclaw.json > /tmp/openclaw.json && mv /tmp/openclaw.json ~/.openclaw/openclaw.json

jq '.agents.accessControl["xianyu-data-analyst"] = {
  "canCall": [],
  "cannotCall": ["xianyu-commander", "xianyu-content-creator", "xianyu-operator"]
}' ~/.openclaw/openclaw.json > /tmp/openclaw.json && mv /tmp/openclaw.json ~/.openclaw/openclaw.json

jq '.agents.accessControl["xianyu-content-creator"] = {
  "canCall": [],
  "cannotCall": ["xianyu-commander", "xianyu-data-analyst", "xianyu-operator"]
}' ~/.openclaw/openclaw.json > /tmp/openclaw.json && mv /tmp/openclaw.json ~/.openclaw/openclaw.json

jq '.agents.accessControl["xianyu-operator"] = {
  "canCall": [],
  "cannotCall": ["xianyu-commander", "xianyu-data-analyst", "xianyu-content-creator"]
}' ~/.openclaw/openclaw.json > /tmp/openclaw.json && mv /tmp/openclaw.json ~/.openclaw/openclaw.json

# ===== 5. 配置飞书群聊默认 agent =====
jq '.feishu.defaultAgentForGroup["oc_2495bf92d31c385fc9818642325fb3d0"] = "xianyu-commander"' \
   ~/.openclaw/openclaw.json > /tmp/openclaw.json && mv /tmp/openclaw.json ~/.openclaw/openclaw.json

# ===== 6. 配置 Heartbeat =====
jq '.agents.defaults.heartbeat = {
  "every": "10m",
  "target": "last",
  "prompt": "Read /root/.openclaw/workspace/xianyu-automation/HEARTBEAT-TASK.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK."
}' ~/.openclaw/openclaw.json > /tmp/openclaw.json && mv /tmp/openclaw.json ~/.openclaw/openclaw.json

# ===== 7. 验证配置 =====
cat ~/.openclaw/openclaw.json | jq '.agents'

# ===== 8. 重启 Gateway =====
openclaw gateway restart
```

### 11. 创建初始化脚本

为了方便后续使用，创建一个初始化脚本：

```bash
cat > /root/.openclaw/workspace/xianyu-automation/scripts/init-xianyu-config.sh << 'EOF'
#!/bin/bash
# 咸鱼自动化项目配置初始化脚本

echo "开始配置咸鱼自动化项目..."

# 检查 OpenClaw 是否运行
if ! openclaw gateway status &>/dev/null; then
  echo "OpenClaw Gateway 未运行，正在启动..."
  openclaw gateway start
fi

# 1. 配置绘图模型
echo "[1/6] 配置绘图模型..."
openclaw config set agents.defaults.imageModel "https://your-third-party-api.com/v1/images/generations"
openclaw config set agents.defaults.imageModelProvider "openai"
openclaw config set agents.defaults.imageModelKey "your-api-key"

# 2. 配置咸鱼 agents
echo "[2/6] 配置咸鱼 agents..."
openclaw config set agents.customAgents.xianyu-commander.model "zai/glm-4.7"
openclaw config set agents.customAgents.xianyu-commander.cwd "/root/.openclaw/workspace/xianyu-automation"
openclaw config set agents.customAgents.xianyu-commander.skills '["complex-task-subagent", "tavily-search"]'

openclaw config set agents.customAgents.xianyu-data-analyst.model "zai/glm-4.7"
openclaw config set agents.customAgents.xianyu-data-analyst.cwd "/root/.openclaw/workspace/xianyu-automation"
openclaw config set agents.customAgents.xianyu-data-analyst.skills '["tavily-search"]'

openclaw config set agents.customAgents.xianyu-content-creator.model "zai/glm-4.7"
openclaw config set agents.customAgents.xianyu-content-creator.cwd "/root/.openclaw/workspace/xianyu-automation"
openclaw config set agents.customAgents.xianyu-content-creator.skills '["complex-task-subagent"]'

openclaw config set agents.customAgents.xianyu-operator.model "zai/glm-4.7"
openclaw config set agents.customAgents.xianyu-operator.cwd "/root/.openclaw/workspace/xianyu-automation"
openclaw config set agents.customAgents.xianyu-operator.skills '["complex-task-subagent", "tavily-search"]'

# 3. 配置权限控制
echo "[3/6] 配置权限控制..."
openclaw config set agents.accessControl.xianyu-commander.canCall '["xianyu-data-analyst", "xianyu-content-creator", "xianyu-operator"]'
openclaw config set agents.accessControl.xianyu-commander.cannotCall '[]'

openclaw config set agents.accessControl.xianyu-data-analyst.canCall '[]'
openclaw config set agents.accessControl.xianyu-data-analyst.cannotCall '["xianyu-commander", "xianyu-content-creator", "xianyu-operator"]'

openclaw config set agents.accessControl.xianyu-content-creator.canCall '[]'
openclaw config set agents.accessControl.xianyu-content-creator.cannotCall '["xianyu-commander", "xianyu-data-analyst", "xianyu-operator"]'

openclaw config set agents.accessControl.xianyu-operator.canCall '[]'
openclaw config set agents.accessControl.xianyu-operator.cannotCall '["xianyu-commander", "xianyu-data-analyst", "xianyu-content-creator"]'

# 4. 配置飞书群聊默认 agent
echo "[4/6] 配置飞书群聊默认 agent..."
openclaw config set feishu.defaultAgentForGroup.oc_2495bf92d31c385fc9818642325fb3d0 "xianyu-commander"

# 5. 配置 Heartbeat
echo "[5/6] 配置 Heartbeat..."
openclaw config set agents.defaults.heartbeat.every "10m"
openclaw config set agents.defaults.heartbeat.target "last"
openclaw config set agents.defaults.heartbeat.prompt "Read /root/.openclaw/workspace/xianyu-automation/HEARTBEAT-TASK.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK."

# 6. 重启 Gateway
echo "[6/6] 重启 Gateway..."
openclaw gateway restart

echo "✅ 咸鱼自动化项目配置完成！"
echo ""
echo "使用方法："
echo "1. 在飞书群聊中 @xianyu-commander 启动任务"
echo "2. 或使用命令: openclaw agent send --agent xianyu-commander --message '启动任务'"
EOF

chmod +x /root/.openclaw/workspace/xianyu-automation/scripts/init-xianyu-config.sh
```

---

**技能版本**：2.0.0
**最后更新**：2026-03-15

## 更新日志

### v2.0.0 (2026-03-15)

**新增功能：**

1. **🌙 夜间无人模式**
   - 提前收集用户偏好和必要信息
   - 在用户休息期间自助决策完成任务
   - 支持预配置操作权限和降级策略

2. **🔑 关键节点确认模式**
   - 重要决策点自动提醒用户
   - 超时自动降级到无人模式
   - 可配置提醒间隔和最大提醒次数

3. **💾 智能缓存管理**
   - 子代理工作期间使用临时缓存
   - 正常完成自动回收缓存
   - 异常中断可从缓存恢复进度
   - 支持缓存清理和统计

4. **⚡ 深度工作模式**
   - 完全无人值守的自动化任务执行
   - 集成 Heartbeat 实现自动推进
   - 支持多 Agent 协作工作区
   - 完整的配置指南和热加载指令

**新增脚本：**

- `scripts/select-execution-mode.sh` - 执行模式选择脚本
- `scripts/cache-manager.sh` - 子代理缓存管理脚本
- `scripts/notification-manager.sh` - 通知提醒管理脚本

**文档改进：**

- 添加了完整的深度工作模式配置指南（以 xianyu-automation 为例）
- 详细的热加载指令和 jq 配置示例
- 飞书群聊配置说明
- Agent 权限控制配置
