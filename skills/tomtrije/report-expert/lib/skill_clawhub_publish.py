"""技能发布到 ClawHub registry"""

import json, subprocess, sys
from pathlib import Path

from lib.config import BASE_DIR, get_clawhub_slug, get_clawhub_slug as _get_slug, update_manifest_hashes
from lib.skill_cf_publish import _sync_version


def publish_to_clawhub(version=None, changelog=""):
    """Publish skill to ClawHub registry via `clawhub publish` CLI.

    Args:
        version: Optional version string (auto-bumps if None).
        changelog: Changelog message for this release.
    """
    skill_dir = BASE_DIR
    slug = get_clawhub_slug()
    manifest_path = skill_dir / "manifest.json"

    # Bump version if not specified
    if version is None and manifest_path.exists():
        m = json.loads(manifest_path.read_text("utf-8"))
        ver = m.get("version", "0.0.0")
        parts = ver.split(".")
        parts[-1] = str(int(parts[-1]) + 1)
        version = ".".join(parts)
        m["version"] = version
        manifest_path.write_text(json.dumps(m, ensure_ascii=False, indent=2), "utf-8")
        update_manifest_hashes(skill_dir)
        print(f"🔄 版本自动升级: v{version}")

    # Sync version and regenerate index.html
    _sync_version(skill_dir, version)

    import shutil, tempfile

    print(f"📦 发布到 ClawHub: {slug} v{version}")

    # Temporarily exclude dist/ and backups/ to stay under 20MB limit
    exclude_dirs = ["dist", "backups"]
    moved = []
    for d in exclude_dirs:
        p = skill_dir / d
        if p.is_dir():
            tmp = Path(tempfile.mkdtemp()) / d
            shutil.move(str(p), str(tmp))
            moved.append((tmp, p))
            print(f"  ⏳ 临时移除 {d}/")

    try:
        # Build clawhub publish command
        cmd = ["clawhub", "publish", str(skill_dir)]
        if version:
            cmd.extend(["--version", version])
        if changelog:
            cmd.extend(["--changelog", changelog])

        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
            print("❌ ClawHub 发布失败")
            sys.exit(1)
        else:
            print(f"✅ ClawHub 发布成功: {slug} v{version}")
    finally:
        for tmp, orig in moved:
            shutil.move(str(tmp), str(orig))
            print(f"  ✅ 已恢复 {orig.name}/")
