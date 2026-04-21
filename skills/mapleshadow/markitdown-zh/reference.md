# MarkItDown API 参考

## MarkItDown 类

### 构造函数

```python
class MarkItDown:
    def __init__(
        self,
        enable_plugins: bool = False,
        llm_client = None,
        llm_model: str = None,
        llm_prompt: str = None,
        docintel_endpoint: str = None
    )
```

**参数：**
- `enable_plugins` (bool): 启用第三方插件（默认：False）
- `llm_client`: 用于图像描述的 OpenAI 兼容客户端
- `llm_model` (str): 图像描述的模型名称（例如："gpt-4o"）
- `llm_prompt` (str): 图像描述的自定义提示
- `docintel_endpoint` (str): Azure Document Intelligence 端点

**示例：**
```python
from markitdown import MarkItDown

# 基本用法
md = MarkItDown()

# 启用插件
md = MarkItDown(enable_plugins=True)

# 使用 LLM 图像描述
from openai import OpenAI
client = OpenAI()
md = MarkItDown(llm_client=client, llm_model="gpt-4o")

# 使用 Azure Document Intelligence
md = MarkItDown(docintel_endpoint="https://your-endpoint.cognitiveservices.azure.com/")
```

### convert() 方法

```python
def convert(
    self,
    source: str | Path | bytes | BinaryIO
) -> ConversionResult
```

**参数：**
- `source`: 文件路径（str/Path）、字节或类文件对象（二进制模式）

**返回：**
- 包含 `text_content` 属性的 `ConversionResult` 对象

**示例：**
```python
# 从文件路径
result = md.convert("document.pdf")

# 从字节
with open("document.pdf", "rb") as f:
    result = md.convert(f.read())

# 从类文件对象
with open("document.pdf", "rb") as f:
    result = md.convert(f)

print(result.text_content)
```

### convert_stream() 方法

```python
def convert_stream(
    self,
    stream: BinaryIO,
    file_extension: str = None
) -> ConversionResult
```

**参数：**
- `stream` (BinaryIO): 二进制类文件对象（例如：打开的文件、io.BytesIO）
- `file_extension` (str): 可选的文件扩展名提示

**返回：**
- `ConversionResult` 对象

**示例：**
```python
import io

# 从 BytesIO
data = io.BytesIO(pdf_bytes)
result = md.convert_stream(data, file_extension=".pdf")
```

## ConversionResult

```python
class ConversionResult:
    text_content: str  # Markdown 输出
```

**属性：**
- `text_content` (str): 转换后的 markdown 内容

## CLI 使用

### 基本命令

```bash
# 转换到标准输出
markitdown <文件>

# 转换到文件
markitdown <文件> -o <输出.md>

# 管道输入
cat <文件> | markitdown
```

### 选项

```bash
markitdown --help
markitdown --list-plugins
markitdown --use-plugins <文件>
markitdown <文件> -d -e <端点>  # Azure Document Intelligence
```

## 格式特定详情

### PDF
- **最适合：** 基于文本的 PDF
- **限制：** 复杂布局可能需要 Azure Document Intelligence
- **依赖项：** `pip install 'markitdown[pdf]'`

### PowerPoint (.pptx)
- **提取：** 幻灯片文本、结构
- **增强功能：** LLM 图像描述
- **依赖项：** `pip install 'markitdown[pptx]'`

### Word (.docx)
- **保留：** 标题、列表、表格、链接
- **依赖项：** `pip install 'markitdown[docx]'`

### Excel (.xlsx, .xls)
- **提取：** 表格、多个工作表
- **格式：** Markdown 表格
- **依赖项：** `pip install 'markitdown[xlsx]'` 或 `'markitdown[xls]'`

### 图像 (jpg, png 等)
- **提取：** EXIF 元数据 + OCR 文本
- **需要：** Tesseract OCR 系统依赖项
- **增强功能：** LLM 描述

### 音频 (wav, mp3)
- **提取：** EXIF 元数据 + 语音转录
- **依赖项：** `pip install 'markitdown[audio-transcription]'`
- **注意：** 可能需要系统音频库

### YouTube
- **提取：** 视频转录（如果可用）
- **依赖项：** `pip install 'markitdown[youtube-transcription]'`
- **用法：** `markitdown "https://youtube.com/watch?v=视频_ID"`

### HTML
- **保留：** 文档结构
- **无需额外依赖项**

### CSV/JSON/XML
- **转换：** 为可读的 markdown 格式
- **无需额外依赖项**

### ZIP
- **行为：** 遍历内部所有文件
- **无需额外依赖项**

