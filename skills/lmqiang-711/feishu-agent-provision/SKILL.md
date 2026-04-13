---
name: feishu-agent-provision
description: 创建绑定飞书群聊的专用 Agent。支持：询问配置问题、创建独立 workspace、注册 agent 到 OpenClaw 配置、绑定飞书群到该 agent、设置每日/每周定时报告。触发条件：用户说"创建一个飞书agent"、"创建项目agent"、"新建agent并绑定飞书群"、"创建一个专属agent"、或需要新建一个在飞书群里独立响应的助理。
---

# feishu-agent-provision

为指定飞书群创建一个专属 Agent，独立响应群内消息并执行定时报告任务。

## 工作流程

### 第一步：收集配置（询问用户）

依次询问以下问题，确认所有配置：

1. **Agent ID** — 英文ID，如 `ctyun`、`project-x`（字母+数字+短横线）
2. **Agent 中文名** — 对外显示名称，如"**业务代理"
3. **飞书群 ID** — 形如 `oc_xxx`（确认已加入机器人的群）
4. **Agent 职责描述** — 这个 agent 负责什么？（简要描述）
5. **汇报时间**：
   - 每日汇报时间（默认 17:00）
   - 每周汇报时间（默认周五 17:00）
6. **数据文件路径**（可选）— agent 需要读取的数据文件绝对路径，如 `/Users/xxx/.project/data.json`

> 如果用户提供了完整信息，跳过询问直接使用。

### 第二步：创建 Workspace

```bash
AGENT_ID="<id>"
AGENT_DIR="$HOME/.openclaw/agents/$AGENT_ID/workspace"
mkdir -p "$AGENT_DIR/memory"
```

### 第三步：写入 Workspace 文件

**SOUL.md** — Agent 身份定义，包含：
- Agent 名称和职责
- 项目背景和关键数据
- 工作原则和优先级定义
- 汇报飞书群 ID
- 语气风格

**USER.md** — 服务对象信息

**AGENTS.md** — 标准 workspace 指引（从主 workspace 复制）

**HEARTBEAT.md** — 空或仅有注释

### 第四步：注册 Agent 到 OpenClaw 配置

使用 `gateway config.patch` 注入：

```json
{
  "agents": {
    "list": [{
      "id": "<AGENT_ID>",
      "workspace": "<AGENT_DIR>",
      "identity": { "name": "<中文名>" }
    }]
  },
  "bindings": [{
    "type": "route",
    "agentId": "<AGENT_ID>",
    "match": {
      "channel": "feishu",
      "peer": { "kind": "group", "id": "<飞书群ID>" }
    }
  }]
}
```

### 第五步：验证路由

发送测试消息到对应飞书群，检查日志确认路由成功：

```bash
openclaw logs --follow | grep "dispatching to agent"
```

确认日志出现 `agent:<AGENT_ID>:feishu:group:<飞书群ID>`

### 第六步：设置定时报告（如有需要）

使用 `cron add` 创建定时任务，`sessionTarget: "session:<AGENT_ID>-reports"`：

- **日报**：每周一至周五指定时间（默认 17:00）
- **周报**：每周指定时间（默认周五 17:00），周五时与日报合并发送

Cron payload 示例：
```json
{
  "kind": "agentTurn",
  "message": "<报告提示词，包含数据文件路径和报告内容要求>",
  "timeoutSeconds": 120
}
```

## 注意事项

- 始终使用绝对路径，勿用 `~`（agent 运行时不会展开）
- SOUL.md 要具体，包含实际的项目数据（KPI、合作模式、优先名单等）
- 飞书群必须已在 `channels.feishu.groupAllowFrom` 中配置
- 创建完成后在飞书群实测：发送一条消息，确认由对应 agent 响应而非主 agent

## 故障排查（Troubleshooting）

### 问题1：Agent 未响应群消息

**症状**：在飞书群发送消息，没有收到回复。

**排查步骤**：

1. 检查 Gateway 是否运行
   ```bash
   openclaw gateway status
   ```

2. 检查飞书群是否在白名单
   ```bash
   openclaw config get channels.feishu.groupAllowFrom
   ```
   确认群 ID 在列表中。

3. 检查日志路由
   ```bash
   openclaw logs --limit 50 | grep "<飞书群ID>"
   ```
   查看是否有消息到达和 dispatch 记录。

4. 检查 Agent 是否注册成功
   ```bash
   openclaw config get agents.list
   ```
   确认新 Agent ID 在列表中。

### 问题2：消息回退到主 Agent

**症状**：群消息被主 Agent 响应，而不是专属 Agent。

**原因**：binding 路由未生效。

**排查**：

1. 确认 bindings 配置正确：
   ```bash
   openclaw config get bindings
   ```
   检查 `agentId` 是否指向正确的 Agent，`peer.id` 是否是群 ID。

2. 重启 Gateway：
   ```bash
   openclaw gateway restart
   ```
   配置修改后需重启生效。

3. 检查 Gateway 日志中是否有 dispatch 记录：
   ```bash
   openclaw logs | grep "dispatching to agent"
   ```

### 问题3：定时报告未发送

