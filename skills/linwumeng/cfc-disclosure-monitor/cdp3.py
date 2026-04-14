#!/usr/bin/env python3
"""
专项采集：3家WSL2受限的消金公司
- 中银消费金融  boccfc.cn  (layui翻页)
- 长银五八消费金融  hncy58.com  (telling.html)
- 苏银凯基消费金融  sykcfc.cn  (Vue Tab + Cloudflare WAF)

用 playwright 自己的 Chromium（绕过系统Chrome崩溃问题）
"""
import asyncio, json, re, os, sys
from pathlib import Path
from playwright.async_api import async_playwright

TODAY = str(__import__("datetime").date.today())
OUT_BASE = Path(f"~/.openclaw/workspace/cfc_raw_data/{TODAY}").expanduser()
OUT_BASE.mkdir(parents=True, exist_ok=True)

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

SKIP_TITLES = {
    "首页","关于我们","联系我们","版权","Copyright","Registered","客服","办公地址",
    "关注我们","下载APP","加入我们","网站地图","企业名称","点击查看","更多",
    "网站标识码","ICP证","可信网站","网络文化经营许可证","95137",
}
DATE_PAT = re.compile(
    r"^\d{4}[\s\-/.年][\s\-/月]*\d{0,2}[\s\-/日]*\d{0,2}|"
    r"^\d{4}[/.]\d{1,2}[/.]\d{1,2}|"
    r"^\d{1,2}/\d{1,2}|"
    r"^(?:20)?(19|20)\d{2}$|"
    r"^\d{1,2}[-\. ]\d{1,2}[-\. ]\d{4}$|"
    r"^\d{1,2}[-\.]\d{1,2}[-\.]\d{2}$|"
    r"^\d{1,2}[-\.]\d{1,2}[-\.]\d{2}$|"
    r"^\d{4}\.\d{1,2}$|"
    r"^\d{4}/\d{1,2}|"
    r"时间[：:]\s*\d{4}[\s\-/.年][\s\-/月]?\d{0,2}[\s\-/日]?\d{0,2}|"
    r"日期[：:]\s*\d{4}[\s\-/.年][\s\-/月]?\d{0,2}[\s\-/日]?\d{0,2}"
)

def normalize_date(s):
    s = re.sub(r"\s+\d{2}:\d{2}(:\d{2})?$", "", s)
    s = re.sub(r'\s+', '', s)
    s = s.replace("\xa0", "").replace(" ","")
    s = s.replace("年","-").replace("月","-").replace("日"," ")
    m = re.match(r"^(\d{1,2})/(\d{1,2})$", s)
    if m:
        return f"PARTIAL:{int(m.group(1)):02d}/{int(m.group(2)):02d}"
    s = s.replace("/","-")
    s = re.sub(r"^时间[：:]\s*","",s)
    s = re.sub(r"^发布时间[：:]\s*","",s)
    s = re.sub(r'\s+(?:浏览量|访问量|点击量|pv)[：:]*[\d]*.*$', '', s)
    m = re.search(r'(?:^|[^\d])(\d{4}-\d{2}-\d{2})(?!\d|-)', s)
    if m:
        parts = m.group(1).split('-')
        return f"{int(parts[0]):04d}-{int(parts[1]):02d}-{int(parts[2]):02d}"
    m = re.search(r'(?:^|[^\d])(\d{4}-\d{2})(?!\d|-)', s)
    if m:
        parts = m.group(1).split('-')
        return f"{int(parts[0]):04d}-{int(parts[1]):02d}"
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2}) (\d{2}):(\d{2})", s)
    if m:
        return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    t = s.replace("（","").replace("(","").replace("）","").replace(")","")
    t = re.sub(r'[^\d-]', '', t).rstrip('-')
    m = re.match(r"^(\d{4})-(\d{1,2})$", t)
    if m:
        return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}"
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", s)
    if m:
        return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m = re.match(r"^(\d{4})-(\d{1,2})$", s)
    if m:
        return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}"
    m = re.match(r"^(\d{4})[/\.](\d{1,2})[/\.](\d{1,2})$", s)
    if m:
        return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m = re.match(r"^(\d{4})/(\d{1,2})$", s)
    if m:
        return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}"
    m = re.match(r"^(20\d{2})$", s)
    if m:
        return f"PARTIAL:{m.group(1)}"
    m = re.match(r"^(\d{1,2})[-\. ](\d{1,2})[-\. ](\d{4})$", s)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if d > 12 and mo <= 12:
            return f"{y:04d}-{mo:02d}-{d:02d}"
        elif mo > 12 and d <= 12:
            return f"{y:04d}-{d:02d}-{mo:02d}"
        else:
            return f"{y:04d}-{mo:02d}-{d:02d}"
    s = re.sub(r"\s+\d{2}:\d{2}(:\d{2})?$", "", s)
    m = re.match(r"^(\d{1,2})-(\d{1,2})-(\d{2})$", s)
    if m:
        g1, g2, yy = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if g1 > 12:
            return f"{2000+g1:04d}-{g2:02d}-{yy:02d}"
        elif g2 > 12:
            return f"{2000+g2:04d}-{g1:02d}-{yy:02d}"
        else:
            return f"{2000+yy:04d}-{g1:02d}-{g2:02d}"
    m = re.match(r"^(\d{1,2})-(\d{1,2})$", s)
    if m:
        return f"PARTIAL:{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    m = re.match(r"^(\d{4})\.(\d{1,2})$", s)
    if m:
        return f"PARTIAL:{m.group(1)}.{m.group(2)}"
    return ""


