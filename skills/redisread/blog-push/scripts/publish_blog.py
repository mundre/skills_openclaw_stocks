#!/usr/bin/env python3
"""
Hugo 博客文章发布脚本
将 Markdown 文档和封面图发布到 Hugo 博客

支持环境变量配置：
- HUGO_BLOG_DIR: 博客项目根目录
- HUGO_POSTS_DIR: posts 目录相对路径（默认: content/zh/posts）
- HUGO_TEMPLATE_PATH: 模板文件相对路径（默认: archetypes/default.md）

优先级：命令行参数 > 环境变量 > 默认值
"""

import os
import sys
import shutil
import datetime
import argparse
from pathlib import Path


ENV_BLOG_DIR = "HUGO_BLOG_DIR"
ENV_POSTS_DIR = "HUGO_POSTS_DIR"
ENV_TEMPLATE_PATH = "HUGO_TEMPLATE_PATH"
DEFAULT_POSTS_DIR = "content/zh/posts"
DEFAULT_TEMPLATE = "archetypes/default.md"


def validate_hugo_project(blog_dir: str) -> bool:
    """验证是否为有效的 Hugo 项目"""
    blog_path = Path(blog_dir)
    if not blog_path.exists():
        return False

    config_files = [
        "config.toml",
        "config.yaml",
        "config.yml",
        "config.json",
    ]

    for config_file in config_files:
        if (blog_path / config_file).exists():
            return True

    if (blog_path / "config").exists():
        return True

    return False


def resolve_paths(args) -> tuple:
    """
    解析路径配置
    优先级：命令行参数 > 环境变量 > 默认值

    返回：(blog_dir, posts_dir, template_path, sources)
    """
    sources = {}

    blog_dir = args.blog_dir if args.blog_dir else os.environ.get(ENV_BLOG_DIR, ".")
    sources["blog_dir"] = (
        "命令行参数"
        if args.blog_dir
        else ("环境变量" if os.environ.get(ENV_BLOG_DIR) else "默认值(当前目录)")
    )

    if args.posts_dir:
        posts_dir = args.posts_dir
        sources["posts_dir"] = "命令行参数"
    else:
        relative_posts = os.environ.get(ENV_POSTS_DIR, DEFAULT_POSTS_DIR)
        posts_dir = os.path.join(blog_dir, relative_posts)
        sources["posts_dir"] = "环境变量" if os.environ.get(ENV_POSTS_DIR) else "默认值"

    if args.template:
        template_path = args.template
        sources["template"] = "命令行参数"
    else:
        relative_template = os.environ.get(ENV_TEMPLATE_PATH, DEFAULT_TEMPLATE)
        template_path = os.path.join(blog_dir, relative_template)
        sources["template"] = (
            "环境变量" if os.environ.get(ENV_TEMPLATE_PATH) else "默认值"
        )

    return blog_dir, posts_dir, template_path, sources


def display_config(blog_dir: str, posts_dir: str, template_path: str, sources: dict):
    """显示当前配置信息"""
    print("\n✓ Hugo 博客配置信息")
    print("=" * 60)
    print(f"博客根目录: {blog_dir}")
    print(f"  来源: {sources['blog_dir']}")

    blog_valid = validate_hugo_project(blog_dir)
    if blog_valid:
        print(f"  状态: ✓ 有效 (检测到 Hugo 配置文件)")
    else:
        print(f"  状态: ✗ 无效 (未检测到 Hugo 配置文件)")

    print(f"\nposts 目录: {posts_dir}")
    print(f"  来源: {sources['posts_dir']}")

    posts_path = Path(posts_dir)
    if posts_path.exists():
        print(f"  状态: ✓ 存在")
    else:
        print(f"  状态: ✗ 不存在")

    print(f"\n模板路径: {template_path}")
    print(f"  来源: {sources['template']}")

    template_file = Path(template_path)
    if template_file.exists():
        print(f"  状态: ✓ 存在")
    else:
        print(f"  状态: ✗ 不存在")

    print("=" * 60)

    print("\n环境变量配置:")
    print(f"  {ENV_BLOG_DIR}: {os.environ.get(ENV_BLOG_DIR, '(未设置)')}")
    print(f"  {ENV_POSTS_DIR}: {os.environ.get(ENV_POSTS_DIR, '(未设置)')}")
    print(f"  {ENV_TEMPLATE_PATH}: {os.environ.get(ENV_TEMPLATE_PATH, '(未设置)')}")


