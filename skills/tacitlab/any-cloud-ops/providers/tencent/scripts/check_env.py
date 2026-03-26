#!/usr/bin/env python3
"""
腾讯云智能顾问环境检测脚本。

目标：
- 仅执行运行环境检测与只读 API 校验
- 不执行自动更新检查
- 不写入本地配置文件
- 不自动读取本地凭据文件
- 不创建角色、不关联策略、不生成登录链接

用法:
    python3 check_env.py
    python3 check_env.py --quiet

返回码:
    0 - 环境就绪（AK/SK 正常，且已存在可用的角色配置）
    1 - Python 版本不满足或网络调用失败
    2 - AK/SK 未配置或无效
    3 - 免密登录角色尚未完成本地配置
"""

from __future__ import annotations

import json
import os
import platform
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from tcloud_api import call_api  # noqa: E402

CLOUDQ_DIR = Path.home() / ".cloudq"
CONFIG_FILE = CLOUDQ_DIR / "tencent" / "config.json"
ADVISOR_ROLE_NAME = "advisor"
QUIET_MODE = "--quiet" in sys.argv


def log_info(msg: str):
    if not QUIET_MODE:
        print(msg)


def log_ok(msg: str):
    if not QUIET_MODE:
        print(f"  [OK] {msg}")


def log_warn(msg: str):
    if not QUIET_MODE:
        print(f"  [WARN] {msg}")


def log_fail(msg: str):
    print(f"  [FAIL] {msg}")


def log_section(title: str):
    if not QUIET_MODE:
        print(f"\n=== {title} ===")


def _load_saved_role_arn() -> str:
    if not CONFIG_FILE.exists():
        return ""
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return ""
    return str(data.get("roleArn", "") or "")


def main():
    log_section("1. 检查运行环境")
    py_ver = sys.version_info
    if py_ver < (3, 7):
        log_fail(f"Python 版本过低: {sys.version}，需要 Python 3.7+")
        sys.exit(1)
    log_ok(f"Python {py_ver.major}.{py_ver.minor}.{py_ver.micro} ({platform.system()} {platform.machine()})")

    log_section("2. 检查 AK/SK 配置")
    secret_id = os.environ.get("TENCENTCLOUD_SECRET_ID", "")
    secret_key = os.environ.get("TENCENTCLOUD_SECRET_KEY", "")

    if not secret_id or not secret_key:
        missing = []
        if not secret_id:
            missing.append("TENCENTCLOUD_SECRET_ID")
        if not secret_key:
            missing.append("TENCENTCLOUD_SECRET_KEY")
        log_fail(f"未配置以下环境变量: {', '.join(missing)}")
        log_info("")
        log_info("  请在当前终端会话中设置环境变量（推荐）:")
        log_info('    export TENCENTCLOUD_SECRET_ID="your-secret-id"')
        log_info('    export TENCENTCLOUD_SECRET_KEY="your-secret-key"')
        log_info("")
        log_info("  安全建议: 推荐使用 STS 临时凭证或子账号密钥，避免使用主账号长期密钥")
        log_info("  密钥获取地址: https://console.cloud.tencent.com/cam/capi")
        log_info("  说明: 当前版本不会自动读取任何本地凭据文件")
        sys.exit(2)

    masked_id = f"{secret_id[:4]}****{secret_id[-4:]}" if len(secret_id) > 8 else "****"
    log_ok(f"SecretId 已配置: {masked_id}")
    log_ok("SecretKey 已配置: ****")
    if os.environ.get("TENCENTCLOUD_TOKEN"):
        log_ok("临时密钥 Token 已配置")

    log_section("3. 验证 AK/SK 有效性")
    verify_result = call_api(
        "advisor",
        "advisor.tencentcloudapi.com",
        "DescribeArchList",
        "2020-07-21",
        {"PageNumber": 1, "PageSize": 1},
        "ap-guangzhou",
    )

    if verify_result.get("success"):
        log_ok("AK/SK 验证通过，接口调用成功")
    else:
        error_code = verify_result.get("error", {}).get("code", "Unknown")
        if error_code in {
            "AuthFailure.SecretIdNotFound",
            "AuthFailure.SignatureFailure",
            "AuthFailure.InvalidSecretId",
        }:
            log_fail(f"AK/SK 无效: {error_code}")
            log_info("  请检查密钥是否正确: https://console.cloud.tencent.com/cam/capi")
            sys.exit(2)
        if error_code in {"NetworkError", "HTTPError"}:
            log_fail("接口调用失败，请检查网络连接")
            sys.exit(1)
        log_ok("AK/SK 鉴权成功")
        if not QUIET_MODE:
            log_warn(f"接口返回业务错误: {error_code}（不影响鉴权）")

    log_section("4. 检查免密登录角色配置")
    role_arn = os.environ.get("TENCENTCLOUD_ROLE_ARN", "")
    if role_arn:
        log_ok("ROLE_ARN 已通过环境变量配置")
        sys.exit(0)

    saved_arn = _load_saved_role_arn()
    if saved_arn:
        log_ok("角色已通过本地配置文件保存")
        sys.exit(0)

    role_name_env = os.environ.get("TENCENTCLOUD_ROLE_NAME", "")
    if role_name_env:
        log_ok(f"ROLE_NAME 已配置: {role_name_env}")
        sys.exit(0)

    log_warn("尚未检测到免密登录角色配置")
    log_info("")
    log_info("  继续查询账号中是否已存在可复用角色（只读检查）...")

    uin_result = call_api("sts", "sts.tencentcloudapi.com", "GetCallerIdentity", "2018-08-13", {})
    account_uin = str(uin_result.get("data", {}).get("AccountId", ""))
    if not uin_result.get("success") or not account_uin or account_uin == "None":
        log_warn("无法读取当前账号 UIN，将角色配置状态视为未完成")
        log_info("  如需免密登录功能，请运行 setup_role.py 完成本地配置")
        sys.exit(3)

    log_info(f"  账号 UIN: {account_uin}")
    role_check = call_api(
        "cam",
        "cam.tencentcloudapi.com",
        "GetRole",
        "2019-01-16",
        {"RoleName": ADVISOR_ROLE_NAME},
    )

    if role_check.get("success") and role_check.get("data", {}).get("ConsoleLogin", 0) == 1:
        log_warn(f"检测到账号中已存在可用角色 {ADVISOR_ROLE_NAME}，但当前会话尚未配置")
        log_info("  这意味着 API 查询通常已可用，但免密登录功能还未完成本地配置")
        log_info("  可选方案:")
        log_info(f"    1. 运行向导: python3 {SCRIPT_DIR / 'setup_role.py'}")
        log_info('    2. 当前会话设置: export TENCENTCLOUD_ROLE_NAME="advisor"')
        sys.exit(3)

    log_warn(f"未检测到可用角色 {ADVISOR_ROLE_NAME}")
    log_info("  如需免密登录功能，请在充分了解权限影响后运行 setup_role.py 或 create_role.py")
    sys.exit(3)


if __name__ == "__main__":
    main()