def classify(t):
    t = t or ""
    if any(x in t for x in ["关联交易","关联授信","关联方","统一交易协议"]): return "关联交易"
    if any(x in t for x in ["三支柱","资本信息","资本充足","风险加权"]): return "资本信息"
    if any(x in t for x in ["合作催收","合作机构","委外催收","增信服务"]): return "合作机构"
    if any(x in t for x in ["社会责任","社责报告"]): return "社会责任"
    if any(x in t for x in ["年度信息","年度披露","年报"]): return "年度信披"
    if any(x in t for x in ["服务内容","价格公示","价目"]): return "服务价格"
    if any(x in t for x in ["债权转让","不良贷款","个人不良"]): return "债权转让"
    return "重要公告"


def extract_from_text(text, url, max_dist=8):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    results, seen = [], set()
    date_map = {}

    for i, line in enumerate(lines):
        if DATE_PAT.match(line):
            ds = normalize_date(line)
            if ds and ds.startswith("PARTIAL:"):
                date_map[i] = ds
            elif ds:
                date_map[i] = ds
        else:
            mmdd_m = re.match(r"^(\d{1,2})-(\d{1,2})$", line)
            if mmdd_m:
                date_map[i] = f"PARTIAL:{int(mmdd_m.group(1)):02d}-{int(mmdd_m.group(2)):02d}"

    final_dates = {}
    for i, ds in list(date_map.items()):
        if ds.startswith("PARTIAL:"):
            mmdd = ds[8:].replace("/", "-")
            for j in range(i+1, min(i+4, len(lines))):
                year_m = re.match(r"^(19|20)(\d{2})$", lines[j])
                if year_m:
                    year = int(year_m.group(1)+year_m.group(2))
                    mm = int(mmdd[:2]); dd = int(mmdd[3:])
                    final_dates[i] = f"{year}-{mm:02d}-{dd:02d}"
                    break
            mmdd_m = re.match(r"^(\d{1,2})-(\d{1,2})$", mmdd)
            if mmdd_m:
                g1, g2 = int(mmdd_m.group(1)), int(mmdd_m.group(2))
                for j in range(i+1, min(i+4, len(lines))):
                    year_m = re.match(r"^(19|20)(\d{2})$", lines[j])
                    if year_m:
                        year = int(year_m.group(1) + year_m.group(2))
                        final_dates[i] = f"{year}-{g1:02d}-{g2:02d}"
                        break
        elif ds.startswith("PARTIAL_Y:"):
            ym = ds[10:]
            day_line = lines[i-1] if i > 0 else ""
            day_m = re.match(r"^(\d{1,2})$", day_line)
            if day_m:
                parts = ym.split(".")
                if len(parts) == 2:
                    final_dates[i] = f"{parts[0]}-{parts[1]}-{int(day_m.group(1)):02d}"
            else:
                final_dates[i] = ds
        else:
            final_dates[i] = ds

    BODY_PAT = re.compile(r"^(根据|为了|按照|近来|任何|如您|本|特此|本公司|兹有)")
    for i, line in enumerate(lines):
        if len(line) < 4: continue
        if any(x in line for x in ["95137","layui-laypage","layui-box","layui-laypage-default"]): continue
        if line in SKIP_TITLES: continue
        if re.match(r"^[\d\-\/\.\:\s]+$", line) and not DATE_PAT.match(line): continue
        if re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", line): continue
        if BODY_PAT.match(line): continue
        if re.match(r"^[\u4e00-\u9fa5]{0,3}(首页|关于我们|联系我们|版权|客服)", line): continue
        if re.match(r"^时间[：:]", line):
            norm = normalize_date(line)
            if not norm: pass
            else: continue
        elif DATE_PAT.match(line): continue
        if "<" in line or ">" in line: continue
        if re.match(r"^\d{1,2}月\d{1,2}(日[上下晚]午|日)[^日}\n]{0,20}[，,]", line): continue
        if re.match(r"^[上下晚]午\d", line): continue
        if len(line) > 50 and line.startswith(("中原消费金融",)) and line.count("，") >= 2: continue
        if 5 < len(line) < 500 and not DATE_PAT.match(line):
            best_date, best_dist = None, 999
            for dj in sorted(final_dates.keys()):
                d = abs(dj - i)
                if d < best_dist or (d == best_dist and dj > i):
                    best_dist, best_date = d, final_dates[dj]
            if best_date and best_dist <= max_dist:
                key = f"{line[:30]}|{best_date}"
                if key not in seen:
                    seen.add(key)
                    results.append({
                        "title": line[:200], "date": best_date,
                        "url": url, "category": classify(line)
                    })
    return results


