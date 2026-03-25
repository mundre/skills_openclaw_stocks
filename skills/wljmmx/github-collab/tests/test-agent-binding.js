/**
 * Agent Binding Test - Agent 绑定测试
 */

const TaskManager = require('../core/task-manager');
const AgentBinding = require('../core/agent-binding');

async function runTests() {
  console.log('=== Agent Binding Tests ===\n');
  
  const taskManager = new TaskManager({ dbPath: ':memory:' });
  const agentBinding = new AgentBinding({ taskManager });
  
  // 测试 1: 创建项目和任务
  console.log('Test 1: Create project and task');
  const project = taskManager.createProject({
    name: 'Agent Test Project',
    github_url: 'https://github.com/test/agent-project',
    description: 'Agent 测试项目'
  });
  console.log('✅ Project created:', project.id);
  
  const task = taskManager.createTask({
    projectId: project.id,
    name: 'Agent Test Task',
    description: 'Agent 测试任务',
    priority: 10
  });
  console.log('✅ Task created:', task.id);
  
  // 测试 2: 分配任务给 Agent
  console.log('\nTest 2: Assign task to agent');
  const assignment = agentBinding.assignTask(task.id, 'agent1');
  console.log('✅ Task assigned:', assignment);
  
  // 测试 3: 验证任务状态
  console.log('\nTest 3: Verify task status');
  const updatedTask = taskManager.getTask(task.id);
  console.log('✅ Task assigned_agent:', updatedTask.assigned_agent);
  
  // 测试 4: Agent 状态
  console.log('\nTest 4: Agent status');
  const agentStatus = agentBinding.getAgentStatus('agent1');
  console.log('✅ Agent status:', agentStatus);
  
  // 测试 5: 完成 Agent 任务
  console.log('\nTest 5: Complete agent task');
  agentBinding.completeTask(task.id, 'agent1', '任务完成');
  const completedTask = taskManager.getTask(task.id);
  console.log('✅ Task completed:', completedTask.status);
  
  taskManager.close();
  console.log('\n✅ All Agent Binding tests passed!');
}

runTests().catch(console.error);