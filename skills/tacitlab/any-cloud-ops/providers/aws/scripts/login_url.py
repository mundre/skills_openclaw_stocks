#!/usr/bin/env python3
"""
AWS Federation 登录链接生成脚本。

用法:
    python3 login_url.py <target_url>

示例:
    python3 login_url.py "https://console.aws.amazon.com/"
    python3 login_url.py "https://us-east-1.console.aws.amazon.com/ec2/home"
"""

from __future__ import annotations

import json
import os
import ssl
import sys
from pathlib import Path
from typing import Any, Dict
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from aws_cli import call_aws  # noqa: E402

ACTION_NAME = "GenerateLoginURL"
CONFIG_FILE = Path.home() / ".cloudq" / "aws" / "config.json"
DEFAULT_ISSUER = "https://cloudq.local/"


def output_error(code: str, message: str, request_id: str = "") -> str:
    return json.dumps({
        "success": False,
        "action": ACTION_NAME,
        "error": {"code": code, "message": message},
        "requestId": request_id,
    }, ensure_ascii=False)


def output_success(login_url: str, target_url: str, role_arn: str, expire_seconds: int, request_id: str) -> str:
    return json.dumps({
        "success": True,
        "action": ACTION_NAME,
        "data": {
            "loginUrl": login_url,
            "targetUrl": target_url,
            "roleArn": role_arn,
            "expireSeconds": expire_seconds,
        },
        "requestId": request_id,
    }, ensure_ascii=False)


def _get_ssl_context() -> ssl.SSLContext:
    try:
        import certifi  # type: ignore
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def _load_config() -> Dict[str, Any]:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _get_role_arn() -> str:
    if os.environ.get("AWS_ROLE_ARN"):
        return os.environ.get("AWS_ROLE_ARN", "")
    return str(_load_config().get("roleArn", "") or "")


def _get_signin_token(session: Dict[str, str], duration: int) -> Dict[str, Any]:
    query = urlencode({
        "Action": "getSigninToken",
        "Session": json.dumps(session, separators=(",", ":")),
        "SessionDuration": str(duration),
    })
    request = Request(f"https://signin.aws.amazon.com/federation?{query}")
    try:
        with urlopen(request, context=_get_ssl_context(), timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except HTTPError as exc:
        return {"success": False, "code": "HTTPError", "message": f"获取 SigninToken 失败: HTTP {exc.code}"}
    except URLError as exc:
        return {"success": False, "code": "NetworkError", "message": f"连接 AWS federation 端点失败: {exc.reason}"}
    except Exception as exc:  # pragma: no cover - defensive branch
        return {"success": False, "code": "NetworkError", "message": f"获取 SigninToken 失败: {exc}"}

    token = str(data.get("SigninToken", ""))
    if not token:
        return {"success": False, "code": "SigninTokenMissing", "message": "AWS federation 端点未返回 SigninToken"}
    return {"success": True, "token": token}


def main() -> None:
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        print(output_error("MissingParameter", "缺少目标 URL 参数。用法: python3 login_url.py <target_url>"))
        sys.exit(1)

    target_url = sys.argv[1].strip()
    role_arn = _get_role_arn()
    if not role_arn:
        print(output_error(
            "MissingRoleConfiguration",
            "未配置 AWS_ROLE_ARN，且未检测到 ~/.cloudq/aws/config.json。请先运行 setup_role.py 或设置 AWS_ROLE_ARN。",
        ))
        sys.exit(1)

    role_session_name = os.environ.get("AWS_ROLE_SESSION_NAME", "cloudq-session")
    try:
        duration = int(os.environ.get("AWS_ROLE_SESSION_DURATION", "3600"))
    except ValueError:
        duration = 3600
    duration = max(900, min(duration, 43200))

    assume_result = call_aws(
        "sts",
        "assume-role",
        {
            "RoleArn": role_arn,
            "RoleSessionName": role_session_name,
            "DurationSeconds": duration,
        },
    )
    if not assume_result.get("success"):
        error = assume_result.get("error", {})
        print(output_error(error.get("code", "AssumeRoleFailed"), error.get("message", "AssumeRole 失败")))
        sys.exit(1)

    credentials = assume_result.get("data", {}).get("Credentials", {})
    access_key_id = str(credentials.get("AccessKeyId", ""))
    secret_access_key = str(credentials.get("SecretAccessKey", ""))
    session_token = str(credentials.get("SessionToken", ""))
    request_id = str(assume_result.get("requestId", "") or "")

    if not access_key_id or not secret_access_key or not session_token:
        print(output_error("AssumeRoleFailed", "AssumeRole 成功响应中缺少临时凭据", request_id))
        sys.exit(1)

    token_result = _get_signin_token(
        {
            "sessionId": access_key_id,
            "sessionKey": secret_access_key,
            "sessionToken": session_token,
        },
        duration,
    )
    if not token_result.get("success"):
        print(output_error(token_result.get("code", "SigninTokenFailed"), token_result.get("message", "获取 SigninToken 失败"), request_id))
        sys.exit(1)

    issuer = os.environ.get("AWS_FEDERATION_ISSUER", DEFAULT_ISSUER)
    login_query = urlencode({
        "Action": "login",
        "Issuer": issuer,
        "Destination": target_url,
        "SigninToken": token_result.get("token", ""),
    })
    login_url = f"https://signin.aws.amazon.com/federation?{login_query}"
    print(output_success(login_url, target_url, role_arn, duration, request_id))


if __name__ == "__main__":
    main()
