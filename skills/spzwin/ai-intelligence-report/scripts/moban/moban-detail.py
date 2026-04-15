#!/usr/bin/env python3
"""
moban / moban-detail 脚本

用途：读取指定模版的章节结构与提示词配置

使用方式：
  python3 scripts/moban/moban-detail.py

环境变量：
  XG_USER_TOKEN        - access-token（必须）
  MOBAN_ID             - 模版 ID（必须）
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

API_URL = "https://cwork-api.mediportal.com.cn/ai-report/moban/mobanDetail"
AUTH_MODE = "access-token"


def call_api(token: str, moban_id: str) -> dict:
    req = urllib.request.Request(
        API_URL,
        data=json.dumps({"mobanId": moban_id}).encode("utf-8"),
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
    moban_id = os.environ.get("MOBAN_ID")
    if not (token and moban_id):
        print("错误: 请设置 XG_USER_TOKEN 与 MOBAN_ID", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(call_api(token, moban_id), ensure_ascii=False))


if __name__ == "__main__":
    main()
