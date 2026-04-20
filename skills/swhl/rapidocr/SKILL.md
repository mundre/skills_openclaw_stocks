---
name: RapidOCR
slug: rapidocr
version: 1.0.1
description: The latest official RapidOCR command-line version, supporting Chinese-English mixed OCR text recognition for local images (JPG/PNG/WEBP). No complex configuration needed, one-click terminal call. Returns structured text, location information, and confidence levels, suitable for daily office work, image-to-text and other high-frequency scenarios.
tags: [ocr, vision, cli, rapidocr, text recognition, Chinese-English recognition, tool, latest]
author: RapidAI
email: liekkaskono@163.com
homepage: https://rapidai.github.io/RapidOCRDocs
license: Apache-2.0 License
tools:
  - exec:run
  - file:read
  - file:write
install: |
  # Dependency Installation Steps (auto-shown to users when installing the Skill)
  1. Ensure Python 3.7+ is installed locally (3.8-3.11 recommended)
  2. Install dependencies with this command: pip install rapidocr onnxruntime
  3. Verify installation: Enter `rapidocr check` in terminal. Version info means successful installation.
main: rapidocr -img {{img_path}}
---


# RapidOCR

本技能用于本地图片 OCR 识别，兼容 Windows / Linux，支持 png、jpg、jpeg、webp、bmp、tif、tiff。

## 标准执行命令

```bash
node "{baseDir}/run_rapidocr.js" "{{input}}"
```

## 典型输入示例

纯文本输出示例：

    请识别图片里的文字，图片路径是 /tmp/demo.png

Windows 示例：

    请识别图片里的文字，图片路径是 C:\Users\name\Desktop\demo.png

JSON 输出示例：

    请识别图片里的文字并返回json，图片路径是 /tmp/demo.png --json

远程图片 URL 示例：

    请识别这张图，图片链接是 https://example.com/demo.png

## 代理执行规则

1. 直接把用户原话作为唯一参数传给脚本。
2. 脚本会自动从文本中提取本地绝对路径或远程图片 URL。
3. 若检测到 `--json`、`json输出`、`返回json`、`json格式`、`结构化`，则输出 JSON。
4. 若输入是远程图片 URL，脚本会先下载到本机临时目录，再执行 OCR。
5. 执行时优先尝试 `rapidocr -img <path>`；若不可用或失败，再自动回退到 Python API。
6. 建议先安装依赖：`python -m pip install rapidocr onnxruntime`
7. 输入变量使用 `{{input}}`，路径解析由脚本自行完成。

## 注意事项

- 默认返回纯文本，每行一条识别结果。
- JSON 模式返回 `text`、`lines`、`boxes`、`scores`、`source`。
- 仅支持图片，不直接支持 PDF。
- Windows 下 `rapidocr.exe` 通常是 Python 安装生成的 launcher；Linux 下通常直接是 `rapidocr`。
- Skill 只保留一条 bash 标准执行命令，避免解析歧义。
