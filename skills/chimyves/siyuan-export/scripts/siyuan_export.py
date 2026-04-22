#!/usr/bin/env python3
"""
思源笔记文档导出工具（Word）

通过思源笔记 API 将文档导出为 Word(.docx) 格式。
支持单文档导出和批量导出子文档，返回结构化 JSON 输出。

配置:
    config.json（技能目录下）:
    {"baseURL": "http://127.0.0.1:6806", "token": "你的API Token", "timeout": 10000}

用法:
    # 单文档导出
    python siyuan_export.py --doc-id <id> --output <dir>
    python siyuan_export.py --path "/AI/某文档" --output C:/Desktop

    # 导出文档及其所有子文档
    python siyuan_export.py --doc-id <id> --children --output C:/Desktop/Midjourney
"""

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


def get_config():
    """从配置文件读取配置"""
    base_url = "http://127.0.0.1:6806"
    token = ""

    config_paths = [
        Path(__file__).parent.parent / "config.json",
        Path(__file__).parent.parent.parent / "siyuan-skill" / "config.json",
    ]
    for cp in config_paths:
        if cp.exists():
            try:
                with open(cp, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                if cfg.get("token"):
                    token = cfg["token"]
                if cfg.get("baseURL"):
                    base_url = cfg["baseURL"]
                break
            except Exception:
                pass

    # 环境变量覆盖
    if os.environ.get("SIYUAN_TOKEN"):
        token = os.environ["SIYUAN_TOKEN"]
    if os.environ.get("SIYUAN_BASE_URL"):
        base_url = os.environ["SIYUAN_BASE_URL"]

    return {"base_url": base_url, "token": token}


def api_call(endpoint: str, data: dict, config: dict) -> dict:
    """调用思源 API 并返回解析后的 JSON"""
    url = f"{config['base_url']}{endpoint}"
    body = json.dumps(data, ensure_ascii=False).encode("utf-8")
    req = Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Token {config['token']}",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=30) as resp:
            raw = resp.read()
            for enc in ("utf-8", "gbk", "latin-1"):
                try:
                    text = raw.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                text = raw.decode("utf-8", errors="replace")
            return json.loads(text)
    except HTTPError as e:
        err_body = ""
        try:
            err_body = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        return {"code": e.code, "msg": f"HTTP {e.code}: {err_body[:200]}"}
    except URLError as e:
        return {"code": -1, "msg": f"连接失败: {e.reason}"}
    except json.JSONDecodeError as e:
        return {"code": -1, "msg": f"JSON 解析失败: {e}"}


def resolve_doc_id(path_or_id: str, config: dict) -> str | None:
    """将人类可读路径转换为文档 ID"""
    if path_or_id is None:
        return path_or_id
    if len(path_or_id) == 22 and path_or_id[14] == "-":
        return path_or_id
    if path_or_id.startswith("/"):
        result = api_call("/api/filetree/getDocByPath", {"path": path_or_id}, config)
        if result.get("code") == 0 and result.get("data"):
            doc_data = result["data"]
            if isinstance(doc_data, dict):
                return doc_data.get("id")
            return str(doc_data)
        else:
            print(f"[WARN] 路径转换失败: {result.get('msg', 'unknown')}", file=sys.stderr)
            return None
    return path_or_id


def get_child_docs(doc_id: str, config: dict) -> list[dict]:
    """
    获取文档下所有子文档（直接子文档 + 嵌套子文档）

    Returns:
        子文档列表，每项包含 id 和 content(标题)
    """
    # 先获取父文档的 hpath，用于 LIKE 查询
    doc_info = api_call(
        "/api/query/sql",
        {"stmt": f"SELECT id, content, hpath FROM blocks WHERE id = '{doc_id}' AND type = 'd'"},
        config,
    )
    if doc_info.get("code") != 0 or not doc_info.get("data"):
        return []

    parent_hpath = doc_info["data"][0]["hpath"]
    parent_content = doc_info["data"][0].get("content", "")

    # 查询所有子文档：hpath 以父文档路径为前缀，且不是父文档本身
    escaped_hpath = parent_hpath.replace("'", "''")
    result = api_call(
        "/api/query/sql",
        {"stmt": f"SELECT id, content, hpath FROM blocks WHERE hpath LIKE '{escaped_hpath}/%' AND type = 'd' ORDER BY hpath"},
        config,
    )

    if result.get("code") != 0:
        return []

    return result.get("data", [])


def export_docx(doc_id: str, output: str, config: dict) -> dict:
    """
    导出文档为 Word 格式

    Args:
        doc_id: 文档 ID
        output: 输出目录路径，API 会在该目录下以文档标题命名生成 .docx 文件

    Returns:
        结构化结果字典
    """
    save_dir = Path(output)
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = str(save_dir).replace("\\", "/")

    # 调用 exportDocx 接口
    req_data = {
        "id": doc_id,
        "savePath": save_path,
        "removeAssets": True,  # 图片打包进文档，只生成单个文件
    }
    result = api_call("/api/export/exportDocx", req_data, config)

    if result.get("code") != 0:
        return {
            "success": False,
            "error": "api_error",
            "message": result.get("msg", "未知错误"),
            "api_code": result.get("code"),
        }

    api_path = result.get("data", {}).get("path", "")
    if not api_path:
        return {
            "success": False,
            "error": "no_path_returned",
            "message": "API 成功但未返回文件路径",
        }

    final_path = Path(api_path)
    file_size = final_path.stat().st_size if final_path.exists() else 0

    return {
        "success": True,
        "data": {
            "path": str(final_path),
            "size_bytes": file_size,
            "size_kb": round(file_size / 1024, 1),
        },
    }


def export_children(doc_id: str, output: str, config: dict, include_self: bool = False, json_mode: bool = False) -> dict:
    """
    批量导出文档的所有子文档

    Args:
        doc_id: 父文档 ID
        output: 输出目录路径
        include_self: 是否同时导出父文档本身
        json_mode: 是否静默模式

    Returns:
        批量导出结果
    """
    children = get_child_docs(doc_id, config)
    total = len(children)
    if total == 0:
        return {
            "success": False,
            "error": "no_children",
            "message": "该文档下没有子文档",
        }

    if not json_mode:
        print(f"发现 {total} 个子文档，开始批量导出...", file=sys.stderr)

    results = []
    ok_count = 0
    fail_count = 0

    # 可选：同时导出父文档本身
    if include_self:
        if not json_mode:
            print(f"  [0/{total + 1}] 导出父文档 {doc_id}...", file=sys.stderr)
        r = export_docx(doc_id, output, config)
        if r.get("success"):
            ok_count += 1
        else:
            fail_count += 1
        results.append({
            "id": doc_id,
            "title": "(parent)",
            "result": r,
        })

    for i, child in enumerate(children, 1):
        child_id = child["id"]
        child_title = child.get("content", "")
        if not json_mode:
            print(f"  [{i}/{total}] 导出: {child_title}", file=sys.stderr)

        r = export_docx(child_id, output, config)
        if r.get("success"):
            ok_count += 1
        else:
            fail_count += 1
        results.append({
            "id": child_id,
            "title": child_title,
            "result": r,
        })

    return {
        "success": fail_count == 0,
        "data": {
            "total": total + (1 if include_self else 0),
            "success_count": ok_count,
            "fail_count": fail_count,
            "output_dir": str(Path(output).resolve()),
            "details": results,
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="思源笔记文档导出工具（Word）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 按 ID 导出单个文档到桌面
  python siyuan_export.py --doc-id 20260404211618-s3bjc3l

  # 按路径导出，指定输出目录
  python siyuan_export.py --path "/AI/AIGC/绘画" --output C:/output

  # 导出文档下所有子文档
  python siyuan_export.py --doc-id 20260404211558-ca856ca --children --output C:/Desktop/Midjourney

  # 导出文档本身 + 所有子文档
  python siyuan_export.py --doc-id 20260404211558-ca856ca --children --include-self --output C:/Desktop/Midjourney
        """,
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--doc-id", "-i", help="文档 ID（如 20260404211618-s3bjc3l）")
    group.add_argument("--path", "-p", help="文档路径（如 /AI/AIGC/绘画）")

    parser.add_argument("--output", "-o", default="", help="输出目录（默认：桌面）")
    parser.add_argument("--children", "-c", action="store_true", help="导出该文档下所有子文档（批量模式）")
    parser.add_argument("--include-self", action="store_true", help="批量模式时同时导出父文档本身（需配合 --children）")
    parser.add_argument("--json", action="store_true", help="仅输出 JSON 结果")

    args = parser.parse_args()
    config = get_config()

    if not config["token"]:
        print(json.dumps({"success": False, "error": "no_token", "message": "未配置 token，请在 config.json 中填写"}, ensure_ascii=False))
        sys.exit(1)

    source = args.doc_id or args.path
    doc_id = resolve_doc_id(source, config)
    if not doc_id:
        print(json.dumps({"success": False, "error": "resolve_failed", "message": f"无法识别文档: {source}"}, ensure_ascii=False))
        sys.exit(1)

    output = args.output or os.path.join(os.path.expanduser("~"), "Desktop")

    if args.children:
        # 批量导出子文档
        if not args.json:
            print(f"正在批量导出子文档...", file=sys.stderr)
            print(f"  父文档ID: {doc_id}", file=sys.stderr)
            print(f"  输出到: {output}", file=sys.stderr)

        result = export_children(doc_id, output, config, include_self=args.include_self, json_mode=args.json)
    else:
        # 单文档导出
        if not args.json:
            print(f"正在导出文档...", file=sys.stderr)
            print(f"  文档ID: {doc_id}", file=sys.stderr)
            print(f"  输出到: {output}", file=sys.stderr)

        result = export_docx(doc_id, output, config)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
