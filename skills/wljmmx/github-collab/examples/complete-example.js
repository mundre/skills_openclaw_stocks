/**
 * GitHub 协作 - 完整示例
 * 
 * 本示例展示完整的 GitHub 协作流程：
 * - 任务创建与分解
 * - 多 Agent 协作
 * - 代码审查
 * - 自动部署
 * 
 * @author OpenClaw Team
 * @version 1.0.0
 */

const { TaskManager } = require('../core/task-manager-enhanced');
const { DevAgent } = require('../core/dev-agent');
const { TestAgent } = require('../core/test-agent');
const { ReviewAgent } = require('../core/review-agent');
const { DeployAgent } = require('../core/deploy-agent');
const { DocumentAgent } = require('../core/document-agent');
const { STPIntegrator } = require('../core/stp-integrator-enhanced');

async function main() {
    console.log('=== GitHub 协作 - 完整示例 ===\n');

    // 1. 初始化所有组件
    console.log('1. 初始化所有组件...');
    
    const taskManager = new TaskManager();
    await taskManager.initialize();
    console.log('✅ 任务管理器初始化完成');

    const devAgent = new DevAgent();
    await devAgent.initialize();
    console.log('✅ Dev Agent 初始化完成');

    const testAgent = new TestAgent();
    await testAgent.initialize();
    console.log('✅ Test Agent 初始化完成');

    const reviewAgent = new ReviewAgent();
    await reviewAgent.initialize();
    console.log('✅ Review Agent 初始化完成');

    const deployAgent = new DeployAgent();
    await deployAgent.initialize();
    console.log('✅ Deploy Agent 初始化完成');

    const documentAgent = new DocumentAgent();
    await documentAgent.initialize();
    console.log('✅ Document Agent 初始化完成');

    const stpIntegrator = new STPIntegrator();
    await stpIntegrator.initialize();
    console.log('✅ STP Integrator 初始化完成\n');

    // 2. 创建主任务
    console.log('2. 创建主任务...');
    const mainTask = await taskManager.createTask({
        name: '用户管理系统',
        description: '开发一个完整的用户管理系统',
        type: 'project',
        priority: 'high',
        assignee: 'system',
        dependencies: []
    });
    console.log(`✅ 主任务创建成功：${mainTask.id}\n`);

    // 3. 使用 STP 进行任务分解
    console.log('3. 使用 STP 进行任务分解...');
    const plan = await stpIntegrator.createPlan({
        task: mainTask,
        description: '开发用户管理系统，包含用户注册、登录、权限管理等功能'
    });
    console.log(`✅ 任务分解完成，生成 ${plan.steps.length} 个步骤\n`);

    // 4. 创建子任务
    console.log('4. 创建子任务...');
    const subTasks = [];
    for (const step of plan.steps) {
        const subTask = await taskManager.createTask({
            name: step.name,
            description: step.description,
            type: step.type,
            priority: step.priority,
            assignee: getAssigneeForStep(step),
            dependencies: step.dependencies || [],
            parentTask: mainTask.id
        });
        subTasks.push(subTask);
        console.log(`✅ 子任务创建：${subTask.name}`);
    }
    console.log('');

    // 5. 执行开发任务
    console.log('5. 执行开发任务...');
    for (const task of subTasks.filter(t => t.assignee === devAgent.agentId)) {
        console.log(`   执行：${task.name}`);
        await devAgent.processTask(task);
    }
    console.log('✅ 开发任务完成\n');

    // 6. 执行测试任务
    console.log('6. 执行测试任务...');
    for (const task of subTasks.filter(t => t.assignee === testAgent.agentId)) {
        console.log(`   测试：${task.name}`);
        await testAgent.processTask(task);
    }
    console.log('✅ 测试任务完成\n');

    // 7. 执行代码审查
    console.log('7. 执行代码审查...');
    for (const task of subTasks.filter(t => t.assignee === reviewAgent.agentId)) {
        console.log(`   审查：${task.name}`);
        await reviewAgent.processTask(task);
    }
    console.log('✅ 代码审查完成\n');

    // 8. 生成文档
    console.log('8. 生成文档...');
    await documentAgent.processTask({
        id: mainTask.id,
        name: '项目文档',
        description: '生成用户管理系统文档',
        type: 'documentation'
    });
    console.log('✅ 文档生成完成\n');

    // 9. 部署应用
    console.log('9. 部署应用...');
    await deployAgent.processTask({
        id: mainTask.id,
        action: 'deploy',
        environment: 'production',
        name: '用户管理系统部署'
    });
    console.log('✅ 部署完成\n');

    // 10. 完成主任务
    console.log('10. 完成主任务...');
    await taskManager.completeTask(mainTask.id);
    console.log('✅ 主任务完成\n');

    console.log('=== 完整示例完成 ===');
}

/**
 * 根据步骤类型分配 Agent
 */
function getAssigneeForStep(step) {
    switch (step.type) {
        case 'development':
            return 'dev-agent';
        case 'testing':
            return 'test-agent';
        case 'review':
            return 'review-agent';
        case 'documentation':
            return 'document-agent';
        default:
            return 'dev-agent';
    }
}

// 运行示例
main().catch(error => {
    console.error('示例运行失败:', error);
    process.exit(1);
});