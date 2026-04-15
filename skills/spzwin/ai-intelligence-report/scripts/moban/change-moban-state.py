#!/usr/bin/env python3
"""
moban / change-moban-state 脚本

用途：模版发布/下架

使用方式：
  python3 scripts/moban/change-moban-state.py

环境变量：
  XG_USER_TOKEN                - access-token（必须）
  MOBAN_ID                     - 模版 ID（必须）
  MOBAN_STATE                  - 模版状态（必须，0 下架 / 1 上架）
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

API_URL = "https://cwork-api.mediportal.com.cn/ai-report/moban/changeMobanState"
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
    moban_id = os.environ.get("MOBAN_ID")
    state_raw = os.environ.get("MOBAN_STATE")

    if not token:
        print("错误: 请设置环境变量 XG_USER_TOKEN", file=sys.stderr)
        sys.exit(1)
    if not moban_id:
        print("错误: 请设置环境变量 MOBAN_ID", file=sys.stderr)
        sys.exit(1)
    if state_raw is None:
        print("错误: 请设置环境变量 MOBAN_STATE（0/1）", file=sys.stderr)
        sys.exit(1)

    try:
        state = int(state_raw)
    except ValueError:
        print("错误: MOBAN_STATE 必须是 0 或 1", file=sys.stderr)
        sys.exit(1)

    if state not in (0, 1):
        print("错误: MOBAN_STATE 只能是 0 或 1", file=sys.stderr)
        sys.exit(1)

    payload = {"mobanId": moban_id, "state": state}
    print(json.dumps(call_api(token, payload), ensure_ascii=False))


if __name__ == "__main__":
    main()
