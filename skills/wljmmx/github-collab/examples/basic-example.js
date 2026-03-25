/**
 * GitHub 协作 - 基础示例
 * 
 * 本示例展示如何使用 GitHub 协作技能的基础功能：
 * - 创建任务
 * - 分配任务
 * - 执行任务
 * 
 * @author OpenClaw Team
 * @version 1.0.0
 */

const { TaskManager } = require('../core/task-manager-enhanced');
const { DevAgent } = require('../core/dev-agent');
const { TestAgent } = require('../core/test-agent');

async function main() {
    console.log('=== GitHub 协作 - 基础示例 ===\n');

    // 1. 初始化任务管理器
    console.log('1. 初始化任务管理器...');
    const taskManager = new TaskManager();
    await taskManager.initialize();
    console.log('✅ 任务管理器初始化完成\n');

    // 2. 初始化 Agent
    console.log('2. 初始化 Agent...');
    const devAgent = new DevAgent();
    await devAgent.initialize();
    console.log('✅ Dev Agent 初始化完成');

    const testAgent = new TestAgent();
    await testAgent.initialize();
    console.log('✅ Test Agent 初始化完成\n');

    // 3. 创建任务
    console.log('3. 创建任务...');
    const task = await taskManager.createTask({
        name: '基础功能开发',
        description: '实现一个基础功能',
        type: 'development',
        priority: 'high',
        assignee: devAgent.agentId,
        dependencies: []
    });
    console.log(`✅ 任务创建成功: ${task.id}\n`);

    // 4. 分配任务
    console.log('4. 分配任务...');
    await taskManager.assignTask(task.id, devAgent.agentId);
    console.log('✅ 任务分配成功\n');

    // 5. 执行任务
    console.log('5. 执行任务...');
    const result = await devAgent.processTask({
        id: task.id,
        name: task.name,
        description: task.description,
        type: task.type
    });
    console.log(`✅ 任务执行完成: ${result.status}\n`);

    // 6. 运行测试
    console.log('6. 运行测试...');
    const testResult = await testAgent.processTask({
        id: task.id,
        name: task.name,
        description: task.description,
        type: 'testing'
    });
    console.log(`✅ 测试完成: ${testResult.status}\n`);

    // 7. 完成任务
    console.log('7. 完成任务...');
    await taskManager.completeTask(task.id);
    console.log('✅ 任务完成\n');

    console.log('=== 基础示例完成 ===');
}

// 运行示例
main().catch(error => {
    console.error('示例运行失败:', error);
    process.exit(1);
});