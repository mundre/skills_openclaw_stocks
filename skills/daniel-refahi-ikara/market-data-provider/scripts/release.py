#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[1]
SKILL_DIR = ROOT
VERSION_FILE = SKILL_DIR / "VERSION"
SMOKE_TEST = SKILL_DIR / "scripts" / "smoke_test.py"
PACKAGER = Path.home() / ".npm-global/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py"


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print("+", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Release market-data-provider")
    parser.add_argument("--version", help="Update VERSION before releasing")
    parser.add_argument("--skip-live", action="store_true", help="Skip live EODHD smoke test")
    args = parser.parse_args()

    if args.version:
        VERSION_FILE.write_text(args.version.strip() + "\n", encoding="utf-8")
        print(f"Updated version to {args.version.strip()}")

    run(["python3", str(SMOKE_TEST)], cwd=WORKSPACE)
    run(["env", "MARKET_DATA_PROVIDER=mock", "python3", str(SMOKE_TEST)], cwd=WORKSPACE)
    if not args.skip_live:
        run(["python3", str(SMOKE_TEST)], cwd=WORKSPACE)
    run(["python3", str(PACKAGER), str(SKILL_DIR)], cwd=WORKSPACE)
    print("Release checks complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
