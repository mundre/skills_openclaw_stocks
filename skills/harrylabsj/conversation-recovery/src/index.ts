/**
 * Conversation Recovery Skill - Main Entry Point
 * 
 * Provides conversation state management and recovery capabilities
 * for OpenClaw sessions that get interrupted or need context restoration.
 */

export * from './models.js';
export * from './storage.js';
export * from './analyzer.js';

import { 
  createSession, 
  getSession, 
  updateSession, 
  deleteSession, 
  listSessions,
  createSnapshot,
  getSnapshot,
  getSessionSnapshots,
  deleteSnapshot,
  getLatestSnapshot,
  getStorageStats,
  initStorage
} from './storage.js';

import type { 
  Session, 
  Snapshot, 
  Intent, 
  Fact, 
  Task,
  RecoverySummary 
} from './models.js';

/**
 * Generate a unique ID
 */
function generateId(prefix: string): string {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Create a new session
 */
export async function startSession(
  title?: string, 
  channel?: string
): Promise<Session> {
  await initStorage();
  
  const session: Session = {
    id: generateId('session'),
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    title,
    channel,
    status: 'active',
    snapshots: []
  };
  
  await createSession(session);
  return session;
}

/**
 * Create a snapshot of current conversation state
 */
export async function captureSnapshot(
  sessionId: string,
  options: {
    description?: string;
    intents?: Intent[];
    facts?: Fact[];
    tasks?: Task[];
    context?: string;
    tokenCount?: number;
  } = {}
): Promise<Snapshot> {
  const session = await getSession(sessionId);
  if (!session) {
    throw new Error(`Session not found: ${sessionId}`);
  }
  
  const snapshot: Snapshot = {
    id: generateId('snapshot'),
    sessionId,
    createdAt: new Date().toISOString(),
    description: options.description,
    intents: options.intents || [],
    facts: options.facts || [],
    tasks: options.tasks || [],
    context: options.context,
    tokenCount: options.tokenCount
  };
  
  await createSnapshot(snapshot);
  return snapshot;
}

/**
 * Recover a session from a snapshot
 */
export async function recoverSession(
  sessionId: string,
  snapshotId?: string
): Promise<RecoverySummary> {
  const session = await getSession(sessionId);
  if (!session) {
    throw new Error(`Session not found: ${sessionId}`);
  }
  
  let snapshot: Snapshot | null;
  
  if (snapshotId) {
    snapshot = await getSnapshot(snapshotId);
    if (!snapshot) {
      throw new Error(`Snapshot not found: ${snapshotId}`);
    }
  } else {
    snapshot = await getLatestSnapshot(sessionId);
    if (!snapshot) {
      throw new Error(`No snapshots found for session: ${sessionId}`);
    }
  }
  
  // Update session status
  session.status = 'recovered';
  await updateSession(session);
  
  // Build recovery summary
  const outstandingTasks = snapshot.tasks.filter(t => 
    t.status === 'pending' || t.status === 'in_progress' || t.status === 'blocked'
  );
  
  const keyIntents = snapshot.intents.filter(i => !i.fulfilled);
  const keyFacts = snapshot.facts.filter(f => f.active);
  
  // Generate suggestions based on state
  const suggestions: string[] = [];
  
  if (keyIntents.length > 0) {
    suggestions.push(`Address ${keyIntents.length} outstanding intent(s)`);
  }
  
  if (outstandingTasks.length > 0) {
    const criticalTasks = outstandingTasks.filter(t => t.priority === 'critical');
    if (criticalTasks.length > 0) {
      suggestions.push(`Prioritize ${criticalTasks.length} critical task(s)`);
    }
    suggestions.push(`Review ${outstandingTasks.length} outstanding task(s)`);
  }
  
  if (keyFacts.length > 0) {
    suggestions.push(`Consider ${keyFacts.length} active fact(s) in context`);
  }
  
  return {
    sessionId,
    snapshotId: snapshot.id,
    keyIntents,
    keyFacts,
    outstandingTasks,
    suggestions
  };
}

/**
 * Pause a session (mark as inactive)
 */
export async function pauseSession(sessionId: string): Promise<void> {
  const session = await getSession(sessionId);
  if (!session) {
    throw new Error(`Session not found: ${sessionId}`);
  }
  
  session.status = 'paused';
  await updateSession(session);
}

/**
 * Resume a paused session
 */
export async function resumeSession(sessionId: string): Promise<void> {
  const session = await getSession(sessionId);
  if (!session) {
    throw new Error(`Session not found: ${sessionId}`);
  }
  
  session.status = 'active';
  await updateSession(session);
}

/**
 * Archive a session
 */
export async function archiveSession(sessionId: string): Promise<void> {
  const session = await getSession(sessionId);
  if (!session) {
    throw new Error(`Session not found: ${sessionId}`);
  }
  
  session.status = 'archived';
  await updateSession(session);
}

/**
 * Get all active sessions
 */
export async function getActiveSessions(): Promise<Session[]> {
  const sessions = await listSessions();
  return sessions.filter(s => s.status === 'active');
}

/**
 * Clean up old snapshots (keep only last N per session)
 */
export async function cleanupSnapshots(
  sessionId: string, 
  keepCount: number = 10
): Promise<number> {
  const snapshots = await getSessionSnapshots(sessionId);
  
  if (snapshots.length <= keepCount) {
    return 0;
  }
  
  const toDelete = snapshots.slice(keepCount);
  let deleted = 0;
  
  for (const snapshot of toDelete) {
    if (await deleteSnapshot(snapshot.id)) {
      deleted++;
    }
  }
  
  return deleted;
}

// Export main API
export default {
  startSession,
  captureSnapshot,
  recoverSession,
  pauseSession,
  resumeSession,
  archiveSession,
  getActiveSessions,
  cleanupSnapshots,
  getSession,
  getSnapshot,
  getSessionSnapshots,
  getLatestSnapshot,
  deleteSession,
  deleteSnapshot,
  listSessions,
  getStorageStats
};
