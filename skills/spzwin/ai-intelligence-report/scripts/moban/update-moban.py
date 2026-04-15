#!/usr/bin/env python3
"""
moban / update-moban 脚本

用途：编辑已有模版

使用方式：
  python3 scripts/moban/update-moban.py

环境变量：
  XG_USER_TOKEN                - access-token（必须）
  MOBAN_ID                     - 模版 ID（必须）
  MOBAN_NAME                   - 模版名称（必须）
  MOBAN_SECTION_LIST           - 章节结构 JSON 字符串（必须）
  MOBAN_DESC                   - 模版描述（可选）
  MOBAN_DIR_ID                 - 目录 ID（可选）
  MOBAN_TYPE_ID                - 模版类型 ID（可选）
  MOBAN_PROMPT                 - 任务级提示词（可选）
  MOBAN_EDIT_NOTE              - 改动日志（可选）
  MOBAN_PUBLIC                 - 公开状态（可选，0/1）
  MOBAN_THIRD_SYSTEM           - 第三方系统标识（可选）
  MOBAN_DO_SUMMARY             - 是否总结（可选，0/1/2）
  MOBAN_SUMMARY_PROMPT         - 总结提示词（可选）
  MOBAN_AI_TYPE                - AI 类型（可选）
  MOBAN_REQUIRE_CONTEXT        - 上下文字段 JSON 字符串（可选，string[]）
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

API_URL = "https://cwork-api.mediportal.com.cn/ai-report/moban/updateMoban"
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


def parse_json_env(env_name: str, default):
    raw = os.environ.get(env_name)
    if not raw:
        return default
    return json.loads(raw)


def main() -> None:
    token = os.environ.get("XG_USER_TOKEN")
    moban_id = os.environ.get("MOBAN_ID")
    name = os.environ.get("MOBAN_NAME")
    if not token:
        print("错误: 请设置环境变量 XG_USER_TOKEN", file=sys.stderr)
        sys.exit(1)
    if not moban_id:
        print("错误: 请设置环境变量 MOBAN_ID", file=sys.stderr)
        sys.exit(1)
    if not name:
        print("错误: 请设置环境变量 MOBAN_NAME", file=sys.stderr)
        sys.exit(1)

    try:
        section_list = parse_json_env("MOBAN_SECTION_LIST", None)
        if not isinstance(section_list, list) or len(section_list) == 0:
            print("错误: MOBAN_SECTION_LIST 必须是非空 JSON 数组", file=sys.stderr)
            sys.exit(1)
        require_context = parse_json_env("MOBAN_REQUIRE_CONTEXT", None)
    except json.JSONDecodeError as exc:
        print(f"错误: JSON 环境变量解析失败: {exc}", file=sys.stderr)
        sys.exit(1)

    payload = {
        "mobanId": moban_id,
        "name": name,
        "sectionList": section_list,
    }
    if os.environ.get("MOBAN_DESC"):
        payload["desc"] = os.environ["MOBAN_DESC"]
    if os.environ.get("MOBAN_DIR_ID"):
        payload["dirId"] = os.environ["MOBAN_DIR_ID"]
    if os.environ.get("MOBAN_TYPE_ID"):
        payload["mobanTypeId"] = os.environ["MOBAN_TYPE_ID"]
    if os.environ.get("MOBAN_PROMPT"):
        payload["prompt"] = os.environ["MOBAN_PROMPT"]
    if os.environ.get("MOBAN_EDIT_NOTE"):
        payload["editNote"] = os.environ["MOBAN_EDIT_NOTE"]
    if os.environ.get("MOBAN_PUBLIC"):
        payload["public"] = int(os.environ["MOBAN_PUBLIC"])
    if os.environ.get("MOBAN_THIRD_SYSTEM"):
        payload["thirdSystem"] = os.environ["MOBAN_THIRD_SYSTEM"]
    if os.environ.get("MOBAN_DO_SUMMARY"):
        payload["doSummary"] = int(os.environ["MOBAN_DO_SUMMARY"])
    if os.environ.get("MOBAN_SUMMARY_PROMPT"):
        payload["summaryPrompt"] = os.environ["MOBAN_SUMMARY_PROMPT"]
    if os.environ.get("MOBAN_AI_TYPE"):
        payload["aiType"] = os.environ["MOBAN_AI_TYPE"]
    if require_context is not None:
        payload["requireContext"] = require_context

    print(json.dumps(call_api(token, payload), ensure_ascii=False))


if __name__ == "__main__":
    main()
