# MarkItDown 使用指南

文档转换的详细示例和模式。

## CLI 使用

### 基本转换

```bash
# 输出到标准输出
markitdown document.pdf

# 输出到文件
markitdown document.pdf -o output.md

# 从标准输入读取
cat document.pdf | markitdown > output.md
```

### 网页内容

```bash
# 转换网页
markitdown https://example.com/docs -o docs.md

# 转换 GitHub README
markitdown https://github.com/user/repo/blob/main/README.md -o readme.md
```

### 图像 OCR

```bash
# 提取图像中的文本
markitdown image.jpg -o text.md

# 使用 LLM 生成图像描述
markitdown image.jpg --llm-model gpt-4o -o description.md
```

### 音频转录

```bash
# 转录音频文件
markitdown audio.mp3 -o transcript.md
```

## 批量处理

### 使用批量脚本

```bash
# 转换目录中的所有 PDF 文件
python scripts/batch_convert.py docs/*.pdf -o markdown/

# 详细输出
python scripts/batch_convert.py docs/*.pdf -o markdown/ -v

# 启用插件
python scripts/batch_convert.py docs/*.pdf -o markdown/ -p
```

### Shell 循环

```bash
# 转换所有 PDF 文件
for file in *.pdf; do
  markitdown "$file" -o "${file%.pdf}.md"
done

# 转换所有 Word 文档
for file in *.docx; do
  markitdown "$file" -o "${file%.docx}.md"
done
```

## Python API

### 基本使用

```python
from markitdown import MarkItDown

# 初始化转换器
md = MarkItDown()

# 转换文件
result = md.convert("document.pdf")
print(result.text_content)

# 转换 URL
result = md.convert("https://example.com/docs")
print(result.text_content)
```

### 高级配置

```python
from markitdown import MarkItDown
from openai import OpenAI

# 使用 LLM 客户端
client = OpenAI()

md = MarkItDown(
    llm_client=client,
    llm_model="gpt-4o",
    enable_plugins=True,
    docintel_endpoint="https://your-endpoint.cognitiveservices.azure.com/"
)

result = md.convert("image.jpg")
print(result.text_content)
```

### 处理结果

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("document.pdf")

# 访问不同属性
print(f"文本内容: {result.text_content}")
print(f"元数据: {result.metadata}")
print(f"结构: {result.structure}")
print(f"图像: {result.images}")
print(f"表格: {result.tables}")
```

## 常见用例

### 文档归档

```bash
# 将整个文档目录转换为 markdown
find docs/ -type f \( -name "*.pdf" -o -name "*.docx" \) -exec markitdown {} -o {}.md \;
```

### 网页抓取

```bash
# 抓取并转换多个网页
for url in "https://example.com/page1" "https://example.com/page2"; do
  filename=$(basename "$url")
  markitdown "$url" -o "pages/${filename}.md"
done
```

### 会议记录

```bash
# 转录会议录音
markitdown meeting.mp3 -o meeting_notes.md

# 转换会议幻灯片
markitdown presentation.pptx -o presentation_notes.md
```

## 故障排除

### 常见错误

**"markitdown: command not found"**
```bash
# 安装pipx包管理应用，通过pipx安装包不需要（或者说是自动）新建虚拟环境
sudo apt-get install pipx
# 使用pipx安装markitdown包 all表示支持所有格式
pipx install 'markitdown[all]'
# 将markitdown调用路径放入当前变量PATH内
pipx ensurepath
```

**OCR 失败**
```bash
# 安装 Tesseract OCR
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# 从 https://github.com/UB-Mannheim/tesseract/wiki 下载
```

### 性能优化

**大文件处理**
```bash
# 分割大文件
split -b 10M large_document.pdf document_part_

# 分别转换每个部分
for part in document_part_*; do
  markitdown "$part" -o "${part}.md"
done
```

**内存限制**
```bash
# 使用较小的模型
markitdown document.pdf --model small -o output.md
```

## 最佳实践

1. **测试小样本**：在处理大量文件前，先测试一个小样本
2. **检查输出**：转换后检查输出文件的完整性
3. **备份原始文件**：始终保留原始文件的备份
4. **使用版本控制**：将转换后的 markdown 文件纳入版本控制
5. **监控资源使用**：处理大文件时监控内存和 CPU 使用情况

## 集成示例

### 与 OpenClaw 集成

```python
# 在 OpenClaw 技能中使用 markitdown
import subprocess

def convert_to_markdown(input_file, output_file):
    """将文件转换为 markdown"""
    try:
        result = subprocess.run(
            ["markitdown", input_file, "-o", output_file],
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
```

### 自动化工作流

```bash
#!/bin/bash
# 自动化文档处理工作流

# 1. 转换所有新文档
find ./incoming -type f -name "*.pdf" -mtime -1 | while read file; do
  markitdown "$file" -o "./markdown/$(basename "$file").md"
done

# 2. 生成摘要
echo "# 每日文档摘要" > daily_summary.md
echo "生成时间: $(date)" >> daily_summary.md
echo "" >> daily_summary.md

find ./markdown -name "*.md" -mtime -1 | while read file; do
  echo "## $(basename "$file")" >> daily_summary.md
  head -5 "$file" >> daily_summary.md
  echo "" >> daily_summary.md
done
```

## 更多资源

- [MarkItDown GitHub](https://github.com/microsoft/markitdown) - 官方仓库
- [SKILL.md](SKILL.md) - 技能文档
- [reference.md](reference.md) - 完整 API 参考
