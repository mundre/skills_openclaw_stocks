/**
 * Task Manager Test - 任务管理器测试
 */

const TaskManager = require('../core/task-manager');

async function runTests() {
    console.log('=== Task Manager Tests ===\n');
    
    const taskManager = new TaskManager({ dbPath: ':memory:' });
    
    // 测试 1: 创建项目
    console.log('Test 1: Create project');
    const project = await taskManager.createProject({
        name: 'Test Project',
        description: 'Test description',
        github_url: 'https://github.com/test/repo'
    });
    console.log('✅ Project created:', project.id);
    
    // 测试 2: 创建任务
    console.log('\nTest 2: Create task');
    const task = await taskManager.createTask({
        project_id: project.id,
        name: 'Test Task',
        description: 'Test task description',
        priority: 10
    });
    console.log('✅ Task created:', task.id);
    
    // 测试 3: 批量创建任务
    console.log('\nTest 3: Batch create tasks');
    const batchTasks = await taskManager.createBatchTasks(
        project.id,
        [
            { name: 'Task 1', description: 'Desc 1', priority: 10 },
            { name: 'Task 2', description: 'Desc 2', priority: 9 },
            { name: 'Task 3', description: 'Desc 3', priority: 8 }
        ]
    );
    console.log('✅ Batch created', batchTasks.length, 'tasks');
    
    // 测试 4: 任务依赖
    console.log('\nTest 4: Task dependencies');
    const task1 = await taskManager.createTask({
        project_id: project.id,
        name: 'Task A',
        priority: 10
    });
    const task2 = await taskManager.createTask({
        project_id: project.id,
        name: 'Task B',
        priority: 9
    });
    await taskManager.addTaskDependency(task2.id, task1.id);
    console.log('✅ Dependency added: Task B depends on Task A');
    
    // 测试 5: 检查依赖
    console.log('\nTest 5: Check dependencies');
    const depsMet1 = await taskManager.checkTaskDependencies(task1.id);
    console.log('Task A dependencies met:', depsMet1);
    
    const depsMet2 = await taskManager.checkTaskDependencies(task2.id);
    console.log('Task B dependencies met:', depsMet2);
    
    // 测试 6: 分配任务
    console.log('\nTest 6: Assign task');
    await taskManager.assignTask(task1.id, 'dev-agent');
    console.log('✅ Task A assigned to dev-agent');
    
    // 测试 7: 完成任务
    console.log('\nTest 7: Complete task');
    await taskManager.completeTask(task1.id, 'dev-agent');
    console.log('✅ Task A completed');
    
    // 测试 8: 再次检查依赖
    console.log('\nTest 8: Check dependencies again');
    const depsMet3 = await taskManager.checkTaskDependencies(task2.id);
    console.log('Task B dependencies met:', depsMet3);
    
    // 测试 9: 项目状态
    console.log('\nTest 9: Project status');
    const status = await taskManager.getProjectStatus(project.id);
    console.log('Project Status:', status);
    
    console.log('\n=== All Tests Completed ===');
}

runTests().catch(console.error);