/**
 * File storage layer for conversation-recovery skill
 * Handles CRUD operations for snapshots and sessions
 */
import * as fs from 'fs/promises';
import * as path from 'path';
const STORAGE_DIR = process.env.CONVERSATION_RECOVERY_STORAGE
    || path.join(process.env.HOME || '~', '.openclaw', 'conversation-recovery');
const SESSIONS_DIR = path.join(STORAGE_DIR, 'sessions');
const SNAPSHOTS_DIR = path.join(STORAGE_DIR, 'snapshots');
/**
 * Initialize storage directories
 */
export async function initStorage() {
    await fs.mkdir(SESSIONS_DIR, { recursive: true });
    await fs.mkdir(SNAPSHOTS_DIR, { recursive: true });
}
/**
 * Get path to session file
 */
function getSessionPath(sessionId) {
    return path.join(SESSIONS_DIR, `${sessionId}.json`);
}
/**
 * Get path to snapshot file
 */
function getSnapshotPath(snapshotId) {
    return path.join(SNAPSHOTS_DIR, `${snapshotId}.json`);
}
/**
 * Create a new session
 */
export async function createSession(session) {
    await initStorage();
    const filePath = getSessionPath(session.id);
    await fs.writeFile(filePath, JSON.stringify(session, null, 2), 'utf-8');
}
/**
 * Get a session by ID
 */
export async function getSession(sessionId) {
    try {
        const filePath = getSessionPath(sessionId);
        const data = await fs.readFile(filePath, 'utf-8');
        return JSON.parse(data);
    }
    catch (error) {
        if (error.code === 'ENOENT') {
            return null;
        }
        throw error;
    }
}
/**
 * Update an existing session
 */
export async function updateSession(session) {
    const filePath = getSessionPath(session.id);
    session.updatedAt = new Date().toISOString();
    await fs.writeFile(filePath, JSON.stringify(session, null, 2), 'utf-8');
}
/**
 * Delete a session and all its snapshots
 */
export async function deleteSession(sessionId) {
    try {
        const session = await getSession(sessionId);
        if (!session)
            return false;
        // Delete all associated snapshots
        for (const snapshotId of session.snapshots) {
            await deleteSnapshot(snapshotId);
        }
        // Delete session file
        const filePath = getSessionPath(sessionId);
        await fs.unlink(filePath);
        return true;
    }
    catch (error) {
        if (error.code === 'ENOENT') {
            return false;
        }
        throw error;
    }
}
/**
 * List all sessions
 */
export async function listSessions() {
    await initStorage();
    try {
        const files = await fs.readdir(SESSIONS_DIR);
        const sessions = [];
        for (const file of files) {
            if (file.endsWith('.json')) {
                const sessionId = file.slice(0, -5);
                const session = await getSession(sessionId);
                if (session)
                    sessions.push(session);
            }
        }
        return sessions.sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime());
    }
    catch {
        return [];
    }
}
/**
 * Create a new snapshot
 */
export async function createSnapshot(snapshot) {
    await initStorage();
    const filePath = getSnapshotPath(snapshot.id);
    await fs.writeFile(filePath, JSON.stringify(snapshot, null, 2), 'utf-8');
    // Update session to include this snapshot
    const session = await getSession(snapshot.sessionId);
    if (session && !session.snapshots.includes(snapshot.id)) {
        session.snapshots.push(snapshot.id);
        session.updatedAt = new Date().toISOString();
        await updateSession(session);
    }
}
/**
 * Get a snapshot by ID
 */
export async function getSnapshot(snapshotId) {
    try {
        const filePath = getSnapshotPath(snapshotId);
        const data = await fs.readFile(filePath, 'utf-8');
        return JSON.parse(data);
    }
    catch (error) {
        if (error.code === 'ENOENT') {
            return null;
        }
        throw error;
    }
}
/**
 * Get all snapshots for a session
 */
export async function getSessionSnapshots(sessionId) {
    const session = await getSession(sessionId);
    if (!session)
        return [];
    const snapshots = [];
    for (const snapshotId of session.snapshots) {
        const snapshot = await getSnapshot(snapshotId);
        if (snapshot)
            snapshots.push(snapshot);
    }
    return snapshots.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
}
/**
 * Delete a snapshot
 */
export async function deleteSnapshot(snapshotId) {
    try {
        const snapshot = await getSnapshot(snapshotId);
        if (!snapshot)
            return false;
        // Remove from session's snapshot list
        const session = await getSession(snapshot.sessionId);
        if (session) {
            session.snapshots = session.snapshots.filter(id => id !== snapshotId);
            await updateSession(session);
        }
        // Delete snapshot file
        const filePath = getSnapshotPath(snapshotId);
        await fs.unlink(filePath);
        return true;
    }
    catch (error) {
        if (error.code === 'ENOENT') {
            return false;
        }
        throw error;
    }
}
/**
 * Get the latest snapshot for a session
 */
export async function getLatestSnapshot(sessionId) {
    const snapshots = await getSessionSnapshots(sessionId);
    return snapshots[0] || null;
}
/**
 * Get storage statistics
 */
export async function getStorageStats() {
    const sessions = await listSessions();
    let totalSnapshots = 0;
    for (const session of sessions) {
        totalSnapshots += session.snapshots.length;
    }
    return {
        totalSessions: sessions.length,
        totalSnapshots,
        storagePath: STORAGE_DIR
    };
}
//# sourceMappingURL=storage.js.map