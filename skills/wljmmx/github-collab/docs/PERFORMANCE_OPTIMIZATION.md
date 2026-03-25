# 性能优化指南

## 一、数据库优化

### 1. 索引优化
```javascript
// 为常用查询字段添加索引
this.db.exec(`
  CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks(project_id);
  CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
  CREATE INDEX IF NOT EXISTS idx_tasks_assigned_agent ON tasks(assigned_agent);
  CREATE INDEX IF NOT EXISTS idx_agents_current_task ON agents(current_task_id);
  CREATE INDEX IF NOT EXISTS idx_agent_queue_agent_name ON agent_task_queue(agent_name);
  CREATE INDEX IF NOT EXISTS idx_agent_queue_status ON agent_task_queue(status);
`);
```

### 2. 连接池优化
- 使用 better-sqlite3 的同步 API（已实现）
- 避免频繁创建数据库连接
- 使用事务批量操作

### 3. 查询优化
```javascript
// 优化：使用事务批量插入
async createTasksBatch(tasks) {
  const insert = this.db.prepare(`
    INSERT INTO tasks (project_id, name, description, status, priority)
    VALUES (?, ?, ?, ?, ?)
  `);
  
  const transaction = this.db.transaction((tasks) => {
    for (const task of tasks) {
      insert.run(task.projectId, task.name, task.description, task.status, task.priority);
    }
  });
  
  transaction(tasks);
}
```

## 二、缓存优化

### 1. 任务缓存
```javascript
// 添加 LRU 缓存
const NodeCache = require('node-cache');
const taskCache = new NodeCache({ stdTTL: 300 }); // 5 分钟过期

async getTask(taskId) {
  const cached = taskCache.get(taskId);
  if (cached) return cached;
  
  const task = await this.fetchTaskFromDB(taskId);
  taskCache.set(taskId, task);
  return task;
}
```

### 2. Agent 状态缓存
```javascript
const agentCache = new NodeCache({ stdTTL: 60 }); // 1 分钟过期

async getAgentStatus(agentName) {
  const cached = agentCache.get(agentName);
  if (cached) return cached;
  
  const status = await this.fetchAgentStatusFromDB(agentName);
  agentCache.set(agentName, status);
  return status;
}
```

## 三、异步优化

### 1. 并行处理
```javascript
// 优化：并行处理多个任务
async processTasksParallel(taskIds) {
  const promises = taskIds.map(taskId => this.processTask(taskId));
  return await Promise.all(promises);
}

// 限制并发数
async processTasksWithLimit(taskIds, limit = 5) {
  const results = [];
  for (let i = 0; i < taskIds.length; i += limit) {
    const chunk = taskIds.slice(i, i + limit);
    const chunkResults = await Promise.all(chunk.map(taskId => this.processTask(taskId)));
    results.push(...chunkResults);
  }
  return results;
}
```

### 2. 事件驱动
```javascript
// 使用事件驱动减少轮询
const EventEmitter = require('events');
class TaskManager extends EventEmitter {
  // 任务状态变更时触发事件
  updateTaskStatus(taskId, newStatus) {
    this.emit('taskStatusChanged', { taskId, newStatus });
    // ... 更新逻辑
  }
}
```

## 四、代码优化

### 1. 减少重复计算
```javascript
// 优化：缓存计算结果
const memoize = require('memoizee');

const getProjectStats = memoize((projectId) => {
  // 复杂计算逻辑
  return calculateStats(projectId);
}, {
  maxAge: 60000, // 1 分钟
  promise: true
});
```

### 2. 使用更高效的数据结构
```javascript
// 优化：使用 Map 替代对象查找
const taskMap = new Map();

// 快速查找
const task = taskMap.get(taskId);

// 批量操作
taskMap.forEach((task, id) => {
  // 处理任务
});
```

### 3. 避免阻塞操作
```javascript
// 优化：将同步操作改为异步
const fs = require('fs').promises;

async readConfig() {
  const data = await fs.readFile('config.json', 'utf-8');
  return JSON.parse(data);
}
```

