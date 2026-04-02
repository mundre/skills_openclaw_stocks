---
name: blog-publisher
description: Hugo 博客文章发布工具。将 Markdown 文档和封面图发布到 Hugo 博客系统。使用场景：(1) 用户需要发布博客文章到 Hugo，(2) "发布文章"、"publish blog"、"创建博客"，(3) 将完成的 Markdown 文档移动到 posts 目录。支持查看分类、选择目录、自动生成 front matter、处理封面图、草稿管理、环境变量配置、从任意目录执行。
---

# Hugo 博客文章发布技能

本技能用于将 Markdown 文档和封面图发布到 Hugo 博客系统，支持从任意目录执行发布操作。

## 核心功能

1. **环境变量配置** - 通过环境变量配置博客路径，从任意位置执行
2. **查看分类目录** - 列出所有可用的博客分类
3. **发布文章** - 将 Markdown 文档复制到指定分类目录
4. **处理封面图** - 自动复制封面图并更新 front matter
5. **生成 front matter** - 基于 Hugo 模板自动生成元数据
6. **草稿管理** - 支持将文章标记为草稿

## 环境变量配置

### 配置方式

在 shell 配置文件中设置环境变量：

```bash
# ~/.zshrc 或 ~/.bashrc
export HUGO_BLOG_DIR=/Users/victor/Desktop/Projects/github/HUGO_blog
export HUGO_POSTS_DIR=content/zh/posts  # 可选，默认值
export HUGO_TEMPLATE_PATH=archetypes/default.md  # 可选，默认值
```

### 环境变量说明

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `HUGO_BLOG_DIR` | 博客项目根目录（完整路径） | 当前目录 `.` |
| `HUGO_POSTS_DIR` | posts 目录相对路径 | `content/zh/posts` |
| `HUGO_TEMPLATE_PATH` | 模板文件相对路径 | `archetypes/default.md` |

### 路径优先级

**命令行参数 > 环境变量 > 默认值**

优先级逻辑：
1. 命令行参数（如 `--blog-dir`）优先级最高
2. 环境变量（如 `HUGO_BLOG_DIR`）次之
3. 默认值优先级最低

## 使用方法

### 检查配置信息

```bash
python3 scripts/publish_blog.py --check-config
```

输出示例：
```
✓ Hugo 博客配置信息
============================================================
博客根目录: /Users/victor/Desktop/Projects/github/HUGO_blog
  来源: 环境变量
  状态: ✓ 有效 (检测到 Hugo 配置文件)

posts 目录: /Users/victor/Desktop/Projects/github/HUGO_blog/content/zh/posts
  来源: 默认值
  状态: ✓ 存在

模板路径: /Users/victor/Desktop/Projects/github/HUGO_blog/archetypes/default.md
  来源: 默认值
  状态: ✓ 存在
============================================================

环境变量配置:
  HUGO_BLOG_DIR: /Users/victor/Desktop/Projects/github/HUGO_blog
  HUGO_POSTS_DIR: (未设置)
  HUGO_TEMPLATE_PATH: (未设置)
```

### 查看可用分类

```bash
python3 scripts/publish_blog.py --list-categories
```

这将显示 `content/zh/posts/` 下的所有分类目录：
- AI
- AI编程
- 产品故事
- 专业领域
- 书籍
- 工具折腾
- 思考
- 技术
- 技术实践
- 生活
- tech

### 从任意目录发布文章

**设置环境变量后（推荐）：**

```bash
# 设置环境变量
export HUGO_BLOG_DIR=/Users/victor/Desktop/Projects/github/HUGO_blog

# 从任意位置执行发布
cd ~/Downloads/workspace
python3 ~/.config/opencode/skills/blog-publisher/scripts/publish_blog.py \
  --md ./my-article.md \
  --category 技术
```

**临时指定博客目录：**

```bash
python3 scripts/publish_blog.py \
  --md ./my-article.md \
  --category 技术 \
  --blog-dir /Users/victor/Desktop/Projects/github/HUGO_blog
```

### 带封面图发布

```bash
python3 scripts/publish_blog.py \
  --md ./workspace/my-article.md \
  --cover ./images/cover.png \
  --category AI
```

封面图会被复制到文章所在目录，文件名格式为 `{文章名}-cover.{扩展名}`。

### 发布为草稿

```bash
python3 scripts/publish_blog.py \
  --md ./workspace/draft.md \
  --category 思考 \
  --draft
```

