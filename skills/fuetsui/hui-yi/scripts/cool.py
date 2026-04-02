#!/usr/bin/env python
"""Cold-memory cooling helper for Hui-Yi."""
from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parents[2]
DEFAULT_MEMORY_ROOT = WORKSPACE_ROOT / "memory"


def resolve_memory_root(arg: str | None) -> Path:
    if arg:
        candidate = Path(arg)
        return candidate if candidate.is_absolute() else (Path.cwd() / candidate).resolve()
    return DEFAULT_MEMORY_ROOT


def load_state(path: Path) -> dict:
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {}


def save_state(path: Path, state: dict) -> None:
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ensure_cold_state(state: dict) -> dict:
    cold = state.get("coldMemory")
    if not isinstance(cold, dict):
        cold = {}
        state["coldMemory"] = cold
    cold.setdefault("lastScan", None)
    cold.setdefault("lastArchive", None)
    cold.setdefault("lastIndexRefresh", None)
    cold.setdefault("lastSummary", "")
    cold.setdefault("totalCoolings", 0)
    cold.setdefault("totalNotesArchived", 0)
    cold.setdefault("totalNotesMerged", 0)
    return cold


def parse_iso_to_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        return None


def scan_notes(memory_root: Path, last_archive_date: date | None) -> list[Path]:
    all_notes = sorted(memory_root.glob("????-??-??.md"))
    if last_archive_date is None:
        return all_notes

    pending: list[Path] = []
    for path in all_notes:
        try:
            note_date = date.fromisoformat(path.stem)
        except ValueError:
            pending.append(path)
            continue
        if note_date > last_archive_date:
            pending.append(path)
    return pending


def cmd_scan(args: argparse.Namespace) -> int:
    memory_root = resolve_memory_root(args.memory_root)
    heartbeat = memory_root / "heartbeat-state.json"
    state = load_state(heartbeat)
    cold = ensure_cold_state(state)
    last_archive_date = parse_iso_to_date(cold.get("lastArchive"))
    pending = scan_notes(memory_root, last_archive_date)

    print("=== Cooling scan ===")
    print(f"Memory root: {memory_root}")
    print(f"Last scan: {cold.get('lastScan')}")
    print(f"Last archive: {cold.get('lastArchive')}\n")

    if not pending:
        print("No new daily notes pending cooling.")
    else:
        print(f"{len(pending)} daily note(s) pending cooling:")
        for path in pending:
            print(f"- {path.name}")

    cold["lastScan"] = datetime.now().astimezone().isoformat(timespec="seconds")
    save_state(heartbeat, state)
    return 0


def cmd_done(args: argparse.Namespace) -> int:
    memory_root = resolve_memory_root(args.memory_root)
    heartbeat = memory_root / "heartbeat-state.json"
    state = load_state(heartbeat)
    cold = ensure_cold_state(state)
    now = datetime.now().astimezone().isoformat(timespec="seconds")

    cold["lastArchive"] = now
    cold["lastSummary"] = f"Reviewed {args.reviewed}, archived {args.archived}, merged {args.merged}."
    cold["totalCoolings"] = int(cold.get("totalCoolings", 0)) + 1
    cold["totalNotesArchived"] = int(cold.get("totalNotesArchived", 0)) + args.archived
    cold["totalNotesMerged"] = int(cold.get("totalNotesMerged", 0)) + args.merged

    save_state(heartbeat, state)
    print(json.dumps(cold, ensure_ascii=False, indent=2))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    memory_root = resolve_memory_root(args.memory_root)
    heartbeat = memory_root / "heartbeat-state.json"
    state = load_state(heartbeat)
    cold = ensure_cold_state(state)
    print(json.dumps(cold, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["scan", "done", "status"])
    parser.add_argument("reviewed", type=int, nargs="?", default=0)
    parser.add_argument("archived", type=int, nargs="?", default=0)
    parser.add_argument("merged", type=int, nargs="?", default=0)
    parser.add_argument("--memory-root", default=None)
    args = parser.parse_args()

    if args.command == "scan":
        return cmd_scan(args)
    if args.command == "done":
        return cmd_done(args)
    return cmd_status(args)


if __name__ == "__main__":
    raise SystemExit(main())
