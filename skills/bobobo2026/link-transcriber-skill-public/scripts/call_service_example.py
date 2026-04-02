#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import time
from urllib import parse, request

DEFAULT_API_BASE_URL = "http://139.196.124.192/linktranscriber-api"


def infer_platform(url: str) -> str | None:
    lowered = url.lower()
    if "douyin.com" in lowered or "v.douyin.com" in lowered:
        return "douyin"
    if "xiaohongshu.com" in lowered or "xhslink.com" in lowered:
        return "xiaohongshu"
    return None


def http_json(method: str, url: str, *, payload: dict | None = None) -> dict:
    body = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = request.Request(url, data=body, headers=headers, method=method)
    with request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw)


def main() -> int:
    if len(sys.argv) not in {2, 3, 4}:
        print("Usage: call_service_example.py <url> [cookie] [platform]", file=sys.stderr)
        return 1

    base_url = os.getenv("LINK_SKILL_API_BASE_URL", DEFAULT_API_BASE_URL).strip().rstrip("/")
    provider_id = os.getenv("LINK_SKILL_SUMMARY_PROVIDER_ID", "deepseek").strip() or "deepseek"
    model_name = os.getenv("LINK_SKILL_SUMMARY_MODEL_NAME", "deepseek-chat").strip() or "deepseek-chat"

    url = sys.argv[1]
    cookie = ""
    platform = None
    if len(sys.argv) == 3:
        if sys.argv[2] in {"douyin", "xiaohongshu"}:
            platform = sys.argv[2]
        else:
            cookie = sys.argv[2]
    elif len(sys.argv) == 4:
        cookie = sys.argv[2]
        platform = sys.argv[3]
    platform = platform or infer_platform(url)
    if not platform:
        print("Platform could not be inferred. Pass platform explicitly: douyin or xiaohongshu.", file=sys.stderr)
        return 1

    create_payload = {
        "url": url,
        "platform": platform,
    }
    if cookie:
        create_payload["cookie"] = cookie
    create_result = http_json("POST", f"{base_url}/api/service/transcriptions", payload=create_payload)
    task_id = (((create_result.get("data") or {}).get("task_id")) if isinstance(create_result, dict) else None)
    if not task_id:
        print(json.dumps(create_result, ensure_ascii=False))
        return 0

    final_result = create_result
    for _ in range(20):
        polled = http_json("GET", f"{base_url}/api/service/transcriptions/{parse.quote(str(task_id))}")
        final_result = polled
        status = (((polled.get("data") or {}).get("status")) if isinstance(polled, dict) else None) or ""
        if status not in {"PENDING", "RUNNING"}:
            break
        time.sleep(1)

    final_status = (((final_result.get("data") or {}).get("status")) if isinstance(final_result, dict) else None) or ""
    if final_status != "SUCCESS":
        print(json.dumps(final_result, ensure_ascii=False))
        return 0

    summary_payload = {
        "transcription_task_id": str(task_id),
        "provider_id": provider_id,
        "model_name": model_name,
    }
    summary_result = http_json("POST", f"{base_url}/api/service/summaries", payload=summary_payload)
    summary_markdown = (((summary_result.get("data") or {}).get("summary_markdown")) if isinstance(summary_result, dict) else None)
    if summary_markdown:
        print(summary_markdown)
        return 0

    print(json.dumps(summary_result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
