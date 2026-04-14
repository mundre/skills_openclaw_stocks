#!/usr/bin/env python3
"""
Phase 1: 消费金融信披列表采集器
解耦设计：从 companies/companies.json 读取配置，输出标准化 JSON
支持增量（--since）、dry-run、并发控制
"""
import argparse
import asyncio
import json
import sys
import time
from datetime import datetime, date
from pathlib import Path

# ── 项目根目录 ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# ── 从 verify_skill.py 复用所有采集方法 ──────────────────────────────────────
from verify_skill import (
    METHODS, COMPANIES, extract_from_text, classify,
    DATE_PAT, normalize_date, BODY_PAT, SKIP_TITLES,
)
import re


# ── CLI 参数 ──────────────────────────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(description="消费金融信披列表采集（Phase 1）")
    parser.add_argument("--date", default=None,
                        help="采集日期（默认今天），格式 YYYY-MM-DD")
    parser.add_argument("--since", default=None,
                        help="只采集此日期之后发布的公告（增量模式），格式 YYYY-MM-DD")
    parser.add_argument("--companies", default=None,
                        help="指定公司名（逗号分隔），留空则采集全部")
    parser.add_argument("--workers", type=int, default=3,
                        help="并发Chrome数（默认3，WSL2建议≤3）")
    parser.add_argument("--dry-run", action="store_true",
                        help="不写文件，只打印预期输出")
    parser.add_argument("--output", default=None,
                        help="输出根目录（默认 cfc_raw_data/）")
    parser.add_argument("--retry", type=int, default=3,
                        help="单家失败重试次数（默认3）")
    parser.add_argument("--delay", type=float, default=2.0,
                        help="采集间隔延迟秒数（默认2.0）")
    return parser.parse_args()


# ── 状态加载（支持增量） ───────────────────────────────────────────────────────
def load_history(company_dir: Path) -> dict:
    """加载该公司历史 announcements.json，返回 {(title[:30])|date: item}"""
    history_file = company_dir / "announcements.json"
    if not history_file.exists():
        return {}
    try:
        items = json.loads(history_file.read_text(encoding="utf-8"))
        return {f"{it['title'][:30]}|{it['date']}": it for it in items}
    except Exception:
        return {}


def filter_since(items: list, since: date) -> tuple[list, list]:
    """按 --since 过滤，返回 (new_items, seen_items)"""
    new_items, seen_items = [], []
    for it in items:
        try:
            item_date = datetime.strptime(it["date"], "%Y-%m-%d").date()
            if item_date >= since:
                it["status"] = "new"
                new_items.append(it)
            else:
                it["status"] = "seen"
                seen_items.append(it)
        except Exception:
            it["status"] = "new"
            new_items.append(it)
    return new_items, seen_items


# ── 单家公司采集（带重试） ────────────────────────────────────────────────────
async def run_company(name: str, url: str, method: str, extra: str,
                      args, semaphore: asyncio.Semaphore) -> dict:
    """采集一家公司，返回结果 dict"""
    async with semaphore:
        for attempt in range(1, args.retry + 1):
            try:
                result = await _collect_one(name, url, method, extra, args)
                result["status"] = "ok"
                return result
            except Exception as e:
                if attempt == args.retry:
                    return {
                        "company": name, "count": 0, "status": "error",
                        "error": str(e)[:200], "attempt": attempt
                    }
                await asyncio.sleep(2 * attempt)
        return {"company": name, "count": 0, "status": "error", "error": "max retries"}


async def _collect_one(name: str, url: str, method: str,
                       extra: str, args) -> dict:
    """实际执行一家公司的列表采集"""
    from playwright.async_api import async_playwright

    STEALTH_ARGS = [
        "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu",
        "--disable-blink-features=AutomationControlled",
        "--disable-web-security", "--enable-webgl",
        "--allow-running-insecure-content", "--headless=new",
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=STEALTH_ARGS,
            executable_path="/home/linwum/.local/bin/google-chrome",
        )
        page = await browser.new_page(viewport={"width": 1280, "height": 800})

        if method in METHODS:
            print(f"  ▶ {name} ({method})", flush=True)
            items = await METHODS[method](page, url)
        else:
            # 通用 html_dom
            print(f"  ▶ {name} (html_dom)", flush=True)
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(3)
            for _ in range(6):
                await page.evaluate("window.scrollBy(0, 600)")
                await asyncio.sleep(0.4)
            text = await page.evaluate("document.body.innerText")
            items = extract_from_text(text, url)

        await browser.close()

    return {"company": name, "url": url, "method": method, "items": items}


