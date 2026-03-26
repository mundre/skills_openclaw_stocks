#!/usr/bin/env python3
"""
阿里云 Provider 角色配置向导。

用法:
    python3 setup_role.py

说明:
- 读取当前阿里云身份
- 查询已有 RAM 角色
- 允许选择已有角色，或按确认创建 CloudQAuditRole
- 保存配置到 ~/.cloudq/aliyun/config.json
"""

from __future__ import annotations

import json
import os
import platform
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from aliyun_cli import call_aliyun  # noqa: E402

CONFIG_DIR = Path.home() / ".cloudq" / "aliyun"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_ROLE_NAME = "CloudQAuditRole"


def _supports_color() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


USE_COLOR = _supports_color()


def _c(code: str, text: str) -> str:
    if USE_COLOR:
        return f"\033[{code}m{text}\033[0m"
    return text


def green(text: str) -> str:
    return _c("0;32", text)


def yellow(text: str) -> str:
    return _c("1;33", text)


def red(text: str) -> str:
    return _c("0;31", text)


def cyan(text: str) -> str:
    return _c("1;36", text)


def print_header(title: str) -> None:
    bar = cyan("=" * 64)
    print("\n" + bar)
    print(cyan(f"  {title}"))
    print(bar + "\n")


def print_step(msg: str) -> None:
    print(green(f"▶ {msg}"))


def print_ok(msg: str) -> None:
    print(green(f"✓ {msg}"))


def print_warn(msg: str) -> None:
    print(yellow(f"⚠ {msg}"))


def print_fail(msg: str) -> None:
    print(red(f"✗ {msg}"))


