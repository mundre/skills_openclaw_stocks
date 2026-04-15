#!/usr/bin/env python3

from __future__ import annotations

import os
import sys
from pathlib import Path


def _has_output_dir_override(argv: list[str]) -> bool:
    return any(item == "--output-dir" or item.startswith("--output-dir=") for item in argv)


def _workspace_output_dir(skill_root: Path, output_slug: str) -> str | None:
    if skill_root.parent.name == "skills" and skill_root.parent.parent.name == "workspace":
        workspace_root = skill_root.parent.parent
        return str((workspace_root / "outputs" / output_slug).resolve())
    return None


def run_profile(*, active_skill: str, default_args: list[str], output_slug: str | None = None) -> int:
    skill_root = Path(__file__).resolve().parent
    user_args = sys.argv[1:]
    merged_args = list(default_args)

    if output_slug and not _has_output_dir_override(user_args):
        workspace_output = _workspace_output_dir(skill_root, output_slug)
        if workspace_output:
            merged_args.extend(["--output-dir", workspace_output])

    if str(skill_root) not in sys.path:
        sys.path.insert(0, str(skill_root))

    os.environ.setdefault("GIGO_ACTIVE_SKILL", active_skill)
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

    import main as runtime_main

    return runtime_main.main(merged_args + user_args)
