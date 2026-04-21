#!/usr/bin/env python3
"""传琪 · 报告部署系统 — 索引管理、首页生成、页面部署"""

import json, sys, shutil, re
from pathlib import Path
from datetime import date

BASE_DIR = Path(__file__).parent
DIST_DIR = BASE_DIR / "dist"

CATEGORIES = {
    "research": "深度研究",
    "analysis": "数据分析",
    "summary": "内容摘要",
    "comparison": "对比评测",
    "tutorial": "教程指南",
    "project": "项目作品",
    "other": "其他",
}

# ── 自适应配置：从 TOOLS.md 读取部署模式 ──
def _load_config():
    """Read REPORT_DEPLOY_MODE and related vars from TOOLS.md"""
    config = {"mode": "local", "local_dir": str(BASE_DIR), "local_url": "/", "site_name": "传琪"}
    tools = Path.home() / ".openclaw/workspace/TOOLS.md"
    if not tools.exists():
        return config
    text = tools.read_text("utf-8")
    def _get(key):
        m = re.search(rf'{key}=(.+)', text)
        if not m: return None
        v = m.group(1).strip()
        return v.strip().strip('`').strip() if v else None
    mode = _get("REPORT_DEPLOY_MODE") or "local"
    config["mode"] = mode
    if mode == "local":
        config["local_dir"] = _get("REPORT_LOCAL_DIR") or str(BASE_DIR)
        config["local_url"] = _get("REPORT_LOCAL_URL") or "/"
        config["site_name"] = _get("REPORT_SITE_NAME") or "传琪"
    elif mode == "remote":
        config["site_name"] = _get("CF_SITE_NAME") or "传琪"
        config["local_url"] = _get("CF_SITE_URL") or "/"
        config["local_dir"] = _get("CF_PROJECT_DIR") or str(BASE_DIR)
    return config

_CFG = _load_config()
INDEX_FILE = Path(_CFG["local_dir"]) / "index.json"
SITE_URL = _CFG["local_url"].rstrip("/")
SITE_NAME = _CFG["site_name"]

def load_index():
    if INDEX_FILE.exists():
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"site": {"name": SITE_NAME, "baseUrl": SITE_URL}, "pages": []}

def save_index(data):
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def strip_emoji(text):
    """Remove emoji and special symbols from text"""
    import unicodedata
    return re.sub(r'[\U0001f300-\U0001f9ff\U00002702-\U000027b0\U00002600-\U000026ff\U0001fa00-\U0001fa6f\U0001fa70-\U0001faff\u200d\ufe0f]', '', text)

def add_ids(html):
    counter = {}
    def repl(m):
        tag = m.group(1).lower()
        text = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        slug = re.sub(r'[^\w\u4e00-\u9fff]+', '-', text).strip('-').lower()
        if not slug: slug = 'section'
        counter[slug] = counter.get(slug, 0) + 1
        uid = slug if counter[slug] == 1 else f"{slug}-{counter[slug]}"
        return f'<{tag} id="{uid}">{m.group(2)}</{tag}>'
    return re.sub(r'<(h[23])>(.*?)</\1>', repl, html, flags=re.DOTALL)

def generate_page_html(page_info, base_url):
    cat = page_info["category"]
    cat_name = CATEGORIES.get(cat, "其他")
    body = add_ids(page_info["body"])
    page_style = page_info.get("style", "")
    style_tag = f"\n  <style>\n    {page_style}\n  </style>" if page_style else ""
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page_info["title"]}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+SC:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../styles/base.css">
{style_tag}
</head>
<body>
  <div class="scroll-progress"></div>
  <aside class="toc-sidebar">
    <div class="toc-sidebar__header">
      <div class="toc-sidebar__title">目录</div>
      <button class="toc-sidebar__close" aria-label="收起目录">✕</button>
    </div>
    <div class="toc-list"></div>
  </aside>
  <button class="toc-toggle" aria-label="展开目录">☰</button>
  <div class="report-wrap">
    <header class="report-header">
      <div class="report-header__breadcrumb">
        <a href="../" target="_top">🏠</a>
        <span>{cat_name}</span>
      </div>
      <div class="report-header__meta">
        <span class="report-header__tag">{cat_name}</span>
        <span class="report-header__date">{page_info["date"]}</span>
      </div>
      <h1 class="report-header__title">{page_info["title"]}</h1>
      {f'<p class="report-header__desc">{page_info["desc"]}</p>' if page_info.get("desc") else ""}
    </header>
    <div class="page-body" data-reveal>{body}</div>
  </div>
  <footer class="page-footer">
    <div class="page-footer__logo">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
    </div>
    <a href="../" class="page-footer__link" target="_top">{SITE_NAME}</a>
    <div class="page-footer__sep"></div>
    <span>报告与研究成果</span>
  </footer>
  <script src="../scripts/main.js?v=6"></script>
