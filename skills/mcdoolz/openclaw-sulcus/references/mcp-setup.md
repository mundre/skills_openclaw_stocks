# MCP Setup (Claude Desktop & Local)

Sulcus speaks MCP (Model Context Protocol) natively via the `sulcus-local` binary.

## Claude Desktop (1-click)

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%/Claude/claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "sulcus": {
      "command": "sulcus-local",
      "args": ["serve"]
    }
  }
}
```

Restart Claude Desktop. Sulcus tools appear automatically.

## Configuration

Create `~/.sulcus/sulcus.ini` for cloud sync:

```ini
[server]
url = https://api.sulcus.ca
api_key = YOUR_API_KEY
```

Without config, `sulcus-local` runs in local-only mode with embedded PostgreSQL.

## MCP Tools Provided

| Tool | Description |
|---|---|
| `add_memory` | Store a new memory |
| `search_memory` | Semantic search |
| `list_memories` | List with filters |
| `recall_memory` | Retrieve by ID |
| `forget_memory` | Delete by ID |
| `boost_memory` | Increase heat |
| `deprecate_memory` | Accelerate decay |
| `pin_memory` | Pin (prevent decay) |
| `relate_memories` | Create relationship |
| `reclassify_memory` | Change memory type |
| `configure_thermodynamics` | Tune decay params |

## Streamable HTTP Transport

For web-based MCP clients (no local binary needed):

```
Endpoint: https://api.sulcus.ca/mcp
Authorization: Bearer YOUR_API_KEY
```

Supports the MCP Streamable HTTP transport specification for direct browser/cloud integration.

## Local Panel

`sulcus-local` serves a built-in dashboard at `http://localhost:4203` when running. Use it to browse memories, view the graph, and configure settings locally.
