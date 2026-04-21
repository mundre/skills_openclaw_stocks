"""配置加载、常量定义与工具函数"""

import json, re, sys, shutil
from pathlib import Path
from datetime import date

BASE_DIR = Path(__file__).parent.parent
DIST_DIR = BASE_DIR / "dist"

# ── 核心原则 ──
# 技能目录是唯一工作台。DIST_DIR 是技能 dist/，所有整理/索引/备份都在这里操作。
# 部署目录（REPORT_LOCAL_DIR）纯粹是同步目标，通过 sync_to_deploy() 推送。



# ── TOOLS.md 配置读取 ──
_TOOLS_PATH = Path.home() / ".openclaw/workspace/TOOLS.md"
_tools_text = _TOOLS_PATH.read_text("utf-8") if _TOOLS_PATH.exists() else ""

def _get(key):
    """Read a config value from TOOLS.md by key=value pattern."""
    m = re.search(rf'{key}=(.+)', _tools_text)
    if not m: return None
    v = m.group(1).strip()
    return v.strip().strip('`').strip() or None

def _get_cfg_val(key):
    """Alias for _get (backward compat)."""
    return _get(key)

# ── 1. 本地报告部署配置 ──
REPORT_LOCAL_DIR = _get("REPORT_LOCAL_DIR") or str(BASE_DIR)
REPORT_LOCAL_URL = (_get("REPORT_LOCAL_URL") or "/").rstrip("/")
REPORT_SITE_NAME = _get("REPORT_SITE_NAME") or "传琪"
REPORT_DEPLOY_MODE = _get("REPORT_DEPLOY_MODE") or "local"

# ── 2. 远程报告部署配置 ──
REPORT_CF_PROJECT = _get("REPORT_CF_PROJECT") or _get("CF_PROJECT_NAME")
REPORT_CF_ACCOUNT = _get("REPORT_CF_ACCOUNT")

# ── 3. 技能 CF 发布配置 ──
SKILL_CF_PROJECT = _get("SKILL_CF_PROJECT") or "report-expert-skill"
SKILL_CF_ACCOUNT = _get("SKILL_CF_ACCOUNT")

# ── 4. 技能 ClawHub 发布配置 ──
SKILL_CLAWHUB_SLUG = _get("SKILL_CLAWHUB_SLUG") or "report-expert"
SKILL_CLAWHUB_NAME = _get("SKILL_CLAWHUB_NAME") or "报告专家"

# ── 向后兼容 _CFG 字典 ──
_CFG = {
    "mode": REPORT_DEPLOY_MODE,
    "local_dir": REPORT_LOCAL_DIR,
    "local_url": REPORT_LOCAL_URL,
    "site_name": REPORT_SITE_NAME,
}

# ── 派生常量 ──
# 索引文件在技能 dist（工作台），deploy 时推到部署目录
INDEX_FILE = DIST_DIR / "index.json"
SITE_URL = REPORT_LOCAL_URL
SITE_NAME = REPORT_SITE_NAME


def sync_to_deploy(clean=False):
    """将技能 dist/ 同步到部署目录（local 模式的核心推送操作）。

    技能目录是唯一工作台，部署目录只是同步目标。
    clean=True 时会删除部署目录中不在 dist/ 里的文件。
    """
    deploy_root = Path(REPORT_LOCAL_DIR)
    if not DIST_DIR.exists():
        print(f"⚠️ 技能 dist 不存在: {DIST_DIR}")
        return 0
    count = 0
    for fpath in sorted(DIST_DIR.rglob("*")):
        if not fpath.is_file():
            continue
        rel = fpath.relative_to(DIST_DIR)
        dst = deploy_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists() or dst.stat().st_mtime < fpath.stat().st_mtime:
            shutil.copy2(fpath, dst)
            count += 1
    # 清理模式：删除部署目录中不在 dist/ 里的文件
    removed = 0
    if clean:
        for fpath in sorted(deploy_root.rglob("*")):
            if not fpath.is_file():
                continue
            rel = fpath.relative_to(deploy_root)
            if not (DIST_DIR / rel).exists():
                fpath.unlink()
                removed += 1
        # 清理空目录
        for d in sorted(deploy_root.rglob("*"), reverse=True):
            if d.is_dir() and not any(d.iterdir()):
                d.rmdir()
    if removed:
        print(f"  🗑️  清理: {removed} 个过期文件")
    return count

def get_report_cf_project():
    return REPORT_CF_PROJECT

def get_skill_cf_project():
    return SKILL_CF_PROJECT

def get_clawhub_slug():
    return SKILL_CLAWHUB_SLUG

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

def update_manifest_hashes(skill_dir=None):
    """Update file hashes and sizes in manifest.json. Returns version string."""
    skill_dir = skill_dir or BASE_DIR
    manifest_path = skill_dir / "manifest.json"
    if not manifest_path.exists():
        return None
    m = json.loads(manifest_path.read_text("utf-8"))
    ver = m.get("version", "0.0.0")
    for rel in list(m.get("files", {}).keys()):
        fp = skill_dir / rel
        if fp.exists():
            with open(fp, "rb") as f:
                m["files"][rel]["sha256"] = hashlib.sha256(f.read()).hexdigest()
                m["files"][rel]["size"] = fp.stat().st_size
    manifest_path.write_text(json.dumps(m, ensure_ascii=False, indent=2), "utf-8")
    return ver

import hashlib  # for update_manifest_hashes
