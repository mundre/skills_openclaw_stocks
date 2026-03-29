---
name: mcp-marketplace
description: >
  Install, configure, and manage MCP servers. Search 50+ verified servers plus
  npm and Smithery registries. Auto-generate configs for OpenClaw, Claude Desktop,
  Claude Code, and Cursor. Health check servers, troubleshoot issues. Use for:
  "install GitHub MCP", "add Postgres MCP server", "find database servers",
  "show my MCP servers", "remove Slack MCP", "set up Notion MCP", "what MCP
  servers are available", "is my server working", "test the GitHub MCP".
  Covers: MCP install, setup, configure, discover, search, remove, uninstall,
  list, status, update, add server, connect server, health check, troubleshoot.
---

# MCP Server Marketplace

Help users discover, install, configure, and manage MCP servers. Supports OpenClaw, Claude Desktop, Claude Code, and Cursor.

## Core Principles

1. **ClawHub First** — Always check for a ClawHub plugin bundle before raw server install. Bundles include skills and workflows on top of the MCP connection.
2. **Never Store Secrets** — Auth values are always env var references (`${VAR_NAME}`), never raw tokens. Never ask the user to paste their actual token in chat.
3. **Verify Before Acting** — Confirm server choice and auth readiness before installing.
4. **Guide Completely** — Don't just install. Walk through auth setup and verification.

## Intent Routing

Classify the user's request into one of these intents, then follow the corresponding workflow.

### DISCOVER — "What MCP servers are available for X?"

1. Run search:
   ```
   python3 {baseDir}/scripts/search_registries.py --query "<user's topic>" [--category "<category>"]
   ```
2. If `clawHubMatch` is present, mention the bundle first: "There's a **[bundle name]** plugin on ClawHub with [N] skills — want that instead?"
3. Present results as a numbered list with name, description, and auth requirements.
4. If any result has `"source": "npm"` or `"source": "smithery"`, add a note: "This server is from [npm/Smithery] and hasn't been verified by our team. It should work but proceed with caution."
5. Offer to install any result.

### INSTALL — "Install the X MCP server"

This is the most complex flow. Follow all steps in order.

**Step 1 — Search:**
```
python3 {baseDir}/scripts/search_registries.py --query "<server name>"
```

**Step 2 — ClawHub bundle offer:**
If `clawHubMatch` is present, offer the bundle:

> I found a **[bundle displayName]** plugin on ClawHub that includes the MCP connection plus [skillCount] additional skills. Would you like the full bundle, or just the raw MCP connection?

If user wants the bundle, guide them to install via ClawHub (`clawhub install <bundleId>`). Then record the install and stop.

**Step 3 — Confirm server:**
If multiple results, present a numbered list and ask user to pick. If one result, confirm: "I'll set up **[displayName]** — sound good?"

**Step 4 — Build config:**
```
python3 {baseDir}/scripts/build_config.py --server-id "<id>" [--client "<client>"]
```
The `--client` flag is optional. If omitted, the script auto-detects the client (OpenClaw, Claude Desktop, Claude Code, or Cursor). The output includes `mergeTarget` (the config file path) and `client` (the detected client name).

**Step 5 — Auth guidance (if server has requiredEnv):**
Follow the Auth Guidance Pattern below. Wait for user to confirm they have their token ready before proceeding.

**Step 6 — Check prerequisites and install:**
```
python3 {baseDir}/scripts/install_server.py --server-id "<id>"
```
This script checks prerequisites and returns the install command — it does NOT run it.

- If `prerequisitesMet` is `false`, show the `prerequisites.suggestion` and help the user install the prerequisite first.
- If `prerequisitesMet` is `true`, run the `installCommand.command` directly using the Bash tool. For example, if the output says `"command": "npx -y @github/mcp-server --help"`, run that command to verify the package resolves.
- If `installCommand.command` is `null` (HTTP servers), skip — no install needed.
- If the install command fails, try the `installCommand.fallbackCommand` if present, or consult `{baseDir}/references/troubleshooting.md`.

**Step 7 — Write config:**
Present the `configEntry` from step 4 and explain it needs to be added to the config file at `mergeTarget` (the path returned by build_config.py). If the config file exists, merge the new server entry into the existing `mcpServers` object. If it doesn't exist, create it:
```json
{
  "mcpServers": {
    <configEntry content here>
  }
}
```

**Step 8 — Record state:**
```
python3 {baseDir}/scripts/manage_servers.py --action record --server-id "<id>" --package "<package>" --transport "<transport>" --install-method "<method>" --source "<source>"
```
Use `--source curated`, `--source npm`, or `--source smithery` based on where the server was found.

**Step 8.5 — Health check (optional):**
```
python3 {baseDir}/scripts/health_check.py --server-id "<id>"
```
If `status` is `"healthy"`, include the tool count in the summary. If `"unhealthy"` or `"error"`, troubleshoot before declaring success — consult `{baseDir}/references/troubleshooting.md`.

