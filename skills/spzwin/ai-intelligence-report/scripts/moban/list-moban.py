#!/usr/bin/env python3
"""
moban / list-moban 脚本

用途：按分页条件检索模版列表

使用方式：
  python3 scripts/moban/list-moban.py

环境变量：
  XG_USER_TOKEN        - access-token（必须）
  MOBAN_PAGE_NUM       - 页码，默认 0
  MOBAN_PAGE_SIZE      - 每页条数，默认 20
  MOBAN_DIR_ID         - 目录筛选（可选）
  MOBAN_SEARCH_KEY     - 关键词筛选（可选）
  MOBAN_ONLY_MINE      - 是否仅看我的（可选）
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

API_URL = "https://cwork-api.mediportal.com.cn/ai-report/moban/listMobanByPageV2"
AUTH_MODE = "access-token"


def call_api(token: str, payload: dict) -> dict:
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"access-token": token, "Content-Type": "application/json"},
        method="POST",
    )
    last = None
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            last = e
            if i < 2:
                time.sleep(1)
    raise last


def main() -> None:
    token = os.environ.get("XG_USER_TOKEN")
    if not token:
        print("错误: 请设置环境变量 XG_USER_TOKEN", file=sys.stderr)
        sys.exit(1)

    payload = {
        "pageNum": int(os.environ.get("MOBAN_PAGE_NUM", "0")),
        "pageSize": int(os.environ.get("MOBAN_PAGE_SIZE", "20")),
    }
    if os.environ.get("MOBAN_DIR_ID"):
        payload["dirId"] = os.environ["MOBAN_DIR_ID"]
    if os.environ.get("MOBAN_SEARCH_KEY"):
        payload["searchKey"] = os.environ["MOBAN_SEARCH_KEY"]
    if os.environ.get("MOBAN_ONLY_MINE"):
        payload["onlyMine"] = os.environ["MOBAN_ONLY_MINE"]

    print(json.dumps(call_api(token, payload), ensure_ascii=False))


if __name__ == "__main__":
    main()
