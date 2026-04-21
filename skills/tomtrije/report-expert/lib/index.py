"""索引管理：重建索引、添加页面、扫描目录"""

import json, re, sys, subprocess
from pathlib import Path
from datetime import date

from lib.config import (BASE_DIR, DIST_DIR, SITE_URL, SITE_NAME, _CFG,
                         INDEX_FILE, load_index, save_index, sync_to_deploy)
from lib.page import copy_assets

# 技能 dist 下需要排除扫描的子目录
_SCAN_EXCLUDE = {'backups', 'data', 'templates', 'scripts', 'styles',
                 '.wrangler', '__pycache__', 'node_modules'}


def _get_scan_dirs():
    """返回需要扫描的目录列表（技能 dist/）。"""
    return [DIST_DIR]


def rebuild_index(clean=False):
    """Scan pages and rebuild index.json, then regenerate index.html."""
    scan_and_rebuild()
    data = load_index()
    copy_assets()
    tpl = BASE_DIR / "templates" / "index.html"
    if tpl.exists():
        html = tpl.read_text("utf-8")
        html = html.replace("{{SITE_BASE}}", ".")
        html = html.replace("{{SITE_NAME}}", SITE_NAME)
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        # 写入技能 dist
        (DIST_DIR / "index.html").write_text(html, "utf-8")
        (DIST_DIR / "index.json").write_text(json_str, "utf-8")
    # 推送到部署目录
    synced = sync_to_deploy(clean=clean)
    print(f"✅ 索引已刷新，共 {len(data['pages'])} 篇内容")
    if synced:
        print(f"   同步: {synced} 个文件推送到部署目录")

def add_to_index(filename, title, desc, category, url=None):
    """Add an external page (e.g. deployed elsewhere) to the index"""
    data = load_index()
    today = date.today().isoformat()
    entry = {
        "filename": filename,
        "title": title,
        "desc": desc or "",
        "date": today,
        "category": category,
        "external": True,
    }
    if url:
        entry["url"] = url
    data["pages"].append(entry)
    save_index(data)
    print(f"✅ 已添加到索引: {title}")

