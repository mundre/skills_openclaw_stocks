#!/bin/bash
# wechat_read.sh — Read chat history from a WeChat contact/group via macOS desktop client
# Usage:
#   Phase 1: wechat_read.sh <contact> --enter
#   Phase 2: wechat_read.sh <contact> --capture <x>,<y> [--pages N]
#
# Requires: macOS Accessibility + Screen Recording permission, cliclick

set -euo pipefail

CONTACT="${1:?Usage: wechat_read.sh <contact> --enter | --capture <x>,<y> [--pages N]}"
SEARCH_SCREENSHOT="/tmp/wechat_read_search.png"
PAGE_PREFIX="/tmp/wechat_read_p"

# ── Tunable parameters ──────────────────────────────────────────────
# Chat content area: x, y, width, height (screen-absolute)
# Based on window at {50,50} size {1200,800}
# Excludes sidebar (~320px), title bar (~40px), input box (~160px)
CHAT_X=370
CHAT_Y=90
CHAT_W=830
CHAT_H=620

# Scroll tuning
SCROLL_STEPS=8           # arrow-up keystrokes per page
SCROLL_DELAY=0.04        # seconds between keystrokes
POST_SCROLL_WAIT=0.6     # seconds to wait after scroll before capture

# Focus click position (center of chat content area)
FOCUS_X=750
FOCUS_Y=400
# ─────────────────────────────────────────────────────────────────────

log() { echo "[wechat-read] $*"; }
fail() { echo "[wechat-read] FAIL: $*" >&2; exit 1; }

command -v cliclick >/dev/null || fail "cliclick not found. Install: brew install cliclick"

clip_write() {
    local text="$1"
    printf '%s' "$text" > /tmp/wechat_read_clip.txt
    osascript -e 'set the clipboard to (read POSIX file "/tmp/wechat_read_clip.txt" as "utf8")'
}

activate_and_resize() {
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
}

do_search() {
    activate_and_resize

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
    screencapture -x -R "50,50,500,600" "$SEARCH_SCREENSHOT" || fail "Cannot capture screenshot"
    log "Screenshot saved: $SEARCH_SCREENSHOT"
}

capture_page() {
    local page_num="$1"
    local outfile="${PAGE_PREFIX}${page_num}.png"
    screencapture -x -R "${CHAT_X},${CHAT_Y},${CHAT_W},${CHAT_H}" "$outfile" \
        || fail "Cannot capture page $page_num"
    echo "$outfile"
}

scroll_up_once() {
    # Generate the AppleScript to press arrow-up SCROLL_STEPS times
    local repeat_block=""
    repeat_block="tell application \"System Events\"
        tell process \"WeChat\"
            repeat ${SCROLL_STEPS} times
                key code 126
                delay ${SCROLL_DELAY}
            end repeat
        end tell
    end tell"
    osascript -e "$repeat_block" || fail "Scroll failed"
    sleep "$POST_SCROLL_WAIT"
}

file_checksum() {
    md5 -q "$1" 2>/dev/null || md5sum "$1" | cut -d' ' -f1
}

do_capture() {
    local coords="$1"
    local max_pages="$2"
    local x="${coords%,*}"
    local y="${coords#*,}"

    log "Clicking contact at ($x, $y)..."
    cliclick c:"$x","$y" || fail "cliclick failed"
    sleep 1.5

    # Close search overlay by pressing Escape
    osascript -e '
    tell application "System Events"
        tell process "WeChat"
            key code 53
        end tell
    end tell'
    sleep 0.5

    # Click chat content area to ensure it has focus for scrolling
    log "Focusing chat content area..."
    cliclick c:"$FOCUS_X","$FOCUS_Y" || true
    sleep 0.3

    # Capture first page (current view = most recent messages)
    log "Capturing page 1 / $max_pages (latest messages)..."
    local outfile
    outfile=$(capture_page 1)
    local prev_checksum
    prev_checksum=$(file_checksum "$outfile")
    log "  Saved: $outfile"

    # Scroll up and capture additional pages
    local page=2
    while [ "$page" -le "$max_pages" ]; do
        log "Scrolling up..."
        scroll_up_once

        log "Capturing page $page / $max_pages..."
        outfile=$(capture_page "$page")

        # Check if page changed (scroll-stop detection)
        local cur_checksum
        cur_checksum=$(file_checksum "$outfile")
        if [ "$cur_checksum" = "$prev_checksum" ]; then
            log "[REACHED_TOP] Page $page is identical to page $((page - 1)). Chat top reached."
            rm -f "$outfile"  # Remove duplicate
            page=$((page - 1))
            break
        fi
        prev_checksum="$cur_checksum"
        log "  Saved: $outfile"
        page=$((page + 1))
    done

    local total=$((page - 1))
    [ "$page" -le "$max_pages" ] && total=$page  # adjust if reached top

    echo ""
    log "Capture complete. $total page(s) saved."
    log "Files: ${PAGE_PREFIX}1.png through ${PAGE_PREFIX}${total}.png"
    log ""
    log "Page order: p1 = newest (bottom of chat), p${total} = oldest (top of chat)"
    log ""
    log "Next: Agent reads all page screenshots, performs OCR, deduplicates"
    log "overlapping content between adjacent pages, and assembles the"
    log "conversation in chronological order (reverse page order)."
}

# ── Parse arguments ──────────────────────────────────────────────────
MODE=""
CLICK_COORDS=""
MAX_PAGES=3

shift  # skip CONTACT

while [[ $# -gt 0 ]]; do
    case "$1" in
        --enter)
            MODE="enter"; shift ;;
        --capture)
            MODE="capture"; CLICK_COORDS="$2"; shift 2 ;;
        --pages)
            MAX_PAGES="$2"; shift 2 ;;
        *)
            fail "Unknown argument: $1" ;;
    esac
done

[[ -z "$MODE" ]] && fail "Specify --enter or --capture <x>,<y>"

# ── Clean up old captures ───────────────────────────────────────────
rm -f /tmp/wechat_read_p*.png /tmp/wechat_read_search.png 2>/dev/null || true

case "$MODE" in
    enter)
        do_search
        log "Phase 1 complete. Analyze $SEARCH_SCREENSHOT, find target row, then run:"
        log "  wechat_read.sh \"$CONTACT\" --capture <x>,<y> [--pages N]"
        ;;
    capture)
        [[ -z "$CLICK_COORDS" ]] && fail "Coordinates required for --capture"
        do_capture "$CLICK_COORDS" "$MAX_PAGES"
        ;;
esac
