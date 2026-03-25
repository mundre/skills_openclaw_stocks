# GitHub 协作 Skill 数据整理

## 📊 技能概述

**技能名称**: GitHub Collaboration Skill  
**版本**: 1.0.0  
**类型**: 多 Agent 协作开发  
**核心功能**: 需求分析、任务拆分、Agent 分配、进度跟踪

---

## 🎯 技能核心能力

### 1. 多 Agent 协作系统

| Agent | 职责 | 任务队列 | 状态跟踪 |
|-------|------|---------|---------|
| **Main Agent** | 需求接收、GitHub 项目创建、任务分配 | 项目管理 | 项目状态 |
| **Dev Agent** | 代码开发任务执行 | 开发任务 | 代码提交 |
| **Test Agent** | 测试验证任务执行 | 测试任务 | 测试报告 |
| **Worker Agent** | 通用任务执行 | 通用任务 | 执行状态 |

### 2. GitHub 集成能力

- ✅ 自动创建 GitHub 仓库（使用 `gh` 工具）
- ✅ 关联 GitHub 项目与本地任务
- ✅ 项目进度同步
- ✅ 任务与 Issue 映射

### 3. 任务管理系统

**数据库表结构:**
```sql
projects          -- 项目信息
tasks            -- 任务记录
agents           -- Agent 注册信息
agent_task_queue -- Agent 任务队列
task_logs        -- 任务活动日志
task_assignments -- 任务分配历史
task_history     -- 任务变更历史
```

### 4. 进度报告功能

- ✅ Markdown 格式报告生成
- ✅ 实时进度统计
- ✅ Agent 状态监控
- ✅ 任务完成度跟踪

---

## 📁 技能相关文件

### 核心文件

| 文件 | 路径 | 说明 |
|------|------|------|
| SKILL.md | `/SKILL.md` | 技能说明文档 |
| README.md | `/README.md` | 项目主文档 |
| index.js | `/index.js` | 入口文件 |
| config.js | `/config.js` | 配置文件 |

### 数据库模块

| 文件 | 路径 | 说明 |
|------|------|------|
| init.js | `/db/init.js` | 数据库初始化 |
| agent-manager.js | `/db/agent-manager.js` | Agent 管理 |
| task-manager.js | `/db/task-manager.js` | 任务管理 |
| config-manager.js | `/db/config-manager.js` | 配置管理 |

### 核心模块

| 文件 | 路径 | 说明 |
|------|------|------|
| main-controller.js | `/core/main-controller.js` | 主控制器 |
| stp-integrator.js | `/core/stp-integrator.js` | STP 集成器 |
| task-manager.js | `/core/task-manager.js` | 任务管理器 |
| agent-binding.js | `/core/agent-binding.js` | Agent 绑定 |

### 脚本工具

| 文件 | 路径 | 说明 |
|------|------|------|
| config-cli.js | `/scripts/config-cli.js` | 统一配置管理 CLI |
| init-db.js | `/scripts/init-db.js` | 数据库初始化脚本 |
| project-manager.js | `/scripts/project-manager.js` | 项目管理器 |
| scheduler.js | `/scripts/scheduler.js` | 调度器 |

---

## 🔧 技能配置

### 环境变量

```bash
# 数据库路径（可选）
DB_PATH=/path/to/custom.db

# QQ 通知（可选）
QQ_TOKEN=your_qq_token
```

### 技能配置

```javascript
const skill = require('github-collab-skill');

// 配置 QQ 通知
skill.configure({
    qqToken: process.env.QQ_TOKEN
});
```

---

## 🚀 技能使用流程

### 1. 初始化

```bash
# 初始化数据库
npm run db:init

# 验证配置
npm run db:validate
```

### 2. 创建项目

```javascript
const skill = require('github-collab-skill');

// 创建项目（自动使用 gh 工具创建 GitHub 仓库）
const project = await skill.createProject(
    '开发一个 Todo 应用，支持增删改查功能',
    'Todo App',
    null // 不提供 URL，系统自动创建
);

console.log(`项目已创建：${project.projectName}`);
console.log(`GitHub URL: ${project.githubUrl}`);
console.log(`任务数：${project.taskCount}`);
```

### 3. 获取项目报告

```javascript
const report = await skill.getProjectReport(projectId);
console.log(report);
```

### 4. 列出所有项目

```javascript
const projects = await skill.listProjects();
console.log(`共有 ${projects.length} 个项目`);
```

---

## 📊 数据流架构

```
用户输入需求
    ↓
Main Agent (需求分析)
    ↓
使用 gh 工具创建 GitHub 仓库
    ↓
STP Integrator (任务拆分)
    ↓
Task Manager (创建任务记录)
    ↓
分配任务给 Agent (添加到 Agent 任务队列)
    ↓
Dev Agent / Test Agent (从自己的队列获取任务并执行)
    ↓
Task Manager (更新任务状态)
    ↓
生成进度报告
```

---

## 📝 技能命令速查

### 数据库管理

| 命令 | 说明 |
|------|------|
| `npm run db:init` | 初始化数据库 |
| `npm run db:list` | 列出 Agent |
| `npm run db:sync` | 同步配置 |
| `npm run db:validate` | 验证配置 |

### 配置管理

| 命令 | 说明 |
|------|------|
| `npm run config status` | 显示配置状态 |
| `npm run config list` | 列出所有 Agent |
| `npm run config update <name> <address>` | 更新 Agent 地址 |
| `npm run config backup` | 备份数据库 |
| `npm run config restore <path>` | 恢复数据库 |
| `npm run config export <path>` | 导出配置 |
| `npm run config import <path>` | 导入配置 |
| `npm run config cleanup [days]` | 清理过期日志 |
| `npm run config summary` | 显示配置摘要 |

### 任务管理

| 命令 | 说明 |
|------|------|
| `npm run task:list` | 列出所有任务 |
| `npm run task:show <id>` | 查看任务详情 |
| `npm run task:assign <id> <agent>` | 分配任务 |
| `npm run task:complete <id> <agent>` | 完成任务 |
| `npm run task:stats` | 显示任务统计 |

---

## 📈 技能统计

| 指标 | 数值 |
|------|------|
| **核心文件数** | 30+ |
| **数据库表数** | 6 张 |
| **Agent 数量** | 4 个默认 |
| **支持功能** | 需求分析、任务拆分、Agent 分配、进度跟踪 |
| **GitHub 集成** | ✅ 支持 |
| **任务队列** | ✅ 独立队列 |
| **进度报告** | ✅ Markdown 格式 |

---

## 🎯 技能特性总结

✅ **多 Agent 协作** - Main/Dev/Test/Worker Agent 分工协作  
✅ **GitHub 集成** - 自动创建仓库、关联项目  
✅ **任务管理** - 完整的任务创建、分配、跟踪  
✅ **独立队列** - 每个 Agent 有独立任务队列  
✅ **进度报告** - Markdown 格式实时报告  
✅ **配置管理** - 备份、恢复、导出、导入  
✅ **CLI 工具** - 统一的命令行管理界面  
✅ **自动同步** - 配置自动同步到代码文件  
✅ **会话校验** - 每次对话自动校验配置  
✅ **错误处理** - 完善的错误处理和降级机制  

---

## 📞 技术支持

- **文档**: `/SKILL.md`, `/README.md`
- **测试**: `npm test`
- **帮助**: `npm run config help`

---

**生成时间**: 2024-03-21  
**版本**: 1.0.0  
**维护者**: OpenClaw Team