#!/usr/bin/env python3
"""Shared timestamp parsing and lookback helpers."""

from __future__ import annotations

from datetime import datetime, timedelta

from zoneinfo import ZoneInfo

from normalize import normalize_text


SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")


def now_shanghai() -> datetime:
    return datetime.now(SHANGHAI_TZ)


def parse_timestamp(value: str) -> datetime | None:
    cleaned = normalize_text(value)
    if not cleaned:
        return None

    iso_candidate = cleaned.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(iso_candidate)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=SHANGHAI_TZ)
        return dt.astimezone(SHANGHAI_TZ)
    except ValueError:
        pass

    formats = (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%Y/%m/%d",
    )
    for fmt in formats:
        try:
            dt = datetime.strptime(cleaned, fmt)
            return dt.replace(tzinfo=SHANGHAI_TZ)
        except ValueError:
            continue
    return None


def within_lookback(dt: datetime | None, lookback_hours: int, now: datetime | None = None) -> bool:
    if dt is None:
        return False
    anchor = now or now_shanghai()
    return dt >= anchor - timedelta(hours=lookback_hours)


def isoformat_or_empty(dt: datetime | None) -> str:
    if dt is None:
        return ""
    return dt.isoformat()
