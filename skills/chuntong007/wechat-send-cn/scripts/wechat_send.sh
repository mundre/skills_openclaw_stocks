#!/bin/bash
# wechat_send.sh — Send a message to a WeChat contact/group via macOS desktop client
# Usage:
#   Phase 1: wechat_send.sh <contact> --search-only
#   Phase 2: wechat_send.sh <contact> <message> --send-only <x>,<y>
#
# Requires: macOS Accessibility permission, cliclick (brew install cliclick)

set -euo pipefail

CONTACT="${1:?Usage: wechat_send.sh <contact> <message> [--search-only | --send-only x,y]}"
SCREENSHOT_PATH="/tmp/wechat_search_dropdown.png"

log() { echo "[wechat-send] $*"; }
fail() { echo "[wechat-send] FAIL: $*" >&2; exit 1; }

command -v cliclick >/dev/null || fail "cliclick not found. Install: brew install cliclick"

clip_write() {
    # Write text to clipboard via temp file (safe for CJK + multiline)
    local text="$1"
    printf '%s' "$text" > /tmp/wechat_send_clip.txt
    osascript -e 'set the clipboard to (read POSIX file "/tmp/wechat_send_clip.txt" as "utf8")'
}

do_search() {
    log "Activating WeChat..."
    osascript -e 'tell application "WeChat" to activate' || fail "Cannot activate WeChat"
    sleep 1

    log "Setting window geometry..."
    osascript -e '
    tell application "System Events"
        tell process "WeChat"
            set position of window 1 to {50, 50}
            set size of window 1 to {1200, 800}
        end tell
    end tell' || fail "Cannot resize window"
    sleep 0.5

    log "Opening search..."
    osascript -e '
    tell application "System Events"
        tell process "WeChat"
            key code 53
            delay 0.3
            keystroke "f" using command down
        end tell
    end tell' || fail "Cannot trigger search"
    sleep 0.8

    log "Searching for contact: $CONTACT"
    clip_write "$CONTACT"
    osascript -e '
    tell application "System Events"
        tell process "WeChat"
            keystroke "a" using command down
            delay 0.2
            keystroke "v" using command down
        end tell
    end tell' || fail "Cannot paste contact name"
    sleep 1.5

    log "Capturing search dropdown..."
    screencapture -x -R "50,50,500,600" "$SCREENSHOT_PATH" || fail "Cannot capture screenshot"
    log "Screenshot saved: $SCREENSHOT_PATH"
}

do_click_and_send() {
    local coords="$1"
    local message="$2"
    local x="${coords%,*}"
    local y="${coords#*,}"

    log "Clicking contact at ($x, $y) via cliclick..."
    cliclick c:"$x","$y" || fail "cliclick failed"
    sleep 1.5

    log "Pasting message..."
    clip_write "$message"
    cliclick c:700,650
    sleep 0.3
    osascript -e '
    tell application "System Events"
        tell process "WeChat"
            keystroke "v" using command down
        end tell
    end tell' || fail "Cannot paste message"
    sleep 0.5

    log "Sending..."
    osascript -e '
    tell application "System Events"
        tell process "WeChat"
            key code 36
        end tell
    end tell' || fail "Cannot send"
    sleep 0.5

    log "Done."
}

# Parse args
MODE="search-only"
MESSAGE=""
CLICK_COORDS=""

shift # skip CONTACT

while [[ $# -gt 0 ]]; do
    case "$1" in
        --search-only)
            MODE="search-only"; shift ;;
        --send-only)
            MODE="send-only"; CLICK_COORDS="$2"; shift 2 ;;
        *)
            [[ -z "$MESSAGE" ]] && MESSAGE="$1"; shift ;;
    esac
done

case "$MODE" in
    search-only)
        do_search
        log "Phase 1 complete. Analyze $SCREENSHOT_PATH, find target row, then run:"
        log "  wechat_send.sh \"$CONTACT\" \"<message>\" --send-only <x>,<y>"
        ;;
    send-only)
        [[ -z "$MESSAGE" ]] && fail "Message required for --send-only"
        [[ -z "$CLICK_COORDS" ]] && fail "Coordinates required for --send-only"
        do_click_and_send "$CLICK_COORDS" "$MESSAGE"
        ;;
esac