## 五、监控与日志

### 1. 性能监控
```javascript
// 添加性能监控
const perf_hooks = require('perf_hooks');

async performTask(taskId) {
  const start = perf_hooks.performance.now();
  
  try {
    await processTask(taskId);
    
    const duration = perf_hooks.performance.now() - start;
    console.log(`Task ${taskId} completed in ${duration.toFixed(2)}ms`);
    
    if (duration > 1000) {
      console.warn(`Slow task detected: ${taskId} (${duration.toFixed(2)}ms)`);
    }
  } catch (error) {
    const duration = perf_hooks.performance.now() - start;
    console.error(`Task ${taskId} failed after ${duration.toFixed(2)}ms:`, error);
    throw error;
  }
}
```

### 2. 日志优化
```javascript
// 使用结构化日志
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});
```

## 六、依赖优化

### 1. 按需加载
```javascript
// 优化：延迟加载重型模块
let heavyModule;
function getHeavyModule() {
  if (!heavyModule) {
    heavyModule = require('heavy-module');
  }
  return heavyModule;
}
```

### 2. 使用轻量级替代
```javascript
// 优化：使用更轻量的库
// 替代：lodash -> lodash-es
// 替代：moment -> dayjs
```

## 七、测试优化

### 1. 并行测试
```json
{
  "scripts": {
    "test": "jest --maxWorkers=4",
    "test:parallel": "jest --parallel"
  }
}
```

### 2. 测试缓存
```json
{
  "jest": {
    "cache": true,
    "cacheDirectory": ".jest_cache"
  }
}
```

## 八、CI/CD 优化

### 1. 缓存依赖
```yaml
- name: Install dependencies
  run: npm ci
  env:
    NPM_CONFIG_CACHE: ${{ runner.tool_cache }}/npm
```

### 2. 并行工作流
```yaml
jobs:
  test:
    strategy:
      matrix:
        node-version: [18, 20, 22]
        os: [ubuntu-latest, windows-latest]
```

## 九、配置优化

### 1. 环境变量
```javascript
// 优化：使用环境变量配置
const config = {
  dbPath: process.env.DB_PATH || './github-collab.db',
  cacheTTL: parseInt(process.env.CACHE_TTL) || 300,
  maxWorkers: parseInt(process.env.MAX_WORKERS) || 4
};
```

### 2. 配置热重载
```javascript
// 监听配置文件变化
const chokidar = require('chokidar');

const watcher = chokidar.watch('config.json');
watcher.on('change', () => {
  // 重新加载配置
  require.cache[require.resolve('./config')].exports = require('./config');
});
```

## 十、最佳实践

### 1. 代码审查
- 所有 PR 必须通过 CI 检查
- 性能回归测试
- 代码复杂度检查

### 2. 性能基准
- 建立性能基准测试
- 定期运行基准测试
- 监控性能指标

### 3. 文档维护
- 更新性能优化文档
- 记录优化前后对比
- 分享优化经验

## 实施计划

### 第一阶段：数据库优化（1 天）
- [x] 添加索引
- [x] 优化查询
- [x] 添加事务

### 第二阶段：缓存优化（1 天）
- [ ] 添加 LRU 缓存
- [ ] 实现缓存失效策略
- [ ] 添加缓存监控

### 第三阶段：异步优化（1 天）
- [ ] 并行处理
- [ ] 事件驱动
- [ ] 减少阻塞

### 第四阶段：监控与日志（1 天）
- [ ] 性能监控
- [ ] 结构化日志
- [ ] 告警系统

### 第五阶段：CI/CD 优化（1 天）
- [ ] 并行工作流
- [ ] 缓存优化
- [ ] 测试优化

## 预期效果

- 查询速度提升 50%
- 内存使用降低 30%
- 构建时间减少 40%
- 测试时间减少 60%