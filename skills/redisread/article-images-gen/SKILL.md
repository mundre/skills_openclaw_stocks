---
name: article-images-gen
description: 文案插图专家，为文章生成手绘风格插图。风格：手绘、简约、整洁、留白、构图平衡、色调统一。Use when user asks to generate illustrations for articles, "为文章配图", "生成插图", or needs hand-drawn style images for content.
---

# Article Images Generator (文案插图专家)

专为文章生成手绘风格插图，使用阿里百炼 DashScope Qwen-Image API。

## 调用脚本

```bash
# 为文章生成配图（全自动：分析 → 生成大纲 → 生成提示词 → 生成图片 → 插入文章）
bun scripts/illustrator.ts path/to/article.md [--density <level>] [--output-dir <path>]

# 单张图片（直接 prompt）
bun scripts/main.ts --prompt "your prompt" [--image output.png]

# 批量 prompt 文件
bun scripts/main.ts --promptfiles prompt1.md,prompt2.md
```

密度选项：`minimal` (1-2张) | `balanced` (3-4张) | `per-section`（推荐）| `rich` (5+张)

## 工作流程

1. **分析文案**：识别章节结构、核心论点、适合插图的位置
2. **分析判断**：AI 根据文章章节数量和内容自动选择密度（默认 per-section）
3. **生成大纲**：保存 `{outputDir}/outline.md`
4. **生成提示词**：保存 `{outputDir}/prompts/NN-hand-drawn-{slug}.md`
5. **生成图片**：调用 DashScope API，保存到 `{outputDir}/`
6. **更新文章**：在对应章节后插入图片引用 `![描述](imgs/01-hand-drawn-xxx.png)`

## 环境要求

- **运行时**：[bun](https://bun.sh) (`bun run` / `bunx`)
- **API Key**：`DASHSCOPE_API_KEY` 环境变量

## 输出目录

固定输出到 `/tmp/imageGen/{YYYYMMDD}/{articleName}/`，例如：
`/tmp/imageGen/20260410/my-article/01-hand-drawn-concept.png`

`articleName` 取文章文件名（不含扩展名），日期取当天日期。
