#!/usr/bin/env bash
set -euo pipefail

detect_platform() {
    case "$(uname -s)" in
        Linux)
            grep -qi microsoft /proc/version 2>/dev/null && echo "wsl2" || echo "linux"
            ;;
        Darwin) echo "macos" ;;
        *) echo "unsupported" ;;
    esac
}

PLATFORM="$(detect_platform)"

case "$PLATFORM" in
    linux|wsl2)
        SERVICE_FILE="/etc/systemd/system/openclaw-gateway.service"
        if [ -f "$SERVICE_FILE" ]; then
            echo "Stopping and disabling systemd service..."
            sudo systemctl stop openclaw-gateway.service 2>/dev/null || true
            sudo systemctl disable openclaw-gateway.service 2>/dev/null || true
            sudo rm -f "$SERVICE_FILE"
            sudo systemctl daemon-reload
            echo "✅ systemd service uninstalled."
        else
            echo "No systemd service found."
        fi
        ;;
    macos)
        PLIST_FILE="$HOME/Library/LaunchAgents/com.openclaw.gateway.plist"
        if [ -f "$PLIST_FILE" ]; then
            echo "Unloading and removing launchd plist..."
            launchctl unload "$PLIST_FILE" 2>/dev/null || true
            rm -f "$PLIST_FILE"
            echo "✅ launchd plist uninstalled."
        else
            echo "No launchd plist found."
        fi
        ;;
    *)
        echo "ERROR: Unsupported platform $(uname -s)" >&2
        exit 1
        ;;
esac
