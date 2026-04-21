#!/usr/bin/env python3
"""
代码审计报告生成器 - 生成飞书消息格式
敏感配置（飞书群 ID）通过环境变量读取，不硬编码
"""
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# 飞书群 ID 通过环境变量读取（不硬编码）
FEISHU_GROUP_ID = os.environ.get("CODE_REVIEW_FEISHU_CHAT_ID", "")


def severity_emoji(severity: str) -> str:
    """严重级别对应 emoji"""
    mapping = {
        "ERROR": "🔴",
        "HIGH": "🔴",
        "WARNING": "🟡",
        "MEDIUM": "🟡",
        "INFO": "🟢",
        "LOW": "🟢",
    }
    return mapping.get(severity.upper(), "⚪")


def severity_label(severity: str) -> str:
    """严重级别标签"""
    mapping = {
        "ERROR": "错误",
        "HIGH": "严重",
        "WARNING": "警告",
        "MEDIUM": "中等",
        "INFO": "提示",
        "LOW": "低",
    }
    return mapping.get(severity.upper(), severity)


def format_file_path(path: str) -> str:
    """精简文件路径显示"""
    if "/tmp/svn_repos/" in path:
        parts = path.split("/tmp/svn_repos/")[1].split("/", 1)
        if len(parts) > 1:
            return parts[1]
    return os.path.basename(path)


def group_issues_by_file(issues: List[Dict]) -> Dict[str, List[Dict]]:
    """按文件分组问题"""
    grouped = {}
    for issue in issues:
        file_key = issue.get("file", "unknown")
        if file_key not in grouped:
            grouped[file_key] = []
        grouped[file_key].append(issue)
    return grouped


def generate_fix_suggestion(issue: Dict, lang: str) -> str:
    """生成修复建议"""
    message = issue.get("message", "")
    test_id = issue.get("test_id", "")
    symbol = issue.get("symbol", "")
    rule = issue.get("rule", "")

    suggestions = {
        # Django/Python
        "B101": "使用随机数种子替代硬编码值",
        "B102": "避免使用 exec/eval，或严格限制输入",
        "B103": "确保 DEBUG=False 在生产环境",
        "B104": "避免硬编码 IP 地址",
        "B105": "避免硬编码密码/密钥，使用环境变量",
        "B106": "避免使用弱加密算法（MD5/SHA1）",
        "B107": "确保 SECRET_KEY 从环境变量读取",
        "B108": "确保日志不记录敏感信息",
        "B201": "避免使用 shell=True，使用列表形式参数",
        "B301": "避免使用 pickle 反序列化",
        "B303": "避免使用 DES/RC4 等弱加密",
        "B307": "避免使用 eval()",
        "B310": "避免 URL 包含用户输入",
        "B311": "避免使用 random 生成安全随机数",
        "B313": "避免使用 xml.etree.ElementTree 解析外部 XML",
        "B323": "确保使用 HTTPS",
        "B324": "避免使用 hashlib.md5",
        "B413": "避免使用 pycrypto",
        "B419": "避免使用 requests 不验证证书",
        "B506": "避免使用 yaml.load 不指定 Loader",
        "B601": "避免使用 subprocess without shell=False",
        "B602": "避免使用 subprocess with shell=True",
        "B603": "避免使用 os.system",
        "B604": "避免使用 os.popen",
        "B701": "避免使用 wtforms 不转义",
    }

    if test_id in suggestions:
        return suggestions[test_id]
    if symbol in suggestions:
        return suggestions[symbol]

    # 根据消息内容生成通用建议
    msg_lower = message.lower()
    if "hardcoded" in msg_lower or "硬编码" in msg_lower:
        return "使用环境变量或配置文件管理敏感信息"
    if "sql" in msg_lower or "注入" in msg_lower:
        return "使用参数化查询，避免字符串拼接 SQL"
    if "eval" in msg_lower:
        return "避免使用 eval()，改用更安全的替代方案"
    if "shell" in msg_lower:
        return "避免使用 shell=True，使用列表参数形式"
    if "password" in msg_lower or "secret" in msg_lower:
        return "使用环境变量或密钥管理服务，不要硬编码"
    if "debug" in msg_lower:
        return "确保生产环境 DEBUG=False"

    return "建议人工审核并修复"


