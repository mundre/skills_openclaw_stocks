# MCP Server Format

JSON format reference per agent.

## File Locations

| Agent | File | Scope |
|-------|------|-------|
| (Project) | `./.mcp.json` | Current project only |
| Claude Code | `~/.mcp.json` | Global |
| Cursor | `~/.cursor/mcp.json` | Global |
| Antigravity | `~/.gemini/antigravity/mcp_config.json` | Global |

## Basic Format

```json
{
  "server-name": {
    "command": "npx",
    "args": ["-y", "@package/name"]
  }
}
```

## When Environment Variables Are Required

```json
{
  "server-name": {
    "command": "npx",
    "args": ["-y", "@package/name"],
    "env": {
      "API_KEY": "${API_KEY}",
      "CONFIG_FILE": "~/.config/file.json"
    }
  }
}
```

## Using uvx (Python Packages)

```json
{
  "postgres": {
    "command": "uvx",
    "args": ["postgres-mcp", "--access-mode=unrestricted"],
    "env": {
      "DATABASE_URI": "postgresql://user:pass@host:5432/db"
    }
  }
}
```

## Antigravity Format Difference

Antigravity requires the `transport` field:

```json
{
  "server-name": {
    "transport": "stdio",
    "command": "npx",
    "args": ["-y", "@package/name"]
  }
}
```

Claude Code / Cursor do not require `transport`.
