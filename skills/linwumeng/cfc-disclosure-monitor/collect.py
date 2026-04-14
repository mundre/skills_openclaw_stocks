#!/usr/bin/env python3
"""
消金信披采集 — 统一入口
═══════════════════════════════════════════════════════════════════
Phase 1: 列表采集（announcements.json）
Phase 2: 内容抓取（content/）

执行:
    python3 collect.py                  # 全量采集（3次重试，延迟2秒）
    python3 collect.py --resume        # 增量采集（保留旧数据）
    python3 collect.py --retry 1 --delay 0   # 快速测试
    python3 collect.py --company "中银消费金融,蚂蚁消费金融"   # 指定公司
    python3 collect.py --date 2026-04-11    # 指定日期目录
    python3 collect.py --check              # 检查浏览器状态
"""
import argparse
import asyncio
import json
import shutil
import sys
from datetime import date
from pathlib import Path

# ── 路径设置 ─────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
OUT_BASE = ROOT.parent.parent / "cfc_raw_data"
TODAY = str(date.today())

# ── 核心模块 ─────────────────────────────────────────────────────────────────
sys.path.insert(0, str(ROOT))
from core import extract_from_text, classify
from collectors import COLLECTORS

# Playwright 浏览器参数（已验证可用：WSL2 + playwright内置Chromium）
STEALTH_ARGS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-blink-features=AutomationControlled",
    "--disable-web-security",
    "--enable-webgl",
    "--ignore-certificate-errors",
    "--allow-running-insecure-content",
    "--headless=new",
]

# ── 公司配置加载 ─────────────────────────────────────────────────────────────
def load_companies() -> list[dict]:
    """从 companies.json 加载配置（唯一真相源）"""
    cfg_file = ROOT / "companies.json"
    if cfg_file.exists():
        cfg = json.loads(cfg_file.read_text(encoding="utf-8"))
        return cfg["companies"]
    # 降级：从不存在的 companies/companies.json（旧路径）读
    old_cfg = ROOT / "companies" / "companies.json"
    if old_cfg.exists():
        cfg = json.loads(old_cfg.read_text(encoding="utf-8"))
        return cfg["companies"]
    print(f"❌ 未找到配置文件: {cfg_file}", file=sys.stderr)
    sys.exit(1)


