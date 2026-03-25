/**
 * Task Manager
 * 任务管理模块 - 支持任务创建、分配、状态跟踪
 */

const { initDatabase, DB_PATH } = require('./init');

/**
 * 创建任务
 */
async function createTask(taskData) {
  const db = await initDatabase();
  
  return new Promise((resolve, reject) => {
    const {
      task_id,
      title,
      description,
      status = 'pending',
      priority = 'medium',
      assignee,
      created_by,
      github_issue_number,
      github_repo,
      metadata
    } = taskData;

    db.run(`
      INSERT INTO tasks (task_id, title, description, status, priority, assignee, created_by, github_issue_number, github_repo, metadata)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `, [
      task_id,
      title,
      description,
      status,
      priority,
      assignee || null,
      created_by || null,
      github_issue_number || null,
      github_repo || null,
      metadata ? JSON.stringify(metadata) : null
    ], function(err) {
      db.close();
      if (err) {
        reject(new Error(`创建任务失败：${err.message}`));
        return;
      }
      resolve({
        success: true,
        task_id,
        id: this.lastID
      });
    });
  });
}

/**
 * 获取任务
 */
async function getTask(taskId) {
  const db = await initDatabase();
  
  return new Promise((resolve, reject) => {
    db.get('SELECT * FROM tasks WHERE task_id = ?', [taskId], (err, row) => {
      db.close();
      if (err) {
        reject(new Error(`获取任务失败：${err.message}`));
        return;
      }
      if (row) {
        row.metadata = row.metadata ? JSON.parse(row.metadata) : null;
      }
      resolve(row);
    });
  });
}

/**
 * 获取所有任务
 */
async function getAllTasks(filters = {}) {
  const db = await initDatabase();
  
  let query = 'SELECT * FROM tasks WHERE 1=1';
  const params = [];
  
  if (filters.status) {
    query += ' AND status = ?';
    params.push(filters.status);
  }
  
  if (filters.assignee) {
    query += ' AND assignee = ?';
    params.push(filters.assignee);
  }
  
  if (filters.priority) {
    query += ' AND priority = ?';
    params.push(filters.priority);
  }
  
  query += ' ORDER BY created_at DESC';
  
  return new Promise((resolve, reject) => {
    db.all(query, params, (err, rows) => {
      db.close();
      if (err) {
        reject(new Error(`获取任务列表失败：${err.message}`));
        return;
      }
      // 解析 metadata
      const tasks = rows.map(row => {
        if (row.metadata) {
          row.metadata = JSON.parse(row.metadata);
        }
        return row;
      });
      resolve(tasks);
    });
  });
}

/**
 * 更新任务状态
 */
async function updateTaskStatus(taskId, status, changedBy = 'system') {
  const db = await initDatabase();
  
  return new Promise(async (resolve, reject) => {
    try {
      // 获取旧状态
      const oldTask = await getTask(taskId);
      if (!oldTask) {
        db.close();
        reject(new Error('任务不存在'));
        return;
      }
      
      // 更新任务状态
      db.run(`
        UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE task_id = ?
      `, [status, taskId], async function(err) {
        if (err) {
          db.close();
          reject(new Error(`更新任务状态失败：${err.message}`));
          return;
        }
        
        // 记录历史
        await logTaskHistory(db, taskId, 'status_update', oldTask.status, status, changedBy);
        
        db.close();
        resolve({
          success: true,
          task_id: taskId,
          old_status: oldTask.status,
          new_status: status
        });
      });
    } catch (error) {
      db.close();
      reject(error);
    }
  });
}

/**
 * 分配任务给 Agent
 */
async function assignTask(taskId, agentName, notes = '') {
  const db = await initDatabase();
  
  return new Promise(async (resolve, reject) => {
    try {
      // 检查任务是否存在
      const task = await getTask(taskId);
      if (!task) {
        db.close();
        reject(new Error('任务不存在'));
        return;
      }
      
      // 插入分配记录
      db.run(`
        INSERT INTO task_assignments (task_id, agent_name, status, notes)
        VALUES (?, ?, 'assigned', ?)
      `, [taskId, agentName, notes || null], async function(err) {
        if (err) {
          db.close();
          reject(new Error(`分配任务失败：${err.message}`));
          return;
        }
        
        // 更新任务的 assignee
        db.run(`
          UPDATE tasks SET assignee = ?, status = 'assigned', updated_at = CURRENT_TIMESTAMP WHERE task_id = ?
        `, [agentName, taskId], async function(err) {
          if (err) {
            db.close();
            reject(new Error(`更新任务 assignee 失败：${err.message}`));
            return;
          }
          
          // 记录历史
          await logTaskHistory(db, taskId, 'assignment', task.assignee, agentName, 'system');
          
          db.close();
          resolve({
            success: true,
            task_id: taskId,
            agent_name: agentName
          });
        });
      });
    } catch (error) {
      db.close();
      reject(error);
    }
  });
}

/**
 * 完成任务
 */
async function completeTask(taskId, agentName) {
  const db = await initDatabase();
  
  return new Promise(async (resolve, reject) => {
    try {
      // 更新任务状态
      await updateTaskStatus(taskId, 'completed', agentName);
      
      // 更新分配记录
      db.run(`
        UPDATE task_assignments 
        SET status = 'completed', completed_at = CURRENT_TIMESTAMP 
        WHERE task_id = ? AND agent_name = ? AND status = 'assigned'
      `, [taskId, agentName], function(err) {
        if (err) {
          db.close();
          reject(new Error(`标记任务完成失败：${err.message}`));
          return;
        }
        
        // 记录历史
        logTaskHistory(db, taskId, 'completion', 'assigned', 'completed', agentName);
        
        db.close();
        resolve({
          success: true,
          task_id: taskId,
          completed_by: agentName
        });
      });
    } catch (error) {
      db.close();
      reject(error);
    }
  });
}

/**
 * 记录任务历史
 */
async function logTaskHistory(db, taskId, action, oldValue, newValue, changedBy) {
  return new Promise((resolve) => {
    db.run(`
      INSERT INTO task_history (task_id, action, old_value, new_value, changed_by)
      VALUES (?, ?, ?, ?, ?)
    `, [taskId, action, oldValue || '', newValue || '', changedBy], function(err) {
      if (err) {
        console.error('记录任务历史失败:', err.message);
      }
      resolve();
    });
  });
}

/**
 * 获取任务历史
 */
async function getTaskHistory(taskId, limit = 50) {
  const db = await initDatabase();
  
  return new Promise((resolve, reject) => {
    db.all(`
      SELECT * FROM task_history 
      WHERE task_id = ? 
      ORDER BY created_at DESC 
      LIMIT ?
    `, [taskId, limit], (err, rows) => {
      db.close();
      if (err) {
        reject(new Error(`获取任务历史失败：${err.message}`));
        return;
      }
      resolve(rows);
    });
  });
}

/**
 * 获取待处理任务统计
 */
async function getTaskStats() {
  const db = await initDatabase();
  
  return new Promise((resolve, reject) => {
    db.all(`
      SELECT 
        status,
        COUNT(*) as count
      FROM tasks
      GROUP BY status
    `, (err, rows) => {
      db.close();
      if (err) {
        reject(new Error(`获取任务统计失败：${err.message}`));
        return;
      }
      
      const stats = {};
      rows.forEach(row => {
        stats[row.status] = row.count;
      });
      
      resolve(stats);
    });
  });
}

module.exports = {
  createTask,
  getTask,
  getAllTasks,
  updateTaskStatus,
  assignTask,
  completeTask,
  getTaskHistory,
  getTaskStats
};