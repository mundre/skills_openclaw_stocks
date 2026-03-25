/**
 * STP 对接验证脚本
 * 验证真实 STP skill 的集成
 */

const STPIntegrator = require('../core/stp-integrator-enhanced');

async function testSTPIntegration() {
    console.log('===== STP 对接验证 =====\n');
    
    const stpIntegrator = new STPIntegrator();
    
    try {
        // 1. 检查 STP 安装状态
        console.log('1. 检查 STP 安装状态...');
        const isInstalled = stpIntegrator.checkSTPInstalled();
        console.log('   STP 安装状态:', isInstalled ? '✅ 已安装' : '❌ 未安装');
        
        if (!isInstalled) {
            console.log('\n❌ STP 未安装，无法进行真实测试');
            return false;
        }
        
        // 2. 测试任务分解
        console.log('\n2. 测试任务分解...');
        const result = await stpIntegrator.splitTask(
            '开发一个简单的待办事项应用，支持添加、删除、标记完成功能',
            'Todo App'
        );
        
        console.log('✅ 任务分解成功');
        console.log('   来源:', result.metadata.source);
        console.log('   任务数:', result.tasks.length);
        
        // 3. 显示任务详情
        console.log('\n3. 任务详情:');
        result.tasks.forEach((task, index) => {
            console.log(`   ${index + 1}. ${task.name}`);
            console.log(`      类型：${task.type}`);
            console.log(`      优先级：${task.priority}`);
            console.log(`      预估时间：${task.estimated_hours} 小时`);
            console.log(`      依赖：${task.dependencies.length > 0 ? task.dependencies.join(', ') : '无'}`);
        });
        
        // 4. 显示执行计划
        console.log('\n4. 执行计划:');
        result.executionPlan.forEach((plan, index) => {
            console.log(`   ${index + 1}. ${plan.taskName} -> ${plan.agentType}`);
        });
        
        console.log('\n✅ STP 对接验证成功!');
        return true;
        
    } catch (error) {
        console.error('\n❌ STP 对接验证失败:', error.message);
        console.error(error.stack);
        return false;
    }
}

// 运行验证
testSTPIntegration().catch(console.error);
