#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AIDSO GEO 内容生产轮询脚本

用途：
- 轮询 GEO内容生产结果
- 成功时原样输出 data.final_article
- 不做任何改写、拆分、重组

用法：
    python content_poll.py "欧莱雅小蜜罐" "30岁左右抗老面霜推荐有哪些？" "DB"
    python content_poll.py "欧莱雅小蜜罐" "30岁左右抗老面霜推荐有哪些？" "DB" --api-key your_key
    python content_poll.py "欧莱雅小蜜罐" "30岁左右抗老面霜推荐有哪些？" "DB" --interval 60 --max-attempts 30

环境变量：
    AIDSO_GEO_API_KEY   可选，若未传 --api-key，则从环境变量读取
"""

import sys
import os
import json
import time
import argparse
import requests

API_URL = "https://api.aidso.com/openapi/skills/geo_content/generate"
API_KEY_URL = "https://geo.aidso.com/setting?type=apiKey&platform=GEO"
PURCHASE_POINTS_URL = "https://geo.aidso.com"

DEFAULT_INTERVAL_SECONDS = 60
DEFAULT_MAX_ATTEMPTS = 30


def out_text(msg: str) -> None:
    print(msg, flush=True)


def out_debug(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def build_auth_headers(api_key: str) -> dict:
    return {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }


def normalize_code(code):
    if code is None:
        return None
    try:
        return int(code)
    except Exception:
        return code


def get_backend_msg(data: dict) -> str:
    if not isinstance(data, dict):
        return ""
    msg = data.get("msg")
    if isinstance(msg, str) and msg.strip():
        return msg.strip()
    message = data.get("message")
    if isinstance(message, str) and message.strip():
        return message.strip()
    return ""


def format_backend_error_message(msg: str) -> str:
    if not msg:
        return "接口返回错误"
    if "积分不足" in msg:
        return f"{msg}\n请前往{PURCHASE_POINTS_URL} 购买积分"
    return msg


def is_invalid_token_response(data: dict) -> bool:
    if not isinstance(data, dict):
        return False
    code = normalize_code(data.get("code"))
    msg = get_backend_msg(data).lower()
    return code == 401 or "invalid token" in msg or "鉴权失败" in msg


def is_processing_response(data: dict) -> bool:
    if not isinstance(data, dict):
        return False
    code = normalize_code(data.get("code"))
    msg = get_backend_msg(data).lower()
    return (
        code == 405
        or "处理中" in msg
        or "processing" in msg
        or "请稍后" in msg
        or "正在处理中" in msg
    )


def extract_final_article(data: dict) -> str | None:
    if not isinstance(data, dict):
        return None
    payload = data.get("data")
    if not isinstance(payload, dict):
        return None
    final_article = payload.get("final_article")
    if isinstance(final_article, str) and final_article.strip():
        return final_article
    return None


def parse_json_utf8(resp: requests.Response) -> dict:
    raw = resp.content
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        pass
    try:
        return resp.json()
    except Exception:
        pass
    return json.loads(resp.text)


def request_content(brand: str, issue: str, platform: str, api_key: str) -> dict:
    payload = {
        "brand": brand,
        "issue": issue,
        "platform": platform,
    }

    resp = requests.post(
        API_URL,
        headers=build_auth_headers(api_key),
        json=payload,
        timeout=180,
    )
    resp.raise_for_status()
    return parse_json_utf8(resp)


def poll_content(brand: str, issue: str, platform: str, api_key: str, interval_seconds: int, max_attempts: int):
    for attempt in range(1, max_attempts + 1):
        out_debug(
            f"[DEBUG] polling attempt={attempt}/{max_attempts}, brand={brand}, platform={platform}"
        )

        data = request_content(brand, issue, platform, api_key)

        if is_invalid_token_response(data):
            return (
                "text",
                f"当前绑定的 API key 已失效或不正确，请重新输入你在后台创建的 API key 完成绑定。\n"
                f"获取地址：{API_KEY_URL}"
            )

        final_article = extract_final_article(data)
        if normalize_code(data.get("code")) == 200 and final_article:
            return ("text", final_article)

        if is_processing_response(data):
            if attempt < max_attempts:
                time.sleep(interval_seconds)
                continue
            return ("text", "GEO内容暂未生成完成，请稍后请求获取结果。")

        msg = get_backend_msg(data)
        return ("text", format_backend_error_message(msg or json.dumps(data, ensure_ascii=False)))

    return ("text", "GEO内容暂未生成完成，请稍后请求获取结果。")


def parse_args():
    parser = argparse.ArgumentParser(description="AIDSO GEO 内容生产轮询脚本")
    parser.add_argument("brand", help="品牌名称")
    parser.add_argument("issue", help="AI问题")
    parser.add_argument("platform", help="平台字段值，如 DB / DP / TXYB")
    parser.add_argument("--api-key", dest="api_key", help="API key")
    parser.add_argument("--interval", dest="interval", type=int, default=DEFAULT_INTERVAL_SECONDS, help="轮询间隔秒数")
    parser.add_argument("--max-attempts", dest="max_attempts", type=int, default=DEFAULT_MAX_ATTEMPTS, help="最大轮询次数")
    return parser.parse_args()


def main():
    try:
        args = parse_args()

        brand = args.brand.strip()
        issue = args.issue.strip()
        platform = args.platform.strip()
        api_key = (args.api_key or os.environ.get("AIDSO_GEO_API_KEY") or "").strip()

        if not brand:
            out_text("brand 不能为空")
            sys.exit(0)

        if not issue:
            out_text("issue 不能为空")
            sys.exit(0)

        if not platform:
            out_text("platform 不能为空")
            sys.exit(0)

        if not api_key:
            out_text(
                f"未检测到 API key，请通过 --api-key 传入，或设置环境变量 AIDSO_GEO_API_KEY。\n"
                f"获取地址：{API_KEY_URL}"
            )
            sys.exit(0)

        _, payload = poll_content(
            brand=brand,
            issue=issue,
            platform=platform,
            api_key=api_key,
            interval_seconds=args.interval,
            max_attempts=args.max_attempts,
        )

        out_text(payload)
        sys.exit(0)

    except requests.HTTPError as e:
        status = getattr(e.response, "status_code", None)
        if status == 401:
            out_text(
                f"当前绑定的 API key 已失效或不正确，请重新输入你在后台创建的 API key 完成绑定。\n"
                f"获取地址：{API_KEY_URL}"
            )
            sys.exit(0)

        out_text(f"请求失败：HTTP {status or '未知状态码'}")
        sys.exit(0)

    except Exception as e:
        out_debug(f"[ERROR] content_poll failed: {e}")
        out_text(f"GEO内容生成失败：{e}")
        sys.exit(0)


if __name__ == "__main__":
    main()