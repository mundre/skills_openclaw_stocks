"""Track rotation state machine.

State file: ../state.json (relative to scripts/)
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

TRACKS = ["ai", "crypto", "devtools"]
STATE_FILE = Path(__file__).parent.parent / "state.json"


@dataclass
class RunState:
    current_track_index: int = 0
    last_run: str | None = None  # ISO 8601
    last_tracks: list[str] = field(default_factory=list)  # last N track names


def load_state() -> RunState:
    """Load state from disk. Returns default state if file missing/corrupt."""
    if not STATE_FILE.exists():
        print("[autoresearch] INFO  state.json not found — starting fresh", file=sys.stderr)
        return RunState()
    try:
        data = json.loads(STATE_FILE.read_text())
        return RunState(
            current_track_index=int(data.get("current_track_index", 0)) % len(TRACKS),
            last_run=data.get("last_run"),
            last_tracks=list(data.get("last_tracks", [])),
        )
    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        print(f"[autoresearch] WARN  state.json corrupt ({exc}) — resetting to defaults", file=sys.stderr)
        return RunState()


def save_state(state: RunState) -> None:
    """Persist state to disk (atomic write via tmp + rename)."""
    data = {
        "current_track_index": state.current_track_index,
        "last_run": state.last_run,
        "last_tracks": state.last_tracks[-10:],  # keep last 10 only
    }
    tmp_path = STATE_FILE.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(data, indent=2))
    os.rename(tmp_path, STATE_FILE)


def get_current_track(state: RunState) -> str:
    """Return the track name for this run (e.g. 'ai')."""
    return TRACKS[state.current_track_index % len(TRACKS)]


def advance_track(state: RunState) -> RunState:
    """Advance to next track, update last_run timestamp, append to last_tracks."""
    current = get_current_track(state)
    next_index = (state.current_track_index + 1) % len(TRACKS)
    new_last_tracks = state.last_tracks + [current]
    return RunState(
        current_track_index=next_index,
        last_run=datetime.now(timezone.utc).isoformat(),
        last_tracks=new_last_tracks[-10:],
    )


def override_track(track_name: str) -> str:
    """Validate a manual --track override. Raises ValueError if invalid."""
    if track_name not in TRACKS:
        raise ValueError(f"Invalid track '{track_name}'. Valid tracks: {', '.join(TRACKS)}")
    return track_name
