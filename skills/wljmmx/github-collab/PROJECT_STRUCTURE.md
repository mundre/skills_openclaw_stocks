# GitHub 协作 Agent 系统 - 完整项目结构

## 📁 目录结构

```
github-collab-git/
├── 📄 README.md                    # 项目主文档
├── 📄 SKILL.md                     # Agent 技能说明
├── 📄 AGENT_SETUP.md               # Agent 设置指南
├── 📄 DB_SETUP.md                  # 数据库设置文档
├── 📄 CHANGELOG.md                 # 更新日志
├── 📄 package.json                 # 项目配置和脚本
├── 📄 package-lock.json            # 依赖锁定文件
├── 📄 index.js                     # 入口文件
├── 📄 agent-addresses.js           # Agent 地址配置
├── 📄 task-manager-state.json      # 任务管理器状态
├── 📄 _meta.json                   # 元数据
│
├── 📂 db/                          # 数据库模块
│   ├── 📄 README.md               # 数据库模块文档
│   ├── 📄 init.js                 # 数据库初始化
│   ├── 📄 agent-manager.js        # Agent 管理模块
│   ├── 📄 config-manager.js       # 配置管理器
│   ├── 📄 config-sync.js          # 配置同步工具
│   ├── 📄 session-validator.js    # 会话验证器
│   └── 📄 task-manager.js         # 任务管理模块 ✨
│
├── 📂 core/                        # 核心模块
│   ├── 📄 main-controller.js      # 主控制器
│   ├── 📄 agent-binding.js        # Agent 绑定
│   ├── 📄 openclaw-message.js     # OpenClaw 消息处理
│   ├── 📄 stp-integrator.js       # STP 集成器
│   ├── 📄 stp-integrator-enhanced.js  # 增强版 STP
│   ├── 📄 task-manager.js         # 任务管理器
│   └── 📄 task-manager-enhanced.js  # 增强版任务管理器
│
├── 📂 scripts/                     # 管理脚本
│   ├── 📄 README.md               # 脚本使用文档
│   ├── 📄 config-cli.js           # 统一配置管理 CLI ✨
│   ├── 📄 init-db.js              # 数据库初始化脚本
│   ├── 📄 sync-config.js          # 配置同步脚本
│   ├── 📄 validate-config.js      # 配置验证脚本
│   ├── 📄 update-agent.js         # Agent 更新脚本
│   ├── 📄 main.js                 # 主脚本
│   ├── 📄 project-manager.js      # 项目管理器
│   ├── 📄 scheduler.js            # 调度器
│   ├── 📄 agent-assign.js         # Agent 分配
│   ├── 📄 task-breakdown.js       # 任务分解
│   ├── 📄 progress-report.js      # 进度报告
│   └── 📄 test.js                 # 测试脚本
│
├── 📂 test/                        # 测试模块
│   └── 📄 task-test.js            # 任务管理测试 ✨
│
└── 📂 .env.example                 # 环境变量示例
```

## 📊 核心模块说明

### 1️⃣ **数据库模块 (db/)**

| 文件 | 说明 | 功能 |
|------|------|------|
| `init.js` | 数据库初始化 | 创建表结构、初始化默认数据 |
| `agent-manager.js` | Agent 管理 | 增删改查 Agent 配置 |
| `config-manager.js` | 配置管理器 | 统一配置管理、备份恢复 ✨ |
| `config-sync.js` | 配置同步 | 数据库 ↔ 代码文件同步 |
| `session-validator.js` | 会话验证 | 每次对话校验配置有效性 |
| `task-manager.js` | 任务管理 | 任务 CRUD、状态跟踪 ✨ |

**数据库表结构:**
```sql
agents              -- Agent 配置
agent_configs       -- Agent 详细配置
message_logs        -- 消息日志
tasks              -- 任务信息 ✨
task_assignments    -- 任务分配历史 ✨
task_history        -- 任务变更历史 ✨
```

### 2️⃣ **核心模块 (core/)**