**Step 9 — Summary:**
Tell the user what was installed, what tools are now available (from health check if run), and remind them to restart their client to pick up the new server.

### CONFIGURE — "Set the API key for X" / "Connect X to my database"

1. Identify the server from the user's request.
2. Run `build_config.py --server-id "<id>"` with any custom env/args the user provides:
   ```
   python3 {baseDir}/scripts/build_config.py --server-id "<id>" --custom-env '{"KEY": "${KEY}"}'
   ```
3. Follow the Auth Guidance Pattern for any new env vars.
4. Update the `.mcp.json` config entry.

### STATUS — "Show my installed MCP servers"

1. Run:
   ```
   python3 {baseDir}/scripts/manage_servers.py --action list
   ```
2. Present as a formatted table: server name, package, transport, install method, installed date, config present.
3. If any server has `"configPresent": false`, warn: "This server is recorded but its config entry was not found. It may need to be re-configured."
4. If the user asks about a specific server:
   ```
   python3 {baseDir}/scripts/manage_servers.py --action status --server-id "<id>"
   ```
5. If no servers installed, suggest running a discovery search.

### REMOVE — "Remove the X server"

1. Confirm: "Remove **[displayName]**? This will remove the state record. You should also remove its entry from `.mcp.json`."
2. Run:
   ```
   python3 {baseDir}/scripts/manage_servers.py --action remove --server-id "<id>"
   ```
3. Remind user to remove the corresponding entry from `.mcp.json` and restart OpenClaw.

### UPDATE — "Update my MCP servers"

1. List installed servers via `manage_servers.py --action list`.
2. For npx/uvx servers, no explicit update is needed — they resolve latest versions on each run.
3. For npm global servers, suggest: `npm update -g <package>`.
4. For pip servers, suggest: `pip install --upgrade <package>`.

### HEALTH CHECK — "Is my X server working?" / "Test the GitHub MCP"

1. Identify the server from the user's request.
2. Run:
   ```
   python3 {baseDir}/scripts/health_check.py --server-id "<id>"
   ```
3. If `status` is `"healthy"`:
   - Present the tool count and list a few tool names.
   - "Your **[displayName]** server is healthy with [toolCount] tools available."
4. If `status` is `"unhealthy"` or `"error"`:
   - Show the error message.
   - Consult `{baseDir}/references/troubleshooting.md` for the specific error.
   - Update server status: `python3 {baseDir}/scripts/manage_servers.py --action update-status --server-id "<id>" --status error`
   - Guide the user through the fix, then re-run the health check to confirm.

### TROUBLESHOOT — "X server isn't working" / "Why can't I use the GitHub tools?"

1. Identify the server.
2. Run health check:
   ```
   python3 {baseDir}/scripts/health_check.py --server-id "<id>"
   ```
3. Based on the error, consult `{baseDir}/references/troubleshooting.md`.
4. Guide the user through the fix step by step.
5. Re-run health check to confirm resolution.
6. If resolved, update status: `python3 {baseDir}/scripts/manage_servers.py --action update-status --server-id "<id>" --status active`

## Auth Guidance Pattern

When a server requires environment variables:

1. **List each required variable** with its purpose (from `authGuidance.instructions`).
2. **Provide the generation URL** if available: "You can create one at [URL]".
3. **Show the export command**: `export VAR_NAME=<your-value-here>`
4. **Remind about persistence**: "Add this to `~/.zshrc` (or `~/.bashrc`) so it persists across sessions."
5. **NEVER ask the user to paste their actual token** in the chat. Guide them to set it in their shell.
6. **NEVER store raw token values** in config — only `${VAR_NAME}` references.

## Error Recovery

- **Install fails with missing prerequisites**: Read `{baseDir}/references/troubleshooting.md` for the specific error and guide the user.
- **Server not found in catalog**: The search falls back to npm and Smithery registries automatically. If still not found, suggest checking https://github.com/modelcontextprotocol/servers for the official list or https://smithery.ai for community servers.
- **Config generation fails**: Show a manual config example from `{baseDir}/references/transport-patterns.md` and walk through it.
- **Server starts but tools don't appear**: Run `python3 {baseDir}/scripts/health_check.py --server-id "<id>"` to diagnose. Consult `{baseDir}/references/troubleshooting.md`.
- **Health check times out**: The server may need env vars, a database connection, or more time. Try increasing the timeout with `--timeout 30`.
- **Config not found for a client**: Check the `mergeTarget` path from build_config.py. See `{baseDir}/references/troubleshooting.md` for client-specific config paths.

## Categories

Available category filters for discovery: `developer-tools`, `database`, `communication`, `productivity`, `cloud-infra`, `ai-ml`, `data`, `cms-content`, `finance`, `observability`, `search`, `auth`, `storage`, `version-control`, `browser`.
