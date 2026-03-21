/**
 * Conversation Recovery Skill - Phase 3: Advanced Recovery
 *
 * Provides:
 * 1. Context Compression Algorithm - Retain key information, remove redundancy
 * 2. Intent Similarity Calculation - Jaccard + Semantic similarity
 * 3. Recovery Decision Algorithm - Select best snapshot for recovery
 * 4. External Change Detection - Compare current state with snapshot
 */
// ============================================================================
// Context Compression Algorithm
// ============================================================================
/**
 * Context Compressor class
 * Compresses snapshots by removing redundant and low-priority information
 */
export class ContextCompressor {
    options;
    constructor(options = {}) {
        this.options = {
            targetTokens: 2000,
            maxAgeDays: 30,
            minConfidence: 0.5,
            compressFulfilledIntents: true,
            compressCompletedTasks: true,
            compressInactiveFacts: true,
            priorityWeights: {
                critical: 1.0,
                high: 0.8,
                medium: 0.5,
                low: 0.3
            },
            ...options
        };
    }
    /**
     * Compress a snapshot to reduce token count while preserving key information
     */
    compress(snapshot) {
        const originalTokens = this.estimateTokens(snapshot);
        const cutoffDate = new Date();
        cutoffDate.setDate(cutoffDate.getDate() - this.options.maxAgeDays);
        // Filter and score intents
        const intentResult = this.compressIntents(snapshot.intents, cutoffDate);
        // Filter and score facts
        const factResult = this.compressFacts(snapshot.facts, cutoffDate);
        // Filter and score tasks
        const taskResult = this.compressTasks(snapshot.tasks, cutoffDate);
        // Create compressed snapshot
        const compressedSnapshot = {
            ...snapshot,
            intents: intentResult.retained,
            facts: factResult.retained,
            tasks: taskResult.retained,
            tokenCount: undefined // Will be recalculated
        };
        const compressedTokens = this.estimateTokens(compressedSnapshot);
        const compressionRatio = originalTokens > 0 ? compressedTokens / originalTokens : 1;
        return {
            snapshot: compressedSnapshot,
            metadata: {
                originalTokens,
                compressedTokens,
                compressionRatio,
                removedItems: {
                    intents: intentResult.removed,
                    facts: factResult.removed,
                    tasks: taskResult.removed
                },
                retainedItems: {
                    intents: intentResult.retained.length,
                    facts: factResult.retained.length,
                    tasks: taskResult.retained.length
                }
            }
        };
    }
    /**
     * Compress intents - remove fulfilled and low-confidence intents
     */
    compressIntents(intents, cutoffDate) {
        const scored = intents.map(intent => {
            let score = intent.confidence * 100;
            const age = new Date().getTime() - new Date(intent.createdAt).getTime();
            const ageInDays = age / (1000 * 60 * 60 * 24);
            // Penalize old intents
            if (ageInDays > 7)
                score *= 0.9;
            if (ageInDays > 14)
                score *= 0.8;
            // Penalize fulfilled intents if compression enabled
            if (this.options.compressFulfilledIntents && intent.fulfilled) {
                score *= 0.3;
            }
            return { intent, score };
        });
        // Sort by score descending
        scored.sort((a, b) => b.score - a.score);
        // Keep intents above threshold
        const retained = [];
        let removed = 0;
        for (const { intent, score } of scored) {
            if (score >= this.options.minConfidence * 100 && new Date(intent.createdAt) >= cutoffDate) {
                retained.push(intent);
            }
            else {
                removed++;
            }
        }
        return { retained, removed };
    }
    /**
     * Compress facts - remove inactive and low-confidence facts
     */
    compressFacts(facts, cutoffDate) {
        const scored = facts.map(fact => {
            let score = fact.confidence * 100;
            // Penalize inactive facts if compression enabled
            if (this.options.compressInactiveFacts && !fact.active) {
                score *= 0.4;
            }
            // Boost important categories
            if (fact.category === 'constraint')
                score *= 1.2;
            if (fact.category === 'decision')
                score *= 1.1;
            return { fact, score };
        });
        scored.sort((a, b) => b.score - a.score);
        const retained = [];
        let removed = 0;
        for (const { fact, score } of scored) {
            if (score >= this.options.minConfidence * 100 && new Date(fact.createdAt) >= cutoffDate) {
                retained.push(fact);
            }
            else {
                removed++;
            }
        }
        return { retained, removed };
    }
    /**
     * Compress tasks - remove completed and low-priority tasks
     */
    compressTasks(tasks, cutoffDate) {
        const scored = tasks.map(task => {
            let score = this.options.priorityWeights[task.priority] * 100;
            // Penalize completed tasks if compression enabled
            if (this.options.compressCompletedTasks && task.status === 'completed') {
                score *= 0.2;
            }
            // Boost in-progress tasks
            if (task.status === 'in_progress')
                score *= 1.2;
            // Boost blocked tasks
            if (task.status === 'blocked')
                score *= 1.1;
            // Penalize old tasks
            const age = new Date().getTime() - new Date(task.createdAt).getTime();
            const ageInDays = age / (1000 * 60 * 60 * 24);
            if (ageInDays > 7)
                score *= 0.95;
            return { task, score };
        });
        scored.sort((a, b) => b.score - a.score);
        const retained = [];
        let removed = 0;
        for (const { task, score } of scored) {
            if (score >= this.options.minConfidence * 100 && new Date(task.createdAt) >= cutoffDate) {
                retained.push(task);
            }
            else {
                removed++;
            }
        }
        return { retained, removed };
    }
    /**
     * Estimate token count for a snapshot
     * Rough estimate: 1 token ≈ 4 characters for English, 2 for Chinese
     */
    estimateTokens(snapshot) {
        let totalChars = 0;
        // Count description
        if (snapshot.description) {
            totalChars += snapshot.description.length;
        }
        // Count context
        if (snapshot.context) {
            totalChars += snapshot.context.length;
        }
        // Count intents
        for (const intent of snapshot.intents) {
            totalChars += intent.description.length;
        }
        // Count facts
        for (const fact of snapshot.facts) {
            totalChars += fact.statement.length;
        }
        // Count tasks
        for (const task of snapshot.tasks) {
            totalChars += task.description.length;
            if (task.dueDate)
                totalChars += task.dueDate.length;
        }
        // Rough estimate: 1 token ≈ 3 characters on average
        return Math.ceil(totalChars / 3);
    }
}
// ============================================================================
// Intent Similarity Calculation (Jaccard + Semantic)
// ============================================================================
/**
 * Similarity Calculator class
 * Calculates similarity between intents using Jaccard and semantic methods
 */
