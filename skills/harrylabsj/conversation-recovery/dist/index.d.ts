/**
 * Conversation Recovery Skill - Main Entry Point
 *
 * Provides conversation state management and recovery capabilities
 * for OpenClaw sessions that get interrupted or need context restoration.
 */
export * from './models.js';
export * from './storage.js';
export * from './analyzer.js';
import { getSession, deleteSession, listSessions, getSnapshot, getSessionSnapshots, deleteSnapshot, getLatestSnapshot, getStorageStats } from './storage.js';
import type { Session, Snapshot, Intent, Fact, Task, RecoverySummary } from './models.js';
/**
 * Create a new session
 */
export declare function startSession(title?: string, channel?: string): Promise<Session>;
/**
 * Create a snapshot of current conversation state
 */
export declare function captureSnapshot(sessionId: string, options?: {
    description?: string;
    intents?: Intent[];
    facts?: Fact[];
    tasks?: Task[];
    context?: string;
    tokenCount?: number;
}): Promise<Snapshot>;
/**
 * Recover a session from a snapshot
 */
export declare function recoverSession(sessionId: string, snapshotId?: string): Promise<RecoverySummary>;
/**
 * Pause a session (mark as inactive)
 */
export declare function pauseSession(sessionId: string): Promise<void>;
/**
 * Resume a paused session
 */
export declare function resumeSession(sessionId: string): Promise<void>;
/**
 * Archive a session
 */
export declare function archiveSession(sessionId: string): Promise<void>;
/**
 * Get all active sessions
 */
export declare function getActiveSessions(): Promise<Session[]>;
/**
 * Clean up old snapshots (keep only last N per session)
 */
export declare function cleanupSnapshots(sessionId: string, keepCount?: number): Promise<number>;
declare const _default: {
    startSession: typeof startSession;
    captureSnapshot: typeof captureSnapshot;
    recoverSession: typeof recoverSession;
    pauseSession: typeof pauseSession;
    resumeSession: typeof resumeSession;
    archiveSession: typeof archiveSession;
    getActiveSessions: typeof getActiveSessions;
    cleanupSnapshots: typeof cleanupSnapshots;
    getSession: typeof getSession;
    getSnapshot: typeof getSnapshot;
    getSessionSnapshots: typeof getSessionSnapshots;
    getLatestSnapshot: typeof getLatestSnapshot;
    deleteSession: typeof deleteSession;
    deleteSnapshot: typeof deleteSnapshot;
    listSessions: typeof listSessions;
    getStorageStats: typeof getStorageStats;
};
export default _default;
//# sourceMappingURL=index.d.ts.map