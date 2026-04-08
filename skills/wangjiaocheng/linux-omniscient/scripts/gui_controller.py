#!/usr/bin/env python3
"""
GUI Controller - Mouse, keyboard, screenshot, and visual control (Linux).

Capabilities:
  - Mouse: move, click, double-click, right-click, drag, scroll, get position
  - Keyboard: type text, press hotkeys, key combinations
  - Screenshot: full screen, region, save to file
  - OCR: extract text from screen regions

Requirements: Linux with X11, Python 3.x
Dependencies: pyautogui (auto-installed), pillow (auto-installed), 
              scrot/gnome-screenshot for screenshots, 
              xdotool for some operations
"""

import sys
import os
import json
import subprocess
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run_cmd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOT_DIR = os.path.join(SCRIPT_DIR, "screenshots")


def _check_tool(tool):
    """Check if a tool is available."""
    result = subprocess.run(
        ["which", tool],
        capture_output=True,
        text=True
    )
    return result.returncode == 0


HAS_XDOTOOL = _check_tool("xdotool")
HAS_SCROT = _check_tool("scrot")
HAS_GNOME_SCREENSHOT = _check_tool("gnome-screenshot")
HAS_IMAGEMAGICK = _check_tool("import")  # ImageMagick


# ========== Dependency Management ==========

def _ensure_deps(modules=None):
    """Ensure required Python packages are installed. Returns True on success."""
    if modules is None:
        modules = []
    missing = []
    for mod in modules:
        try:
            __import__(mod)
        except ImportError:
            missing.append(mod)
    if not missing:
        return True
    pkg_map = {
        "pyautogui": "pyautogui",
        "PIL": "pillow",
        "pytesseract": "pytesseract",
    }
    pkgs = [pkg_map.get(m, m) for m in missing]
    pip = sys.executable
    if not pip:
        return False
    cmd = [pip, "-m", "pip", "install"] + pkgs
    print(f"INFO: Installing missing packages: {', '.join(pkgs)}", file=sys.stderr)
    try:
        subprocess.run(cmd, capture_output=True, timeout=120)
        return True
    except Exception as e:
        print(f"ERROR: Failed to install packages: {e}", file=sys.stderr)
        return False


def _get_gui():
    """Import and return pyautogui, installing if needed."""
    _ensure_deps(["pyautogui", "PIL"])
    try:
        import pyautogui
        pyautogui.FAILSAFE = True
        return pyautogui
    except ImportError:
        print("ERROR: pyautogui not available. Run: pip install pyautogui pillow")
        sys.exit(1)


# ========== Mouse Control ==========

def mouse_move(x, y, duration=0.3):
    """Move mouse to absolute screen coordinates (x, y)."""
    gui = _get_gui()
    gui.moveTo(x, y, duration=duration)
    print(f"OK: Mouse moved to ({x}, {y})")


def mouse_click(x=None, y=None, button="left", clicks=1, duration=0.2):
    """Click at position. Uses current position if x,y not provided."""
    gui = _get_gui()
    if x is not None and y is not None:
        gui.moveTo(x, y, duration=duration)
    if clicks == 1:
        gui.click(button=button)
    else:
        gui.click(button=button, clicks=clicks, interval=0.1)
    pos = gui.position()
    print(f"OK: {button} click x{clicks} at ({pos.x}, {pos.y})")


def mouse_right_click(x=None, y=None):
    """Right-click at position."""
    mouse_click(x, y, button="right")


def mouse_double_click(x=None, y=None):
    """Double-click at position."""
    mouse_click(x, y, clicks=2)


def mouse_drag(start_x, start_y, end_x, end_y, duration=0.5, button="left"):
    """Drag from one position to another."""
    gui = _get_gui()
    gui.moveTo(start_x, start_y, duration=0.2)
    gui.dragTo(end_x, end_y, duration=duration, button=button)
    print(f"OK: Dragged from ({start_x},{start_y}) to ({end_x},{end_y})")


def mouse_scroll(x=None, y=None, clicks=5, direction="up"):
    """Scroll mouse wheel. Positive clicks=up, negative=down."""
    gui = _get_gui()
    if x is not None and y is not None:
        gui.moveTo(x, y, duration=0.2)
    amount = clicks if direction == "up" else -clicks
    gui.scroll(amount)
    pos = gui.position()
    print(f"OK: Scrolled {direction} {abs(clicks)} clicks at ({pos.x}, {pos.y})")


