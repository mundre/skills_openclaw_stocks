/**
 * 集成测试 - 测试多个模块协同工作
 */

const TaskManager = require('../core/task-manager');
const AgentBinding = require('../core/agent-binding');
const STPIntegrator = require('../core/stp-integrator-enhanced');

describe('Integration Tests', () => {
  let taskManager;
  let agentBinding;
  let stpIntegrator;

  beforeAll(() => {
    taskManager = new TaskManager(':memory:');
    agentBinding = new AgentBinding(taskManager);
    stpIntegrator = new STPIntegrator(taskManager);
  });

  afterAll(() => {
    taskManager.close();
  });

  test('完整的任务创建和分配流程', () => {
    // 创建项目
    const project = taskManager.createProject({
      name: 'Test Project',
      github_url: 'https://github.com/test/project',
      description: '测试项目'
    });

    expect(project.id).toBeDefined();
    expect(project.name).toBe('Test Project');

    // 创建任务
    const task = taskManager.createTask({
      projectId: project.id,
      name: 'Test Task',
      description: '测试任务',
      priority: 10
    });

    expect(task.id).toBeDefined();
    expect(task.name).toBe('Test Task');
    expect(task.status).toBe('pending');

    // 分配给 Agent
    const assignment = agentBinding.assignTask(task.id, 'agent1');
    expect(assignment).toBeDefined();
    expect(assignment.taskId).toBe(task.id);
    expect(assignment.agentName).toBe('agent1');

    // 验证任务状态更新
    const updatedTask = taskManager.getTask(task.id);
    expect(updatedTask.assigned_agent).toBe('agent1');
  });

  test('STP 任务分解和创建', () => {
    const project = taskManager.createProject({
      name: 'STP Test Project',
      github_url: 'https://github.com/test/stp-project',
      description: 'STP 测试项目'
    });

    // 使用 STP 分解任务
    const tasks = stpIntegrator.splitTask({
      project: project,
      description: '创建一个简单的 Web 应用，包括前端和后端'
    });

    expect(tasks).toBeDefined();
    expect(tasks.length).toBeGreaterThan(0);

    // 验证任务已创建
    const firstTask = tasks[0];
    const dbTask = taskManager.getTask(firstTask.id);
    expect(dbTask).toBeDefined();
    expect(dbTask.projectId).toBe(project.id);
  });

  test('任务状态流转', () => {
    const project = taskManager.createProject({
      name: 'Status Test Project',
      github_url: 'https://github.com/test/status-project',
      description: '状态测试项目'
    });

    const task = taskManager.createTask({
      projectId: project.id,
      name: 'Status Task',
      description: '状态测试任务',
      priority: 5
    });

    // 初始状态
    expect(task.status).toBe('pending');

    // 开始任务
    taskManager.updateTaskStatus(task.id, 'in_progress');
    let updatedTask = taskManager.getTask(task.id);
    expect(updatedTask.status).toBe('in_progress');

    // 完成任务
    taskManager.updateTaskStatus(task.id, 'completed', {
      result: '任务完成',
      completedAt: new Date().toISOString()
    });
    updatedTask = taskManager.getTask(task.id);
    expect(updatedTask.status).toBe('completed');
    expect(updatedTask.result).toBe('任务完成');
  });

  test('多 Agent 协作', () => {
    const project = taskManager.createProject({
      name: 'Multi Agent Project',
      github_url: 'https://github.com/test/multi-agent',
      description: '多 Agent 测试项目'
    });

    // 创建多个任务
    const tasks = [];
    for (let i = 1; i <= 3; i++) {
      const task = taskManager.createTask({
        projectId: project.id,
        name: `Task ${i}`,
        description: `测试任务 ${i}`,
        priority: 10 - i
      });
      tasks.push(task);
    }

    // 分配给不同的 Agent
    const agents = ['agent1', 'agent2', 'agent3'];
    tasks.forEach((task, index) => {
      agentBinding.assignTask(task.id, agents[index]);
    });

    // 验证所有任务都已分配
    tasks.forEach((task, index) => {
      const updatedTask = taskManager.getTask(task.id);
      expect(updatedTask.assigned_agent).toBe(agents[index]);
    });
  });

  test('任务优先级排序', () => {
    const project = taskManager.createProject({
      name: 'Priority Test Project',
      github_url: 'https://github.com/test/priority-project',
      description: '优先级测试项目'
    });

    // 创建不同优先级的任务
    const task1 = taskManager.createTask({
      projectId: project.id,
      name: 'Low Priority',
      priority: 1
    });

    const task2 = taskManager.createTask({
      projectId: project.id,
      name: 'High Priority',
      priority: 10
    });

    const task3 = taskManager.createTask({
      projectId: project.id,
      name: 'Medium Priority',
      priority: 5
    });

    // 获取按优先级排序的任务
    const sortedTasks = taskManager.getTasksByProject(project.id, {
      sortBy: 'priority',
      sortOrder: 'desc'
    });

    expect(sortedTasks[0].name).toBe('High Priority');
    expect(sortedTasks[1].name).toBe('Medium Priority');
    expect(sortedTasks[2].name).toBe('Low Priority');
  });
});