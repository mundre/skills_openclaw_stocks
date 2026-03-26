#!/usr/bin/env python3
"""
腾讯云 API 签名 v3 通用调用脚本 (Python 版)
基于腾讯云 API 签名 v3 文档实现: https://cloud.tencent.com/document/product/213/30654

纯 Python 标准库实现，支持 Windows / Linux / macOS 跨平台运行。
不依赖 curl、openssl、jq 等外部工具。

用法 (命令行):
    python3 tcloud_api.py <service> <host> <action> <version> [payload] [region]

示例:
    python3 tcloud_api.py advisor advisor.tencentcloudapi.com DescribeArchList 2020-07-21 '{"PageNumber":1,"PageSize":10}'

作为模块导入:
    from tcloud_api import call_api
    result = call_api("advisor", "advisor.tencentcloudapi.com",
                      "DescribeArchList", "2020-07-21",
                      {"PageNumber": 1, "PageSize": 10})

环境变量（必须提前设置）:
    TENCENTCLOUD_SECRET_ID  - 腾讯云 SecretId
    TENCENTCLOUD_SECRET_KEY - 腾讯云 SecretKey
    TENCENTCLOUD_TOKEN      - 临时密钥 Token（可选，使用临时密钥时设置）

输出格式（统一 JSON）:
    成功: {"success": true, "action": "<Action>", "data": {...}, "requestId": "xxx"}
    失败: {"success": false, "action": "<Action>", "error": {"code": "xxx", "message": "xxx"}, "requestId": "xxx"}
"""

import hashlib
import hmac
import json
import os
import ssl
import sys
import time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def _get_ssl_context():
    """获取 SSL 上下文，优先使用 certifi 证书，其次使用系统默认 CA 证书。
    绝不禁用 SSL 验证。如果证书验证失败，请安装 certifi: pip install certifi"""
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def _sign_tc3(key: bytes, msg: str) -> bytes:
    """TC3 HMAC-SHA256 签名辅助函数"""
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def _output_json(obj: dict) -> str:
    """统一 JSON 输出"""
    return json.dumps(obj, ensure_ascii=False)


def _make_error(action: str, code: str, message: str, request_id: str = "") -> dict:
    """构造统一错误结果"""
    return {
        "success": False,
        "action": action,
        "error": {"code": code, "message": message},
        "requestId": request_id,
    }


def _make_success(action: str, data: dict, request_id: str) -> dict:
    """构造统一成功结果"""
    return {
        "success": True,
        "action": action,
        "data": data,
        "requestId": request_id,
    }


def call_api(service: str, host: str, action: str, version: str,
             payload: dict | str = None, region: str = "ap-guangzhou",
             secret_id: str = None, secret_key: str = None,
             token: str = None) -> dict:
    """
    调用腾讯云 API（TC3-HMAC-SHA256 签名）
    """
    secret_id = secret_id or os.environ.get("TENCENTCLOUD_SECRET_ID", "")
    secret_key = secret_key or os.environ.get("TENCENTCLOUD_SECRET_KEY", "")
    token = token or os.environ.get("TENCENTCLOUD_TOKEN", "")

    if not secret_id or not secret_key:
        return _make_error(
            action,
            "MissingCredentials",
            "未配置 TENCENTCLOUD_SECRET_ID 或 TENCENTCLOUD_SECRET_KEY。"
            "请在当前终端会话中设置环境变量。"
            "密钥获取: https://console.cloud.tencent.com/cam/capi"
        )

    if payload is None:
        payload_str = "{}"
    elif isinstance(payload, dict):
        payload_str = json.dumps(payload, separators=(",", ":"))
    else:
        payload_str = str(payload)

    algorithm = "TC3-HMAC-SHA256"
    timestamp = int(time.time())
    date = datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d")

    hashed_payload = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()
    canonical_request = (
        f"POST\n"
        f"/\n"
        f"\n"
        f"content-type:application/json; charset=utf-8\n"
        f"host:{host}\n"
        f"x-tc-action:{action.lower()}\n"
        f"\n"
        f"content-type;host;x-tc-action\n"
        f"{hashed_payload}"
    )

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
        "Content-Type": "application/json; charset=utf-8",
        "Host": host,
        "X-TC-Action": action,
        "X-TC-Timestamp": str(timestamp),
        "X-TC-Version": version,
        "X-TC-Region": region,
    }
    if token:
        headers["X-TC-Token"] = token

    req = Request(
        f"https://{host}",
        data=payload_str.encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        ctx = _get_ssl_context()
        with urlopen(req, context=ctx, timeout=30) as resp:
            response_body = resp.read().decode("utf-8")
    except HTTPError as e:
        try:
            body = e.read().decode("utf-8")
            data = json.loads(body)
            response = data.get("Response", {})
            error = response.get("Error", {})
            if error:
                return _make_error(
                    action,
                    error.get("Code", "HTTPError"),
                    error.get("Message", f"HTTP {e.code}"),
                    response.get("RequestId", ""),
                )
        except Exception:
            pass
        return _make_error(
            action, "HTTPError",
            f"HTTP 请求失败 (状态码 {e.code}): {e.reason}"
        )
    except URLError as e:
        return _make_error(
            action, "NetworkError",
            f"网络连接失败，请检查网络和域名 {host} 是否可达: {e.reason}"
        )
    except Exception as e:
        return _make_error(
            action, "NetworkError",
            f"请求异常: {e}"
        )

    try:
        data = json.loads(response_body)
    except json.JSONDecodeError:
        return _make_error(action, "ParseError", "响应不是有效的 JSON")

    response = data.get("Response", {})
    request_id = response.get("RequestId", "")

    if "Error" in response:
        err = response["Error"]
        return _make_error(
            action,
            err.get("Code", "Unknown"),
            err.get("Message", "未知错误"),
            request_id,
        )

    result_data = {k: v for k, v in response.items() if k != "RequestId"}
    return _make_success(action, result_data, request_id)


def main():
    """命令行入口"""
    args = sys.argv[1:]

    if len(args) < 4:
        print(_output_json(_make_error(
            "", "MissingParameter",
            "缺少必要参数。用法: python3 tcloud_api.py <service> <host> <action> <version> [payload] [region]"
        )))
        sys.exit(1)

    service = args[0]
    host = args[1]
    action = args[2]
    version = args[3]
    payload_str = args[4] if len(args) > 4 else "{}"
    region = args[5] if len(args) > 5 else "ap-guangzhou"

    try:
        payload = json.loads(payload_str)
    except json.JSONDecodeError:
        payload = payload_str

    result = call_api(service, host, action, version, payload, region)
    print(_output_json(result))

    if not result.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()
