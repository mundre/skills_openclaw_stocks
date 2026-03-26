#!/usr/bin/env python3
"""
腾讯云控制台免密登录链接生成脚本 (Python 版)
通过 STS AssumeRole 获取临时凭证，生成免密登录 URL

用法:
    python3 login_url.py <target_url>

示例:
    python3 login_url.py "https://console.cloud.tencent.com/advisor?archId=arch-gvqocc25"
    python3 login_url.py "https://console.cloud.tencent.com/advisor"

环境变量（必须提前设置）:
    TENCENTCLOUD_SECRET_ID   - 腾讯云 SecretId（必填）
    TENCENTCLOUD_SECRET_KEY  - 腾讯云 SecretKey（必填）
    TENCENTCLOUD_ROLE_ARN    - CAM 角色 ARN（可选）
    TENCENTCLOUD_ROLE_NAME   - CAM 角色名称（可选），系统会自动拼接完整 ARN

配置优先级:
    1. 环境变量 TENCENTCLOUD_ROLE_ARN（完整 ARN）
    2. 配置文件 ~/.cloudq/tencent/config.json
    3. 环境变量 TENCENTCLOUD_ROLE_NAME + 自动获取账号 UIN

可选环境变量:
    TENCENTCLOUD_ROLE_SESSION - 角色会话名称（默认 advisor-session）
    TENCENTCLOUD_STS_DURATION - 临时凭证有效期秒数（默认 3600，最大 43200）

输出格式（统一 JSON）:
    成功: {"success": true, "action": "GenerateLoginURL", "data": {"loginUrl": "...", "targetUrl": "...", "expireSeconds": 3600}, "requestId": "xxx"}
    失败: {"success": false, "action": "GenerateLoginURL", "error": {"code": "xxx", "message": "xxx"}, "requestId": ""}
"""

import base64
import hashlib
import hmac
import json
import os
import random
import ssl
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from tcloud_api import call_api  # noqa: E402

ACTION_NAME = "GenerateLoginURL"


def output_error(code: str, message: str, request_id: str = "") -> str:
    return json.dumps({
        "success": False,
        "action": ACTION_NAME,
        "error": {"code": code, "message": message},
        "requestId": request_id,
    }, ensure_ascii=False)


def output_success(login_url: str, target_url: str, expire_seconds: int, request_id: str) -> str:
    return json.dumps({
        "success": True,
        "action": ACTION_NAME,
        "data": {
            "loginUrl": login_url,
            "targetUrl": target_url,
            "expireSeconds": expire_seconds,
        },
        "requestId": request_id,
    }, ensure_ascii=False)


def _get_ssl_context():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def _sign_tc3(key: bytes, msg: str) -> bytes:
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def _get_role_arn(secret_id: str, secret_key: str) -> str:
    role_arn = os.environ.get("TENCENTCLOUD_ROLE_ARN", "")
    if role_arn:
        return role_arn

    config_file = Path.home() / ".cloudq" / "tencent" / "config.json"
    if config_file.exists():
        try:
            config = json.loads(config_file.read_text(encoding="utf-8"))
            role_arn = config.get("roleArn", "")
            if role_arn:
                return role_arn
        except (json.JSONDecodeError, OSError):
            pass

    role_name = os.environ.get("TENCENTCLOUD_ROLE_NAME", "")
    if role_name:
        try:
            result = call_api(
                "sts",
                "sts.tencentcloudapi.com",
                "GetCallerIdentity",
                "2018-08-13",
                {},
                secret_id=secret_id,
                secret_key=secret_key,
            )
            account_uin = str(result.get("data", {}).get("AccountId", ""))
            if account_uin and account_uin not in ("", "None", "null"):
                return f"qcs::cam::uin/{account_uin}:roleName/{role_name}"
        except Exception:
            pass

    return ""


