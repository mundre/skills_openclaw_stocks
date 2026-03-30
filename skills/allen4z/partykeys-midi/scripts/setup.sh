#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_NAME="partykeys_midi"
MCP_NAME="partykeys"

echo "=== PartyKeys MIDI Skill Setup ==="
echo "Skill directory: $SKILL_DIR"
echo ""

# ── 1. Check prerequisites ──────────────────────────────────────────
check_bin() {
  if ! command -v "$1" &>/dev/null; then
    echo "ERROR: '$1' not found. Please install it first."
    exit 1
  fi
}

check_bin python3
check_bin node
check_bin npm

echo "[✓] Prerequisites: python3, node, npm"

# ── 2. Copy MCP server source if not present ────────────────────────
SERVER_DIR="$SKILL_DIR/server"
GATEWAY_DIR="$SKILL_DIR/web-gateway"

if [ ! -f "$SERVER_DIR/mcp_server.py" ]; then
  REPO_SERVER="$(cd "$SKILL_DIR/../../partykeys-mcp/server" 2>/dev/null && pwd || true)"
  if [ -n "$REPO_SERVER" ] && [ -f "$REPO_SERVER/mcp_server.py" ]; then
    echo "Copying MCP server source from repo..."
    mkdir -p "$SERVER_DIR"
    cp "$REPO_SERVER/mcp_server.py" "$SERVER_DIR/"
    cp "$REPO_SERVER/script_ble_client.py" "$SERVER_DIR/"
    cp "$REPO_SERVER/web_gateway_server.py" "$SERVER_DIR/"
    [ -f "$REPO_SERVER/requirements.txt" ] && cp "$REPO_SERVER/requirements.txt" "$SERVER_DIR/"
  else
    echo "ERROR: server/mcp_server.py not found."
    echo "Please copy partykeys-mcp/server/ contents into $SERVER_DIR/"
    exit 1
  fi
fi

if [ ! -f "$GATEWAY_DIR/package.json" ]; then
  REPO_GATEWAY="$(cd "$SKILL_DIR/../../partykeys-mcp/web-gateway" 2>/dev/null && pwd || true)"
  if [ -n "$REPO_GATEWAY" ] && [ -f "$REPO_GATEWAY/package.json" ]; then
    echo "Copying web-gateway source from repo..."
    mkdir -p "$GATEWAY_DIR"
    cp "$REPO_GATEWAY/package.json" "$GATEWAY_DIR/"
    for f in "$REPO_GATEWAY"/*.js "$REPO_GATEWAY"/*.html; do
      [ -f "$f" ] && cp "$f" "$GATEWAY_DIR/"
    done
  else
    echo "WARN: web-gateway not found — Web mode will not work (Script mode is fine)."
  fi
fi

echo "[✓] MCP server source ready"

# ── 3. Create Python venv & install deps ────────────────────────────
VENV_DIR="$SKILL_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating Python virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

echo "Installing Python dependencies..."
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet mcp aiohttp bleak

echo "[✓] Python dependencies installed"

# ── 4. Install Node.js deps for web-gateway ─────────────────────────
if [ -f "$GATEWAY_DIR/package.json" ]; then
  echo "Installing Node.js dependencies for web-gateway..."
  (cd "$GATEWAY_DIR" && npm install --silent 2>/dev/null)
  echo "[✓] Node.js dependencies installed"
fi

# ── 5. Register MCP server in OpenClaw ───────────────────────────────
PYTHON_BIN="$VENV_DIR/bin/python"
MCP_ENTRY="$SERVER_DIR/mcp_server.py"
MCP_JSON="$HOME/.openclaw/mcp.json"

register_mcp() {
  mkdir -p "$HOME/.openclaw"

  if command -v openclaw &>/dev/null; then
    openclaw mcp set "$MCP_NAME" "{\"command\":\"$PYTHON_BIN\",\"args\":[\"$MCP_ENTRY\"]}"
    echo "[✓] MCP server registered via 'openclaw mcp set'"
  elif command -v jq &>/dev/null; then
    if [ ! -f "$MCP_JSON" ]; then
      echo "{}" > "$MCP_JSON"
    fi
    local tmp
    tmp=$(mktemp)
    jq --arg name "$MCP_NAME" \
       --arg cmd "$PYTHON_BIN" \
       --arg entry "$MCP_ENTRY" \
       '.mcpServers[$name] = {"command": $cmd, "args": [$entry]}' \
       "$MCP_JSON" > "$tmp" && mv "$tmp" "$MCP_JSON"
    echo "[✓] MCP server registered in $MCP_JSON"
  else
    echo ""
    echo "──────────────────────────────────────────"
    echo "Add this to $MCP_JSON:"
    echo ""
    echo "  {"
    echo "    \"mcpServers\": {"
    echo "      \"$MCP_NAME\": {"
    echo "        \"command\": \"$PYTHON_BIN\","
    echo "        \"args\": [\"$MCP_ENTRY\"]"
    echo "      }"
    echo "    }"
    echo "  }"
    echo "──────────────────────────────────────────"
    echo ""
    echo "Or run: openclaw mcp set $MCP_NAME '{\"command\":\"$PYTHON_BIN\",\"args\":[\"$MCP_ENTRY\"]}'"
  fi
}

register_mcp

# ── 6. Copy skill to OpenClaw skills directory ──────────────────────
OPENCLAW_SKILLS_DIR="$HOME/.openclaw/skills/$SKILL_NAME"

if [ ! -d "$OPENCLAW_SKILLS_DIR" ] || [ "$SKILL_DIR" != "$OPENCLAW_SKILLS_DIR" ]; then
  echo "Linking skill to OpenClaw skills directory..."
  mkdir -p "$HOME/.openclaw/skills"
  ln -sfn "$SKILL_DIR" "$OPENCLAW_SKILLS_DIR"
  echo "[✓] Skill linked at $OPENCLAW_SKILLS_DIR"
fi

# ── 7. Done ─────────────────────────────────────────────────────────
echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Restart OpenClaw:  openclaw gateway restart"
echo "  2. Verify skill:      openclaw skills list"
echo "  3. Verify MCP:        openclaw mcp list"
echo "  4. Test:              Ask the agent '连接我的 MIDI 键盘'"
echo ""
echo "MCP server: $PYTHON_BIN $MCP_ENTRY"
echo "Skill path: $SKILL_DIR"
