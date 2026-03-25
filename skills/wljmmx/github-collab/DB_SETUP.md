# 数据库配置管理说明

## 📋 概述

系统使用 SQLite 数据库管理 Agent 配置，实现配置持久化和动态更新。

## 🎯 数据库结构

### 表结构

#### 1. `agents` 表
存储 Agent 基本信息

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | INTEGER | 主键，自增 |
| `name` | TEXT | Agent 名称（唯一） |
| `role` | TEXT | Agent 角色 |
| `target` | TEXT | QQ 地址 |
| `description` | TEXT | 描述 |
| `capabilities` | TEXT | 能力列表（JSON） |
| `is_active` | INTEGER | 是否激活（1/0） |
| `created_at` | DATETIME | 创建时间 |
| `updated_at` | DATETIME | 更新时间 |

#### 2. `agent_configs` 表
存储 Agent 额外配置

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | INTEGER | 主键，自增 |
| `agent_name` | TEXT | Agent 名称 |
| `config_key` | TEXT | 配置键 |
| `config_value` | TEXT | 配置值 |
| `created_at` | DATETIME | 创建时间 |
| `updated_at` | DATETIME | 更新时间 |

#### 3. `message_logs` 表
存储消息日志

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | INTEGER | 主键，自增 |
| `from_agent` | TEXT | 发送方 |
| `to_agent` | TEXT | 接收方 |
| `message` | TEXT | 消息内容 |
| `status` | TEXT | 状态 |
| `created_at` | DATETIME | 创建时间 |

## 🚀 快速开始

### 1. 初始化数据库

```bash
# 初始化数据库和默认 Agent
npm run db:init
```

输出示例：
```
🚀 开始初始化数据库...

✅ 数据库已打开：/workspace/github-collab-git/db/agents.db
✅ agents 表已创建
✅ agent_configs 表已创建
✅ message_logs 表已创建
✅ 已初始化 4 个默认 Agent

✅ 数据库初始化完成！
```

### 2. 查看 Agent 列表

```bash
# 列出所有 Agent
npm run db:list
```

输出示例：
```
=== 当前 Agent 列表 ===

1. main-agent
   角色：main
   地址：qqbot:c2c:MAIN_AGENT_PLACEHOLDER
   描述：任务管理与调度
   状态：✅ 活跃

2. coder-agent
   角色：coder
   地址：qqbot:c2c:CODER_AGENT_PLACEHOLDER
   描述：代码开发
   状态：✅ 活跃

...
```

### 3. 更新 Agent 地址

```bash
# 更新指定 Agent 的地址
npm run db:update update <agent-name> <new-address>
```

示例：
```bash
npm run db:update update coder-agent qqbot:c2c:NEW_CODER_ID
```

### 4. 同步配置到代码

```bash
# 同步数据库配置到 agent-addresses.js
npm run db:sync
```

### 5. 验证配置

```bash
# 验证配置是否正确
npm run db:validate
```

## 📝 代码集成

### 在代码中使用数据库配置

```javascript
const { getAllAgents, getAgentAddress, updateAgentAddress } = require('./db/agent-manager');

// 获取所有 Agent
const agents = await getAllAgents();
console.log(agents);

// 获取特定 Agent 地址
const coderAddress = await getAgentAddress('coder-agent');
console.log(coderAddress);

// 更新 Agent 地址
await updateAgentAddress('coder-agent', 'qqbot:c2c:NEW_ID');
```

### 会话开始时自动校验

```javascript
const { validateSessionConfig } = require('./db/session-validator');

// 在会话开始时调用
const result = await validateSessionConfig();
if (result.valid) {
  console.log('✅ 配置验证通过');
} else {
  console.error('❌ 配置验证失败:', result.error);
}
```

## 🔧 管理命令

| 命令 | 说明 |
|------|------|
| `npm run db:init` | 初始化数据库 |
| `npm run db:list` | 列出所有 Agent |
| `npm run db:update update <name> <address>` | 更新 Agent 地址 |
| `npm run db:sync` | 同步配置到代码 |
| `npm run db:validate` | 验证配置 |

## ⚠️ 注意事项

1. **地址格式**：必须使用 `qqbot:c2c:USER_ID` 或 `qqbot:group:GROUP_ID` 格式
2. **自动同步**：每次更新数据库后，配置会自动同步到 `agent-addresses.js`
3. **会话校验**：每次对话开始时会自动校验配置
4. **错误处理**：配置错误时会有降级机制

## 🔄 工作流程

```
1. 初始化数据库
   ↓
2. 配置 Agent 地址（通过脚本或代码）
   ↓
3. 同步配置到代码文件
   ↓
4. 会话开始时自动校验
   ↓
5. 使用最新配置发送消息
```

## 📊 监控与日志

### 查看消息日志

```javascript
const { getMessageLogs } = require('./db/agent-manager');

const logs = await getMessageLogs(10);
console.log(logs);
```

### 记录自定义活动

```javascript
const { logSessionActivity } = require('./db/session-validator');

await logSessionActivity('coder-agent', 'task-completed', {
  task: '实现登录功能',
  duration: '30 minutes'
});
```

## 🆘 故障排除

### 问题：数据库文件不存在

**解决**：
```bash
npm run db:init
```

### 问题：配置不同步

**解决**：
```bash
npm run db:sync
```

### 问题：地址格式错误

**解决**：
确保地址格式为 `qqbot:c2c:USER_ID` 或 `qqbot:group:GROUP_ID`

### 问题：Agent 未找到

**解决**：
```bash
npm run db:list  # 查看已配置的 Agent
```

## 📞 技术支持

如有问题，请联系：
- 技术支持：OpenClaw Team
- 文档：https://openclaw.ai/docs
- 社区：https://community.openclaw.ai