def mouse_position():
    """Get current mouse position."""
    gui = _get_gui()
    pos = gui.position()
    size = gui.size()
    result = json.dumps({
        "x": pos.x,
        "y": pos.y,
        "screen_width": size.width,
        "screen_height": size.height
    })
    print(result)


# ========== Keyboard Control ==========

def keyboard_type(text, interval=0.02):
    """Type text character by character at current cursor position."""
    gui = _get_gui()
    gui.typewrite(text, interval=interval)
    print(f"OK: Typed {len(text)} characters")


def keyboard_press(keys):
    """Press a key or key combination (e.g., 'ctrl', 'alt+tab', 'ctrl+shift+esc')."""
    gui = _get_gui()
    gui.hotkey(*keys.split("+"))
    print(f"OK: Pressed {keys}")


def keyboard_hotkey(*key_list):
    """Press multiple keys simultaneously. Keys as separate args."""
    gui = _get_gui()
    gui.hotkey(*key_list)
    print(f"OK: Pressed {'+'.join(key_list)}")


def keyboard_key_down(key):
    """Hold down a key."""
    gui = _get_gui()
    gui.keyDown(key)
    print(f"OK: Key down: {key}")


def keyboard_key_up(key):
    """Release a held key."""
    gui = _get_gui()
    gui.keyUp(key)
    print(f"OK: Key up: {key}")


# ========== Screenshot ==========

def _get_screenshot_tool():
    """Determine the best available screenshot tool."""
    if HAS_SCROT:
        return "scrot"
    elif HAS_GNOME_SCREENSHOT:
        return "gnome-screenshot"
    elif HAS_IMAGEMAGICK:
        return "imagemagick"
    return None


def screenshot_full(filepath=None):
    """Take a full screen screenshot. Save to file if path provided."""
    tool = _get_screenshot_tool()
    
    if filepath:
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    else:
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        filepath = os.path.join(SCREENSHOT_DIR, "screenshot.png")
    
    if tool == "scrot":
        out, err, code = run_cmd(f"scrot '{filepath}'")
    elif tool == "gnome-screenshot":
        out, err, code = run_cmd(f"gnome-screenshot -f '{filepath}'")
    elif tool == "imagemagick":
        out, err, code = run_cmd(f"import -window root '{filepath}'")
    else:
        # Fallback to pyautogui
        gui = _get_gui()
        img = gui.screenshot()
        img.save(filepath)
        print(f"OK: Screenshot saved to {filepath}")
        print(f"INFO: File size: {os.path.getsize(filepath)} bytes")
        return
    
    if code == 0:
        print(f"OK: Screenshot saved to {filepath}")
        print(f"INFO: File size: {os.path.getsize(filepath)} bytes")
    else:
        print(f"ERROR: {err}" if err else "ERROR: Failed to capture screenshot")


def screenshot_region(x, y, width, height, filepath=None):
    """Take a screenshot of a specific region."""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    if filepath:
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    else:
        filepath = os.path.join(SCREENSHOT_DIR, "region.png")
    
    tool = _get_screenshot_tool()
    
    if tool == "scrot":
        out, err, code = run_cmd(f"scrot -a {x},{y},{width},{height} '{filepath}'")
    elif tool == "imagemagick":
        out, err, code = run_cmd(f"import -window root -crop {width}x{height}+{x}+{y} '{filepath}'")
    else:
        # Fallback to pyautogui
        gui = _get_gui()
        img = gui.screenshot(region=(x, y, width, height))
        img.save(filepath)
        print(f"OK: Region screenshot saved to {filepath}")
        return
    
    if code == 0:
        print(f"OK: Region screenshot saved to {filepath}")
    else:
        print(f"ERROR: {err}" if err else "ERROR: Failed to capture region screenshot")


