#!/usr/bin/env python3
"""
Window Manager - Linux desktop window control via wmctrl and xdotool.

Requirements: Linux with wmctrl and/or xdotool installed
Dependencies: wmctrl, xdotool (install via package manager)
"""

import subprocess
import json
import sys
import os
import re
import shlex

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run_cmd


# ========== Safety: Input Validation ==========

DANGEROUS_CHARS_PATTERN = re.compile(r'[;&|`$(){}[\]!<>\n\r]')


def _validate_string(value, field_name="input"):
    """Validate that a string doesn't contain shell injection characters."""
    if not value:
        return True
    if DANGEROUS_CHARS_PATTERN.search(value):
        raise ValueError(
            f"ERROR: {field_name} contains forbidden shell characters."
        )
    return True


def _check_tool(tool):
    """Check if a tool is available."""
    result = subprocess.run(
        ["which", tool],
        capture_output=True,
        text=True
    )
    return result.returncode == 0


# Determine available tools
HAS_WMCTRL = _check_tool("wmctrl")
HAS_XDOTOOL = _check_tool("xdotool")


def list_windows():
    """List all visible windows with title, process name, position, and size."""
    if HAS_WMCTRL:
        stdout, stderr, code = run_cmd("wmctrl -l -p -G")
        if code == 0 and stdout:
            windows = []
            for line in stdout.split('\n'):
                if line.strip():
                    parts = line.split(None, 6)
                    if len(parts) >= 7:
                        wid, desktop, pid, x, y, w, h = parts[:7]
                        title = parts[6] if len(parts) > 6 else ""
                        windows.append({
                            "wid": wid,
                            "desktop": desktop,
                            "pid": pid,
                            "x": x,
                            "y": y,
                            "width": w,
                            "height": h,
                            "title": title
                        })
            return json.dumps(windows, indent=2)
        return "[]"
    
    elif HAS_XDOTOOL:
        stdout, stderr, code = run_cmd("xdotool search --onlyvisible --name ''")
        if code == 0 and stdout:
            windows = []
            for wid in stdout.strip().split('\n'):
                if wid:
                    name_out, _, _ = run_cmd(f"xdotool getwindowname {wid}")
                    pid_out, _, _ = run_cmd(f"xdotool getwindowpid {wid}")
                    geom_out, _, _ = run_cmd(f"xdotool getwindowgeometry {wid}")
                    windows.append({
                        "wid": wid.strip(),
                        "title": name_out.strip() if name_out else "",
                        "pid": pid_out.strip() if pid_out else "",
                        "geometry": geom_out.strip() if geom_out else ""
                    })
            return json.dumps(windows, indent=2)
        return "[]"
    
    return '{"error":"No window manager tools available (install wmctrl or xdotool)"}'


def activate_window(pid=None, title=None):
    """Bring a window to the foreground by PID or title substring."""
    if not (pid or title):
        return "ERROR: Provide --pid or --title"
    
    if HAS_XDOTOOL:
        if pid:
            stdout, stderr, code = run_cmd(f"xdotool search --onlyvisible --pid {pid} windowactivate")
        elif title:
            _validate_string(title, "window title")
            stdout, stderr, code = run_cmd(f"xdotool search --onlyvisible --name '*{title}*' windowactivate")
        
        if code == 0:
            return f"OK: Window activated"
        return stderr if stderr else "ERROR: Window not found"
    
    elif HAS_WMCTRL:
        if pid:
            stdout, stderr, code = run_cmd(f"wmctrl -F -a $(ps -p {pid} -o comm= 2>/dev/null || echo '')")
        elif title:
            _validate_string(title, "window title")
            stdout, stderr, code = run_cmd(f"wmctrl -F -a '{title}'")
        
        if code == 0:
            return f"OK: Window activated"
        return stderr if stderr else "ERROR: Window not found"
    
    return "ERROR: No window manager tools available"