# ── 浏览器管理 ───────────────────────────────────────────────────────────────
class Browser:
    """
    统一浏览器生命周期。
    设计说明：
    - 使用 playwright 内置 Chromium（系统 Chrome 在 WSL2 会 crash）
    - 每个公司独立 ctx/page，用完即关（避免状态污染）
    - 支持 CDP 复用来复用登录态（预留，未激活）
    """

    def __init__(self):
        self._pw = None
        self._browser = None

    async def launch(self):
        if self._browser:
            return self._browser
        from playwright.async_api import async_playwright
        self._pw = await async_playwright().start()
        self._browser = await self._pw.chromium.launch(
            headless=True,
            args=STEALTH_ARGS,
        )
        return self._browser

    async def new_page(self, ua: str = None) -> "page":
        browser = await self.launch()
        ctx = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            no_viewport=True,
            user_agent=ua or (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        return await ctx.new_page()

    async def close(self):
        if self._browser:
            await self._browser.close()
            self._browser = None
        if self._pw:
            await self._pw.stop()
            self._pw = None


# ── 单家公司采集 ─────────────────────────────────────────────────────────────
async def run_company(
    name: str,
    url: str,
    method: str,
    out_dir: Path,
    retry: int = 3,
    since_date: str = None,
) -> dict:
    """
    返回 dict: {"company", "url", "method", "count", "status", "errors", "retry", "since_date", "new_count"}
    """
    import datetime
    browser = Browser()
    result = {
        "company": name,
        "url": url,
        "method": method,
        "count": 0,
        "status": "error",
        "errors": [],
        "retry": 0,
        "since_date": since_date,
        "new_count": 0,
    }
    valid = []   # 初始化，避免 except 分支后未定义

    # ── 增量合并：加载已有数据 ───────────────────────────────
    company_dir = out_dir / name
    existing = []
    if company_dir.exists():
        existing_file = company_dir / "announcements.json"
        if existing_file.exists():
            try:
                existing = json.loads(existing_file.read_text(encoding="utf-8"))
            except Exception:
                existing = []
    existing_keys = {f"{it['title'][:30]}|{it['date']}" for it in existing}

    for attempt in range(1, retry + 1):
        result["retry"] = attempt
        try:
            page = await browser.new_page()
            collector = COLLECTORS.get(method)

            print(f"\n▶ {name} ({method})", flush=True)

            if collector:
                items = await collector(page, url)
            else:
                # 兜底：html_dom
                print(f"  ⚠️ 方法 {method} 未找到，使用 html_dom 兜底", flush=True)
                items = await COLLECTORS["html_dom"](page, url)

            await page.close()

            errors = [i for i in items if i.get("title", "").startswith("ERROR:")]
            fetched = [i for i in items if not i.get("title", "").startswith("ERROR:") and i.get("date")]

            # ── 增量过滤 ────────────────────────────────────
            if since_date:
                try:
                    since_dt = datetime.datetime.strptime(since_date, "%Y-%m-%d").date()
                    new_fetched = []
                    for it in fetched:
                        try:
                            item_dt = datetime.datetime.strptime(it["date"][:10], "%Y-%m-%d").date()
                            if item_dt >= since_dt:
                                new_fetched.append(it)
                        except Exception:
                            new_fetched.append(it)   # 无法解析日期，保守保留
                    since_note = f"（{since_date}后过滤）"
                    fetched = new_fetched
                except Exception:
                    since_note = f"（{since_date} 日期解析失败，未过滤）"
            else:
                since_note = ""

            if since_note:
                print(f"  {since_note}", flush=True)

            # ── 与历史合并（去重）──────────────────────────────
            merged = list(existing)
            new_count = 0
            for it in fetched:
                key = f"{it['title'][:30]}|{it['date']}"
                if key not in existing_keys:
                    merged.append(it)
                    existing_keys.add(key)
                    new_count += 1

            valid = merged
            result["new_count"] = new_count

            print(f"  本次新增: {new_count}条 / 历史: {len(existing)}条 / 合并后: {len(valid)}条", flush=True)

            result["count"] = len(valid)
            result["errors"] = [e["title"] for e in errors]
            result["status"] = "ok" if valid or not errors else "empty"

            if result["count"] > 0 or not errors:
                break   # 有数据或无错误，停止重试

            wait = 2 ** (attempt - 1)
            print(f"  ⚠️ {name} 0条 + {len(errors)}个错误，第{attempt}次重试（等待{wait}s）...", flush=True)
            await asyncio.sleep(wait)

        except Exception as e:
            err_str = str(e)[:200]
            print(f"  ❌ {name} 异常 (attempt {attempt}): {err_str}", flush=True)
            result["errors"].append(f"ERROR: {err_str}")
            if attempt < retry:
                await asyncio.sleep(2 ** (attempt - 1))
        finally:
            try:
                await browser.close()
            except Exception:
                pass

    # ── 写文件 ────────────────────────────────────────────
    out_dir.mkdir(parents=True, exist_ok=True)
    company_dir.mkdir(parents=True, exist_ok=True)
    with open(company_dir / "announcements.json", "w", encoding="utf-8") as f:
        json.dump(valid, f, ensure_ascii=False, indent=2)

    categories = {}
    for it in valid:
        cat = it.get("category", "其他")
        categories[cat] = categories.get(cat, 0) + 1

    with open(company_dir / "index.json", "w", encoding="utf-8") as f:
        json.dump({
            "company": name,
            "url": url,
            "method": method,
            "collect_date": TODAY,
            "status": result["status"],
            "count": result["count"],
            "retry": result["retry"],
            "categories": categories,
            "errors": result["errors"][:5],
        }, f, ensure_ascii=False, indent=2)

    return result


async def _load_existing(company_dir: Path) -> list:
    f = company_dir / "announcements.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    return []


# ── CLI ──────────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(description="消费金融官网信披采集")
    p.add_argument("--resume", action="store_true", help="增量模式（保留历史数据目录）")
    p.add_argument("--retry", type=int, default=3, help="单家公司最大重试次数（默认3）")
    p.add_argument("--delay", type=float, default=2.0, help="公司间延迟秒数（默认2）")
    p.add_argument("--company", default=None, help="指定公司（逗号分隔）")
    p.add_argument("--date", default=None, help="采集日期（默认今天）")
    p.add_argument("--check", action="store_true", help="检查浏览器状态")
    p.add_argument("--since", default=None,
                   help="增量起始日期（YYYY-MM-DD），默认从上次采集日期自动推断")
    p.add_argument("--incremental", action="store_true",
                   help="增量模式：自动读取上次采集日期，只抓新公告（隐含 --resume）")
    return p.parse_args()


async def cmd_check():
    from playwright.async_api import async_playwright
    print("检查 Playwright Chromium...")
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True, args=STEALTH_ARGS)
            print("✅ Chromium 可用")
            await browser.close()
        except Exception as e:
            print(f"❌ Chromium 启动失败: {e}")


