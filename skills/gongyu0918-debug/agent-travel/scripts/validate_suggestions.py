#!/usr/bin/env python3
"""Validate the canonical agent-travel suggestion block."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path


START = "<!-- agent-travel:suggestions:start -->"
END = "<!-- agent-travel:suggestions:end -->"
TOP_LEVEL_REQUIRED = {
    "generated_at",
    "expires_at",
    "budget",
    "search_mode",
    "tool_preference",
    "thread_scope",
    "problem_fingerprint",
    "advisory_only",
}
ITEM_REQUIRED = {
    "title",
    "applies_when",
    "hint",
    "confidence",
    "manual_check",
    "solves_point",
    "new_idea",
    "fit_reason",
    "version_scope",
    "do_not_apply_when",
}
ISO_FIELDS = {"generated_at", "expires_at"}
INJECTION_MARKERS = ("ignore previous", "override system", "bypass guard", "ignore all")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="Path to suggestions.md")
    parser.add_argument(
        "--max-suggestions",
        type=int,
        default=5,
        help="Maximum active suggestions allowed",
    )
    parser.add_argument(
        "--max-ttl-days",
        type=int,
        default=30,
        help="Maximum allowed TTL in days",
    )
    return parser.parse_args()


def fail(errors: list[str]) -> int:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1


def parse_iso(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


def main() -> int:
    args = parse_args()
    path = Path(args.path)
    if not path.exists():
        return fail([f"file not found: {path}"])

    text = path.read_text(encoding="utf-8")
    start = text.find(START)
    end = text.find(END)
    if start == -1 or end == -1 or end <= start:
        return fail(["missing or invalid agent-travel markers"])

    block = text[start + len(START) : end].strip()
    lines = [line.rstrip() for line in block.splitlines()]

    errors: list[str] = []
    top_level: dict[str, str] = {}
    suggestions: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    current_evidence: list[str] | None = None

    key_pattern = re.compile(r"^([a-z_]+):\s*(.+)$")
    heading_pattern = re.compile(r"^##\s+suggestion-\d+\s*$")

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("# agent-travel suggestions"):
            continue
        if heading_pattern.match(line):
            current = {"evidence": []}
            suggestions.append(current)
            current_evidence = None
            continue
        if line == "evidence:":
            if current is None:
                errors.append("found evidence block before any suggestion heading")
                continue
            current_evidence = current["evidence"]  # type: ignore[assignment]
            continue
        if line.startswith("- "):
            if current_evidence is None:
                errors.append(f"unexpected evidence item outside evidence block: {line}")
                continue
            current_evidence.append(line[2:].strip())
            continue

        match = key_pattern.match(line)
        if not match:
            errors.append(f"unrecognized line: {line}")
            current_evidence = None
            continue

        key, value = match.groups()
        current_evidence = None
        if current is None:
            top_level[key] = value
        else:
            current[key] = value

    missing_top = sorted(TOP_LEVEL_REQUIRED - set(top_level))
    if missing_top:
        errors.append(f"missing top-level fields: {', '.join(missing_top)}")

    if top_level.get("advisory_only", "").lower() != "true":
        errors.append("advisory_only must be true")
    if top_level.get("thread_scope", "") != "active_conversation_only":
        errors.append("thread_scope must be active_conversation_only")

    for key in ISO_FIELDS & set(top_level):
        try:
            top_level[key] = parse_iso(top_level[key]).isoformat()
        except ValueError as exc:
            errors.append(f"{key} is not valid ISO-8601: {exc}")

    if {"generated_at", "expires_at"} <= set(top_level):
        generated = parse_iso(top_level["generated_at"])
        expires = parse_iso(top_level["expires_at"])
        ttl_days = (expires - generated).total_seconds() / 86400
        if ttl_days <= 0:
            errors.append("expires_at must be later than generated_at")
        if ttl_days > args.max_ttl_days:
            errors.append(
                f"TTL is {ttl_days:.2f} days, which exceeds --max-ttl-days={args.max_ttl_days}"
            )

    if not suggestions:
        errors.append("no suggestions found")
    if len(suggestions) > args.max_suggestions:
        errors.append(
            f"found {len(suggestions)} suggestions, which exceeds --max-suggestions={args.max_suggestions}"
        )

    for index, suggestion in enumerate(suggestions, start=1):
        missing = sorted(ITEM_REQUIRED - set(suggestion))
        if missing:
            errors.append(
                f"suggestion-{index} is missing fields: {', '.join(missing)}"
            )
        evidence = suggestion.get("evidence", [])
        if not isinstance(evidence, list) or len(evidence) < 2:
            errors.append(f"suggestion-{index} needs at least 2 evidence items")
        if isinstance(evidence, list):
            official_present = any(
                item.startswith("official:") or item.startswith("official_discussion:")
                for item in evidence
            )
            if not official_present:
                errors.append(
                    f"suggestion-{index} needs at least 1 official or official_discussion evidence item"
                )
        hint = str(suggestion.get("hint", ""))
        if any(marker in hint.lower() for marker in INJECTION_MARKERS):
            errors.append(f"suggestion-{index} hint contains policy-overriding language")

        rationale_values = {
            key: str(suggestion.get(key, "")).strip()
            for key in (
                "solves_point",
                "new_idea",
                "fit_reason",
                "version_scope",
                "do_not_apply_when",
            )
        }
        for key, value in rationale_values.items():
            if len(value) < 12:
                errors.append(
                    f"suggestion-{index} {key} is too short to be actionable"
                )
            lowered = value.lower()
            if any(marker in lowered for marker in INJECTION_MARKERS):
                errors.append(
                    f"suggestion-{index} {key} contains policy-overriding language"
                )

        if len(set(rationale_values.values())) < len(rationale_values):
            errors.append(
                f"suggestion-{index} rationale and guard fields must carry different information"
            )

    if errors:
        return fail(errors)

    print(
        f"OK: validated {len(suggestions)} suggestion(s) in {path}",
        file=sys.stdout,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
