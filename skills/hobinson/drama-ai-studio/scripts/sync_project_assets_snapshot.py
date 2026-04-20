#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调用 DramaAIStudio（灵伴 iDrama）OpenAPI，拉取指定剧目下全部资产详情：
含 §6.3 的候选图 URL 列表，以及 §6.7 的终稿候选列表。

将快照写入「数据总目录 / 项目ID / assets.json」；若与上次快照差异则打印变更摘要。

依赖：Python 3.9+，仅标准库。

认证：环境变量 IDRAMA_TOKEN，或命令行 --token。
基地址：环境变量 IDRAMA_BASE_URL，默认 https://idrama.lingban.cn
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# 从候选图访问 URL 中解析候选图 ID（兼容 …/candidates/<id>/image 与 …/image/original）
_CAND_ID_FROM_URL = re.compile(r"/candidates/([^/]+)/image")


def _utc_iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_candidate_id_from_image_url(url: str) -> Optional[str]:
    """
    从服务端返回的候选图 image URL 中解析候选图 ID。
    若无法解析则返回 None（仍会保留原始 URL 做对比）。
    """
    if not url or not isinstance(url, str):
        return None
    m = _CAND_ID_FROM_URL.search(url)
    return m.group(1) if m else None


def _request_json(
    base_url: str,
    token: str,
    method: str,
    path: str,
    *,
    timeout: float = 120.0,
) -> Tuple[int, Dict[str, Any]]:
    """
    发起已鉴权的 JSON 请求，返回 (http_status, body_dict)。
    body 若不是合法 JSON 则包装为 {"_raw": text}。
    """
    url = urllib.parse.urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
    req = urllib.request.Request(
        url,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            status = getattr(resp, "status", 200) or 200
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        status = e.code
    try:
        body = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        body = {"_raw": raw, "_parse_error": True}
    return status, body if isinstance(body, dict) else {"_raw": body}


def _unwrap_api(body: Dict[str, Any]) -> Tuple[int, Any, str]:
    """统一响应：返回 (code, data, msg)。非标准结构时 code 视 HTTP 已在外层处理，此处尽量兜底。"""
    code = body.get("code", 0)
    try:
        code_int = int(code)
    except (TypeError, ValueError):
        code_int = 0
    return code_int, body.get("data"), str(body.get("msg") or "")


def fetch_asset_list(base_url: str, token: str, play_id: str, *, include_deleted: bool) -> List[Dict[str, Any]]:
    # 第 1 步：拉资产列表（§6.1），作为后续详情的索引。
    q = {"include_deleted": "true"} if include_deleted else {}
    qs = urllib.parse.urlencode(q) if q else ""
    path = f"/openapi/drama/{play_id}/assets/list" + (f"?{qs}" if qs else "")
    status, body = _request_json(base_url, token, "GET", path)
    code, data, msg = _unwrap_api(body)
    if status >= 400 or code != 1:
        raise RuntimeError(f"资产列表失败 HTTP {status} code={code} msg={msg} body_keys={list(body.keys())}")
    if not isinstance(data, list):
        raise RuntimeError(f"资产列表 data 类型异常: {type(data)}")
    return [x for x in data if isinstance(x, dict)]


def fetch_asset_detail(base_url: str, token: str, play_id: str, asset_id: str) -> Tuple[Dict[str, Any], List[str], List[str]]:
    """
    单个资产：§6.3 详情（含 candidate_image_urls）。
    返回 (精简字段 dict, candidate_ids 按接口顺序, 原始 urls 列表)。
    """
    path = f"/openapi/drama/{play_id}/assets/{urllib.parse.quote(str(asset_id), safe='')}"
    status, body = _request_json(base_url, token, "GET", path)
    code, data, msg = _unwrap_api(body)
    if status >= 400 or code != 1 or not isinstance(data, dict):
        raise RuntimeError(
            f"资产详情失败 asset_id={asset_id} HTTP {status} code={code} msg={msg}"
        )
    urls = data.get("candidate_image_urls") or []
    if not isinstance(urls, list):
        urls = []
    cand_ids: List[str] = []
    for u in urls:
        if not isinstance(u, str):
            continue
        cid = parse_candidate_id_from_image_url(u)
        if cid is not None:
            cand_ids.append(cid)
        else:
            # 无法用路径解析时，用稳定摘要占位，避免 Py hash() 随机盐导致误判
            h = hashlib.sha256(u.encode("utf-8")).hexdigest()[:16]
            cand_ids.append(f"_unparsed:{h}")
    slim = {
        "id": str(data.get("id", asset_id)),
        "type": data.get("type"),
        "name": data.get("name"),
        "description": data.get("description"),
        "deleted": bool(data.get("deleted", False)),
        "operation_time": data.get("operation_time"),
        "has_final_image": data.get("has_final_image"),
        "prompt": data.get("prompt"),
    }
    return slim, cand_ids, [u for u in urls if isinstance(u, str)]


def fetch_final_candidates(
    bas e_url: str, token: str, play_id: str, asset_type: Any, asset_id: str
) -> Tuple[List[Dict[str, Any]], List[str], Optional[str]]:
    """
    §6.7 终稿列表。
    返回 (items 原样, candidate_id 有序列表, 若失败则为 error 字符串否则 None)。
    """
    try:
        at = int(asset_type)
    except (TypeError, ValueError):
        return [], [], "invalid asset_type"
    path = (
        f"/openapi/drama/{play_id}/assets/{at}/"
        f"{urllib.parse.quote(str(asset_id), safe='')}/general/candidates/final-candidates"
    )
    status, body = _request_json(base_url, token, "GET", path)
    code, data, msg = _unwrap_api(body)
    if status >= 400 or code != 1:
        return [], [], f"HTTP {status} code={code} msg={msg}"
    if not isinstance(data, dict):
        return [], [], "data not object"
    items = data.get("items") or []
    if not isinstance(items, list):
        return [], [], "items not list"
    out_items: List[Dict[str, Any]] = [x for x in items if isinstance(x, dict)]
    finals: List[str] = []
    for it in out_items:
        cid = it.get("candidate_id")
        if cid is not None:
            finals.append(str(cid))
    return out_items, finals, None


def build_snapshot(
    base_url: str,
    token: str,
    play_id: str,
    *,
    include_deleted: bool,
) -> Dict[str, Any]:
    """聚合当前剧目全部资产 + 候选图 + 终稿，形成可落盘的快照 dict。"""
    rows = fetch_asset_list(base_url, token, play_id, include_deleted=include_deleted)
    assets_out: List[Dict[str, Any]] = []
    for summary in sorted(rows, key=lambda x: str(x.get("id", ""))):
        aid = str(summary.get("id", ""))
        if not aid:
            continue
        slim, cand_ids, cand_urls = fetch_asset_detail(base_url, token, play_id, aid)
        at = slim.get("type")
        if at is None:
            at = summary.get("type")
        final_items, final_ids, final_err = fetch_final_candidates(
            base_url, token, play_id, at, aid
        )
        assets_out.append(
            {
                **slim,
                "list_summary": {
                    "cover_url": summary.get("cover_url"),
                    "has_final_image": summary.get("has_final_image"),
                },
                "candidate_ids": cand_ids,
                "candidate_image_urls": cand_urls,
                "final_candidate_ids": final_ids,
                "final_items": final_items,
                "final_fetch_error": final_err,
            }
        )
    return {
        "schema_version": 1,
        "play_id": str(play_id),
        "fetched_at": _utc_iso_now(),
        "include_deleted": include_deleted,
        "assets": assets_out,
    }


def _asset_key_map(snapshot: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    assets = snapshot.get("assets") or []
    out: Dict[str, Dict[str, Any]] = {}
    if isinstance(assets, list):
        for a in assets:
            if isinstance(a, dict) and a.get("id") is not None:
                out[str(a["id"])] = a
    return out


def diff_snapshots(old: Optional[Dict[str, Any]], new: Dict[str, Any]) -> Dict[str, Any]:
    """
    对比两次快照，产出结构化变更说明。
    当 old 为 None（首次）时，返回 {"initial": True, ...}。
    """
    if old is None:
        return {
            "initial": True,
            "play_id": new.get("play_id"),
            "asset_count": len(new.get("assets") or []),
        }

    old_m = _asset_key_map(old)
    new_m = _asset_key_map(new)
    old_ids = set(old_m.keys())
    new_ids = set(new_m.keys())

    changes: Dict[str, Any] = {
        "initial": False,
        "play_id": new.get("play_id"),
        "assets_added": sorted(new_ids - old_ids),
        "assets_removed": sorted(old_ids - new_ids),
        "assets_modified": [],
    }

    for aid in sorted(old_ids & new_ids):
        o = old_m[aid]
        n = new_m[aid]
        mods: Dict[str, Any] = {}
        for field in ("name", "type", "description", "deleted", "operation_time", "prompt"):
            if o.get(field) != n.get(field):
                mods[field] = {"before": o.get(field), "after": n.get(field)}
        if o.get("candidate_ids") != n.get("candidate_ids"):
            mods["candidate_ids"] = {"before": o.get("candidate_ids"), "after": n.get("candidate_ids")}
        if o.get("candidate_image_urls") != n.get("candidate_image_urls"):
            mods["candidate_image_urls"] = {
                "before_count": len(o.get("candidate_image_urls") or []),
                "after_count": len(n.get("candidate_image_urls") or []),
            }
        if o.get("final_candidate_ids") != n.get("final_candidate_ids"):
            mods["final_candidate_ids"] = {
                "before": o.get("final_candidate_ids"),
                "after": n.get("final_candidate_ids"),
            }
        if o.get("final_items") != n.get("final_items"):
            mods["final_items"] = {"before": o.get("final_items"), "after": n.get("final_items")}
        fe_o = o.get("final_fetch_error")
        fe_n = n.get("final_fetch_error")
        if fe_o != fe_n:
            mods["final_fetch_error"] = {"before": fe_o, "after": fe_n}
        if mods:
            entry = {"asset_id": aid, "name": n.get("name"), "changes": mods}
            changes["assets_modified"].append(entry)

    return changes


def has_meaningful_change(diff: Dict[str, Any]) -> bool:
    if diff.get("initial"):
        return False
    if diff.get("assets_added") or diff.get("assets_removed"):
        return True
    if diff.get("assets_modified"):
        return True
    return False


def load_json_file(path: str) -> Optional[Dict[str, Any]]:
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json_file(path: str, data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="拉取剧目资产快照（候选图 + 终稿），写入数据目录并对比上次结果",
    )
    parser.add_argument("play_id", help="剧目（项目）ID")
    parser.add_argument(
        "--data-dir",
        default=os.environ.get("IDRAMA_DATA_DIR", "./project_data"),
        help="数据总目录，其下每个剧目一个子目录（默认 ../project_data 或环境变量 IDRAMA_DATA_DIR）",
    )
    parser.add_argument(
        "--base-url",
        default=os.environ.get("IDRAMA_BASE_URL", "https://idrama.lingban.cn"),
        help="API 基地址（不含路径前缀，默认读 IDRAMA_BASE_URL）",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("IDRAMA_TOKEN", ""),
        help="Bearer Token（默认读环境变量 IDRAMA_TOKEN）",
    )
    parser.add_argument(
        "--include-deleted",
        action="store_true",
        help="资产列表包含已软删除项（对应 §6.1 include_deleted=true）",
    )
    parser.add_argument(
        "--print-full-snapshot",
        action="store_true",
        help="无论是否变化，将完整快照 JSON 打印到 stdout",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="仅输出变更或错误；正常情况不打印进度",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.WARNING if args.quiet else logging.INFO,
        format="%(levelname)s %(message)s",
    )

    token = (args.token or "").strip()
    if not token:
        logger.error("缺少 Token：请设置环境变量 IDRAMA_TOKEN 或使用 --token")
        return 2

    play_id = str(args.play_id).strip()
    project_dir = os.path.join(args.data_dir, play_id)
    snapshot_path = os.path.join(project_dir, "assets.json")

    # 第 2 步：构建最新快照并与本地 assets.json 对比。
    try:
        new_snap = build_snapshot(
            args.base_url,
            token,
            play_id,
            include_deleted=args.include_deleted,
        )
    except Exception:
        logger.exception("拉取快照失败 play_id=%s", play_id)
        return 1

    previous = load_json_file(snapshot_path)
    diff = diff_snapshots(previous, new_snap)

    if diff.get("initial"):
        save_json_file(snapshot_path, new_snap)
        if not args.quiet:
            print(json.dumps({"status": "initial", "path": snapshot_path, "detail": diff}, ensure_ascii=False, indent=2))
        elif args.print_full_snapshot:
            print(json.dumps(new_snap, ensure_ascii=False, indent=2))
        return 0

    if has_meaningful_change(diff):
        print(json.dumps({"status": "changed", "diff": diff}, ensure_ascii=False, indent=2))
        save_json_file(snapshot_path, new_snap)
        if args.print_full_snapshot:
            print(json.dumps({"status": "full_snapshot", "snapshot": new_snap}, ensure_ascii=False, indent=2))
        return 0

    # 无变更：可选更新 fetched_at 以保持「上次检查时间」——这里仍写回一份，便于审计抓取时间。
    save_json_file(snapshot_path, new_snap)
    if not args.quiet:
        print(json.dumps({"status": "unchanged", "play_id": play_id, "path": snapshot_path}, ensure_ascii=False, indent=2))
    if args.print_full_snapshot:
        print(json.dumps(new_snap, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