# ─── 中銀消費金融：layui 分页 ───
async def fetch_zhongyin(page, url):
    """中银消费金融：layui JS分页，13页，.main_content_body_item"""
    all_items, seen = [], set()
    base = "https://www.boccfc.cn"
    page_num = 0
    for pg in range(1, 20):
        page_num += 1
        try:
            if pg == 1:
                await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                await asyncio.sleep(3)
            else:
                # 点击页码按钮
                clicked = False
                for sel in [f'a[data-page="{pg}"]', f'.layui-laypage a[data-page="{pg}"]']:
                    try:
                        btn = page.locator(sel).first
                        if await btn.count() > 0:
                            await btn.click(timeout=3000)
                            clicked = True
                            break
                    except: pass
                if not clicked:
                    # 尝试找"下一页"按钮
                    try:
                        next_btn = page.locator('.layui-laypage a.layui-laypage-prev + a').first
                        if await next_btn.count() > 0:
                            await next_btn.click(timeout=3000)
                            clicked = True
                    except: pass
                if not clicked:
                    print(f"    中银第{pg}页找不到按钮，停止", flush=True)
                    break
            await asyncio.sleep(2)

            # 提取当前页
            items = await page.query_selector_all(".main_content_body_item")
            new_count = 0
            for item in items:
                try:
                    href = await item.get_attribute("href") or ""
                    # 尝试多种选择器找日期
                    spans = await item.query_selector_all("span")
                    date_str = ""
                    for sp in spans:
                        t = await sp.inner_text()
                        if re.search(r"\d{4}[-/]\d{2}[-/]\d{2}", t):
                            m = re.search(r"(\d{4}[-/]\d{2}[-/]\d{2})", t)
                            date_str = m.group(1).replace("/","-")
                            break
                    # 获取标题
                    title_els = await item.query_selector_all("a")
                    title = ""
                    for a in title_els:
                        t = await a.inner_text()
                        if t and len(t) > 3:
                            title = t.strip()
                            break
                    if not title:
                        title = "公告"
                    detail_url = base + href if href else url
                    key = f"{detail_url[:40]}|{date_str}"
                    if key not in seen:
                        seen.add(key)
                        all_items.append({
                            "title": title[:200],
                            "date": date_str,
                            "url": detail_url,
                            "category": classify(title)
                        })
                        new_count += 1
                except Exception as e:
                    continue
            print(f"  中银第{pg}页:+{new_count}条 累计{len(all_items)}条", flush=True)
            if new_count == 0:
                # 最后一页了
                break
        except Exception as e:
            print(f"  中银第{pg}页异常: {e}", flush=True)
            break
    return all_items


# ─── 長銀五八消費金融 ───
async def fetch_changyin58(page, url):
    """长银五八消费金融：telling.html"""
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        await asyncio.sleep(4)
        for _ in range(10):
            await page.evaluate("window.scrollBy(0, 500)")
            await asyncio.sleep(0.5)
        text = await page.evaluate("document.body.innerText")
        items = extract_from_text(text, page.url)
        print(f"  长银五八: {len(items)}条", flush=True)
        return items
    except Exception as e:
        return [{"title": f"ERROR: {e}", "date": "", "url": url, "category": "错误"}]


