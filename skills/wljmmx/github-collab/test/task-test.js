/**
 * Task Manager Tests
 * 任务管理模块测试
 */

const { 
  createTask, 
  getTask, 
  getAllTasks, 
  updateTaskStatus,
  assignTask,
  completeTask,
  getTaskHistory,
  getTaskStats
} = require('../db/task-manager');

async function runTests() {
  console.log('🧪 开始任务管理测试...\n');
  
  // 测试 1: 创建任务
  console.log('测试 1: 创建任务');
  try {
    const taskData = {
      task_id: 'test-task-001',
      title: '测试任务',
      description: '这是一个测试任务',
      status: 'pending',
      priority: 'high',
      created_by: 'test-user'
    };
    
    const result = await createTask(taskData);
    console.log('✅ 任务创建成功:', result);
  } catch (error) {
    console.error('❌ 任务创建失败:', error.message);
  }
  
  // 测试 2: 获取任务
  console.log('\n测试 2: 获取任务');
  try {
    const task = await getTask('test-task-001');
    if (task) {
      console.log('✅ 任务获取成功:', task);
    } else {
      console.log('⚠️ 任务不存在（可能是第一次运行）');
    }
  } catch (error) {
    console.error('❌ 获取任务失败:', error.message);
  }
  
  // 测试 3: 获取所有任务
  console.log('\n测试 3: 获取所有任务');
  try {
    const tasks = await getAllTasks();
    console.log(`✅ 获取到 ${tasks.length} 个任务`);
    tasks.forEach(task => {
      console.log(`  - ${task.task_id}: ${task.title} (${task.status})`);
    });
  } catch (error) {
    console.error('❌ 获取任务列表失败:', error.message);
  }
  
  // 测试 4: 分配任务
  console.log('\n测试 4: 分配任务');
  try {
    const result = await assignTask('test-task-001', 'coder-agent', '测试分配');
    console.log('✅ 任务分配成功:', result);
  } catch (error) {
    console.error('❌ 任务分配失败:', error.message);
  }
  
  // 测试 5: 更新任务状态
  console.log('\n测试 5: 更新任务状态');
  try {
    const result = await updateTaskStatus('test-task-001', 'in_progress', 'coder-agent');
    console.log('✅ 任务状态更新成功:', result);
  } catch (error) {
    console.error('❌ 更新任务状态失败:', error.message);
  }
  
  // 测试 6: 完成任务
  console.log('\n测试 6: 完成任务');
  try {
    const result = await completeTask('test-task-001', 'coder-agent');
    console.log('✅ 任务完成成功:', result);
  } catch (error) {
    console.error('❌ 完成任务失败:', error.message);
  }
  
  // 测试 7: 获取任务历史
  console.log('\n测试 7: 获取任务历史');
  try {
    const history = await getTaskHistory('test-task-001');
    console.log(`✅ 获取到 ${history.length} 条历史记录`);
    history.forEach(record => {
      console.log(`  - ${record.action}: ${record.old_value || ''} -> ${record.new_value || ''}`);
    });
  } catch (error) {
    console.error('❌ 获取任务历史失败:', error.message);
  }
  
  // 测试 8: 获取任务统计
  console.log('\n测试 8: 获取任务统计');
  try {
    const stats = await getTaskStats();
    console.log('✅ 任务统计:', stats);
  } catch (error) {
    console.error('❌ 获取任务统计失败:', error.message);
  }
  
  console.log('\n✅ 所有测试完成！');
}

// 运行测试
runTests().catch(console.error);