def scan_and_rebuild():
    """Scan all HTML pages in dist/, extract metadata, build complete index.json.

    Reads title/date/desc from each page. If --ai flag is passed, also uses
    page content to auto-detect category and generate description.
    """
    use_ai = "--ai" in sys.argv
    # 扫描技能 dist
    scan_dirs = _get_scan_dirs()

    # Preserve existing external pages from current index
    existing_externals = []
    try:
        old_data = load_index()
        existing_externals = [p for p in old_data.get("pages", []) if p.get("external")]
        if existing_externals:
            print(f"📎 保留 {len(existing_externals)} 个外部页面")
    except Exception:
        pass

    pages = []
    seen_files = set()  # 按 filename 去重，后扫描的优先

    total_files = 0
    for dist in scan_dirs:
        if not dist.exists():
            continue
        html_files = sorted(dist.rglob("*.html"))
        # (排除规则在 _SCAN_EXCLUDE)
        html_files = [f for f in html_files
                       if f.name != "index.html"
                       and not any(p in _SCAN_EXCLUDE for p in f.parts)]
        total_files += len(html_files)

    if total_files == 0:
        print("⚠️ 未找到任何 HTML 页面"); return

    print(f"📡 扫描到 {total_files} 个页面（{len(scan_dirs)} 个目录）...")

    for dist in scan_dirs:
        if not dist.exists():
            continue
        for fpath in sorted(dist.rglob("*.html")):
            if fpath.name == "index.html":
                continue
            if any(p in _SCAN_EXCLUDE for p in fpath.parts):
                continue
            rel = fpath.relative_to(dist)
            category = str(rel.parent)  # e.g. "research", "analysis"
            key = f"{category}/{rel.name}"
            # 去重：同名文件只保留最新扫描的版本
            pages = [p for p in pages if f"{p['category']}/{p['filename']}" != key]
            html = fpath.read_text("utf-8")

            # Extract title
            title_m = re.search(r'<title>(.*?)</title>', html)
            title = title_m.group(1).strip() if title_m else fpath.stem

            # Extract date from filename (2026-04-09-xxx.html)
            date_m = re.match(r'(\d{4}-\d{2}-\d{2})', fpath.stem)
            date_str = date_m.group(1) if date_m else date.today().isoformat()

            # Extract desc from meta or first paragraph
            desc = ""
            desc_m = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]+)"', html)
            if not desc_m:
                desc_m = re.search(r'<p class="report-header__desc">(.*?)</p>', html, re.DOTALL)
            if desc_m:
                desc = re.sub(r'<[^>]+>', '', desc_m.group(1)).strip()

            # Extract body text for AI classification (first 2000 chars)
            body_text = ""
            body_m = re.search(r'<div class="page-body"[^>]*>(.*)</div>\s*<footer', html, re.DOTALL)
            if body_m:
                body_text = re.sub(r'<[^>]+>', '', body_m.group(1)).strip()[:2000]

            # Detect external pages (iframes or redirects)
            is_external = bool(re.search(r'<iframe|window\.location', html))
            page_url = f"{SITE_URL}/{rel}" if not is_external else None

            pages.append({
                "filename": rel.name,
                "title": title,
                "desc": desc,
                "date": date_str,
                "category": category,
                "url": page_url,
            })

            status = f"  ✅ {category}/{rel.name} — {title}"
            if use_ai and body_text:
                status += " (待 AI 分类)"
            print(status)

    # AI classification pass
    if use_ai:
        print(f"\n🤖 AI 分类中...")
        # Build a prompt with all pages
        cat_list = "(无限制)"
        for p in pages:
            fpath = None
            for d in scan_dirs:
                candidate = d / p["category"] / p["filename"]
                if candidate.exists():
                    fpath = candidate
                    break
            if not fpath or not fpath.exists():
                continue
            html = fpath.read_text("utf-8")
            body_m = re.search(r'<div class="page-body"[^>]*>(.*)</div>\s*<footer', html, re.DOTALL)
            body_text = re.sub(r'<[^>]+>', '', body_m.group(1)).strip()[:1500] if body_m else ""
            if not body_text:
                continue
            prompt = f"""根据以下内容，选择最合适的分类。
可选分类: {cat_list}
内容标题: {p['title']}
内容摘要(前1500字): {body_text}

只输出分类英文key，不要其他内容:"""
            try:
                result = subprocess.run(
                    ["openclaw", "ai", "--model", "zai/glm-5-turbo", "--prompt", prompt],
                    capture_output=True, text=True, timeout=30
                )
                ai_cat = result.stdout.strip().lower()
                if ai_cat:
                    old_cat = p["category"]
                    p["category"] = ai_cat
                    if old_cat != ai_cat:
                        print(f"  🔄 {p['filename']}: {old_cat} → {ai_cat}")
                # Also generate desc if missing
                if not p["desc"]:
                    desc_prompt = f"""用一句话(20-40字)描述以下内容的核心主题。
标题: {p['title']}
内容: {body_text[:800]}

只输出描述文字:"""
                    dr = subprocess.run(
                        ["openclaw", "ai", "--model", "zai/glm-5-turbo", "--prompt", desc_prompt],
                        capture_output=True, text=True, timeout=30
                    )
                    p["desc"] = dr.stdout.strip()[:100]
            except Exception as e:
                print(f"  ⚠️ {p['filename']}: AI 分类失败 ({e})")

    # Build categories from actual pages + preserve existing config
    existing_data = load_index()
    existing_cats = existing_data.get("categories", {})
    categories = {}
    for p in pages:
        cat = p["category"]
        if cat not in categories:
            categories[cat] = {"name": cat}  # default: use category key as display name
    # Merge existing categories config (only icon/description/color, not name if it's same as key)
    for cat, cfg in existing_cats.items():
        if cat in categories:
            for k, v in cfg.items():
                if k == "name" and v == cat:
                    continue  # skip fallback name (same as key)
                if v:
                    categories[cat][k] = v

    # Merge preserved external pages, deduplicate by URL
    scanned_urls = {p.get("url", "") for p in pages if p.get("url")}
    for ep in existing_externals:
        if ep.get("url", "") not in scanned_urls:
            pages.append(ep)
        else:
            print(f"  ⏭️ 跳过重复外部页面: {ep.get('title', ep.get('url'))}")

    # Save
    data = {
        "site": {"name": SITE_NAME, "baseUrl": SITE_URL},
        "categories": categories,
        "pages": pages,
    }
    save_index(data)

    print(f"\n✅ 索引重建完成")
    print(f"   页面: {len(pages)} 篇")
    print(f"   分类: {', '.join(categories.keys())}")
    print(f"   文件: {INDEX_FILE}")
