#!/usr/bin/env python3
"""Pure helpers for cleaning and shaping tracker data."""

from __future__ import annotations

from typing import Any


def normalize_text(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def lowercase_text(*parts: Any) -> str:
    return " ".join(normalize_text(part) for part in parts if normalize_text(part)).lower()


def compact_snippet(value: Any, limit: int = 180) -> str:
    text = normalize_text(value)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def unique_strings(items: list[str], limit: int | None = None) -> list[str]:
    seen: list[str] = []
    for item in items:
        cleaned = normalize_text(item)
        if cleaned and cleaned not in seen:
            seen.append(cleaned)
        if limit is not None and len(seen) >= limit:
            break
    return seen


def contains_any(text: str, keywords: list[str]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def filter_blank_records(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [item for item in items if any(normalize_text(value) for value in item.values())]