def get_posts_categories(posts_dir: str) -> list:
    """获取 posts 目录下的所有分类目录"""
    categories = []
    posts_path = Path(posts_dir)

    if not posts_path.exists():
        print(f"错误: posts 目录不存在: {posts_dir}")
        sys.exit(1)

    for item in posts_path.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            categories.append(item.name)

    return sorted(categories)


def display_categories(categories: list):
    """显示所有分类"""
    print("\n可用的博客分类目录:")
    print("=" * 50)
    for i, category in enumerate(categories, 1):
        print(f"{i}. {category}")
    print("=" * 50)


def validate_category(category: str, categories: list) -> bool:
    """验证分类是否存在"""
    return category in categories


def get_current_time() -> str:
    """获取当前时间，格式为 Hugo 需要的格式"""
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%dT%H:%M:%S+08:00")


def sanitize_filename(name: str) -> str:
    """清理文件名，替换特殊字符"""
    name = name.replace(" ", "-")
    name = "".join(c for c in name if c.isalnum() or c in "-_")
    return name.lower()


def read_template(template_path: str) -> str:
    """读取模板文件"""
    template_file = Path(template_path)

    if not template_file.exists():
        print(f"错误: 模板文件不存在: {template_path}")
        sys.exit(1)

    with open(template_file, "r", encoding="utf-8") as f:
        return f.read()


def process_frontmatter(template: str, title: str, current_time: str) -> str:
    """处理 front matter，替换标题和时间"""
    lines = template.split("\n")
    processed_lines = []
    in_frontmatter = False

    for line in lines:
        if line.strip() == "---":
            in_frontmatter = not in_frontmatter
            processed_lines.append(line)
            continue

        if in_frontmatter:
            if line.startswith("title:"):
                processed_lines.append(f'title: "{title}"')
            elif line.startswith("date:"):
                processed_lines.append(f"date: {current_time}")
            elif line.startswith("publishDate:"):
                processed_lines.append(f"publishDate: {current_time}")
            else:
                processed_lines.append(line)
        else:
            processed_lines.append(line)

    return "\n".join(processed_lines)


def copy_cover_image(cover_path: str, target_dir: str, article_name: str) -> str:
    """复制封面图到目标目录"""
    if not cover_path or not Path(cover_path).exists():
        return ""

    cover_file = Path(cover_path)
    ext = cover_file.suffix
    target_filename = f"{article_name}-cover{ext}"
    target_path = Path(target_dir) / target_filename

    shutil.copy2(cover_file, target_path)
    print(f"✓ 封面图已复制到: {target_path}")

    return target_filename


def read_markdown_content(md_path: str) -> str:
    """读取 Markdown 文件内容"""
    md_file = Path(md_path)

    if not md_file.exists():
        print(f"错误: Markdown 文件不存在: {md_path}")
        sys.exit(1)

    with open(md_file, "r", encoding="utf-8") as f:
        return f.read()


def extract_content_without_frontmatter(content: str) -> str:
    """提取内容，去除原有的 front matter"""
    lines = content.split("\n")
    content_lines = []
    skip_frontmatter = False
    frontmatter_count = 0

    for line in lines:
        if line.strip() == "---":
            frontmatter_count += 1
            if frontmatter_count <= 2:
                skip_frontmatter = True
                continue
            else:
                skip_frontmatter = False

        if not skip_frontmatter:
            content_lines.append(line)

    return "\n".join(content_lines)


