#!/usr/bin/env python3
"""
Phase 2: 消费金融信披内容抓取器
扫描 announcements.json，按 URL 后缀匹配处理器，下载内容到 content/ 目录
解耦设计：处理器独立，新增处理器只需放在 processors/ 目录
"""
import argparse
import asyncio
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "processors"))

# 动态导入所有处理器（自动注册）
import processors
import processors.pdf_handler   # noqa: auto-registers via @register_handler
import processors.html_handler  # noqa
import processors.vue_handler   # noqa
import processors.image_handler # noqa
import processors.cloudflare_handler  # noqa
from processors import HANDLERS, get_handler, make_id
from urllib.parse import urlparse, urljoin

from playwright.async_api import async_playwright


STEALTH_ARGS = [
    "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
    "--disable-blink-features=AutomationControlled",
    "--disable-web-security", "--enable-webgl",
    "--allow-running-insecure-content", "--headless=new",
]


def parse_args():
    parser = argparse.ArgumentParser(description="消费金融信披内容抓取（Phase 2）")
    parser.add_argument("--date", default=None,
                        help="指定日期目录（默认最新）")
    parser.add_argument("--company", default=None,
                        help="指定公司名（逗号分隔），留空则全部")
    parser.add_argument("--workers", type=int, default=2,
                        help="并发数（默认2）")
    parser.add_argument("--dry-run", action="store_true",
                        help="不写文件，只打印预期")
    parser.add_argument("--status", default=None,
                        help="只处理指定状态的公告（new|error），留空则全部")
    parser.add_argument("--retry", type=int, default=2,
                        help="失败重试次数（默认2）")
    parser.add_argument("--since", default=None,
                        help="只处理此日期之后的公告，格式 YYYY-MM-DD")
    parser.add_argument("--raw", action="store_true",
                        help="同时保存原始 HTML/PDF（不只是文本）")
    return parser.parse_args()


