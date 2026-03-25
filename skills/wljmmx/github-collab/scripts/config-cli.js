#!/usr/bin/env node

/**
 * Config CLI
 * 统一配置管理命令行工具 - 支持 Agent 和任务管理
 */

const ConfigManager = require('../db/config-manager');
const { updateAgentAddress, getAllAgents } = require('../db/agent-manager');
const { syncToCode } = require('../db/config-sync');
const { assignTask, completeTask, getAllTasks, getTask } = require('../db/task-manager');

const configManager = new ConfigManager();

/**
 * 显示帮助信息
 */
function showHelp() {
  console.log(`
🚀 统一配置管理工具 (Agent + 任务)

用法:
  node scripts/config-cli.js <command> [options]

Agent 命令:
  status              显示配置状态
  list                列出所有 Agent
  update <name> <address>  更新 Agent 地址
  backup              备份数据库
  restore <path>      恢复数据库
  export <path>       导出配置
  import <path>       导入配置
  cleanup [days]      清理过期日志（默认 30 天）
  summary             显示配置摘要

任务命令:
  task:list           列出所有任务
  task:show <id>      查看任务详情
  task:create <title> 创建任务
  task:assign <id> <agent> 分配任务给 Agent
  task:complete <id> <agent> 完成任务
  task:stats          显示任务统计

示例:
  # Agent 管理
  node scripts/config-cli.js status
  node scripts/config-cli.js list
  node scripts/config-cli.js update coder-agent qqbot:c2c:NEW_ID
  node scripts/config-cli.js backup
  
  # 任务管理
  node scripts/config-cli.js task:list
  node scripts/config-cli.js task:show task-001
  node scripts/config-cli.js task:assign task-001 coder-agent
  node scripts/config-cli.js task:complete task-001 coder-agent

环境配置:
  设置数据库路径：export DB_PATH=/path/to/custom.db
  或使用：DB_PATH=/path/to/custom.db node scripts/config-cli.js status
`);
}

/**
 * 显示配置状态
 */
async function showStatus() {
  const stats = await configManager.getDatabaseStats();
  
  console.log('\n=== 配置状态 ===\n');
  console.log(`数据库路径：${stats.dbPath}`);
  console.log(`数据库存在：${stats.databaseExists ? '✅' : '❌'}`);
  console.log(`配置文件存在：${stats.configFileExists ? '✅' : '❌'}`);
  
  if (stats.totalAgents !== undefined) {
    console.log(`\nAgent 统计:`);
    console.log(`  总数：${stats.totalAgents}`);
    console.log(`  活跃：${stats.activeAgents}`);
    console.log(`  停用：${stats.inactiveAgents}`);
  }
  
  if (stats.totalTasks !== undefined) {
    console.log(`\n任务统计:`);
    console.log(`  总数：${stats.totalTasks}`);
    if (stats.taskStats) {
      Object.entries(stats.taskStats).forEach(([status, count]) => {
        console.log(`  ${status}: ${count}`);
      });
    }
  } else if (stats.error) {
    console.log(`\n错误：${stats.error}`);
  }
}

/**
 * 列出所有 Agent
 */
async function listAgents() {
  try {
    const agents = await getAllAgents();
    
    console.log('\n=== Agent 列表 ===\n');
    
    if (agents.length === 0) {
      console.log('没有配置任何 Agent');
      return;
    }
    
    agents.forEach((agent, index) => {
      const status = agent.is_active === 1 ? '✅ 活跃' : '⏸️ 停用';
      console.log(`${index + 1}. ${agent.name}`);
      console.log(`   角色：${agent.role}`);
      console.log(`   地址：${agent.target}`);
      console.log(`   描述：${agent.description}`);
      console.log(`   状态：${status}`);
      console.log('');
    });
  } catch (error) {
    console.error('❌ 获取 Agent 列表失败:', error.message);
  }
}

/**
 * 更新 Agent 地址
 */
async function updateAgent(name, address) {
  try {
    const result = await updateAgentAddress(name, address);
    console.log(`✅ 已更新 Agent ${name} 的地址`);
    console.log(`   修改次数：${result.changes}`);
    
    await syncToCode();
    console.log('✅ 配置已同步到代码文件');
  } catch (error) {
    console.error('❌ 更新失败:', error.message);
  }
}

/**
 * 备份数据库
 */
async function backupDatabase() {
  const result = await configManager.backupDatabase();
  
  if (result.success) {
    console.log('✅ 数据库备份成功');
    console.log(`   备份路径：${result.backupPath}`);
    console.log(`   时间：${result.timestamp}`);
  } else {
    console.error('❌ 备份失败:', result.error);
  }
}

