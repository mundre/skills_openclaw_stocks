/**
 * Conversation Recovery Skill - Phase 2: Intelligent Analysis
 *
 * Provides:
 * 1. Context Analyzer - Extracts intents, facts, and tasks from conversation
 * 2. Intent Extraction Algorithm - Keyword-based + LLM-based extraction
 * 3. Fact Extraction and Validation - Identifies and validates facts
 * 4. Task Recognition and Priority Assessment - Identifies tasks and assigns priorities
 */
// ============================================================================
// Context Analyzer - Main Entry Point
// ============================================================================
/**
 * Context Analyzer class
 * Orchestrates the extraction of intents, facts, and tasks from conversation
 */
export class ContextAnalyzer {
    options;
    intentExtractor;
    factExtractor;
    taskExtractor;
    constructor(options = {}) {
        this.options = {
            method: 'hybrid',
            confidenceThreshold: 0.5,
            useLLM: true,
            ...options
        };
        this.intentExtractor = new IntentExtractor();
        this.factExtractor = new FactExtractor();
        this.taskExtractor = new TaskExtractor();
    }
    /**
     * Analyze conversation messages and extract intents, facts, and tasks
     */
    async analyze(messages) {
        const analyzedAt = new Date().toISOString();
        const tokenCount = this.estimateTokenCount(messages);
        // Extract intents
        const intentExtractions = await this.intentExtractor.extract(messages, this.options.method, this.options.existingIntents);
        // Extract facts
        const factExtractions = await this.factExtractor.extract(messages, this.options.method, this.options.existingFacts);
        // Extract tasks
        const taskExtractions = await this.taskExtractor.extract(messages, this.options.method, this.options.existingTasks);
        // Convert extractions to model types
        const intents = this.convertToIntents(intentExtractions);
        const facts = this.convertToFacts(factExtractions);
        const tasks = this.convertToTasks(taskExtractions);
        // Merge with existing context if provided
        const mergedIntents = this.mergeIntents(intents, this.options.existingIntents || []);
        const mergedFacts = this.mergeFacts(facts, this.options.existingFacts || []);
        const mergedTasks = this.mergeTasks(tasks, this.options.existingTasks || []);
        // Calculate overall confidence
        const confidence = this.calculateOverallConfidence(intentExtractions, factExtractions, taskExtractions);
        return {
            intents: mergedIntents,
            facts: mergedFacts,
            tasks: mergedTasks,
            metadata: {
                analyzedAt,
                method: this.options.method,
                confidence,
                tokenCount
            }
        };
    }
    /**
     * Quick analysis using keyword-based extraction only
     */
    async analyzeQuick(messages) {
        const originalMethod = this.options.method;
        this.options.method = 'keyword';
        const result = await this.analyze(messages);
        this.options.method = originalMethod;
        return result;
    }
    /**
     * Estimate token count from messages
     */
    estimateTokenCount(messages) {
        // Rough estimate: 1 token ≈ 4 characters for English, 2 for Chinese
        const totalChars = messages.reduce((sum, m) => sum + m.content.length, 0);
        return Math.ceil(totalChars / 3);
    }
    /**
     * Convert intent extractions to Intent model
     */
    convertToIntents(extractions) {
        return extractions
            .filter(e => e.confidence >= (this.options.confidenceThreshold || 0.5))
            .map(e => ({
            id: this.generateId('intent'),
            description: e.description,
            confidence: e.confidence,
            sourceMessageId: e.sourceMessageId,
            fulfilled: false,
            createdAt: new Date().toISOString()
        }));
    }
    /**
     * Convert fact extractions to Fact model
     */
    convertToFacts(extractions) {
        return extractions
            .filter(e => e.confidence >= (this.options.confidenceThreshold || 0.5))
            .map(e => ({
            id: this.generateId('fact'),
            statement: e.statement,
            category: e.category,
            sourceMessageId: e.sourceMessageId,
            confidence: e.confidence,
            active: true,
            createdAt: new Date().toISOString()
        }));
    }
    /**
     * Convert task extractions to Task model
     */
    convertToTasks(extractions) {
        const now = new Date().toISOString();
        return extractions
            .filter(e => e.confidence >= (this.options.confidenceThreshold || 0.5))
            .map(e => ({
            id: this.generateId('task'),
            description: e.description,
            status: 'pending',
            priority: e.priority,
            relatedIntentIds: [],
            dependencies: [],
            dueDate: e.dueDate,
            createdAt: now,
            updatedAt: now
        }));
    }
    /**
     * Merge new intents with existing ones, avoiding duplicates
     */
    mergeIntents(newIntents, existing) {
        const merged = [...existing];
        for (const newIntent of newIntents) {
            const isDuplicate = existing.some(e => this.similarity(e.description, newIntent.description) > 0.8);
            if (!isDuplicate) {
                merged.push(newIntent);
            }
        }
        return merged;
    }
    /**
     * Merge new facts with existing ones, avoiding duplicates
     */
    mergeFacts(newFacts, existing) {
        const merged = [...existing];
        for (const newFact of newFacts) {
            const isDuplicate = existing.some(e => this.similarity(e.statement, newFact.statement) > 0.85);
            if (!isDuplicate) {
                merged.push(newFact);
            }
        }
        return merged;
    }
    /**
     * Merge new tasks with existing ones, avoiding duplicates
     */
    mergeTasks(newTasks, existing) {
        const merged = [...existing];
        for (const newTask of newTasks) {
            const isDuplicate = existing.some(e => this.similarity(e.description, newTask.description) > 0.85);
            if (!isDuplicate) {
                merged.push(newTask);
            }
        }
        return merged;
    }
    /**
     * Calculate overall confidence score
     */
    calculateOverallConfidence(intents, facts, tasks) {
        const allConfidences = [
            ...intents.map(i => i.confidence),
            ...facts.map(f => f.confidence),
            ...tasks.map(t => t.confidence)
        ];
        if (allConfidences.length === 0)
            return 0;
        const sum = allConfidences.reduce((a, b) => a + b, 0);
        return sum / allConfidences.length;
    }
    /**
     * Calculate simple string similarity (Jaccard index)
     */
    similarity(a, b) {
        const setA = new Set(a.toLowerCase().split(/\s+/));
        const setB = new Set(b.toLowerCase().split(/\s+/));
        const intersection = new Set([...setA].filter(x => setB.has(x)));
        const union = new Set([...setA, ...setB]);
        return intersection.size / union.size;
    }
    /**
     * Generate unique ID
     */
    generateId(prefix) {
        return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
}
// ============================================================================
// Intent Extractor - Extract user intents from conversation
// ============================================================================
/**
 * Intent Extractor class
 * Uses keyword-based and LLM-based methods to extract user intents
 */
export class IntentExtractor {
    // Intent keywords for pattern matching
    intentPatterns = [
        // Goal/Objective patterns
        { pattern: /(?:I want to|I need to|I'd like to|我想|我要|我需要)\s+(.+?)(?:\.|$|,|，)/gi, weight: 0.9, type: 'goal' },
        { pattern: /(?:my goal is|my objective is|the goal is)\s+(.+?)(?:\.|$|,)/gi, weight: 0.9, type: 'goal' },
        { pattern: /(?:planning to|plan to|打算|计划)\s+(.+?)(?:\.|$|,|，)/gi, weight: 0.85, type: 'plan' },
        // Question/Help patterns
        { pattern: /(?:how (?:do|can|should) I|how to|怎么|如何)\s+(.+?)(?:\?|$)/gi, weight: 0.8, type: 'question' },
        { pattern: /(?:help me|assist me|帮我|帮助我)\s+(?:to\s+)?(.+?)(?:\.|$|,|，)/gi, weight: 0.85, type: 'help' },
        // Action patterns
        { pattern: /(?:create|make|build|develop|write|generate)\s+(?:a|an|the)?\s*(.+?)(?:\.|$|,|，)/gi, weight: 0.8, type: 'action' },
        { pattern: /(?:fix|solve|resolve|debug|repair)\s+(?:the|this|that)?\s*(.+?)(?:\.|$|,|，)/gi, weight: 0.8, type: 'fix' },
        // Request patterns
        { pattern: /(?:can you|could you|would you|please)\s+(.+?)(?:\?|$)/gi, weight: 0.75, type: 'request' },
        { pattern: /(?:能否|可以|请)\s*(?:帮我)?\s*(.+?)(?:\?|$|，|。)/gi, weight: 0.75, type: 'request' },
        // Problem patterns
        { pattern: /(?:I'm having trouble with|I'm struggling with|I have a problem with|遇到|问题)\s+(.+?)(?:\.|$|,|，)/gi, weight: 0.8, type: 'problem' },
        // Comparison/Decision patterns
        { pattern: /(?:compare|choose between|decide between|对比|选择|比较)\s+(.+?)(?:\.|$|,|，)/gi, weight: 0.75, type: 'decision' },
        { pattern: /(?:should I|which (?:one|option)|whether to)\s+(.+?)(?:\?|$)/gi, weight: 0.75, type: 'decision' },
    ];
    /**
     * Extract intents from messages
     */
    async extract(messages, method = 'hybrid', existingIntents) {
        const extractions = [];
        // Keyword-based extraction
        if (method === 'keyword' || method === 'hybrid') {
            const keywordResults = this.extractByKeywords(messages);
            extractions.push(...keywordResults);
        }
        // LLM-based extraction (simulated for now)
        if (method === 'llm' || method === 'hybrid') {
            const llmResults = await this.extractByLLM(messages, existingIntents);
            extractions.push(...llmResults);
        }
        // Deduplicate and sort by confidence
        return this.deduplicateIntents(extractions);
    }
    /**
     * Extract intents using keyword patterns
     */
    extractByKeywords(messages) {
        const extractions = [];
        for (const message of messages) {
            if (message.role !== 'user')
                continue;
            for (const { pattern, weight, type } of this.intentPatterns) {
                const matches = message.content.matchAll(pattern);
                for (const match of matches) {
                    const description = match[1]?.trim() || match[0]?.trim();
                    if (description && description.length > 5) {
                        // Calculate confidence based on pattern weight and description length
                        const lengthBonus = Math.min(description.length / 100, 0.1);
                        const confidence = Math.min(weight + lengthBonus, 1.0);
                        extractions.push({
                            description: this.cleanIntentDescription(description, type),
                            confidence,
                            sourceMessageId: message.id
                        });
                    }
                }
            }
        }
        return extractions;
    }
    /**
     * Extract intents using LLM (simulated implementation)
     * In production, this would call an actual LLM API
     */
    async extractByLLM(messages, existingIntents) {
        // This is a placeholder for LLM-based extraction
        // In production, this would:
        // 1. Format messages for LLM
        // 2. Send to LLM with prompt for intent extraction
        // 3. Parse and return structured results
        // For now, return empty array - keyword extraction handles most cases
        // When LLM is available, it would catch nuanced intents missed by patterns
        return [];
    }
    /**
     * Clean and normalize intent description
     */
    cleanIntentDescription(description, type) {
        let cleaned = description
            .replace(/^(?:to|with|for|about)\s+/i, '')
            .replace(/\s+/g, ' ')
            .trim();
        // Capitalize first letter
        cleaned = cleaned.charAt(0).toUpperCase() + cleaned.slice(1);
        return cleaned;
    }
    /**
     * Deduplicate intents by similarity
     */
    deduplicateIntents(extractions) {
        const unique = [];
        for (const extraction of extractions) {
            const isDuplicate = unique.some(u => this.similarity(u.description, extraction.description) > 0.75);
            if (!isDuplicate) {
                unique.push(extraction);
            }
        }
        // Sort by confidence descending
        return unique.sort((a, b) => b.confidence - a.confidence);
    }
    /**
     * Calculate string similarity
     */
    similarity(a, b) {
        const setA = new Set(a.toLowerCase().split(/\s+/));
        const setB = new Set(b.toLowerCase().split(/\s+/));
        const intersection = new Set([...setA].filter(x => setB.has(x)));
        const union = new Set([...setA, ...setB]);
        return intersection.size / union.size;
    }
}
// ============================================================================
// Fact Extractor - Extract facts from conversation
// ============================================================================
/**
 * Fact Extractor class
 * Identifies and validates facts established in conversation
 */
export class FactExtractor {
    // Fact patterns by category
    factPatterns = {
        preference: [
            { pattern: /(?:I prefer|I like|I enjoy|I want|I'd rather|我喜欢|我偏好|我更喜欢)\s+(.+?)(?:\.|$|,|，)/gi, weight: 0.85 },
            { pattern: /(?:my favorite|my preferred|我最喜欢的|我的最爱)\s+(?:is|are)?\s*(.+?)(?:\.|$|,|，)/gi, weight: 0.9 },
            { pattern: /(?:I don't like|I dislike|I hate|我不喜欢|我讨厌)\s+(.+?)(?:\.|$|,|，)/gi, weight: 0.8 },
        ],
        constraint: [
            { pattern: /(?:I (?:only|just) have|I have (?:only|just)|I have limited|limited to|only|我只有|我只有|仅限于)\s+(.+?)(?:\.|$|,|，)/gi, weight: 0.85 },
            { pattern: /(?:must|need to|have to|required|required to|必须|需要|得)\s+(.+?)(?:\.|$|,|，)/gi, weight: 0.8 },
            { pattern: /(?:can't|cannot|unable to|won't be able to|不能|无法|不可以)\s+(.+?)(?:\.|$|,|，)/gi, weight: 0.8 },
            { pattern: /(?:budget|cost|price|limit|maximum|minimum|预算|成本|价格|限制)\s+(?:is|of)?\s*[:\s]*(.+?)(?:\.|$|,|，)/gi, weight: 0.85 },
            { pattern: /(?:deadline|due|by|before|期限|截止日期|之前)\s+(.+?)(?:\.|$|,|，)/gi, weight: 0.85 },
        ],
        context: [
            { pattern: /(?:I'm working on|I'm using|we're using|we use|我正在用|我们在用|使用)\s+(.+?)(?:\.|$|,|，)/gi, weight: 0.8 },
            { pattern: /(?:currently|right now|at the moment|目前|当前|现在)\s+(.+?)(?:\.|$|,|，)/gi, weight: 0.75 },
            { pattern: /(?:in my project|for my project|in our|在我们的|在我的)\s+(.+?)(?:\.|$|,|，)/gi, weight: 0.8 },
        ],
        decision: [
            { pattern: /(?:I decided|we decided|decision is|决定|我决定|我们决定)\s+(?:to|on)?\s*(.+?)(?:\.|$|,|，)/gi, weight: 0.9 },
            { pattern: /(?:let's go with|we'll use|let's choose|选择|选用|用)\s+(.+?)(?:\.|$|,|，)/gi, weight: 0.85 },
            { pattern: /(?:agreed|agreement|settled on|finalized|确定|敲定|同意)\s+(?:on|to)?\s*(.+?)(?:\.|$|,|，)/gi, weight: 0.9 },
        ],
        requirement: [
            { pattern: /(?:needs? to|should|must|requirements?|需求|要求|需要)\s+(?:be|have)?\s*(.+?)(?:\.|$|,|，)/gi, weight: 0.8 },
            { pattern: /(?:it should|it needs|it must|应该|必须)\s+(.+?)(?:\.|$|,|，)/gi, weight: 0.8 },
            { pattern: /(?:the (?:system|app|feature|function)\s+(?:should|needs? to|must)|系统|应用|功能)\s+(.+?)(?:\.|$|,|，)/gi, weight: 0.85 },
        ],
    };
    // Fact validation keywords
    validationIndicators = {
        strong: ['definitely', 'certainly', 'absolutely', 'sure', 'confirmed', '确定', '肯定', '绝对'],
        weak: ['maybe', 'perhaps', 'possibly', 'might', 'could', '可能', '也许', '或许'],
        negative: ['not', "don't", "doesn't", "won't", 'never', '不', '没', '无'],
    };
    /**
     * Extract facts from messages
     */
    async extract(messages, method = 'hybrid', existingFacts) {
        const extractions = [];
        // Keyword-based extraction
        if (method === 'keyword' || method === 'hybrid') {
            const keywordResults = this.extractByKeywords(messages);
            extractions.push(...keywordResults);
        }
        // LLM-based extraction
        if (method === 'llm' || method === 'hybrid') {
            const llmResults = await this.extractByLLM(messages, existingFacts);
            extractions.push(...llmResults);
        }
        // Validate and deduplicate
        return this.validateAndDeduplicate(extractions);
    }
    /**
     * Extract facts using keyword patterns
     */
    extractByKeywords(messages) {
        const extractions = [];
        for (const message of messages) {
            // Focus on both user and assistant messages for facts
            for (const [category, patterns] of Object.entries(this.factPatterns)) {
                for (const { pattern, weight } of patterns) {
                    const matches = message.content.matchAll(pattern);
                    for (const match of matches) {
                        const statement = match[1]?.trim() || match[0]?.trim();
                        if (statement && statement.length > 5) {
                            const validation = this.validateFact(statement, message.content);
                            const confidence = Math.min(weight * validation.confidenceMultiplier, 1.0);
                            extractions.push({
                                statement: this.cleanStatement(statement),
                                category: category,
                                confidence,
                                sourceMessageId: message.id
                            });
                        }
                    }
                }
            }
        }
        return extractions;
    }
    /**
     * Extract facts using LLM
     */
    async extractByLLM(messages, existingFacts) {
        // Placeholder for LLM-based fact extraction
        return [];
    }
    /**
     * Validate a fact based on language indicators
     */
    validateFact(statement, context) {
        const lowerContext = context.toLowerCase();
        const lowerStatement = statement.toLowerCase();
        let confidenceMultiplier = 1.0;
        // Check for strong validation indicators
        if (this.validationIndicators.strong.some(w => lowerContext.includes(w) || lowerStatement.includes(w))) {
            confidenceMultiplier = 1.0;
        }
        // Check for weak/uncertain indicators
        if (this.validationIndicators.weak.some(w => lowerContext.includes(w) || lowerStatement.includes(w))) {
            confidenceMultiplier = 0.7;
        }
        // Check for negation (may invalidate)
        const hasNegation = this.validationIndicators.negative.some(w => lowerContext.includes(w));
        // If statement itself is positive but context has negation, reduce confidence
        if (hasNegation && !this.validationIndicators.negative.some(w => lowerStatement.includes(w))) {
            confidenceMultiplier *= 0.8;
        }
        return {
            isValid: confidenceMultiplier > 0.5,
            confidenceMultiplier
        };
    }
    /**
     * Clean and normalize statement
     */
    cleanStatement(statement) {
        return statement
            .replace(/\s+/g, ' ')
            .replace(/^(?:that|which|who)\s+/i, '')
            .trim();
    }
    /**
     * Validate and deduplicate facts
     */
    validateAndDeduplicate(extractions) {
        const unique = [];
        for (const extraction of extractions) {
            // Skip if confidence too low
            if (extraction.confidence < 0.5)
                continue;
            const isDuplicate = unique.some(u => u.category === extraction.category &&
                this.similarity(u.statement, extraction.statement) > 0.8);
            if (!isDuplicate) {
                unique.push(extraction);
            }
        }
        return unique.sort((a, b) => b.confidence - a.confidence);
    }
    /**
     * Calculate string similarity
     */
    similarity(a, b) {
        const setA = new Set(a.toLowerCase().split(/\s+/));
        const setB = new Set(b.toLowerCase().split(/\s+/));
        const intersection = new Set([...setA].filter(x => setB.has(x)));
        const union = new Set([...setA, ...setB]);
        return intersection.size / union.size;
    }
}
// ============================================================================
// Task Extractor - Extract tasks and assess priorities
// ============================================================================
/**
 * Task Extractor class
 * Identifies tasks and assigns priority levels
 */
export class TaskExtractor {
    // Task identification patterns
    taskPatterns = [
        // Direct action items
        { pattern: /(?:TODO|FIXME|XXX|HACK|NOTE):?\s*(.+?)(?:\n|$)/gi, weight: 0.95, priorityModifier: 0 },
        { pattern: /(?:action item|task|todo|待办|任务)[:\s]+(.+?)(?:\.|$|,|，|\n)/gi, weight: 0.9, priorityModifier: 0 },
        // Commitment patterns
        { pattern: /(?:I will|I'll|I shall|我会|我将|我打算)\s+(.+?)(?:\.|$|,|，)/gi, weight: 0.85, priorityModifier: 0.1 },
        { pattern: /(?:let me|allow me to|让我|让我来)\s+(.+?)(?:\.|$|,|，)/gi, weight: 0.8, priorityModifier: 0 },
        // Assignment patterns
        { pattern: /(?:you (?:should|need to|must)|you'll|you will|你应该|你需要)\s+(.+?)(?:\.|$|,|，)/gi, weight: 0.8, priorityModifier: 0.1 },
        // Follow-up patterns
        { pattern: /(?:follow up|check back|get back|跟进|回复|回头)/gi, weight: 0.75, priorityModifier: 0.1 },
        // Reminder patterns
        { pattern: /(?:don't forget|remember to|make sure|别忘了|记得|确保)\s+(?:to\s+)?(.+?)(?:\.|$|,|，)/gi, weight: 0.8, priorityModifier: 0.1 },
    ];
    // Priority indicators
    priorityKeywords = {
        critical: [
            'urgent', 'emergency', 'critical', 'ASAP', 'immediately', 'blocking',
            '严重', '紧急', '关键', '阻塞', '立即', '马上', '尽快'
        ],
        high: [
            'important', 'high priority', 'essential', 'crucial', 'needed',
            '重要', '高优先级', '关键', '必须', '必要'
        ],
        medium: [
            'should', 'would be good', 'nice to have', 'consider',
            '应该', '最好', '可以考虑', '建议'
        ],
        low: [
            'maybe', 'if possible', 'when you have time', 'eventually',
            '可能', '如果有时间', '以后', '最终', '随意'
        ],
    };
    // Due date patterns
    datePatterns = [
        {
            pattern: /(?:by|before|due|on)\s+(?:next\s+)?(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|tomorrow|today)/i,
            parser: (match) => this.parseRelativeDay(match[1])
        },
        {
            pattern: /(?:by|before|due|on)\s+(\d{1,2})\s*(?:st|nd|rd|th)?\s*(?:of\s+)?(January|February|March|April|May|June|July|August|September|October|November|December)/i,
            parser: (match) => this.parseDate(match[2], match[1])
        },
        {
            pattern: /(?:in|within)\s+(\d+)\s*(day|days|week|weeks|hour|hours)/i,
            parser: (match) => this.parseDuration(parseInt(match[1]), match[2])
        },
        {
            pattern: /(?:本周|下周|这周五|下周一|明天|后天|今天)内?/,
            parser: (match) => this.parseChineseDate(match[0])
        },
    ];
    /**
     * Extract tasks from messages
     */
    async extract(messages, method = 'hybrid', existingTasks) {
        const extractions = [];
        // Keyword-based extraction
        if (method === 'keyword' || method === 'hybrid') {
            const keywordResults = this.extractByKeywords(messages);
            extractions.push(...keywordResults);
        }
        // LLM-based extraction
        if (method === 'llm' || method === 'hybrid') {
            const llmResults = await this.extractByLLM(messages, existingTasks);
            extractions.push(...llmResults);
        }
        // Deduplicate and sort
        return this.deduplicateAndSort(extractions);
    }
    /**
     * Extract tasks using keyword patterns
     */
    extractByKeywords(messages) {
        const extractions = [];
        for (const message of messages) {
            for (const { pattern, weight, priorityModifier } of this.taskPatterns) {
                const matches = message.content.matchAll(pattern);
                for (const match of matches) {
                    const description = match[1]?.trim() || match[0]?.trim();
                    if (description && description.length > 5) {
                        const priority = this.assessPriority(description, message.content);
                        const dueDate = this.extractDueDate(message.content);
                        // Adjust confidence based on priority modifier
                        const baseConfidence = weight + priorityModifier;
                        const confidence = Math.min(baseConfidence, 1.0);
                        extractions.push({
                            description: this.cleanTaskDescription(description),
                            priority,
                            confidence,
                            sourceMessageId: message.id,
                            dueDate
                        });
                    }
                }
            }
        }
        return extractions;
    }
    /**
     * Extract tasks using LLM
     */
    async extractByLLM(messages, existingTasks) {
        // Placeholder for LLM-based task extraction
        return [];
    }
    /**
     * Assess priority level based on keywords
     */
    assessPriority(description, context) {
        const text = (description + ' ' + context).toLowerCase();
        for (const [priority, keywords] of Object.entries(this.priorityKeywords)) {
            if (keywords.some(kw => text.includes(kw.toLowerCase()))) {
                return priority;
            }
        }
        return 'medium';
    }
    /**
     * Extract due date from text
     */
    extractDueDate(text) {
        for (const { pattern, parser } of this.datePatterns) {
            const match = text.match(pattern);
            if (match) {
                return parser(match);
            }
        }
        return undefined;
    }
    /**
     * Parse relative day references
     */
    parseRelativeDay(day) {
        const now = new Date();
        const days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
        if (day.toLowerCase() === 'today') {
            return now.toISOString().split('T')[0];
        }
        if (day.toLowerCase() === 'tomorrow') {
            now.setDate(now.getDate() + 1);
            return now.toISOString().split('T')[0];
        }
        const targetDay = days.indexOf(day.toLowerCase());
        if (targetDay !== -1) {
            const currentDay = now.getDay();
            let daysUntil = targetDay - currentDay;
            if (daysUntil <= 0)
                daysUntil += 7;
            now.setDate(now.getDate() + daysUntil);
            return now.toISOString().split('T')[0];
        }
        return undefined;
    }
    /**
     * Parse month/day date
     */
    parseDate(month, day) {
        const months = ['january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december'];
        const monthIndex = months.indexOf(month.toLowerCase());
        if (monthIndex === -1)
            return undefined;
        const now = new Date();
        const year = now.getFullYear();
        const date = new Date(year, monthIndex, parseInt(day));
        // If date has passed, assume next year
        if (date < now) {
            date.setFullYear(year + 1);
        }
        return date.toISOString().split('T')[0];
    }
    /**
     * Parse duration expressions
     */
    parseDuration(amount, unit) {
        const now = new Date();
        const normalizedUnit = unit.toLowerCase();
        if (normalizedUnit.includes('hour')) {
            now.setHours(now.getHours() + amount);
        }
        else if (normalizedUnit.includes('day')) {
            now.setDate(now.getDate() + amount);
        }
        else if (normalizedUnit.includes('week')) {
            now.setDate(now.getDate() + amount * 7);
        }
        return now.toISOString().split('T')[0];
    }
    /**
     * Parse Chinese date expressions
     */
    parseChineseDate(text) {
        const now = new Date();
        if (text.includes('今天')) {
            return now.toISOString().split('T')[0];
        }
        if (text.includes('明天')) {
            now.setDate(now.getDate() + 1);
            return now.toISOString().split('T')[0];
        }
        if (text.includes('后天')) {
            now.setDate(now.getDate() + 2);
            return now.toISOString().split('T')[0];
        }
        if (text.includes('本周')) {
            // End of this week (Sunday)
            const daysUntilSunday = 7 - now.getDay();
            now.setDate(now.getDate() + daysUntilSunday);
            return now.toISOString().split('T')[0];
        }
        if (text.includes('下周')) {
            now.setDate(now.getDate() + 7);
            return now.toISOString().split('T')[0];
        }
        return undefined;
    }
    /**
     * Clean task description
     */
    cleanTaskDescription(description) {
        return description
            .replace(/^(?:to|about|for|on)\s+/i, '')
            .replace(/\s+/g, ' ')
            .trim();
    }
    /**
     * Deduplicate and sort tasks
     */
    deduplicateAndSort(extractions) {
        const unique = [];
        for (const extraction of extractions) {
            const isDuplicate = unique.some(u => this.similarity(u.description, extraction.description) > 0.8);
            if (!isDuplicate) {
                unique.push(extraction);
            }
        }
        // Sort by priority (critical > high > medium > low) then confidence
        const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
        return unique.sort((a, b) => {
            const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
            if (priorityDiff !== 0)
                return priorityDiff;
            return b.confidence - a.confidence;
        });
    }
    /**
     * Calculate string similarity
     */
    similarity(a, b) {
        const setA = new Set(a.toLowerCase().split(/\s+/));
        const setB = new Set(b.toLowerCase().split(/\s+/));
        const intersection = new Set([...setA].filter(x => setB.has(x)));
        const union = new Set([...setA, ...setB]);
        return intersection.size / union.size;
    }
}
// ============================================================================
// Utility Functions
// ============================================================================
/**
 * Generate unique ID
 */
function generateId(prefix) {
    return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}
/**
 * Convenience function to analyze conversation
 */
export async function analyzeConversation(messages, options = {}) {
    const analyzer = new ContextAnalyzer(options);
    return analyzer.analyze(messages);
}
/**
 * Convenience function for quick keyword-based analysis
 */
export async function analyzeQuick(messages) {
    const analyzer = new ContextAnalyzer({ method: 'keyword' });
    return analyzer.analyzeQuick(messages);
}
/**
 * Extract intents only
 */
export async function extractIntents(messages, method = 'hybrid') {
    const extractor = new IntentExtractor();
    const extractions = await extractor.extract(messages, method);
    return extractions.map(e => ({
        id: generateId('intent'),
        description: e.description,
        confidence: e.confidence,
        sourceMessageId: e.sourceMessageId,
        fulfilled: false,
        createdAt: new Date().toISOString()
    }));
}
/**
 * Extract facts only
 */
export async function extractFacts(messages, method = 'hybrid') {
    const extractor = new FactExtractor();
    const extractions = await extractor.extract(messages, method);
    return extractions.map(e => ({
        id: generateId('fact'),
        statement: e.statement,
        category: e.category,
        sourceMessageId: e.sourceMessageId,
        confidence: e.confidence,
        active: true,
        createdAt: new Date().toISOString()
    }));
}
/**
 * Extract tasks only
 */
export async function extractTasks(messages, method = 'hybrid') {
    const extractor = new TaskExtractor();
    const extractions = await extractor.extract(messages, method);
    const now = new Date().toISOString();
    return extractions.map(e => ({
        id: generateId('task'),
        description: e.description,
        status: 'pending',
        priority: e.priority,
        relatedIntentIds: [],
        dependencies: [],
        dueDate: e.dueDate,
        createdAt: now,
        updatedAt: now
    }));
}
//# sourceMappingURL=analyzer.js.map