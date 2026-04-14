# collectors.py — 消金信披 Phase-1 采集方法（按架构模式分组）
"""
注册机制：
  所有函数以 collect_<name> 命名，自动注册到 COLLECTORS 字典。
  方法派发：run_company() 根据 companies.json 中的 method 字段查表。

架构分组：
  GROUP_A  — 静态 HTML，滚动即可（无翻页）
  GROUP_B  — 翻页型，通用下一页按钮
  GROUP_C  — 首页滚动（JS动态加载）
  GROUP_D  — 详情页 URL 可枚举（从列表页提取 ID 构造）
  GROUP_E  — Vue / Element UI / 各类 JS 框架
  GROUP_F  — 多 Tab / 多栏
  GROUP_G  — 特殊格式（日期分两行、PDF附件等）
  GROUP_H  — WSL2 受限（需特殊处理）
"""
import asyncio
import re
from pathlib import Path
from typing import Callable

from core import extract_from_text, classify, normalize_date

# ─── 注册表 ──────────────────────────────────────────────────────────────────
COLLECTORS: dict[str, Callable] = {}

def collector(name: str) -> Callable:
    """装饰器：注册采集方法"""
    def decor(fn: Callable) -> Callable:
        COLLECTORS[name] = fn
        for alias in name.split("|"):
            COLLECTORS[alias.strip()] = fn
        return fn
    return decor


# ════════════════════════════════════════════════════════════════════════════════
# GROUP_A — 静态 HTML（滚动提取，无翻页）
# ════════════════════════════════════════════════════════════════════════════════

@collector("html_dom")
async def collect_html_dom(page, url: str) -> list:
    """静态HTML直接提取，滚动加载"""
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(3)
    for _ in range(6):
        await page.evaluate("window.scrollBy(0, 600)")
        await asyncio.sleep(0.4)
    text = await page.evaluate("document.body.innerText")
    return extract_from_text(text, url)


@collector("cdp_rpa")
async def collect_cdp_rpa(page, url: str) -> list:
    """大量滚动（15次）用于慢加载页面"""
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(3)
    for _ in range(15):
        await page.evaluate("window.scrollBy(0, 400)")
        await asyncio.sleep(0.5)
    text = await page.evaluate("document.body.innerText")
    return extract_from_text(text, url)


# ════════════════════════════════════════════════════════════════════════════════
# GROUP_B — 翻页型
# ════════════════════════════════════════════════════════════════════════════════

@collector("paginated")
async def collect_paginated(page, url: str) -> list:
    """通用翻页：找下一页按钮循环"""
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(3)
    all_items, seen = [], set()
    page_num = 0
    while True:
        page_num += 1
        for _ in range(6):
            await page.evaluate("window.scrollBy(0, 600)")
            await asyncio.sleep(0.3)
        text = await page.evaluate("document.body.innerText")
        items = extract_from_text(text, page.url)
        new_count = 0
        for item in items:
            key = f"{item['title'][:30]}|{item['date']}"
            if key not in seen:
                seen.add(key)
                all_items.append(item)
                new_count += 1
        print(f"  第{page_num}页:+{new_count}条 累计{len(all_items)}条", flush=True)
        if new_count == 0:
            break
        clicked = False
        for sel in [
            '[aria-label="下一页"]', '.btn-next', 'span.next',
            'text=">"', 'span[class*="next"]',
        ]:
            try:
                btn = page.locator(sel).first
                if not await btn.get_attribute("disabled"):
                    try:
                        await btn.click(timeout=2000)
                    except Exception:
                        await btn.evaluate("el => el.click()")
                    clicked = True
                    break
            except Exception:
                pass
        if not clicked:
            break
        await asyncio.sleep(2.5)
    return all_items


@collector("el_pagination")
async def collect_el_pagination(page, url: str) -> list:
    """Element UI 翻页（海尔消金专用）"""
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(3)
    all_items, seen = [], set()
    while True:
        for _ in range(4):
            await page.evaluate("window.scrollBy(0, 500)")
            await asyncio.sleep(0.3)
        text = await page.evaluate("document.body.innerText")
        raw_items = extract_from_text(text, page.url)
        skip = ["每月", "领导接访", "来访人", "来访请求", "预约电话",
                "尊敬的客户", "来信来访", "注册地", "法定代表人",
                "可用资本", "来访者应", "来信人", "预约后"]
        new_count = 0
        for item in raw_items:
            t = item["title"]
            if len(t) < 6 or any(p in t for p in skip):
                continue
            if not item["date"]:
                continue
            key = f"{t[:30]}|{item['date']}"
            if key not in seen:
                seen.add(key)
                all_items.append(item)
                new_count += 1
        print(f"  page: +{new_count}条, 累计{len(all_items)}条", flush=True)
        if len(all_items) > 100:   # 海尔消金有频率限制
            break
        if new_count == 0:
            break
        clicked = False
        for sel in ["[aria-label=下一页]", "button:has-text(下一页)", "span:has-text(下一页)"]:
            try:
                btn = page.locator(sel).first
                if not await btn.get_attribute("disabled"):
                    await btn.click(timeout=2000)
                    clicked = True
                    break
            except Exception:
                pass
        if not clicked:
            break
        await asyncio.sleep(2.5)
    return all_items