/**
 * 恢复数据库
 */
async function restoreDatabase(backupPath) {
  const result = await configManager.restoreDatabase(backupPath);
  
  if (result.success) {
    console.log('✅ 数据库恢复成功');
    console.log(`   恢复自：${result.restoredFrom}`);
    console.log(`   时间：${result.timestamp}`);
  } else {
    console.error('❌ 恢复失败:', result.error);
  }
}

/**
 * 导出配置
 */
async function exportConfig(exportPath) {
  const result = await configManager.exportConfig(exportPath);
  
  if (result.success) {
    console.log('✅ 配置导出成功');
    console.log(`   导出路径：${result.exportPath}`);
    console.log(`   Agent 数量：${result.agentCount}`);
    console.log(`   任务数量：${result.taskCount}`);
  } else {
    console.error('❌ 导出失败:', result.error);
  }
}

/**
 * 导入配置
 */
async function importConfig(importPath) {
  const result = await configManager.importConfig(importPath);
  
  if (result.success) {
    console.log('✅ 配置导入成功');
    console.log(`   Agent 成功：${result.importedAgents} 个`);
    console.log(`   Agent 失败：${result.failedAgents} 个`);
    console.log(`   任务成功：${result.importedTasks} 个`);
    console.log(`   任务失败：${result.failedTasks} 个`);
  } else {
    console.error('❌ 导入失败:', result.error);
  }
}

/**
 * 清理日志
 */
async function cleanupLogs(days = 30) {
  const result = await configManager.cleanupLogs(days);
  
  if (result.success) {
    console.log('✅ 日志清理成功');
    console.log(`   删除记录：${result.deletedCount}`);
  } else {
    console.error('❌ 清理失败:', result.error);
  }
}

/**
 * 显示配置摘要
 */
async function showSummary() {
  const summary = await configManager.getSummary();
  
  console.log('\n=== 配置摘要 ===\n');
  
  if (summary.error) {
    console.log(`错误：${summary.error}`);
    return;
  }
  
  console.log(`数据库路径：${summary.dbPath}`);
  console.log(`数据库存在：${summary.databaseExists ? '✅' : '❌'}`);
  console.log(`配置文件存在：${summary.configFileExists ? '✅' : '❌'}`);
  console.log(`\nAgent 统计:`);
  console.log(`  总数：${summary.totalAgents}`);
  console.log(`  活跃：${summary.activeAgents}`);
  console.log(`  停用：${summary.inactiveAgents}`);
  
  if (summary.totalTasks !== undefined) {
    console.log(`\n任务统计:`);
    console.log(`  总数：${summary.totalTasks}`);
    if (summary.taskStats) {
      Object.entries(summary.taskStats).forEach(([status, count]) => {
        console.log(`  ${status}: ${count}`);
      });
    }
  }
  
  if (summary.agents && summary.agents.length > 0) {
    console.log('\nAgent 列表:');
    summary.agents.forEach(agent => {
      const status = agent.isActive ? '✅' : '⏸️';
      console.log(`  ${status} ${agent.name} (${agent.role}): ${agent.target}`);
    });
  }
  
  if (summary.pendingTasks && summary.pendingTasks.length > 0) {
    console.log('\n待处理任务:');
    summary.pendingTasks.forEach(task => {
      console.log(`  📋 ${task.task_id}: ${task.title} (${task.status})`);
      if (task.assignee) {
        console.log(`     分配给：${task.assignee}`);
      }
    });
  }
  
  console.log(`\n最后更新：${summary.lastUpdated}`);
}

/**
 * 列出所有任务
 */
async function listTasks() {
  try {
    const tasks = await getAllTasks();
    
    console.log('\n=== 任务列表 ===\n');
    
    if (tasks.length === 0) {
      console.log('没有任务');
      return;
    }
    
    tasks.forEach((task, index) => {
      console.log(`${index + 1}. ${task.task_id}`);
      console.log(`   标题：${task.title}`);
      console.log(`   状态：${task.status}`);
      console.log(`   优先级：${task.priority}`);
      if (task.assignee) {
        console.log(`   分配给：${task.assignee}`);
      }
      console.log('');
    });
  } catch (error) {
    console.error('❌ 获取任务列表失败:', error.message);
  }
}

/**
 * 查看任务详情
 */
