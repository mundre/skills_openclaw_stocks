"""MoltAssist deduplication -- event ID tracking via persisted log."""

import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path

from moltassist.log import _get_log_path, _read_log


def _generate_event_id(message: str, category: str, timestamp_hour: str) -> str:
    """Generate a deterministic event ID from message + category + hour."""
    raw = f"{message}|{category}|{timestamp_hour}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def is_duplicate(
    event_id: str,
    log_path: str | Path | None = None,
    window_days: int = 7,
) -> bool:
    """Return True if event_id already exists in recent log entries.

    Only scans entries from the last *window_days* days to avoid O(n)
    growth over the full log history.
    """
    path = Path(log_path) if log_path else _get_log_path()
    entries = _read_log(path)
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)

    for entry in entries:
        # Skip entries older than the window
        ts_str = entry.get("timestamp")
        if ts_str:
            try:
                ts = datetime.fromisoformat(ts_str)
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                if ts < cutoff:
                    continue
            except (ValueError, TypeError):
                pass  # If timestamp is unparseable, still check it

        if entry.get("event_id") == event_id:
            return True
    return False
