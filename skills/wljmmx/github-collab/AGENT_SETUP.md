# Agent 独立地址配置说明（方案 C）

## 📋 概述

方案 C 使用独立的 QQ 机器人地址，每个 Agent 都有独立的接收端，实现真正的多 Agent 协作。

## 🎯 Agent 角色

| Agent | 角色 | 功能 | 地址变量 |
|-------|------|------|---------|
| **main-agent** | 任务管理 | 任务调度、报告接收 | `MAIN_AGENT_QQ_ID` |
| **coder-agent** | 代码开发 | 代码编写、调试、测试 | `CODER_AGENT_QQ_ID` |
| **checker-agent** | 审查测试 | 代码审查、质量保证 | `CHECKER_AGENT_QQ_ID` |
| **memowriter-agent** | 文档记录 | 文档编写、知识管理 | `MEMOWRITER_AGENT_QQ_ID` |

## 🚀 快速开始

### 1. 配置环境变量

复制 `.env.example` 到 `.env` 并修改：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```bash
# QQ Bot 配置
QQ_ENABLED=true
QQ_TOKEN=your_qq_bot_token

# 独立 Agent 地址
MAIN_AGENT_QQ_ID=qqbot:c2c:YOUR_MAIN_AGENT_QQ_ID
CODER_AGENT_QQ_ID=qqbot:c2c:YOUR_CODER_AGENT_QQ_ID
CHECKER_AGENT_QQ_ID=qqbot:c2c:YOUR_CHECKER_AGENT_QQ_ID
MEMOWRITER_AGENT_QQ_ID=qqbot:c2c:YOUR_MEMOWRITER_AGENT_QQ_ID
```

### 2. 获取 QQ 机器人地址

#### 方法 1：创建 QQ 群组（推荐）

1. 创建 QQ 群组
2. 邀请所有 Agent 机器人加入
3. 使用群组地址：`qqbot:group:GROUP_ID`

#### 方法 2：独立 QQ 机器人

1. 为每个 Agent 创建独立的 QQ 机器人
2. 获取每个机器人的用户 ID
3. 使用私聊地址：`qqbot:c2c:BOT_USER_ID`

### 3. 测试消息发送

运行测试脚本：

```bash
node examples/agent-messaging.js
```

## 📝 代码示例

### 向单个 Agent 发送消息

```javascript
const { sendToAgent } = require('./examples/agent-messaging');

// 向 Coder Agent 发送任务
await sendToAgent('coder-agent', '实现登录功能', {
  priority: 'high',
  deadline: '2026-03-22'
});
```

### 向所有 Agent 发送消息

```javascript
const { sendToAllAgents } = require('./examples/agent-messaging');

// 向所有 Agent 广播
await sendToAllAgents('系统维护通知', {
  maintenanceTime: '2026-03-22 02:00',
  duration: '2 hours'
});
```

### 获取 Agent 信息

```javascript
const { getAgentInfo, getAgentAddress } = require('./agent-addresses');

// 获取 Coder Agent 信息
const coderInfo = getAgentInfo('coder-agent');
console.log(coderInfo);
// {
//   role: 'coder',
//   target: 'qqbot:c2c:CODER_AGENT_QQ_ID',
//   description: '代码开发',
//   capabilities: ['code-writing', 'debugging', 'testing']
// }

// 获取地址
const coderAddress = getAgentAddress('coder-agent');
console.log(coderAddress);
// 'qqbot:c2c:CODER_AGENT_QQ_ID'
```

## 🔧 配置管理

### 动态切换 Agent 地址

```javascript
const { AGENT_ADDRESSES } = require('./agent-addresses');

// 临时修改 Main Agent 地址
AGENT_ADDRESSES['main-agent'].target = 'qqbot:c2c:NEW_MAIN_AGENT_ID';
```

### 添加新 Agent

```javascript
// 在 agent-addresses.js 中添加
const AGENT_ADDRESSES = {
  // ... existing agents
  'new-agent': {
    role: 'new',
    target: process.env.NEW_AGENT_QQ_ID || 'qqbot:c2c:NEW_AGENT_PLACEHOLDER',
    description: '新功能',
    capabilities: ['feature-a', 'feature-b']
  }
};
```

## ⚠️ 注意事项

1. **地址格式**：必须使用 `qqbot:c2c:USER_ID` 或 `qqbot:group:GROUP_ID` 格式
2. **权限配置**：确保 QQ 机器人有发送消息的权限
3. **环境变量**：生产环境不要硬编码地址，使用环境变量
4. **错误处理**：发送消息失败时应有重试机制

## 📊 监控与日志

### 查看发送状态

```javascript
const result = await sendToAgent('coder-agent', '任务');
console.log('发送状态:', result.result);
```

### 日志输出

```
✅ 消息已发送到 coder-agent: {
  channel: 'qqbot',
  messageId: 'ROBOT1.0_...'
}
```

## 🔄 回滚方案

如果需要回滚到方案 A（所有消息发给你）：

```bash
# 修改 .env 文件
QQ_TARGET=qqbot:c2c:YOUR_QQ_ID

# 修改 config.js 使用默认地址
target: process.env.QQ_TARGET || 'qqbot:c2c:YOUR_QQ_ID'
```

## 📞 技术支持

如有问题，请联系：
- 技术支持：OpenClaw Team
- 文档：https://openclaw.ai/docs
- 社区：https://community.openclaw.ai