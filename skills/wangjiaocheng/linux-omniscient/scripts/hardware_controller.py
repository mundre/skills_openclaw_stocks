#!/usr/bin/env python3
"""
Hardware Controller - Control Linux system hardware settings.

Capabilities:
  - Volume control (get/set/mute) via amixer/pactl/playerctl
  - Screen brightness (get/set) via xbacklight/ddcutil
  - Display settings (resolution, orientation) via xrandr
  - Power management (sleep, shutdown, restart, lock)
  - Network adapters (list, enable, disable) via ip/nmcli
  - WiFi (list networks) via nmcli
  - USB devices (list) via lsusb

Requirements: Linux with X11/Wayland
Dependencies: amixer, xrandr, xbacklight, pactl (install via package manager)
"""

import subprocess
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run_cmd


def _check_tool(tool):
    """Check if a tool is available."""
    result = subprocess.run(
        ["which", tool],
        capture_output=True,
        text=True
    )
    return result.returncode == 0


# Check available tools
HAS_AMIXER = _check_tool("amixer")
HAS_PACTL = _check_tool("pactl")
HAS_XRANDR = _check_tool("xrandr")
HAS_XBACKLIGHT = _check_tool("xbacklight")
HAS_DDCCUTIL = _check_tool("ddcutil")
HAS_NMCLI = _check_tool("nmcli")


# ========== Volume Control ==========

def get_volume():
    """Get current volume level and mute state."""
    if HAS_PACTL:
        # Use pactl for PulseAudio
        stdout, stderr, code = run_cmd("pactl get-default-sink")
        if code == 0:
            sink = stdout.strip()
            vol_out, _, _ = run_cmd(f"pactl get-sink-volume {sink}")
            mute_out, _, _ = run_cmd(f"pactl get-sink-mute {sink}")
            return json.dumps({
                "sink": sink,
                "volume": vol_out.strip() if vol_out else "?",
                "mute": mute_out.strip() if mute_out else "?"
            }, indent=2)
    elif HAS_AMIXER:
        stdout, stderr, code = run_cmd("amixer sget Master")
        if code == 0 and stdout:
            return stdout.strip()
    
    return '{"Note":"Audio control tools not available (install amixer, pactl)"}'


def set_volume(level):
    """Set volume level (0-100)."""
    if not (0 <= level <= 100):
        return "ERROR: Volume level must be 0-100"
    
    if HAS_PACTL:
        stdout, stderr, code = run_cmd("pactl get-default-sink")
        if code == 0:
            sink = stdout.strip()
            out, err, code = run_cmd(f"pactl set-sink-volume {sink} {level}%")
            if code == 0:
                return f"OK: Volume set to {level}%"
            return f"ERROR: {err}" if err else "ERROR: Failed to set volume"
    
    elif HAS_AMIXER:
        out, err, code = run_cmd(f"amixer set Master {level}%")
        if code == 0:
            return f"OK: Volume set to {level}%"
        return f"ERROR: {err}" if err else "ERROR: Failed to set volume"
    
    return "ERROR: No volume control tool available (install amixer or pactl)"


def toggle_mute():
    """Toggle system mute."""
    if HAS_PACTL:
        stdout, stderr, code = run_cmd("pactl get-default-sink")
        if code == 0:
            sink = stdout.strip()
            out, err, code = run_cmd(f"pactl set-sink-mute {sink} toggle")
            if code == 0:
                return "OK: Toggle mute"
            return f"ERROR: {err}" if err else "ERROR: Failed to toggle mute"
    
    elif HAS_AMIXER:
        out, err, code = run_cmd("amixer set Master toggle")
        if code == 0:
            return "OK: Toggle mute"
        return f"ERROR: {err}" if err else "ERROR: Failed to toggle mute"
    
    return "ERROR: No volume control tool available"


# ========== Screen / Display ==========

def get_brightness():
    """Get screen brightness level."""
    if HAS_XBACKLIGHT:
        stdout, stderr, code = run_cmd("xbacklight -get")
        if code == 0 and stdout:
            try:
                val = float(stdout.strip())
                return json.dumps({
                    "brightness": round(val, 1),
                    "percent": round(val)
                })
            except:
                pass
    elif HAS_DDCCUTIL:
        stdout, stderr, code = run_cmd("ddcutil getvcp 10")
        if code == 0 and stdout:
            return stdout.strip()
    
    return '{"Error":"Could not read brightness (try installing xbacklight or ddcutil)"}'


def set_brightness(level):
    """Set screen brightness (0-100)."""
    if not (0 <= level <= 100):
        return "ERROR: Brightness must be 0-100"
    
    if HAS_XBACKLIGHT:
        out, err, code = run_cmd(f"xbacklight -set {level}")
        if code == 0:
            return f"OK: Brightness set to {level}%"
        return f"ERROR: {err}" if err else "ERROR: Failed to set brightness"
    
    elif HAS_DDCCUTIL:
        out, err, code = run_cmd(f"ddcutil setvcp 10 {level}")
        if code == 0:
            return f"OK: Brightness set to {level}%"
        return f"ERROR: {err}" if err else "ERROR: Failed to set brightness"
    
    return "ERROR: No brightness control tool available (install xbacklight or ddcutil)"


