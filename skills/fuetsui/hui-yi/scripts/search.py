#!/usr/bin/env python
"""Search Hui-Yi cold memory index and tags metadata."""
from __future__ import annotations

import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parents[2]
DEFAULT_MEMORY_ROOT = WORKSPACE_ROOT / "memory" / "cold"


def resolve_memory_root(arg: str | None) -> Path:
    if arg:
        candidate = Path(arg)
        return candidate if candidate.is_absolute() else (Path.cwd() / candidate).resolve()
    return DEFAULT_MEMORY_ROOT


def load_tags(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        notes = data.get("notes", [])
        return notes if isinstance(notes, list) else []
    if isinstance(data, list):
        return data
    return []


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/search.py <keyword> [memory_root]")
        return 1

    keyword_raw = sys.argv[1]
    keyword = keyword_raw.lower()
    memory_root = resolve_memory_root(sys.argv[2] if len(sys.argv) >= 3 else None)
    index_path = memory_root / "index.md"
    tags_path = memory_root / "tags.json"

    print(f"=== Searching cold memory for: {keyword_raw} ===\n")

    if index_path.exists():
        lines = index_path.read_text(encoding="utf-8").splitlines()
        hits = [(i + 1, line) for i, line in enumerate(lines) if keyword in line.lower()]
        if hits:
            print("## index.md matches:")
            for line_no, line in hits:
                print(f"{line_no}: {line}")
            print()
        else:
            print("## No matches in index.md\n")
    else:
        print(f"## index.md not found at {index_path}\n")

    notes = load_tags(tags_path)
    if notes:
        matched = []
        for note in notes:
            haystacks = [
                note.get("title", ""),
                note.get("summary", ""),
                note.get("semantic_context", ""),
                " ".join(note.get("tags", []) if isinstance(note.get("tags"), list) else []),
                " ".join(note.get("triggers", []) if isinstance(note.get("triggers"), list) else []),
                " ".join(note.get("scenarios", []) if isinstance(note.get("scenarios"), list) else []),
            ]
            if keyword in " ".join(haystacks).lower():
                matched.append(note)

        if matched:
            print("## tags.json matches:")
            for note in matched:
                print(f"- {note.get('title', 'untitled')} -> {note.get('path', '(missing path)')}")
            print()
        else:
            print("## No matches in tags.json")
    else:
        print(f"## tags.json not found or empty at {tags_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
