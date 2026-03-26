#!/usr/bin/env python3
"""
阿里云 Provider 配置清理脚本。

用法:
    python3 cleanup.py
    python3 cleanup.py --all
    python3 cleanup.py --all --cloud

清理范围:
    1. 配置目录 ~/.cloudq/aliyun/
    2. 环境变量 ALIBABA_CLOUD_*（当前会话清理脚本）
    3. 云端角色 CloudQAuditRole（可选，仅删除自动创建的角色）
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import stat
import sys
import tempfile
from pathlib import Path
from typing import Dict

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from aliyun_cli import call_aliyun  # noqa: E402

CONFIG_DIR = Path.home() / ".cloudq" / "aliyun"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_ROLE_NAME = "CloudQAuditRole"
POLICIES = ["AliyunGovernanceReadOnlyAccess", "AliyunRAMReadOnlyAccess"]
ENV_VARS = [
    "ALIBABA_CLOUD_ACCESS_KEY_ID",
    "ALIBABA_CLOUD_ACCESS_KEY_SECRET",
    "ALIBABA_CLOUD_SECURITY_TOKEN",
    "ALIBABA_CLOUD_PROFILE",
    "ALIBABA_CLOUD_REGION_ID",
    "ALIBABA_CLOUD_ROLE_ARN",
    "ALIBABA_CLOUD_ROLE_SESSION_NAME",
    "ALIBABA_CLOUD_ROLE_SESSION_DURATION",
    "ALIBABA_CLOUD_SSO_SIGN_IN_URL",
]


def _supports_color() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


_COLOR = _supports_color()


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _COLOR else text


def green(text: str) -> str:
    return _c("32", text)


def red(text: str) -> str:
    return _c("31", text)


def yellow(text: str) -> str:
    return _c("33", text)


def bold(text: str) -> str:
    return _c("1", text)


def dim(text: str) -> str:
    return _c("2", text)


def confirm(prompt: str) -> bool:
    try:
        answer = input(f"{prompt} [y/N]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return answer in {"y", "yes"}


def read_config() -> Dict[str, object]:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def remove_dir(path: Path, label: str) -> bool:
    if not path.exists():
        print(f"  {dim('[-]')} {label}: {dim('不存在，跳过')}")
        return False
    try:
        shutil.rmtree(str(path))
        print(f"  {green('[OK]')} {label}: 已删除")
        return True
    except OSError as exc:
        print(f"  {red('[FAIL]')} {label}: 删除失败 - {exc}")
        return False


def clean_config_dir(interactive: bool) -> bool:
    print(f"\n{bold('1. 配置目录')}")
    if not CONFIG_DIR.exists():
        print(f"  {dim('[-]')} {CONFIG_DIR}: {dim('不存在，跳过')}")
        return False
    if interactive and not confirm(f"确认删除 {CONFIG_DIR} ?"):
        print(f"  {yellow('[SKIP]')} 用户跳过")
        return False
    return remove_dir(CONFIG_DIR, str(CONFIG_DIR))


def clean_env_vars(interactive: bool) -> bool:
    print(f"\n{bold('2. 环境变量')}")
    found = {key: os.environ.get(key, "") for key in ENV_VARS if os.environ.get(key, "")}
    if not found:
        print(f"  {dim('[-]')} 未检测到已设置的 ALIBABA_CLOUD_* 环境变量，跳过")
        return False

    print(f"  检测到 {len(found)} 个已设置的环境变量:")
    for key, value in found.items():
        masked = value
        if "KEY" in key or "TOKEN" in key or "SECRET" in key:
            masked = value[:4] + "****" + value[-4:] if len(value) > 8 else "****"
        print(f"    - {key} = {masked}")

    if interactive and not confirm("确认生成当前会话环境变量清理脚本?"):
        print(f"  {yellow('[SKIP]')} 用户跳过")
        return False

    is_windows = platform.system() == "Windows"
    if is_windows:
        script_file = Path(tempfile.gettempdir()) / "cleanup_aliyun_env.ps1"
        lines = ["# CloudQ 阿里云环境变量清理脚本", ""]
        for key in found:
            lines.append(f'Remove-Item Env:\\{key} -ErrorAction SilentlyContinue')
            lines.append(f'Write-Host "  [OK] 已清除 {key}"')
        script_file.write_text("\n".join(lines), encoding="utf-8")
        print(f"  已生成 PowerShell 清理脚本: {script_file}")
        print(f"  请执行: . {script_file}")
    else:
        script_file = Path(tempfile.gettempdir()) / "cleanup_aliyun_env.sh"
        lines = ["#!/bin/sh", "# CloudQ 阿里云环境变量清理脚本", ""]
        for key in found:
            lines.append(f"unset {key}")
            lines.append(f'echo "  [OK] 已清除 {key}"')
        script_file.write_text("\n".join(lines), encoding="utf-8")
        try:
            os.chmod(str(script_file), stat.S_IRWXU)
        except OSError:
            pass
        print(f"  已生成清理脚本: {script_file}")
        print(f"  请执行: source {script_file}")

    print(f"  {yellow('注意')}: Python 进程无法直接修改父 shell 的环境变量。")
    return True


def clean_cloud_role(interactive: bool) -> bool:
    print(f"\n{bold('3. 云端 RAM 角色')}")
    config = read_config()
    auto_created = bool(config.get("autoCreated", False))
    role_name = str(config.get("roleName", DEFAULT_ROLE_NAME) or DEFAULT_ROLE_NAME)

    if config and not auto_created:
        print(f"  {dim('[-]')} 当前配置指向的是手动选择的已有角色 {role_name}，默认不自动删除")
        return False

    if interactive and not confirm(f"确认删除云端角色 {role_name} ? (此操作不可恢复)"):
        print(f"  {yellow('[SKIP]')} 用户跳过")
        return False

    for policy_name in POLICIES:
        call_aliyun(
            "ram",
            "DetachPolicyFromRole",
            {
                "PolicyType": "System",
                "PolicyName": policy_name,
                "RoleName": role_name,
            },
        )

    delete_result = call_aliyun("ram", "DeleteRole", {"RoleName": role_name})
    if delete_result.get("success"):
        print(f"  {green('[OK]')} 云端角色 {role_name} 已删除")
        return True

    print(f"  {red('[FAIL]')} 删除角色失败: {delete_result.get('error', {}).get('message', '未知错误')}")
    return False


def main() -> None:
    args = set(sys.argv[1:])
    auto_mode = "--all" in args
    include_cloud = "--cloud" in args
    interactive = not auto_mode

    print(f"\n{'=' * 58}")
    print("  CloudQ 阿里云 - 配置清理")
    print(f"{'=' * 58}")

    config = read_config()
    if config:
        print("\n当前配置:")
        print(f"  账号 ID:   {config.get('accountId', '未知')}")
        print(f"  角色名称:  {config.get('roleName', '未知')}")
        print(f"  角色 ARN:  {config.get('roleArn', '未知')}")
        print(f"  自动创建:  {config.get('autoCreated', False)}")

    results = []
    results.append(("配置目录", clean_config_dir(interactive)))
    if include_cloud:
        results.append(("云端角色", clean_cloud_role(interactive)))
    else:
        print(f"\n{bold('3. 云端 RAM 角色')}")
        print(f"  {dim('[-]')} 未指定 --cloud 参数，跳过云端角色清理")
    results.append(("环境变量", clean_env_vars(interactive)))

    cleaned = sum(1 for _, ok in results if ok)
    print(f"\n{'=' * 58}")
    print(f"  清理完成: {cleaned}/{len(results)} 项已处理")
    print(f"{'=' * 58}\n")


if __name__ == "__main__":
    main()