def screenshot_active_window(filepath=None):
    """Take a screenshot of the active (foreground) window."""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    if filepath:
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    else:
        filepath = os.path.join(SCREENSHOT_DIR, "window.png")
    
    # Get active window ID with xdotool
    if HAS_XDOTOOL:
        out, _, _ = run_cmd("xdotool getactivewindow")
        if out:
            wid = out.strip()
            # Try using xdotool to capture
            out2, err, code = run_cmd(f"xdotool getactivewindow windowcapture --png '{filepath}'")
            if code == 0:
                print(f"OK: Window screenshot saved to {filepath}")
                return
    
    # Fallback: use scrot with active window mode
    if HAS_SCROT:
        out, err, code = run_cmd(f"scrot -u '{filepath}'")
        if code == 0:
            print(f"OK: Window screenshot saved to {filepath}")
            return
    
    # Fallback: capture focused window using imagemagick
    if HAS_IMAGEMAGICK and HAS_XDOTOOL:
        out, _, _ = run_cmd("xdotool getactivewindow")
        if out:
            wid = out.strip()
            out2, err, code = run_cmd(f"import -window {wid} '{filepath}'")
            if code == 0:
                print(f"OK: Window screenshot saved to {filepath}")
                return
    
    print("ERROR: Could not capture active window")


def get_screen_size():
    """Get screen resolution."""
    gui = _get_gui()
    size = gui.size()
    print(json.dumps({"width": size.width, "height": size.height}))


# ========== Visual / OCR ==========

def ocr_region(x, y, width, height, lang="eng+chi_sim"):
    """Extract text from a screen region using Tesseract OCR."""
    _ensure_deps(["pytesseract"])
    
    # First take a screenshot of the region
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    tmp_path = os.path.join(SCREENSHOT_DIR, "ocr_temp.png")
    
    tool = _get_screenshot_tool()
    if tool == "scrot":
        run_cmd(f"scrot -a {x},{y},{width},{height} '{tmp_path}'")
    elif tool == "imagemagick":
        run_cmd(f"import -window root -crop {width}x{height}+{x}+{y} '{tmp_path}'")
    else:
        gui = _get_gui()
        img = gui.screenshot(region=(x, y, width, height))
        img.save(tmp_path)
    
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(tmp_path)
        text = pytesseract.image_to_string(img, lang=lang)
        text = text.strip()
        if text:
            print(f"OK: OCR result:\n{text}")
        else:
            print("OK: OCR result: (no text detected)")
    except ImportError:
        print("ERROR: pytesseract not installed. Run: pip install pytesseract")
        print("INFO: Also ensure Tesseract OCR engine is installed: sudo apt install tesseract-ocr tesseract-ocr-chi-sim")
    except Exception as e:
        print(f"ERROR: OCR failed: {e}")


def ocr_full(lang="eng+chi_sim"):
    """OCR the entire screen."""
    gui = _get_gui()
    size = gui.size()
    ocr_region(0, 0, size.width, size.height, lang)


def find_image(template_path, confidence=0.9):
    """Find an image template on screen. Returns position or error."""
    import glob
    
    # Search in screenshots dir if relative path
    if not os.path.isabs(template_path):
        paths = glob.glob(os.path.join(SCREENSHOT_DIR, template_path))
        if not paths:
            paths = glob.glob(os.path.join(SCRIPT_DIR, "..", "assets", template_path))
        if paths:
            template_path = paths[0]

    if not os.path.exists(template_path):
        print(f"ERROR: Template image not found: {template_path}")
        return

    gui = _get_gui()
    try:
        location = gui.locateOnScreen(template_path, confidence=confidence)
        if location:
            center = gui.center(location)
            result = json.dumps({
                "found": True,
                "x": center.x,
                "y": center.y,
                "width": location.width,
                "height": location.height
            })
            print(f"OK: Found template at center ({center.x}, {center.y})")
            print(result)
        else:
            print(f"OK: Template not found on screen (confidence threshold: {confidence})")
    except Exception as e:
        print(f"ERROR: {e}")


def click_image(template_path, button="left", confidence=0.9, offset_x=0, offset_y=0):
    """Find an image on screen and click it."""
    import glob
    if not os.path.isabs(template_path):
        paths = glob.glob(os.path.join(SCREENSHOT_DIR, template_path))
        if paths:
            template_path = paths[0]

    if not os.path.exists(template_path):
        print(f"ERROR: Template image not found: {template_path}")
        return

    gui = _get_gui()
    try:
        location = gui.locateOnScreen(template_path, confidence=confidence)
        if location:
            center = gui.center(location)
            target_x = center.x + offset_x
            target_y = center.y + offset_y
            gui.click(x=target_x, y=target_y, button=button)
            print(f"OK: Clicked template at ({target_x}, {target_y})")
        else:
            print(f"ERROR: Template not found on screen")
    except Exception as e:
        print(f"ERROR: {e}")


