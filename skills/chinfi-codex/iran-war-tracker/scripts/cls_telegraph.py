#!/usr/bin/env python3
"""Thin CLI entrypoint for merged market telegraph collection."""

from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

import requests

from config import DEFAULT_LOOKBACK_HOURS
from cls_feed import build_telegraph_payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch merged CLS and Jin10 telegraph items for Iran tracker.")
    parser.add_argument("--output", help="Optional path to write telegraph data as JSON.")
    parser.add_argument("--limit", type=int, default=20, help="Maximum items to return.")
    parser.add_argument("--hours", type=int, default=DEFAULT_LOOKBACK_HOURS, help="Lookback window in hours. Default: 18.")
    parser.add_argument(
        "--source",
        choices=["all", "cls", "jin10"],
        default="all",
        help="Select telegraph source. Default: all.",
    )
    parser.add_argument(
        "--format",
        choices=["normalized", "raw"],
        default="normalized",
        help="Output normalized merged records or raw source payloads. Default: normalized.",
    )
    return parser.parse_args()


def get_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": "iran-war-tracker-telegraph/2.0"})
    return session


def main() -> int:
    args = parse_args()
    session = get_session()
    payload = build_telegraph_payload(
        session=session,
        source=args.source,
        output_format=args.format,
        limit=args.limit,
        lookback_hours=args.hours,
    )
    content = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(content, encoding="utf-8")
    else:
        print(content)
    return 0


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main())
