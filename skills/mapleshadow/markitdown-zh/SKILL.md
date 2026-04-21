---
name: markitdown-zh
description: OpenClaw 智能体文档转换技能，用于将各类文档转换为 Markdown 格式，又称为 md 格式。基于微软 MarkItDown 库，支持 PDF、Word、PowerPoint、Excel、图像 (OCR)、音频 (转录)、HTML 和 YouTube 链接。
metadata:
  openclaw:
    emoji: "📄"
    homepage: https://github.com/karmanverma/markitdown-skill
    requires:
      bins: ["python3", "pipx", "markitdown"]
    install:
      - id: "markitdown"
        kind: "pipx"
        package: "markitdown[all]"
        bins: ["markitdown"]
        label: "安装 MarkItDown CLI (pipx)"
---

# MarkItDown 技能

使用微软 [MarkItDown](https://github.com/microsoft/markitdown) 库将文档转换为 Markdown 的文档和工具。

> **注意：** 此技能提供文档和批量脚本。实际的转换由通过 pip 安装的 `markitdown` CLI/库完成。

## 何时使用

**使用 markitdown 进行：**
- 📄 获取文档（README、API 文档）
- 🌐 将网页转换为 markdown
- 📝 文档分析（PDF、Word、PowerPoint）
- 🎬 YouTube 转录
- 🖼️ 图像文本提取（OCR）
- 🎤 音频转录

## 快速开始

```bash
# 将文件转换为 markdown
markitdown document.pdf -o output.md

# 转换 URL
markitdown https://example.com/docs -o docs.md
```

## 支持的格式

| 格式 | 功能 |
|------|------|
| PDF | 文本提取、结构保留 |
| Word (.docx) | 标题、列表、表格 |
| PowerPoint | 幻灯片、文本 |
| Excel | 表格、工作表 |
| 图像 | OCR + EXIF 元数据 |
| 音频 | 语音转录 |
| HTML | 结构保留 |
| YouTube | 视频转录 |

## 安装

此技能需要微软的 `markitdown` CLI：

```bash
sudo apt-get install pipx
# 使用pipx安装markitdown包 all表示支持所有格式
pipx install 'markitdown[all]'
# 将markitdown调用路径放入当前变量PATH内
pipx ensurepath
```

或仅安装特定格式：
```bash
sudo apt-get install pipx
pip install 'markitdown[pdf,docx,pptx]'
pipx ensurepath
```

## 常用模式

### 获取文档
```bash
markitdown https://github.com/user/repo/blob/main/README.md -o readme.md
```

### 转换 PDF
```bash
markitdown document.pdf -o document.md
```

### 批量转换
```bash
# 使用包含的脚本
python ~/.openclaw/skills/markitdown-zh/scripts/batch_convert.py docs/*.pdf -o markdown/ -v

# 或使用 shell 循环
for file in docs/*.pdf; do
  markitdown "$file" -o "${file%.pdf}.md"
done
```

## Python API

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("document.pdf")
print(result.text_content)
```

## 故障排除

### "markitdown 未找到"
```bash
# 安装pipx包管理应用，通过pipx安装包不需要（或者说是自动）新建虚拟环境
sudo apt-get install pipx
# 使用pipx安装markitdown包 all表示支持所有格式
pipx install 'markitdown[all]'
# 将markitdown调用路径放入当前变量PATH内
pipx ensurepath
```

### OCR 无法工作
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract
```

## 此技能提供的内容

| 组件 | 来源 |
|------|------|
| `markitdown` CLI | 微软的 pip 包 |
| `markitdown` Python API | 微软的 pip 包 |
| `scripts/batch_convert.py` | 此技能（工具脚本） |
| 文档 | 此技能 |

## 另请参阅

- [USAGE-GUIDE.md](USAGE-GUIDE.md) - 详细示例
- [reference.md](reference.md) - 完整 API 参考
- [Microsoft MarkItDown](https://github.com/microsoft/markitdown) - 上游库
