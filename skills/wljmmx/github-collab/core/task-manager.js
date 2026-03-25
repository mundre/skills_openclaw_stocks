/**
 * GitHub Collaboration Task Manager
 * 基于 SQLite 的多 Agent 任务分配系统
 * 
 * 功能增强：
 * 1. 每个 Agent 有独立任务列表
 * 2. 支持任务分配记录
 * 3. 支持项目 - 任务关联
 */

const Database = require('better-sqlite3');
const path = require('path');

class TaskManager {
  constructor(options = {}) {
    // 支持自定义数据库路径
    const dbPath = options.dbPath || process.env.GITHUB_COLLAB_DB_PATH || './github-collab.db';
    this.dbPath = dbPath;
    this.db = new Database(dbPath);
    this.initDatabase();
  }

  /**
   * 初始化数据库表结构
   */
  initDatabase() {
    // 项目表
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        github_url TEXT UNIQUE NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'active',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);

    // 任务表
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'pending',
        assigned_agent TEXT,
        priority INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        completed_at DATETIME,
        result TEXT,
        error TEXT,
        metadata TEXT,
        FOREIGN KEY (project_id) REFERENCES projects(id)
      )
    `);

    // Agent 表
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS agents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        type TEXT NOT NULL,
        status TEXT DEFAULT 'idle',
        current_task_id INTEGER,
        last_heartbeat DATETIME DEFAULT CURRENT_TIMESTAMP,
        capabilities TEXT,
        FOREIGN KEY (current_task_id) REFERENCES tasks(id)
      )
    `);

    // Agent 任务列表表（每个 Agent 自己的任务队列）
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS agent_task_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_name TEXT NOT NULL,
        task_id INTEGER NOT NULL,
        status TEXT DEFAULT 'queued',
        assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        started_at DATETIME,
        completed_at DATETIME,
        result TEXT,
        FOREIGN KEY (agent_name) REFERENCES agents(name),
        FOREIGN KEY (task_id) REFERENCES tasks(id)
      )
    `);

    // 任务日志表
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS task_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        agent_name TEXT NOT NULL,
        action TEXT NOT NULL,
        message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (task_id) REFERENCES tasks(id)
      )
    `);

    // 创建索引
    this.db.exec(`
      CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks(project_id);
      CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
      CREATE INDEX IF NOT EXISTS idx_tasks_assigned_agent ON tasks(assigned_agent);
      CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
      CREATE INDEX IF NOT EXISTS idx_agent_task_queue_agent ON agent_task_queue(agent_name);
      CREATE INDEX IF NOT EXISTS idx_agent_task_queue_task ON agent_task_queue(task_id);
    `);
  }

  /**
   * 创建项目
   */
  createProject(project) {
    const { name, github_url, description = '' } = project;
    
    const stmt = this.db.prepare(`
      INSERT INTO projects (name, github_url, description)
      VALUES (?, ?, ?)
    `);

    const result = stmt.run(name, github_url, description);
    return { id: result.lastInsertRowid, ...project };
  }

  /**
   * 创建任务（关联项目）
   */
  createTask(task) {
    const { project_id, name, description, priority = 0, metadata = {} } = task;
    
    const stmt = this.db.prepare(`
      INSERT INTO tasks (project_id, name, description, priority, metadata)
      VALUES (?, ?, ?, ?, ?)
    `);

    const result = stmt.run(project_id, name, description, priority, JSON.stringify(metadata));
    
    this.logTaskActivity(result.lastInsertRowid, 'system', 'created', `Task created: ${name}`);
    
    return {
      id: result.lastInsertRowid,
      project_id,
      name,
      description,
      status: 'pending',
      priority
    };
  }

  /**
   * 批量创建任务
   */
  createTasks(projectId, tasks) {
    const created = [];
    for (const task of tasks) {
      const createdTask = this.createTask({ ...task, project_id: projectId });
      created.push(createdTask);
    }
    return created;
  }

  /**
   * 分配任务给 Agent（添加到 Agent 任务队列）
   */
  assignTaskToAgent(taskId, agentName) {
    // 更新任务状态和分配记录
    const updateStmt = this.db.prepare(`
      UPDATE tasks
      SET status = 'assigned',
          assigned_agent = ?,
          updated_at = CURRENT_TIMESTAMP
      WHERE id = ?
    `);
    
    updateStmt.run(agentName, taskId);
    
    // 添加到 Agent 任务队列
    const queueStmt = this.db.prepare(`
      INSERT INTO agent_task_queue (agent_name, task_id, status)
      VALUES (?, ?, 'queued')
    `);
    
    queueStmt.run(agentName, taskId);
    
    // 更新 Agent 状态
    this.updateAgentStatus(agentName, 'busy');
    
    this.logTaskActivity(taskId, agentName, 'assigned', `Task assigned to agent: ${agentName}`);
    
    return { taskId, agentName, status: 'assigned' };
  }

  /**
   * Agent 从自己的队列获取下一个任务
   */
  getAgentNextTask(agentName) {
    // 从 Agent 任务队列中获取下一个待处理任务
    const queueTask = this.db.prepare(`
      SELECT aq.*, t.* 
      FROM agent_task_queue aq
      JOIN tasks t ON aq.task_id = t.id
      WHERE aq.agent_name = ? 
        AND aq.status = 'queued'
      ORDER BY aq.assigned_at ASC
      LIMIT 1
    `).get(agentName);

    if (!queueTask) {
      return null;
    }

    // 更新队列状态为进行中
    this.db.prepare(`
      UPDATE agent_task_queue
      SET status = 'in_progress',
          started_at = CURRENT_TIMESTAMP
      WHERE id = ?
    `).run(queueTask.id);

    // 更新任务状态
    this.db.prepare(`
      UPDATE tasks
      SET status = 'in_progress',
          updated_at = CURRENT_TIMESTAMP
      WHERE id = ?
    `).run(queueTask.id);

    // 更新 Agent 当前任务
    this.updateAgentStatus(agentName, 'busy', queueTask.id);
    
    this.logTaskActivity(queueTask.id, agentName, 'started', `Agent started task`);

    return queueTask;
  }

  /**
   * Agent 完成任务
   */
  completeAgentTask(agentName, taskId, result = null, error = null) {
    // 更新任务状态
    this.db.prepare(`
      UPDATE tasks
      SET status = ?,
          result = ?,
          error = ?,
          completed_at = CURRENT_TIMESTAMP,
          updated_at = CURRENT_TIMESTAMP
      WHERE id = ?
    `).run(error ? 'failed' : 'completed', result, error, taskId);

    // 更新 Agent 任务队列状态
    this.db.prepare(`
      UPDATE agent_task_queue
      SET status = ?,
          result = ?,
          completed_at = CURRENT_TIMESTAMP
      WHERE task_id = ? AND agent_name = ?
    `).run(error ? 'failed' : 'completed', result, taskId, agentName);

    // 更新 Agent 状态为空闲
    this.updateAgentStatus(agentName, 'idle', null);
    
    this.logTaskActivity(taskId, agentName, 'completed', `Task completed by agent`);
    
    return { taskId, agentName, status: error ? 'failed' : 'completed' };
  }

  /**
   * 获取项目的任务列表
   */
  getProjectTasks(projectId) {
    return this.db.prepare(`
      SELECT t.*, a.name as agent_name, a.status as agent_status
      FROM tasks t
      LEFT JOIN agents a ON t.assigned_agent = a.name
      WHERE t.project_id = ?
      ORDER BY t.priority DESC, t.created_at ASC
    `).all(projectId);
  }

  /**
   * 获取 Agent 的任务队列
   */
  getAgentTaskQueue(agentName) {
    return this.db.prepare(`
      SELECT aq.*, t.name as task_name, t.description as task_description, t.status as task_status
      FROM agent_task_queue aq
      JOIN tasks t ON aq.task_id = t.id
      WHERE aq.agent_name = ?
      ORDER BY aq.assigned_at ASC
    `).all(agentName);
  }

  /**
   * 获取所有项目
   */
  getAllProjects() {
    return this.db.prepare('SELECT * FROM projects ORDER BY created_at DESC').all();
  }

  /**
   * 获取项目详情（包含任务）
   */
  getProjectWithTasks(projectId) {
    const project = this.db.prepare('SELECT * FROM projects WHERE id = ?').get(projectId);
    const tasks = this.getProjectTasks(projectId);
    return { ...project, tasks };
  }

  /**
   * 更新 Agent 状态
   */
  updateAgentStatus(agentName, status, taskId = null) {
    const existingAgent = this.db.prepare('SELECT * FROM agents WHERE name = ?').get(agentName);
    
    if (!existingAgent) {
      // 自动创建 Agent 记录
      const type = agentName.includes('dev') ? 'developer' : 
                   agentName.includes('test') ? 'tester' : 'general';
      this.db.prepare('INSERT INTO agents (name, type, status) VALUES (?, ?, ?)').run(agentName, type, status);
    } else {
      this.db.prepare(`
        UPDATE agents
        SET status = ?,
            current_task_id = ?,
            last_heartbeat = CURRENT_TIMESTAMP
        WHERE name = ?
      `).run(status, taskId, agentName);
    }
  }

  /**
   * 记录任务活动日志
   */
  logTaskActivity(taskId, agentName, action, message = null) {
    this.db.prepare(`
      INSERT INTO task_logs (task_id, agent_name, action, message)
      VALUES (?, ?, ?, ?)
    `).run(taskId, agentName, action, message);
  }

  /**
   * 获取任务日志
   */
  getTaskLogs(taskId) {
    return this.db.prepare(`
      SELECT * FROM task_logs
      WHERE task_id = ?
      ORDER BY timestamp DESC
    `).all(taskId);
  }

  /**
   * 获取所有活跃 Agent
   */
  getActiveAgents() {
    return this.db.prepare(`
      SELECT a.*, t.name as task_name, t.status as task_status
      FROM agents a
      LEFT JOIN tasks t ON a.current_task_id = t.id
      WHERE a.status != 'offline'
      ORDER BY a.last_heartbeat DESC
    `).all();
  }

  /**
   * 获取项目统计信息
   */
  getProjectStats(projectId) {
    const tasks = this.getProjectTasks(projectId);
    const stats = {
      total: tasks.length,
      pending: tasks.filter(t => t.status === 'pending').length,
      assigned: tasks.filter(t => t.status === 'assigned').length,
      in_progress: tasks.filter(t => t.status === 'in_progress').length,
      completed: tasks.filter(t => t.status === 'completed').length,
      failed: tasks.filter(t => t.status === 'failed').length
    };
    return stats;
  }

  /**
   * 生成进度报告（Markdown 格式）
   */
  generateProgressReport(projectId = null) {
    const project = projectId ? this.getProjectWithTasks(projectId) : null;
    const tasks = projectId ? this.getProjectTasks(projectId) : this.db.prepare('SELECT * FROM tasks ORDER BY created_at DESC').all();
    const now = new Date().toLocaleString('zh-CN');
    
    let report = `# 项目进度报告\n\n`;
    report += `生成时间：${now}\n\n`;
    
    if (project) {
      report += `## 项目信息\n\n`;
      report += `- **项目名称**: ${project.name}\n`;
      report += `- **GitHub URL**: ${project.github_url}\n`;
      report += `- **描述**: ${project.description || '无'}\n\n`;
    }
    
    report += `## 总体统计\n\n`;
    
    const stats = {
      total: tasks.length,
      pending: tasks.filter(t => t.status === 'pending').length,
      assigned: tasks.filter(t => t.status === 'assigned').length,
      in_progress: tasks.filter(t => t.status === 'in_progress').length,
      completed: tasks.filter(t => t.status === 'completed').length,
      failed: tasks.filter(t => t.status === 'failed').length
    };
    
    report += `- 总任务数：${stats.total}\n`;
    report += `- 待处理：${stats.pending}\n`;
    report += `- 已分配：${stats.assigned}\n`;
    report += `- 进行中：${stats.in_progress}\n`;
    report += `- 已完成：${stats.completed}\n`;
    report += `- 失败：${stats.failed}\n\n`;
    
    if (stats.total > 0) {
      const progress = Math.round((stats.completed / stats.total) * 100);
      report += `**完成度：${progress}%**\n\n`;
    }
    
    report += `## 任务列表\n\n`;
    report += `| ID | 任务名称 | 状态 | 分配 Agent | 优先级 |\n`;
    report += `|----|---------|------|-----------|--------|\n`;
    
    tasks.forEach(task => {
      const statusMap = {
        pending: '待处理',
        assigned: '已分配',
        in_progress: '进行中',
        completed: '已完成',
        failed: '失败'
      };
      report += `| ${task.id} | ${task.name} | ${statusMap[task.status] || task.status} | ${task.assigned_agent || '-'} | ${task.priority} |\n`;
    });
    
    report += `\n## Agent 任务队列\n\n`;
    
    const agents = this.getActiveAgents();
    agents.forEach(agent => {
      const queue = this.getAgentTaskQueue(agent.name);
      report += `### ${agent.name}\n\n`;
      report += `- 状态：${agent.status}\n`;
      report += `- 当前任务：${agent.task_name || '无'}\n`;
      report += `- 任务队列：${queue.length} 个任务\n\n`;
      
      if (queue.length > 0) {
        report += `| 任务 ID | 任务名称 | 状态 |\n`;
        report += `|--------|---------|------|\n`;
        queue.forEach(item => {
          report += `| ${item.task_id} | ${item.task_name} | ${item.status} |\n`;
        });
        report += `\n`;
      }
    });
    
    return report;
  }

  /**
   * 关闭数据库连接
   */
  close() {
    this.db.close();
  }
}

module.exports = TaskManager;