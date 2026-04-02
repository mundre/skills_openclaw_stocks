#!/usr/bin/env python
"""Decay Hui-Yi note confidence by last_verified age."""
from __future__ import annotations

import argparse
import re
from datetime import date, datetime
from pathlib import Path

SKIP = {"index.md", "retrieval-log.md", "_template.md"}
SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parents[2]
DEFAULT_MEMORY_ROOT = WORKSPACE_ROOT / "memory" / "cold"


def resolve_memory_root(arg: str | None) -> Path:
    if arg:
        candidate = Path(arg)
        return candidate if candidate.is_absolute() else (Path.cwd() / candidate).resolve()
    return DEFAULT_MEMORY_ROOT


def parse_date(value: str) -> date | None:
    value = value.strip()
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def update_confidence_text(text: str, new_value: str) -> str:
    pattern = re.compile(r"(^## Confidence\s*\n)(-\s*)?(high|medium|low)(\s*$)", re.MULTILINE)
    return pattern.sub(lambda m: f"{m.group(1)}- {new_value}{m.group(4)}", text, count=1)


def parse_confidence(text: str) -> str | None:
    match = re.search(r"^## Confidence\s*\n(?:-\s*)?(high|medium|low)\s*$", text, re.MULTILINE)
    return match.group(1) if match else None


def parse_last_verified(text: str) -> date | None:
    match = re.search(r"^## Last verified\s*\n(?:-\s*)?([^\n]+)\s*$", text, re.MULTILINE)
    return parse_date(match.group(1)) if match else None


def iter_notes(root: Path):
    for path in root.rglob("*.md"):
        if path.name in SKIP:
            continue
        yield path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--memory-root", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = resolve_memory_root(args.memory_root)
    today = date.today()
    changes = []
    stale = []

    for path in iter_notes(root):
        text = path.read_text(encoding="utf-8")
        confidence = parse_confidence(text)
        verified = parse_last_verified(text)
        if not confidence or not verified:
            continue
        age = (today - verified).days
        target = None
        if age > 180 and confidence == "low":
            stale.append((path, age))
        elif age > 90 and confidence == "high":
            target = "medium"
        elif age > 90 and confidence == "medium":
            target = "low"
        if target:
            changes.append((path, confidence, target, age))
            if not args.dry_run:
                path.write_text(update_confidence_text(text, target), encoding="utf-8")

    if not changes and not stale:
        print(f"No decay needed. memory root: {root}")
        return 0

    for path, old, new, age in changes:
        print(f"DECAY: {path} — {old} -> {new} ({age} days)")
    for path, age in stale:
        print(f"STALE: {path} — {age} days, confidence low")

    if args.dry_run:
        print("Dry run only; no files modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
