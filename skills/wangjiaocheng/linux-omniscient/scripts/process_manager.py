#!/usr/bin/env python3
"""
Process Manager - List, start, stop, and monitor system processes (Linux).

Requirements: Linux with standard procps tools
Dependencies: None (uses built-in Linux commands: ps, kill, pgrep, etc.)
"""

import subprocess
import sys
import os
import re
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import run_cmd


# ========== Safety: Input Validation ==========

# Dangerous characters that should never appear in process names or commands
DANGEROUS_CHARS_PATTERN = re.compile(r'[;&|`$(){}[\]!<>\n\r]')

# Protected system processes that must not be killed
PROTECTED_PROCESSES = {
    'init', 'systemd', 'kthreadd', 'ksoftirqd', 'kworker', 'migration',
    'watchdog', 'cpuset', 'khelper', 'netns', 'fs/mqueue', 'bio', 'blkcg',
    'watchdogd', 'bdflush', 'kworker', 'kswapd', 'crypto', 'kintegrityd',
    'bioset', 'kblockd', 'ata', 'firewire', 'dev', 'block', 'multipath',
    'rpciod', 'xprtiod', 'nfsiod', 'jffs2', 'cifsd', 'scsi_', 'scsi_eh',
    'dwc_otg', 'smb', 'nfs', 'nfsd', 'rpcbind', 'dbus', 'systemd-logind',
    'polkitd', 'rtkit', 'avahi-daemon', 'cups', 'bluetoothd', 'wpa_supplicant',
    'NetworkManager', 'ModemManager', 'gdm', 'gnome-shell', 'Xorg', 'pulseaudio',
}

# Blocked command patterns for process start
BLOCKED_COMMAND_PATTERNS = [
    'rm -rf', 'mkfs', 'dd if=', '>/dev/', '>&', '| ', '; ', '&&', '||',
    '$(', '${', '`', 'nohup ', 'screen -dm', 'tmux new',
]


def _validate_string(value, field_name="input"):
    """Validate that a string doesn't contain shell injection characters."""
    if not value:
        return True
    if DANGEROUS_CHARS_PATTERN.search(value):
        raise ValueError(
            f"ERROR: {field_name} contains forbidden shell characters. "
            f"Only alphanumeric, spaces, dots, hyphens, underscores, "
            f"slashes are allowed."
        )
    return True


def _validate_command_path(command):
    """Validate and sanitize a file path/command for execution."""
    if not command:
        raise ValueError("ERROR: Command cannot be empty")
    command = command.strip()
    lower_cmd = command.lower()
    for pattern in BLOCKED_COMMAND_PATTERNS:
        if pattern in lower_cmd:
            raise ValueError(
                f"ERROR: Command blocked - contains dangerous pattern '{pattern}'. "
                f"Use the terminal directly for advanced commands."
            )
    _validate_string(command, "command")
    return command


def list_processes(name=None):
    """List running processes. Optionally filter by name."""
    if name:
        _validate_string(name, "process name")
        stdout, stderr, code = run_cmd(f"ps aux --cols 2000 | grep -i '{name}' | grep -v grep")
    else:
        stdout, stderr, code = run_cmd("ps aux --cols 2000")
    
    if code == 0 and stdout:
        processes = []
        lines = stdout.strip().split('\n')
        if lines:
            # Skip header line
            for line in lines[1:] if not name else lines:
                parts = line.split(None, 10)
                if len(parts) >= 11:
                    processes.append({
                        "USER": parts[0],
                        "PID": parts[1],
                        "CPU": parts[2],
                        "MEM": parts[3],
                        "VSZ": parts[4],
                        "RSS": parts[5],
                        "TTY": parts[6],
                        "STAT": parts[7],
                        "START": parts[8],
                        "TIME": parts[9],
                        "COMMAND": parts[10] if len(parts) > 10 else ""
                    })
        return json.dumps(processes[:100], indent=2)  # Limit to 100 for readability
    return "[]"


def kill_process(pid=None, name=None, force=False):
    """Kill a process by PID or name. Protected system processes are blocked."""
    signal = "-9" if force else "-15"

    if pid:
        try:
            pid_val = int(pid)
            if pid_val < 1:
                return f"ERROR: Invalid PID value: {pid}"
        except (ValueError, TypeError):
            return f"ERROR: PID must be an integer, got: {pid}"

        # Get process name for validation
        name_out, _, _ = run_cmd(f"ps -p {pid_val} -o comm=")
        proc_name = name_out.strip().lower() if name_out else ""
        
        if proc_name in PROTECTED_PROCESSES or proc_name + '.service' in PROTECTED_PROCESSES:
            return f"ERROR: Process '{proc_name}' (PID {pid_val}) is protected and cannot be killed"
        
        stdout, stderr, code = run_cmd(f"kill {signal} {pid_val}")
        if code == 0:
            return f"OK: Killed process PID {pid_val}"
        return stderr if stderr else f"ERROR: Could not kill process PID {pid_val}"
    
    elif name:
        _validate_string(name, "process name")
        name_lower = name.lower().strip()

        # Fast reject from Python-level blacklist
        if name_lower in PROTECTED_PROCESSES:
            return f"ERROR: Process '{name}' is a protected system process and cannot be killed"

        # Find all matching processes
        stdout, stderr, code = run_cmd(f"pgrep -i '{name}'")
        if code == 0 and stdout:
            pids = stdout.strip().split('\n')
            killed = []
            failed = []
            for p in pids:
                try:
                    pid_int = int(p.strip())
                    name_out, _, _ = run_cmd(f"ps -p {pid_int} -o comm=")
                    proc_name = name_out.strip().lower() if name_out else ""
                    if proc_name in PROTECTED_PROCESSES:
                        failed.append(f"{p}(protected)")
                    else:
                        k_out, _, k_code = run_cmd(f"kill {signal} {pid_int}")
                        if k_code == 0:
                            killed.append(p)
                        else:
                            failed.append(p)
                except:
                    failed.append(p)
            
            if killed:
                result = f"OK: Killed {len(killed)} process(es): {', '.join(killed)}"
                if failed:
                    result += f" (failed: {', '.join(failed)})"
                return result
            return f"ERROR: Could not kill processes: {', '.join(failed)}"
        return f"ERROR: No process found matching '{name}'"
    
    else:
        return "ERROR: Provide --pid or --name"


