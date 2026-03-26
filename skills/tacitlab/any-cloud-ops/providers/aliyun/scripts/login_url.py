#!/usr/bin/env python3
"""
阿里云控制台入口辅助脚本。

说明：
- 当前脚本不会伪造“直接 federation 登录 URL”能力
- 它会先验证 RAM 角色扮演是否可用
- 如果提供了 CloudSSO Sign-In URL，则返回可供用户打开的设备登录入口

用法:
    python3 login_url.py <target_url>
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from aliyun_cli import call_aliyun  # noqa: E402

ACTION_NAME = "GetConsoleLoginEntry"
CONFIG_FILE = Path.home() / ".cloudq" / "aliyun" / "config.json"


def output_error(code: str, message: str, request_id: str = "") -> str:
    return json.dumps({
        "success": False,
        "action": ACTION_NAME,
        "error": {"code": code, "message": message},
        "requestId": request_id,
    }, ensure_ascii=False)


def output_success(login_url: str, target_url: str, role_arn: str, mode: str, request_id: str) -> str:
    return json.dumps({
        "success": True,
        "action": ACTION_NAME,
        "data": {
            "loginUrl": login_url,
            "targetUrl": target_url,
            "roleArn": role_arn,
            "mode": mode,
            "note": "请先完成 CloudSSO 设备登录，再在控制台中切换到已配置角色。",
        },
        "requestId": request_id,
    }, ensure_ascii=False)


def _load_config() -> Dict[str, Any]:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _get_role_arn(config: Dict[str, Any]) -> str:
    return os.environ.get("ALIBABA_CLOUD_ROLE_ARN", "") or str(config.get("roleArn", "") or "")


def _get_signin_url(config: Dict[str, Any]) -> str:
    value = os.environ.get("ALIBABA_CLOUD_SSO_SIGN_IN_URL", "") or str(config.get("signInUrl", "") or "")
    if not value:
        return ""
    if value.endswith("/device/code"):
        return value
    return value.rstrip("/") + "/device/code"


def main() -> None:
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        print(output_error("MissingParameter", "缺少目标 URL 参数。用法: python3 login_url.py <target_url>"))
        sys.exit(1)

    target_url = sys.argv[1].strip()
    config = _load_config()
    role_arn = _get_role_arn(config)
    if not role_arn:
        print(output_error(
            "MissingRoleConfiguration",
            "未配置 ALIBABA_CLOUD_ROLE_ARN，且未检测到 ~/.cloudq/aliyun/config.json。请先运行 setup_role.py 或设置 ALIBABA_CLOUD_ROLE_ARN。",
        ))
        sys.exit(1)

    session_name = os.environ.get("ALIBABA_CLOUD_ROLE_SESSION_NAME", "cloudq-session")
    try:
        duration = int(os.environ.get("ALIBABA_CLOUD_ROLE_SESSION_DURATION", "3600"))
    except ValueError:
        duration = 3600
    duration = max(900, min(duration, 43200))

    assume_result = call_aliyun(
        "sts",
        "AssumeRole",
        {
            "RoleArn": role_arn,
            "RoleSessionName": session_name,
            "DurationSeconds": duration,
        },
    )
    if not assume_result.get("success"):
        error = assume_result.get("error", {})
        print(output_error(error.get("code", "AssumeRoleFailed"), error.get("message", "AssumeRole 失败"), assume_result.get("requestId", "")))
        sys.exit(1)

    sign_in_url = _get_signin_url(config)
    if not sign_in_url:
        print(output_error(
            "MissingCloudSSOEntry",
            "未配置 CloudSSO Sign-In URL。请设置 ALIBABA_CLOUD_SSO_SIGN_IN_URL，或先通过 CloudSSO CLI 登录并将入口写入本地配置。",
            assume_result.get("requestId", ""),
        ))
        sys.exit(1)

    print(output_success(sign_in_url, target_url, role_arn, "cloudsso-device-code", assume_result.get("requestId", "")))


if __name__ == "__main__":
    main()