草稿文章的 `draft` 字段会被设置为 `true`，不会在博客中显示。

### 自定义文章名

```bash
python3 scripts/publish_blog.py \
  --md ./workspace/my-article.md \
  --name "我的自定义标题" \
  --category 技术
```

## Front Matter 处理

脚本会自动处理 Hugo 的 front matter：

1. **标题** - 使用文章名称或自定义名称
2. **日期** - 自动生成当前时间（格式：`YYYY-MM-DDTHH:MM:SS+08:00`）
3. **封面图** - 如果提供封面，自动填充 `image` 字段
4. **草稿状态** - 根据 `--draft` 参数设置

### 默认模板

模板位于 `archetypes/default.md`，包含以下字段：

```yaml
---
title: "{{ 文章标题 }}"
subtitle: 
date: {{ 自动生成 }}
publishDate: {{ 自动生成 }}
aliases:
description:
image: {{ 封面图（如果有） }}
draft: false
hideToc: false
enableToc: true
enableTocContent: false
tocPosition: inner
author: VictorHong
authorEmoji: 🪶
authorImageUrl:
tocLevels: ["h1","h2", "h3", "h4"]
libraries: [katex, mathjax, mermaid, chart, flowchartjs, msc, viz, wavedrom]
tags: []
series: []
categories: []
---
```

## 工作流程建议

### 推荐流程

1. **配置环境变量**
   ```bash
   # 在 ~/.zshrc 中添加
   export HUGO_BLOG_DIR=/Users/victor/Desktop/Projects/github/HUGO_blog
   ```

2. **编写文章**
   - 在任意位置创建 Markdown 文件
   - 使用 Obsidian 或其他编辑器
   - 完成内容编写

3. **准备封面图（可选）**
   - 推荐尺寸：1200x630（社交媒体分享）
   - 支持格式：png, jpg, webp

4. **检查配置**
   ```bash
   python3 scripts/publish_blog.py --check-config
   ```

5. **查看可用分类**
   ```bash
   python3 scripts/publish_blog.py --list-categories
   ```

6. **发布文章**
   ```bash
   python3 scripts/publish_blog.py \
     --md ~/Downloads/完成的文章.md \
     --cover ~/Downloads/封面图.png \
     --category 技术
   ```

7. **本地预览**
   ```bash
   cd $HUGO_BLOG_DIR
   hugo server -D
   ```
   访问 http://localhost:1313 查看效果

8. **构建并部署**
   ```bash
   cd $HUGO_BLOG_DIR
   hugo
   git add .
   git commit -m "发布新文章：文章标题"
   git push
   ```

## 文件命名规则

- 文章名会自动转换为小写
- 空格替换为连字符
- 移除特殊字符
- 示例：`"我的第一篇博客"` → `"我的第一篇博客"` → `"我的第一篇博客.md"`

## 注意事项

1. **文章已存在** - 如果目标文件已存在，脚本会警告并覆盖
2. **原 front matter** - Markdown 文件原有的 front matter 会被移除
3. **分类不存在** - 如果指定的分类不存在，脚本会创建新目录
4. **封面图路径** - 支持相对路径和绝对路径
5. **博客验证** - 脚本会检查博客根目录是否包含 Hugo 配置文件

## 完整参数说明

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--check-config` | - | 显示当前配置信息和来源 | - |
| `--list-categories` | `-l` | 显示所有分类目录 | - |
| `--md` | `-m` | Markdown 文件路径 | 必需 |
| `--cover` | `-c` | 封面图片路径 | 可选 |
| `--category` | `-cat` | 博客分类目录名称 | 必需 |
| `--name` | `-n` | 自定义文章名称 | 使用文件名 |
| `--draft` | `-d` | 标记为草稿 | false |
| `--blog-dir` | - | Hugo 博客项目根目录 | 环境变量或当前目录 |
| `--posts-dir` | - | posts 目录完整路径 | 环境变量或默认相对路径 |
| `--template` | - | 模板文件完整路径 | 环境变量或默认相对路径 |

## 技术细节

- **脚本语言**: Python 3
- **依赖**: 仅使用标准库
- **兼容性**: 支持 macOS/Linux/Windows
- **编码**: UTF-8（支持中文）
- **Hugo 验证**: 自动检测 config.toml/yaml/json

## Resources

### scripts/

- `publish_blog.py` - Hugo 博客文章发布脚本，实现所有核心功能

该脚本仅使用 Python 标准库，无需安装额外依赖。