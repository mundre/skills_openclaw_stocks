#!/usr/bin/env python3
"""
生成博客文章 Front Matter 和文件名。

用法：
  python3 new_post.py <title> [--topic TOPIC] [--date DATE] [--dry-run]

参数：
  title       文章标题
  --topic     专题分类 (ai/devops/frontend/backend/tools/arch)
  --date      日期 YYYY-MM-DD（默认今天，自动生成 19-23:59:59 随机时间）
  --dry-run   仅显示生成的 front matter，不写入文件

输出：
  生成 front matter 并写入 hexo 文章文件
"""

import sys
import random
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# 专题配置
TOPIC_CONFIG = {
    "ai":        {"categories": ["AI", "LLM"], "tags": ["LLM", "AI"]},
    "devops":    {"categories": ["运维", "DevOps"], "tags": ["Linux", "Docker"]},
    "frontend":  {"categories": ["前端"], "tags": ["TypeScript", "JavaScript"]},
    "backend":   {"categories": ["后端"], "tags": ["Python", "Java"]},
    "tools":     {"categories": ["工具"], "tags": ["CLI", "效率"]},
    "arch":      {"categories": ["架构"], "tags": ["架构", "微服务"]},
    "db":        {"categories": ["数据库"], "tags": ["Redis", "MySQL"]},
}

POSTS_DIR = Path("/Users/nora/workspace/astralwaveorg/source/_posts")


def generate_random_time(date_str: str) -> str:
    """生成 19:00:00 - 23:59:59 之间的随机时间"""
    base = datetime.strptime(date_str, "%Y-%m-%d")

    # 随机小时 19-23
    hour = random.randint(19, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)

    rand_time = base.replace(hour=hour, minute=minute, second=second)
    return rand_time.strftime("%Y-%m-%d %H:%M:%S")


def slugify(title: str) -> str:
    """将标题转换为适合文件名的 slug"""
    import re
    # 中文标题保留，英文转小写空格变-
    slug = title.lower()
    slug = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    return slug


def generate_frontmatter(title: str, topic: str, date_str: str, description: str = "") -> str:
    """生成 Hexo front matter"""

    config = TOPIC_CONFIG.get(topic, TOPIC_CONFIG["tools"])
    rand_date = generate_random_time(date_str)

    # 生成 tags（取前3个）
    tags = config["tags"][:3]

    fm = f"""---
topic: {topic}
title: {title}
date: {rand_date}
categories:
  - {config["categories"][0]}
tags:
  - {tags[0]}
description: {description or title}
---"""
    return fm


def create_post_file(title: str, topic: str, date_str: str, description: str = "") -> Path:
    """创建博客文章文件"""
    slug = slugify(title)
    date_part = date_str.replace("-", "")

    filename = f"{date_part}-{slug}.md"
    filepath = POSTS_DIR / filename

    if filepath.exists():
        print(f"文件已存在: {filepath}")
        return filepath

    fm = generate_frontmatter(title, topic, date_str, description)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(fm)
        f.write("\n\n")
        f.write(f"# {title}\n")

    print(f"✅ 已创建: {filepath}")
    print(fm)
    return filepath


def main():
    parser = argparse.ArgumentParser(description="生成 Hexo 博客文章")
    parser.add_argument("title", help="文章标题")
    parser.add_argument("--topic", default="tools", help=f"专题: {', '.join(TOPIC_CONFIG.keys())}")
    parser.add_argument("--date", default=None, help="日期 YYYY-MM-DD（默认今天）")
    parser.add_argument("--desc", default="", help="文章描述")
    parser.add_argument("--dry-run", action="store_true", help="仅显示，不写入")
    parser.add_argument("--datetime", default=None, help="完整日期时间（覆盖 --date）")

    args = parser.parse_args()

    date_str = args.date or datetime.now().strftime("%Y-%m-%d")

    if args.datetime:
        # 直接使用指定的完整时间（小时已是19-23）
        date_str = args.datetime

    if args.dry_run:
        print(generate_frontmatter(args.title, args.topic, date_str, args.desc))
    else:
        create_post_file(args.title, args.topic, date_str, args.desc)


if __name__ == "__main__":
    main()
