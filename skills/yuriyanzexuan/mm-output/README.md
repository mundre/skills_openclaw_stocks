# PosterGen Parser Unit

A standalone, reusable unit extracted from the [PosterGen](https://github.com/lewis-key/PosterGen) project. Parses PDF/Markdown files to extract structured text, figures, and tables, then generates various output formats including HTML, PDF, PNG, and DOCX — all in a single Docker container.

## Features

- **Input Formats**: PDF, Markdown
- **Output Formats**: HTML, PDF, PNG, DOCX
- Extracts all text from a PDF into Markdown
- Extracts all figures and tables as PNG files
- Generates HTML posters via LLM with customizable templates
- Unified pipeline: parse + render + convert in one command
- Multi-modal output conversion (HTML → PDF/PNG/DOCX)
- Docker support for easy deployment and migration
- Supports multiple LLM backends: OpenAI, Gemini, Qwen (QST/MAAS)

## Quick Start

### One-Command Pipeline (PDF → HTML + PDF + PNG + DOCX)

```bash
# Build Docker image
./docker-build.sh build

# Parse PDF and generate all output formats at once
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

### Step-by-Step Workflow

```bash
# Step 1: Parse PDF and generate HTML
./docker-build.sh parse ./input/my_paper.pdf

# Step 2: Convert HTML to PDF/PNG/DOCX
./docker-build.sh convert ./output/poster_llm.html
```

## Installation

### Option 1: Docker (Recommended)

```bash
# Build image
./docker-build.sh build

# Or use docker-compose
docker-compose build
```

### Option 2: Local Installation

```bash
# Clone the repository
git clone <repo-url>
cd postergenparserunit

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
pip install playwright
playwright install chromium

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

## LLM Configuration

The renderer supports multiple LLM backends. Configure via `.env`:

### OpenAI / Azure

```bash
TEXT_MODEL="gpt-4.1-2025-04-14"
OPENAI_API_KEY="your-key"
OPENAI_BASE_URL="https://api.openai.com/v1"
```

### Gemini (via Runway)

```bash
TEXT_MODEL="gemini-3-pro-preview"
RUNWAY_API_KEY="your-key"
```

### Qwen (via QST/MAAS)

```bash
TEXT_MODEL="qwen3-vl-235b-a22b-instruct"
QST_API_KEY="your-maas-key"
QST_BASE_URL="https://maas.devops.xiaohongshu.com/v1"
```

The model is auto-detected by name: models containing "gemini" use the Gemini native API, models containing "qwen" use the QST/MAAS OpenAI-compatible API, and all others use the standard OpenAI/Runway HTTP path.

## Usage

### 1. Parse Input (PDF/Markdown → HTML)

```bash
# Parse PDF
python run.py --pdf_path /path/to/document.pdf --output_dir ./output

# Or parse Markdown
python run.py --md_path /path/to/document.md --output_dir ./output

# With auto image enhancement
python run.py --pdf_path input.pdf --output_dir ./output --auto_images
```

### 2. Unified Pipeline (Parse + Render + Convert)

```bash
# Parse and generate all output formats in one step
python run.py --pdf_path input.pdf --output_dir ./output --output-all

# With specific formats only
python run.py --pdf_path input.pdf --output_dir ./output --output-pdf --output-png
```

### 3. Convert Existing HTML (Standalone)

```bash
# Generate all formats
python -m mm_output.cli ./output/poster_llm.html --format all --output-dir ./mm_outputs/

# Generate specific format
python -m mm_output.cli ./output/poster_llm.html --format pdf --output poster.pdf

# With custom options
python -m mm_output.cli ./output/poster.html --format pdf \
    --page-size A3 --landscape --output poster_a3.pdf
```

## Docker Usage

### Build Image

```bash
./docker-build.sh build

# Build without cache
./docker-build.sh build-nc
```

### Run Commands

```bash
# Parse PDF
./docker-build.sh parse ./input/my_paper.pdf

# Convert HTML to multi-modal
./docker-build.sh convert ./output/poster.html

# Interactive shell
./docker-build.sh run

# With additional options
./docker-build.sh parse ./input/my_paper.pdf --auto_images --template doubao_dark.txt
```

### Development Mode (Mount Local Files)

Mount modified source files into the container to test without rebuilding:

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

The `-v "$HOME/.cache/postergen-docker:/root/.cache"` mount persists model downloads across runs.

### Using Docker Compose

```bash
# Start interactive container
docker-compose up -d postergen
docker-compose exec postergen bash

# Run inside container
python run.py --pdf_path /app/input/my_paper.pdf --output_dir /app/output --output-all
```

## Migration & Distribution

### Export Image (Offline Transfer)

```bash
# Using script
./docker-build.sh save
# Creates: postergen-parser-latest.tar.gz

# Manual
docker save postergen-parser:latest | gzip > postergen-parser.tar.gz
```

### Import Image

```bash
# Using script
./docker-build.sh load postergen-parser-latest.tar.gz

# Manual
gunzip -c postergen-parser.tar.gz | docker load
```

### Push to Registry

```bash
export REGISTRY=your-registry.com
./docker-build.sh push
```

## Output Directory Structure

```
output/
├── raw.md                    # Extracted markdown text
├── poster_llm.html           # LLM-generated HTML poster
├── poster_llm__*.html        # Additional template variants
├── poster_preview.html       # Simple preview (fallback)
├── assets/
│   ├── figure-1.png          # Extracted figures
│   ├── table-1.png           # Extracted tables
│   ├── figures.json          # Figure metadata
│   └── tables.json           # Table metadata
└── mm_outputs/               # Multi-modal outputs
    ├── poster_llm.pdf
    ├── poster_llm.png
    └── poster_llm.docx
```

## Command Reference

### Main Parser (`run.py`)

| Argument | Default | Description |
|----------|---------|-------------|
| `--pdf_path` | required* | Input PDF file path |
| `--md_path` | required* | Input Markdown file path |
| `--output_dir` | required | Output directory |
| `--render_mode` | `llm` | `llm` or `simple` |
| `--text_model` | env `TEXT_MODEL` | LLM model name |
| `--template` | all templates | Specific template name |
| `--auto_images` | off | Auto-enhance with web images |
| `--output-all` | off | Generate PDF + PNG + DOCX |
| `--output-pdf` | off | Generate PDF only |
| `--output-png` | off | Generate PNG only |
| `--output-docx` | off | Generate DOCX only |

*One of `--pdf_path` or `--md_path` is required.

### Environment Variables

```bash
# LLM API Configuration (choose one set)
TEXT_MODEL="gpt-4.1-2025-04-14"
OPENAI_API_KEY="your-key"
OPENAI_BASE_URL="https://api.openai.com/v1"

# Or Qwen/QST
QST_API_KEY="your-maas-key"
QST_BASE_URL="https://maas.devops.xiaohongshu.com/v1"

# Or Gemini via Runway
RUNWAY_API_KEY="your-key"

# Chrome Path (auto-detected if not set)
CHROME_EXECUTABLE_PATH="/opt/chrome-linux64/chrome"

# Template Selection
POSTER_TEMPLATE="doubao_dark.txt"
```

## Template Selection

```bash
export POSTER_TEMPLATE="doubao.txt"                  # default
export POSTER_TEMPLATE="doubao_refine.txt"           # with references
export POSTER_TEMPLATE="doubao_dark.txt"             # dark theme
export POSTER_TEMPLATE="doubao_minimal.txt"          # minimal clean
export POSTER_TEMPLATE="doubao_newspaper.txt"        # multi-column
export POSTER_TEMPLATE="doubao_enterprise_blue.txt"  # corporate theme
export POSTER_TEMPLATE="report_web.txt"              # web report
export POSTER_TEMPLATE="report_web_reduced.txt"      # reduced web report
```

Templates are located in the `templates/` directory.

## Python API

```python
from mm_output import MMOutputGenerator

with MMOutputGenerator() as gen:
    # To PDF
    gen.html_to_pdf("input.html", "output.pdf", page_size="A4")

    # To PNG
    gen.html_to_png("input.html", "output.png", full_page=True)

    # To DOCX
    gen.html_to_docx("input.html", "output.docx")

    # All formats at once
    results = gen.convert_all("input.html", "./outputs/")
```

## Troubleshooting

### Chrome Not Found

```bash
export CHROME_EXECUTABLE_PATH=/path/to/chrome
# Or in Docker:
-e CHROME_EXECUTABLE_PATH=/opt/chrome-linux64/chrome
```

### Missing System Dependencies (Local)

```bash
# Ubuntu/Debian
playwright install-deps chromium

# macOS
brew install nss nspr
```

### Memory Issues

```bash
docker run --memory=8g --memory-swap=8g ...
```

### Docker Image Pull Fails (China)

Configure Docker mirror in Docker Desktop → Settings → Docker Engine:

```json
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me"
  ]
}
```

### apt-get Slow in Docker Build (China)

The Dockerfile includes an Alibaba Cloud mirror for Debian packages. If it's still slow, configure a proxy in Docker Desktop → Settings → Resources → Proxies.

## File Structure

```
postergenparserunit/
├── run.py                  # Main entry point (parse + render + convert)
├── parser_unit.py          # PDF/Markdown parser
├── renderer_unit.py        # LLM-based HTML renderer
├── image_unit.py           # Auto image search & enhancement
├── mm_output/              # Multi-modal output module
│   ├── __init__.py
│   ├── converter.py        # PDF/PNG/DOCX generation
│   ├── cli.py              # Command line interface
│   └── integrate.py        # Integration helper for run.py
├── templates/              # HTML poster templates
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Service orchestration
├── docker-build.sh         # Build helper script
├── Makefile                # Make commands
├── .env.example            # Environment variable template
└── requirements.txt        # Python dependencies
```

## License

MIT License
