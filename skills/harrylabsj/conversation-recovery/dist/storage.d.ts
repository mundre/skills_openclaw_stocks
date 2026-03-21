/**
 * File storage layer for conversation-recovery skill
 * Handles CRUD operations for snapshots and sessions
 */
import type { Session, Snapshot } from './models.js';
/**
 * Initialize storage directories
 */
export declare function initStorage(): Promise<void>;
/**
 * Create a new session
 */
export declare function createSession(session: Session): Promise<void>;
/**
 * Get a session by ID
 */
export declare function getSession(sessionId: string): Promise<Session | null>;
/**
 * Update an existing session
 */
export declare function updateSession(session: Session): Promise<void>;
/**
 * Delete a session and all its snapshots
 */
export declare function deleteSession(sessionId: string): Promise<boolean>;
/**
 * List all sessions
 */
export declare function listSessions(): Promise<Session[]>;
/**
 * Create a new snapshot
 */
export declare function createSnapshot(snapshot: Snapshot): Promise<void>;
/**
 * Get a snapshot by ID
 */
export declare function getSnapshot(snapshotId: string): Promise<Snapshot | null>;
/**
 * Get all snapshots for a session
 */
export declare function getSessionSnapshots(sessionId: string): Promise<Snapshot[]>;
/**
 * Delete a snapshot
 */
export declare function deleteSnapshot(snapshotId: string): Promise<boolean>;
/**
 * Get the latest snapshot for a session
 */
export declare function getLatestSnapshot(sessionId: string): Promise<Snapshot | null>;
/**
 * Get storage statistics
 */
export declare function getStorageStats(): Promise<{
    totalSessions: number;
    totalSnapshots: number;
    storagePath: string;
}>;
//# sourceMappingURL=storage.d.ts.map