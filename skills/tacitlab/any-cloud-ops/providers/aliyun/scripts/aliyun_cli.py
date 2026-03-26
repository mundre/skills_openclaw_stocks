#!/usr/bin/env python3
"""
阿里云 CLI 通用调用脚本。

目标：
- 基于本机 `aliyun` CLI 执行阿里云 OpenAPI 调用
- 统一输出 JSON 结果，方便被上层脚本或 AI 解析
- 不保存访问密钥，不修改 CLI 全局配置

用法:
    python3 aliyun_cli.py <product> <Action> [payload_json] [region] [profile]

示例:
    python3 aliyun_cli.py sts GetCallerIdentity
    python3 aliyun_cli.py ram ListRoles '{"MaxItems": 20}'
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
    if shutil.which("aliyun"):
        return None
    return _make_error(
        "",
        "CLIUnavailable",
        "未检测到 aliyun CLI。请先安装阿里云 CLI，并确保 `aliyun` 在 PATH 中可用。",
    )


def _append_param(cmd: list, key: str, value: Any) -> None:
    if value is None:
        return
    flag = key if key.startswith("--") else f"--{key}"
    if isinstance(value, bool):
        if value:
            cmd.append(flag)
        return
    if isinstance(value, (dict, list)):
        cmd.extend([flag, json.dumps(value, ensure_ascii=False, separators=(",", ":"))])
        return
    cmd.extend([flag, str(value)])


def _parse_cli_error(action: str, text: str) -> Dict[str, Any]:
    lowered = text.lower()
    if (
        "nocredentialproviders" in lowered
        or "accesskey" in lowered and "missing" in lowered
        or "no available credential" in lowered
        or "profile" in lowered and "not found" in lowered
    ):
        return _make_error(
            action,
            "MissingCredentials",
            "阿里云 CLI 未检测到可用凭据。请设置 ALIBABA_CLOUD_ACCESS_KEY_ID / ALIBABA_CLOUD_ACCESS_KEY_SECRET，或设置 ALIBABA_CLOUD_PROFILE。",
        )

    code_match = re.search(r"ErrorCode:\s*([^\s]+)", text)
    msg_match = re.search(r"Message:\s*(.+)", text)
    request_match = re.search(r"RequestId:\s*([^\s]+)", text)
    if code_match or msg_match:
        return _make_error(
            action,
            code_match.group(1) if code_match else "CLIError",
            (msg_match.group(1).strip() if msg_match else text.strip()) or "阿里云 CLI 执行失败",
            request_match.group(1) if request_match else "",
        )

    return _make_error(action, "CLIError", text.strip() or "阿里云 CLI 执行失败")


def call_aliyun(
    product: str,
    action: str,
    params: Optional[Dict[str, Any]] = None,
    region: Optional[str] = None,
    profile: Optional[str] = None,
) -> Dict[str, Any]:
    cli_error = _ensure_cli()
    if cli_error:
        cli_error["action"] = action
        return cli_error

    cmd = ["aliyun", product, action]
    for key, value in (params or {}).items():
        _append_param(cmd, key, value)

    active_region = region or os.environ.get("ALIBABA_CLOUD_REGION_ID")
    active_profile = profile or os.environ.get("ALIBABA_CLOUD_PROFILE")

    if active_region:
        cmd.extend(["--region", active_region])
    if active_profile:
        cmd.extend(["--profile", active_profile])

    cmd.extend(["--output", "json"])

    proc = subprocess.run(cmd, capture_output=True, text=True)
    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()

    if proc.returncode != 0:
        return _parse_cli_error(action, stderr or stdout)

    if not stdout:
        return _make_success(action, {}, "")

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        return _make_error(action, "ParseError", "阿里云 CLI 返回了非 JSON 响应")

    request_id = ""
    if isinstance(data, dict):
        request_id = str(data.get("RequestId", "") or "")

    return _make_success(action, data if isinstance(data, dict) else {"items": data}, request_id)


def main() -> None:
    args = sys.argv[1:]
    if len(args) < 2:
        print(_output_json(_make_error(
            "",
            "MissingParameter",
            "缺少必要参数。用法: python3 aliyun_cli.py <product> <Action> [payload_json] [region] [profile]",
        )))
        sys.exit(1)

    product = args[0]
    action = args[1]
    payload_str = args[2] if len(args) > 2 else "{}"
    region = args[3] if len(args) > 3 and args[3] else None
    profile = args[4] if len(args) > 4 and args[4] else None

    try:
        payload = json.loads(payload_str)
    except json.JSONDecodeError:
        payload = {}

    result = call_aliyun(product, action, payload, region=region, profile=profile)
    print(_output_json(result))
    if not result.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()
