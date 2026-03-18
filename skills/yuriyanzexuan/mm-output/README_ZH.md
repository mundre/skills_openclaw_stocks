# PosterGen Parser Unit

本项目是从 [PosterGen](https://github.com/lewis-key/PosterGen) 项目中提取的独立可复用单元。用于解析 PDF/Markdown 文件，提取结构化文本、图片（图表）和表格，然后生成多种输出格式，包括 HTML、PDF、PNG 和 DOCX —— 全部在一个 Docker 容器中完成。

## 功能特性

- **输入格式**: PDF、Markdown
- **输出格式**: HTML、PDF、PNG、DOCX
- 从 PDF 中提取所有文本为 Markdown 格式
- 提取所有图表和表格并保存为 PNG 文件
- 通过 LLM 生成 HTML 海报，支持可定制模板
- 统一流水线：解析 + 渲染 + 转换一条命令完成
- 多模态输出转换（HTML → PDF/PNG/DOCX）
- 支持 Docker，便于部署和迁移
- 支持多种 LLM 后端：OpenAI、Gemini、Qwen（QST/MAAS）

## 快速开始

### 一条命令完成全流程（PDF → HTML + PDF + PNG + DOCX）

```bash
# 构建 Docker 镜像
./docker-build.sh build

# 解析 PDF 并一次性生成所有输出格式
docker run --rm \
  -v "$(pwd)/input:/app/input:ro" \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/.env:/app/.env:ro" \
  -v "$HOME/.cache/postergen-docker:/root/.cache" \
  -e CHROME_EXECUTABLE_PATH=/opt/chrome-linux64/chrome \
  postergen-parser:latest \
  python run.py \
    --pdf_path /app/input/my_paper.pdf \
    --output_dir /app/output \
    --output-all
```

### 分步工作流程

```bash
# 步骤 1: 解析 PDF 并生成 HTML
./docker-build.sh parse ./input/my_paper.pdf

# 步骤 2: 将 HTML 转换为 PDF/PNG/DOCX
./docker-build.sh convert ./output/poster_llm.html
```

## 安装

### 方案 1: Docker（推荐）

```bash
# 构建镜像
./docker-build.sh build

# 或使用 docker-compose
docker-compose build
```

### 方案 2: 本地安装

```bash
# 克隆仓库
git clone <repo-url>
cd postergenparserunit

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
pip install playwright
playwright install chromium

# 配置环境变量
cp .env.example .env
# 编辑 .env 添加你的 API 密钥
```

## LLM 配置

渲染器支持多种 LLM 后端，通过 `.env` 配置：

### OpenAI / Azure

```bash
TEXT_MODEL="gpt-4.1-2025-04-14"
OPENAI_API_KEY="your-key"
OPENAI_BASE_URL="https://api.openai.com/v1"
```

### Gemini（通过 Runway）

```bash
TEXT_MODEL="gemini-3-pro-preview"
RUNWAY_API_KEY="your-key"
```

### Qwen（通过 QST/MAAS）

```bash
TEXT_MODEL="qwen3-vl-235b-a22b-instruct"
QST_API_KEY="your-maas-key"
QST_BASE_URL="https://maas.devops.xiaohongshu.com/v1"
```

模型名称自动检测：包含 "gemini" 的使用 Gemini 原生 API，包含 "qwen" 的使用 QST/MAAS OpenAI 兼容 API，其他使用标准 OpenAI/Runway HTTP 路径。

## 使用说明

### 1. 解析输入（PDF/Markdown → HTML）

```bash
# 解析 PDF
python run.py --pdf_path /path/to/document.pdf --output_dir ./output

# 或解析 Markdown
python run.py --md_path /path/to/document.md --output_dir ./output

# 启用自动图片增强
python run.py --pdf_path input.pdf --output_dir ./output --auto_images
```

### 2. 统一流水线（解析 + 渲染 + 转换）

```bash
# 一步完成解析和所有格式输出
python run.py --pdf_path input.pdf --output_dir ./output --output-all

# 仅生成特定格式
python run.py --pdf_path input.pdf --output_dir ./output --output-pdf --output-png
```

### 3. 转换已有 HTML（独立使用）

```bash
# 生成所有格式
python -m mm_output.cli ./output/poster_llm.html --format all --output-dir ./mm_outputs/

# 生成特定格式
python -m mm_output.cli ./output/poster_llm.html --format pdf --output poster.pdf

# 自定义选项
python -m mm_output.cli ./output/poster.html --format pdf \
    --page-size A3 --landscape --output poster_a3.pdf
```

## Docker 使用

### 构建镜像

```bash
./docker-build.sh build

# 不使用缓存构建
./docker-build.sh build-nc
```

### 运行命令

```bash
# 解析 PDF
./docker-build.sh parse ./input/my_paper.pdf

# 转换 HTML 为多模态输出
./docker-build.sh convert ./output/poster.html

# 交互式 shell
./docker-build.sh run

# 带额外选项
./docker-build.sh parse ./input/my_paper.pdf --auto_images --template doubao_dark.txt
```

### 开发模式（挂载本地文件）

将修改后的源文件挂载到容器中，无需重新构建即可测试：

```bash
docker run --rm \
  -v "$(pwd)/renderer_unit.py:/app/renderer_unit.py:ro" \
  -v "$(pwd)/run.py:/app/run.py:ro" \
  -v "$(pwd)/.env:/app/.env:ro" \
  -v "$(pwd)/input:/app/input:ro" \
  -v "$(pwd)/output:/app/output" \
  -v "$HOME/.cache/postergen-docker:/root/.cache" \
  -e CHROME_EXECUTABLE_PATH=/opt/chrome-linux64/chrome \
  postergen-parser:latest \
  python run.py \
    --pdf_path /app/input/my_paper.pdf \
    --output_dir /app/output \
    --output-all
```

`-v "$HOME/.cache/postergen-docker:/root/.cache"` 挂载可以在多次运行间持久化模型下载缓存。

### 使用 Docker Compose

```bash
# 启动交互式容器
docker-compose up -d postergen
docker-compose exec postergen bash

# 在容器内运行
python run.py --pdf_path /app/input/my_paper.pdf --output_dir /app/output --output-all
```

## 迁移与分发

### 导出镜像（离线传输）

```bash
# 使用脚本
./docker-build.sh save
# 生成: postergen-parser-latest.tar.gz

# 手动
docker save postergen-parser:latest | gzip > postergen-parser.tar.gz
```

### 导入镜像

```bash
# 使用脚本
./docker-build.sh load postergen-parser-latest.tar.gz

# 手动
gunzip -c postergen-parser.tar.gz | docker load
```

### 推送到镜像仓库

```bash
export REGISTRY=your-registry.com
./docker-build.sh push
```

## 输出目录结构

```
output/
├── raw.md                    # 提取的 Markdown 文本
├── poster_llm.html           # LLM 生成的 HTML 海报
├── poster_llm__*.html        # 其他模板变体
├── poster_preview.html       # 简单预览（备用）
├── assets/
│   ├── figure-1.png          # 提取的图表
│   ├── table-1.png           # 提取的表格
│   ├── figures.json          # 图表元数据
│   └── tables.json           # 表格元数据
└── mm_outputs/               # 多模态输出
    ├── poster_llm.pdf
    ├── poster_llm.png
    └── poster_llm.docx
```

## 命令参考

### 主解析器 (`run.py`)

| 参数 | 默认值 | 描述 |
|------|--------|------|
| `--pdf_path` | 必填* | 输入 PDF 文件路径 |
| `--md_path` | 必填* | 输入 Markdown 文件路径 |
| `--output_dir` | 必填 | 输出目录 |
| `--render_mode` | `llm` | `llm` 或 `simple` |
| `--text_model` | 环境变量 `TEXT_MODEL` | LLM 模型名称 |
| `--template` | 所有模板 | 指定模板名称 |
| `--auto_images` | 关闭 | 使用网络图片自动增强 |
| `--output-all` | 关闭 | 生成 PDF + PNG + DOCX |
| `--output-pdf` | 关闭 | 仅生成 PDF |
| `--output-png` | 关闭 | 仅生成 PNG |
| `--output-docx` | 关闭 | 仅生成 DOCX |

*`--pdf_path` 和 `--md_path` 必须二选一。

### 环境变量

```bash
# LLM API 配置（选择一组）
TEXT_MODEL="gpt-4.1-2025-04-14"
OPENAI_API_KEY="your-key"
OPENAI_BASE_URL="https://api.openai.com/v1"

# 或 Qwen/QST
QST_API_KEY="your-maas-key"
QST_BASE_URL="https://maas.devops.xiaohongshu.com/v1"

# 或 Gemini via Runway
RUNWAY_API_KEY="your-key"

# Chrome 路径（未设置时自动检测）
CHROME_EXECUTABLE_PATH="/opt/chrome-linux64/chrome"

# 模板选择
POSTER_TEMPLATE="doubao_dark.txt"
```

## 模板选择

```bash
export POSTER_TEMPLATE="doubao.txt"                  # 默认
export POSTER_TEMPLATE="doubao_refine.txt"           # 带参考文献
export POSTER_TEMPLATE="doubao_dark.txt"             # 深色主题
export POSTER_TEMPLATE="doubao_minimal.txt"          # 极简风格
export POSTER_TEMPLATE="doubao_newspaper.txt"        # 多栏报纸风格
export POSTER_TEMPLATE="doubao_enterprise_blue.txt"  # 企业蓝主题
export POSTER_TEMPLATE="report_web.txt"              # 网页报告
export POSTER_TEMPLATE="report_web_reduced.txt"      # 精简网页报告
```

模板位于 `templates/` 目录。

## Python API

```python
from mm_output import MMOutputGenerator

with MMOutputGenerator() as gen:
    # 转 PDF
    gen.html_to_pdf("input.html", "output.pdf", page_size="A4")

    # 转 PNG
    gen.html_to_png("input.html", "output.png", full_page=True)

    # 转 DOCX
    gen.html_to_docx("input.html", "output.docx")

    # 一次转换所有格式
    results = gen.convert_all("input.html", "./outputs/")
```

## 故障排除

### Chrome 未找到

```bash
export CHROME_EXECUTABLE_PATH=/path/to/chrome
# 或在 Docker 中:
-e CHROME_EXECUTABLE_PATH=/opt/chrome-linux64/chrome
```

### 缺少系统依赖（本地运行）

```bash
# Ubuntu/Debian
playwright install-deps chromium

# macOS
brew install nss nspr
```

### 内存问题

```bash
docker run --memory=8g --memory-swap=8g ...
```

### Docker 镜像拉取失败（国内）

在 Docker Desktop → Settings → Docker Engine 中配置镜像加速器：

```json
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me"
  ]
}
```

### Docker 构建时 apt-get 很慢（国内）

Dockerfile 中已包含阿里云 Debian 镜像源。如果仍然很慢，在 Docker Desktop → Settings → Resources → Proxies 中配置代理。

## 文件结构

```
postergenparserunit/
├── run.py                  # 主入口（解析 + 渲染 + 转换）
├── parser_unit.py          # PDF/Markdown 解析器
├── renderer_unit.py        # 基于 LLM 的 HTML 渲染器
├── image_unit.py           # 自动图片搜索与增强
├── mm_output/              # 多模态输出模块
│   ├── __init__.py
│   ├── converter.py        # PDF/PNG/DOCX 生成
│   ├── cli.py              # 命令行接口
│   └── integrate.py        # run.py 集成辅助
├── templates/              # HTML 海报模板
├── Dockerfile              # Docker 镜像定义
├── docker-compose.yml      # 服务编排
├── docker-build.sh         # 构建辅助脚本
├── Makefile                # Make 命令
├── .env.example            # 环境变量模板
└── requirements.txt        # Python 依赖
```

## 许可证

MIT License