def sts_assume_role(secret_id: str, secret_key: str, role_arn: str,
                    role_session: str, duration: int) -> dict:
    service = "sts"
    host = f"{service}.tencentcloudapi.com"
    action = "AssumeRole"
    version = "2018-08-13"
    region = "ap-guangzhou"

    payload = json.dumps({
        "RoleArn": role_arn,
        "RoleSessionName": role_session,
        "DurationSeconds": duration,
    }, separators=(",", ":"))

    timestamp = int(time.time())
    date = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d")

    hashed_payload = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    canonical_request = (
        f"POST\n"
        f"/\n"
        f"\n"
        f"content-type:application/json\n"
        f"host:{host}\n"
        f"x-tc-action:{action.lower()}\n"
        f"\n"
        f"content-type;host;x-tc-action\n"
        f"{hashed_payload}"
    )

    algorithm = "TC3-HMAC-SHA256"
    credential_scope = f"{date}/{service}/tc3_request"
    hashed_canonical_request = hashlib.sha256(
        canonical_request.encode("utf-8")
    ).hexdigest()
    string_to_sign = (
        f"{algorithm}\n"
        f"{timestamp}\n"
        f"{credential_scope}\n"
        f"{hashed_canonical_request}"
    )

    secret_date = _sign_tc3(f"TC3{secret_key}".encode("utf-8"), date)
    secret_service = _sign_tc3(secret_date, service)
    secret_signing = _sign_tc3(secret_service, "tc3_request")
    signature = hmac.new(
        secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    authorization = (
        f"{algorithm} "
        f"Credential={secret_id}/{credential_scope}, "
        f"SignedHeaders=content-type;host;x-tc-action, "
        f"Signature={signature}"
    )

    headers = {
        "Authorization": authorization,
        "Content-Type": "application/json",
        "Host": host,
        "X-TC-Action": action,
        "X-TC-Version": version,
        "X-TC-Region": region,
        "X-TC-Timestamp": str(timestamp),
    }

    req = Request(
        f"https://{host}",
        data=payload.encode("utf-8"),
        headers=headers,
        method="POST",
    )

    ctx = _get_ssl_context()
    with urlopen(req, context=ctx) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    response_body = result.get("Response", {})
    credentials = response_body.get("Credentials", {})

    if not credentials:
        error = response_body.get("Error", {})
        return {
            "error": True,
            "code": error.get("Code", "STSError"),
            "message": f"STS AssumeRole 失败: {error.get('Message', '请检查 AK/SK 和 ROLE_ARN')}",
            "requestId": response_body.get("RequestId", ""),
        }

    return {
        "error": False,
        "TmpSecretId": credentials["TmpSecretId"],
        "TmpSecretKey": credentials["TmpSecretKey"],
        "Token": credentials["Token"],
        "RequestId": response_body.get("RequestId", ""),
    }


def generate_login_url(tmp_secret_id: str, tmp_secret_key: str,
                       token: str, target_url: str) -> str:
    login_timestamp = int(time.time())
    login_nonce = random.randint(10000, 100000000)

    source_string = (
        f"GETcloud.tencent.com/login/roleAccessCallback?"
        f"action=roleLogin"
        f"&nonce={login_nonce}"
        f"&secretId={tmp_secret_id}"
        f"&timestamp={login_timestamp}"
    )

    login_signature = base64.b64encode(
        hmac.new(
            tmp_secret_key.encode("utf-8"),
            source_string.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")

    login_url = (
        f"https://cloud.tencent.com/login/roleAccessCallback?"
        f"algorithm=sha256"
        f"&secretId={quote(tmp_secret_id, safe='')}"
        f"&token={quote(token, safe='')}"
        f"&nonce={login_nonce}"
        f"&timestamp={login_timestamp}"
        f"&signature={quote(login_signature, safe='')}"
        f"&s_url={quote(target_url, safe='')}"
    )

    return login_url


def main():
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        print(output_error(
            "MissingParameter",
            "缺少目标 URL 参数。用法: python3 login_url.py <target_url>"
        ))
        sys.exit(1)

    target_url = sys.argv[1]

    secret_id = os.environ.get("TENCENTCLOUD_SECRET_ID", "")
    secret_key = os.environ.get("TENCENTCLOUD_SECRET_KEY", "")

    missing = []
    if not secret_id:
        missing.append("TENCENTCLOUD_SECRET_ID")
    if not secret_key:
        missing.append("TENCENTCLOUD_SECRET_KEY")

    if missing:
        print(output_error(
            "MissingCredentials",
            f"缺少环境变量: {' '.join(missing)}。当前版本不会自动读取本地凭据文件。"
        ))
        sys.exit(1)

    role_arn = _get_role_arn(secret_id, secret_key)
    if not role_arn:
        print(output_error(
            "MissingRoleConfiguration",
            "未配置角色信息。请选择以下方式之一:\n\n"
            "方式一: 设置角色名称（推荐）\n"
            "  export TENCENTCLOUD_ROLE_NAME=\"AdvisorRole\"\n\n"
            "方式二: 设置完整 ARN\n"
            "  export TENCENTCLOUD_ROLE_ARN=\"qcs::cam::uin/您的账号UIN:roleName/角色名\"\n\n"
            "方式三: 运行配置向导（首次使用推荐）\n"
            "  python3 scripts/setup_role.py\n\n"
            "提示: 您可以在 CAM 控制台查看可用角色:\n"
            "  https://console.cloud.tencent.com/cam/role"
        ))
        sys.exit(1)

    role_session = os.environ.get("TENCENTCLOUD_ROLE_SESSION", "advisor-session")
    duration = int(os.environ.get("TENCENTCLOUD_STS_DURATION", "3600"))

    try:
        sts_result = sts_assume_role(secret_id, secret_key, role_arn, role_session, duration)
    except Exception as e:
        print(output_error("STSError", f"STS AssumeRole 请求异常: {e}"))
        sys.exit(1)

    if sts_result.get("error"):
        print(output_error(
            sts_result.get("code", "STSError"),
            sts_result.get("message", "STS AssumeRole 失败"),
            sts_result.get("requestId", ""),
        ))
        sys.exit(1)

    login_url = generate_login_url(
        sts_result["TmpSecretId"],
        sts_result["TmpSecretKey"],
        sts_result["Token"],
        target_url,
    )

    print(output_success(login_url, target_url, duration, sts_result["RequestId"]))


if __name__ == "__main__":
    main()