def find_color(target_color, region=None):
    """Find all pixels matching a color on screen. Color as (R,G,B) or hex."""
    gui = _get_gui()
    if isinstance(target_color, str):
        target_color = target_color.lstrip("#")
        target_color = tuple(int(target_color[i:i+2], 16) for i in (0, 2, 4))

    if region:
        img = gui.screenshot(region=region)
        offset_x, offset_y = region[0], region[1]
    else:
        img = gui.screenshot()
        offset_x, offset_y = 0, 0

    width, height = img.size
    matches = []
    tolerance = 10

    step = 2
    for y_pos in range(0, height, step):
        for x_pos in range(0, width, step):
            pixel = img.getpixel((x_pos, y_pos))
            if all(abs(pixel[i] - target_color[i]) <= tolerance for i in range(3)):
                matches.append({
                    "x": x_pos + offset_x,
                    "y": y_pos + offset_y
                })
                if len(matches) >= 50:
                    break
        if len(matches) >= 50:
            break

    if matches:
        print(f"OK: Found {len(matches)} pixels matching color {target_color}")
        print(f"INFO: First match at ({matches[0]['x']}, {matches[0]['y']})")
    else:
        print(f"OK: No pixels found matching color {target_color}")
    return matches


def pixel_color(x, y):
    """Get the color of a pixel at (x, y)."""
    gui = _get_gui()
    pixel = gui.pixel(x, y)
    print(json.dumps({
        "x": x,
        "y": y,
        "RGB": [pixel.red, pixel.green, pixel.blue],
        "hex": f"#{pixel.red:02X}{pixel.green:02X}{pixel.blue:02X}"
    }))


def list_screenshots():
    """List previously saved screenshots."""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    files = []
    for f in sorted(os.listdir(SCREENSHOT_DIR)):
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
            fp = os.path.join(SCREENSHOT_DIR, f)
            files.append({
                "name": f,
                "path": fp,
                "size_bytes": os.path.getsize(fp)
            })
    if files:
        print(json.dumps(files, ensure_ascii=False, indent=2))
    else:
        print("OK: No screenshots saved yet")


# ========== Main CLI ==========

