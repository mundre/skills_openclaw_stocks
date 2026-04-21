"""本地部署：在技能 dist/ 工作完成后同步到部署目录"""

import re, sys, shutil
from pathlib import Path
from datetime import date

from lib.config import (SITE_NAME, REPORT_LOCAL_DIR, BASE_DIR,
                        DIST_DIR, load_index, save_index, strip_emoji, sync_to_deploy)
from lib.page import generate_page_html


def copy_assets():
    """将技能模板/脚本的最新版本同步到技能 dist/。

    技能目录是 source of truth，dist/ 是工作台副本。
    templates/base.css → DIST_DIR/styles/base.css
    scripts/main.js   → DIST_DIR/scripts/main.js
    """
    asset_map = {
        BASE_DIR / "templates" / "base.css": DIST_DIR / "styles" / "base.css",
        BASE_DIR / "scripts" / "main.js": DIST_DIR / "scripts" / "main.js",
    }
    updated = 0
    for src, dst in asset_map.items():
        if not src.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists() or dst.read_bytes() != src.read_bytes():
            shutil.copy2(src, dst)
            updated += 1
            print(f"  📄 {dst.relative_to(DIST_DIR)}")
    if updated:
        print(f"  ✅ 已同步 {updated} 个静态资源")
    return updated


def deploy(category, html_file, title=None, desc=None):
    """Deploy a report page.

    流程：技能 dist/ 工作台处理 → sync_to_deploy() 推送到部署目录。
    1. 生成页面写入 DIST_DIR/category/
    2. copy_assets() 同步最新样式到 DIST_DIR
    3. 更新 DIST_DIR/index.json
    4. sync_to_deploy() 推到部署目录
    """
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

    # 从 body 中移除已提取的 style 标签
    body = re.sub(r'<style>.*?</style>', '', body, flags=re.DOTALL).strip()

    # ── 清理内容中多余的框架嵌套 ──
    body = re.sub(r'<header[^>]*>.*?</header>', '', body, flags=re.DOTALL)
    body = re.sub(r'<footer[^>]*>.*?</footer>', '', body, flags=re.DOTALL)
    body = re.sub(r'<h1[^>]*>.*?</h1>', '', body, flags=re.DOTALL)
    body = re.sub(r'<button[^>]*back-to-top[^>]*>.*?</button>', '', body, flags=re.DOTALL)
    body = re.sub(r'<div[^>]*class="scroll-progress"[^>]*></div>', '', body)
    body = re.sub(r'<aside[^>]*class="toc-sidebar"[^>]*>.*?</aside>', '', body, flags=re.DOTALL)
    body = re.sub(r'<button[^>]*class="toc-toggle"[^>]*>.*?</button>', '', body, flags=re.DOTALL)
    body = re.sub(r'<script[^>]*main\.js[^>]*></script>', '', body)

    changed = True
    while changed:
        changed = False
        for cls in ['report-wrap', 'page-body', 'wrap']:
            m = re.search(rf'^\s*<div class="{cls}"[^>]*>\s*(.*)\s*</div>\s*$', body, re.DOTALL)
            if m:
                body = m.group(1).strip()
                changed = True
            else:
                body = re.sub(rf'<div class="{cls}"[^>]*>\s*</div>', '', body)

    # ── 强制校验（清理之后）──
    div_open = len(re.findall(r'<div[\s>]', body))
    div_close = body.count('</div>')
    if div_open != div_close:
        print(f"❌ div 不平衡: <div>={div_open} </div>={div_close}，部署中止")
        sys.exit(1)
    if body.count('class="report-wrap"') > 1:
        c = body.count('class="report-wrap"'); print(f"❌ 重复 report-wrap ({c}个)，部署中止")
        sys.exit(1)
    if body.count('class="page-body"') > 1:
        c = body.count('class="page-body"'); print(f"❌ 重复 page-body ({c}个)，部署中止")
        sys.exit(1)

    if not title:
        title_match = re.search(r'<title>(.*?)</title>', html)
        title = title_match.group(1) if title_match else src.stem

    data = load_index()
    base_url = data["site"].get("baseUrl", SITE_NAME)
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

    # ── 1. 写入技能 dist（工作台）──
    cat_dir = DIST_DIR / category
    cat_dir.mkdir(parents=True, exist_ok=True)
    with open(cat_dir / filename, "w", encoding="utf-8") as f:
        f.write(page_html)

    # ── 2. 同步静态资源到技能 dist ──
    copy_assets()

    # ── 3. 更新技能 dist 的索引（去重：同标题则覆盖）──
    page_url = f"{base_url}/{category}/{filename}"
    new_entry = {
        "filename": filename,
        "title": title,
        "desc": desc or "",
        "date": today,
        "category": category,
        "url": page_url,
    }
    # 按标题去重：同标题覆盖旧条目，不同标题追加
    replaced = False
    for i, p in enumerate(data["pages"]):
        if p.get("title") == title:
            old_file = p.get("filename", "")
            data["pages"][i] = new_entry
            replaced = True
            if old_file != filename:
                print(f"  🔄 索引去重: 覆盖同名条目 ({old_file} → {filename})")
            break
    if not replaced:
        data["pages"].append(new_entry)
    save_index(data)

    # ── 4. 推送到部署目录 ──
    synced = sync_to_deploy()

    print(f"✅ 部署成功")
    print(f"   标题: {title}")
    print(f"   日期: {today}")
    print(f"   工作台: dist/{category}/{filename}")
    print(f"   链接: {page_url}")
    if synced:
        print(f"   同步: {synced} 个文件推送到部署目录")