# ════════════════════════════════════════════════════════════════════════════════
# GROUP_C — 首页滚动（JS动态加载，列表即首页）
# ════════════════════════════════════════════════════════════════════════════════

@collector("homepage_scroll")
async def collect_homepage_scroll(page, url: str) -> list:
    """首页滚动提取（平安 / 金美信）"""
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(3)
    for _ in range(8):
        await page.evaluate("window.scrollBy(0, 500)")
        await asyncio.sleep(0.4)
    text = await page.evaluate("document.body.innerText")
    return extract_from_text(text, url)


@collector("pingan_detail")
async def collect_pingan(page, url: str) -> list:
    """平安消费金融：首页 fullPage.js 滚动，弹出层关闭"""
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(4)
    for _ in range(15):
        await page.evaluate("window.scrollBy(0, window.innerHeight)")
        await asyncio.sleep(0.3)
    for pop_sel in ["[class*=popUp] button", "[class*=popUp] .close", ".notice_popUp_box"]:
        try:
            await page.locator(pop_sel).first.click(timeout=1000)
        except Exception:
            pass
    await asyncio.sleep(1)
    text = await page.evaluate("document.body.innerText")
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    items = []
    skip_kw = ["产品服务", "关于我们", "消费者之家", "证照公示", "首页",
               "Copyright", "ICP备案", "公网安", "年化利率", "额度", "定价",
               "400-", "中国平安", "注册地址", "公司名称", "经营范围", "有限公司",
               "minDate", "maxDate", "实际利率", "需要根据", "按照单利", "感谢您"]
    for line in lines:
        if len(line) > 15 and "消费金融" in line and not any(k in line for k in skip_kw):
            items.append({"title": line[:100], "date": today, "url": url, "category": "平安消费金融"})
    seen = set()
    unique = [i for i in items if seen.add(i["title"][:30]) is None or i["title"][:30] not in seen]
    return unique[:20]


# ════════════════════════════════════════════════════════════════════════════════
# GROUP_D — 详情页 URL 可枚举（从列表页提取 ID 构造详情 URL）
# ════════════════════════════════════════════════════════════════════════════════

@collector("zhongyou_detail")
async def collect_zhongyou(page, url: str) -> list:
    """中邮消费金融：提取 /xxgg/{id}.html 详情URL"""
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(3)
    for _ in range(6):
        await page.evaluate("window.scrollBy(0, 500)")
        await asyncio.sleep(0.3)

    blocks = await page.evaluate("""
        () => {
            const results = [];
            document.querySelectorAll('a[href*="/xxgg/"]').forEach(a => {
                const href = a.href;
                if (!href.match(/\\/xxgg\\/\\d+\\.html/)) return;
                const text = a.innerText.trim();
                if (!text || text.length < 5) return;
                let date = '';
                const pt = (a.parentElement || {}).innerText || '';
                const m = pt.match(/(\\d{4}[-/]\\d{2}[-/]\\d{2})/);
                if (m) date = m[1];
                if (!date) {
                    const gp = (a.parentElement || {}).parentElement || {};
                    const m2 = (gp.innerText || '').match(/(\\d{4}[-/]\\d{2}[-/]\\d{2})/);
                    if (m2) date = m2[1];
                }
                if (!date) {
                    const urlDate = href.match(/(\\d{4})(\\d{2})(\\d{2})/);
                    if (urlDate) date = urlDate[1] + '-' + urlDate[2] + '-' + urlDate[3];
                }
                if (text && text.length > 5 && date)
                    results.push({ title: text, date, href });
            });
            const seen = new Set();
            return results.filter(r => { if (seen.has(r.href)) return false; seen.add(r.href); return true; });
        }
    """)
    items, seen = [], set()
    for b in (blocks or []):
        key = f"{b['title'][:30]}|{b['date']}"
        if key not in seen:
            seen.add(key)
            items.append({"title": b["title"][:200], "date": b["date"], "url": b["href"],
                          "category": classify(b["title"])})
    print(f"  中邮消金: {len(items)}条详情页", flush=True)
    return items


@collector("xiaomi_detail")
async def collect_xiaomi(page, url: str) -> list:
    """小米消费金融：提取 /newsDetail?id= 详情URL"""
    await page.goto(url, wait_until="networkidle", timeout=20000)
    await asyncio.sleep(4)
    for _ in range(6):
        await page.evaluate("window.scrollBy(0, 500)")
        await asyncio.sleep(0.3)

    blocks = await page.evaluate("""
        () => {
            const results = [];
            document.querySelectorAll('a[href*="newsDetail"]').forEach(a => {
                const href = a.href;
                const text = a.innerText.trim();
                if (!text || text.length < 6) return;
                if (text.includes('AppStore') || text.includes('Android')) return;
                const container = (a.parentElement || {}).innerText || '';
                let date = '';
                const m = container.match(/(\\d{4})[-/年](\\d{1,2})[-/月](\\d{1,2})/);
                if (m)
                    date = m[1] + '-' + String(m[2]).padStart(2,'0') + '-' + String(m[3]).padStart(2,'0');
                if (!date) date = '2025-01-01';
                results.push({ title: text, date, href });
            });
            const seen = new Set();
            return results.filter(r => { if (seen.has(r.href)) return false; seen.add(r.href); return true; });
        }
    """)
    items, seen = [], set()
    for b in (blocks or []):
        key = f"{b['title'][:30]}|{b['date']}"
        if key not in seen:
            seen.add(key)
            items.append({"title": b["title"][:200], "date": b["date"], "url": b["href"],
                          "category": classify(b["title"])})
    print(f"  小米消金: {len(items)}条详情页", flush=True)
    return items


