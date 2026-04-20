#!/bin/bash
# install.sh — self-improvement-loop v4.4.8 installer
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${HOME}/.openclaw/workspace"
CANONICAL_DIR="$WORKSPACE/scripts/self-improvement"
CANONICAL_HOOKS="${HOME}/.openclaw/hooks/self-improvement"
SKILL_HOOKS="$SCRIPT_DIR/hooks"
SKILL_SCRIPTS="$SCRIPT_DIR/scripts"
LEARNINGS_DIR="$WORKSPACE/.learnings"
SKILL_CREATOR_SLUG="yixinli867/skill-creator-2"
OPENCLAW_JSON="${HOME}/.openclaw/openclaw.json"

# ─────────────────────────────────────────────────────────────
# Helper: detect available channels from openclaw.json
# Returns: channel name (e.g. "telegram") or empty
# Sets global CHANNEL and CHANNEL_ACCOUNT
# ─────────────────────────────────────────────────────────────
detect_channel() {
    python3 -c "
import json, os, sys

path = os.path.expanduser('$OPENCLAW_JSON')
if not os.path.exists(path):
    print(''); sys.exit(0)

with open(path) as f:
    d = json.load(f)

channels = d.get('channels', {})
available = []
for name, cfg in channels.items():
    accounts = cfg.get('accounts', {}) if isinstance(cfg, dict) else {}
    if accounts:
        # Pick first available account
        first_account = list(accounts.keys())[0]
        print(f'{name}:{first_account}')
        available.append(name)

if not available:
    print('')
" 2>/dev/null
}

# ─────────────────────────────────────────────────────────────
# Helper: detect Telegram user ID from openclaw.json
# ─────────────────────────────────────────────────────────────
detect_telegram_id() {
    python3 -c "
import json, os
path = os.path.expanduser('$OPENCLAW_JSON')
if not os.path.exists(path):
    print(''); exit()
with open(path) as f:
    d = json.load(f)
cfg = d.get('channels', {}).get('telegram', {})
accounts = cfg.get('accounts', {})
if 'default' in accounts:
    ids = accounts['default'].get('allowFrom', [])
    if ids: print(ids[0]); exit()
ids = cfg.get('allowFrom', [])
if ids: print(ids[0]); exit()
print('')
" 2>/dev/null
}

# ─────────────────────────────────────────────────────────────
# Helper: check if skill-creator is installed
# ─────────────────────────────────────────────────────────────
is_skill_creator_installed() {
    [ -d "$WORKSPACE/skills/skill-creator" ]
}

# ─────────────────────────────────────────────────────────────
# Helper: run skill-creator install (non-interactive)
# ─────────────────────────────────────────────────────────────
install_skill_creator() {
    echo "  Installing skill-creator..."
    local output
    output=$(openclaw skill install "https://clawhub.ai/$SKILL_CREATOR_SLUG" 2>&1) && return 0
    echo "  ⚠ skill-creator install output: $output"
    return 1
}

# ─────────────────────────────────────────────────────────────
# 0. Pre-flight: python3 + skill-creator + channel detection
# ─────────────────────────────────────────────────────────────
echo "=== self-improvement-loop v4.3 installer ==="
echo ""

if ! command -v python3 &>/dev/null; then
    echo "[✗] python3 not found. This skill requires Python 3."
    echo "    Install python3 and retry."
    exit 1
fi
echo "[✓] python3: found"

if is_skill_creator_installed; then
    echo "[✓] skill-creator: found, skipping"
else
    echo "[✓] skill-creator: not found, installing..."
    if install_skill_creator; then
        echo "  ✓ skill-creator installed"
    else
        echo "  ⚠ skill-creator install failed. Run manually after install:"
        echo "    openclaw skill install https://clawhub.ai/$SKILL_CREATOR_SLUG"
    fi
fi

# Detect available channels
echo ""
echo "[0/8] Detecting notification channels..."
CHANNEL_LIST=$(detect_channel)
CHANNEL_COUNT=$(echo "$CHANNEL_LIST" | grep -c ":" || echo 0)

if [ "$CHANNEL_COUNT" -eq 0 ]; then
    echo "  ⚠ No channels detected in openclaw.json."
    echo "    Configure at least one channel (e.g. Telegram) before installing."
    echo "    Installation aborted."
    exit 1
elif [ "$CHANNEL_COUNT" -eq 1 ]; then
    CHANNEL_INFO=$(echo "$CHANNEL_LIST" | grep ":")
    export CHANNEL=$(echo "$CHANNEL_INFO" | cut -d: -f1)
    export CHANNEL_ACCOUNT=$(echo "$CHANNEL_INFO" | cut -d: -f2)
    echo "  ✓ Detected channel: $CHANNEL (account: $CHANNEL_ACCOUNT)"
else
    echo "  ⚠ Multiple channels detected:"
    echo "$CHANNEL_LIST" | while IFS=: read -r ch acc; do
        echo "    - $ch (account: $acc)"
    done
    echo "  Please specify which channel to use by setting CHANNEL env var:"
    echo "    CHANNEL=telegram CHANNEL_ACCOUNT=default bash install.sh"
    echo "  Installation aborted."
    exit 1
fi