def start_process(command, working_dir=None, wait=False):
    """Start a new process with validated/sanitized input."""
    # Validate command path (raises ValueError on dangerous input)
    safe_command = _validate_command_path(command)

    cmd = safe_command
    if working_dir:
        _validate_string(working_dir, "working directory")
        cmd = f"cd '{working_dir}' && {safe_command}"
    
    if wait:
        stdout, stderr, code = run_cmd(cmd)
        if code == 0:
            return f"OK: Process completed\n{stdout}"
        return f"ERROR: {stderr}" if stderr else "ERROR: Process failed"
    else:
        # Start in background
        stdout, stderr, code = run_cmd(f"nohup {safe_command} &")
        return f"OK: Process started in background"


def get_process_info(pid):
    """Get detailed information about a specific process."""
    try:
        pid_val = int(pid)
        if pid_val < 1:
            return f"ERROR: Invalid PID value: {pid}"
    except (ValueError, TypeError):
        return f"ERROR: PID must be an integer, got: {pid}"

    stdout, stderr, code = run_cmd(f"ps -p {pid_val} -o pid,ppid,user,comm,args,pcpu,pmem,vsz,rss,tty,stat,start,time --cols 2000")
    if code == 0 and stdout:
        lines = stdout.strip().split('\n')
        if len(lines) >= 2:
            return stdout
    return f"ERROR: Process PID {pid_val} not found"


def get_system_info():
    """Get overall system resource usage."""
    # CPU load
    cpu_out, _, _ = run_cmd("cat /proc/loadavg")
    load_avg = cpu_out.strip().split()[:3] if cpu_out else ["?", "?", "?"]
    
    # Memory
    mem_out, _, _ = run_cmd("free -m")
    mem_info = {}
    if mem_out:
        for line in mem_out.split('\n'):
            if 'Mem:' in line:
                parts = line.split()
                if len(parts) >= 7:
                    mem_info = {
                        "total_mb": parts[1],
                        "used_mb": parts[2],
                        "free_mb": parts[3],
                        "available_mb": parts[6]
                    }
    
    # Uptime
    uptime_out, _, _ = run_cmd("uptime -s")
    uptime_fmt, _, _ = run_cmd("uptime -p")
    
    # Process count
    proc_out, _, _ = run_cmd("ls /proc/[0-9]* 2>/dev/null | wc -l")
    proc_count = proc_out.strip() if proc_out else "?"
    
    # Hostname
    hostname_out, _, _ = run_cmd("hostname")
    
    result = {
        "hostname": hostname_out.strip() if hostname_out else "unknown",
        "load_average": load_avg,
        "memory_mb": mem_info,
        "process_count": proc_count,
        "uptime_since": uptime_out.strip() if uptime_out else "?",
        "uptime_pretty": uptime_fmt.strip() if uptime_fmt else "?"
    }
    return json.dumps(result, indent=2)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Process Manager (Linux)")
    sub = parser.add_subparsers(dest="action")

    p_list = sub.add_parser("list", help="List processes")
    p_list.add_argument("--name", type=str, help="Filter by name")

    p_kill = sub.add_parser("kill", help="Kill a process")
    p_kill.add_argument("--pid", type=int)
    p_kill.add_argument("--name", type=str)
    p_kill.add_argument("--force", action="store_true")

    p_start = sub.add_parser("start", help="Start a process")
    p_start.add_argument("command", type=str)
    p_start.add_argument("--dir", type=str, help="Working directory")
    p_start.add_argument("--wait", action="store_true")

    p_info = sub.add_parser("info", help="Get process details")
    p_info.add_argument("--pid", type=int, required=True)

    p_sys = sub.add_parser("system", help="Get system resource info")

    args = parser.parse_args()

    if args.action == "list":
        print(list_processes(args.name))
    elif args.action == "kill":
        print(kill_process(args.pid, args.name, args.force))
    elif args.action == "start":
        try:
            print(start_process(args.command, args.dir, args.wait))
        except ValueError as e:
            print(str(e))
    elif args.action == "info":
        print(get_process_info(args.pid))
    elif args.action == "system":
        print(get_system_info())
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
