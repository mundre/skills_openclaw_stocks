/**
 * Task Manager Enhanced - 增强版任务管理器
 * 支持批量操作、缓存、索引、并发安全锁、崩溃恢复
 */

class TaskManagerEnhanced {
    constructor() {
        this.projects = new Map();
        this.tasks = new Map();
        this.dependencies = new Map();
        this.locks = new Map();
        this.state = {
            pendingTasks: [],
            runningTasks: [],
            completedTasks: []
        };
        
        // 性能优化
        this.taskIndex = new Map(); // priority -> taskIds
        this.cache = new Map();
        this.cacheSize = 0;
        this.maxCacheSize = 1000;
        
        // 崩溃恢复
        this.recoveryEnabled = true;
        this.saveInterval = 30 * 60 * 1000; // 30 分钟
        this.lastSaveTime = Date.now();
        
        this.logger = this.createLogger();
        
        // 启动自动保存
        this.startAutoSave();
        
        // 设置崩溃恢复
        this.setupCrashRecovery();
    }

    /**
     * 创建日志器
     */
    createLogger() {
        return {
            info: (msg) => console.log(`[TaskManager] ${msg}`),
            warn: (msg) => console.warn(`[TaskManager WARN] ${msg}`),
            error: (msg) => console.error(`[TaskManager ERROR] ${msg}`),
            debug: (msg) => console.log(`[TaskManager DEBUG] ${msg}`)
        };
    }

    /**
     * 启动自动保存
     */
    startAutoSave() {
        setInterval(async () => {
        await this.saveState();
        this.lastSaveTime = Date.now();
        this.logger.info('Auto-save completed');
        }, this.saveInterval);
    }

    /**
     * 设置崩溃恢复
     */
    setupCrashRecovery() {
        // 监听进程退出
        process.on('SIGTERM', async () => {
            this.logger.info('Received SIGTERM, saving state...');
            await this.saveState();
            process.exit(0);
        });

        process.on('SIGINT', async () => {
            this.logger.info('Received SIGINT, saving state...');
            await this.saveState();
            process.exit(0);
        });

        process.on('uncaughtException', async (error) => {
            this.logger.error('Uncaught exception:', error);
            await this.saveState();
        });

        process.on('unhandledRejection', async (reason, promise) => {
            this.logger.error('Unhandled rejection at:', promise, 'reason:', reason);
            await this.saveState();
        });
    }

    /**
     * 创建项目（带缓存）
     */
    async createProject(projectData) {
        const id = `project-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const project = {
            id,
            ...projectData,
            created_at: Date.now(),
            updated_at: Date.now()
        };

        this.projects.set(id, project);
        this.cacheSet(id, project);
        
        this.logger.info(`Project created: ${id}`);
        return project;
    }

    /**
     * 创建任务（带并发锁）
     */
    async createTask(taskData) {
        const id = `task-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const task = {
            id,
            ...taskData,
            status: 'pending',
            created_at: Date.now(),
            updated_at: Date.now(),
            dependencies: taskData.dependencies || []
        };

        // 加锁防止并发修改
        await this.acquireLock(id);
        
        try {
            this.tasks.set(id, task);
            this.cacheSet(id, task);
            
            // 更新索引
            this.updateTaskIndex(id, task.priority);
            
            this.logger.info(`Task created: ${id}`);
            return task;
        } finally {
            await this.releaseLock(id);
        }
    }

