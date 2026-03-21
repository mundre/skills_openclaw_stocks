/**
 * Conversation Recovery Skill - Phase 2: Intelligent Analysis
 *
 * Provides:
 * 1. Context Analyzer - Extracts intents, facts, and tasks from conversation
 * 2. Intent Extraction Algorithm - Keyword-based + LLM-based extraction
 * 3. Fact Extraction and Validation - Identifies and validates facts
 * 4. Task Recognition and Priority Assessment - Identifies tasks and assigns priorities
 */
import type { Intent, Fact, Task, FactCategory, TaskPriority } from './models.js';
/**
 * Analysis result containing extracted intents, facts, and tasks
 */
export interface AnalysisResult {
    /** Extracted intents from the conversation */
    intents: Intent[];
    /** Extracted facts from the conversation */
    facts: Fact[];
    /** Extracted tasks from the conversation */
    tasks: Task[];
    /** Analysis metadata */
    metadata: {
        /** Timestamp of analysis */
        analyzedAt: string;
        /** Method used for extraction (keyword, llm, hybrid) */
        method: 'keyword' | 'llm' | 'hybrid';
        /** Confidence score for the overall analysis (0-1) */
        confidence: number;
        /** Token count of input text */
        tokenCount?: number;
    };
}
/**
 * Message in a conversation
 */
export interface ConversationMessage {
    /** Message ID */
    id: string;
    /** Message role: user or assistant */
    role: 'user' | 'assistant';
    /** Message content */
    content: string;
    /** Timestamp */
    timestamp: string;
}
/**
 * Options for context analysis
 */
export interface AnalysisOptions {
    /** Analysis method preference */
    method?: 'keyword' | 'llm' | 'hybrid';
    /** Minimum confidence threshold for extraction (0-1) */
    confidenceThreshold?: number;
    /** Whether to use LLM for refinement */
    useLLM?: boolean;
    /** Existing context from previous snapshots */
    existingIntents?: Intent[];
    /** Existing facts from previous snapshots */
    existingFacts?: Fact[];
    /** Existing tasks from previous snapshots */
    existingTasks?: Task[];
}
/**
 * Intent extraction result
 */
interface IntentExtraction {
    description: string;
    confidence: number;
    sourceMessageId: string;
}
/**
 * Fact extraction result
 */
interface FactExtraction {
    statement: string;
    category: FactCategory;
    confidence: number;
    sourceMessageId: string;
}
/**
 * Task extraction result
 */
interface TaskExtraction {
    description: string;
    priority: TaskPriority;
    confidence: number;
    sourceMessageId: string;
    dueDate?: string;
}
/**
 * Context Analyzer class
 * Orchestrates the extraction of intents, facts, and tasks from conversation
 */
export declare class ContextAnalyzer {
    private options;
    private intentExtractor;
    private factExtractor;
    private taskExtractor;
    constructor(options?: AnalysisOptions);
    /**
     * Analyze conversation messages and extract intents, facts, and tasks
     */
    analyze(messages: ConversationMessage[]): Promise<AnalysisResult>;
    /**
     * Quick analysis using keyword-based extraction only
     */
    analyzeQuick(messages: ConversationMessage[]): Promise<AnalysisResult>;
    /**
     * Estimate token count from messages
     */
    private estimateTokenCount;
    /**
     * Convert intent extractions to Intent model
     */
    private convertToIntents;
    /**
     * Convert fact extractions to Fact model
     */
    private convertToFacts;
    /**
     * Convert task extractions to Task model
     */
    private convertToTasks;
    /**
     * Merge new intents with existing ones, avoiding duplicates
     */
    private mergeIntents;
    /**
     * Merge new facts with existing ones, avoiding duplicates
     */
    private mergeFacts;
    /**
     * Merge new tasks with existing ones, avoiding duplicates
     */
    private mergeTasks;
    /**
     * Calculate overall confidence score
     */
    private calculateOverallConfidence;
    /**
     * Calculate simple string similarity (Jaccard index)
     */
    private similarity;
    /**
     * Generate unique ID
     */
    private generateId;
}
/**
 * Intent Extractor class
 * Uses keyword-based and LLM-based methods to extract user intents
 */