def close_window(pid=None, title=None):
    """Close a window by PID or title substring."""
    if not (pid or title):
        return "ERROR: Provide --pid or --title"
    
    if HAS_XDOTOOL:
        if pid:
            stdout, stderr, code = run_cmd(f"xdotool search --onlyvisible --pid {pid} windowclose")
        elif title:
            _validate_string(title, "window title")
            stdout, stderr, code = run_cmd(f"xdotool search --onlyvisible --name '*{title}*' windowclose")
        
        if code == 0:
            return f"OK: Window closed"
        return stderr if stderr else "ERROR: Window not found"
    
    elif HAS_WMCTRL:
        if pid:
            stdout, stderr, code = run_cmd(f"wmctrl -F -c $(ps -p {pid} -o comm= 2>/dev/null || echo '')")
        elif title:
            _validate_string(title, "window title")
            stdout, stderr, code = run_cmd(f"wmctrl -F -c '{title}'")
        
        if code == 0:
            return f"OK: Window closed"
        return stderr if stderr else "ERROR: Window not found"
    
    return "ERROR: No window manager tools available"


def minimize_window(pid=None, title=None):
    """Minimize a window by PID or title substring."""
    if not (pid or title):
        return "ERROR: Provide --pid or --title"
    
    if HAS_XDOTOOL:
        if pid:
            stdout, stderr, code = run_cmd(f"xdotool search --onlyvisible --pid {pid} windowminimize")
        elif title:
            _validate_string(title, "window title")
            stdout, stderr, code = run_cmd(f"xdotool search --onlyvisible --name '*{title}*' windowminimize")
        
        if code == 0:
            return f"OK: Window minimized"
        return stderr if stderr else "ERROR: Window not found"
    
    elif HAS_WMCTRL:
        if title:
            _validate_string(title, "window title")
            stdout, stderr, code = run_cmd(f"wmctrl -F -b add,hidden '{title}'")
            if code == 0:
                return f"OK: Window minimized"
        return stderr if stderr else "ERROR: Window not found"
    
    return "ERROR: No window manager tools available"


def maximize_window(pid=None, title=None):
    """Maximize a window by PID or title substring."""
    if not (pid or title):
        return "ERROR: Provide --pid or --title"
    
    if HAS_XDOTOOL:
        if pid:
            stdout, stderr, code = run_cmd(f"xdotool search --onlyvisible --pid {pid} windowsize --maximize")
        elif title:
            _validate_string(title, "window title")
            stdout, stderr, code = run_cmd(f"xdotool search --onlyvisible --name '*{title}*' windowsize --maximize")
        
        if code == 0:
            return f"OK: Window maximized"
        return stderr if stderr else "ERROR: Window not found"
    
    elif HAS_WMCTRL:
        if title:
            _validate_string(title, "window title")
            stdout, stderr, code = run_cmd(f"wmctrl -F -b add,maximized_vert,maximized_horz '{title}'")
            if code == 0:
                return f"OK: Window maximized"
        return stderr if stderr else "ERROR: Window not found"
    
    return "ERROR: No window manager tools available"


def resize_window(pid=None, title=None, x=None, y=None, width=None, height=None):
    """Move and resize a window. All position/size parameters in pixels."""
    if not (pid or title):
        return "ERROR: Provide --pid or --title"
    if x is None or y is None or width is None or height is None:
        return "ERROR: Provide --x, --y, --width, --height"
    
    # Validate numeric parameters are reasonable
    for name, val in [("x", x), ("y", y), ("width", width), ("height", height)]:
        try:
            ival = int(val)
            if ival < 0 or ival > 100000:
                return f"ERROR: {name} value out of reasonable range: {val}"
        except (ValueError, TypeError):
            return f"ERROR: {name} must be an integer, got: {val}"
    
    if HAS_XDOTOOL:
        if pid:
            stdout, stderr, code = run_cmd(f"xdotool search --onlyvisible --pid {pid} windowmove {x} {y} windowsize {width} {height}")
        elif title:
            _validate_string(title, "window title")
            stdout, stderr, code = run_cmd(f"xdotool search --onlyvisible --name '*{title}*' windowmove {x} {y} windowsize {width} {height}")
        
        if code == 0:
            return f"OK: Window moved to ({x},{y}) size {width}x{height}"
        return stderr if stderr else "ERROR: Window not found"
    
    elif HAS_WMCTRL:
        if title:
            _validate_string(title, "window title")
            stdout, stderr, code = run_cmd(f"wmctrl -F -r '{title}' -e 0,{x},{y},{width},{height}")
            if code == 0:
                return f"OK: Window moved to ({x},{y}) size {width}x{height}"
        return stderr if stderr else "ERROR: Window not found"
    
    return "ERROR: No window manager tools available"