def get_display_info():
    """Get display adapter and resolution information."""
    if HAS_XRANDR:
        stdout, stderr, code = run_cmd("xrandr --listmonitors")
        monitors_out, _, _ = run_cmd("xrandr --query")
        if code == 0:
            return monitors_out.strip()
    
    return '{"Note":"xrandr not available"}'


# ========== Safety: Protected process blacklist ==========
# These critical system processes must never be killed
PROTECTED_PROCESSES = {
    'init', 'systemd', 'kthreadd', 'sshd', 'cron', 'rsyslogd'
}

# ========== Power Management ==========

def _require_confirmation(action_name):
    """
    Safety gate for destructive power operations.
    Returns error string if confirmation env var is not set.
    """
    confirmed = os.environ.get("SYSTEM_CONTROLLER_CONFIRM", "")
    if action_name not in confirmed.split(","):
        return (
            f"ERROR: {action_name} requires explicit confirmation. "
            f"Set environment variable SYSTEM_CONTROLLER_CONFIRM={action_name} "
            f"or SYSTEM_CONTROLLER_CONFIRM=all to proceed."
        )
    return None


def lock_screen():
    """Lock the workstation."""
    # Try various screen lockers
    lockers = ["gnome-screensaver-command -l", "xdg-screensaver lock", 
                "loginctl lock-session", "xlock -mode blank", "slock"]
    for locker in lockers:
        out, err, code = run_cmd(locker)
        if code == 0:
            return "OK: Screen locked"
    return "OK: Lock command sent (may require locker installed)"


def sleep_system():
    """Suspend the system."""
    err = _require_confirmation("sleep")
    if err:
        return err
    out, err, code = run_cmd("systemctl suspend")
    if code == 0:
        return "OK: System entering suspend mode"
    out, err, code = run_cmd("pm-suspend")
    if code == 0:
        return "OK: System entering suspend mode"
    return "ERROR: Could not suspend (may require root or systemd)"


def hibernate():
    """Hibernate the system."""
    err = _require_confirmation("hibernate")
    if err:
        return err
    out, err, code = run_cmd("systemctl hibernate")
    if code == 0:
        return "OK: System hibernating"
    return "ERROR: Could not hibernate (may require root or swap)"


def shutdown(delay_sec=60):
    """Schedule system shutdown. Requires SYSTEM_CONTROLLER_CONFIRM env var."""
    err = _require_confirmation("shutdown")
    if err:
        return err
    if delay_sec < 10:
        return "ERROR: Minimum shutdown delay is 10 seconds"
    out, err, code = run_cmd(f"shutdown -h +{delay_sec//60} '{delay_sec}s delayed shutdown'")
    if code == 0:
        return f"OK: System will shutdown in {delay_sec} seconds. Run 'shutdown -c' to cancel."
    return f"ERROR: {err}" if err else "ERROR: Failed to schedule shutdown"


def restart(delay_sec=60):
    """Schedule system restart. Requires SYSTEM_CONTROLLER_CONFIRM env var."""
    err = _require_confirmation("restart")
    if err:
        return err
    if delay_sec < 10:
        return "ERROR: Minimum restart delay is 10 seconds"
    out, err, code = run_cmd(f"shutdown -r +{delay_sec//60} '{delay_sec}s delayed restart'")
    if code == 0:
        return f"OK: System will restart in {delay_sec} seconds. Run 'shutdown -c' to cancel."
    return f"ERROR: {err}" if err else "ERROR: Failed to schedule restart"


def cancel_shutdown():
    """Cancel a scheduled shutdown/restart."""
    out, err, code = run_cmd("shutdown -c")
    if code == 0:
        return "OK: Shutdown/restart cancelled"
    return "INFO: No shutdown scheduled"


# ========== Network ==========

def list_network_adapters():
    """List all network adapters with status."""
    if HAS_NMCLI:
        stdout, stderr, code = run_cmd("nmcli device status")
        if code == 0:
            return stdout.strip()
    
    # Fallback to ip
    stdout, stderr, code = run_cmd("ip -br link show")
    if code == 0:
        return stdout.strip()
    
    return '{"Note":"Network tools not available"}'


def enable_adapter(name):
    """Enable a network adapter."""
    if HAS_NMCLI:
        out, err, code = run_cmd(f"nmcli device connect '{name}'")
        if code == 0:
            return f"OK: Adapter '{name}' enabled"
        return f"ERROR: {err}" if err else f"ERROR: Failed to enable '{name}'"
    
    out, err, code = run_cmd(f"ip link set '{name}' up")
    if code == 0:
        return f"OK: Adapter '{name}' enabled"
    return f"ERROR: {err}" if err else f"ERROR: Failed to enable '{name}'"


