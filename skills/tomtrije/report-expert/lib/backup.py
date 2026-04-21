"""备份恢复与页面模板更新"""

import re, sys, shutil
from pathlib import Path
from datetime import datetime, timedelta

from lib.config import DIST_DIR, SITE_URL, strip_emoji, sync_to_deploy
from lib.page import generate_page_html

def _backup_dist():
    """Backup dist/ before update. Keep backups for 7 days."""
    backup_root = DIST_DIR.parent / "backups"
    backup_root.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = backup_root / ts
    if DIST_DIR.exists():
        shutil.copytree(DIST_DIR, backup_dir)
        print(f"📦 备份已创建: {backup_dir.relative_to(DIST_DIR.parent)}")
    else:
        backup_dir.mkdir(parents=True)
        print(f"📦 空备份已创建: {backup_dir.relative_to(DIST_DIR.parent)}")
    # Clean up backups older than 7 days
    cutoff = datetime.now() - timedelta(days=7)
    removed = 0
    for d in backup_root.iterdir():
        if d.is_dir():
            try:
                dt = datetime.strptime(d.name, "%Y%m%d_%H%M%S")
                if dt < cutoff:
                    shutil.rmtree(d)
                    removed += 1
            except ValueError:
                pass
    if removed:
        print(f"🗑️  已清理 {removed} 个过期备份（>7天）")


def _restore_backup(backup_name=None):
    """Restore from a backup. If no name, list available backups."""
    backup_root = DIST_DIR.parent / "backups"
    if not backup_root.exists():
        print("❌ 没有备份目录"); return
    backups = sorted([d for d in backup_root.iterdir() if d.is_dir()], reverse=True)
    if not backups:
        print("❌ 没有可用备份"); return
    if not backup_name:
        print("📋 可用备份:")
        for d in backups:
            print(f"  {d.name}")
        return
    target = backup_root / backup_name
    if not target.exists():
        print(f"❌ 备份不存在: {backup_name}"); return
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    shutil.copytree(target, DIST_DIR)
    print(f"✅ 已从备份 {backup_name} 恢复")


def update_pages():
    """Re-wrap all report pages with the latest template and styles.

    Scans dist/ for HTML pages (excluding index.html), extracts body content
    and style, then re-generates each page using generate_page_html.
    Backs up dist/ before updating.
    """
    from datetime import date

    dist = DIST_DIR
    if not dist.exists():
        print(f"❌ dist 目录不存在: {dist}"); sys.exit(1)

    _backup_dist()

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
        # Extract body content between page-body and footer
        # Use non-greedy match, then strip trailing wrapper closings
        body_m = re.search(r'<div class="page-body"[^>]*>(.*?)<footer', html, re.DOTALL)
        if not body_m:
            print(f"  ⏭️  {rel} — 无法提取内容，跳过")
            continue
        body = body_m.group(1).strip()
        # Remove trailing </div>s that close report-wrap/page-body wrappers
        body = body.rstrip()
        while body.endswith('</div>'):
            body = body[:-6].rstrip()
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

    # 推送到部署目录
    synced = sync_to_deploy()
    if synced:
        print(f"   同步: {synced} 个文件推送到部署目录")
