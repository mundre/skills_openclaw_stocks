---
name: "Qoris Memory — Persistent Agent Memory"
description: "Git-like persistent memory for OpenClaw agents. Your agent remembers everything across sessions — versioned, branched, and mergeable like a repository. Never lose context again. Powered by Qoris AI."
version: "1.0.0"
author: "qorisai"
tags:
  - memory
  - persistent-memory
  - agent-memory
  - context
  - versioning
  - knowledge-base
  - cross-session
  - enterprise
  - rag
  - mcp
  - latest
requires:
  env:
    QORIS_API_KEY: "Your Qoris API key from qoris.ai/dashboard"
    QORIS_WORKSPACE_ID: "Your Qoris workspace ID from qoris.ai/dashboard"
---

# Qoris Memory — Persistent Agent Memory

## Purpose

OpenClaw agents are powerful. But by default they forget everything when a session ends. Every conversation starts from zero. Every context you built up disappears.

Qoris Memory gives your OpenClaw agent persistent, versioned, cross-session memory that works like Git — commits, branches, merges, and conflict resolution. Your agent builds up knowledge over time, remembers it across sessions, and shares it across your entire team.

**Think of it as GitHub for your agent's brain.**

## What Qoris Memory Does

### Persistent cross-session memory
Everything your agent learns, discovers, or is told persists beyond the current session. Next session it picks up exactly where it left off. No re-explaining context. No repeating yourself.

### Versioned memory commits
Every memory update is a versioned commit with a timestamp and author. Roll back to any previous state. See the full history of what your agent knows and when it learned it.

### Memory branches
Create separate memory branches for different projects, clients, or contexts. Switch between branches the same way you switch Git branches. Your agent operates in the right context for the right task.

### Conflict resolution
When multiple agents or team members update the same memory, Qoris Memory handles conflicts intelligently — surfacing disagreements for human resolution rather than silently overwriting important context.

### Shared team memory
Memory is workspace-scoped. Every agent in your workspace shares the same knowledge base. One agent learns something — all agents know it. Your AI team operates with a unified brain.

### Knowledge search
Semantic search across everything your agent knows. Ask questions about your memory — get precise, cited answers grounded in what was actually stored, not hallucinated.

## Memory Architecture

Qoris Memory uses a canonical + vector hybrid architecture:

```
Canonical Layer    — structured facts, entities, relationships
                     exact-match retrieval, versioned records

Vector Layer       — semantic embeddings for fuzzy search
                     conceptual retrieval across all memories

Conflict Engine    — detects contradictions between memories
                     surfaces them for human resolution

Audit Trail        — every memory read and write logged
                     integrated with Knox governance if installed
```

## Available Memory Tools

Once installed your agent has access to these tools:

### save_memory
Store a new memory with optional tags and metadata.

### get_memories
Retrieve all memories or filter by tag, date, or relevance.

### search_knowledge
Semantic search across your entire memory and knowledge base.

### update_memory
Update an existing memory with version tracking.

### delete_memory
Remove a memory with audit trail entry.

### list_knowledge_documents
List all documents and files indexed in the knowledge base.

### get_document_full_content
Retrieve the complete content of a knowledge document.

## Setup Instructions

### Step 1 — Get your Qoris credentials

1. Go to qoris.ai and create an account
2. Navigate to your workspace dashboard
3. Copy your QORIS_API_KEY and QORIS_WORKSPACE_ID
4. Add them to your environment:

```bash
export QORIS_API_KEY="your-api-key-here"
export QORIS_WORKSPACE_ID="your-workspace-id-here"
```

### Step 2 — Connect Qoris Memory MCP server

Add to your OpenClaw configuration:

```json
{
  "mcpServers": {
    "qoris-memory": {
      "url": "https://mcp.qoris.ai/mcp",
      "headers": {
        "Authorization": "Bearer ${QORIS_API_KEY}",
        "X-Workspace-ID": "${QORIS_WORKSPACE_ID}"
      }
    }
  }
}
```

### Step 3 — Verify memory is active

Start a new OpenClaw session and run:

```
/memory status
```

## Memory + Knox Governance

If you have Knox Governance installed alongside Qoris Memory, every memory read and write is automatically logged in the Knox audit trail. Install both for the complete governed enterprise agent stack:

```bash
clawhub install knox-governance
clawhub install qoris-memory
```

## Constraints

Memory is workspace-scoped. Free tier includes up to 1,000 memories and 500MB knowledge storage. Paid plans unlock unlimited memories and storage.

## Support and Documentation

- Full documentation: docs.qoris.ai/memory
- Dashboard: qoris.ai/dashboard
- Demo: qoris.ai/contact-us
- Support: eliel@qoris.ai

## About Qoris AI

Qoris AI is the trust and governance layer for enterprise AI agents. Knox governs what agents do. Qoris Memory gives them what they know.

NVIDIA Inception Program member. Claude Partner Network member. Patent Pending U.S. 63/907,730. Based in Stamford, CT.

qoris.ai