# ── 1. Create directories ───────────────────────────────
echo ""
echo "[1/8] Creating directories..."
mkdir -p "$CANONICAL_DIR"
mkdir -p "$CANONICAL_HOOKS"
mkdir -p "$LEARNINGS_DIR"
mkdir -p "$LEARNINGS_DIR/.pending_notifications"
echo "  ✓ directories created"

# ── 2. Install Hook ────────────────────────────────────
echo ""
echo "[2/8] Installing Hook..."
cp "$SKILL_HOOKS/handler.js" "$CANONICAL_HOOKS/handler.js"
echo "  ✓ handler.js → $CANONICAL_HOOKS/"

# ── 3. Install scripts ─────────────────────────────────
echo ""
echo "[3/8] Installing scripts..."
for script in distill.sh archive.sh match-existing-skill.sh; do
    cp "$SKILL_SCRIPTS/$script" "$CANONICAL_DIR/$script" 2>/dev/null \
        && echo "  ✓ $script"
done

for py_script in distill_json.py write_notified.py; do
    cp "$SKILL_SCRIPTS/$py_script" "$CANONICAL_DIR/$py_script"
    echo "  ✓ $py_script"
done
echo "  ✓ all scripts → $CANONICAL_DIR/"

# ── 4. Initialize learnings files ──────────────────────
echo ""
echo "[4/8] Initializing learnings files..."
for f in LEARNINGS.md ERRORS.md FEATURE_REQUESTS.md; do
    target="$LEARNINGS_DIR/$f"
    if [ ! -f "$target" ]; then
        cp "$SCRIPT_DIR/learnings/$f" "$target"
        echo "  ✓ $f (created)"
    else
        echo "  ✓ $f (exists, skipped)"
    fi
done

# ── 5. Register Hook ───────────────────────────────────
echo ""
echo "[5/8] Registering Hook..."
if openclaw hooks list 2>/dev/null | grep -q "self-improvement"; then
    echo "  ✓ Hook already registered, skipped"
else
    openclaw hooks set self-improvement "$CANONICAL_HOOKS/handler.js" 2>/dev/null \
        && echo "  ✓ Hook registered" \
        || echo "  ⚠ Hook registration failed. Run manually:"
    echo "    openclaw hooks set self-improvement $CANONICAL_HOOKS/handler.js"
fi

# ── 6. Setup Cron jobs ─────────────────────────────────
echo ""
echo "[6/8] Setting up Cron jobs..."
TELEGRAM_ID=$(detect_telegram_id)
if [ -z "$TELEGRAM_ID" ]; then
    echo "  ⚠ Could not auto-detect Telegram user ID."
    echo "    Set TELEGRAM_ID env var or check openclaw.json allowFrom."
else
    echo "  ✓ Detected Telegram ID: $TELEGRAM_ID"
fi

CHANNEL="$CHANNEL" \
CHANNEL_ACCOUNT="$CHANNEL_ACCOUNT" \
TELEGRAM_ID="$TELEGRAM_ID" \
    python3 "$SKILL_SCRIPTS/setup_crons.py"

# ── 7. Prompt user to inject A/B/C/D to AGENTS.md ──────────
echo ""
echo "[7/8] A/B/C/D handler for AGENTS.md..."
AGENTS_FILE="$WORKSPACE/AGENTS.md"
AGENTS_FRAGMENT="$SKILL_SCRIPTS/agents-append.md"

if [ ! -f "$AGENTS_FILE" ]; then
    echo "  ⚠ AGENTS.md not found at $AGENTS_FILE, skipping"
elif grep -q "A/B/C/D 响应处理.*self-improvement 闭环" "$AGENTS_FILE" 2>/dev/null; then
    echo "  ✓ A/B/C/D section already present in AGENTS.md"
else
    echo ""
    echo "  ⚠ ACTION REQUIRED: Please append the following to your AGENTS.md"
    echo "  ──────────────────────────────────────────────────────────"
    echo "  Copy the content from:"
    echo "    $AGENTS_FRAGMENT"
    echo "  And append it to:"
    echo "    $AGENTS_FILE"
    echo "  ──────────────────────────────────────────────────────────"
    echo ""
    echo "Press ENTER after you have added it, or 's' to skip: "
    read answer 2>/dev/null || answer=""
    if [ "$answer" = "s" ] || [ "$answer" = "S" ]; then
        echo "  ⚠ Skipped. You can add it manually later."
    else
        if grep -q "A/B/C/D 响应处理.*self-improvement 闭环" "$AGENTS_FILE" 2>/dev/null; then
            echo "  ✓ A/B/C/D section confirmed in AGENTS.md"
        else
            cat "$AGENTS_FRAGMENT" >> "$AGENTS_FILE"
            echo "  ✓ A/B/C/D section appended to AGENTS.md"
        fi
    fi
fi

# ── 8. Gateway restart reminder ─────────────────────────
echo ""
echo "[8/8] Gateway restart reminder..."
echo ""
echo "=== Installation complete ==="
echo ""
echo "⚠ Restart gateway to activate Hook:"
echo "   openclaw gateway restart"
echo ""
echo "Verify distill:"
echo "   bash $CANONICAL_DIR/distill.sh --check-only"
echo ""
echo "Check Cron status:"
echo "   openclaw cron list | grep self-improvement"