def send_keys(text, pid=None, title=None):
    """Send keystrokes to a window. Uses xdotool key/keycode format."""
    _validate_string(text, "text")
    
    if not (pid or title):
        return "ERROR: Provide --pid or --title"
    
    # Convert common key names to xdotool format
    key_map = {
        'ENTER': 'Return',
        'TAB': 'Tab',
        'ESC': 'Escape',
        'SPACE': 'space',
        'BACKSPACE': 'BackSpace',
        'BS': 'BackSpace',
        'DELETE': 'Delete',
        'DEL': 'Delete',
        'INSERT': 'Insert',
        'INS': 'Insert',
        'HOME': 'Home',
        'END': 'End',
        'PGUP': 'Prior',
        'PGDN': 'Next',
        'UP': 'Up',
        'DOWN': 'Down',
        'LEFT': 'Left',
        'RIGHT': 'Right',
    }
    
    # Process special key notation like {ENTER} or Ctrl+C
    processed_keys = []
    import re
    pattern = re.compile(r'\{([^}]+)\}|(\^[a-zA-Z])|(%)')
    
    def replace_key(match):
        if match.group(1):  # {KEY}
            key = match.group(1).upper()
            return key_map.get(key, key)
        elif match.group(2):  # ^C
            mod, key = 'ctrl+', match.group(2)[1].lower()
            return mod + key
        elif match.group(3):  # % (Alt)
            return 'alt+'
        return match.group(0)
    
    processed = pattern.sub(replace_key, text)
    
    if HAS_XDOTOOL:
        if pid:
            stdout, stderr, code = run_cmd(f"xdotool search --onlyvisible --pid {pid} windowactivate --sync key {processed}")
        elif title:
            _validate_string(title, "window title")
            stdout, stderr, code = run_cmd(f"xdotool search --onlyvisible --name '*{title}*' windowactivate --sync key {processed}")
        
        if code == 0:
            return f"OK: Sent keys"
        return stderr if stderr else "ERROR: Window not found"
    
    elif HAS_WMCTRL:
        # wmctrl doesn't support sending keys directly
        return "ERROR: send_keys requires xdotool"
    
    return "ERROR: No window manager tools available"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Window Manager - Control desktop windows (Linux)")
    sub = parser.add_subparsers(dest="action")

    p_list = sub.add_parser("list", help="List all visible windows")
    p_act = sub.add_parser("activate", help="Bring window to foreground")
    p_act.add_argument("--pid", type=int)
    p_act.add_argument("--title", type=str)
    p_close = sub.add_parser("close", help="Close a window")
    p_close.add_argument("--pid", type=int)
    p_close.add_argument("--title", type=str)
    p_min = sub.add_parser("minimize", help="Minimize a window")
    p_min.add_argument("--pid", type=int)
    p_min.add_argument("--title", type=str)
    p_max = sub.add_parser("maximize", help="Maximize a window")
    p_max.add_argument("--pid", type=int)
    p_max.add_argument("--title", type=str)
    p_resize = sub.add_parser("resize", help="Move and resize a window")
    p_resize.add_argument("--pid", type=int)
    p_resize.add_argument("--title", type=str)
    p_resize.add_argument("--x", type=int, required=True)
    p_resize.add_argument("--y", type=int, required=True)
    p_resize.add_argument("--width", type=int, required=True)
    p_resize.add_argument("--height", type=int, required=True)
    p_keys = sub.add_parser("send-keys", help="Send keystrokes to a window")
    p_keys.add_argument("--pid", type=int)
    p_keys.add_argument("--title", type=str)
    p_keys.add_argument("--text", type=str, required=True)

    args = parser.parse_args()

    if args.action == "list":
        print(list_windows())
    elif args.action == "activate":
        print(activate_window(args.pid, args.title))
    elif args.action == "close":
        print(close_window(args.pid, args.title))
    elif args.action == "minimize":
        print(minimize_window(args.pid, args.title))
    elif args.action == "maximize":
        print(maximize_window(args.pid, args.title))
    elif args.action == "resize":
        print(resize_window(args.pid, args.title, args.x, args.y, args.width, args.height))
    elif args.action == "send-keys":
        try:
            print(send_keys(args.text, args.pid, args.title))
        except ValueError as e:
            print(str(e))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
