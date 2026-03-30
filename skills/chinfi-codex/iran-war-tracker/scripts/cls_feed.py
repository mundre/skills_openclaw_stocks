#!/usr/bin/env python3
"""Market telegraph fetchers for CLS and Jin10 with Iran-focused filtering."""

from __future__ import annotations

import hashlib
import time
from datetime import datetime
from typing import Any

import pandas as pd
import requests

from config import (
    CLS_COLUMNS,
    CLS_CONTEXT_HINTS,
    CLS_NOISE_KEYWORDS,
    CLS_TOPIC_TAG_HINTS,
    DEFAULT_LOOKBACK_HOURS,
    DEFAULT_TIMEOUT,
    TOPIC_HINTS,
)
from normalize import compact_snippet, contains_any, filter_blank_records, lowercase_text, normalize_text
from time_utils import isoformat_or_empty, now_shanghai, parse_timestamp, within_lookback


DEFAULT_CLS_RN = 2000
CLS_URL = "https://www.cls.cn/nodeapi/telegraphList"
JIN10_URL = "https://flash-api.jin10.com/get_flash_list?channel=-8200&vip=1"


def build_signed_cls_params(session: requests.Session, rn: int = DEFAULT_CLS_RN, timeout: int = DEFAULT_TIMEOUT) -> dict[str, Any]:
    current_time = int(time.time())
    params: dict[str, Any] = {
        "app": "CailianpressWeb",
        "category": "",
        "lastTime": current_time,
        "last_time": current_time,
        "os": "web",
        "refresh_type": "1",
        "rn": str(rn),
        "sv": "7.7.5",
    }
    query_string = session.get(CLS_URL, params=params, timeout=timeout).url.split("?", 1)[1]
    sha1 = hashlib.sha1(query_string.encode("utf-8")).hexdigest()
    params["sign"] = hashlib.md5(sha1.encode("utf-8")).hexdigest()
    return params