export declare class IntentExtractor {
    private intentPatterns;
    /**
     * Extract intents from messages
     */
    extract(messages: ConversationMessage[], method?: 'keyword' | 'llm' | 'hybrid', existingIntents?: Intent[]): Promise<IntentExtraction[]>;
    /**
     * Extract intents using keyword patterns
     */
    private extractByKeywords;
    /**
     * Extract intents using LLM (simulated implementation)
     * In production, this would call an actual LLM API
     */
    private extractByLLM;
    /**
     * Clean and normalize intent description
     */
    private cleanIntentDescription;
    /**
     * Deduplicate intents by similarity
     */
    private deduplicateIntents;
    /**
     * Calculate string similarity
     */
    private similarity;
}
/**
 * Fact Extractor class
 * Identifies and validates facts established in conversation
 */
export declare class FactExtractor {
    private factPatterns;
    private validationIndicators;
    /**
     * Extract facts from messages
     */
    extract(messages: ConversationMessage[], method?: 'keyword' | 'llm' | 'hybrid', existingFacts?: Fact[]): Promise<FactExtraction[]>;
    /**
     * Extract facts using keyword patterns
     */
    private extractByKeywords;
    /**
     * Extract facts using LLM
     */
    private extractByLLM;
    /**
     * Validate a fact based on language indicators
     */
    private validateFact;
    /**
     * Clean and normalize statement
     */
    private cleanStatement;
    /**
     * Validate and deduplicate facts
     */
    private validateAndDeduplicate;
    /**
     * Calculate string similarity
     */
    private similarity;
}
/**
 * Task Extractor class
 * Identifies tasks and assigns priority levels
 */
export declare class TaskExtractor {
    private taskPatterns;
    private priorityKeywords;
    private datePatterns;
    /**
     * Extract tasks from messages
     */
    extract(messages: ConversationMessage[], method?: 'keyword' | 'llm' | 'hybrid', existingTasks?: Task[]): Promise<TaskExtraction[]>;
    /**
     * Extract tasks using keyword patterns
     */
    private extractByKeywords;
    /**
     * Extract tasks using LLM
     */
    private extractByLLM;
    /**
     * Assess priority level based on keywords
     */
    private assessPriority;
    /**
     * Extract due date from text
     */
    private extractDueDate;
    /**
     * Parse relative day references
     */
    private parseRelativeDay;
    /**
     * Parse month/day date
     */
    private parseDate;
    /**
     * Parse duration expressions
     */
    private parseDuration;
    /**
     * Parse Chinese date expressions
     */
    private parseChineseDate;
    /**
     * Clean task description
     */
    private cleanTaskDescription;
    /**
     * Deduplicate and sort tasks
     */
    private deduplicateAndSort;
    /**
     * Calculate string similarity
     */
    private similarity;
}
/**
 * Convenience function to analyze conversation
 */
export declare function analyzeConversation(messages: ConversationMessage[], options?: AnalysisOptions): Promise<AnalysisResult>;
/**
 * Convenience function for quick keyword-based analysis
 */
export declare function analyzeQuick(messages: ConversationMessage[]): Promise<AnalysisResult>;
/**
 * Extract intents only
 */
export declare function extractIntents(messages: ConversationMessage[], method?: 'keyword' | 'llm' | 'hybrid'): Promise<Intent[]>;
/**
 * Extract facts only
 */
export declare function extractFacts(messages: ConversationMessage[], method?: 'keyword' | 'llm' | 'hybrid'): Promise<Fact[]>;
/**
 * Extract tasks only
 */
export declare function extractTasks(messages: ConversationMessage[], method?: 'keyword' | 'llm' | 'hybrid'): Promise<Task[]>;
export {};
//# sourceMappingURL=analyzer.d.ts.map