**症状**：cron 任务创建了但没收到报告。

**排查**：

1. 检查 cron 任务状态：
   ```bash
   openclaw cron status
   ```

2. 查看最近运行记录：
   ```bash
   openclaw cron runs <job-id>
   ```

3. 检查报告是否因错误中断：
   ```bash
   openclaw logs | grep "error\|Error"
   ```

4. 常见原因：
   - 数据文件路径错误（使用了 `~` 而非绝对路径）
   - 飞书群 ID 变更或失效
   - API 限流

### 问题4：Agent 回复内容错误

**症状**：Agent 的回复内容不符合预期，如身份混淆、回复逻辑错误。

**排查**：

1. 检查 SOUL.md 是否正确加载：
   - 确认 workspace 路径正确
   - 确认 SOUL.md 内容是最新的

2. 检查是否有缓存冲突：
   - 删除 `memory/` 目录下的缓存文件
   - 使用 `/reset` 重置会话

### 问题5：Gateway 重启后 Agent 失效

**症状**：Gateway 重启后，Agent 不再响应。

**排查**：

1. 确认配置文件未丢失：
   ```bash
   cat ~/.openclaw/openclaw.json | grep -A5 "agents.list"
   ```

2. 确认 workspace 目录未被删除：
   ```bash
   ls ~/.openclaw/agents/<AGENT_ID>/
   ```

3. 重新注册 Agent：
   按第四步重新执行 `gateway config.patch`。

## 最佳实践（Best Practices）

### 命名规范

| 类型 | 规则 | 示例 |
|------|------|------|
| Agent ID | 小写字母 + 数字 + 短横线，不以数字开头 | `cloudbiz`, `space-agent`, `sales-bot` |
| Agent 中文名 | 简洁明了，2-6字 | "项目助手"、"客服专员" |
| 飞书群名称 | 建议与 Agent 职责对应 | "项目进度群"、"客服支持" |

### Workspace 目录结构

推荐创建以下文件：

```
agents/<AGENT_ID>/workspace/
├── SOUL.md      # 必填：Agent 身份定义
├── USER.md      # 必填：服务对象信息
├── AGENTS.md    # 必填：workspace 指引
├── HEARTBEAT.md # 可选：定期任务检查
├── TOOLS.md     # 可选：工具配置
└── memory/      # 必建：会话记忆目录
    └── .gitkeep  # 占位文件
```

### SOUL.md 内容要点

一份好的 SOUL.md 应包含：

1. **身份定义** — "我是谁" + 核心职责
2. **项目背景** — 业务背景、关键数据
3. **工作原则** — 行为准则、优先级
4. **数据来源** — 数据文件路径（必须用绝对路径）
5. **汇报目标** — 飞书群 ID、汇报时间
6. **语气风格** — 沟通风格偏好

### 配置管理

1. **修改前备份** — 每次 `config.patch` 前备份：
   ```bash
   cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup-$(date +%Y%m%d)
   ```

2. **分阶段验证** — 创建后先测试路由，再配置 cron

3. **文档记录** — 在 SOUL.md 中记录飞书群 ID、cron 任务 ID 等关键信息

### 多 Agent 管理

当需要管理多个 Agent 时：

1. 使用统一的命名前缀：`cloud-`, `sales-`, `support-`
2. 在主 workspace 的 MEMORY.md 中记录所有 Agent 状态
3. 定期检查 `agents.list` 配置，清理已停用的 Agent

## 安全建议（Security）

### 1. 凭证管理

- **飞书 App Secret**：不要写入 SOUL.md 或任何可读文件
- **API Key**：如果 Agent 需要调用外部 API，使用环境变量而非硬编码
- **敏感数据**：不要把密码、Token 等敏感信息写入 workspace 文件

### 2. 权限控制

- **最小权限原则**：Agent 只需读取必要的数据文件，不要开放写权限
- **外部操作确认**：Agent 发送消息到外部系统前，建议先确认
- **敏感操作限制**：删除文件、修改配置等操作不要交给 Agent 自动执行

### 3. 配置安全

- **groupAllowFrom 白名单**：只添加信任的飞书群，不要用 `groupPolicy: "open"`
- **requireMention**：对公共群建议设为 `true`，避免误响应
- **定期审查**：定期检查 `bindings` 配置，移除不再使用的绑定

### 4. 监控与审计

- **日志监控**：定期查看 `openclaw logs`，关注异常行为
- **cron 运行记录**：检查定时任务是否有异常失败
- **会话历史**：定期清理不再需要的会话记录

### 5. 备份与恢复

- **定期备份**：备份 `~/.openclaw/openclaw.json` 和 `~/.openclaw/agents/`
- **版本控制**：可以把 workspace 纳入 Git 版本控制
- **快速恢复**：保留最近 3 份配置文件备份

### 6. 信任边界

- **内部 Agent**：Agent 在你的 workspace 内运行，风险可控
- **外部输入**：对群内用户输入保持警惕，Agent 不应执行未经确认的外部命令
- **自动化边界**：定时报告等自动化任务，设置了要定期检查效果

---

> **安全原则**：如果不确定某个操作是否有风险，先问用户确认，再执行。