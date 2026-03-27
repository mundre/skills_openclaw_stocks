"""MoltAssist structured log -- append, query, format."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from moltassist.formatter import EMOJI_MAP


def _get_log_path() -> Path:
    workspace = os.environ.get("OPENCLAW_WORKSPACE") or os.path.expanduser("~/.openclaw/workspace")
    return Path(workspace) / "moltassist" / "memory" / "moltassist-log.json"


def _read_log(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return []
    if isinstance(data, list):
        return data
    return []


def _write_log(entries: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(entries, f, indent=2)


def append_log(entry: dict, log_path: str | Path | None = None, max_entries: int = 500) -> None:
    """Append a log entry to the log file. Creates file if missing.

    After appending, trims the log to the most recent *max_entries* entries
    to prevent unbounded file growth.
    """
    path = Path(log_path) if log_path else _get_log_path()
    entries = _read_log(path)
    entries.append(entry)
    if len(entries) > max_entries:
        entries = entries[-max_entries:]
    _write_log(entries, path)


def query_log(
    category: str | None = None,
    urgency: str | None = None,
    hours: int = 24,
    log_path: str | Path | None = None,
) -> list[dict]:
    """Return filtered log entries from the last `hours` hours."""
    path = Path(log_path) if log_path else _get_log_path()
    entries = _read_log(path)

    now = datetime.now(timezone.utc)
    results = []
    for entry in entries:
        ts_str = entry.get("timestamp")
        if ts_str:
            try:
                ts = datetime.fromisoformat(ts_str)
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                diff_hours = (now - ts).total_seconds() / 3600
                if diff_hours > hours:
                    continue
            except (ValueError, TypeError):
                continue

        if category and entry.get("category") != category:
            continue
        if urgency and entry.get("urgency") != urgency:
            continue

        results.append(entry)

    return results


def format_log_summary(entries: list[dict]) -> str:
    """Return a human-readable summary grouped by category."""
    if not entries:
        return "No alerts in the selected period."

    # Group by category
    by_cat: dict[str, list[dict]] = {}
    for e in entries:
        cat = e.get("category", "unknown")
        by_cat.setdefault(cat, []).append(e)

    fired = sum(1 for e in entries if e.get("delivered"))
    queued = sum(1 for e in entries if not e.get("delivered"))

    lines = [f"Last period -- {fired} alerts fired, {queued} queued"]
    lines.append("")

    for cat, cat_entries in sorted(by_cat.items()):
        emoji = EMOJI_MAP.get(cat, "")
        msgs = []
        for e in cat_entries:
            msg = e.get("message", "")[:50]
            urg = e.get("urgency", "?")
            msgs.append(f"{msg} [{urg}]")
        lines.append(f"{emoji} {cat.title()} ({len(cat_entries)}): {', '.join(msgs)}")

    return "\n".join(lines)


def make_log_entry(
    category: str,
    urgency: str,
    source: str,
    message: str,
    delivered: bool,
    channel_used: str | None = None,
    llm_enriched: bool = False,
    event_id: str | None = None,
    error: str | None = None,
) -> dict:
    """Create a well-formed log entry dict."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "category": category,
        "urgency": urgency,
        "source": source,
        "message": message,
        "delivered": delivered,
        "channel_used": channel_used,
        "llm_enriched": llm_enriched,
        "event_id": event_id,
        "error": error,
    }
