"""MoltAssist overnight queue -- enqueue, dequeue, validate."""

import json
import os
from pathlib import Path

REQUIRED_FIELDS = ("timestamp", "category", "urgency", "message")


def _get_queue_path() -> Path:
    workspace = os.environ.get("OPENCLAW_WORKSPACE") or os.path.expanduser("~/.openclaw/workspace")
    return Path(workspace) / "moltassist" / "memory" / "moltassist-queue.json"


def _read_queue(path: Path) -> list[dict]:
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


def _write_queue(entries: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(entries, f, indent=2)


def validate_entry(entry: dict) -> bool:
    """Return True if entry has all required fields and valid types."""
    if not isinstance(entry, dict):
        return False
    for field in REQUIRED_FIELDS:
        if field not in entry:
            return False
        if not isinstance(entry[field], str):
            return False
        if not entry[field].strip():
            return False
    return True


def enqueue(entry: dict, queue_path: str | Path | None = None) -> bool:
    """Append a validated entry to the queue. Returns False if entry is invalid."""
    if not validate_entry(entry):
        return False
    path = Path(queue_path) if queue_path else _get_queue_path()
    entries = _read_queue(path)
    entries.append(entry)
    _write_queue(entries, path)
    return True


def dequeue_all(queue_path: str | Path | None = None) -> list[dict]:
    """Read and clear the queue. Returns list of valid entries; discards invalid ones."""
    path = Path(queue_path) if queue_path else _get_queue_path()
    entries = _read_queue(path)
    # Clear the queue file
    _write_queue([], path)
    # Only return valid entries
    return [e for e in entries if validate_entry(e)]