### EPUB
- **提取：** 电子书内容
- **无需额外依赖项**

## 环境要求

### Python 版本
- **必需：** Python 3.10 或更高版本
- **推荐：** Python 3.12

### 虚拟环境（推荐）

```bash
# 标准 Python
python -m venv .venv
source .venv/bin/activate

# uv
uv venv --python=3.12 .venv
source .venv/bin/activate

# Conda
conda create -n markitdown python=3.12
conda activate markitdown
```

### 系统依赖项

**Tesseract OCR**（用于图像文本提取）：
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# 从 https://github.com/UB-Mannheim/tesseract/wiki 下载安装程序
```

**音频库**（用于音频转录）：
- speech_recognition 库的平台特定依赖项
- 查看：https://github.com/Uberi/speech_recognition

## Azure Document Intelligence

用于复杂布局的高质量 PDF 转换：

### 设置

1. 创建 Azure Document Intelligence 资源
2. 获取端点和 API 密钥
3. 设置环境变量：`AZURE_DOCUMENT_INTELLIGENCE_KEY=<您的密钥>`

### 使用

**CLI：**
```bash
markitdown document.pdf -d -e "<端点>" -o output.md
```

**Python：**
```python
md = MarkItDown(docintel_endpoint="<端点>")
result = md.convert("document.pdf")
```

### 更多信息
https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/

## 插件系统

### 查找插件
在 GitHub 搜索：`#markitdown-plugin`

### 使用插件

**CLI：**
```bash
markitdown --list-plugins
markitdown --use-plugins file.pdf
```

**Python：**
```python
md = MarkItDown(enable_plugins=True)
```

### 创建插件
查看仓库中的：`packages/markitdown-sample-plugin`

## 错误处理

### 常见问题

**缺少依赖项：**
```python
try:
    result = md.convert("file.pdf")
except ImportError as e:
    print(f"缺少依赖项：{e}")
    print("安装命令：pip install 'markitdown[pdf]'")
```

**文件格式不支持：**
```python
try:
    result = md.convert("file.unknown")
except ValueError as e:
    print(f"不支持的格式：{e}")
```

**转换错误：**
```python
try:
    result = md.convert("file.pdf")
except Exception as e:
    print(f"转换失败：{e}")
```

## 性能提示

1. **批量处理：** 重用 MarkItDown 实例
2. **大文件：** 考虑分块或流式处理
3. **OCR：** 如果速度重要，降低图像分辨率
4. **音频：** 预期实时或更慢的转录
5. **Azure Doc Intel：** 最适合复杂 PDF，会产生费用

## 输出格式说明

- **目标：** LLM 友好的 markdown，不是像素完美的复制
- **结构：** 保留标题、列表、表格、链接
- **图像：** 转换为 markdown 图像语法
- **表格：** 转换为 markdown 表格（可能丢失复杂格式）
- **样式：** 尽可能保留粗体、斜体
- **布局：** 线性文档结构（不保留多列）

## 集成示例

### LangChain 文档加载器

```python
from markitdown import MarkItDown
from langchain.docstore.document import Document

md = MarkItDown()

def load_document(file_path):
    result = md.convert(file_path)
    return Document(
        page_content=result.text_content,
        metadata={"source": file_path}
    )
```

### LlamaIndex 文档

```python
from markitdown import MarkItDown
from llama_index import Document

md = MarkItDown()

def create_llama_doc(file_path):
    result = md.convert(file_path)
    return Document(text=result.text_content)
```

### FastAPI 端点

```python
from fastapi import FastAPI, UploadFile
from markitdown import MarkItDown

app = FastAPI()
md = MarkItDown()

@app.post("/convert")
async def convert_file(file: UploadFile):
    content = await file.read()
    result = md.convert(content)
    return {"markdown": result.text_content}
```

## 破坏性变更 (v0.0.1 → v0.1.0)

1. **依赖项：** 现在按功能组组织
   - 使用 `pipx install 'markitdown[all]'` 保持向后兼容性

2. **convert_stream()：** 现在需要二进制类文件对象
   - 从文本（io.StringIO）更改为二进制（io.BytesIO）

3. **DocumentConverter：** 接口从路径更改为流
   - 不再创建临时文件
   - 插件作者需要更新代码

## 资源

- **GitHub：** https://github.com/microsoft/markitdown
- **PyPI：** https://pypi.org/project/markitdown/
- **问题：** https://github.com/microsoft/markitdown/issues
- **贡献：** 查看仓库中的 CONTRIBUTING.md
