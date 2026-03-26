#!/usr/bin/env python3
"""
阿里云 Provider — RAM 角色创建脚本。

功能：创建 CloudQAuditRole，并关联只读治理相关系统策略。
注意：本脚本包含 RAM 写入操作（CreateRole、AttachPolicyToRole），
      仅应在用户明确同意后执行，不可自动运行。

用法:
    python3 create_role.py
    python3 create_role.py --role-name CloudQAuditRole
    python3 create_role.py --account-id 1234567890123456
"""

from __future__ import annotations

import json
import os
import platform
import stat
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from aliyun_cli import call_aliyun  # noqa: E402

CONFIG_DIR = Path.home() / ".cloudq" / "aliyun"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_ROLE_NAME = "CloudQAuditRole"
POLICIES = ["AliyunGovernanceReadOnlyAccess", "AliyunRAMReadOnlyAccess"]


def output_json(obj: Dict[str, Any]) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def output_error(code: str, message: str) -> Dict[str, Any]:
    return {
        "success": False,
        "action": "CreateAuditRole",
        "error": {"code": code, "message": message},
    }


def output_success(role_arn: str, account_id: str, role_name: str, auto_created: bool, warnings: List[str]) -> Dict[str, Any]:
    data = {
        "roleName": role_name,
        "roleArn": role_arn,
        "accountId": account_id,
        "policiesAttached": POLICIES,
        "configFile": str(CONFIG_FILE),
        "autoCreated": auto_created,
    }
    if warnings:
        data["warnings"] = warnings
    return {
        "success": True,
        "action": "CreateAuditRole",
        "data": data,
    }


def save_config(account_id: str, role_name: str, role_arn: str, auto_created: bool) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if platform.system() != "Windows":
        try:
            os.chmod(str(CONFIG_DIR), stat.S_IRWXU)
        except OSError:
            pass

    current = {}
    if CONFIG_FILE.exists():
        try:
            current = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            current = {}

    current.update({
        "accountId": account_id,
        "roleName": role_name,
        "roleArn": role_arn,
        "configuredAt": datetime.now(timezone.utc).isoformat(),
        "autoCreated": auto_created,
        "version": "1.0",
    })
    CONFIG_FILE.write_text(json.dumps(current, indent=2, ensure_ascii=False), encoding="utf-8")

    if platform.system() != "Windows":
        try:
            os.chmod(str(CONFIG_FILE), stat.S_IRUSR | stat.S_IWUSR)
        except OSError:
            pass


def parse_args() -> Dict[str, str]:
    role_name = DEFAULT_ROLE_NAME
    account_id = ""
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--role-name" and i + 1 < len(args):
            role_name = args[i + 1]
            i += 2
        elif args[i] == "--account-id" and i + 1 < len(args):
            account_id = args[i + 1]
            i += 2
        else:
            print(output_json(output_error("InvalidParameter", f"未知参数: {args[i]}")))
            sys.exit(1)
    return {"role_name": role_name, "account_id": account_id}


def extract_roles(data: Dict[str, Any]) -> List[Dict[str, Any]]:
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


def find_role(role_name: str) -> Dict[str, Any]:
    roles_result = call_aliyun("ram", "ListRoles", {"MaxItems": 100})
    if not roles_result.get("success"):
        return {}
    for item in extract_roles(roles_result.get("data", {})):
        if str(item.get("RoleName", "")) == role_name:
            return item
    return {}


def main() -> None:
    parsed = parse_args()
    role_name = parsed["role_name"]
    account_id = parsed["account_id"]

    identity = call_aliyun("sts", "GetCallerIdentity")
    if not identity.get("success"):
        print(output_json(output_error(
            identity.get("error", {}).get("code", "MissingCredentials"),
            identity.get("error", {}).get("message", "无法验证阿里云凭据"),
        )))
        sys.exit(2)

    if not account_id:
        account_id = str(identity.get("data", {}).get("AccountId", ""))
    if not account_id:
        print(output_json(output_error("GetCallerIdentityFailed", "无法获取当前阿里云账号 ID")))
        sys.exit(2)

    existing = find_role(role_name)
    if existing:
        role_arn = str(existing.get("Arn", f"acs:ram::{account_id}:role/{role_name}"))
        save_config(account_id, role_name, role_arn, auto_created=False)
        print(output_json(output_success(role_arn, account_id, role_name, False, [])))
        sys.exit(0)

    trust_policy = {
        "Statement": [
            {
                "Action": "sts:AssumeRole",
                "Effect": "Allow",
                "Principal": {
                    "RAM": [f"acs:ram::{account_id}:root"]
                },
            }
        ],
        "Version": "1",
    }

    create_result = call_aliyun(
        "ram",
        "CreateRole",
        {
            "RoleName": role_name,
            "Description": "CloudQ cross-cloud read-only governance role",
            "AssumeRolePolicyDocument": trust_policy,
            "MaxSessionDuration": 43200,
        },
    )
    if not create_result.get("success"):
        error = create_result.get("error", {})
        print(output_json(output_error(error.get("code", "CreateRoleFailed"), error.get("message", "角色创建失败"))))
        sys.exit(3)

    role_arn = str(create_result.get("data", {}).get("Role", {}).get("Arn", f"acs:ram::{account_id}:role/{role_name}"))
    warnings = []
    for policy_name in POLICIES:
        attach_result = call_aliyun(
            "ram",
            "AttachPolicyToRole",
            {
                "PolicyType": "System",
                "PolicyName": policy_name,
                "RoleName": role_name,
            },
        )
        if not attach_result.get("success"):
            warnings.append(f"策略 {policy_name} 关联失败: {attach_result.get('error', {}).get('message', '未知错误')}")

    save_config(account_id, role_name, role_arn, auto_created=True)
    print(output_json(output_success(role_arn, account_id, role_name, True, warnings)))
    sys.exit(0)


if __name__ == "__main__":
    main()
