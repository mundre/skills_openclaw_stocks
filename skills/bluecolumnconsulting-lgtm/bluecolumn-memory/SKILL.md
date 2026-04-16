---
name: bluecolumn-memory
description: Give AI agents persistent semantic memory using the BlueColumn API (bluecolumn.ai). Use when asked to remember, store, recall, or search memory using BlueColumn; when ingesting notes, conversations, documents, or audio into BlueColumn; when querying what an agent has previously stored; or when wiring up BlueColumn memory endpoints (/agent-remember, /agent-recall, /agent-note) in any workflow. Also use when the user mentions their BlueColumn API key (bc_live_*) and wants to store or retrieve information.
---

# BlueColumn Memory Skill

BlueColumn is a Memory Infrastructure API — three REST endpoints that give AI agents persistent semantic memory backed by Pinecone vector storage and OpenAI embeddings.

## API Key

Store the user's BlueColumn API key in `TOOLS.md` under a `### BlueColumn` section:
```
### BlueColumn
API Key: bc_live_XXXXXXXXXXXXXXXXXXXX
```

Read `TOOLS.md` to retrieve the key before making any API calls.

## Core Workflow

### Store something (text, doc, audio)
Use `/agent-remember` — see references/api.md for full field spec.
```bash
curl -X POST https://xkjkwqbfvkswwdmbtndo.supabase.co/functions/v1/agent-remember \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <key>" \
  -d '{"text": "...", "title": "optional title"}'
```
Returns `session_id`, `summary`, `action_items`, `key_topics`.

### Query memory
Use `/agent-recall` — field is `q` (not `query`).
```bash
curl -X POST https://xkjkwqbfvkswwdmbtndo.supabase.co/functions/v1/agent-recall \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <key>" \
  -d '{"q": "natural language question"}'
```
Returns `answer` + `sources` with relevance scores.

### Save agent observation
Use `/agent-note` — field is `text` (not `note`), min 5 chars.
```bash
curl -X POST https://xkjkwqbfvkswwdmbtndo.supabase.co/functions/v1/agent-note \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <key>" \
  -d '{"text": "...", "tags": ["optional", "tags"]}'
```

## When to Use Each Endpoint

| Situation | Endpoint |
|---|---|
| User shares a document, transcript, or block of text to remember | `/agent-remember` |
| User asks "what do you know about X?" or "recall..." | `/agent-recall` |
| Agent wants to save its own observation, preference, or decision | `/agent-note` |
| End of session — summarize and store what happened | `/agent-remember` or `/agent-note` |

## End-of-Session Memory

At the end of meaningful sessions, proactively push a summary to BlueColumn:
1. Summarize key decisions, facts, and context from the conversation
2. POST to `/agent-remember` with `title` = session topic
3. Confirm storage with the `session_id` returned

## Field Name Gotchas

Common mistakes — read references/api.md for full details:
- `/agent-remember` → `text` not `content`
- `/agent-recall` → `q` not `query`  
- `/agent-note` → `text` not `note`

## Full API Reference

See [references/api.md](references/api.md) for complete field specs, response shapes, and error reference.
