---
name: openclaw-sulcus
description: "Sulcus — thermodynamic memory for AI agents. Use when: (1) storing memories with heat-based decay and spaced repetition, (2) searching/recalling context across sessions, (3) managing memory lifecycle (pin, boost, deprecate, reclassify), (4) setting up the OpenClaw memory plugin, (5) tuning thermodynamic parameters (half-lives, decay classes, resonance). Replaces flat-file memory with persistent, heat-governed recall. Works with OpenClaw plugin, MCP (Claude Desktop, local), Python SDK, Node.js SDK, or REST API."
author: "Digital Forge Studios <contact@dforge.ca>"
version: "1.4.6"
---

# Sulcus

Sulcus is a thermodynamic virtual Memory Management Unit (vMMU). Memories have **heat** that decays over time — frequently accessed memories stay hot, neglected ones cool and page out. This mirrors how human memory works.

## Key Concepts

- **Heat**: 0.0–1.0 score. Recall boosts heat, time decays it. Hot memories enter context, cold ones don't.
- **Decay**: Governed by half-life per memory type. Episodic memories fade in hours, preferences persist for months.
- **Stability**: Spaced repetition multiplier. Each recall increases stability, stretching effective half-life.
- **Pinning**: Pinned memories never decay (heat floor = 1.0).
- **Resonance**: Related memories get heat spillover when neighbors are recalled.

## Memory Types

| Type | Half-life | Use for |
|---|---|---|
| `episodic` | 24h | What happened — conversations, events, tasks |
| `semantic` | 30d | What you know — facts, knowledge, context |
| `preference` | 90d | What you like — user preferences, settings |
| `procedural` | 180d | How to do things — workflows, processes |
| `fact` | 30d | Verified truths — dates, names, specs |
| `moment` | 12h | Fleeting context — current mood, temp state |

## Decay Classes

| Class | Effect |
|---|---|
| `volatile` | 2× faster decay |
| `normal` | Standard half-life |
| `persistent` | 2× slower decay |
| `permanent` | No decay (heat stays at initial value) |

## Tools Available

When the Sulcus plugin is active, these tools are provided:

### memory_store
Store a new memory. Auto-detects type from content.
```
memory_store(text="User prefers dark mode in all applications", memoryType="preference")
```

### memory_search
Semantic search across all memories. Returns matches with heat scores.
```
memory_search(query="database preferences", maxResults=5, minScore=0.3)
```

### memory_get
Retrieve a specific memory by UUID. Auto-boosts heat on recall.
```
memory_get(path="019d021b-8911-7eb3-b290-da264fa673d3")
```

### memory_forget
Delete a memory permanently.
```
memory_forget(memoryId="019d021b-8911-7eb3-b290-da264fa673d3")
```

## Auto-Recall & Auto-Capture

With the OpenClaw plugin configured:

- **Auto-recall**: Before each agent turn, searches for memories relevant to the user's message and injects them into context. No manual `memory_search` needed for basic recall.
- **Auto-capture**: After each turn, detects important information (preferences, facts, decisions) and stores automatically.

Manual `memory_search` is still useful for deep/specific queries beyond what auto-recall surfaces.

## When to Store Memories

Store when you encounter:
- User preferences or settings ("I prefer TypeScript over JavaScript")
- Important decisions ("We chose PostgreSQL for the database")
- Facts worth remembering ("The server IP is 10.0.0.5")
- Procedures ("To deploy: run build, then push to main")
- Contact info ("Sarah's email is sarah@example.com")
- Project context ("The API uses REST, not GraphQL")

Do NOT store: transient chat, greetings, acknowledgments, or information already in workspace files.

## Security & Privacy

> **Credential requirement:** This plugin requires a Sulcus API key (`apiKey` in config). Obtain one by registering at [sulcus.ca](https://sulcus.ca). No anonymous access is possible.

> **Data handling:** When using the cloud backend (`api.sulcus.ca`), memory content is sent over HTTPS to Sulcus servers hosted in Canadian Azure regions (canadacentral). For fully offline operation, use `sulcus-local` — no data leaves your machine.

Sulcus is an external memory backend. When configured:
- **Auto-recall** sends the user's message text to the Sulcus API for semantic search. **Disable with `autoRecall: false`.**
- **Auto-capture** detects preferences/facts from conversations and stores them. **Disable with `autoCapture: false`.**
- **Tenant isolation**: All data is stored under your tenant ID, cryptographically isolated from other users. Agents within the same tenant can share memories across namespaces — this is intentional for multi-agent setups.
- **Namespace scoping**: Each agent gets its own namespace. Cross-namespace queries within the same tenant are permitted by design (e.g., agent A can recall memories from agent B if they share a tenant).
- **API key** is required for all operations — stored in your OpenClaw config at `plugins.entries.openclaw-sulcus.config.apiKey`.
- **Self-hosted option**: Run `sulcus-local` binary for fully local, offline memory with embedded PostgreSQL. No cloud dependency, no network calls.
- **Open source**: Server, client, and SDKs are available at [github.com/digitalforgeca/sulcus](https://github.com/digitalforgeca/sulcus).

Auto-capture and auto-recall can be disabled independently in the plugin config. The plugin performs no network calls when both are disabled and no manual memory tools are invoked.

## Setup

### OpenClaw Plugin (recommended)

See [references/openclaw-setup.md](references/openclaw-setup.md) for complete installation and configuration.

> **Plugin ID: `openclaw-sulcus`** — use this exact string in `plugins.slots.memory`, `plugins.entries`, and `plugins.allow`.

Quick version:
1. `openclaw plugins install @digitalforgestudios/openclaw-sulcus`
2. Add to `openclaw.json`: `plugins.slots.memory = "openclaw-sulcus"` with config under `plugins.entries.openclaw-sulcus`
3. Add `"openclaw-sulcus"` to `plugins.allow` array
3. `openclaw restart`

### MCP (Claude Desktop, local)

See [references/mcp-setup.md](references/mcp-setup.md) for MCP configuration.

### Python SDK

```bash
pip install sulcus
```
```python
from sulcus import Sulcus
client = Sulcus(api_key="sk-...")
client.store("User prefers dark mode", memory_type="preference")
results = client.search("dark mode")
```

### Node.js SDK

```bash
npm install sulcus
```
```typescript
import { Sulcus } from "sulcus";
const client = new Sulcus({ apiKey: "sk-..." });
await client.store("User prefers dark mode", { memoryType: "preference" });
const results = await client.search("dark mode");
```

## Thermodynamic Configuration

For tuning decay rates, resonance, tick modes, and per-type overrides, see [references/thermodynamics.md](references/thermodynamics.md).

## API Reference

For the full REST API endpoint list, see [references/api.md](references/api.md).
