# Add MCP Server

Procedure for registering a new MCP server in `.mcp.json`.

## Required Procedure: Scope Selection (AskUserQuestion Required)

**Before adding an MCP server, always use AskUserQuestion in 2 steps:**

### Step 1: Scope Selection

| Option | Description |
|--------|-------------|
| Global | Add to each agent's config file (proceed to step 2) |
| Project | Add only to the current project's `./.mcp.json` |

### Step 2: When Global is selected → Agent Selection (multiSelect)

| Agent | Config File | Difference |
|-------|-------------|------------|
| Claude Code | `~/.mcp.json` | `transport` field not required |
| Cursor | `~/.cursor/mcp.json` | `transport` field not required |
| Antigravity | `~/.gemini/antigravity/mcp_config.json` | `"transport": "stdio"` required |

**multiSelect: true** — can add to multiple agents simultaneously.

**Do not decide arbitrarily.** Even if `.mcp.json` exists in the project directory, the user may want to add globally, and vice versa.

## Core Rule: Register as Separate Server

New MCP server = register as a separate key in the `mcpServers` object. **Do not put it inside an existing server's `env`.**

**Correct example**:
```json
{
  "mcpServers": {
    "code-mode": {
      "command": "npx",
      "args": ["-y", "@utcp/code-mode-mcp"],
      "env": { "UTCP_CONFIG_FILE": "~/.utcp_config.json" }
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

**Incorrect example** (adding as environment variable):
```json
{
  "mcpServers": {
    "code-mode": {
      "env": {
        "UTCP_CONFIG_FILE": "~/.utcp_config.json",
        "CONTEXT7": "some value"
      }
    }
  }
}
```

## Validation Checklist

- [ ] JSON syntax is valid
- [ ] Each server is registered as a separate key inside the `mcpServers` object
- [ ] `command` and `args` fields exist
- [ ] Environment variables are contained only in that server's `env` object
- [ ] Another server's functionality is not added as an environment variable
