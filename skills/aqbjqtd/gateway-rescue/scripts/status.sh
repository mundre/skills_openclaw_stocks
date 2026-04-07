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
        echo "=== systemd service status ==="
        systemctl status openclaw-gateway.service --no-pager 2>/dev/null || echo "Service not installed."
        echo ""
        echo "=== Recent logs (last 20 lines) ==="
        journalctl -u openclaw-gateway.service --no-pager -n 20 2>/dev/null || echo "No logs available."
        ;;
    macos)
        echo "=== launchd plist status ==="
        if [ -f "$HOME/Library/LaunchAgents/com.openclaw.gateway.plist" ]; then
            launchctl list | grep openclaw || echo "Not loaded."
            echo ""
            echo "=== Recent stdout log (last 20 lines) ==="
            tail -20 "$HOME/.openclaw/logs/launchd-stdout.log" 2>/dev/null || echo "No stdout log."
            echo ""
            echo "=== Recent stderr log (last 20 lines) ==="
            tail -20 "$HOME/.openclaw/logs/launchd-stderr.log" 2>/dev/null || echo "No stderr log."
        else
            echo "No launchd plist found."
        fi
        ;;
    *)
        echo "ERROR: Unsupported platform $(uname -s)" >&2
        exit 1
        ;;
esac
