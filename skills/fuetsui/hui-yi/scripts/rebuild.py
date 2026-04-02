#!/usr/bin/env python
"""Rebuild Hui-Yi index.md and tags.json from note files."""
from __future__ import annotations

import argparse
import json
import shutil
from datetime import date, datetime
from pathlib import Path

SKIP = {"index.md", "retrieval-log.md", "_template.md"}
SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parents[2]
DEFAULT_MEMORY_ROOT = WORKSPACE_ROOT / "memory" / "cold"
DEFAULT_HEARTBEAT_PATH = WORKSPACE_ROOT / "memory" / "heartbeat-state.json"


def resolve_memory_root(arg: str | None) -> Path:
    if arg:
        candidate = Path(arg)
        return candidate if candidate.is_absolute() else (Path.cwd() / candidate).resolve()
    return DEFAULT_MEMORY_ROOT


def load_json(path: Path) -> dict:
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return {}


def save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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


def parse_section_lines(lines: list[str], heading: str) -> list[str]:
    out: list[str] = []
    capture = False
    for line in lines:
        stripped_line = line.strip()
        if stripped_line == heading:
            capture = True
            continue
        if capture and stripped_line.startswith("## "):
            break
        if capture:
            if stripped_line.startswith("- "):
                out.append(stripped_line[2:].strip())
            elif stripped_line:
                out.append(stripped_line)
    return out


def parse_single_value(lines: list[str], heading: str) -> str:
    values = parse_section_lines(lines, heading)
    return values[0] if values else ""


def parse_note(path: Path, memory_root: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    title = next((line[2:].strip() for line in lines if line.startswith("# ")), path.stem)
    summary_lines = parse_section_lines(lines, "## TL;DR")
    memory_type = parse_single_value(lines, "## Memory type") or "unknown"
    semantic_context = " ".join(parse_section_lines(lines, "## Semantic context"))
    triggers = parse_section_lines(lines, "## Triggers")
    scenarios = parse_section_lines(lines, "## Use this when")
    confidence = parse_single_value(lines, "## Confidence") or "unknown"
    last_verified = parse_single_value(lines, "## Last verified") or "unknown"
    tags = parse_section_lines(lines, "## Related tags")

    rel_path = path.relative_to(memory_root.parent).as_posix()
    summary = summary_lines[0] if summary_lines else title

    return {
        "title": title,
        "path": rel_path,
        "type": memory_type,
        "summary": summary,
        "semantic_context": semantic_context,
        "tags": tags,
        "triggers": triggers,
        "scenarios": scenarios,
        "confidence": confidence,
        "last_verified": last_verified,
        "updated": last_verified,
    }


def note_paths(memory_root: Path) -> list[Path]:
    paths = []
    for path in memory_root.rglob("*.md"):
        if path.name in SKIP:
            continue
        if path.parent == memory_root or path.parent.parent == memory_root:
            paths.append(path)
    return sorted(paths)


def backup_if_exists(path: Path) -> None:
    if path.exists():
        shutil.copy2(path, path.with_suffix(path.suffix + ".bak"))


def build_index(notes: list[dict]) -> str:
    lines = ["# Cold Memory Index", "", "## Entries", ""]
    notes_sorted = sorted(notes, key=lambda n: n.get("updated", ""), reverse=True)
    for note in notes_sorted:
        lines.append(f"- `{Path(note['path']).name}` — {note['summary']}")
        lines.append(f"  - type: {note['type']}")
        lines.append(f"  - tags: {', '.join(note['tags']) if note['tags'] else 'none'}")
        lines.append(f"  - triggers: {', '.join(note['triggers']) if note['triggers'] else 'none'}")
        lines.append(f"  - read when: {'; '.join(note['scenarios']) if note['scenarios'] else 'n/a'}")
        lines.append(f"  - confidence: {note['confidence']}")
        lines.append(f"  - updated: {note['updated']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_tags(notes: list[dict]) -> str:
    payload = {
        "_meta": {
            "description": "Structured metadata for cold-memory retrieval",
            "version": 3,
            "updated": date.today().isoformat(),
        },
        "notes": notes,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def update_heartbeat_index_refresh(heartbeat_path: Path, note_count: int) -> None:
    state = load_json(heartbeat_path)
    cold = ensure_cold_state(state)
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    cold["lastIndexRefresh"] = now
    cold["lastSummary"] = f"Rebuilt cold-memory index and tags from {note_count} note(s)."
    save_json(heartbeat_path, state)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--memory-root", default=None)
    parser.add_argument("--heartbeat-path", default=None)
    args = parser.parse_args()

    memory_root = resolve_memory_root(args.memory_root)
    heartbeat_path = Path(args.heartbeat_path).resolve() if args.heartbeat_path else DEFAULT_HEARTBEAT_PATH
    index_path = memory_root / "index.md"
    tags_path = memory_root / "tags.json"

    if not memory_root.exists():
        print(f"memory root not found: {memory_root}")
        return 1

    notes = [parse_note(path, memory_root) for path in note_paths(memory_root)]
    backup_if_exists(index_path)
    backup_if_exists(tags_path)
    index_path.write_text(build_index(notes), encoding="utf-8")
    tags_path.write_text(build_tags(notes), encoding="utf-8")
    update_heartbeat_index_refresh(heartbeat_path, len(notes))
    print(f"Rebuilt index.md and tags.json from {len(notes)} note(s).")
    print(f"memory root: {memory_root}")
    print(f"heartbeat: {heartbeat_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
