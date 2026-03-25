/**
 * Dev Agent - 开发智能体
 * 职责：从自己的任务队列获取任务、执行开发任务、更新进度
 */

const TaskManager = require('./task-manager').TaskManager;

class DevAgent {
    constructor(agentId = 'dev-agent') {
        this.taskManager = new TaskManager();
        this.agentId = agentId;
        this.currentTask = null;
        this.taskQueue = [];
    }

    /**
     * 初始化 Agent（注册到系统）
     */
    async initialize() {
        console.log(`[Dev Agent] 初始化 Agent: ${this.agentId}`);
        this.taskManager.updateAgentStatus(this.agentId, 'idle');
        
        // 获取自己的任务队列
        await this.refreshTaskQueue();
    }

    /**
     * 刷新任务队列
     */
    async refreshTaskQueue() {
        this.taskQueue = await this.taskManager.getAgentTaskQueue(this.agentId);
        console.log(`[Dev Agent] 任务队列刷新：${this.taskQueue.length} 个任务`);
        return this.taskQueue;
    }

    /**
     * 获取下一个开发任务（从自己的任务队列）
     */
    async getNextTask() {
        // 从自己的任务队列获取下一个任务
        const task = await this.taskManager.getAgentNextTask(this.agentId);
        
        if (task) {
            this.currentTask = task;
            console.log(`[Dev Agent] 获取任务：${task.name} (ID: ${task.id})`);
            console.log(`[Dev Agent] 任务描述：${task.description || '无'}`);
            
            // 刷新任务队列
            await this.refreshTaskQueue();
        }
        
        return task;
    }

    /**
     * 执行开发任务
     * @param {Object} task - 任务对象
     * @param {Object} codeResult - 代码开发结果
     */
    async executeTask(task, codeResult = {}) {
        this.currentTask = task;
        
        console.log(`[Dev Agent] 开始执行：${task.name}`);
        
        // 模拟代码开发过程
        const result = {
            success: true,
            code: codeResult.code || '// 代码实现',
            tests: codeResult.tests || '// 测试用例',
            documentation: codeResult.documentation || '// 文档说明',
            files: codeResult.files || []
        };
        
        // 更新任务进度（模拟）
        const progress = codeResult.progress || 100;
        console.log(`[Dev Agent] 任务进度：${progress}%`);
        
        // 完成任务
        if (progress >= 100) {
            await this.taskManager.completeAgentTask(
                this.agentId, 
                task.id, 
                JSON.stringify(result),
                null
            );
            console.log(`[Dev Agent] 任务完成：${task.name}`);
            
            // 刷新任务队列
            await this.refreshTaskQueue();
        }
        
        return result;
    }

    /**
     * 报告任务完成
     * @param {number} taskId - 任务 ID
     * @param {string} notes - 完成备注
     */
    async reportCompletion(taskId, notes = '') {
        const result = {
            notes,
            timestamp: new Date().toISOString()
        };
        
        await this.taskManager.completeAgentTask(
            this.agentId,
            taskId,
            JSON.stringify(result),
            null
        );
        console.log(`[Dev Agent] 报告完成：${taskId}`);
        
        // 刷新任务队列
        await this.refreshTaskQueue();
    }

    /**
     * 报告任务阻塞
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
        console.log(`[Dev Agent] 报告阻塞：${taskId} - ${reason}`);
        
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
        console.log(`[Dev Agent] 开始工作循环`);
        
        // 初始化 Agent
        await this.initialize();
        
        while (true) {
            const task = await this.getNextTask();
            
            if (!task) {
                console.log(`[Dev Agent] 无可用任务，等待 5 秒`);
                await new Promise(resolve => setTimeout(resolve, 5000));
                continue;
            }
            
            // 执行任务
            try {
                await this.executeTask(task, {
                    code: `console.log("Implementing ${task.name}");`,
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
    const devAgent = new DevAgent('dev-agent');
    
    // 示例：获取并执行一个任务
    (async () => {
        await devAgent.initialize();
        
        // 获取任务队列状态
        const status = await devAgent.getTaskQueueStatus();
        console.log('\n=== 任务队列状态 ===');
        console.log(`总任务：${status.stats.total}`);
        console.log(`待处理：${status.stats.queued}`);
        console.log(`进行中：${status.stats.in_progress}`);
        console.log(`已完成：${status.stats.completed}`);
        console.log(`失败：${status.stats.failed}\n`);
        
        // 获取并执行任务
        const task = await devAgent.getNextTask();
        
        if (task) {
            await devAgent.executeTask(task, {
                code: 'console.log("Hello World");',
                progress: 100
            });
        } else {
            console.log('没有可用任务');
        }
    })();
}

module.exports = { DevAgent };