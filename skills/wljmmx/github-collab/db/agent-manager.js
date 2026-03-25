/**
 * Agent Manager
 * Agent 数据库操作模块
 */

const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const DB_PATH = path.join(__dirname, 'agents.db');

/**
 * 获取数据库连接
 */
function getDb() {
  return new sqlite3.Database(DB_PATH);
}

/**
 * 获取所有 Agent
 */
function getAllAgents() {
  return new Promise((resolve, reject) => {
    const db = getDb();
    
    db.all('SELECT * FROM agents WHERE is_active = 1 ORDER BY name', [], (err, rows) => {
      db.close();
      if (err) {
        reject(err);
        return;
      }
      resolve(rows);
    });
  });
}

/**
 * 根据名称获取 Agent
 */
function getAgentByName(name) {
  return new Promise((resolve, reject) => {
    const db = getDb();
    
    db.get('SELECT * FROM agents WHERE name = ? AND is_active = 1', [name], (err, row) => {
      db.close();
      if (err) {
        reject(err);
        return;
      }
      resolve(row);
    });
  });
}

/**
 * 获取 Agent 地址
 */
function getAgentAddress(name) {
  return new Promise((resolve, reject) => {
    const agent = getAgentByName(name)
      .then(agent => {
        if (!agent) {
          throw new Error(`Agent not found: ${name}`);
        }
        return agent.target;
      })
      .catch(reject);
    
    agent.then(resolve).catch(reject);
  });
}

/**
 * 更新 Agent 地址
 */
function updateAgentAddress(name, newTarget) {
  return new Promise((resolve, reject) => {
    const db = getDb();
    
    db.run(
      'UPDATE agents SET target = ?, updated_at = CURRENT_TIMESTAMP WHERE name = ?',
      [newTarget, name],
      function(err) {
        db.close();
        if (err) {
          reject(err);
          return;
        }
        if (this.changes === 0) {
          reject(new Error(`Agent not found: ${name}`));
          return;
        }
        resolve({ changes: this.changes });
      }
    );
  });
}

/**
 * 添加或更新 Agent
 */
function upsertAgent(agent) {
  return new Promise((resolve, reject) => {
    const db = getDb();
    
    db.run(`
      INSERT INTO agents (name, role, target, description, capabilities, is_active)
      VALUES (?, ?, ?, ?, ?, 1)
      ON CONFLICT(name) DO UPDATE SET
        role = excluded.role,
        target = excluded.target,
        description = excluded.description,
        capabilities = excluded.capabilities,
        updated_at = CURRENT_TIMESTAMP
    `, [
      agent.name,
      agent.role,
      agent.target,
      agent.description,
      agent.capabilities
    ], function(err) {
      db.close();
      if (err) {
        reject(err);
        return;
      }
      resolve({ changes: this.changes, lastID: this.lastID });
    });
  });
}

/**
 * 激活或停用 Agent
 */
function toggleAgentStatus(name, isActive) {
  return new Promise((resolve, reject) => {
    const db = getDb();
    
    db.run(
      'UPDATE agents SET is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE name = ?',
      [isActive ? 1 : 0, name],
      function(err) {
        db.close();
        if (err) {
          reject(err);
          return;
        }
        if (this.changes === 0) {
          reject(new Error(`Agent not found: ${name}`));
          return;
        }
        resolve({ changes: this.changes });
      }
    );
  });
}

/**
 * 记录消息日志
 */
function logMessage(fromAgent, toAgent, message, status = 'sent') {
  return new Promise((resolve, reject) => {
    const db = getDb();
    
    db.run(
      'INSERT INTO message_logs (from_agent, to_agent, message, status) VALUES (?, ?, ?, ?)',
      [fromAgent, toAgent, message, status],
      function(err) {
        db.close();
        if (err) {
          reject(err);
          return;
        }
        resolve({ id: this.lastID });
      }
    );
  });
}

/**
 * 获取消息日志
 */
function getMessageLogs(limit = 50) {
  return new Promise((resolve, reject) => {
    const db = getDb();
    
    db.all(
      'SELECT * FROM message_logs ORDER BY created_at DESC LIMIT ?',
      [limit],
      (err, rows) => {
        db.close();
        if (err) {
          reject(err);
          return;
        }
        resolve(rows);
      }
    );
  });
}

/**
 * 验证 Agent 地址格式
 */
function validateAgentAddress(address) {
  const pattern = /^qqbot:(c2c|group):[a-zA-Z0-9_-]+$/;
  return pattern.test(address);
}

/**
 * 批量更新 Agent 地址
 */
function batchUpdateAddresses(updates) {
  return new Promise(async (resolve, reject) => {
    const results = [];
    
    for (const update of updates) {
      try {
        const result = await updateAgentAddress(update.name, update.target);
        results.push({ name: update.name, success: true, result });
      } catch (error) {
        results.push({ name: update.name, success: false, error: error.message });
      }
    }
    
    resolve(results);
  });
}

module.exports = {
  getAllAgents,
  getAgentByName,
  getAgentAddress,
  updateAgentAddress,
  upsertAgent,
  toggleAgentStatus,
  logMessage,
  getMessageLogs,
  validateAgentAddress,
  batchUpdateAddresses
};