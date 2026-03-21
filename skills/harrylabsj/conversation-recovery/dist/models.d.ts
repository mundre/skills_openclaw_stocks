/**
 * Core data models for conversation-recovery skill
 * Defines the structure for sessions, snapshots, intents, facts, and tasks
 */
/**
 * Represents a conversation session
 */
export interface Session {
    /** Unique session identifier */
    id: string;
    /** Session creation timestamp (ISO 8601) */
    createdAt: string;
    /** Last update timestamp */
    updatedAt: string;
    /** Session title/summary */
    title?: string;
    /** Associated channel/platform */
    channel?: string;
    /** Current status: active, paused, recovered, archived */
    status: SessionStatus;
    /** Array of snapshot references */
    snapshots: string[];
}
export type SessionStatus = 'active' | 'paused' | 'recovered' | 'archived';
/**
 * Represents a point-in-time snapshot of conversation state
 */
export interface Snapshot {
    /** Unique snapshot identifier */
    id: string;
    /** Associated session ID */
    sessionId: string;
    /** Snapshot creation timestamp */
    createdAt: string;
    /** Human-readable description */
    description?: string;
    /** User's intents at this point */
    intents: Intent[];
    /** Facts established in conversation */
    facts: Fact[];
    /** Tasks identified or in progress */
    tasks: Task[];
    /** Raw conversation context (truncated/summary) */
    context?: string;
    /** Token count estimate */
    tokenCount?: number;
}
/**
 * Represents user intent extracted from conversation
 */
export interface Intent {
    /** Unique intent identifier */
    id: string;
    /** Intent description */
    description: string;
    /** Intent confidence score (0-1) */
    confidence: number;
    /** Source message reference */
    sourceMessageId?: string;
    /** Whether this intent is fulfilled */
    fulfilled: boolean;
    /** Timestamp when intent was identified */
    createdAt: string;
}
/**
 * Represents a fact established in conversation
 */
export interface Fact {
    /** Unique fact identifier */
    id: string;
    /** Fact statement */
    statement: string;
    /** Fact category: preference, constraint, context, decision */
    category: FactCategory;
    /** Source message reference */
    sourceMessageId?: string;
    /** Confidence level (0-1) */
    confidence: number;
    /** Whether this fact is still valid */
    active: boolean;
    /** Timestamp when fact was established */
    createdAt: string;
}
export type FactCategory = 'preference' | 'constraint' | 'context' | 'decision' | 'requirement';
/**
 * Represents a task identified or in progress
 */
export interface Task {
    /** Unique task identifier */
    id: string;
    /** Task description */
    description: string;
    /** Task status */
    status: TaskStatus;
    /** Priority level */
    priority: TaskPriority;
    /** Associated intent IDs */
    relatedIntentIds: string[];
    /** Dependencies (task IDs that must complete first) */
    dependencies: string[];
    /** Estimated completion timestamp */
    dueDate?: string;
    /** Timestamp when task was created */
    createdAt: string;
    /** Timestamp when task was completed or updated */
    updatedAt: string;
}
export type TaskStatus = 'pending' | 'in_progress' | 'blocked' | 'completed' | 'cancelled';
export type TaskPriority = 'low' | 'medium' | 'high' | 'critical';
/**
 * Recovery summary for displaying to user
 */
export interface RecoverySummary {
    /** Session being recovered */
    sessionId: string;
    /** Snapshot used for recovery */
    snapshotId: string;
    /** Key intents to address */
    keyIntents: Intent[];
    /** Important facts to remember */
    keyFacts: Fact[];
    /** Outstanding tasks */
    outstandingTasks: Task[];
    /** Suggested next actions */
    suggestions: string[];
}
//# sourceMappingURL=models.d.ts.map