#!/usr/bin/env python3
"""
task / list-task-by-page 脚本

用途：分页查询报告列表

使用方式：
  python3 scripts/task/list-task-by-page.py

环境变量：
  XG_USER_TOKEN        - access-token（必须）
  PAGE_NUM             - 页码，默认 0
  PAGE_SIZE            - 每页条数，默认 10
  REPORT_TYPE          - 报告来源，默认 1
  DEL_FLAG             - 删除标记，默认 0
  DIR_ID               - 目录 ID（可选）
  MOBAN_TYPE_ID        - 模版类型 ID（可选）
  STATE                - 任务状态（可选）
  SEARCH_KEY           - 关键词（可选）
  ONLY_MINE            - 是否仅看我的（可选）
  ONLY_MINE_STATUS     - 我的任务状态（可选）
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

API_URL = "https://cwork-api.mediportal.com.cn/ai-report/task/listTaskByPage"
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
        "pageNum": int(os.environ.get("PAGE_NUM", "0")),
        "pageSize": int(os.environ.get("PAGE_SIZE", "10")),
        "reportType": int(os.environ.get("REPORT_TYPE", "1")),
        "delFlag": int(os.environ.get("DEL_FLAG", "0")),
    }
    if os.environ.get("DIR_ID"):
        payload["dirId"] = os.environ["DIR_ID"]
    if os.environ.get("MOBAN_TYPE_ID"):
        payload["mobanTypeId"] = os.environ["MOBAN_TYPE_ID"]
    if os.environ.get("STATE"):
        payload["state"] = int(os.environ["STATE"])
    if os.environ.get("SEARCH_KEY"):
        payload["searchKey"] = os.environ["SEARCH_KEY"]
    if os.environ.get("ONLY_MINE"):
        payload["onlyMine"] = os.environ["ONLY_MINE"]
    if os.environ.get("ONLY_MINE_STATUS"):
        payload["onlyMineStatus"] = int(os.environ["ONLY_MINE_STATUS"])

    print(json.dumps(call_api(token, payload), ensure_ascii=False))


if __name__ == "__main__":
    main()