async function showTask(taskId) {
  try {
    const task = await getTask(taskId);
    
    if (!task) {
      console.log(`❌ 任务 ${taskId} 不存在`);
      return;
    }
    
    console.log('\n=== 任务详情 ===\n');
    console.log(`任务 ID: ${task.task_id}`);
    console.log(`标题：${task.title}`);
    console.log(`描述：${task.description || '无'}`);
    console.log(`状态：${task.status}`);
    console.log(`优先级：${task.priority}`);
    console.log(`分配给：${task.assignee || '未分配'}`);
    console.log(`创建者：${task.created_by || '未知'}`);
    if (task.github_issue_number) {
      console.log(`GitHub Issue: #${task.github_issue_number}`);
    }
    if (task.github_repo) {
      console.log(`GitHub Repo: ${task.github_repo}`);
    }
    console.log(`创建时间：${task.created_at}`);
    console.log(`更新时间：${task.updated_at}`);
  } catch (error) {
    console.error('❌ 获取任务失败:', error.message);
  }
}

/**
 * 分配任务
 */
async function assignTaskToAgent(taskId, agentName) {
  try {
    const result = await assignTask(taskId, agentName);
    
    if (result.success) {
      console.log(`✅ 任务 ${taskId} 已分配给 ${agentName}`);
    } else {
      console.error(`❌ 分配失败：${result.error}`);
    }
  } catch (error) {
    console.error('❌ 分配任务失败:', error.message);
  }
}

/**
 * 完成任务
 */
async function completeTaskById(taskId, agentName) {
  try {
    const result = await completeTask(taskId, agentName);
    
    if (result.success) {
      console.log(`✅ 任务 ${taskId} 已完成`);
      console.log(`   完成者：${result.completed_by}`);
    } else {
      console.error(`❌ 完成失败：${result.error}`);
    }
  } catch (error) {
    console.error('❌ 完成任务失败:', error.message);
  }
}

/**
 * 显示任务统计
 */
async function showTaskStats() {
  try {
    const stats = await getAllTasks();
    
    console.log('\n=== 任务统计 ===\n');
    
    const statusCounts = {};
    stats.forEach(task => {
      statusCounts[task.status] = (statusCounts[task.status] || 0) + 1;
    });
    
    console.log(`总任务数：${stats.length}`);
    Object.entries(statusCounts).forEach(([status, count]) => {
      console.log(`  ${status}: ${count}`);
    });
  } catch (error) {
    console.error('❌ 获取任务统计失败:', error.message);
  }
}

/**
 * 主函数
 */
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    showHelp();
    return;
  }
  
  const command = args[0];
  
  // 任务命令
  if (command.startsWith('task:')) {
    const subCommand = command.split(':')[1];
    const taskArgs = args.slice(1);
    
    switch (subCommand) {
      case 'list':
        await listTasks();
        break;
      case 'show':
        if (taskArgs.length < 1) {
          console.error('❌ 需要提供任务 ID');
          return;
        }
        await showTask(taskArgs[0]);
        break;
      case 'assign':
        if (taskArgs.length < 2) {
          console.error('❌ 需要提供任务 ID 和 Agent 名称');
          return;
        }
        await assignTaskToAgent(taskArgs[0], taskArgs[1]);
        break;
      case 'complete':
        if (taskArgs.length < 2) {
          console.error('❌ 需要提供任务 ID 和完成者 Agent');
          return;
        }
        await completeTaskById(taskArgs[0], taskArgs[1]);
        break;
      case 'stats':
        await showTaskStats();
        break;
      default:
        console.error('❌ 未知的任务命令');
        showHelp();
        break;
    }
    return;
  }
  
  // Agent 命令
  switch (command) {
    case 'status':
      await showStatus();
      break;
    case 'list':
      await listAgents();
      break;
    case 'update':
      if (args.length < 3) {
        console.error('❌ 参数错误！需要提供 Agent 名称和新地址');
        console.log('用法：node scripts/config-cli.js update <name> <address>');
        return;
      }
      await updateAgent(args[1], args[2]);
      break;
    case 'backup':
      await backupDatabase();
      break;
    case 'restore':
      if (args.length < 2) {
        console.error('❌ 参数错误！需要提供备份文件路径');
        console.log('用法：node scripts/config-cli.js restore <path>');
        return;
      }
      await restoreDatabase(args[1]);
      break;
    case 'export':
      const exportPath = args[1] || null;
      await exportConfig(exportPath);
      break;
    case 'import':
      if (args.length < 2) {
        console.error('❌ 参数错误！需要提供配置文件路径');
        console.log('用法：node scripts/config-cli.js import <path>');
        return;
      }
      await importConfig(args[1]);
      break;
    case 'cleanup':
      const days = args[1] ? parseInt(args[1]) : 30;
      await cleanupLogs(days);
      break;
    case 'summary':
      await showSummary();
      break;
    case 'help':
    default:
      showHelp();
      break;
  }
}

main().catch(console.error);