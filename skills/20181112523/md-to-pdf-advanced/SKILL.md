---
name: md-to-pdf-advanced
description: Convert Markdown files to PDF with multiple backend options (WeasyPrint, Pandoc, wkhtmltopdf). Supports syntax highlighting, tables, images, custom CSS themes, and page styling. Use when converting Markdown (.md) to PDF, generating documents from markdown, creating PDF reports, or any markdown-to-pdf conversion task. Triggers on markdown to pdf, md to pdf, convert markdown pdf, generate pdf from markdown.
metadata:
  openclaw:
    requires:
      bins: ["python3"]
      anyBins: ["pandoc", "wkhtmltopdf"]
    install:
      - id: "pip"
        kind: "pip"
        packages: ["weasyprint", "markdown", "Pygments"]
        label: "Install Python dependencies (WeasyPrint)"
      - id: "apt-pandoc"
        kind: "apt"
        packages: ["pandoc", "wkhtmltopdf"]
        label: "Install pandoc and wkhtmltopdf (apt)"
      - id: "brew-pandoc"
        kind: "brew"
        formula: "pandoc"
        cask: "wkhtmltopdf"
        label: "Install pandoc and wkhtmltopdf (brew)"
    requirements:
      binaries:
        - python3
      binaries_optional:
        - pandoc
        - wkhtmltopdf
    openclaw:
      requires:
        network:
          - description: "No network required for local file conversion"
        write_access:
          - description: "Writes PDF output to specified output path"
---

# Markdown to PDF Converter

Convert Markdown files to PDF with professional formatting. Supports multiple backends for different use cases.

## Backends

### Primary: WeasyPrint (Pure Python)
- **Pros**: No system dependencies, pip install only, good CSS support
- **Cons**: Slightly slower on large documents
- **Use for**: Most use cases, especially when you can't install system packages

### Optional: Pandoc + wkhtmltopdf
- **Pros**: Most powerful, LaTeX support, best typography
- **Cons**: Requires system package installation
- **Use for**: Academic papers, complex documents, LaTeX math

## Quick Start

```bash
# Using WeasyPrint (recommended, auto-installed)
python3 scripts/md_to_pdf.py input.md output.pdf

# Using Pandoc (if installed)
python3 scripts/md_to_pdf.py input.md output.pdf --backend pandoc
```

## Usage from Agent

### Basic Conversion

```python
# Convert markdown to PDF
exec("python3 skills/md-to-pdf-advanced/scripts/md_to_pdf.py /path/to/input.md /path/to/output.pdf")
```

### With Custom CSS

```python
# Apply custom theme
exec("python3 skills/md-to-pdf-advanced/scripts/md_to_pdf.py input.md output.pdf --css skills/md-to-pdf-advanced/assets/github-theme.css")
```

### With Options

```python
# Landscape, custom margins
exec("python3 skills/md-to-pdf-advanced/scripts/md_to_pdf.py input.md output.pdf --orientation landscape --margin 15mm")
```

## Features


- ✅ Syntax-highlighted code blocks
- ✅ Tables with styling
- ✅ Images (local and remote)
- ✅ Headers and footers with page numbers
- ✅ Custom CSS themes
- ✅ Page size and orientation options
- ✅ Adjustable margins

## CSS Themes

Available in `assets/`:
- `github-theme.css` - GitHub-like styling
- `minimal-theme.css` - Clean minimal look
- `academic-theme.css` - Academic paper style

## Troubleshooting

### WeasyPrint fails to install

```bash
# Install system dependencies first (Ubuntu/Debian)
sudo apt-get install python3-dev libffi-dev libxml2-dev libxslt1-dev

# Then install Python packages
pip3 install weasyprint markdown Pygments
```

### Images not showing

Use absolute paths or ensure images are relative to the markdown file location.

### Fonts look wrong

WeasyPrint uses system fonts. Install the fonts you reference in CSS:

```bash
# Ubuntu/Debian
sudo apt-get install fonts-liberation fonts-dejavu

# macOS
brew install --cask font-liberation
```