| 文件 | 说明 | 功能 |
|------|------|------|
| `main-controller.js` | 主控制器 | 消息路由、任务分发 |
| `agent-binding.js` | Agent 绑定 | Agent 与数据库绑定 |
| `openclaw-message.js` | 消息处理 | OpenClaw 消息格式处理 |
| `stp-integrator.js` | STP 集成 | 标准任务流程集成 |
| `task-manager.js` | 任务管理 | 任务调度、执行跟踪 |

### 3️⃣ **脚本模块 (scripts/)**

| 文件 | 说明 | 功能 |
|------|------|------|
| `config-cli.js` | 统一 CLI | Agent 和任务管理 ✨ |
| `init-db.js` | 初始化 | 数据库初始化 |
| `sync-config.js` | 同步 | 配置同步 |
| `update-agent.js` | 更新 | Agent 地址更新 |
| `validate-config.js` | 验证 | 配置验证 |

### 4️⃣ **测试模块 (test/)**

| 文件 | 说明 | 功能 |
|------|------|------|
| `task-test.js` | 任务测试 | 任务管理功能测试 ✨ |

## 🚀 快速开始

### 1. 初始化数据库

```bash
npm run db:init
```

### 2. 查看配置状态

```bash
npm run config status
```

### 3. 列出所有 Agent

```bash
npm run config list
```

### 4. 更新 Agent 地址

```bash
npm run config update coder-agent qqbot:c2c:YOUR_ID
```

### 5. 管理任务

```bash
# 列出任务
npm run task:list

# 分配任务
npm run task:assign task-001 coder-agent

# 完成任务
npm run task:complete task-001 coder-agent
```

## 📝 配置管理 CLI 命令

### Agent 管理

| 命令 | 说明 |
|------|------|
| `status` | 显示配置状态 |
| `list` | 列出所有 Agent |
| `update <name> <address>` | 更新 Agent 地址 |
| `backup` | 备份数据库 |
| `restore <path>` | 恢复数据库 |
| `export <path>` | 导出配置 |
| `import <path>` | 导入配置 |
| `cleanup [days]` | 清理过期日志 |
| `summary` | 显示配置摘要 |

### 任务管理

| 命令 | 说明 |
|------|------|
| `task:list` | 列出所有任务 |
| `task:show <id>` | 查看任务详情 |
| `task:assign <id> <agent>` | 分配任务 |
| `task:complete <id> <agent>` | 完成任务 |
| `task:stats` | 显示任务统计 |

## 🔧 环境变量配置

```bash
# 复制示例文件
cp .env.example .env

# 设置自定义数据库路径（可选）
export DB_PATH=/path/to/custom.db

# 或使用
DB_PATH=/path/to/custom.db npm run db:init
```

## 📊 项目统计

- **总文件数**: ~30 个
- **核心模块**: 3 个 (db, core, scripts)
- **数据库表**: 6 张
- **Agent 数量**: 4 个默认
- **支持功能**: Agent 管理、任务管理、配置备份恢复

## 🎯 核心特性

✅ **统一数据库** - Agent 和任务管理一体化  
✅ **自定义路径** - 支持环境变量配置数据库路径  
✅ **任务管理** - 完整的任务创建、分配、跟踪  
✅ **配置管理** - 备份、恢复、导出、导入  
✅ **CLI 工具** - 统一的命令行管理界面  
✅ **自动同步** - 配置自动同步到代码文件  
✅ **会话校验** - 每次对话自动校验配置  
✅ **错误处理** - 完善的错误处理和降级机制  
✅ **测试套件** - 完整的单元测试  
✅ **文档完善** - 详细的使用文档  

## 📞 技术支持

- **文档**: 查看各模块的 README.md
- **测试**: `npm test` 或 `node test/task-test.js`
- **帮助**: `npm run config help`

---

**项目版本**: 1.0.0  
**最后更新**: 2024-03-21  
**维护者**: OpenClaw Team