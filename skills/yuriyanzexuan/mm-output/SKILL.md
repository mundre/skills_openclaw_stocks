---
name: mm-output
description: >-
  Run the Docker image yuriyzx/mm-output:latest to convert PDF/Markdown into
  HTML and multi-modal outputs (PDF, PNG, DOCX). Use when the user needs
  OpenAI-compatible API configuration, env setup, and Docker-based usage.
---

# MM Output (Docker Skill)

This skill uses **OpenAI-compatible** API configuration only. No other backend is documented.

## Capabilities

- Input: PDF / Markdown
- Rendering: Generate HTML posters
- Conversion: HTML -> PDF / PNG / DOCX
- Runtime: Docker image `yuriyzx/mm-output:latest`

---

## 1) Quick Start

```bash
docker pull yuriyzx/mm-output:latest

mkdir -p input output outputs
cp .env.example .env
cp /path/to/paper.pdf input/
```

Run the full pipeline (PDF -> HTML + PDF + PNG + DOCX):

```bash
docker run --rm \
  -v "$(pwd)/input:/app/input:ro" \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/outputs:/app/outputs" \
  -v "$(pwd)/.env:/app/.env:ro" \
  -v "$HOME/.cache/postergen-docker:/root/.cache" \
  -e CHROME_EXECUTABLE_PATH=/opt/chrome-linux64/chrome \
  yuriyzx/mm-output:latest \
  python run.py \
    --pdf_path /app/input/paper.pdf \
    --output_dir /app/output \
    --output-all
```

---

## 2) API Configuration (OpenAI-compatible Only)

Your `.env` only needs these three fields:

```bash
TEXT_MODEL="gpt-4.1-2025-04-14"
OPENAI_API_KEY="your-api-key"
OPENAI_BASE_URL="https://api.openai.com/v1"
```

OpenAI-compatible request format (example):

```json
{
  "model": "gpt-4.1-2025-04-14",
  "temperature": 0.7,
  "max_tokens": 8192,
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
  ]
}
```

---

## 3) Configuration Strategy

Recommended priority:

1. Mount `.env` file (recommended)
2. Temporary override via `docker run -e`
3. CLI arguments override (for example, `--template`)

Example:

```bash
docker run --rm \
  -v "$(pwd)/.env:/app/.env:ro" \
  -e CHROME_EXECUTABLE_PATH=/opt/chrome-linux64/chrome \
  yuriyzx/mm-output:latest \
  python run.py --help
```

---

## 4) Usage

### 4.1 PDF Input

```bash
docker run --rm \
  -v "$(pwd)/input:/app/input:ro" \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/outputs:/app/outputs" \
  -v "$(pwd)/.env:/app/.env:ro" \
  -e CHROME_EXECUTABLE_PATH=/opt/chrome-linux64/chrome \
  yuriyzx/mm-output:latest \
  python run.py \
    --pdf_path /app/input/paper.pdf \
    --output_dir /app/output \
    --output-all
```

### 4.2 Markdown Input

```bash
docker run --rm \
  -v "$(pwd)/input:/app/input:ro" \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/outputs:/app/outputs" \
  -v "$(pwd)/.env:/app/.env:ro" \
  -e CHROME_EXECUTABLE_PATH=/opt/chrome-linux64/chrome \
  yuriyzx/mm-output:latest \
  python run.py \
    --md_path /app/input/paper.md \
    --output_dir /app/output \
    --output-all
```

### 4.3 Convert Existing HTML Only

```bash
docker run --rm \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/mm_outputs:/app/mm_outputs" \
  -e CHROME_EXECUTABLE_PATH=/opt/chrome-linux64/chrome \
  yuriyzx/mm-output:latest \
  python -m mm_output.cli /app/output/poster_llm.html \
    --format all \
    --output-dir /app/mm_outputs
```

---

## 5) Key Arguments

`run.py`:

- `--pdf_path` / `--md_path` (choose one)
- `--output_dir`
- `--render_mode llm|simple`
- `--template <name-or-path>`
- `--output-all` / `--output-pdf` / `--output-png` / `--output-docx`
- `--auto_images`

`python -m mm_output.cli`:

- `--format pdf|png|docx|all`
- `--output` (single file + single format)
- `--output-dir` (multi-format or batch mode)
- `--page-size`, `--landscape`
- `--viewport-width`, `--viewport-height`

---

## 6) Output Structure

```text
output/
├── raw.md
├── poster_llm.html
├── poster_llm__*.html
├── assets/
│   ├── figures.json
│   └── tables.json
└── mm_outputs/
    ├── poster_llm.pdf
    ├── poster_llm.png
    └── poster_llm.docx
```

---

## 7) Troubleshooting

- **401 authorization failed**: Verify `OPENAI_API_KEY`
- **404 model not found**: Verify `TEXT_MODEL` against provider-supported models
- **Connection failed**: Verify `OPENAI_BASE_URL` is a valid OpenAI-compatible endpoint
- **Chrome not found**: Pass `-e CHROME_EXECUTABLE_PATH=/opt/chrome-linux64/chrome`
- **Slow first run**: Mount `~/.cache/postergen-docker` to reuse cache

---

## 8) Script Image Name Alignment (Optional)

In this repo, `docker-build.sh` defaults to image name `postergen-parser:latest`.  
If you use the community image, add a local alias first:

```bash
docker tag yuriyzx/mm-output:latest postergen-parser:latest
```

Then you can directly reuse `./docker-build.sh parse|convert|run`.