    /**
     * 批量创建任务（性能优化）
     */
    async createBatchTasks(projectId, taskList) {
        const tasks = [];
        
        // 批量加锁
        const lockIds = taskList.map(() => `batch-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
        for (const lockId of lockIds) {
            await this.acquireLock(lockId);
        }

        try {
            for (const taskData of taskList) {
                const task = await this.createTask({
                    ...taskData,
                    project_id: projectId
                });
                tasks.push(task);
            }
            
            this.logger.info(`Batch created ${tasks.length} tasks`);
            return tasks;
        } finally {
            // 批量释放锁
            for (const lockId of lockIds) {
                await this.releaseLock(lockId);
            }
        }
    }

    /**
     * 获取任务（带缓存）
     */
    async getTask(taskId) {
        // 检查缓存
        if (this.cache.has(taskId)) {
            const cached = this.cache.get(taskId);
            if (cached.timestamp > Date.now() - 5 * 60 * 1000) { // 5 分钟缓存
                return cached.data;
            }
        }

        // 从主存储获取
        const task = this.tasks.get(taskId);
        if (task) {
            this.cacheSet(taskId, task);
        }

        return task;
    }

    /**
     * 分配任务（带依赖检查）
     */
    async assignTask(taskId, agentId) {
        const task = await this.getTask(taskId);
        if (!task) {
            throw new Error(`Task ${taskId} not found`);
        }

        // 检查依赖
        const dependenciesMet = await this.checkTaskDependencies(taskId);
        if (!dependenciesMet) {
            throw new Error(`Task ${taskId} dependencies not met`);
        }

        // 加锁
        await this.acquireLock(taskId);
        
        try {
            task.status = 'assigned';
            task.assignee = agentId;
            task.updated_at = Date.now();
            
            this.tasks.set(taskId, task);
            this.cacheSet(taskId, task);
            
            this.logger.info(`Task ${taskId} assigned to ${agentId}`);
            return task;
        } finally {
            await this.releaseLock(taskId);
        }
    }

    /**
     * 完成任务
     */
    async completeTask(taskId, agentId) {
        const task = await this.getTask(taskId);
        if (!task) {
            throw new Error(`Task ${taskId} not found`);
        }

        await this.acquireLock(taskId);
        
        try {
            task.status = 'completed';
            task.completed_by = agentId;
            task.completed_at = Date.now();
            task.updated_at = Date.now();
            
            this.tasks.set(taskId, task);
            this.cacheSet(taskId, task);
            
            // 更新状态
            this.state.completedTasks.push(taskId);
            
            this.logger.info(`Task ${taskId} completed by ${agentId}`);
            return task;
        } finally {
            await this.releaseLock(taskId);
        }
    }

    /**
     * 检查任务依赖
     */
    async checkTaskDependencies(taskId) {
        const task = await this.getTask(taskId);
        if (!task || !task.dependencies || task.dependencies.length === 0) {
            return true;
        }

        for (const depId of task.dependencies) {
            const depTask = await this.getTask(depId);
            if (!depTask || depTask.status !== 'completed') {
                return false;
            }
        }

        return true;
    }

    /**
     * 添加任务依赖
     */
    async addTaskDependency(taskId, dependencyId) {
        const task = await this.getTask(taskId);
        if (!task) {
            throw new Error(`Task ${taskId} not found`);
        }

        await this.acquireLock(taskId);
        
        try {
            if (!task.dependencies.includes(dependencyId)) {
                task.dependencies.push(dependencyId);
                this.tasks.set(taskId, task);
                this.cacheSet(taskId, task);
            }
            
            this.logger.info(`Dependency added: ${taskId} depends on ${dependencyId}`);
        } finally {
            await this.releaseLock(taskId);
        }
    }

    /**
     * 获取任务列表（按优先级排序）
     */
    async getTaskList(projectId, options = {}) {
        const tasks = Array.from(this.tasks.values())
            .filter(t => !projectId || t.project_id === projectId)
            .sort((a, b) => b.priority - a.priority);

        // 分页
        if (options.limit) {
            return tasks.slice(0, options.limit);
        }

        return tasks;
    }

    /**
     * 获取项目状态
     */
    async getProjectStatus(projectId) {
        const tasks = await this.getTaskList(projectId);
        
        return {
            totalTasks: tasks.length,
            pendingTasks: tasks.filter(t => t.status === 'pending').length,
            assignedTasks: tasks.filter(t => t.status === 'assigned').length,
            completedTasks: tasks.filter(t => t.status === 'completed').length,
            failedTasks: tasks.filter(t => t.status === 'failed').length
        };
    }

    /**
     * 并发锁 - 获取锁
     */
    async acquireLock(resourceId, timeout = 5000) {
        const start = Date.now();
        
        while (Date.now() - start < timeout) {
            if (!this.locks.has(resourceId)) {
                this.locks.set(resourceId, { acquired: Date.now() });
                return true;
            }
            
            await this.delay(10);
        }
        
        throw new Error(`Timeout acquiring lock for ${resourceId}`);
    }

    /**
     * 并发锁 - 释放锁
     */
    async releaseLock(resourceId) {
        this.locks.delete(resourceId);
    }

    /**
     * 缓存设置
     */
    cacheSet(key, data) {
        if (this.cacheSize >= this.maxCacheSize) {
            // 清除最旧的缓存
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
            this.cacheSize--;
        }
        
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
        
        if (!this.cache.has(key)) {
            this.cacheSize++;
        }
    }

    /**
     * 更新任务索引
     */
    updateTaskIndex(taskId, priority) {
        if (!this.taskIndex.has(priority)) {
            this.taskIndex.set(priority, new Set());
        }
        this.taskIndex.get(priority).add(taskId);
    }

    /**
     * 保存状态（崩溃恢复）
     */
    async saveState() {
        const state = {
            timestamp: Date.now(),
            projects: Array.from(this.projects.entries()),
            tasks: Array.from(this.tasks.entries()),
            dependencies: Array.from(this.dependencies.entries()),
            state: this.state
        };

        const statePath = './task-manager-state.json';
        try {
            require('fs').writeFileSync(statePath, JSON.stringify(state, null, 2));
            this.logger.info('State saved successfully');
        } catch (error) {
            this.logger.error('Failed to save state:', error.message);
        }
    }

    /**
     * 恢复状态（崩溃恢复）
     */
    async restoreState() {
        const statePath = './task-manager-state.json';
        try {
            const fs = require('fs');
            if (!fs.existsSync(statePath)) {
                return;
            }

            const state = JSON.parse(fs.readFileSync(statePath, 'utf-8'));
            
            // 恢复项目
            for (const [id, project] of state.projects) {
                this.projects.set(id, project);
            }
            
            // 恢复任务
            for (const [id, task] of state.tasks) {
                this.tasks.set(id, task);
            }
            
            // 恢复依赖
            for (const [id, deps] of state.dependencies) {
                this.dependencies.set(id, deps);
            }
            
            this.logger.info(`State restored: ${state.projects.length} projects, ${state.tasks.length} tasks`);
        } catch (error) {
            this.logger.error('Failed to restore state:', error.message);
        }
    }

    /**
     * 延迟
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

module.exports = { TaskManagerEnhanced };