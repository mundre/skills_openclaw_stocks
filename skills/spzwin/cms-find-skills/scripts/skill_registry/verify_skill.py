#!/usr/bin/env python3
"""
verify_skill.py — Skill 目录结构校验

校验项：
  1. 目录存在
  2. SKILL.md 存在且非空
  3. SKILL.md 含 YAML frontmatter，包含 name 和 description 字段
  4. 若有 scripts/，python 文件可 py_compile

使用方式：
  python3 verify_skill.py /path/to/skill-dir
  python3 verify_skill.py /path/to/skill-dir --json
"""

from __future__ import annotations

import argparse
import json
import os
import py_compile
import re
import sys
from typing import List


REQUIRED_FIELDS = ("name", "description")


def _read_frontmatter(skill_md_path: str) -> dict:
    with open(skill_md_path, "r", encoding="utf-8") as f:
        text = f.read()
    if not text.startswith("---"):
        raise ValueError("SKILL.md 缺少 YAML frontmatter")
    end = text.find("\n---", 3)
    if end < 0:
        raise ValueError("SKILL.md frontmatter 未闭合")
    front = text[3:end].strip()
    data: dict = {}
    for line in front.splitlines():
        m = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", line)
        if m:
            data[m.group(1)] = m.group(2).strip()
    return data


def verify(skill_dir: str) -> dict:
    errors: List[str] = []
    warnings: List[str] = []

    if not os.path.isdir(skill_dir):
        return {"success": False, "errors": [f"目录不存在: {skill_dir}"], "warnings": []}

    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(skill_md) or os.path.getsize(skill_md) == 0:
        errors.append("缺少或空白的 SKILL.md")
    else:
        try:
            front = _read_frontmatter(skill_md)
            for field in REQUIRED_FIELDS:
                if not front.get(field):
                    errors.append(f"SKILL.md frontmatter 缺少字段: {field}")
        except Exception as exc:
            errors.append(f"SKILL.md 解析失败: {exc}")

    scripts_dir = os.path.join(skill_dir, "scripts")
    if os.path.isdir(scripts_dir):
        for root, _dirs, files in os.walk(scripts_dir):
            for name in files:
                if name.endswith(".py"):
                    path = os.path.join(root, name)
                    try:
                        py_compile.compile(path, doraise=True)
                    except py_compile.PyCompileError as exc:
                        errors.append(f"Python 脚本编译失败: {path}: {exc.msg}")

    return {
        "success": not errors,
        "skill_dir": os.path.abspath(skill_dir),
        "errors": errors,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="校验 Skill 目录结构")
    parser.add_argument("skill_dir", help="待校验的 Skill 目录")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    result = verify(args.skill_dir)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result["success"]:
            print(f"✅ Skill 目录校验通过: {result['skill_dir']}")
        else:
            print(f"❌ Skill 目录校验失败: {result['skill_dir']}")
            for err in result["errors"]:
                print(f"  - {err}")

    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