@collector("jinmixin_detail")
async def collect_jinmixin(page, url: str) -> list:
    """金美信消费金融：提取 /xxpl/{id} 详情URL"""
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(3)
    for _ in range(8):
        await page.evaluate("window.scrollBy(0, 500)")
        await asyncio.sleep(0.4)

    blocks = await page.evaluate("""
        () => {
            const results = [];
            document.querySelectorAll('a[href]').forEach(a => {
                const href = a.href;
                if (!href.match(/\\/xxpl\\/\\d+/)) return;
                const text = a.innerText.trim();
                if (!text || text.length < 6) return;
                if (['首页', '关于金美信', '产品服务'].includes(text)) return;
                let date = '';
                const pt = (a.parentElement || {}).innerText || '';
                const m = pt.match(/(\\d{4}-\\d{2}-\\d{2})/);
                if (m) date = m[1];
                if (!date) {
                    const gp = (a.parentElement || {}).parentElement || {};
                    const m2 = (gp.innerText || '').match(/(\\d{4}-\\d{2}-\\d{2})/);
                    if (m2) date = m2[1];
                }
                if (!date) date = '2025-01-01';
                results.push({ title: text, date, href });
            });
            const seen = new Set();
            return results.filter(r => { if (seen.has(r.href)) return false; seen.add(r.href); return true; });
        }
    """)
    items, seen = [], set()
    for b in (blocks or []):
        key = f"{b['title'][:30]}|{b['date']}"
        if key not in seen:
            seen.add(key)
            items.append({"title": b["title"][:200], "date": b["date"], "url": b["href"],
                          "category": classify(b["title"])})
    print(f"  金美信消金: {len(items)}条详情页", flush=True)
    return items


@collector("xingye_detail")
async def collect_xingye(page, url: str) -> list:
    """兴业消费金融：精确 DOM（.new_title + .new_time + 附件）"""
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(3)
    await page.evaluate("window.scrollTo(0, 0)")
    await asyncio.sleep(1)

    blocks = await page.evaluate("""
        () => {
            const results = [];
            document.querySelectorAll('.new_title').forEach(titleEl => {
                const parent = titleEl.parentElement;
                const title = titleEl.innerText.trim();
                if (!title || title.length < 10) return;
                let date = '';
                const timeEl = parent.querySelector('.new_time');
                if (timeEl) {
                    const m = timeEl.innerText.match(/(\\d{4}-\\d{2}-\\d{2})/);
                    if (m) date = m[1];
                }
                if (!date) return;
                const links = [];
                parent.querySelectorAll('a[href]').forEach(a => {
                    const h = a.href;
                    if (h && !h.includes('javascript') && h !== '#') links.push(h);
                });
                let sib = parent.nextElementSibling;
                while (sib) {
                    sib.querySelectorAll('a[href]').forEach(a => {
                        const h = a.href;
                        if (h && !h.includes('javascript') && h !== '#') links.push(h);
                    });
                    if (sib.querySelector('.new_title')) break;
                    sib = sib.nextElementSibling;
                }
                const uniqueLinks = [...new Set(links)];
                if (uniqueLinks.length === 0)
                    results.push({ title, date, url: window.location.href });
                else
                    uniqueLinks.forEach(href => results.push({ title, date, url: href }));
            });
            return results;
        }
    """)
    items, seen = [], set()
    for b in (blocks or []):
        key = f"{b['title'][:30]}|{b['date']}|{b['url'][:30]}"
        if key not in seen:
            seen.add(key)
            items.append({"title": b["title"][:200], "date": b["date"], "url": b["url"],
                          "category": classify(b["title"])})
    print(f"  兴业消金: {len(items)}条（含PDF附件）", flush=True)
    return items


