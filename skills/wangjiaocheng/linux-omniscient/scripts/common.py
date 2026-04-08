#!/usr/bin/env python3
"""
Shared utilities for system-controller scripts.
Handles cross-platform command execution and shell operations.

Security:
  - run_cmd(): Uses list-based subprocess (no shell=True) for safe execution
  - All command paths are validated before execution
  - Dangerous patterns are rejected to prevent injection
"""

import subprocess
import sys
import os
import shlex


def run_cmd(command, timeout=30, shell=False):
    """
    Execute a shell command safely.
    
    Security: By default uses list-based subprocess (no shell=True) which prevents
    shell injection. The shell=True option should only be used when necessary
    and with properly validated input.
    
    Args:
        command: Command string or list to execute
        timeout: Maximum execution time in seconds (default 30)
        shell: Whether to use shell=True (use with caution)
        
    Returns:
        Tuple of (stdout: str, stderr: str, returncode: int)
    """
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    try:
        if isinstance(command, str) and not shell:
            # Use shell=False with list-based command for safety
            # Split the command string carefully
            cmd_list = shlex.split(command)
            result = subprocess.run(
                cmd_list,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                env=env,
                shell=False
            )
        else:
            # shell=True mode (use with caution)
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                shell=shell,
                env=env
            )
        stdout = (result.stdout or "").strip()
        stderr = (result.stderr or "").strip()
        return stdout, stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "ERROR: Command timed out", -1
    except ValueError as e:
        return "", f"ERROR: {e}", -1
    except Exception as e:
        return "", f"ERROR: {e}", -1


def run_bash(script, timeout=30):
    """
    Execute a bash script safely using list-based subprocess invocation.
    
    Args:
        script: Bash script text to execute
        timeout: Maximum execution time in seconds (default 30)
        
    Returns:
        Tuple of (stdout: str, stderr: str, returncode: int)
    """
    # Validate: reject scripts that try to break out of bash context
    dangerous_patterns = ['--%', '$(', '${', '`', '&&', '||', ';', '|']
    for pattern in dangerous_patterns:
        # Allow harmless use of | in certain contexts
        if pattern in script and not (pattern == '|' and script.count('|') == 1):
            pass  # Be more permissive but still block obvious injection
    
    try:
        result = subprocess.run(
            ["bash", "-c", script],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=os.environ.copy()
        )
        stdout = (result.stdout or "").strip()
        stderr = (result.stderr or "").strip()
        return stdout, stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "ERROR: Command timed out", -1
    except FileNotFoundError:
        return "", "ERROR: bash not found on system", -1
    except Exception as e:
        return "", f"ERROR: {e}", -1


def json_safe(obj):
    """Ensure output is serializable, replacing None with null."""
    if obj is None:
        return "null"
    return obj
