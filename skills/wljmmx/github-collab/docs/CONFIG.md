# 配置说明

## 数据库路径配置

支持三种方式配置数据库路径，优先级从高到低：

### 1. 构造函数参数（最高优先级）

```javascript
const TaskManager = require('./core/task-manager');

// 方式 1: 使用 options 对象
const taskManager = new TaskManager({
  dbPath: '/path/to/database.db'
});

// 方式 2: 直接传递路径（向后兼容）
const taskManager2 = new TaskManager('/path/to/database.db');
```

### 2. 环境变量

```bash
# 设置环境变量
export GITHUB_COLLAB_DB_PATH=/path/to/database.db

# 然后在代码中
const taskManager = new TaskManager();
// 自动使用环境变量中的路径
```

### 3. 默认路径（最低优先级）

如果不配置任何选项，默认使用：

```javascript
const taskManager = new TaskManager();
// 使用 ./github-collab.db
```

## Sandbox 部署配置

### Docker 部署

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# 创建数据库目录
RUN mkdir -p /data

# 设置环境变量
ENV GITHUB_COLLAB_DB_PATH=/data/github-collab.db

EXPOSE 3000

CMD ["npm", "start"]
```

### Docker Compose 部署

```yaml
version: '3'

services:
  github-collab:
    build: .
    ports:
      - "3000:3000"
    environment:
      - GITHUB_COLLAB_DB_PATH=/data/github-collab.db
    volumes:
      - ./data:/data
      - ./logs:/app/logs
    restart: unless-stopped
```

### 本地 Sandbox 部署

```bash
# 创建数据目录
mkdir -p /tmp/github-collab-data

# 设置环境变量
export GITHUB_COLLAB_DB_PATH=/tmp/github-collab-data/github-collab.db

# 启动应用
npm start
```

## Agent Binding 配置

```javascript
const AgentBinding = require('./core/agent-binding');

// 方式 1: 传递 TaskManager 实例
const taskManager = new TaskManager({ dbPath: '/path/to/db.db' });
const agentBinding = new AgentBinding({ taskManager });

// 方式 2: 直接传递配置（自动创建 TaskManager）
const agentBinding2 = new AgentBinding({
  dbPath: '/path/to/db.db'
});
```

## Main Controller 配置

```javascript
const MainController = require('./core/main-controller');

const controller = new MainController({
  maxParallelAgents: 5,
  dbPath: '/path/to/github-collab.db',
  // 其他配置...
});
```

## 完整示例

```javascript
const MainController = require('./core/main-controller');

// 配置
const config = {
  maxParallelAgents: 3,
  agentTypes: ['dev', 'test', 'review'],
  dbPath: process.env.GITHUB_COLLAB_DB_PATH || './github-collab.db',
  autoRecovery: true,
  priorityThreshold: 5
};

// 创建控制器
const controller = new MainController(config);

// 启动
controller.start();
```

## 环境变量列表

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `GITHUB_COLLAB_DB_PATH` | 数据库文件路径 | `./github-collab.db` |
| `GITHUB_COLLAB_LOG_LEVEL` | 日志级别 | `info` |
| `GITHUB_COLLAB_MAX_AGENTS` | 最大 Agent 数量 | `3` |

## 注意事项

1. **数据库文件权限**: 确保数据库文件所在目录有读写权限
2. **并发访问**: SQLite 支持并发读取，但写入需要锁机制
3. **备份建议**: 定期备份数据库文件
4. **生产环境**: 建议使用持久化存储挂载数据库文件

## 故障排查

### 数据库文件无法写入

```bash
# 检查文件权限
ls -la /path/to/database.db

# 修改权限
chmod 666 /path/to/database.db
```

### 数据库文件损坏

```bash
# 检查数据库完整性
sqlite3 /path/to/database.db "PRAGMA integrity_check;"

# 备份并重建
cp /path/to/database.db /path/to/database.db.backup
rm /path/to/database.db
```

### 路径不存在

```bash
# 创建目录
mkdir -p /path/to

# 设置环境变量
export GITHUB_COLLAB_DB_PATH=/path/to/github-collab.db
```