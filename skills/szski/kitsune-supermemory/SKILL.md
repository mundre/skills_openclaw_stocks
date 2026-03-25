---
name: supermemory
description: Long-term semantic memory via Supermemory API. Use when you need to store memories for later recall, search existing memories, ingest files or workspace context into memory, or retrieve relevant context at session startup. Triggers on requests like "remember this", "what do you know about X", "ingest my memory files", "recall context", "add this to memory", or any task requiring persistent memory across sessions. Agent-agnostic — use containerTag to namespace memories per agent or user.
metadata:
  openclaw:
    emoji: "🧠"
    requires:
      env: ["SUPERMEMORY_API_KEY"]
    primaryEnv: "SUPERMEMORY_API_KEY"
---

# Supermemory

Persistent semantic memory. Store anything, recall it later by meaning — not just keywords.

Key concept: **containerTag** namespaces memories per agent/user. Use a consistent tag (e.g. `sapphire`, `aria`, `user-123`) to keep memories isolated and retrievable.

## Setup

```bash
# Install SDK
npm install supermemory

# Verify key
echo $SUPERMEMORY_API_KEY
```

## Core Operations

### Add a memory
```js
const client = new Supermemory({ apiKey: process.env.SUPERMEMORY_API_KEY });

await client.add({
  content: "The user prefers Python over Node for backend work.",
  containerTag: "my-agent",  // namespace
  metadata: { source: "conversation", date: new Date().toISOString() }
});
```

### Search memories
```js
const results = await client.search.documents({
  q: "programming language preferences",
  containerTag: "my-agent",
  threshold: 0.5,
  limit: 10
});
results.results.forEach(r => {
  const text = r.chunks?.[0]?.content || r.title || '';
  console.log(text);
});
```

### Get user profile (static + dynamic context)
```js
const profile = await client.profile({
  containerTag: "my-agent",
  q: "recent context and identity",
  threshold: 0.5
});

const staticFacts = profile.profile?.static || [];
const recentContext = profile.profile?.dynamic || [];
const memories = profile.searchResults?.results || [];
```

### Ingest a file
```js
await client.add({
  content: fs.readFileSync('/path/to/file.md', 'utf8'),
  containerTag: "my-agent",
  metadata: { source: "file", path: "/path/to/file.md" }
});
```

### Forget a memory
```js
await client.memories.forget({ memoryId: "<id>" });
```

## Scripts

- **[scripts/ingest.js](scripts/ingest.js)** — Ingest a file or directory of markdown files into a containerTag. Change-tracked (skips unchanged files).
- **[scripts/recall.js](scripts/recall.js)** — Recall context for a containerTag. Prints static facts, dynamic context, and relevant memories. Use at session startup.
- **[scripts/add.js](scripts/add.js)** — Add a single memory from stdin or CLI arg.
- **[scripts/search.js](scripts/search.js)** — Search memories and print results.

Usage:
```bash
# Ingest a workspace directory
node scripts/ingest.js --dir /path/to/workspace --container my-agent

# Recall context at session start
node scripts/recall.js --container my-agent --query "who am I, recent projects"

# Add a one-off memory
node scripts/add.js --container my-agent --content "User prefers dark mode"

# Search
node scripts/search.js --container my-agent --query "payment integration"
```

## References

- [references/api.md](references/api.md) — Full API reference for advanced operations (batch add, delete, container management, conversations)
