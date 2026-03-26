#!/usr/bin/env python3
"""
AWS CLI 通用调用脚本。

目标：
- 基于本机 `aws` CLI 执行只读或已获同意的 AWS 调用
- 统一输出 JSON 结果，方便被上层脚本或 AI 解析
- 不保存访问密钥，不修改 CLI 全局配置

用法:
    python3 aws_cli.py <service> <operation> [payload_json] [region] [profile]

示例:
    python3 aws_cli.py sts get-caller-identity
    python3 aws_cli.py iam list-roles '{"MaxItems": 20}'

输出格式（统一 JSON）:
    成功: {"success": true, "action": "<operation>", "data": {...}, "requestId": "xxx"}
    失败: {"success": false, "action": "<operation>", "error": {"code": "xxx", "message": "xxx"}, "requestId": ""}
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from typing import Any, Dict, Optional


def _output_json(obj: Dict[str, Any]) -> str:
    return json.dumps(obj, ensure_ascii=False)


def _make_error(action: str, code: str, message: str, request_id: str = "") -> Dict[str, Any]:
    return {
        "success": False,
        "action": action,
        "error": {"code": code, "message": message},
        "requestId": request_id,
    }


def _make_success(action: str, data: Dict[str, Any], request_id: str = "") -> Dict[str, Any]:
    return {
        "success": True,
        "action": action,
        "data": data,
        "requestId": request_id,
    }


def _ensure_cli() -> Optional[Dict[str, Any]]:
    if shutil.which("aws"):
        return None
    return _make_error(
        "",
        "CLIUnavailable",
        "未检测到 aws CLI。请先安装 AWS CLI，并确保 `aws` 在 PATH 中可用。",
    )


def _flag_name(name: str) -> str:
    if name.startswith("--"):
        return name
    if "-" in name and name.lower() == name:
        return f"--{name}"
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name)
    text = text.replace("_", "-").lower()
    return f"--{text}"


def _append_param(cmd: list, key: str, value: Any) -> None:
    if value is None:
        return

    flag = _flag_name(key)

    if isinstance(value, bool):
        if value:
            cmd.append(flag)
        return

    if isinstance(value, (dict, list)):
        cmd.extend([flag, json.dumps(value, ensure_ascii=False, separators=(",", ":"))])
        return

    cmd.extend([flag, str(value)])


def _parse_cli_error(operation: str, text: str) -> Dict[str, Any]:
    lowered = text.lower()
    if (
        "unable to locate credentials" in lowered
        or "aws_access_key_id" in lowered
        or "aws_secret_access_key" in lowered
        or "config profile" in lowered
        or "could not be found" in lowered and "profile" in lowered
    ):
        return _make_error(
            operation,
            "MissingCredentials",
            "AWS CLI 未检测到可用凭据。请设置 AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY，或设置 AWS_PROFILE。",
        )

    match = re.search(
        r"An error occurred \((?P<code>[^)]+)\) when calling the (?P<api>[^ ]+) operation: (?P<message>.+)",
        text,
        re.S,
    )
    if match:
        return _make_error(
            operation,
            match.group("code"),
            match.group("message").strip(),
        )

    return _make_error(operation, "CLIError", text.strip() or "AWS CLI 执行失败")


def call_aws(
    service: str,
    operation: str,
    params: Optional[Dict[str, Any]] = None,
    region: Optional[str] = None,
    profile: Optional[str] = None,
) -> Dict[str, Any]:
    cli_error = _ensure_cli()
    if cli_error:
        cli_error["action"] = operation
        return cli_error

    cmd = ["aws", service, operation]
    for key, value in (params or {}).items():
        _append_param(cmd, key, value)

    active_region = region or os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
    active_profile = profile or os.environ.get("AWS_PROFILE")

    if active_region:
        cmd.extend(["--region", active_region])
    if active_profile:
        cmd.extend(["--profile", active_profile])

    cmd.extend(["--output", "json", "--no-cli-pager"])

    proc = subprocess.run(cmd, capture_output=True, text=True)
    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()

    if proc.returncode != 0:
        return _parse_cli_error(operation, stderr or stdout)

    if not stdout:
        return _make_success(operation, {}, "")

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return _make_error(operation, "ParseError", "AWS CLI 返回了非 JSON 响应")

    request_id = ""
    if isinstance(data, dict):
        request_id = str(data.get("RequestId", "") or "")
        meta = data.get("ResponseMetadata", {})
        if isinstance(meta, dict) and meta.get("RequestId"):
            request_id = str(meta.get("RequestId"))

    return _make_success(operation, data if isinstance(data, dict) else {"items": data}, request_id)


def main() -> None:
    args = sys.argv[1:]
    if len(args) < 2:
        print(_output_json(_make_error(
            "",
            "MissingParameter",
            "缺少必要参数。用法: python3 aws_cli.py <service> <operation> [payload_json] [region] [profile]",
        )))
        sys.exit(1)

    service = args[0]
    operation = args[1]
    payload_str = args[2] if len(args) > 2 else "{}"
    region = args[3] if len(args) > 3 and args[3] else None
    profile = args[4] if len(args) > 4 and args[4] else None

    try:
        payload = json.loads(payload_str)
    except json.JSONDecodeError:
        payload = {}

    result = call_aws(service, operation, payload, region=region, profile=profile)
    print(_output_json(result))
    if not result.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()