# ── 写文件 ───────────────────────────────────────────────────────────────────
def write_company_output(company_dir: Path, items: list,
                          dry_run: bool, collect_date: str):
    """写 announcements.json 和 index.json"""
    if dry_run:
        print(f"  [dry-run] 写 {company_dir.name}/announcements.json ({len(items)}条)")
        return

    company_dir.mkdir(parents=True, exist_ok=True)

    # announcements.json
    announcements_file = company_dir / "announcements.json"
    announcements_file.write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    # index.json
    categories = {}
    for it in items:
        cat = it.get("category", "其他")
        categories[cat] = categories.get(cat, 0) + 1

    index = {
        "company": items[0].get("company", company_dir.name) if items else company_dir.name,
        "collect_date": collect_date,
        "total": len(items),
        "categories": categories,
        "status": "ok",
    }
    index_file = company_dir / "index.json"
    index_file.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"  ✅ {company_dir.name}: {len(items)}条", flush=True)


# ── 主采集循环 ───────────────────────────────────────────────────────────────
async def collect_all(args):
    collect_date = args.date or datetime.now().strftime("%Y-%m-%d")
    output_root = Path(args.output) if args.output else ROOT.parent.parent / "cfc_raw_data"
    output_dir = output_root / collect_date
    since_date = datetime.strptime(args.since, "%Y-%m-%d").date() if args.since else None

    print(f"============================================================", flush=True)
    print(f"消费金融信披采集 | {collect_date} | 重试:{args.retry}次 | 延迟:{args.delay}秒", flush=True)
    print(f"输出: {output_dir}", flush=True)
    if since_date:
        print(f"增量模式: 只采集 {since_date} 之后的公告", flush=True)
    print(f"============================================================", flush=True)

    # 加载公司配置
    companies_file = ROOT / "companies" / "companies.json"
    if companies_file.exists():
        cfg = json.loads(companies_file.read_text(encoding="utf-8"))
        company_list = cfg["companies"]
    else:
        # 降级：从 verify_skill.py 的 COMPANIES 读取
        company_list = [{"name": c[0], "url": c[1], "method": c[2], "extra": c[3]}
                        for c in COMPANIES]

    # 过滤指定公司
    if args.companies:
        names = {n.strip() for n in args.companies.split(",")}
        company_list = [c for c in company_list if c["name"] in names]
        print(f"已筛选 {len(company_list)} 家公司", flush=True)

    # 并发控制
    semaphore = asyncio.Semaphore(args.workers)

    results = []
    for c in company_list:
        name, url, method, extra = c["name"], c["url"], c["method"], c.get("extra", "")
        company_dir = output_dir / name

        # 增量：合并历史
        history = load_history(company_dir)
        since_filter_active = since_date and history

        r = await run_company(name, url, method, extra, args, semaphore)
        r["company_dir"] = company_dir
        results.append(r)

        if since_filter_active and r.get("items"):
            new_items, seen_items = filter_since(r["items"], since_date)
            # 合并：历史 + 新（去重）
            seen_keys = {f"{it['title'][:30]}|{it['date']}" for it in seen_items}
            merged = seen_items + [it for it in new_items if
                                   f"{it['title'][:30]}|{it['date']}" not in seen_keys]
            r["items"] = merged
            print(f"  增量: 新增{len(new_items)}条 / 历史{len(seen_items)}条 / 合并后{len(merged)}条", flush=True)
        else:
            for it in r.get("items", []):
                it["status"] = it.get("status", "new")
            seen_items = []

        write_company_output(company_dir, r.get("items", []),
                             args.dry_run, collect_date)

        await asyncio.sleep(args.delay)

    # 汇总
    total = sum(len(r.get("items", [])) for r in results)
    errors = [r["company"] for r in results if r.get("status") == "error"]
    ok_count = sum(1 for r in results if r.get("status") == "ok")

    print(f"\n============================================================", flush=True)
    print(f"总计: {total} 条 / {ok_count}/{len(results)}家 （重试: {len(errors)}次）", flush=True)
    if errors:
        print(f"失败: {errors}", flush=True)
    print(f"输出目录: {output_dir}", flush=True)

    if not args.dry_run:
        # 保存全局索引
        summary = {
            "collect_date": collect_date,
            "total": total,
            "ok": ok_count,
            "errors": errors,
            "companies": [{
                "name": r["company"],
                "count": len(r.get("items", [])),
                "method": r.get("method", ""),
                "status": r.get("status", ""),
            } for r in results]
        }
        (output_dir / "_summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    args = parse_args()
    asyncio.run(collect_all(args))


if __name__ == "__main__":
    main()
