#!/usr/bin/env python3
"""
生成符合规范的 Git commit message。

用法：
  python3 commit_msg.py <title> [type]
  type: post/feat/fix/docs（默认 post）

输出：
  <type>: <标题>
"""

import sys

TYPE_MAP = {
    "post":   "post",
    "feat":   "feat",
    "fix":    "fix",
    "docs":   "docs",
    "refactor": "refactor",
}

def main():
    if len(sys.argv) < 2:
        print("Usage: commit_msg.py <title> [type]")
        sys.exit(1)

    title = sys.argv[1]
    type_ = sys.argv[2] if len(sys.argv) > 2 else "post"

    prefix = TYPE_MAP.get(type_, "post")
    print(f"{prefix}: {title}")

if __name__ == "__main__":
    main()