async def fetch_one(ann: dict, content_dir: Path,
                    args, page=None,
                    content_cache: dict = None) -> dict:
    """抓取单条公告内容，返回更新后的 ann + meta.

    content_cache: dict[url -> {"ann_id", "result", "processed"}]
    同一 URL 只实际抓取一次，后续复用缓存结果。
    用于：列表页内嵌内容（多公告共享同一URL）"""
    ann_id = make_id(ann.get("title", ""), ann.get("date", ""))
    item_dir = content_dir / ann_id
    item_dir.mkdir(parents=True, exist_ok=True)

    url = ann.get("url", "")
    handler = get_handler(url, ann.get("category", ""))

    if not handler:
        meta = {
            "announcement": ann,
            "handler": "none",
            "success": False,
            "error": "no matching handler",
        }
        (item_dir / "meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        ann["_content_status"] = "error"
        ann["_content_type"] = "none"
        ann["_content_id"] = ann_id
        return ann

    # URL 去重：同一 URL 只实际抓取一次
    if content_cache is not None and url in content_cache:
        cached = content_cache[url]
        if cached.get("processed"):
            print(f"  → [{handler.name}] {ann.get('title','')[:40]} [复用 #{cached['ann_id']}]", flush=True)
            ann["_content_status"] = "ok"
            ann["_content_type"] = cached["result"].content_type
            ann["_content_id"] = cached["ann_id"]
            ann["_shared_url"] = url
            # 为复用项写 meta.json（内容指向原始条目）
            meta = {
                "announcement": ann,
                "handler": handler.name,
                "content_type": cached["result"].content_type,
                "success": True,
                "text_length": len(cached["result"].text),
                "attachments": cached["result"].attachments,
                "fetch_time": datetime.now().isoformat(),
                "reused_from": cached["ann_id"],
                "error": "",
            }
            (item_dir / "meta.json").write_text(
                json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
            return ann

    print(f"  → [{handler.name}] {ann.get('title','')[:40]}", flush=True)

    for attempt in range(1, args.retry + 1):
        try:
            result = await handler.fetch(ann, item_dir, page=page)
            break
        except Exception as e:
            if attempt == args.retry:
                result = processors.ContentResult(False, "error", error=str(e)[:200])

    if result.text:
        (item_dir / "fulltext.txt").write_text(result.text, encoding="utf-8")

    meta = {
        "announcement": ann,
        "handler": handler.name,
        "content_type": result.content_type,
        "success": result.success,
        "text_length": len(result.text),
        "attachments": result.attachments,
        "fetch_time": datetime.now().isoformat(),
        "error": result.error,
    }
    (item_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    if content_cache is not None:
        content_cache[url] = {
            "ann_id": ann_id,
            "result": result,
            "processed": True,
        }

    ann["_content_status"] = "ok" if result.success else "error"
    ann["_content_type"] = result.content_type
    ann["_content_id"] = ann_id
    ann["_shared_url"] = url

    return ann


async def fetch_company(args, company_name: str, company_dir: Path,
                        semaphore: asyncio.Semaphore, stats: dict):
    async with semaphore:
        ann_file = company_dir / "announcements.json"
        if not ann_file.exists():
            return

        announcements = json.loads(ann_file.read_text(encoding="utf-8"))

        # 过滤
        since_date = None
        if args.since:
            since_date = datetime.strptime(args.since, "%Y-%m-%d").date()
        if args.status:
            announcements = [a for a in announcements
                            if a.get("status") == args.status]
        if since_date:
            announcements = [a for a in announcements
                            if datetime.strptime(a["date"], "%Y-%m-%d").date() >= since_date]

        if not announcements:
            print(f"  ⏭ {company_name}: 无需采集的公告", flush=True)
            return

        content_dir = company_dir / "content"
        content_dir.mkdir(parents=True, exist_ok=True)

        print(f"  ▶ {company_name}: {len(announcements)} 条待采集", flush=True)

        # 启动浏览器
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=STEALTH_ARGS,
                executable_path="/home/linwum/.local/bin/google-chrome",
            )
            context = await browser.contexts[0] if browser.contexts else await browser.new_context()
            page = await context.new_page()

            # URL去重缓存：同一URL只实际抓取一次
            content_cache: dict = {}

            for ann in announcements:
                await fetch_one(ann, content_dir, args, page=page,
                               content_cache=content_cache)
                await asyncio.sleep(1.0)

            await browser.close()

        # 写回 announcements.json（含状态更新）
        ann_file.write_text(
            json.dumps(announcements, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        ok = sum(1 for a in announcements if a.get("_content_status") == "ok")
        stats["total"] += len(announcements)
        stats["ok"] += ok
        stats["error"] += len(announcements) - ok
        print(f"  ✅ {company_name}: {ok}/{len(announcements)} 成功", flush=True)


async def fetch_all(args):
    raw_root = ROOT.parent.parent / "cfc_raw_data"

    # 确定日期目录
    if args.date:
        date_dir = raw_root / args.date
    else:
        # 取最新日期目录
        date_dirs = sorted(
            [d for d in raw_root.iterdir() if d.is_dir() and d.name.startswith("20")],
            reverse=True
        )
        date_dir = date_dirs[0] if date_dirs else None

    if not date_dir or not date_dir.exists():
        print(f"错误：未找到数据目录（raw_root={raw_root}）")
        return

    print(f"数据目录: {date_dir}", flush=True)
    print(f"处理器: {[h.name for h in HANDLERS]}", flush=True)

    # 扫描公司
    companies = []
    for company_dir in sorted(date_dir.iterdir()):
        if not company_dir.is_dir():
            continue
        if args.company:
            names = {n.strip() for n in args.company.split(",")}
            if company_dir.name not in names:
                continue
        if (company_dir / "announcements.json").exists():
            companies.append(company_dir)

    print(f"目标公司: {[c.name for c in companies]}", flush=True)

    semaphore = asyncio.Semaphore(args.workers)
    stats = {"total": 0, "ok": 0, "error": 0}

    await asyncio.gather(*[
        fetch_company(args, c.name, c, semaphore, stats)
        for c in companies
    ])

    print(f"\n============================================================", flush=True)
    print(f"内容抓取完成: {stats['ok']}/{stats['total']} 成功 ({stats['error']} 失败)", flush=True)
    print(f"数据目录: {date_dir}", flush=True)


def main():
    args = parse_args()
    asyncio.run(fetch_all(args))


if __name__ == "__main__":
    main()
