#!/usr/bin/env bash
set -euo pipefail

# Resolve paths
OPENCLAW_DIR="${OPENCLAW_DIR:-$HOME/.openclaw}"
OPENCLAW_BIN="$(command -v openclaw 2>/dev/null || true)"

# Try nvm if openclaw not in PATH
if [ -z "$OPENCLAW_BIN" ]; then
    NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
    [ -s "$NVM_DIR/nvm.sh" ] && source "$NVM_DIR/nvm.sh"
    OPENCLAW_BIN="$(command -v openclaw 2>/dev/null || true)"
fi

if [ -z "$OPENCLAW_BIN" ]; then
    echo "ERROR: openclaw binary not found. Ensure it's installed and in PATH." >&2
    exit 1
fi

echo "Using openclaw: $OPENCLAW_BIN"

# Build PATH with nvm node
NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
NODE_BIN=""
if [ -s "$NVM_DIR/nvm.sh" ]; then
    source "$NVM_DIR/nvm.sh"
    NODE_BIN="$(dirname "$(which node 2>/dev/null)" 2>/dev/null || true)"
fi
FULL_PATH="${NODE_BIN:+$NODE_BIN:}/usr/local/bin:/usr/bin:/bin"

detect_platform() {
    local uname_s="$(uname -s)"
    case "$uname_s" in
        Linux)
            # Check for WSL2
            if grep -qi microsoft /proc/version 2>/dev/null; then
                echo "wsl2"
            else
                echo "linux"
            fi
            ;;
        Darwin) echo "macos" ;;
        *) echo "unsupported" ;;
    esac
}

PLATFORM="$(detect_platform)"
echo "Detected platform: $PLATFORM"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
UNITS_DIR="$SCRIPT_DIR/../units"

case "$PLATFORM" in
    linux|wsl2)
        SERVICE_FILE="/etc/systemd/system/openclaw-gateway.service"
        echo "Installing systemd service..."

        sed -e "s|__OPENCLAW_BIN__|$OPENCLAW_BIN|g" \
            -e "s|__OPENCLAW_DIR__|$OPENCLAW_DIR|g" \
            -e "s|__PATH__|$FULL_PATH|g" \
            -e "s|__HOME__|$HOME|g" \
            "$UNITS_DIR/openclaw-gateway.service" | sudo tee "$SERVICE_FILE" > /dev/null

        sudo systemctl daemon-reload
        sudo systemctl enable openclaw-gateway.service
        sudo systemctl start openclaw-gateway.service
        echo "✅ systemd service installed and started."
        ;;
    macos)
        PLIST_FILE="$HOME/Library/LaunchAgents/com.openclaw.gateway.plist"
        mkdir -p "$OPENCLAW_DIR/logs"

        echo "Installing launchd plist..."

        sed -e "s|__OPENCLAW_BIN__|$OPENCLAW_BIN|g" \
            -e "s|__OPENCLAW_DIR__|$OPENCLAW_DIR|g" \
            -e "s|__PATH__|$FULL_PATH|g" \
            -e "s|__HOME__|$HOME|g" \
            "$UNITS_DIR/com.openclaw.gateway.plist" > "$PLIST_FILE"

        launchctl load "$PLIST_FILE"
        echo "✅ launchd plist installed and loaded."
        ;;
    *)
        echo "ERROR: Unsupported platform $(uname -s)" >&2
        exit 1
        ;;
esac
