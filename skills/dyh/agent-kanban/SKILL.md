---
name: agent-kanban
description: OpenClaw Agent Dashboard - A Bloomberg Terminal-style web interface for real-time monitoring of all Agent status, session history, and session file sizes. Use this skill when users need to monitor agents, view agent status, or deploy a kanban dashboard.
---

# Agent Kanban

OpenClaw Agent Dashboard - Bloomberg Terminal Style Interface.

## Features

- **Real-time Monitoring** - View all Agent online status and last active time
- **Auto Grouping** - Group by project prefix (main, pmo, alpha, beta)
- **Session History** - Click cards to view recent conversation history
- **File Viewer** - View Agent's OKR.md, SOUL.md, HEARTBEAT.md
- **Session Size Monitor** - Display .jsonl file size with threshold warnings
- **Font Size Control** - 10px-24px with reset button (R)
- **Bloomberg Style** - Bloomberg Terminal style interface

## Tech Stack

- **Backend**: Node.js + Express
- **Frontend**: React 18 (CDN)
- **Avatar**: DiceBear Pixel Art API
- **API**: OpenClaw Gateway HTTP API

## Quick Start

### 1. Deploy

```bash
# Copy project to destination
cp -r assets/agent-kanban /path/to/destination/
cd /path/to/destination/agent-kanban

# Install dependencies
npm install
```

### 2. Configure

```bash
# Copy config file
cp config.js config.local.js

# Edit config, fill in Gateway Token
# Get token from ~/.openclaw/openclaw.json:
# cat ~/.openclaw/openclaw.json | jq '.gateway.auth.token'
```

Config options:

```javascript
module.exports = {
  server: { port: 3100, host: '0.0.0.0' },
  gateway: {
    url: 'http://127.0.0.1:18789',
    token: 'YOUR_GATEWAY_TOKEN'
  },
  openclaw: { homeDir: '.openclaw', configFilename: 'openclaw.json' },
  refreshInterval: 60000,
  sessionSizeThresholds: { warning: 500, danger: 1024 }
};
```

### 3. Start

```bash
# Ensure Gateway is running
openclaw gateway start

# Start Kanban
npm start

# Access
# http://localhost:3100
```

## Prerequisites

1. OpenClaw installed and running
2. Gateway started (`openclaw gateway start`)
3. Node.js 18+ installed

## UI Operations

| Action | Description |
|--------|-------------|
| Click agent card | View details (files + messages) |
| `-` / `+` button | Adjust font size (10-24px) |
| `R` button | Reset font size to 13px |
| `CLOSE` button | Close agent + hide right panel |
| `HIDE` button | Hide right panel |

## Get Gateway Token

```bash
# Method 1: From config file
cat ~/.openclaw/openclaw.json | jq '.gateway.auth.token'

# Method 2: From CLI
openclaw gateway status
```

---

# Agent Kanban（中文）

OpenClaw Agent 状态监控面板 - Bloomberg Terminal 风格界面。

## 功能特性

- **实时监控** - 显示所有 Agent 的在线状态、最后活跃时间
- **自动分组** - 按项目前缀自动分组（main、pmo、alpha、beta）
- **会话历史** - 点击卡片查看最近的对话记录
- **文件查看** - 查看 Agent 的 OKR.md、SOUL.md、HEARTBEAT.md
- **Session 大小监控** - 显示 .jsonl 文件大小，超过阈值高亮警告
- **字号调节** - 10px-24px，带重置按钮
- **彭博风格** - Bloomberg Terminal 风格界面

## 技术栈

- **后端**: Node.js + Express
- **前端**: React 18 (CDN)
- **头像**: DiceBear Pixel Art API
- **API**: OpenClaw Gateway HTTP API

## 快速开始

### 1. 部署

```bash
cp -r assets/agent-kanban /path/to/destination/
cd /path/to/destination/agent-kanban
npm install
```

### 2. 配置

```bash
cp config.js config.local.js
# 编辑 config.local.js，填入 Gateway Token
```

### 3. 启动

```bash
openclaw gateway start
npm start
# 访问 http://localhost:3100
```

## 获取 Gateway Token

```bash
cat ~/.openclaw/openclaw.json | jq '.gateway.auth.token'
```

---

## More Documentation

See `references/README.md` for full documentation.