@collector("haier_news_detail")
async def collect_haier(page, url: str) -> list:
    """海尔消费金融：Element UI 分页（14页）+ .newsList DOM提取公告图片URL"""
    await page.goto(url, wait_until="networkidle", timeout=20000)
    await asyncio.sleep(4)

    all_items, seen = [], set()

    async def extract_page_items():
        blocks = await page.evaluate("""
            () => {
                const results = [];
                document.querySelectorAll(".newsList").forEach(item => {
                    const day = item.querySelector(".day") ? item.querySelector(".day").innerText.trim() : "";
                    const month = item.querySelector(".month") ? item.querySelector(".month").innerText.trim() : "";
                    const titleEl = item.querySelector(".title");
                    const title = titleEl ? titleEl.innerText.trim() : "";
                    const imgEl = item.querySelector(".imgBox img");
                    const imgSrc = imgEl ? imgEl.src : "";
                    const contentEl = item.querySelector(".contentBox");
                    const truncated = contentEl ? contentEl.innerText.trim() : "";
                    if (!title) return;
                    let date = "";
                    if (month && day) {
                        const m2 = month.match(/^(\\d{4})\\/(\\d{2})$/);
                        if (m2) date = m2[1] + "-" + m2[2] + "-" + (day || "01").padStart(2, "0");
                    }
                    if (!date) date = "2026-01-01";
                    results.push({ title, date, imgSrc, truncated });
                });
                return results;
            }
        """)
        return blocks or []

    for b in await extract_page_items():
        key = f"{b['title'][:30]}|{b['date']}"
        if key not in seen:
            seen.add(key)
            all_items.append({"title": b["title"][:200], "date": b["date"],
                             "url": b["imgSrc"], "_truncated": b["truncated"][:500],
                             "category": classify(b["title"])})

    print(f"  海尔第1页: +{len(all_items)}条 累计{len(all_items)}条", flush=True)

    for pg in range(2, 15):
        try:
            btn = page.locator(f'.el-pager li[aria-label="第 {pg} 页"]')
            await btn.click(timeout=3000)
            await asyncio.sleep(2)
            new_count = 0
            for b in await extract_page_items():
                key = f"{b['title'][:30]}|{b['date']}"
                if key not in seen:
                    seen.add(key)
                    all_items.append({"title": b["title"][:200], "date": b["date"],
                                     "url": b["imgSrc"], "_truncated": b["truncated"][:500],
                                     "category": classify(b["title"])})
                    new_count += 1
            print(f"  海尔第{pg}页: +{new_count}条 累计{len(all_items)}条", flush=True)
        except Exception as e:
            print(f"  海尔第{pg}页失败: {str(e)[:50]}", flush=True)
            break

    print(f"  海尔消金: {len(all_items)}条（含图片URL）", flush=True)
    return all_items


@collector("beiyin_marquee")
async def collect_beiyin(page, url: str) -> list:
    """北银消费金融：首页滚动区提取URL → 详情页获取日期"""
    all_items, seen = [], set()
    base = "https://www.bobcfc.com"
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        await asyncio.sleep(3)
        for _ in range(6):
            await page.evaluate("window.scrollBy(0, 400)")
            await asyncio.sleep(0.5)
        els = await page.query_selector_all('.dowebok a[href*="/contents/"]')
        urls = []
        for el in els:
            href = await el.get_attribute("href") or ""
            if href and href not in seen:
                seen.add(href)
                t = await el.inner_text()
                t = t.replace("处理个人信息合作机构列表", "").strip()
                if t:
                    urls.append((t, base + href))
        print(f"  北银滚动区: {len(urls)}个公告", flush=True)
        for title, detail_url in urls:
            try:
                await page.goto(detail_url, wait_until="domcontentloaded", timeout=15000)
                await asyncio.sleep(2)
                text = await page.evaluate("document.body.innerText")
                date_str = ""
                for line in text.split("\n"):
                    line = line.strip()
                    if re.search(r"202[4-6]", line) and len(line) < 30:
                        date_str = line
                        break
                if date_str:
                    all_items.append({"title": title[:200], "date": date_str,
                                     "url": detail_url, "category": classify(title)})
            except Exception as e:
                print(f"    北银详情页异常 {detail_url}: {e}", flush=True)
    except Exception as e:
        return [{"title": f"ERROR: {e}", "date": "", "url": url, "category": "错误"}]
    return all_items


@collector("jincheng_detail")
async def collect_jincheng(page, url: str) -> list:
    """锦程消费金融：从标题提取 YYYYMM / YYYY.MM 格式日期"""
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(3)
    for _ in range(5):
        await page.evaluate("window.scrollBy(0, 400)")
        await asyncio.sleep(0.3)
    items, seen = [], set()
    date_re = re.compile(r"(\d{4})[\.月](\d{2})")
    lines = (await page.evaluate("document.body.innerText")).split("\n")
    for line in lines:
        line = line.strip()
        if not line or len(line) < 5:
            continue
        m = date_re.search(line)
        date_str = ""
        if m:
            y, mo = int(m.group(1)), int(m.group(2))
            if 2020 <= y <= 2030 and 1 <= mo <= 12:
                date_str = f"{y:04d}-{mo:02d}"
        key = line[:30] + "|" + date_str
        if key not in seen:
            seen.add(key)
            items.append({"title": line, "date": date_str, "url": url, "category": "锦程消费金融"})
    valid = [i for i in items if i["date"]]
    return valid if valid else items[:5]


# ════════════════════════════════════════════════════════════════════════════════
# GROUP_E — Vue / SPA / JS 框架
# ════════════════════════════════════════════════════════════════════════════════