def fetch_cls_records(
    session: requests.Session,
    rn: int = DEFAULT_CLS_RN,
    timeout: int = DEFAULT_TIMEOUT,
) -> list[dict[str, Any]]:
    params = build_signed_cls_params(session, rn=rn, timeout=timeout)
    response = session.get(
        CLS_URL,
        params=params,
        headers={
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://www.cls.cn/telegraph",
            "User-Agent": "Mozilla/5.0",
        },
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    records = payload.get("data", {}).get("roll_data", [])
    if not isinstance(records, list):
        raise ValueError("Unexpected CLS response: data.roll_data is not a list")
    return [record for record in records if isinstance(record, dict)]


def fetch_jin10_payload(session: requests.Session, timeout: int = DEFAULT_TIMEOUT) -> dict[str, Any]:
    response = session.get(
        JIN10_URL,
        headers={
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
            "content-type": "application/x-www-form-urlencoded",
            "handleerror": "true",
            "origin": "https://www.jin10.com",
            "referer": "https://www.jin10.com/",
            "sec-ch-ua": '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
            ),
            "x-app-id": "bVBF4FyRTn5NJF5n",
            "x-version": "1.0.0",
        },
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("Unexpected Jin10 response: payload is not an object")
    return payload


def _join_subject_names(subjects: Any) -> str:
    if not isinstance(subjects, list):
        return ""
    values = [normalize_text(item.get("subject_name", "")) for item in subjects if isinstance(item, dict)]
    return ",".join(value for value in values if value)


def _join_tag_values(values: Any) -> str:
    if not isinstance(values, list):
        return ""
    tags: list[str] = []
    for value in values:
        if isinstance(value, str):
            cleaned = normalize_text(value)
        elif isinstance(value, dict):
            cleaned = normalize_text(value.get("name") or value.get("tag") or value.get("value"))
        else:
            cleaned = normalize_text(value)
        if cleaned:
            tags.append(cleaned)
    return ",".join(tags)


def _date_and_time_from_string(value: str) -> tuple[str, str]:
    cleaned = normalize_text(value)
    if not cleaned:
        return "", ""
    parsed = parse_timestamp(cleaned)
    if parsed is not None:
        return parsed.strftime("%Y-%m-%d"), parsed.strftime("%H:%M:%S")
    parts = cleaned.split(" ", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return "", cleaned


def normalize_cls_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not records:
        return []

    df = pd.DataFrame(records)
    for column in ["title", "content", "level", "subjects", "ctime"]:
        if column not in df.columns:
            df[column] = None

    normalized = df[["title", "content", "level", "subjects", "ctime"]].copy()
    normalized["ctime"] = pd.to_datetime(normalized["ctime"], unit="s", utc=True, errors="coerce").dt.tz_convert(
        "Asia/Shanghai"
    )

    items: list[dict[str, Any]] = []
    for item in normalized.to_dict("records"):
        dt = item.get("ctime")
        py_dt = dt.to_pydatetime() if pd.notna(dt) else None
        date_text = dt.strftime("%Y-%m-%d") if pd.notna(dt) else ""
        time_text = dt.strftime("%H:%M:%S") if pd.notna(dt) else ""
        items.append(
            {
                "source": "cls",
                CLS_COLUMNS["date"]: date_text,
                CLS_COLUMNS["time"]: time_text,
                CLS_COLUMNS["title"]: normalize_text(item.get("title", "")),
                CLS_COLUMNS["content"]: normalize_text(item.get("content", "")),
                CLS_COLUMNS["tags"]: _join_subject_names(item.get("subjects")),
                CLS_COLUMNS["level"]: normalize_text(item.get("level", "")),
                "published_at": isoformat_or_empty(py_dt),
            }
        )
    return filter_blank_records(items)


def normalize_jin10_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    records = payload.get("data", [])
    if not isinstance(records, list):
        raise ValueError("Unexpected Jin10 response: data is not a list")

    items: list[dict[str, Any]] = []
    for item in records:
        if not isinstance(item, dict):
            continue
        item_data = item.get("data", {})
        if not isinstance(item_data, dict):
            item_data = {}
        date_text, time_text = _date_and_time_from_string(normalize_text(item.get("time", "")))
        tags = _join_tag_values(item.get("tags"))
        channel = _join_tag_values(item.get("channel"))
        if channel:
            tags = ",".join(part for part in [tags, channel] if part)
        published_at = parse_timestamp(" ".join(part for part in [date_text, time_text] if part))
        items.append(
            {
                "source": "jin10",
                CLS_COLUMNS["date"]: date_text,
                CLS_COLUMNS["time"]: time_text,
                CLS_COLUMNS["title"]: normalize_text(item_data.get("title", "")),
                CLS_COLUMNS["content"]: normalize_text(item_data.get("content", "")),
                CLS_COLUMNS["tags"]: tags,
                CLS_COLUMNS["level"]: str(item.get("important", "")) if item.get("important") is not None else "",
                "id": normalize_text(item.get("id", "")),
                "type": str(item.get("type", "")) if item.get("type") is not None else "",
                "source_name": normalize_text(item_data.get("source", "")),
                "source_link": normalize_text(item_data.get("source_link", "")),
                "published_at": isoformat_or_empty(published_at),
            }
        )
    return filter_blank_records(items)


def merge_telegraph_items(cls_items: list[dict[str, Any]], jin10_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        [*cls_items, *jin10_items],
        key=lambda item: normalize_text(item.get("published_at", "")),
        reverse=True,
    )


def _keyword_hits(text: str, keywords: list[str]) -> int:
    lowered = text.lower()
    return sum(1 for keyword in keywords if keyword.lower() in lowered)


def _telegraph_score(title: str, content: str, tags: str) -> int:
    haystack = lowercase_text(title, content, tags)
    title_and_tags = lowercase_text(title, tags)
    if not haystack:
        return 0
    if contains_any(title_and_tags, CLS_NOISE_KEYWORDS):
        return 0

    primary_hits = _keyword_hits(haystack, TOPIC_HINTS)
    topic_tag_hits = _keyword_hits(tags, CLS_TOPIC_TAG_HINTS)
    context_hits = _keyword_hits(haystack, CLS_CONTEXT_HINTS)

    if primary_hits == 0 and topic_tag_hits == 0:
        return 0

    return primary_hits * 3 + topic_tag_hits * 2 + context_hits


def _telegraph_fingerprint(item: dict[str, Any]) -> str:
    return lowercase_text(
        item.get("source", ""),
        item.get(CLS_COLUMNS["date"], ""),
        item.get(CLS_COLUMNS["time"], ""),
        item.get(CLS_COLUMNS["title"], ""),
        compact_snippet(item.get(CLS_COLUMNS["content"], ""), limit=120),
    )


def filter_telegraph_items(
    items: list[dict[str, Any]],
    limit: int = 20,
    lookback_hours: int = DEFAULT_LOOKBACK_HOURS,
) -> list[dict[str, Any]]:
    if not items:
        return []

    filtered: list[dict[str, Any]] = []
    seen_fingerprints: set[str] = set()
    anchor = now_shanghai()
    for item in items:
        published_at = parse_timestamp(normalize_text(item.get("published_at", "")))
        if not within_lookback(published_at, lookback_hours, now=anchor):
            continue

        title = normalize_text(item.get(CLS_COLUMNS["title"], ""))
        content = normalize_text(item.get(CLS_COLUMNS["content"], ""))
        tags = normalize_text(item.get(CLS_COLUMNS["tags"], ""))
        score = _telegraph_score(title=title, content=content, tags=tags)
        if score < 3:
            continue

        fingerprint = _telegraph_fingerprint(item)
        if fingerprint in seen_fingerprints:
            continue
        seen_fingerprints.add(fingerprint)

        filtered.append(
            {
                **item,
                CLS_COLUMNS["title"]: compact_snippet(title, limit=90),
                CLS_COLUMNS["content"]: compact_snippet(content, limit=160),
                CLS_COLUMNS["tags"]: tags,
            }
        )
        if len(filtered) >= limit:
            break
    return filter_blank_records(filtered)


def build_telegraph_payload(
    session: requests.Session,
    source: str = "all",
    output_format: str = "normalized",
    limit: int | None = None,
    lookback_hours: int = DEFAULT_LOOKBACK_HOURS,
    timeout: int = DEFAULT_TIMEOUT,
    cls_rn: int = DEFAULT_CLS_RN,
) -> Any:
    if source not in {"all", "cls", "jin10"}:
        raise ValueError(f"Unsupported source: {source}")
    if output_format not in {"raw", "normalized"}:
        raise ValueError(f"Unsupported output format: {output_format}")

    cls_records: list[dict[str, Any]] = []
    jin10_payload: dict[str, Any] = {}
    if source in {"all", "cls"}:
        cls_records = fetch_cls_records(session, rn=cls_rn, timeout=timeout)
    if source in {"all", "jin10"}:
        jin10_payload = fetch_jin10_payload(session, timeout=timeout)

    if output_format == "raw":
        if source == "cls":
            return cls_records[:limit] if limit is not None else cls_records
        if source == "jin10":
            if limit is None:
                return jin10_payload
            payload = dict(jin10_payload)
            data = payload.get("data", [])
            if isinstance(data, list):
                payload["data"] = data[:limit]
            return payload
        payload: dict[str, Any] = {}
        payload["cls"] = cls_records[:limit] if limit is not None else cls_records
        payload["jin10"] = dict(jin10_payload)
        if limit is not None:
            data = payload["jin10"].get("data", [])
            if isinstance(data, list):
                payload["jin10"]["data"] = data[:limit]
        return payload

    cls_items = normalize_cls_records(cls_records) if cls_records else []
    jin10_items = normalize_jin10_items(jin10_payload) if jin10_payload else []
    if source == "cls":
        items = cls_items
    elif source == "jin10":
        items = jin10_items
    else:
        items = merge_telegraph_items(cls_items, jin10_items)
    items = filter_telegraph_items(items, limit=limit or len(items), lookback_hours=lookback_hours)
    return items[:limit] if limit is not None else items


def collect_filtered_telegraph(
    session: requests.Session,
    limit: int = 20,
    lookback_hours: int = DEFAULT_LOOKBACK_HOURS,
    timeout: int = DEFAULT_TIMEOUT,
    cls_rn: int = DEFAULT_CLS_RN,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    cls_items = normalize_cls_records(fetch_cls_records(session, rn=cls_rn, timeout=timeout))
    jin10_items = normalize_jin10_items(fetch_jin10_payload(session, timeout=timeout))
    merged_items = merge_telegraph_items(cls_items, jin10_items)
    filtered_items = filter_telegraph_items(merged_items, limit=limit, lookback_hours=lookback_hours)
    counts = {
        "cls_items": len(cls_items),
        "jin10_items": len(jin10_items),
        "telegraph_items": len(filtered_items),
        "telegraph_items_in_window": len(filtered_items),
        "telegraph_total_before_window": len(merged_items),
    }
    return filtered_items, counts


def telegraph_lines(items: list[dict[str, Any]], limit: int = 6) -> list[str]:
    lines: list[str] = []
    for item in items[:limit]:
        parts = [
            normalize_text(item.get("source", "")),
            normalize_text(item.get(CLS_COLUMNS["time"], "")),
            normalize_text(item.get(CLS_COLUMNS["title"], "")),
            normalize_text(item.get(CLS_COLUMNS["content"], "")),
        ]
        line = " | ".join(part for part in parts if part)
        if line:
            lines.append(line)
    return lines