export class SimilarityCalculator {
    options;
    // Expanded keyword mappings for semantic similarity
    keywordExpansions = {
        'create': ['build', 'make', 'develop', 'generate', 'produce', 'design'],
        'delete': ['remove', 'eliminate', 'destroy', 'clear', 'erase'],
        'update': ['modify', 'change', 'edit', 'revise', 'alter', 'refresh'],
        'get': ['fetch', 'retrieve', 'obtain', 'acquire', 'read', 'load'],
        'send': ['transmit', 'deliver', 'dispatch', 'forward', 'post'],
        'find': ['search', 'locate', 'discover', 'identify', 'look for'],
        'fix': ['repair', 'resolve', 'solve', 'correct', 'debug', 'patch'],
        'add': ['insert', 'append', 'include', 'attach', 'incorporate'],
        'check': ['verify', 'validate', 'confirm', 'inspect', 'review'],
        'show': ['display', 'present', 'reveal', 'list', 'view'],
        'start': ['begin', 'initiate', 'launch', 'commence', 'open'],
        'stop': ['end', 'terminate', 'halt', 'close', 'finish'],
        'configure': ['setup', 'set up', 'adjust', 'customize', 'tune'],
        'install': ['deploy', 'setup', 'place', 'put', 'load'],
        'remove': ['delete', 'uninstall', 'eliminate', 'detach', 'clear'],
        'help': ['assist', 'support', 'aid', 'guide', 'advice'],
        'want': ['need', 'desire', 'wish', 'would like', 'intend'],
        'plan': ['schedule', 'arrange', 'organize', 'prepare', 'design'],
        'problem': ['issue', 'error', 'bug', 'trouble', 'difficulty'],
        'question': ['query', 'inquiry', 'doubt', 'uncertainty'],
        // Chinese expansions
        '创建': ['建立', '生成', '制作', '开发', '设计'],
        '删除': ['移除', '清除', '销毁', '去掉'],
        '修改': ['更新', '编辑', '更改', '调整', '变更'],
        '获取': ['得到', '读取', '加载', '取得', '获得'],
        '发送': ['传送', '递交', '转发', '提交'],
        '查找': ['搜索', '寻找', '定位', '发现'],
        '修复': ['解决', '修理', '纠正', '调试'],
        '添加': ['插入', '附加', '包含', '加入'],
        '检查': ['验证', '确认', '审查', '查看'],
        '显示': ['展示', '呈现', '列出', '查看'],
        '开始': ['启动', '开启', '发起', '着手'],
        '停止': ['结束', '终止', '关闭', '暂停'],
        '配置': ['设置', '调整', '定制', '调优'],
        '安装': ['部署', '装载', '放置'],
        '帮助': ['协助', '支持', '辅助', '指导'],
        '需要': ['想要', '希望', '打算', '计划'],
        '问题': ['错误', '故障', '困难', '疑问']
    };
    constructor(options = {}) {
        this.options = {
            jaccardWeight: 0.4,
            semanticWeight: 0.6,
            threshold: 0.6,
            useKeywordExpansion: true,
            ...options
        };
    }
    /**
     * Calculate similarity between two intents
     */
    calculateIntentSimilarity(intentA, intentB) {
        const jaccardScore = this.calculateJaccardSimilarity(intentA);
    }
}
//# sourceMappingURL=recovery.js.map