@collector("vue_pagination")
async def collect_vue_pagination(page, url: str) -> list:
    """Vue翻页（'>'按钮）：招联消费金融"""
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(3)
    all_items, seen = [], set()
    while True:
        for _ in range(4):
            await page.evaluate("window.scrollBy(0, 500)")
            await asyncio.sleep(0.3)
        text = await page.evaluate("document.body.innerText")
        items = extract_from_text(text, page.url)
        new_count = 0
        for item in items:
            key = f"{item['title'][:30]}|{item['date']}"
            if key not in seen:
                seen.add(key)
                all_items.append(item)
                new_count += 1
        print(f"  page: +{new_count}条, 累计{len(all_items)}条", flush=True)
        if new_count == 0:
            break
        clicked = False
        for sel in ["text=>", "text=下一页", "[class*=next]",
                    "button:has-text('下一页')"]:
            try:
                btn = page.locator(sel).first
                if not await btn.get_attribute("disabled"):
                    await btn.click(timeout=2000)
                    clicked = True
                    break
            except Exception:
                pass
        if not clicked:
            try:
                btns = page.locator(".pc_media.page__pagination__item:not(.disabled)")
                cnt = await btns.count()
                if cnt > 0:
                    await btns.nth(cnt - 1).click(timeout=2000)
                    clicked = True
            except Exception:
                pass
        if not clicked:
            break
        await asyncio.sleep(2.5)
    return all_items


@collector("jianxin_dmyy")
async def collect_jianxin(page, url: str) -> list:
    """建信消费金融：Vue SPA，等待网络idle + 充分滚动"""
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(4)
    for _ in range(6):
        await page.evaluate("window.scrollBy(0, 500)")
        await asyncio.sleep(0.5)
    text = await page.evaluate("document.body.innerText")
    return extract_from_text(text, url)


@collector("suyinkaiji_vue")
async def collect_suyinkaiji(page, url: str) -> list:
    """苏银凯基消费金融：Vue Tab切换，Cloudflare WAF bypass"""
    def norm_date(year_str: str, day_str: str) -> str:
        m = re.match(r"(\d{4})\s*[-–]\s*(\d{1,2})", year_str.strip())
        if m:
            return f"{m.group(1)}-{int(m.group(2)):02d}-{int(day_str.strip()):02d}"
        return ""

    async def extract_page(seen: set) -> list:
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
                except Exception:
                    continue
        except Exception:
            pass
        return items

    await page.goto(url, wait_until="domcontentloaded", timeout=20000)
    await asyncio.sleep(4)
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
            except Exception:
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


# ════════════════════════════════════════════════════════════════════════════════
# GROUP_F — 多 Tab / 多栏
# ════════════════════════════════════════════════════════════════════════════════

@collector("multi_page")
async def collect_multi_page(page, url: str) -> list:
    """多Tab翻页（通知公告+消保之声+企业新闻）：湖北消费金融"""
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(3)
    all_items, seen = [], set()
    tabs = ["通知公告", "消保之声", "企业新闻"]
    for tab_name in tabs:
        try:
            tab_btn = page.locator(f"text={tab_name}").first
            await tab_btn.click(timeout=3000)
            await asyncio.sleep(2)
        except Exception:
            pass
        page_num = 0
        while True:
            page_num += 1
            for _ in range(4):
                await page.evaluate("window.scrollBy(0, 400)")
                await asyncio.sleep(0.3)
            text = await page.evaluate("document.body.innerText")
            items = extract_from_text(text, url)
            new_count = 0
            for item in items:
                key = f"{item['title'][:30]}|{item['date']}"
                if key not in seen:
                    seen.add(key)
                    all_items.append(item)
                    new_count += 1
            print(f"  [{tab_name}] {page_num}页:+{new_count}条 累计{len(all_items)}条", flush=True)
            if new_count == 0:
                break
            next_clicked = False
            for sel in ["text=下一页", "[class*=next]", "span.next"]:
                try:
                    btn = page.locator(sel).first
                    if not await btn.get_attribute("disabled"):
                        await btn.click(timeout=2000)
                        next_clicked = True
                        break
                except Exception:
                    pass
            if not next_clicked:
                break
            await asyncio.sleep(2)
    return all_items


@collector("jinshang_detail|jinshang_two_col")
async def collect_jinshang(page, url: str) -> list:
    """晋商消费金融：双栏（col23 + col22），提取详情URL"""
    all_items, seen = [], set()
    for col_url, col_name in [
        ("https://www.jcfc.cn/col23/list.html", "col23"),
        ("https://www.jcfc.cn/col22/list.html", "col22"),
    ]:
        await page.goto(col_url, wait_until="domcontentloaded", timeout=15000)
        await asyncio.sleep(3)
        page_num = 0
        while True:
            page_num += 1
            for _ in range(4):
                await page.evaluate("window.scrollBy(0, 400)")
                await asyncio.sleep(0.3)

            blocks = await page.evaluate("""
                () => {
                    const results = [];
                    document.querySelectorAll("a[href]").forEach(a => {
                        const href = a.href;
                        if (!href.match(/\\/col23\\/\\d+\\.html|\\/col22\\/\\d+\\.html/)) return;
                        const text = a.innerText.trim();
                        if (!text || text.length < 5) return;
                        let date = '';
                        const pt = (a.parentElement || {}).innerText || '';
                        const dm = pt.match(/(\\d{4}-\\d{2}-\\d{2})/);
                        if (dm) date = dm[1];
                        if (!date) {
                            const gp = (a.parentElement || {}).parentElement || {};
                            const dm2 = (gp.innerText || '').match(/(\\d{4}-\\d{2}-\\d{2})/);
                            if (dm2) date = dm2[1];
                        }
                        if (!date) date = '2025-01-01';
                        results.push({ title: text, date, href });
                    });
                    const seenLocal = new Set();
                    return results.filter(r => {
                        if (seenLocal.has(r.href)) return false;
                        seenLocal.add(r.href); return true;
                    });
                }
            """)
            new_count = 0
            for b in (blocks or []):
                key = f"{b['title'][:30]}|{b['date']}"
                if key not in seen:
                    seen.add(key)
                    all_items.append({"title": b["title"][:200], "date": b["date"],
                                     "url": b["href"], "category": classify(b["title"])})
                    new_count += 1
            print(f"  [{col_name}第{page_num}页]+{new_count}条 累计{len(all_items)}条", flush=True)
            if new_count == 0:
                break
            clicked = False
            for sel in ["text=下一页"]:
                try:
                    btn = page.locator(sel).first
                    if await btn.count() > 0 and not await btn.get_attribute("disabled"):
                        await btn.click(timeout=2000)
                        clicked = True
                except Exception:
                    pass
            if not clicked:
                break
            await asyncio.sleep(2)
    return all_items


