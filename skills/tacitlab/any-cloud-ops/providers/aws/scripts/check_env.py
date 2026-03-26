#!/usr/bin/env python3
"""
AWS Provider 环境检测脚本。

目标：
- 仅执行运行环境检测与只读身份校验
- 不写入本地配置文件
- 不创建角色、不关联策略、不生成登录链接

用法:
    python3 check_env.py
    python3 check_env.py --quiet

返回码:
    0 - 环境就绪（AWS 凭据有效，且已存在角色配置）
    1 - Python / CLI / 网络问题
    2 - AWS 凭据缺失或无效
    3 - Federation 登录角色尚未完成配置
"""

from __future__ import annotations

import json
import platform
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from aws_cli import call_aws  # noqa: E402

CONFIG_FILE = Path.home() / ".cloudq" / "aws" / "config.json"
DEFAULT_ROLE_NAME = "CloudQAuditRole"
QUIET_MODE = "--quiet" in sys.argv


def log_info(msg: str) -> None:
    if not QUIET_MODE:
        print(msg)


def log_ok(msg: str) -> None:
    if not QUIET_MODE:
        print(f"  [OK] {msg}")


def log_warn(msg: str) -> None:
    if not QUIET_MODE:
        print(f"  [WARN] {msg}")


def log_fail(msg: str) -> None:
    print(f"  [FAIL] {msg}")


def log_section(title: str) -> None:
    if not QUIET_MODE:
        print(f"\n=== {title} ===")


def _load_saved_role_arn() -> str:
    if not CONFIG_FILE.exists():
        return ""
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    return str(data.get("roleArn", "") or "")


def main() -> None:
    log_section("1. 检查运行环境")
    if sys.version_info < (3, 7):
        log_fail(f"Python 版本过低: {sys.version}，需要 Python 3.7+")
        sys.exit(1)
    log_ok(f"Python {platform.python_version()} ({platform.system()} {platform.machine()})")

    if not shutil.which("aws"):
        log_fail("未检测到 aws CLI，请先安装并完成 aws configure")
        sys.exit(1)
    log_ok("aws CLI 已安装")

    log_section("2. 检查 AWS 凭据")
    identity = call_aws("sts", "get-caller-identity")
    if not identity.get("success"):
        code = identity.get("error", {}).get("code", "Unknown")
        message = identity.get("error", {}).get("message", "未知错误")
        if code in {"MissingCredentials", "InvalidClientTokenId", "SignatureDoesNotMatch", "ExpiredToken"}:
            log_fail(f"AWS 凭据不可用: {message}")
            log_info("  请设置 AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY，或设置 AWS_PROFILE")
            sys.exit(2)
        log_fail(f"身份校验失败: {message}")
        sys.exit(1)

    data = identity.get("data", {})
    account_id = str(data.get("Account", ""))
    caller_arn = str(data.get("Arn", ""))
    log_ok(f"身份校验成功，账号: {account_id or 'unknown'}")
    if caller_arn:
        log_ok(f"当前身份 ARN: {caller_arn}")

    log_section("3. 检查 Federation 角色配置")
    role_arn = ""
    if "AWS_ROLE_ARN" in __import__("os").environ:
        role_arn = __import__("os").environ.get("AWS_ROLE_ARN", "")
    if role_arn:
        log_ok("AWS_ROLE_ARN 已通过环境变量配置")
        sys.exit(0)

    saved_arn = _load_saved_role_arn()
    if saved_arn:
        log_ok("角色已通过本地配置文件保存")
        sys.exit(0)

    role_check = call_aws("iam", "get-role", {"RoleName": DEFAULT_ROLE_NAME})
    if role_check.get("success"):
        log_warn(f"检测到账号中已存在可用角色 {DEFAULT_ROLE_NAME}，但当前会话尚未完成本地配置")
        log_info(f"  可运行向导: python3 {SCRIPT_DIR / 'setup_role.py'}")
        sys.exit(3)

    log_warn("尚未检测到 Federation 登录角色配置")
    log_info(f"  如需控制台登录辅助，可运行: python3 {SCRIPT_DIR / 'setup_role.py'}")
    sys.exit(3)


if __name__ == "__main__":
    main()