# ─── 苏銀凱基消費金融：Vue Tab ───
async def fetch_suyinkaiji(page, url):
    """苏银凯基消费金融：Vue Tab切换，Cloudflare WAF bypass"""
    def norm_date(year_str, day_str):
        m = re.match(r"(\d{4})\s*[-–]\s*(\d{1,2})", year_str.strip())
        if m:
            return f"{m.group(1)}-{int(m.group(2)):02d}-{int(day_str.strip()):02d}"
        return ""

    async def extract_page(seen):
        items = []
        try:
            news_items = await page.query_selector_all(".sykj-news_item")
            for item in news_items:
                try:
                    day_el = await item.query_selector(".day")
                    year_el = await item.query_selector(".year")
                    title_el = await item.query_selector(".title")
                    day = await day_el.inner_text() if day_el else ""
                    year = await year_el.inner_text() if year_el else ""
                    title = await title_el.inner_text() if title_el else ""
                    if title and year:
                        ds = norm_date(year, day)
                        key = f"{title[:30]}|{ds}"
                        if key not in seen:
                            seen.add(key)
                            items.append({"title": title.strip()[:200], "date": ds,
                                         "url": page.url, "category": classify(title)})
                except:
                    continue
        except:
            pass
        return items

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        await asyncio.sleep(4)
        # 切换到第二个Tab（公告）
        try:
            tabs = await page.query_selector_all(".sykj-scroolnavs_wrap a")
            if len(tabs) > 1:
                await tabs[1].click(timeout=3000)
                await asyncio.sleep(3)
        except Exception as e:
            print(f"  苏银凯基Tab切换: {e}", flush=True)

        seen, all_items = set(), []
        all_items.extend(await extract_page(seen))
        print(f"  苏银凯基第1页: {len(all_items)}条", flush=True)

        # 翻页最多20页
        for p in range(2, 21):
            next_clicked = False
            for sel in ["button:has-text('下一页')", "span:has-text('下一页')",
                        "div:has-text('下一页')", "a:has-text('下一页')",
                        "[class*='next']", "[class*='page']"]:
                try:
                    el = page.locator(sel).first
                    if await el.count() > 0 and "disabled" not in (await el.get_attribute("class") or ""):
                        await el.click(timeout=2000)
                        next_clicked = True
                        break
                except:
                    pass
            if not next_clicked:
                print(f"  苏银凯基第{p}页找不到下一页，停止", flush=True)
                break
            await asyncio.sleep(3)
            new_items = await extract_page(seen)
            if not new_items:
                print(f"  苏银凯基第{p}页无新数据，停止", flush=True)
                break
            all_items.extend(new_items)
            print(f"  苏银凯基第{p}页:+{len(new_items)}条 累计{len(all_items)}条", flush=True)
        return all_items
    except Exception as e:
        return [{"title": f"ERROR: {e}", "date": "", "url": url, "category": "错误"}]


async def main():
    companies = [
        ("中银消费金融",     "https://www.boccfc.cn/xinwen/gonggao/",              fetch_zhongyin),
        ("长银五八消费金融", "https://www.hncy58.com/telling.html",                fetch_changyin58),
        ("苏银凯基消费金融", "https://www.sykcfc.cn/#/layout/information",         fetch_suyinkaiji),
    ]

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=STEALTH_ARGS
        )
        print("✅ Chromium launched", flush=True)

        ctx = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        page = await ctx.new_page()

        for name, url, fn in companies:
            print(f"\n▶ {name}", flush=True)
            items = await fn(page, url)
            errors = [i for i in items if i.get("title","").startswith("ERROR")]
            valid = [i for i in items if not i.get("title","").startswith("ERROR") and i.get("date","")]
            cnt = len(valid)

            company_dir = OUT_BASE / name
            company_dir.mkdir(parents=True, exist_ok=True)
            with open(company_dir / "announcements.json", "w", encoding="utf-8") as f:
                json.dump(valid, f, ensure_ascii=False, indent=2)
            with open(company_dir / "index.json", "w", encoding="utf-8") as f:
                json.dump({
                    "company": name, "url": url, "method": fn.__name__,
                    "status": "success" if cnt > 0 else "empty",
                    "count": cnt, "errors": [i["title"] for i in errors]
                }, f, ensure_ascii=False, indent=2)

            status = "✅" if cnt > 0 else "❌"
            print(f"  {status} {name}: {cnt}条", flush=True)
            if errors:
                for e in errors[:3]:
                    print(f"     ERROR: {e['title'][:80]}", flush=True)

            await asyncio.sleep(2)

        await browser.close()

    print(f"\n输出: {OUT_BASE}")

if __name__ == "__main__":
    asyncio.run(main())
