---
name: obsidian-search
description: "Semantic search for Obsidian notes using AI vector embeddings. Find notes by meaning, discover connections, filter by tags/dates/folders, and retrieve full content. Use when the user says 'search my notes', 'find in Obsidian', 'what did I write about', 'related notes', 'Obsidian search', or wants AI-powered knowledge retrieval from their Obsidian vault."
version: 1.0.0
metadata:
  openclaw:
    emoji: "🔍"
    homepage: https://obsidian.10xboost.org/
---

# Obsidian Search

AI-powered semantic search for your Obsidian notes — find notes by meaning, not just keywords. Powered by [Obvec](https://obsidian.10xboost.org).

## Security & Data Handling

- **MCP link is a credential**: Your MCP Server URL contains an embedded authentication token. Treat it like a password — do not share it publicly. You can regenerate it anytime in Settings.
- **Token scope**: The token grants **read-only** access to your indexed Obsidian notes. It can search, list, retrieve note content, and analyze connections. It cannot modify, delete, or create notes in your vault.
- **Token storage**: The token is generated and managed server-side. When you paste the MCP link into a Claude Connector, the link (containing the token) is stored locally by your MCP client. You can regenerate or revoke the token anytime at [obsidian.10xboost.org](https://obsidian.10xboost.org), which invalidates any previously shared links.
- **Data flow**: To enable semantic search, your note content is uploaded to the Obvec service and indexed as vector embeddings on a secure cloud server. Search queries are also sent to the server for similarity matching. No data is shared with other users or used for model training.
- **No additional credentials**: No separate API keys, environment variables, or secrets are needed beyond the MCP link.
- **Third-party service**: This skill relies on [Obvec](https://obsidian.10xboost.org), an AI-powered Obsidian search service. By using this skill, you are sending your note content to the Obvec server for indexing and search. Review the [privacy policy](https://obsidian.10xboost.org) before use.


## Prerequisites

1. **Sign up** at [obsidian.10xboost.org](https://obsidian.10xboost.org) with Google
2. **Connect your Obsidian vault** — follow the setup guide to sync your notes
3. **Get your MCP link**: Go to **Settings** → copy your MCP Server URL
4. **Add to Claude**: Paste the MCP link as a Connector — no install, no API key needed

## Available Tools (4)

| Tool | Description |
|------|-------------|
| `search_notes` | Semantic search — find notes by meaning with similarity scoring, tag/date filters |
| `list_notes` | Browse notes by folder, tags, date range, with sorting options |
| `get_note` | Retrieve full content of a specific note by path or search term |
| `analyze_connections` | Discover related notes through AI-powered similarity analysis |

## Workflow

### Step 1: Understand the User's Intent

| User Request | Tool to Use |
|-------------|------------|
| "Find notes about X" | `search_notes` |
| "What did I write about X?" | `search_notes` |
| "Show my recent notes" | `list_notes` with `sortBy: "modifiedAt"` |
| "Notes in folder X" | `list_notes` with `pathPrefix` |
| "Open note X" | `get_note` |
| "What's related to X?" | `analyze_connections` |

### Step 2: Search Notes

#### Semantic Search
```
search_notes(
  query: "machine learning project ideas",
  limit: 10,
  minScore: 0.7
)
```

#### With Filters
```
search_notes(
  query: "meeting notes",
  tags: ["work", "project-x"],
  sortBy: "modifiedAt",
  limit: 20
)
```

### Step 3: Retrieve Full Content

```
get_note(path: "Projects/AI Research.md")
```
or search by term:
```
get_note(searchTerm: "quarterly review")
```

### Step 4: Discover Connections

```
analyze_connections(
  reference: "Projects/AI Research.md",
  limit: 10,
  minScore: 0.6
)
```

Returns notes most semantically similar to the reference — great for finding related ideas, building knowledge graphs, or discovering forgotten notes.

### Step 5: Present Results

- **Search results**: Show titles, relevance scores, and brief excerpts
- **Note content**: Display the full markdown content
- **Connections**: Present as a ranked list with similarity scores and note titles


## Error Handling

| Error | Solution |
|-------|----------|
| No results found | Try a broader query or lower `minScore` |
| Note not found | Use `list_notes` to find the correct path |
| Token expired | Re-authenticate via browser (tokens last 30 days by default) |