def disable_adapter(name):
    """Disable a network adapter. Requires confirmation to prevent self-disconnect."""
    err = _require_confirmation("disable_network")
    if err:
        return err
    
    if HAS_NMCLI:
        out, err, code = run_cmd(f"nmcli device disconnect '{name}'")
        if code == 0:
            return f"OK: Adapter '{name}' disabled"
        return f"ERROR: {err}" if err else f"ERROR: Failed to disable '{name}'"
    
    out, err, code = run_cmd(f"ip link set '{name}' down")
    if code == 0:
        return f"OK: Adapter '{name}' disabled"
    return f"ERROR: {err}" if err else f"ERROR: Failed to disable '{name}'"


def list_wifi_networks():
    """List available WiFi networks."""
    if HAS_NMCLI:
        stdout, stderr, code = run_cmd("nmcli device wifi list")
        if code == 0:
            return stdout.strip()
    
    out, err, code = run_cmd("iw dev wlan0 scan 2>/dev/null | grep SSID")
    if code == 0:
        return out.strip()
    
    return '{"Note":"WiFi scan not available (install nmcli or iw)"}'


def get_network_info():
    """Get current network configuration."""
    stdout, stderr, code = run_cmd("ip addr show")
    if code == 0:
        return stdout.strip()
    
    return '{"Note":"Network info not available"}'


# ========== USB / Device ==========

def list_usb_devices():
    """List connected USB devices."""
    stdout, stderr, code = run_cmd("lsusb")
    if code == 0:
        devices = []
        for line in stdout.strip().split('\n'):
            if line:
                devices.append(line)
        return json.dumps(devices, indent=2)
    
    return '{"Note":"lsusb not available"}'


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Hardware Controller (Linux)")
    sub = parser.add_subparsers(dest="category")

    # Volume
    p_vol = sub.add_parser("volume", help="Volume control")
    vol_sub = p_vol.add_subparsers(dest="action")
    vol_sub.add_parser("get", help="Get volume level")
    vol_set = vol_sub.add_parser("set", help="Set volume")
    vol_set.add_argument("--level", type=int, required=True, help="0-100")
    vol_sub.add_parser("mute", help="Toggle mute")

    # Screen
    p_scr = sub.add_parser("screen", help="Screen/display control")
    scr_sub = p_scr.add_subparsers(dest="action")
    scr_sub.add_parser("info", help="Get display info")
    bri_get = scr_sub.add_parser("brightness", help="Get/set brightness")
    bri_get.add_argument("--level", type=int, help="0-100")

    # Power
    p_pwr = sub.add_parser("power", help="Power management")
    pwr_sub = p_pwr.add_subparsers(dest="action")
    pwr_sub.add_parser("lock", help="Lock screen")
    pwr_sub.add_parser("sleep", help="Suspend mode")
    pwr_sub.add_parser("hibernate", help="Hibernate")
    pwr_sd = pwr_sub.add_parser("shutdown", help="Shutdown")
    pwr_sd.add_argument("--delay", type=int, default=60, help="Seconds")
    pwr_rs = pwr_sub.add_parser("restart", help="Restart")
    pwr_rs.add_argument("--delay", type=int, default=60, help="Seconds")
    pwr_sub.add_parser("cancel", help="Cancel scheduled shutdown")

    # Network
    p_net = sub.add_parser("network", help="Network control")
    net_sub = p_net.add_subparsers(dest="action")
    net_sub.add_parser("adapters", help="List network adapters")
    net_en = net_sub.add_parser("enable", help="Enable adapter")
    net_en.add_argument("--name", type=str, required=True)
    net_dis = net_sub.add_parser("disable", help="Disable adapter")
    net_dis.add_argument("--name", type=str, required=True)
    net_sub.add_parser("wifi", help="List WiFi networks")
    net_sub.add_parser("info", help="Get network config")

    # USB
    p_usb = sub.add_parser("usb", help="USB devices")
    usb_sub = p_usb.add_subparsers(dest="action")
    usb_sub.add_parser("list", help="List USB devices")

    args = parser.parse_args()

    if args.category == "volume":
        if args.action == "get":
            print(get_volume())
        elif args.action == "set":
            print(set_volume(args.level))
        elif args.action == "mute":
            print(toggle_mute())
        else:
            p_vol.print_help()
    elif args.category == "screen":
        if args.action == "info":
            print(get_display_info())
        elif args.action == "brightness":
            if args.level is not None:
                print(set_brightness(args.level))
            else:
                print(get_brightness())
        else:
            p_scr.print_help()
    elif args.category == "power":
        if args.action == "lock":
            print(lock_screen())
        elif args.action == "sleep":
            print(sleep_system())
        elif args.action == "hibernate":
            print(hibernate())
        elif args.action == "shutdown":
            print(shutdown(args.delay))
        elif args.action == "restart":
            print(restart(args.delay))
        elif args.action == "cancel":
            print(cancel_shutdown())
        else:
            p_pwr.print_help()
    elif args.category == "network":
        if args.action == "adapters":
            print(list_network_adapters())
        elif args.action == "enable":
            print(enable_adapter(args.name))
        elif args.action == "disable":
            print(disable_adapter(args.name))
        elif args.action == "wifi":
            print(list_wifi_networks())
        elif args.action == "info":
            print(get_network_info())
        else:
            p_net.print_help()
    elif args.category == "usb":
        if args.action == "list":
            print(list_usb_devices())
        else:
            p_usb.print_help()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