def build_report(
    repo_name: str,
    lang: str,
    scan_result: Dict[str, Any],
    scan_type: str,
    changed_files: List[str] = None,
) -> Dict[str, Any]:
    """构建飞书报告内容"""
    all_issues = []
    if isinstance(scan_result, dict) and "issues" in scan_result and "summary" in scan_result:
        all_issues = scan_result.get("issues", [])
    elif isinstance(scan_result, dict):
        for lang_result in scan_result.values():
            if isinstance(lang_result, dict):
                all_issues.extend(lang_result.get("issues", []))

    total = len(all_issues)
    errors = sum(1 for i in all_issues if i.get("severity") in ("ERROR", "HIGH"))
    warnings = sum(1 for i in all_issues if i.get("severity") in ("WARNING", "MEDIUM"))
    info = sum(1 for i in all_issues if i.get("severity") in ("INFO", "LOW"))

    # 仓库别名（通用展示名称，不含敏感 URL）
    repo_alias = {
        "ops_api": "运维后台后端 (Django)",
        "ops_web": "运维后台前端 (React+TS)",
        "ops_api_trunk": "运维后台后端 (Django)",
        "ops_web_trunk": "运维后台前端 (React+TS)",
        "gm": "GM后台 (PHP+React)",
    }.get(repo_name, repo_name)

    # 仓库 URL 从 svn_manager 动态读取（不硬编码）
    try:
        from svn_manager import get_repo_url
        repo_url = get_repo_url(repo_name)
    except Exception:
        repo_url = ""

    scan_type_label = "🔄 增量扫描" if scan_type == "incremental" else "📋 全量扫描"
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    url_line = f"\n🔗 {repo_url}" if repo_url else ""

    header = f"""📊 **代码审计报告**
━━━━━━━━━━━━━━━━━━
🏷️ 仓库：{repo_alias}{url_line}
📅 时间：{time_str}
🔍 方式：{scan_type_label}
📁 扫描文件：{len(changed_files) if changed_files else 'N/A'}
🐛 问题总数：{total}
  🔴 严重/错误：{errors}
  🟡 警告：{warnings}
  🟢 提示：{info}
━━━━━━━━━━━━━━━━━━"""

    if total == 0:
        body = "\n\n✅ **本次扫描无问题，代码质量良好！**"
    else:
        sorted_issues = sorted(
            all_issues,
            key=lambda x: (
                0 if x.get("severity") in ("ERROR", "HIGH") else
                1 if x.get("severity") in ("WARNING", "MEDIUM") else 2
            )
        )
        display_issues = sorted_issues[:20]

        body_parts = []
        for issue in display_issues:
            emoji = severity_emoji(issue.get("severity", "INFO"))
            file_p = format_file_path(issue.get("file", ""))
            line = issue.get("line", 0)
            message = issue.get("message", "")[:80]
            suggestion = generate_fix_suggestion(issue, lang)

            issue_text = f"""{emoji} **{severity_label(issue.get("severity", "INFO"))}** | `{file_p}`:{line}
   └ {message}
   └ 🛠️ 修复：{suggestion}"""
            body_parts.append(issue_text)

        body = "\n\n".join(body_parts)

        if total > 20:
            body += f"\n\n_...还有 {total - 20} 个问题未显示_"

    footer = "\n━━━━━━━━━━━━━━━━━━\n⚙️ 由 OpenClaw 代码审计 Skill 自动生成"

    full_report = header + body + footer

    return {
        "repo_name": repo_name,
        "repo_alias": repo_alias,
        "scan_type": scan_type,
        "total_issues": total,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "changed_files_count": len(changed_files) if changed_files else 0,
        "text": full_report,
        "issues": all_issues[:50],
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 report_generator.py <repo_name> [scan_result_json]", file=sys.stderr)
        sys.exit(1)

    repo_name = sys.argv[1]

    if len(sys.argv) >= 3:
        scan_result = json.loads(sys.argv[2])
    else:
        scan_result = {}

    scan_type = sys.argv[3] if len(sys.argv) >= 4 else "incremental"
    changed_files_json = sys.argv[4] if len(sys.argv) >= 5 else "[]"
    changed_files = json.loads(changed_files_json) if changed_files_json != "[]" else None

    lang_map = {
        "ops_api": "django",
        "ops_web": "react",
        "ops_api_trunk": "django",
        "ops_web_trunk": "react",
        "gm": "mixed",
    }

    report = build_report(
        repo_name,
        lang_map.get(repo_name, "unknown"),
        scan_result,
        scan_type,
        changed_files,
    )

    print(json.dumps(report, ensure_ascii=False, indent=2))
