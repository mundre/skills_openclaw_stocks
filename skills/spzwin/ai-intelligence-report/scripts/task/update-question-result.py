#!/usr/bin/env python3
"""
task / update-question-result 脚本

用途：覆盖指定子章节内容

使用方式：
  python3 scripts/task/update-question-result.py

环境变量：
  XG_USER_TOKEN        - access-token（必须）
  QUESTION_ID          - 子章节 ID（必须）
  RESULT               - 新章节内容（必须）
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

API_URL = "https://cwork-api.mediportal.com.cn/ai-report/task/updateQuestionResult"
AUTH_MODE = "access-token"


def call_api(token: str, question_id: str, result: str) -> dict:
    req = urllib.request.Request(
        API_URL,
        data=json.dumps({"questionId": question_id, "result": result}).encode("utf-8"),
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
    question_id = os.environ.get("QUESTION_ID")
    result = os.environ.get("RESULT")
    if not (token and question_id and result):
        print("错误: 请设置 XG_USER_TOKEN/QUESTION_ID/RESULT", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(call_api(token, question_id, result), ensure_ascii=False))


if __name__ == "__main__":
    main()
