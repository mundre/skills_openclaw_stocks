#!/usr/bin/env python3
"""Output helpers for markdown and JSON payloads."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from schemas import ReportContext


def build_json_payload(context: ReportContext, report_markdown: str = "") -> dict[str, Any]:
    payload = context.to_dict()
    if report_markdown:
        payload["report_markdown"] = report_markdown
    return payload


def write_markdown(path: str, markdown: str) -> None:
    Path(path).write_text(markdown, encoding="utf-8")


def write_json(path: str, payload: dict[str, Any]) -> None:
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
