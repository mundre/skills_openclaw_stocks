#!/usr/bin/env python3
"""
Discord command wrapper for the network scanner.
Usage: python3 discord_network_command.py <command>

Commands:
  !net <target> [--depth quick|normal|intense]  Scan a target
  !net local [--depth quick|normal|intense]    Scan local network
  !net help                                     Show help
"""

import subprocess
import sys
import re

SCRIPT_PATH = "/home/guy/.openclaw/workspace/apps/network-scanner/scanner.py"

HELP_TEXT = """
**`!net <target> [quick|normal|intense]`** — Scan a target
**`!net local [quick|normal|intense]`** — Fast local scan (gateway + nearby IPs)
**`!net local-full [quick|normal|intense]`** — Full subnet scan (slower)
**`!net help`** — Show this help

**Depth levels:**
• `quick`   — 9 common ports (fastest)
• `normal`  — 20 common ports (default)
• `intense` — top 100 ports (slowest, most thorough)

**Targets:** IP (1.2.3.4), CIDR (1.2.3.0/24), hostname, or URL
**Examples:**
  `!net 192.168.1.0/24 normal`
  `!net scanme.nmap.org intense`
  `!net local quick`
  `!net local-full`
  `!net https://example.com`
"""

def run_scan(args_str: str) -> str:
    depth = "normal"
    target = ""

    args = args_str.strip().split()
    if not args:
        return "Usage: `!net <target>` or `!net local`"

    if args[0] == "help":
        return HELP_TEXT.strip()

    if args[0] in ("local", "local-full"):
        is_full = args[0] == "local-full"
        cmd = ["python3", SCRIPT_PATH, "--local-scan" if not is_full else "--local",
               "--format", "discord"]
        if len(args) > 1 and args[1] in ("quick", "normal", "intense"):
            depth = args[1]
        cmd.extend(["--depth", depth])
        cmd.append("127.0.0.1")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            out = result.stdout.strip()
            if not out:
                return f"```\n{result.stderr.strip() or 'No output'}\n```"
            return out
        except subprocess.TimeoutExpired:
            return "⏱ Scan timed out after 2 minutes."
        except Exception as e:
            return f"⚠ Error: {e}"

    # Parse depth if provided as last arg
    if args and args[-1] in ("quick", "normal", "intense"):
        depth = args[-1]
        args = args[:-1]

    target = " ".join(args)
    if not target:
        return "Usage: `!net <target>`"

    cmd = ["python3", SCRIPT_PATH, target, "--format", "discord", "--depth", depth]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        out = result.stdout.strip()
        if not out:
            err = result.stderr.strip()
            return f"```\n{err or 'No output'}\n```"
        return out
    except subprocess.TimeoutExpired:
        return "⏱ Scan timed out after 3 minutes."
    except Exception as e:
        return f"⚠ Error: {e}"

if __name__ == "__main__":
    input_str = sys.argv[1] if len(sys.argv) > 1 else ""
    print(run_scan(input_str))