def _extract_roles(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    roles = data.get("Roles", {})
    if isinstance(roles, dict):
        items = roles.get("Role", [])
        if isinstance(items, list):
            return items
        if isinstance(items, dict):
            return [items]
    if isinstance(roles, list):
        return roles
    return []


def _existing_signin_url() -> str:
    if os.environ.get("ALIBABA_CLOUD_SSO_SIGN_IN_URL"):
        return os.environ.get("ALIBABA_CLOUD_SSO_SIGN_IN_URL", "")
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            return str(data.get("signInUrl", "") or "")
        except (OSError, json.JSONDecodeError):
            return ""
    return ""


def save_config(account_id: str, role_name: str, role_arn: str, auto_created: bool) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if platform.system() != "Windows":
        try:
            os.chmod(str(CONFIG_DIR), stat.S_IRWXU)
        except OSError:
            pass

    data = {
        "accountId": account_id,
        "roleName": role_name,
        "roleArn": role_arn,
        "configuredAt": datetime.now(timezone.utc).isoformat(),
        "autoCreated": auto_created,
        "version": "1.0",
    }
    sign_in_url = _existing_signin_url()
    if sign_in_url:
        data["signInUrl"] = sign_in_url

    CONFIG_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    if platform.system() != "Windows":
        try:
            os.chmod(str(CONFIG_FILE), stat.S_IRUSR | stat.S_IWUSR)
        except OSError:
            pass


def run_create_role() -> Tuple[bool, Dict[str, Any]]:
    script = SCRIPT_DIR / "create_role.py"
    proc = subprocess.run([sys.executable, str(script), "--role-name", DEFAULT_ROLE_NAME], capture_output=True, text=True)
    try:
        data = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return False, {"error": {"message": proc.stderr.strip() or "角色创建返回格式异常"}}
    return bool(data.get("success")), data


def test_role(role_arn: str) -> Tuple[bool, Dict[str, Any]]:
    session_name = os.environ.get("ALIBABA_CLOUD_ROLE_SESSION_NAME", "cloudq-session")
    try:
        duration = int(os.environ.get("ALIBABA_CLOUD_ROLE_SESSION_DURATION", "3600"))
    except ValueError:
        duration = 3600
    duration = max(900, min(duration, 43200))
    result = call_aliyun(
        "sts",
        "AssumeRole",
        {
            "RoleArn": role_arn,
            "RoleSessionName": session_name,
            "DurationSeconds": duration,
        },
    )
    return bool(result.get("success")), result


def print_config_summary(account_id: str, role_name: str, role_arn: str) -> None:
    print("\n配置摘要:")
    print("━" * 64)
    print(f"  账号 ID:   {account_id}")
    print(f"  角色名称:  {role_name}")
    print(f"  角色 ARN:  {role_arn}")
    print(f"  配置文件:  {CONFIG_FILE}")
    sign_in_url = _existing_signin_url()
    if sign_in_url:
        print(f"  CloudSSO:  {sign_in_url}")
    print("━" * 64)


def main() -> None:
    print_header("CloudQ 阿里云 - 角色配置向导")

    print_step("步骤 1/5: 验证阿里云身份")
    identity = call_aliyun("sts", "GetCallerIdentity")
    if not identity.get("success"):
        print_fail(identity.get("error", {}).get("message", "无法验证阿里云凭据"))
        print("\n请先设置 ALIBABA_CLOUD_ACCESS_KEY_ID / ALIBABA_CLOUD_ACCESS_KEY_SECRET，或设置 ALIBABA_CLOUD_PROFILE。")
        sys.exit(1)

    account_id = str(identity.get("data", {}).get("AccountId", ""))
    caller_arn = str(identity.get("data", {}).get("Arn", ""))
    print_ok(f"账号 ID: {account_id}")
    print_ok(f"当前身份: {caller_arn}")

    print("\n")
    print_step("步骤 2/5: 查询 RAM 角色")
    roles_result = call_aliyun("ram", "ListRoles", {"MaxItems": 25})
    if not roles_result.get("success"):
        print_fail(roles_result.get("error", {}).get("message", "无法读取 RAM 角色列表"))
        print("\n您也可以直接设置 ALIBABA_CLOUD_ROLE_ARN 后再运行 login_url.py。")
        sys.exit(1)

    roles = _extract_roles(roles_result.get("data", {}))
    if not roles:
        print_warn("当前账号未返回可选 RAM 角色。")
        choice = "c"
    else:
        print_ok(f"检测到 {len(roles)} 个角色")
        print("\n可用角色列表:")
        print("━" * 88)
        for idx, role in enumerate(roles, 1):
            role_name = str(role.get("RoleName", "未知"))
            role_arn = str(role.get("Arn", ""))
            description = str(role.get("Description", "无描述") or "无描述")
            print(f"  {idx:2d}. {cyan(role_name)}")
            print(f"      ARN: {role_arn}")
            print(f"      描述: {description}")
            print("")
        print("━" * 88)
        print("输入角色序号以选择已有角色，或输入 c 创建推荐角色 CloudQAuditRole。")
        try:
            choice = input(green("请选择 [1-n / c]: ")).strip().lower()
        except (EOFError, KeyboardInterrupt):
            choice = ""

    if choice == "c":
        print("\n")
        print_warn("即将创建只读治理角色 CloudQAuditRole，并关联 AliyunGovernanceReadOnlyAccess 与 AliyunRAMReadOnlyAccess。")
        try:
            confirm = input(green("是否继续创建？[y/N]: ")).strip().lower()
        except (EOFError, KeyboardInterrupt):
            confirm = ""
        if confirm not in {"y", "yes"}:
            print_warn("已取消。")
            sys.exit(1)

        created, data = run_create_role()
        if not created:
            print_fail(data.get("error", {}).get("message", "创建角色失败"))
            sys.exit(1)
        role_data = data.get("data", {})
        role_name = str(role_data.get("roleName", DEFAULT_ROLE_NAME))
        role_arn = str(role_data.get("roleArn", ""))
        auto_created = True
        print_ok(f"角色创建完成: {role_name}")
    else:
        try:
            selected_index = int(choice) - 1
        except ValueError:
            print_fail(f"无效的选择: {choice}")
            sys.exit(1)
        if selected_index < 0 or selected_index >= len(roles):
            print_fail(f"无效的选择: {choice}")
            sys.exit(1)

        selected = roles[selected_index]
        role_name = str(selected.get("RoleName", ""))
        role_arn = str(selected.get("Arn", ""))
        auto_created = False
        save_config(account_id, role_name, role_arn, auto_created=False)
        print_ok(f"已选择角色: {role_name}")

    if auto_created:
        save_config(account_id, role_name, role_arn, auto_created=True)

    print("\n")
    print_step("步骤 3/5: 保存本地配置")
    print_ok(f"配置文件已保存: {CONFIG_FILE}")

    print("\n")
    print_step("步骤 4/5: 测试角色扮演")
    success, result = test_role(role_arn)
    if success:
        print_ok("AssumeRole 测试成功")
    else:
        print_warn(result.get("error", {}).get("message", "AssumeRole 测试失败"))
        print_warn("角色可能存在信任策略限制，或当前身份无权扮演该角色。")

    print("\n")
    print_step("步骤 5/5: 完成")
    print_config_summary(account_id, role_name, role_arn)
    print("\n现在您可以:")
    print(f"  1. 查询身份: python3 {SCRIPT_DIR / 'aliyun_cli.py'} sts GetCallerIdentity")
    print(f"  2. 查询角色: python3 {SCRIPT_DIR / 'aliyun_cli.py'} ram ListRoles '{{\"MaxItems\": 10}}'")
    print(f"  3. 生成控制台入口: python3 {SCRIPT_DIR / 'login_url.py'} \"https://home.console.aliyun.com/\"")


if __name__ == "__main__":
    main()