</body>
</html>'''

def copy_assets():
    """Ensure static assets exist in dist"""
    pass

def rebuild_index():
    data = load_index()
    copy_assets()
    tpl = BASE_DIR / "templates" / "index.html"
    if tpl.exists():
        html = tpl.read_text("utf-8")
        html = html.replace("{{SITE_BASE}}", ".")
        html = html.replace("{{SITE_NAME}}", SITE_NAME)
        (DIST_DIR / "index.html").write_text(html, "utf-8")
        (DIST_DIR / "index.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")
    print(f"✅ 索引已刷新，共 {len(data['pages'])} 篇内容")

def deploy(category, html_file, title=None, desc=None):
    if category not in CATEGORIES:
        print(f"❌ 未知分类: {category}")
        print(f"   可选: {', '.join(CATEGORIES.keys())}")
        sys.exit(1)
    src = Path(html_file)
    if not src.exists():
        print(f"❌ 文件不存在: {html_file}")
        sys.exit(1)

    with open(src, "r", encoding="utf-8") as f:
        html = f.read()

    # Extract body content
    body_match = re.search(r'<body[^>]*>(.*)</body>', html, re.DOTALL)
    if body_match:
        body = body_match.group(1).strip()
    else:
        body = html
    body = strip_emoji(body)

    # Extract style
    style_match = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
    page_style = style_match.group(1).strip() if style_match else ""

    # Remove wrapper divs if present
    for cls in ['report-wrap', 'page-body', 'wrap']:
        m = re.search(rf'<div class="{cls}"[^>]*>(.*)</div>\s*$', body, re.DOTALL)
        if m: body = m.group(1).strip()

    # Remove old headers/footers
    body = re.sub(r'<header[^>]*>.*?</header>', '', body, flags=re.DOTALL)
    body = re.sub(r'<footer[^>]*>.*?</footer>', '', body, flags=re.DOTALL)
    body = re.sub(r'<h1[^>]*>.*?</h1>', '', body, flags=re.DOTALL)

    if not title:
        title_match = re.search(r'<title>(.*?)</title>', html)
        title = title_match.group(1) if title_match else src.stem

    data = load_index()
    base_url = data["site"].get("baseUrl", SITE_URL)
    today = date.today().isoformat()
    filename = f"{today}-{src.stem}.html"

    page_info = {
        "title": title,
        "desc": desc or "",
        "date": today,
        "category": category,
        "body": body,
        "style": page_style,
    }

    page_html = generate_page_html(page_info, base_url)

    cat_dir = DIST_DIR / category
    cat_dir.mkdir(parents=True, exist_ok=True)
    out_path = cat_dir / filename
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page_html)

    # Update index
    page_url = f"{base_url}/{category}/{filename}"
    data["pages"].append({
        "filename": filename,
        "title": title,
        "desc": desc or "",
        "date": today,
        "category": category,
        "url": page_url,
    })
    save_index(data)

    print(f"✅ 部署成功")
    print(f"   分类: {CATEGORIES.get(category, category)} ({category})")
    print(f"   标题: {title}")
    print(f"   日期: {today}")
    print(f"   路径: /{category}/{filename}")
    print(f"   链接: {page_url}")

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
    import subprocess

    use_ai = "--ai" in sys.argv
    dist = DIST_DIR
    if not dist.exists():
        print(f"❌ dist 目录不存在: {dist}"); sys.exit(1)

    pages = []
    html_files = sorted(dist.rglob("*.html"))
    # Exclude index.html
    html_files = [f for f in html_files if f.name != "index.html"]

    if not html_files:
        print("⚠️ 未找到任何 HTML 页面"); return

    print(f"📡 扫描到 {len(html_files)} 个页面...")

    for fpath in html_files:
        rel = fpath.relative_to(dist)
        category = str(rel.parent)  # e.g. "research", "analysis"
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
        cat_list = ", ".join(CATEGORIES.keys())
        for p in pages:
            fpath = dist / p["category"] / p["filename"]
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
                if ai_cat in CATEGORIES:
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

    # Build categories from actual pages found
    cat_colors = {
        "research": {"c": "var(--c-amber)", "b": "var(--c-amber-light)"},
        "analysis": {"c": "var(--c-green)", "b": "var(--c-green-light)"},
        "project": {"c": "var(--c-accent)", "b": "var(--c-accent-light)"},
        "summary": {"c": "var(--c-purple)", "b": "var(--c-purple-light)"},
        "comparison": {"c": "var(--c-accent)", "b": "var(--c-accent-light)"},
        "tutorial": {"c": "var(--c-orange)", "b": "var(--c-orange-light)"},
        "other": {"c": "var(--c-text-muted)", "b": "var(--c-surface-alt)"},
    }
    cat_icons = {
        "research": "🔍", "analysis": "📊", "project": "🛠️",
        "summary": "📝", "comparison": "⚖️", "tutorial": "📖", "other": "📎",
    }
    cat_descs = {
        "research": "系统性调研与深度分析报告", "analysis": "数据驱动的分析洞察",
        "project": "开发项目与互动作品", "summary": "信息整理与要点提炼",
        "comparison": "产品、方案或工具的横向对比", "tutorial": "操作指南与最佳实践",
        "other": "未分类内容",
    }

    categories = {}
    for p in pages:
        cat = p["category"]
        if cat not in categories:
            categories[cat] = {
                "name": CATEGORIES.get(cat, cat),
                "icon": cat_icons.get(cat, "📄"),
                "description": cat_descs.get(cat, ""),
            }
            if cat in cat_colors:
                categories[cat]["color"] = cat_colors[cat]

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

def update_pages():
    """Re-wrap all report pages with the latest template and styles.

    Scans dist/ for HTML pages (excluding index.html), extracts body content
    and style, then re-generates each page using generate_page_html.
    """
    dist = DIST_DIR
    if not dist.exists():
        print(f"❌ dist 目录不存在: {dist}"); sys.exit(1)

    html_files = sorted(dist.rglob("*.html"))
    html_files = [f for f in html_files if f.name != "index.html"]

    if not html_files:
        print("⚠️ 未找到任何 HTML 页面"); return

    print(f"🔄 更新 {len(html_files)} 个页面...")
    updated = 0

    for fpath in html_files:
        rel = fpath.relative_to(dist)
        category = str(rel.parent)
        html = fpath.read_text("utf-8")

        # Extract title
        title_m = re.search(r'<title>(.*?)</title>', html)
        title = title_m.group(1).strip() if title_m else fpath.stem

        # Extract date from filename
        date_m = re.match(r'(\d{4}-\d{2}-\d{2})', fpath.stem)
        date_str = date_m.group(1) if date_m else date.today().isoformat()

        # Extract body (from page-body div)
        body_m = re.search(r'<div class="page-body"[^>]*>(.*)</div>\s*<footer', html, re.DOTALL)
        if not body_m:
            print(f"  ⏭️  {rel} — 无法提取内容，跳过")
            continue
        body = body_m.group(1).strip()
        body = strip_emoji(body)
        body = re.sub(r'<h1[^>]*>.*?</h1>', '', body, flags=re.DOTALL)
        body = re.sub(r'<header[^>]*>.*?</header>', '', body, flags=re.DOTALL)
        body = re.sub(r'<footer[^>]*>.*?</footer>', '', body, flags=re.DOTALL)

        # Extract page-specific style (from <style> in <head>)
        style_m = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
        page_style = style_m.group(1).strip() if style_m else ""

        # Extract desc from header
        desc = ""
        desc_m = re.search(r'<p class="report-header__desc">(.*?)</p>', html, re.DOTALL)
        if desc_m:
            desc = re.sub(r'<[^>]+>', '', desc_m.group(1)).strip()

        # Re-generate with latest template
        page_info = {
            "title": title,
            "desc": desc,
            "date": date_str,
            "category": category,
            "body": body,
            "style": page_style,
        }
        page_html = generate_page_html(page_info, SITE_URL)

        # Write back to same path
        fpath.write_text(page_html, "utf-8")
        updated += 1
        print(f"  ✅ {rel} — {title}")

    print(f"\n✅ 更新完成: {updated}/{len(html_files)} 个页面已重新生成")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python deploy.py deploy <category> <html_file> [--title T] [--desc D]")
        print("  python deploy.py add <filename> --title T --desc D --category C [--url U]")
        print("  python deploy.py rebuild_index")
        print("  python deploy.py scan [--ai]")
        print("  python deploy.py update")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "deploy":
        if len(sys.argv) < 4:
            print("❌ 用法: python deploy.py deploy <category> <html_file> [--title T] [--desc D]")
            sys.exit(1)
        category = sys.argv[2]
        html_file = sys.argv[3]
        title = desc = None
        i = 4
        while i < len(sys.argv):
            if sys.argv[i] == '--title' and i+1 < len(sys.argv): title = sys.argv[i+1]; i += 2
            elif sys.argv[i] == '--desc' and i+1 < len(sys.argv): desc = sys.argv[i+1]; i += 2
            else: i += 1
        deploy(category, html_file, title, desc)

    elif cmd == "add":
        if len(sys.argv) < 3:
            print("❌ 用法: python deploy.py add <filename> --title T --desc D --category C [--url U]")
            sys.exit(1)
        filename = sys.argv[2]
        title = desc = category = url = None
        i = 3
        while i < len(sys.argv):
            if sys.argv[i] == '--title' and i+1 < len(sys.argv): title = sys.argv[i+1]; i += 2
            elif sys.argv[i] == '--desc' and i+1 < len(sys.argv): desc = sys.argv[i+1]; i += 2
            elif sys.argv[i] == '--category' and i+1 < len(sys.argv): category = sys.argv[i+1]; i += 2
            elif sys.argv[i] == '--url' and i+1 < len(sys.argv): url = sys.argv[i+1]; i += 2
            else: i += 1
        if not title or not category:
            print("❌ --title 和 --category 是必须的")
            sys.exit(1)
        add_to_index(filename, title, desc, category, url)

    elif cmd == "rebuild_index":
        rebuild_index()

    elif cmd == "scan":
        scan_and_rebuild()

    elif cmd == "update":
        update_pages()

    else:
        print(f"❌ 未知命令: {cmd}")
