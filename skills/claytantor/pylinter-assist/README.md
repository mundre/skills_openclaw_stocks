# pylinter-assist

Context-aware Python linting with smart pattern heuristics for PR review.

A soft PR reviewer that combines Pylint with custom pattern checks to catch hardcoded secrets, missing FastAPI docstrings, and other issues traditional linters miss. Complements hard CI tests; branches are assignable by the user.

## Quick Start

```bash
# Install dependencies
uv sync

# Install CLI for direct command usage
uv pip install -e .

# Lint your project
lint-pr files src/ --format markdown
```

## GitHub Actions (Recommended for PRs)

Automatically lint PRs by adding the workflow to your repository:

```bash
mkdir -p .github/workflows
curl -o .github/workflows/lint-pr.yml \
  https://raw.githubusercontent.com/claytantor/pylinter-assist/main/.github/workflows/lint-pr.yml
```

See [GitHub Actions Integration](#github-actions-integration) for full setup instructions.

## Features

| Check | Code | Severity | Catches |
|-------|------|----------|---------|
| Pylint | C/W/R/E/F | varies | Standard Python quality issues |
| Hardcoded password/secret | HCS001 | ERROR | `password = "abc123"` |
| Credentials in URL | HCS002 | ERROR | `https://user:pass@host` |
| Hardcoded IP address | HCS003 | ERROR | `HOST = "10.0.0.5"` |
| Hardcoded localhost URL | HCS004 | ERROR | `"http://localhost:8000"` |
| AWS/GCP access key | HCS005 | ERROR | `AKIAIOSFODNN7EXAMPLE` |
| FastAPI missing docstring | FAD001 | WARNING | `@router.get("/")` without docstring |
| useEffect missing deps | RUE001 | WARNING | `useEffect(() => { ... })` with no `[]` |
| useEffect suspicious deps | RUE002 | INFO | `useEffect(..., [])` references outer vars |

## Installation

### Option A: Install via pip (recommended for CLI access)

First, sync dependencies:

```bash
uv sync
```

Then install the CLI for direct command usage:

```bash
uv pip install -e .
```

After installation, `lint-pr` is available as a direct command.

### Option B: Use uv scripts (no installation required)

```bash
uv sync
uv lint-pr [TARGET] [OPTIONS]
```

### Option C: Run via wrapper script

```bash
uv sync
./scripts/lint-pr [TARGET] [OPTIONS]
```

## Usage

```bash
lint-pr [TARGET] [OPTIONS]
```

> **Note:** All three installation options provide the same `lint-pr` command. Choose based on your needs:
> - Option A: Best for production use, CLI available system-wide
> - Option B: Best for development, no installation needed
> - Option C: Best when working directly from source

### Targets

| Target | Description |
|--------|-------------|
| `pr <number>` | Lint all files changed in a GitHub PR |
| `staged` | Lint git-staged files |
| `diff <file>` | Lint files from a unified diff file |
| `files <path>...` | Lint explicit files or directories |

### Options

| Flag | Description |
|------|-------------|
| `--format text\|json\|markdown` | Output format (default: markdown) |
| `--config <path>` | Custom `.linting-rules.yml` path |
| `--post-comment` / `--no-post-comment` | Post result as GitHub PR comment |
| `--fail-on-warning` | Also fail on warnings (default: errors only) |

### Examples

```bash
# Lint PR #42 and post a comment
lint-pr pr 42 --post-comment

# Lint staged files before commit
lint-pr staged

# Lint a diff file
lint-pr diff /tmp/changes.diff

# Lint specific files
lint-pr files src/ tests/

# Use custom rules
lint-pr files src/ --config .linting-rules.yml
```

## Configuration

Copy `.linting-rules.yml` to your project root and edit:

```yaml
pylint:
  enabled: true
  disable: [C0114, C0115]   # suppress module/class docstring warnings

hardcoded_secrets:
  enabled: true
  skip_ip_check: false

fastapi_docstring:
  severity: warning

react_useeffect_deps:
  severity: warning

github:
  post_comment: true
  fail_on_error: true
  fail_on_warning: false
```

## Publishing to ClawHub

```bash
# Install dependencies
uv sync

# Publish the skill
make publish

# Auto-increment minor version and publish
make publish-bump

# Dry run before publishing
make publish-dry-run
```

## Development

```bash
# Run tests
uv run pytest

# Format code
uv run ruff format .

# Lint code
uv run pylint pylinter_assist
```

## GitHub Actions Integration

Automatically lint PRs in your project using the provided GitHub Actions workflow.

### Setup

1. **Clone or download the workflow file**

   Copy `.github/workflows/lint-pr.yml` to your project:

   ```bash
   mkdir -p .github/workflows
   curl -o .github/workflows/lint-pr.yml \
     https://raw.githubusercontent.com/claytantor/pylinter-assist/main/.github/workflows/lint-pr.yml
   ```

2. **Add configuration file** (optional)

   Copy `.linting-rules.yml` to your project root and customize:

   ```bash
   curl -o .linting-rules.yml \
     https://raw.githubusercontent.com/claytantor/pylinter-assist/main/.linting-rules.yml
   ```

3. **Commit and push**

   The workflow will automatically trigger on PRs.

### Workflow Triggers

| Trigger | Description |
|---------|-------------|
| `pull_request` | Auto-lints all files changed in a PR |
| `workflow_dispatch` | Manual trigger via GitHub UI or API |

### Manual Trigger via GitHub UI

1. Go to your repository's **Actions** tab
2. Select **Pylint Assist** workflow
3. Click **Run workflow**
4. Choose branch and optional inputs:
   - PR number (leave empty for current branch)
   - Output format (markdown, text, json)
   - Config path
   - Post comment (true/false)

### Manual Trigger via GitHub CLI

```bash
gh workflow run lint-pr.yml \
  -f pr_number=42 \
  -f format=markdown \
  -f post_comment=true
```

### Manual Trigger via API

```bash
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/OWNER/REPO/actions/workflows/lint-pr.yml/dispatches \
  -d '{"ref":"main","inputs":{"pr_number":"42","format":"markdown","post_comment":"true"}}'
```

### Workflow Permissions

The workflow requires these permissions:

```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write
```

### Output Artifacts

Every run generates a `lint-report.json` artifact available for 14 days.

## License

MIT
