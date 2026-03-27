#!/usr/bin/env python3
"""
MoltAssist morning digest -- sends queued overnight notifications as a single summary.
Called by launchd/cron at quiet_hours.end (default 08:00).

Usage: python3 scripts/digest.py [--workspace /path/to/workspace]
"""

import argparse
import json
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from moltassist.config import load_config
from moltassist.formatter import EMOJI_MAP
from moltassist.log import append_log, make_log_entry
from moltassist.queue import _get_queue_path, _read_queue, _write_queue, validate_entry


def _build_digest_mode_a(entries: list[dict]) -> str:
    """Mode A: bullet list grouped by category (no LLM)."""
    grouped: dict[str, list[str]] = defaultdict(list)
    for entry in entries:
        cat = entry.get("category", "custom")
        msg = entry.get("message", "Unknown event")
        grouped[cat].append(msg)

    total = len(entries)
    lines = [f" Overnight digest -- {total} queued\n"]

    for cat, messages in grouped.items():
        emoji = EMOJI_MAP.get(cat, "")
        count = len(messages)
        # Truncate each message to keep digest readable
        summaries = ", ".join(m[:80] for m in messages)
        lines.append(f"{emoji} {cat.title()} ({count}): {summaries}")

    return "\n".join(lines)


def _build_digest_mode_b(entries: list[dict]) -> str | None:
    """Mode B: LLM prose summary via openclaw agent. Returns None on failure."""
    # Build a plain-text list for the LLM
    item_lines = []
    for entry in entries:
        cat = entry.get("category", "custom")
        msg = entry.get("message", "Unknown event")
        item_lines.append(f"- [{cat}] {msg}")

    items_text = "\n".join(item_lines)
    total = len(entries)

    prompt = (
        f"You are a concise morning briefing assistant. Summarise these {total} "
        f"overnight notifications into a short, natural prose paragraph. "
        f"No preamble, no sign-off. Be direct and conversational.\n\n"
        f"{items_text}"
    )

    try:
        result = subprocess.run(
            ["openclaw", "agent", "--local", "-m", prompt],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return None
        output = result.stdout.strip()
        if not output:
            return None
        return f" Morning -- {total} things while you slept\n\n{output}"
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def _send_digest(message: str, config: dict) -> tuple[bool, str | None]:
    """Send digest via openclaw message send."""
    delivery = config.get("delivery", {})
    channel = delivery.get("default_channel", "telegram")

    # Use the channels module for delivery
    from moltassist.channels import deliver
    return deliver(message, channel=channel)


def run_digest(workspace: str | None = None) -> None:
    """Read queue, build digest, send, clear queue, log result."""
    # Set workspace env if provided
    if workspace:
        os.environ["OPENCLAW_WORKSPACE"] = workspace

    config = load_config()
    queue_path = _get_queue_path()
    raw_entries = _read_queue(queue_path)

    if not raw_entries:
        return  # Empty queue -- exit silently

    # Validate each entry, reject corrupt ones
    valid = []
    rejected = 0
    for entry in raw_entries:
        if validate_entry(entry):
            valid.append(entry)
        else:
            rejected += 1

    if not valid:
        # All entries were corrupt -- clear queue, log, exit
        _write_queue([], queue_path)
        append_log(make_log_entry(
            category="digest",
            urgency="low",
            source="digest",
            message=f"Digest: {rejected} corrupt entries rejected, nothing to send",
            delivered=False,
        ))
        return

    # Try Mode B (LLM prose) first, fall back to Mode A (bullet list)
    llm_mode = config.get("llm_mode", "none")
    digest_message = None

    if llm_mode != "none":
        digest_message = _build_digest_mode_b(valid)

    if digest_message is None:
        digest_message = _build_digest_mode_a(valid)

    # Send via configured channel
    success, error = _send_digest(digest_message, config)

    if success:
        # Clear the queue after successful send
        _write_queue([], queue_path)
        channel = config.get("delivery", {}).get("default_channel", "telegram")
        append_log(make_log_entry(
            category="digest",
            urgency="low",
            source="digest",
            message=f"Morning digest sent: {len(valid)} items"
            + (f", {rejected} rejected" if rejected else ""),
            delivered=True,
            channel_used=channel,
        ))
    else:
        # Leave queue intact on failure -- will retry next run
        append_log(make_log_entry(
            category="digest",
            urgency="high",
            source="digest",
            message=f"Digest send failed: {error}",
            delivered=False,
            error=error,
        ))


def main():
    parser = argparse.ArgumentParser(description="MoltAssist morning digest")
    parser.add_argument(
        "--workspace",
        type=str,
        default=None,
        help="Path to OpenClaw workspace (default: ~/.openclaw/workspace)",
    )
    args = parser.parse_args()
    run_digest(workspace=args.workspace)


if __name__ == "__main__":
    main()
