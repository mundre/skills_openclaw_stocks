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
TIMEOUT=30

echo "=== Gateway Rescue Test ==="
echo "Will stop gateway and wait up to ${TIMEOUT}s for auto-recovery..."
echo ""

# Stop the service
case "$PLATFORM" in
    linux|wsl2)
        if ! systemctl is-active openclaw-gateway.service &>/dev/null; then
            echo "ERROR: Service is not running. Install first." >&2
            exit 1
        fi
        echo "Stopping service..."
        sudo systemctl stop openclaw-gateway.service
        ;;
    macos)
        if ! launchctl list | grep -q openclaw; then
            echo "ERROR: Service is not loaded. Install first." >&2
            exit 1
        fi
        echo "Killing gateway process..."
        pkill -f "openclaw gateway" 2>/dev/null || true
        ;;
    *)
        echo "ERROR: Unsupported platform $(uname -s)" >&2
        exit 1
        ;;
esac

echo "Waiting for recovery (timeout: ${TIMEOUT}s)..."
ELAPSED=0
RECOVERED=false

while [ "$ELAPSED" -lt "$TIMEOUT" ]; do
    sleep 2
    ELAPSED=$((ELAPSED + 2))

    case "$PLATFORM" in
        linux|wsl2)
            if systemctl is-active openclaw-gateway.service &>/dev/null; then
                RECOVERED=true
                break
            fi
            ;;
        macos)
            if pgrep -f "openclaw gateway" &>/dev/null; then
                RECOVERED=true
                break
            fi
            ;;
    esac
    echo "  ${ELAPSED}s... still waiting"
done

echo ""
if [ "$RECOVERED" = true ]; then
    echo "✅ Gateway recovered automatically in ${ELAPSED}s!"
else
    echo "❌ Gateway did NOT recover within ${TIMEOUT}s."
    echo "   Check status: bash $(dirname "$0")/status.sh"
    exit 1
fi
