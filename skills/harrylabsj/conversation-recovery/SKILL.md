---
name: conversation-recovery
description: Capture and recover conversation state across OpenClaw sessions. Use when conversations get interrupted, span multiple sessions, or need context restoration. Helps save progress, restore context, and manage long-running tasks.
---

# conversation-recovery

Capture and recover conversation state across OpenClaw sessions.

## Description

This skill provides conversation state management and recovery capabilities for OpenClaw. When conversations get interrupted or span multiple sessions, it captures the essential context (intents, facts, tasks) and allows seamless recovery.

## Use Cases

- **Long-running tasks**: Save progress when a conversation spans multiple days
- **Context restoration**: Recover where you left off after interruptions
- **Session handoff**: Transfer context between different channels/platforms
- **Memory management**: Archive old sessions while preserving key information

## Installation

```bash
# Dependencies are managed via package.json
npm install

# Build TypeScript
npm run build
```

## Core Concepts

### Session
A conversation container with metadata (status, channel, timestamps).

### Snapshot
A point-in-time capture of conversation state containing:
- **Intents**: What the user wants to accomplish
- **Facts**: Established information and preferences
- **Tasks**: Action items and their status

### Recovery
Restoring context from a snapshot to continue a conversation seamlessly.

## API Usage

### Starting a Session

```typescript
import { startSession } from 'conversation-recovery';

const session = await startSession(
  'Project Planning Discussion',
  'discord'
);
```

### Capturing a Snapshot

```typescript
import { captureSnapshot } from 'conversation-recovery';

const snapshot = await captureSnapshot(session.id, {
  description: 'User wants to plan Q3 roadmap',
  intents: [{
    id: 'intent_1',
    description: 'Create Q3 product roadmap',
    confidence: 0.95,
    fulfilled: false,
    createdAt: new Date().toISOString()
  }],
  facts: [{
    id: 'fact_1',
    statement: 'Team has 5 engineers available',
    category: 'constraint',
    confidence: 1.0,
    active: true,
    createdAt: new Date().toISOString()
  }],
  tasks: [{
    id: 'task_1',
    description: 'Gather requirements from stakeholders',
    status: 'pending',
    priority: 'high',
    relatedIntentIds: ['intent_1'],
    dependencies: [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }]
});
```

### Recovering a Session

```typescript
import { recoverSession } from 'conversation-recovery';

const recovery = await recoverSession(session.id);
// Returns RecoverySummary with key intents, facts, tasks, and suggestions
```

### Managing Sessions

```typescript
import { 
  pauseSession, 
  resumeSession, 
  archiveSession,
  getActiveSessions,
  deleteSession 
} from 'conversation-recovery';

await pauseSession(session.id);      // Mark as paused
await resumeSession(session.id);     // Mark as active
await archiveSession(session.id);    // Mark as archived
await deleteSession(session.id);     // Permanently delete

const active = await getActiveSessions();
```

### Storage Operations

```typescript
import { 
  getSession,
  getSnapshot,
  getSessionSnapshots,
  getLatestSnapshot,
  deleteSnapshot,
  listSessions,
  getStorageStats,
  cleanupSnapshots
} from 'conversation-recovery';

const session = await getSession(sessionId);
const snapshot = await getSnapshot(snapshotId);
const snapshots = await getSessionSnapshots(sessionId);
const latest = await getLatestSnapshot(sessionId);

const allSessions = await listSessions();
const stats = await getStorageStats();

// Keep only last 10 snapshots
await cleanupSnapshots(sessionId, 10);
```

## Data Models

### Session
```typescript
interface Session {
  id: string;
  createdAt: string;
  updatedAt: string;
  title?: string;
  channel?: string;
  status: 'active' | 'paused' | 'recovered' | 'archived';
  snapshots: string[];
}
```

### Snapshot
```typescript
interface Snapshot {
  id: string;
  sessionId: string;
  createdAt: string;
  description?: string;
  intents: Intent[];
  facts: Fact[];
  tasks: Task[];
  context?: string;
  tokenCount?: number;
}
```

### Intent
```typescript
interface Intent {
  id: string;
  description: string;
  confidence: number;
  sourceMessageId?: string;
  fulfilled: boolean;
  createdAt: string;
}
```

### Fact
```typescript
interface Fact {
  id: string;
  statement: string;
  category: 'preference' | 'constraint' | 'context' | 'decision' | 'requirement';
  sourceMessageId?: string;
  confidence: number;
  active: boolean;
  createdAt: string;
}
```

### Task
```typescript
interface Task {
  id: string;
  description: string;
  status: 'pending' | 'in_progress' | 'blocked' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'critical';
  relatedIntentIds: string[];
  dependencies: string[];
  dueDate?: string;
  createdAt: string;
  updatedAt: string;
}
```

## Storage

Data is stored in JSON files at:
- Sessions: `~/.openclaw/conversation-recovery/sessions/`
- Snapshots: `~/.openclaw/conversation-recovery/snapshots/`

Override with environment variable:
```bash
export CONVERSATION_RECOVERY_STORAGE=/custom/path
```

## Roadmap

### Phase 1 (Current)
- ✅ Core data models (Session, Snapshot, Intent, Fact, Task)
- ✅ File storage layer (CRUD operations)
- ✅ Basic session lifecycle management
- ✅ Recovery summary generation

### Phase 2 (Planned)
- Intent extraction from conversation text
- Automatic snapshot triggers (token limits, time intervals)
- Compression and summarization of old snapshots

### Phase 3 (Planned)
- Vector search for similar past sessions
- Cross-session knowledge graph
- Integration with OpenClaw memory system

## License

MIT
