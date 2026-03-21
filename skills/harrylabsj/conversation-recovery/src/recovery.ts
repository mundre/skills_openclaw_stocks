/**
 * Conversation Recovery Skill - Phase 3: Advanced Recovery
 *
 * Provides:
 * 1. Context Compression Algorithm - Retain key information, remove redundancy
 * 2. Intent Similarity Calculation - Jaccard + Semantic similarity
 * 3. Recovery Decision Algorithm - Select best snapshot for recovery
 * 4. External Change Detection - Compare current state with snapshot
 */

import type { Session, Snapshot, Intent, Fact, Task, RecoverySummary } from './models.js';
import { getSession, getSnapshot, getSessionSnapshots, getLatestSnapshot } from './storage.js';

// ============================================================================
// Types for Advanced Recovery
// ============================================================================

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
export type RecoveryStrategy =
  | 'full_restore'      // Restore all context
  | 'partial_restore'   // Restore only key items
  | 'merge_current'     // Merge with current context
  | 'summarize_only'    // Provide summary only
  | 'confirm_first';    // Ask user before restoring

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

// ============================================================================
// Context Compression Algorithm
// ============================================================================

/**
 * Context Compressor class
 * Compresses snapshots by removing redundant and low-priority information
 */
export class ContextCompressor {
  private options: Required<CompressionOptions>;

  constructor(options: CompressionOptions = {}) {
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
  compress(snapshot: Snapshot): CompressionResult {
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
    const compressedSnapshot: Snapshot = {
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
