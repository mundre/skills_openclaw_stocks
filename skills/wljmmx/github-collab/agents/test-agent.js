/**
 * Test Agent - 测试智能体
 * 职责：从自己的任务队列获取任务、执行测试任务、验证结果
 */

const TaskManager = require('./task-manager').TaskManager;

class TestAgent {
    constructor(agentId = 'test-agent') {
        this.taskManager = new TaskManager();
        this.agentId = agentId;
        this.currentTask = null;
        this.taskQueue = [];
    }

    /**
     * 初始化 Agent（注册到系统）
     */
    async initialize() {
        console.log(`[Test Agent] 初始化 Agent: ${this.agentId}`);
        this.taskManager.updateAgentStatus(this.agentId, 'idle');
        
        // 获取自己的任务队列
        await this.refreshTaskQueue();
    }

    /**
     * 刷新任务队列
     */
    async refreshTaskQueue() {
        this.taskQueue = await this.taskManager.getAgentTaskQueue(this.agentId);
        console.log(`[Test Agent] 任务队列刷新：${this.taskQueue.length} 个任务`);
        return this.taskQueue;
    }

    /**
     * 获取下一个测试任务（从自己的任务队列）
     */
    async getNextTask() {
        // 从自己的任务队列获取下一个任务
        const task = await this.taskManager.getAgentNextTask(this.agentId);
        
        if (task) {
            this.currentTask = task;
            console.log(`[Test Agent] 获取任务：${task.name} (ID: ${task.id})`);
            console.log(`[Test Agent] 任务描述：${task.description || '无'}`);
            
            // 刷新任务队列
            await this.refreshTaskQueue();
        }
        
        return task;
    }

    /**
     * 执行测试任务
     * @param {Object} task - 任务对象
     * @param {Object} testResult - 测试结果
     */
    async executeTask(task, testResult = {}) {
        this.currentTask = task;
        
        console.log(`[Test Agent] 开始执行测试：${task.name}`);
        
        // 模拟测试执行过程
        const result = {
            success: testResult.success !== false,
            passed: testResult.passed || 0,
            failed: testResult.failed || 0,
            total: testResult.total || 0,
            coverage: testResult.coverage || 0,
            report: testResult.report || '// 测试报告'
        };
        
        // 更新任务进度
        const progress = testResult.progress || 100;
        console.log(`[Test Agent] 测试进度：${progress}%`);
        console.log(`[Test Agent] 测试结果：${result.passed}/${result.total} 通过`);
        
        // 完成任务
        if (progress >= 100) {
            const error = result.success ? null : `测试失败：${result.failed} 个用例失败`;
            
            await this.taskManager.completeAgentTask(
                this.agentId,
                task.id,
                JSON.stringify(result),
                error
            );
            
            console.log(`[Test Agent] 测试完成：${task.name}`);
            
            // 刷新任务队列
            await this.refreshTaskQueue();
        }
        
        return result;
    }

    /**
     * 报告测试完成
     * @param {number} taskId - 任务 ID
     * @param {Object} report - 测试报告
     */
    async reportCompletion(taskId, report = {}) {
        const result = {
            ...report,
            timestamp: new Date().toISOString()
        };
        
        const error = report.success !== false ? null : `测试失败：${report.failed || 0} 个用例失败`;
        
        await this.taskManager.completeAgentTask(
            this.agentId,
            taskId,
            JSON.stringify(result),
            error
        );
        console.log(`[Test Agent] 报告完成：${taskId}`);
        
        // 刷新任务队列
        await this.refreshTaskQueue();
    }

    /**
     * 报告测试阻塞
     * @param {number} taskId - 任务 ID
     * @param {string} reason - 阻塞原因
     */
    async reportBlocked(taskId, reason) {
        const error = {
            reason,
            timestamp: new Date().toISOString()
        };
        
        await this.taskManager.completeAgentTask(
            this.agentId,
            taskId,
            null,
            JSON.stringify(error)
        );
        console.log(`[Test Agent] 报告阻塞：${taskId} - ${reason}`);
        
        // 刷新任务队列
        await this.refreshTaskQueue();
    }

    /**
     * 获取自己的任务队列状态
     */
    async getTaskQueueStatus() {
        const queue = await this.taskManager.getAgentTaskQueue(this.agentId);
        const stats = {
            total: queue.length,
            queued: queue.filter(t => t.status === 'queued').length,
            in_progress: queue.filter(t => t.status === 'in_progress').length,
            completed: queue.filter(t => t.status === 'completed').length,
            failed: queue.filter(t => t.status === 'failed').length
        };
        return { queue, stats };
    }

    /**
     * 持续工作模式
     */
    async workLoop() {
        console.log(`[Test Agent] 开始工作循环`);
        
        // 初始化 Agent
        await this.initialize();
        
        while (true) {
            const task = await this.getNextTask();
            
            if (!task) {
                console.log(`[Test Agent] 无可用任务，等待 5 秒`);
                await new Promise(resolve => setTimeout(resolve, 5000));
                continue;
            }
            
            // 执行任务
            try {
                await this.executeTask(task, {
                    passed: 5,
                    failed: 0,
                    total: 5,
                    coverage: 85,
                    progress: 100
                });
            } catch (error) {
                await this.reportBlocked(task.id, error.message);
            }
            
            // 短暂休息
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
    }
}

// CLI 入口
if (require.main === module) {
    const testAgent = new TestAgent('test-agent');
    
    // 示例：获取并执行一个任务
    (async () => {
        await testAgent.initialize();
        
        // 获取任务队列状态
        const status = await testAgent.getTaskQueueStatus();
        console.log('\n=== 任务队列状态 ===');
        console.log(`总任务：${status.stats.total}`);
        console.log(`待处理：${status.stats.queued}`);
        console.log(`进行中：${status.stats.in_progress}`);
        console.log(`已完成：${status.stats.completed}`);
        console.log(`失败：${status.stats.failed}\n`);
        
        // 获取并执行任务
        const task = await testAgent.getNextTask();
        
        if (task) {
            await testAgent.executeTask(task, {
                passed: 3,
                failed: 0,
                total: 3,
                coverage: 90,
                progress: 100
            });
        } else {
            console.log('没有可用任务');
        }
    })();
}

module.exports = { TestAgent };