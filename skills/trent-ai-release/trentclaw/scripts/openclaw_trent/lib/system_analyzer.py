# Copyright (c) 2025-2026 Trent AI. All rights reserved.
# Licensed under the Trent AI Proprietary License.

"""Collects OpenClaw deployment context for security audits.

Gathers channel configuration and installed skill names.
All output is redacted for secrets before emission.
"""

import json
import logging
import re
import subprocess
from pathlib import Path
from typing import Any

from openclaw_trent import __version__
from openclaw_trent.openclaw_config.secret_redactor import SecretRedactor

logger = logging.getLogger(__name__)

SUBPROCESS_TIMEOUT = 10  # seconds
DEFAULT_OPENCLAW_PATH = Path.home() / ".openclaw"


# --- Channel parsing ---

# Matches lines like: "- Telegram default: not configured, token=none, enabled"
_CHANNEL_RE = re.compile(r"^-\s+(\S+)\s+(\S+):\s*(.+)$")
# Matches lines like: "- anthropic:default (token)"
_AUTH_RE = re.compile(r"^-\s+(\S+)\s+\((\w+)\)$")


def detect_channels() -> dict[str, Any]:
    """Run `openclaw channels list` and parse output.

    Returns channel info, auth providers, and doctor warnings.
    Handles missing binary, timeouts, and parse failures gracefully.
    """
    result: dict[str, Any] = {
        "channels": [],
        "auth_providers": [],
        "doctor_warnings": [],
        "channel_count": 0,
        "command_error": None,
        "parse_error": None,
    }

    try:
        proc = subprocess.run(
            ["openclaw", "channels", "list"],
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT,
        )
        stdout = proc.stdout
    except FileNotFoundError:
        result["command_error"] = "openclaw binary not found"
        return result
    except subprocess.TimeoutExpired:
        result["command_error"] = f"command timed out after {SUBPROCESS_TIMEOUT}s"
        return result
    except OSError as e:
        result["command_error"] = str(e)
        return result

    try:
        _parse_channel_output(stdout, result)
    except Exception as e:
        logger.warning("Failed to parse openclaw channels output: %s", e)
        result["parse_error"] = str(e)

    result["channel_count"] = len(result["channels"])
    return result


def _parse_channel_output(stdout: str, result: dict[str, Any]) -> None:
    """Parse the structured output of `openclaw channels list`."""
    section = None  # "doctor", "channels", "auth"

    for line in stdout.splitlines():
        stripped = line.strip()

        # Detect doctor warnings section
        if "Doctor warnings" in line:
            section = "doctor"
            continue

        # Detect channel section header
        if stripped.startswith("Chat channels:"):
            section = "channels"
            continue

        # Detect auth section header
        if stripped.startswith("Auth providers"):
            section = "auth"
            continue

        # Skip box-drawing decoration lines
        if stripped.startswith(("│", "├", "╮", "╯", "◇")) or stripped == "":
            # But extract doctor warning text from inside the box
            if section == "doctor" and stripped.startswith("│"):
                warning_text = stripped.lstrip("│").strip()
                if warning_text and not warning_text.startswith(("─", "╮", "╯", "├")):
                    # Accumulate multi-line warnings
                    if result["doctor_warnings"] and not warning_text.startswith("-"):
                        result["doctor_warnings"][-1] += " " + warning_text
                    elif warning_text.startswith("- "):
                        result["doctor_warnings"].append(warning_text[2:])
            continue

        # Parse channel lines
        if section == "channels":
            m = _CHANNEL_RE.match(stripped)
            if m:
                name, profile, details = m.group(1), m.group(2), m.group(3)
                enabled = "enabled" in details.lower()
                # Extract status (everything before the first comma, minus known tokens)
                status_parts = [
                    p.strip()
                    for p in details.split(",")
                    if p.strip().lower() not in ("enabled", "disabled")
                    and not p.strip().startswith("token=")
                    and not p.strip().startswith("bot=")
                    and not p.strip().startswith("app=")
                ]
                status = ", ".join(status_parts) if status_parts else "configured"

                result["channels"].append(
                    {
                        "name": name,
                        "profile": profile,
                        "status": status,
                        "enabled": enabled,
                    }
                )
            continue

        # Parse auth provider lines
        if section == "auth":
            m = _AUTH_RE.match(stripped)
            if m:
                result["auth_providers"].append({"name": m.group(1), "type": m.group(2)})
            continue


def detect_skills(openclaw_path: Path | None = None) -> dict[str, Any]:
    """List installed skills from managed and workspace directories.

    Only collects directory names — does not read file contents.
    """
    base_path = (openclaw_path or DEFAULT_OPENCLAW_PATH).expanduser()
    skills: list[dict[str, str]] = []
    errors: list[str] = []

    skill_dirs = [
        ("managed", base_path / "skills"),
        ("workspace", base_path / "workspace" / "skills"),
    ]

    for source, skills_dir in skill_dirs:
        if not skills_dir.is_dir():
            continue
        try:
            for entry in sorted(skills_dir.iterdir()):
                if entry.is_dir() and not entry.name.startswith("."):
                    skills.append({"name": entry.name, "source": source})
        except OSError as e:
            errors.append(f"Cannot read {skills_dir}: {e}")

    managed_count = sum(1 for s in skills if s["source"] == "managed")
    workspace_count = sum(1 for s in skills if s["source"] == "workspace")

    result: dict[str, Any] = {
        "skills": skills,
        "managed_count": managed_count,
        "workspace_count": workspace_count,
    }
    if errors:
        result["errors"] = errors
    return result


def collect_system_analysis(openclaw_path: Path | None = None) -> dict[str, Any]:
    """Collect OpenClaw deployment context with secret redaction.

    Gathers channel configuration and installed skill names.
    Applies SecretRedactor to the full result before returning.
    """
    errors: list[str] = []

    channel_info = detect_channels()
    skills_info = detect_skills(openclaw_path=openclaw_path)

    # Collect errors from sub-results
    if channel_info.get("command_error"):
        errors.append(f"channels: {channel_info['command_error']}")
    if channel_info.get("parse_error"):
        errors.append(f"channels parse: {channel_info['parse_error']}")
    if skills_info.get("errors"):
        errors.extend(skills_info.pop("errors"))

    result: dict[str, Any] = {
        "schema_version": "2.0",
        "channels": channel_info,
        "skills": skills_info,
        "errors": errors,
    }

    # Apply secret redaction
    redactor = SecretRedactor()
    result = redactor.redact(result)
    result["redacted_paths"] = redactor.redacted_paths

    return result


def main() -> None:
    """CLI entry point for system analysis."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="trent-openclaw-sysinfo",
        description="Collect OpenClaw deployment context for security audit.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--path",
        type=str,
        default=None,
        help="Path to OpenClaw config directory (default: ~/.openclaw)",
    )
    args = parser.parse_args()

    path_arg = Path(args.path) if args.path else None
    result = collect_system_analysis(openclaw_path=path_arg)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
