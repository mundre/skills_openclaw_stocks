/**
 * Conversation Recovery Skill - Phase 3: Advanced Recovery
 *
 * Provides:
 * 1. Context Compression Algorithm - Retain key information, remove redundancy
 * 2. Intent Similarity Calculation - Jaccard + Semantic similarity
 * 3. Recovery Decision Algorithm - Select best snapshot for recovery
 * 4. External Change Detection - Compare current state with snapshot
 */
import type { Snapshot, Intent, Fact, Task } from './models.js';
/**
 * Compression result containing compressed snapshot and metadata
 */
export interface CompressionResult {
    /** Compressed snapshot */
    snapshot: Snapshot;
    /** Compression metadata */
    metadata: {
        /** Original token count */
        originalTokens: number;
        /** Compressed token count */
        compressedTokens: number;
        /** Compression ratio */
        compressionRatio: number;
        /** Items removed by category */
        removedItems: {
            intents: number;
            facts: number;
            tasks: number;
        };
        /** Items retained by category */
        retainedItems: {
            intents: number;
            facts: number;
            tasks: number;
        };
    };
}
/**
 * Similarity score between two intents
 */
export interface IntentSimilarity {
    /** Jaccard similarity score (0-1) */
    jaccardScore: number;
    /** Semantic similarity score (0-1) */
    semanticScore: number;
    /** Combined similarity score (0-1) */
    combinedScore: number;
    /** Weight used for combining scores */
    weights: {
        jaccard: number;
        semantic: number;
    };
}
/**
 * Recovery decision result
 */
export interface RecoveryDecision {
    /** Selected snapshot for recovery */
    selectedSnapshot: Snapshot;
    /** Decision confidence score (0-1) */
    confidence: number;
    /** Reasoning for the decision */
    reasoning: string;
    /** Alternative snapshots considered */
    alternatives: Array<{
        snapshot: Snapshot;
        score: number;
        reason: string;
    }>;
    /** Recommended recovery strategy */
    strategy: RecoveryStrategy;
}
/**
 * Recovery strategy types
 */
export type RecoveryStrategy = 'full_restore' | 'partial_restore' | 'merge_current' | 'summarize_only' | 'confirm_first';
/**
 * External change detection result
 */
export interface ChangeDetectionResult {
    /** Whether changes were detected */
    hasChanges: boolean;
    /** Change severity level */
    severity: 'none' | 'minor' | 'moderate' | 'major';
    /** Detected changes by category */
    changes: {
        /** Intent changes */
        intents: IntentChange[];
        /** Fact changes */
        facts: FactChange[];
        /** Task changes */
        tasks: TaskChange[];
    };
    /** Summary of changes */
    summary: string;
    /** Recommendations based on changes */
    recommendations: string[];
}
/**
 * Intent change record
 */
export interface IntentChange {
    type: 'added' | 'removed' | 'modified' | 'fulfilled';
    intent: Intent;
    previousIntent?: Intent;
    similarityScore?: number;
}
/**
 * Fact change record
 */
export interface FactChange {
    type: 'added' | 'removed' | 'modified' | 'deactivated';
    fact: Fact;
    previousFact?: Fact;
    similarityScore?: number;
}
/**
 * Task change record
 */
export interface TaskChange {
    type: 'added' | 'removed' | 'modified' | 'completed' | 'status_changed';
    task: Task;
    previousTask?: Task;
    similarityScore?: number;
}
/**
 * Options for context compression
 */
export interface CompressionOptions {
    /** Target token count (approximate) */
    targetTokens?: number;
    /** Maximum age of items to retain (in days) */
    maxAgeDays?: number;
    /** Minimum confidence threshold for retention */
    minConfidence?: number;
    /** Whether to compress fulfilled intents */
    compressFulfilledIntents?: boolean;
    /** Whether to compress completed tasks */
    compressCompletedTasks?: boolean;
    /** Whether to compress inactive facts */
    compressInactiveFacts?: boolean;
    /** Priority weights for retention decisions */
    priorityWeights?: {
        critical: number;
        high: number;
        medium: number;
        low: number;
    };
}
/**
 * Options for similarity calculation
 */
export interface SimilarityOptions {
    /** Weight for Jaccard similarity (0-1) */
    jaccardWeight?: number;
    /** Weight for semantic similarity (0-1) */
    semanticWeight?: number;
    /** Minimum similarity threshold */
    threshold?: number;
    /** Whether to use keyword expansion for semantic similarity */
    useKeywordExpansion?: boolean;
}
/**
 * Options for recovery decision
 */
export interface RecoveryDecisionOptions {
    /** Preferred recovery strategy */
    preferredStrategy?: RecoveryStrategy;
    /** Minimum confidence threshold for auto-recovery */
    minConfidenceThreshold?: number;
    /** Time window for relevant snapshots (in hours) */
    timeWindowHours?: number;
    /** Whether to consider session status in decision */
    considerSessionStatus?: boolean;
    /** Custom scoring weights */
    scoringWeights?: {
        recency: number;
        completeness: number;
        relevance: number;
        freshness: number;
    };
}
/**
 * Options for change detection
 */
export interface ChangeDetectionOptions {
    /** Similarity threshold for matching items */
    similarityThreshold?: number;
    /** Whether to detect fulfilled intents as changes */
    trackIntentFulfillment?: boolean;
    /** Whether to detect completed tasks as changes */
    trackTaskCompletion?: boolean;
    /** Whether to detect fact deactivation */
    trackFactDeactivation?: boolean;
}
/**
 * Context Compressor class
 * Compresses snapshots by removing redundant and low-priority information
 */
export declare class ContextCompressor {
    private options;
    constructor(options?: CompressionOptions);
    /**
     * Compress a snapshot to reduce token count while preserving key information
     */
    compress(snapshot: Snapshot): CompressionResult;
    /**
     * Compress intents - remove fulfilled and low-confidence intents
     */
    private compressIntents;
    /**
     * Compress facts - remove inactive and low-confidence facts
     */
    private compressFacts;
    /**
     * Compress tasks - remove completed and low-priority tasks
     */
    private compressTasks;
    /**
     * Estimate token count for a snapshot
     * Rough estimate: 1 token ≈ 4 characters for English, 2 for Chinese
     */
    private estimateTokens;
}
/**
 * Similarity Calculator class
 * Calculates similarity between intents using Jaccard and semantic methods
 */
export declare class SimilarityCalculator {
    private options;
    private keywordExpansions;
    constructor(options?: SimilarityOptions);
    /**
     * Calculate similarity between two intents
     */
    calculateIntentSimilarity(intentA: Intent, intentB: Intent): IntentSimilarity;
}
//# sourceMappingURL=recovery.d.ts.map