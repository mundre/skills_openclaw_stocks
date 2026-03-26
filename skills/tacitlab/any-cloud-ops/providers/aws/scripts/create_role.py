#!/usr/bin/env python3
"""
AWS Provider — IAM 角色创建脚本。

功能：创建 CloudQAuditRole 角色并关联 ReadOnlyAccess 托管策略。
注意：本脚本包含 IAM 写入操作（CreateRole、AttachRolePolicy），
      仅应在用户明确同意后执行，不可自动运行。

用法:
    python3 create_role.py
    python3 create_role.py --role-name CloudQAuditRole
    python3 create_role.py --account-id 123456789012

返回码:
    0 - 角色创建成功或已存在，配置已保存
    1 - 参数错误
    2 - AWS 凭据缺失或无效
    3 - 角色创建失败
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

from aws_cli import call_aws  # noqa: E402

CONFIG_DIR = Path.home() / ".cloudq" / "aws"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_ROLE_NAME = "CloudQAuditRole"
POLICY_ARNS = ["arn:aws:iam::aws:policy/ReadOnlyAccess"]


def output_json(obj: Dict[str, Any]) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def output_error(code: str, message: str) -> Dict[str, Any]:
    return {
        "success": False,
        "action": "CreateAuditRole",
        "error": {"code": code, "message": message},
    }


def output_success(role_arn: str, account_id: str, role_id: str, role_name: str, auto_created: bool, warnings: List[str]) -> Dict[str, Any]:
    data = {
        "roleName": role_name,
        "roleArn": role_arn,
        "roleId": role_id,
        "accountId": account_id,
        "policiesAttached": POLICY_ARNS,
        "consoleLogin": True,
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


def save_config(account_id: str, role_name: str, role_arn: str, role_id: str, auto_created: bool) -> None:
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
        "roleId": role_id,
        "configuredAt": datetime.now(timezone.utc).isoformat(),
        "autoCreated": auto_created,
        "version": "1.0",
    }
    CONFIG_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

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


def main() -> None:
    parsed = parse_args()
    role_name = parsed["role_name"]
    account_id = parsed["account_id"]

    identity = call_aws("sts", "get-caller-identity")
    if not identity.get("success"):
        print(output_json(output_error(
            identity.get("error", {}).get("code", "MissingCredentials"),
            identity.get("error", {}).get("message", "无法验证 AWS 凭据"),
        )))
        sys.exit(2)

    if not account_id:
        account_id = str(identity.get("data", {}).get("Account", ""))
    if not account_id:
        print(output_json(output_error("GetCallerIdentityFailed", "无法获取当前 AWS 账号 ID")))
        sys.exit(2)

    existing = call_aws("iam", "get-role", {"RoleName": role_name})
    if existing.get("success"):
        role_data = existing.get("data", {}).get("Role", {})
        role_arn = str(role_data.get("Arn", ""))
        role_id = str(role_data.get("RoleId", "unknown"))
        save_config(account_id, role_name, role_arn, role_id, auto_created=False)
        print(output_json(output_success(role_arn, account_id, role_id, role_name, False, [])))
        sys.exit(0)

    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": f"arn:aws:iam::{account_id}:root"},
                "Action": "sts:AssumeRole",
            }
        ],
    }

    create_result = call_aws(
        "iam",
        "create-role",
        {
            "RoleName": role_name,
            "AssumeRolePolicyDocument": trust_policy,
            "Description": "CloudQ cross-cloud read-only governance role",
            "MaxSessionDuration": 43200,
        },
    )
    if not create_result.get("success"):
        err = create_result.get("error", {})
        print(output_json(output_error(err.get("code", "CreateRoleFailed"), err.get("message", "角色创建失败"))))
        sys.exit(3)

    role_data = create_result.get("data", {}).get("Role", {})
    role_arn = str(role_data.get("Arn", f"arn:aws:iam::{account_id}:role/{role_name}"))
    role_id = str(role_data.get("RoleId", "unknown"))

    warnings = []
    for policy_arn in POLICY_ARNS:
        attach_result = call_aws(
            "iam",
            "attach-role-policy",
            {"RoleName": role_name, "PolicyArn": policy_arn},
        )
        if not attach_result.get("success"):
            message = attach_result.get("error", {}).get("message", "未知错误")
            warnings.append(f"策略 {policy_arn} 关联失败: {message}")

    save_config(account_id, role_name, role_arn, role_id, auto_created=True)
    print(output_json(output_success(role_arn, account_id, role_id, role_name, True, warnings)))
    sys.exit(0)


if __name__ == "__main__":
    main()
