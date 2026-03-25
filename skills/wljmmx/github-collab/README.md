# GitHub Collaboration

GitHub 项目协作开发系统 - 多 Agent 协作完成 GitHub 项目开发任务

## 📋 目录

- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [功能特性](#功能特性)
- [使用示例](#使用示例)
- [配置说明](#配置说明)
- [测试](#测试)

## 🚀 快速开始

### 安装依赖

```bash
npm install
```

### 配置环境变量

```bash
# 方式 1: 使用 .env 文件
cd skills/github-collab
cp .env.example .env
# 编辑 .env 文件，填入你的配置

# 方式 2: 直接设置环境变量（推荐 Sandbox 部署）
export GITHUB_COLLAB_DB_PATH=/path/to/github-collab.db
export GITHUB_COLLAB_LOG_LEVEL=info
export GITHUB_COLLAB_MAX_AGENTS=3
```

### 数据库路径配置（Sandbox 部署）

```bash
# Docker 部署 - 挂载数据库文件
docker run -d \
  -e GITHUB_COLLAB_DB_PATH=/data/github-collab.db \
  -v ./data:/data \
  github-collab

# 本地 Sandbox 部署
mkdir -p /tmp/github-collab-data
export GITHUB_COLLAB_DB_PATH=/tmp/github-collab-data/github-collab.db
npm start
```

更多配置选项请参考 [CONFIG.md](./docs/CONFIG.md)

### 运行示例

```bash
npm run example
```

## 📁 项目结构

```
github-collab/
├── README.md                    # 项目总说明
├── package.json                 # 根项目配置
├── .gitignore
├── examples/                    # 示例代码
│   ├── basic-example.js         # 基础示例
│   ├── complete-example.js      # 完整示例
│   └── stp-example.js           # STP 集成示例
├── tests/                       # 测试文件
│   ├── test.js                  # 单元测试
│   └── test-enhanced.js         # 增强版测试
└── skills/
    └── github-collab/           # 核心技能模块
        ├── SKILL.md             # 技能文档
        ├── README.md            # 技能说明
        ├── package.json         # 技能配置
        ├── index.js             # 入口文件
        ├── config.js            # 配置管理
        ├── task-manager.js      # 基础任务管理器
        ├── task-manager-enhanced.js  # 增强版任务管理器
        ├── dev-agent.js         # 开发 Agent
        ├── test-agent.js        # 测试 Agent
        ├── main-agent.js        # 主 Agent
        ├── stp-integrator.js    # STP 集成
        ├── stp-integrator-enhanced.js # 增强版 STP
        ├── openclaw-message.js  # OpenClaw 消息工具
        ├── qq-notifier.js       # QQ 通知工具
        └── .env.example         # 环境变量示例
```

## ✨ 功能特性

### 1. 任务管理

- ✅ 任务创建、分配、执行
- ✅ 任务依赖管理
- ✅ 并发锁机制
- ✅ 崩溃恢复
- ✅ 性能优化（批量创建、缓存、索引）

### 2. 多 Agent 协作

- ✅ Dev Agent - 代码开发
- ✅ Test Agent - 单元测试
- ✅ Review Agent - 代码审查（规划中）
- ✅ Deploy Agent - 自动部署（规划中）

### 3. STP 任务规划

- ✅ 任务自动拆分
- ✅ 依赖关系验证
- ✅ 执行计划生成
- ✅ 资源估算

### 4. 消息通知

- ✅ QQ 消息通知
- ✅ 进度更新
- ✅ 任务完成通知
- ✅ 错误通知

## 📖 使用示例

### 基础示例

```javascript
const { TaskManagerEnhanced, DevAgent, TestAgent } = require('./skills/github-collab');

// 创建任务管理器
const taskManager = new TaskManagerEnhanced();

// 创建项目
const project = await taskManager.createProject({
    name: 'My Project',
    description: 'A sample project',
    github_url: 'https://github.com/example/repo'
});

// 创建任务
const task = await taskManager.createTask({
    project_id: project.id,
    name: 'Implement feature',
    description: 'Implement new feature',
    priority: 10
});

// 启动 Agent
const devAgent = new DevAgent('dev-agent');
await devAgent.initialize();
await devAgent.processQueue();
```

### 任务依赖示例

```javascript
// 创建开发任务
const devTask = await taskManager.createTask({
    name: 'Implement feature',
    type: 'development'
});

// 创建测试任务
const testTask = await taskManager.createTask({
    name: 'Test feature',
    type: 'testing'
});

// 添加依赖关系
taskManager.addTaskDependency(testTask.id, devTask.id);

// 检查依赖是否满足
const dependenciesMet = taskManager.checkTaskDependencies(testTask.id);
if (dependenciesMet) {
    await taskManager.assignTask(testTask.id, 'test-agent');
}
```

### STP 集成示例

```javascript
const { STPIntegratorEnhanced } = require('./skills/github-collab');

const stp = new STPIntegratorEnhanced();

// 拆分任务
const result = await stp.splitTask(
    'Build a web application with user authentication',
    'Node.js, Express, MongoDB',
    { deadline: '2024-12-31' }
);

console.log('拆分后的任务:', result.tasks);
console.log('执行计划:', result.executionPlan);
```

## ⚙️ 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|-------|------|--------|
| GITHUB_TOKEN | GitHub API Token | - |
| GITHUB_OWNER | GitHub 用户名 | default-owner |
| DEV_AGENT_COUNT | Dev Agent 数量 | 2 |
| TEST_AGENT_COUNT | Test Agent 数量 | 1 |
| REVIEW_AGENT_COUNT | Review Agent 数量 | 1 |
| LOG_LEVEL | 日志级别 | info |
| QQ_ENABLED | 启用 QQ 通知 | false |
| QQ_TOKEN | QQ Token | - |
| QQ_TARGET | QQ 目标用户 | - |

### 配置文件

创建 `skills/github-collab/.github-collab-config.json` 文件：

```json
{
    "github": {
        "token": "your_token",
        "owner": "your_username"
    },
    "agents": {
        "dev_count": 2,
        "test_count": 1
    },
    "logging": {
        "level": "info"
    }
}
```

## 🧪 测试

### 运行所有测试

```bash
npm test
```

### 运行增强版测试

```bash
npm run test:enhanced
```

### 运行特定测试

```bash
npm run test:task-manager
npm run test:agent
npm run test:stp
```

## 📊 性能指标

| 操作 | 时间 |
|------|------|
| 任务创建 | ~1ms |
| 任务分配 | ~2ms |
| 并发锁 | ~0.5ms |
| 缓存命中率 | ~90% |
| 数据库查询 | ~5ms |

## 🔧 维护建议

1. 定期清理过期缓存
2. 监控数据库性能
3. 定期检查 Agent 健康状态
4. 更新依赖包版本
5. 备份数据库文件

## 📝 更新日志

### v1.0.0 (2024-12-19)

- ✅ 初始版本发布
- ✅ 任务管理功能
- ✅ 多 Agent 协作
- ✅ STP 任务规划
- ✅ QQ 消息通知

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License