def main():
    parser = argparse.ArgumentParser(description="GUI Controller (Linux) - Mouse, Keyboard, Screenshot, OCR")
    sub = parser.add_subparsers(dest="category")

    # Mouse
    p_mouse = sub.add_parser("mouse", help="Mouse control")
    mouse_sub = p_mouse.add_subparsers(dest="action")
    mouse_sub.add_parser("position", help="Get current mouse position")

    m_move = mouse_sub.add_parser("move", help="Move mouse")
    m_move.add_argument("--x", type=int, required=True)
    m_move.add_argument("--y", type=int, required=True)
    m_move.add_argument("--duration", type=float, default=0.3)

    m_click = mouse_sub.add_parser("click", help="Left click")
    m_click.add_argument("--x", type=int)
    m_click.add_argument("--y", type=int)

    m_rclick = mouse_sub.add_parser("right-click", help="Right click")
    m_rclick.add_argument("--x", type=int)
    m_rclick.add_argument("--y", type=int)

    m_dclick = mouse_sub.add_parser("double-click", help="Double click")
    m_dclick.add_argument("--x", type=int)
    m_dclick.add_argument("--y", type=int)

    m_drag = mouse_sub.add_parser("drag", help="Drag from A to B")
    m_drag.add_argument("--start-x", type=int, required=True)
    m_drag.add_argument("--start-y", type=int, required=True)
    m_drag.add_argument("--end-x", type=int, required=True)
    m_drag.add_argument("--end-y", type=int, required=True)
    m_drag.add_argument("--duration", type=float, default=0.5)

    m_scroll = mouse_sub.add_parser("scroll", help="Scroll")
    m_scroll.add_argument("--x", type=int)
    m_scroll.add_argument("--y", type=int)
    m_scroll.add_argument("--clicks", type=int, default=5)
    m_scroll.add_argument("--direction", choices=["up", "down"], default="up")

    # Keyboard
    p_key = sub.add_parser("keyboard", help="Keyboard control")
    key_sub = p_key.add_subparsers(dest="action")
    key_type = key_sub.add_parser("type", help="Type text")
    key_type.add_argument("--text", type=str, required=True)
    key_press = key_sub.add_parser("press", help="Press key/combo")
    key_press.add_argument("--keys", type=str, required=True)
    key_down = key_sub.add_parser("key-down", help="Key down")
    key_down.add_argument("--key", type=str, required=True)
    key_up = key_sub.add_parser("key-up", help="Key up")
    key_up.add_argument("--key", type=str, required=True)

    # Screenshot
    p_shot = sub.add_parser("screenshot", help="Screenshot")
    shot_sub = p_shot.add_subparsers(dest="action")
    shot_sub.add_parser("full", help="Full screen")
    shot_sub.add_parser("active-window", help="Active window")
    shot_reg = shot_sub.add_parser("region", help="Region")
    shot_reg.add_argument("--x", type=int, required=True)
    shot_reg.add_argument("--y", type=int, required=True)
    shot_reg.add_argument("--width", type=int, required=True)
    shot_reg.add_argument("--height", type=int, required=True)
    shot_sub.add_parser("list", help="List screenshots")
    shot_sub.add_parser("size", help="Get screen size")

    # Visual/OCR
    p_vis = sub.add_parser("visual", help="Visual/OCR")
    vis_sub = p_vis.add_subparsers(dest="action")
    vis_ocr = vis_sub.add_parser("ocr", help="OCR region")
    vis_ocr.add_argument("--x", type=int, default=0)
    vis_ocr.add_argument("--y", type=int, default=0)
    vis_ocr.add_argument("--width", type=int, default=1920)
    vis_ocr.add_argument("--height", type=int, default=1080)
    vis_ocr.add_argument("--lang", type=str, default="eng+chi_sim")
    vis_find = vis_sub.add_parser("find", help="Find image")
    vis_find.add_argument("--template", type=str, required=True)
    vis_find.add_argument("--confidence", type=float, default=0.9)
    vis_click = vis_sub.add_parser("click-image", help="Click image")
    vis_click.add_argument("--template", type=str, required=True)
    vis_click.add_argument("--confidence", type=float, default=0.9)
    vis_click.add_argument("--offset-x", type=int, default=0)
    vis_click.add_argument("--offset-y", type=int, default=0)
    vis_color = vis_sub.add_parser("find-color", help="Find color")
    vis_color.add_argument("--color", type=str, required=True)
    vis_pixel = vis_sub.add_parser("pixel", help="Get pixel color")
    vis_pixel.add_argument("--x", type=int, required=True)
    vis_pixel.add_argument("--y", type=int, required=True)

    args = parser.parse_args()

    if args.category == "mouse":
        if args.action == "position":
            mouse_position()
        elif args.action == "move":
            mouse_move(args.x, args.y, args.duration)
        elif args.action == "click":
            mouse_click(args.x, args.y)
        elif args.action == "right-click":
            mouse_right_click(args.x, args.y)
        elif args.action == "double-click":
            mouse_double_click(args.x, args.y)
        elif args.action == "drag":
            mouse_drag(args.start_x, args.start_y, args.end_x, args.end_y, args.duration)
        elif args.action == "scroll":
            mouse_scroll(args.x, args.y, args.clicks, args.direction)
        else:
            p_mouse.print_help()

    elif args.category == "keyboard":
        if args.action == "type":
            keyboard_type(args.text)
        elif args.action == "press":
            keyboard_press(args.keys)
        elif args.action == "key-down":
            keyboard_key_down(args.key)
        elif args.action == "key-up":
            keyboard_key_up(args.key)
        else:
            p_key.print_help()

    elif args.category == "screenshot":
        if args.action == "full":
            screenshot_full()
        elif args.action == "active-window":
            screenshot_active_window()
        elif args.action == "region":
            screenshot_region(args.x, args_y, args.width, args.height)
        elif args.action == "list":
            list_screenshots()
        elif args.action == "size":
            get_screen_size()
        else:
            p_shot.print_help()

    elif args.category == "visual":
        if args.action == "ocr":
            ocr_region(args.x, args.y, args.width, args.height, args.lang)
        elif args.action == "find":
            find_image(args.template, args.confidence)
        elif args.action == "click-image":
            click_image(args.template, "left", args.confidence, args.offset_x, args.offset_y)
        elif args.action == "find-color":
            find_color(args.color)
        elif args.action == "pixel":
            pixel_color(args.x, args.y)
        else:
            p_vis.print_help()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
