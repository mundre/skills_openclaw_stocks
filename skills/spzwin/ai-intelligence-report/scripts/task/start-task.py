#!/usr/bin/env python3
"""
task / start-task 脚本

用途：基于模版发起异步报告生成任务

使用方式：
  python3 scripts/task/start-task.py

环境变量：
  XG_USER_TOKEN        - access-token（必须）
  MOBAN_ID             - 模版 ID（必须）
  TASK_NAME            - 报告名称（必须）
  TASK_DIR_ID          - 目录 ID（可选）
  TASK_CONTEXT         - 上下文 JSON 字符串（可选）
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

API_URL = "https://cwork-api.mediportal.com.cn/ai-report/task/startTask"
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
    task_name = os.environ.get("TASK_NAME")
    task_dir_id = os.environ.get("TASK_DIR_ID")
    if not (token and moban_id and task_name):
        print("错误: 请设置 XG_USER_TOKEN/MOBAN_ID/TASK_NAME", file=sys.stderr)
        sys.exit(1)

    payload = {"mobanId": moban_id, "taskName": task_name}
    if task_dir_id:
        payload["dirId"] = task_dir_id
    if os.environ.get("TASK_CONTEXT"):
        payload["context"] = json.loads(os.environ["TASK_CONTEXT"])

    print(json.dumps(call_api(token, payload), ensure_ascii=False))


if __name__ == "__main__":
    main()