async def cmd_collect(args):
    collect_date = args.date or TODAY
    out_dir = Path(OUT_BASE) / collect_date

    # ── 确定 since_date（增量起始日期）─────────────────────────────
    since_date = None
    if args.incremental or args.since:
        if args.since:
            since_date = args.since
            since_label = f"指定日期 {since_date} 起"
        else:
            # 自动从最新日期目录读取 last_run_date
            date_dirs = sorted(
                [d for d in OUT_BASE.iterdir() if d.is_dir() and d.name.startswith("20")],
                reverse=True,
            )
            latest_dir = date_dirs[0] if date_dirs else None
            if latest_dir and (latest_dir / "_summary.json").exists():
                try:
                    prev = json.loads((latest_dir / "_summary.json").read_text())
                    since_date = prev.get("last_run_date") or latest_dir.name
                    since_label = f"上次采集 {since_date} 起（自动推断）"
                except Exception:
                    since_date = latest_dir.name
                    since_label = f"最新目录 {since_date} 起（自动推断）"
            else:
                since_date = None
                since_label = "无法推断，执行全量"
    
    # --resume 但没有 --since：合并历史数据，但不按日期过滤
    resume_mode = args.resume or args.incremental
    if not args.resume:
        shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    companies = load_companies()

    # 过滤指定公司
    if args.company:
        names = {n.strip() for n in args.company.split(",")}
        companies = [c for c in companies if c["name"] in names]
        print(f"已筛选 {len(companies)} 家公司: {names}", flush=True)

    print(f"""
╔══════════════════════════════════════════════════════╗
║  消金信披采集  {collect_date}                         ║
║  公司: {len(companies)}家  重试:{args.retry}次  延迟:{args.delay}秒            ║
║  输出: {out_dir}                        ║""", flush=True)
    if since_date:
        print(f"║  增量: {since_label}                        ║")
    print(f"╚══════════════════════════════════════════════════════╝", flush=True)

    results = []
    for c in companies:
        r = await run_company(
            name=c["name"],
            url=c["url"],
            method=c["method"],
            out_dir=out_dir,
            retry=args.retry,
            since_date=since_date,
        )
        results.append(r)

        status_icon = "✅" if r["count"] > 0 else ("⚠️" if r["retry"] > 1 else "❌")
        retry_note = f" (重试{r['retry']}次)" if r["retry"] > 1 else ""
        new_note = f" 新增+{r['new_count']}" if r.get("new_count", 0) > 0 else ""
        print(f"  {status_icon} {r['company']}: {r['count']}条{new_note}{retry_note}", flush=True)

        # 公司间延迟（最后一公司不等待）
        if args.delay > 0 and c != companies[-1]:
            await asyncio.sleep(args.delay)

    # 汇总
    total = sum(r["count"] for r in results)
    ok = sum(1 for r in results if r["status"] == "ok")
    errors_total = sum(len(r["errors"]) for r in results)

    new_total = sum(r.get("new_count", 0) for r in results)
    since_info = f"\n║  增量: 本次新增 {new_total} 条（起始 {since_date}）" if since_date else ""
    print(f"""
╠══════════════════════════════════════════════════════╣
║  总计: {total} 条 / {ok}/{len(results)}家                          ║{since_info}
╠══════════════════════════════════════════════════════╣""", flush=True)

    for r in sorted(results, key=lambda x: -x["count"])[:10]:
        bar = "█" * min(r["count"], 50)
        new_tag = f" +{r.get('new_count',0)}" if r.get('new_count', 0) > 0 else ""
        print(f"  {r['count']:4d}{new_tag}  {r['company']:<16} {r['method']:<20} {bar}")

    # 写全局摘要
    summary = {
        "collect_date": collect_date,
        "last_run_date": TODAY,       # 下次 --incremental 用此日期
        "since_date": since_date,     # 本次采集的增量起始日期
        "incremental": bool(since_date),
        "total": total,
        "ok": ok,
        "total_companies": len(results),
        "new_total": sum(r.get("new_count", 0) for r in results),
        "companies": [{
            "name": r["company"],
            "count": r["count"],
            "new_count": r.get("new_count", 0),
            "method": r["method"],
            "status": r["status"],
            "retry": r["retry"],
        } for r in results],
    }
    (out_dir / "_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\n输出目录: {out_dir}", flush=True)


def main():
    args = parse_args()
    if args.check:
        asyncio.run(cmd_check())
    else:
        asyncio.run(cmd_collect(args))


if __name__ == "__main__":
    main()