def create_article(
    template_path: str,
    md_path: str,
    posts_dir: str,
    category: str,
    article_name: str,
    cover_path: str = None,
    draft: bool = False,
):
    """创建博客文章"""
    category_dir = Path(posts_dir) / category
    if not category_dir.exists():
        print(f"创建新分类目录: {category}")
        category_dir.mkdir(parents=True, exist_ok=True)

    article_file = category_dir / f"{article_name}.md"

    if article_file.exists():
        print(f"警告: 文章已存在，将被覆盖: {article_file}")

    template = read_template(template_path)
    current_time = get_current_time()
    processed_template = process_frontmatter(template, article_name, current_time)

    if draft:
        lines = processed_template.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("draft:"):
                lines[i] = "draft: true"
        processed_template = "\n".join(lines)

    md_content = read_markdown_content(md_path)
    article_body = extract_content_without_frontmatter(md_content)

    cover_filename = ""
    if cover_path:
        cover_filename = copy_cover_image(cover_path, str(category_dir), article_name)
        lines = processed_template.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("image:"):
                lines[i] = f"image: {cover_filename}"
        processed_template = "\n".join(lines)

    final_content = processed_template + "\n\n" + article_body

    with open(article_file, "w", encoding="utf-8") as f:
        f.write(final_content)

    print(f"\n✅ 文章已成功创建!")
    print(f"   位置: {article_file}")
    print(f"   标题: {article_name}")
    print(f"   分类: {category}")
    if cover_filename:
        print(f"   封面: {cover_filename}")

    return str(article_file)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Hugo 博客文章发布工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
环境变量配置:
  HUGO_BLOG_DIR       博客项目根目录（完整路径）
  HUGO_POSTS_DIR      posts 目录相对路径（默认: content/zh/posts）
  HUGO_TEMPLATE_PATH  模板文件相对路径（默认: archetypes/default.md）

优先级: 命令行参数 > 环境变量 > 默认值

示例:
  # 设置环境变量（推荐在 ~/.zshrc 中配置）
  export HUGO_BLOG_DIR=/path/to/your/hugo/blog
  
  # 查看配置信息
  %(prog)s --check-config
  
  # 查看可用分类
  %(prog)s --list-categories
  
  # 从任意位置发布文章（需设置环境变量）
  %(prog)s --md ~/Downloads/my-article.md --category 技术
  
  # 临时指定博客目录
  %(prog)s --md ./article.md --category AI --blog-dir /path/to/blog
  
  # 发布文章并设置封面
  %(prog)s --md ./my-article.md --cover ./cover.png --category AI
  
  # 发布为草稿
  %(prog)s --md ./draft.md --category 思考 --draft
        """,
    )

    parser.add_argument(
        "--check-config", action="store_true", help="检查并显示当前配置信息"
    )

    parser.add_argument(
        "--list-categories", "-l", action="store_true", help="显示所有可用的分类目录"
    )

    parser.add_argument("--md", "-m", help="Markdown 文件路径")

    parser.add_argument("--cover", "-c", help="封面图片路径")

    parser.add_argument("--category", "-cat", help="博客分类目录名称")

    parser.add_argument("--name", "-n", help="文章名称（默认使用 Markdown 文件名）")

    parser.add_argument("--draft", "-d", action="store_true", help="将文章标记为草稿")

    parser.add_argument(
        "--blog-dir",
        help="Hugo 博客项目根目录（完整路径），优先级高于环境变量 HUGO_BLOG_DIR",
    )

    parser.add_argument(
        "--posts-dir", help="posts 目录完整路径，优先级高于环境变量 HUGO_POSTS_DIR"
    )

    parser.add_argument(
        "--template", help="模板文件完整路径，优先级高于环境变量 HUGO_TEMPLATE_PATH"
    )

    args = parser.parse_args()

    blog_dir, posts_dir, template_path, sources = resolve_paths(args)

    if args.check_config:
        display_config(blog_dir, posts_dir, template_path, sources)
        sys.exit(0)

    categories = get_posts_categories(posts_dir)

    if args.list_categories:
        display_categories(categories)
        sys.exit(0)

    if not args.md:
        print("错误: 必须指定 Markdown 文件路径 (--md)")
        parser.print_help()
        sys.exit(1)

    if not args.category:
        print("错误: 必须指定分类目录 (--category)")
        display_categories(categories)
        sys.exit(1)

    if not validate_category(args.category, categories):
        print(f"错误: 分类 '{args.category}' 不存在")
        display_categories(categories)
        sys.exit(1)

    if args.name:
        article_name = sanitize_filename(args.name)
    else:
        md_file = Path(args.md)
        article_name = sanitize_filename(md_file.stem)

    create_article(
        template_path=template_path,
        md_path=args.md,
        posts_dir=posts_dir,
        category=args.category,
        article_name=article_name,
        cover_path=args.cover,
        draft=args.draft,
    )


if __name__ == "__main__":
    main()
