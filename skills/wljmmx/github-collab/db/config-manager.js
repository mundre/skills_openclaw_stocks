/**
 * Config Manager
 * 统一配置管理工具类 - 支持 Agent 和任务管理
 */

const fs = require('fs');
const path = require('path');
const { initDatabase, DB_PATH } = require('./init');
const { getAllAgents, updateAgentAddress, upsertAgent } = require('./agent-manager');
const { loadFromDatabase, syncToCode } = require('./config-sync');
const { 
  getAllTasks, 
  getTask, 
  createTask, 
  updateTaskStatus,
  getTaskStats 
} = require('./task-manager');

class ConfigManager {
  constructor(dbPath = null) {
    this.dbPath = dbPath || DB_PATH;
    this.configPath = path.join(__dirname, '..', 'agent-addresses.js');
  }

  /**
   * 检查数据库是否存在
   */
  isDatabaseExists() {
    return fs.existsSync(this.dbPath);
  }

  /**
   * 检查配置文件是否存在
   */
  isConfigFileExists() {
    return fs.existsSync(this.configPath);
  }

  /**
   * 获取数据库统计信息（包含 Agent 和任务）
   */
  async getDatabaseStats() {
    try {
      const agents = await getAllAgents();
      const tasks = await getAllTasks();
      const taskStats = await getTaskStats();
      
      return {
        totalAgents: agents.length,
        activeAgents: agents.filter(a => a.is_active === 1).length,
        inactiveAgents: agents.filter(a => a.is_active === 0).length,
        totalTasks: tasks.length,
        taskStats: taskStats,
        databaseExists: this.isDatabaseExists(),
        configFileExists: this.isConfigFileExists(),
        dbPath: this.dbPath
      };
    } catch (error) {
      return {
        error: error.message,
        databaseExists: this.isDatabaseExists(),
        configFileExists: this.isConfigFileExists(),
        dbPath: this.dbPath
      };
    }
  }

  /**
   * 备份数据库
   */
  async backupDatabase(backupPath = null) {
    try {
      if (!this.isDatabaseExists()) {
        throw new Error('数据库文件不存在');
      }

      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const defaultBackupPath = path.join(path.dirname(this.dbPath), `agents-backup-${timestamp}.db`);
      const targetPath = backupPath || defaultBackupPath;

      fs.copyFileSync(this.dbPath, targetPath);
      
      return {
        success: true,
        backupPath: targetPath,
        timestamp: new Date().toISOString(),
        originalPath: this.dbPath
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * 恢复数据库
   */
  async restoreDatabase(backupPath) {
    try {
      if (!fs.existsSync(backupPath)) {
        throw new Error('备份文件不存在');
      }

      fs.copyFileSync(backupPath, this.dbPath);
      
      // 同步配置到代码文件
      await syncToCode();
      
      return {
        success: true,
        restoredFrom: backupPath,
        timestamp: new Date().toISOString(),
        targetPath: this.dbPath
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * 导出配置为 JSON
   */
  async exportConfig(exportPath = null) {
    try {
      const config = await loadFromDatabase();
      const tasks = await getAllTasks();
      
      const exportData = {
        agents: config,
        tasks: tasks,
        exportedAt: new Date().toISOString()
      };
      
      const defaultExportPath = path.join(path.dirname(this.dbPath), `config-export-${new Date().toISOString().replace(/[:.]/g, '-')}.json`);
      const targetPath = exportPath || defaultExportPath;

      fs.writeFileSync(targetPath, JSON.stringify(exportData, null, 2), 'utf8');
      
      return {
        success: true,
        exportPath: targetPath,
        agentCount: Object.keys(config).length,
        taskCount: tasks.length
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * 导入配置从 JSON
   */
  async importConfig(importPath) {
    try {
      if (!fs.existsSync(importPath)) {
        throw new Error('配置文件不存在');
      }

      const data = JSON.parse(fs.readFileSync(importPath, 'utf8'));
      
      // 导入 Agent
      const agentResults = [];
      if (data.agents) {
        for (const [name, agentConfig] of Object.entries(data.agents)) {
          try {
            await upsertAgent({
              name,
              role: agentConfig.role,
              target: agentConfig.target,
              description: agentConfig.description,
              capabilities: agentConfig.capabilities || []
            });
            agentResults.push({ name, success: true });
          } catch (error) {
            agentResults.push({ name, success: false, error: error.message });
          }
        }
      }

      // 导入任务（可选）
      const taskResults = [];
      if (data.tasks) {
        for (const task of data.tasks) {
          try {
            await createTask(task);
            taskResults.push({ task_id: task.task_id, success: true });
          } catch (error) {
            taskResults.push({ task_id: task.task_id, success: false, error: error.message });
          }
        }
      }

      // 同步配置到代码文件
      await syncToCode();
      
      return {
        success: true,
        importedAgents: agentResults.filter(r => r.success).length,
        failedAgents: agentResults.filter(r => !r.success).length,
        importedTasks: taskResults.filter(r => r.success).length,
        failedTasks: taskResults.filter(r => !r.success).length,
        agentResults,
        taskResults
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * 清理过期日志
   */
  async cleanupLogs(daysToKeep = 30) {
    try {
      const db = await initDatabase(this.dbPath);
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - daysToKeep);
      
      return new Promise((resolve, reject) => {
        db.run(
          'DELETE FROM message_logs WHERE created_at < ?',
          [cutoffDate.toISOString()],
          function(err) {
            db.close();
            if (err) {
              reject(err);
              return;
            }
            resolve({
              success: true,
              deletedCount: this.changes
            });
          }
        );
      });
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * 获取配置摘要
   */
  async getSummary() {
    try {
      const stats = await this.getDatabaseStats();
      const agents = await getAllAgents();
      const tasks = await getAllTasks({ status: 'pending' });
      
      const agentSummary = agents.map(agent => ({
        name: agent.name,
        role: agent.role,
        target: agent.target,
        isActive: agent.is_active === 1
      }));
      
      const pendingTasks = tasks.map(task => ({
        task_id: task.task_id,
        title: task.title,
        status: task.status,
        assignee: task.assignee
      }));
      
      return {
        ...stats,
        agents: agentSummary,
        pendingTasks: pendingTasks,
        lastUpdated: new Date().toISOString()
      };
    } catch (error) {
      return {
        error: error.message
      };
    }
  }

  /**
   * 创建任务
   */
  async createTask(taskData) {
    return createTask(taskData);
  }

  /**
   * 获取任务
   */
  async getTask(taskId) {
    return getTask(taskId);
  }

  /**
   * 更新任务状态
   */
  async updateTaskStatus(taskId, status, changedBy = 'system') {
    return updateTaskStatus(taskId, status, changedBy);
  }
}

module.exports = ConfigManager;