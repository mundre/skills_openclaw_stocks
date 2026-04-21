# 安装后设置

MarkItDown 技能已安装！以下是开始使用的方法。

## 1. 验证安装

```bash
markitdown --version
```

如果未找到，安装 CLI：
```bash
sudo apt-get install pipx
# 使用pipx安装markitdown包 all表示支持所有格式
pipx install 'markitdown[all]'
# 将markitdown调用路径放入当前变量PATH内
pipx ensurepath
```

## 2. 测试

```bash
# 转换 PDF
markitdown document.pdf -o output.md

# 转换 URL
markitdown https://example.com -o page.md
```

## 3. 添加到智能体指令（推荐）

添加到您的 `AGENTS.md`：

```markdown
## 文档转换
当获取文档或转换文件时：
- 使用 `markitdown <url>` 代替 curl/wget 获取网页文档
- 使用 `markitdown <file>` 转换 PDF、Word、Excel 等文件
- 输出是经过优化的干净 markdown，适合 LLM 分析
```

## 4. 安装特定格式的依赖项

首先确保已安装pipx包管理器
```bash
sudo apt-get install pipx
pipx ensurepath
```

只安装您需要的部分：

```bash
pipx install 'markitdown[pdf]'      # PDF 支持
pipx install 'markitdown[docx]'     # Word 文档
pipx install 'markitdown[pptx]'     # PowerPoint
pipx install 'markitdown[xlsx]'     # Excel
pipx install 'markitdown[audio-transcription]'   # 音频
pipx install 'markitdown[youtube-transcription]' # YouTube
```

或安装所有功能：
```bash
pip install 'markitdown[all]'
```

## 5. 系统依赖项（可选）

### OCR（用于图像）
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract
```

## 快速参考

```bash
# 文件转换
markitdown file.pdf -o output.md

# URL 转换
markitdown https://example.com -o page.md

# 批量转换
python ~/.openclaw/skills/markitdown-zh/scripts/batch_convert.py docs/*.pdf -o markdown/ -v
```

## 故障排除

**"markitdown 未找到"**
```bash
sudo apt-get install pipx
pipx install 'markitdown[all]'
pipx ensurepath
```

**"没有名为 'xxx' 的模块"**
```bash
pipx install 'markitdown[pdf]'  # 或 docx、pptx 等
```

**OCR 无法工作**
```bash
sudo apt-get install tesseract-ocr
```