@collector("nyfb_two_page")
async def collect_nyfb(page, url: str) -> list:
    """南银法巴消费金融：双页（公司公告+新闻资讯）"""
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(3)
    all_items, seen = [], set()
    for sub_url, sub_name in [
        ("https://www.boncfc.com/boncfc/xwgg/gsgg/", "gsgg"),
        ("https://www.boncfc.com/boncfc/xwgg/xwzx/", "xwzx"),
    ]:
        try:
            await page.goto(sub_url, wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(2)
        except Exception:
            pass
        page_num = 0
        while True:
            page_num += 1
            for _ in range(4):
                await page.evaluate("window.scrollBy(0, 400)")
                await asyncio.sleep(0.3)
            text = await page.evaluate("document.body.innerText")
            items = extract_from_text(text, sub_url)
            new_count = 0
            for item in items:
                key = f"{item['title'][:30]}|{item['date']}"
                if key not in seen:
                    seen.add(key)
                    all_items.append(item)
                    new_count += 1
            print(f"  [{sub_name}] 第{page_num}页:+{new_count}条 累计{len(all_items)}条", flush=True)
            if new_count == 0:
                break
            clicked = False
            for sel in ["text=下一页", "[class*=next]"]:
                try:
                    btn = page.locator(sel).first
                    if not await btn.get_attribute("disabled"):
                        await btn.click(timeout=2000)
                        clicked = True
                        break
                except Exception:
                    pass
            if not clicked:
                break
            await asyncio.sleep(2)
    return all_items


# ════════════════════════════════════════════════════════════════════════════════
# GROUP_G — 特殊格式
# ════════════════════════════════════════════════════════════════════════════════

@collector("zhongyin_layui")
async def collect_zhongyin(page, url: str) -> list:
    """中银消费金融：layui JS分页，13页，.main_content_body_item"""
    all_items, seen = [], set()
    base = "https://www.boccfc.cn"
    for pg in range(1, 20):
        try:
            if pg == 1:
                await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                await asyncio.sleep(3)
            else:
                clicked = False
                for sel in [f'a[data-page="{pg}"]', f'.layui-laypage a[data-page="{pg}"]']:
                    try:
                        btn = page.locator(sel).first
                        if await btn.count() > 0:
                            await btn.click(timeout=3000)
                            clicked = True
                            break
                    except Exception:
                        pass
                if not clicked:
                    try:
                        next_btn = page.locator('.layui-laypage a.layui-laypage-prev + a').first
                        if await next_btn.count() > 0:
                            await next_btn.click(timeout=3000)
                            clicked = True
                    except Exception:
                        pass
                if not clicked:
                    print(f"    中银第{pg}页找不到按钮，停止", flush=True)
                    break
            await asyncio.sleep(2)

            items = await page.query_selector_all(".main_content_body_item")
            new_count = 0
            for item in items:
                try:
                    href = await item.get_attribute("href") or ""
                    spans = await item.query_selector_all("span")
                    date_str = ""
                    for sp in spans:
                        t = await sp.inner_text()
                        m = re.search(r"(\d{4}[-/]\d{2}[-/]\d{2})", t)
                        if m:
                            date_str = m.group(1).replace("/", "-")
                            break
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
                        all_items.append({"title": title[:200], "date": date_str,
                                         "url": detail_url, "category": classify(title)})
                        new_count += 1
                except Exception:
                    continue
            print(f"  中银第{pg}页:+{new_count}条 累计{len(all_items)}条", flush=True)
            if new_count == 0:
                break
        except Exception as e:
            print(f"  中银第{pg}页异常: {e}", flush=True)
            break
    return all_items


@collector("yangguang_detail")
async def collect_yangguang(page, url: str) -> list:
    """阳光消费金融：DOM列表提取（标题+日期来自URL路径）"""
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(4)
    all_items, seen = [], set()
    page_num = 0
    while page_num < 10:
        page_num += 1
        for _ in range(2):
            await page.evaluate("window.scrollBy(0, 400)")
            await asyncio.sleep(0.3)
        raw_items = await page.evaluate("""
            () => {
                const result = [];
                const selectors = ['.list-item', '.news-item', '.article-item',
                                   'li[data-id]', '.item', 'ul li', '.newslist li'];
                let containers = [];
                for (const sel of selectors) {
                    containers = document.querySelectorAll(sel);
                    if (containers.length > 0) break;
                }
                if (containers.length === 0) {
                    const links = document.querySelectorAll('a[href*="/xxgg/"]');
                    for (const a of links) {
                        const text = a.innerText.trim();
                        if (text.length > 5 && !text.includes('首页') && !text.includes('关于我们'))
                            result.push({ title: text, href: a.href });
                    }
                } else {
                    for (const container of containers) {
                        const a = container.querySelector('a[href*="/xxgg/"]') || container.querySelector('a');
                        const titleEl = a || container.querySelector('.title, h3, h4, .tit');
                        if (titleEl)
                            result.push({ title: titleEl.innerText.trim().slice(0, 100), href: a ? a.href : '' });
                    }
                }
                return result;
            }
        """)
        new_count = 0
        for raw in raw_items:
            title = raw.get('title', '')
            if len(title) < 4:
                continue
            if any(x in title for x in ["首页", "关于我们", "联系我们", "版权", "客服", "投诉"]):
                continue
            href = raw.get('href', '')
            date_str = ""
            date_m = re.search(r'/(\d{4})(\d{2})(\d{2})\d+/index\.html', href)
            if date_m:
                date_str = f"{date_m.group(1)}-{date_m.group(2)}-{date_m.group(3)}"
            key = f"{title[:30]}|{date_str}"
            if key not in seen and title:
                seen.add(key)
                all_items.append({"title": title[:200], "date": date_str,
                                 "url": href or url, "category": classify(title)})
                new_count += 1
        print(f"  第{page_num}页:+{new_count}条 累计{len(all_items)}条", flush=True)
        if new_count == 0:
            break
        clicked = False
        for sel in ["text=下一页", "[class*=next]", "a:has-text('下一页')", ".next"]:
            try:
                btn = page.locator(sel).first
                if await btn.count() > 0 and "disabled" not in (await btn.get_attribute("class") or ""):
                    await btn.click(timeout=2000)
                    clicked = True
                    break
            except Exception:
                pass
        if not clicked:
            break
        await asyncio.sleep(2)
    return all_items


@collector("zhongyuan")
async def collect_zhongyuan(page, url: str) -> list:
    """中原消费金融：滚动加载，'查看更多'翻页，split-line日期"""
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(3)
    all_items, seen = [], set()
    for _ in range(8):
        for _ in range(4):
            await page.evaluate("window.scrollBy(0, 400)")
            await asyncio.sleep(0.3)
        text = await page.evaluate("document.body.innerText")
        items = extract_from_text(text, url)
        for item in items:
            key = f"{item['title'][:30]}|{item['date']}"
            if key not in seen:
                seen.add(key)
                all_items.append(item)
        print(f"  中原:+{len(items)}条 累计{len(all_items)}条", flush=True)
        clicked = False
        for sel in ["text=查看更多", "text=加载更多", "[class*=more]"]:
            try:
                btns = page.locator(sel)
                cnt = await btns.count()
                if cnt > 0:
                    btn = btns.first
                    if not await btn.get_attribute("disabled"):
                        await btn.click(timeout=3000)
                        clicked = True
            except Exception:
                pass
        if not clicked:
            break
        await asyncio.sleep(2)
    skip_prefixes = ("您现在的位置", "新闻公告", "公司动态", "媒体报道", "通知公告",
                     "企业荣誉", "党建活动", "信息披露")
    filtered = [it for it in all_items if not any(it["title"].startswith(p) for p in skip_prefixes)]
    print(f"  中原过滤后:{len(filtered)}条（原始{len(all_items)}条）", flush=True)
    return filtered


@collector("hangyin_two_line")
async def collect_hangyin(page, url: str) -> list:
    """杭银消费金融：双行格式（日期在标题下方），MM/DD split-line"""
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(3)
    all_items, seen = [], set()
    page_num = 0
    while page_num < 10:
        page_num += 1
        for _ in range(4):
            await page.evaluate("window.scrollBy(0, 400)")
            await asyncio.sleep(0.3)
        text = await page.evaluate("document.body.innerText")
        items = extract_from_text(text, url)
        new_count = 0
        for item in items:
            key = f"{item['title'][:30]}|{item['date']}"
            if key not in seen:
                seen.add(key)
                all_items.append(item)
                new_count += 1
        print(f"  第{page_num}页:+{new_count}条 累计{len(all_items)}条", flush=True)
        if new_count == 0:
            break
        clicked = False
        for sel in ["text=下一页", "[class*=next]"]:
            try:
                btn = page.locator(sel).first
                if not await btn.get_attribute("disabled"):
                    await btn.click(timeout=2000)
                    clicked = True
                    break
            except Exception:
                pass
        if not clicked:
            break
        await asyncio.sleep(2)
    return all_items


@collector("static_list")
async def collect_static_list(page, url: str) -> list:
    """蒙商消费金融：静态列表多页"""
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(3)
    all_items, seen = [], set()
    page_num = 0
    while page_num < 10:
        page_num += 1
        for _ in range(4):
            await page.evaluate("window.scrollBy(0, 400)")
            await asyncio.sleep(0.3)
        text = await page.evaluate("document.body.innerText")
        items = extract_from_text(text, url)
        new_count = 0
        for item in items:
            key = f"{item['title'][:30]}|{item['date']}"
            if key not in seen:
                seen.add(key)
                all_items.append(item)
                new_count += 1
        print(f"  第{page_num}页:+{new_count}条 累计{len(all_items)}条", flush=True)
        if new_count == 0:
            break
        clicked = False
        for sel in ["text=下一页", "[class*=next]", "a:has-text('下一页')"]:
            try:
                btn = page.locator(sel).first
                if not await btn.get_attribute("disabled"):
                    await btn.click(timeout=2000)
                    clicked = True
                    break
            except Exception:
                pass
        if not clicked:
            break
        await asyncio.sleep(2)
    return all_items


@collector("mengshang_detail")
async def collect_mengshang(page, url: str) -> list:
    """蒙商消费金融：提取 /html/1//208/217/{id}.html 详情URL"""
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(3)
    for _ in range(4):
        await page.evaluate("window.scrollBy(0, 400)")
        await asyncio.sleep(0.3)
    blocks = await page.evaluate("""
        () => {
            const results = [];
            document.querySelectorAll('a[href]').forEach(a => {
                const href = a.href;
                if (!href.match(/\\/html\\/1\\/\\/208\\/217\\/\\d+\\.html/)) return;
                const text = a.innerText.trim();
                if (!text || text.length < 6) return;
                let date = '';
                const pt = (a.parentElement || {}).innerText || '';
                const dm = pt.match(/(\\d{4}-\\d{2}-\\d{2})/);
                if (dm) date = dm[1];
                if (!date) {
                    const gp = (a.parentElement || {}).parentElement || {};
                    const dm2 = (gp.innerText || '').match(/(\\d{4}-\\d{2}-\\d{2})/);
                    if (dm2) date = dm2[1];
                }
                if (!date) date = '2025-01-01';
                results.push({ title: text, date, href });
            });
            const seenL = new Set();
            return results.filter(r => { if (seenL.has(r.href)) return false; seenL.add(r.href); return true; });
        }
    """)
    items, seen = [], set()
    for b in (blocks or []):
        key = f"{b['title'][:30]}|{b['date']}"
        if key not in seen:
            seen.add(key)
            items.append({"title": b["title"][:200], "date": b["date"], "url": b["href"],
                         "category": classify(b["title"])})
    print(f"  蒙商消金: {len(items)}条详情页", flush=True)
    return items


@collector("hebei_detail")
async def collect_hebei(page, url: str) -> list:
    """河北幸福消费金融：直接文本提取（DD-MM-YY格式）"""
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(3)
    for _ in range(5):
        await page.evaluate("window.scrollBy(0, 600)")
        await asyncio.sleep(0.5)
    text = await page.evaluate("document.body.innerText")
    items = extract_from_text(text, url)
    for item in items:
        item["category"] = "河北幸福消费金融"
    return items


@collector("time_prefix")
async def collect_time_prefix(page, url: str) -> list:
    """盛银消费金融：时间在前标题在后"""
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(3)
    for _ in range(4):
        await page.evaluate("window.scrollBy(0, 400)")
        await asyncio.sleep(0.4)
    text = await page.evaluate("document.body.innerText")
    return extract_from_text(text, url)


@collector("shangcheng_news")
async def collect_shangcheng(page, url: str) -> list:
    """尚诚消费金融：新闻列表"""
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(3)
    for _ in range(4):
        await page.evaluate("window.scrollBy(0, 400)")
        await asyncio.sleep(0.4)
    text = await page.evaluate("document.body.innerText")
    return extract_from_text(text, url)


@collector("pdf_link|notice_link_parse")
async def collect_pdf_link(page, url: str) -> list:
    """天津京东消费金融 / 锦程消费金融：PDF附件列表"""
    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
    await asyncio.sleep(3)
    for _ in range(4):
        await page.evaluate("window.scrollBy(0, 400)")
        await asyncio.sleep(0.4)
    text = await page.evaluate("document.body.innerText")
    return extract_from_text(text, url)


# ════════════════════════════════════════════════════════════════════════════════
# GROUP_H — WSL2 受限（CDP专用，或特殊URL）
# ════════════════════════════════════════════════════════════════════════════════

@collector("changyin58_telling")
async def collect_changyin58(page, url: str) -> list:
    """长银五八消费金融：telling.html（无更新，2018年后停更）"""
    await page.goto(url, wait_until="domcontentloaded", timeout=20000)
    await asyncio.sleep(4)
    for _ in range(10):
        await page.evaluate("window.scrollBy(0, 500)")
        await asyncio.sleep(0.5)
    text = await page.evaluate("document.body.innerText")
    return extract_from_text(text, page.url)
