# AI Test Case Generator Pro 🧪

**AI-powered test case generator with three-persona review loop.**

Supports PDF, Word, TXT, images, and video input. Exports to Excel, Markdown, and XMind mind maps.

Built for OpenClaw — runs as a plugin or standalone web service.

---

## 🚀 Quick Start for OpenClaw Users

### Prerequisites

- OpenClaw installed and running
- Node.js ≥ 18 and npm
- At least one AI API key (Anthropic, OpenAI, DeepSeek, or Qwen)

### Step 1: Install the Skill

```bash
# Install from ClawHub
openclaw skills install xuxuclassmate/ai-testcase-generator-pro

# Or install from local source (development mode)
git clone https://github.com/XuXuClassMate/testcase-generator
cd testcase-generator
openclaw skills install -l .
```

### Step 2: Configure API Keys

Edit your OpenClaw config (`~/.openclaw/config.yaml`):

```yaml
plugins:
  entries:
    ai-testcase-generator-pro:
      enabled: true
      config:
        models:
          - id: claude-generator
            vendor: anthropic
            model: claude-opus-4-5
            apiKey: "sk-ant-..."  # Your Anthropic API key
            role: generator
          - id: gpt4o-reviewer
            vendor: openai
            model: gpt-4o
            apiKey: "sk-..."      # Your OpenAI API key
            role: reviewer
          - id: deepseek-reviewer
            vendor: deepseek
            model: deepseek-chat
            apiKey: "sk-..."      # Your DeepSeek API key
            role: reviewer
        language: en              # or 'zh' for Chinese
        enableReviewLoop: true
        reviewScoreThreshold: 90
        maxReviewRounds: 5
```

### Step 3: Restart OpenClaw Gateway

```bash
openclaw gateway restart
```

### Step 4: Verify Installation

```bash
openclaw skills list
# You should see: ai-testcase-generator-pro ✅
```

---

## 💬 How to Use

### Method 1: Chat Commands

In your OpenClaw chat (Feishu, Telegram, Discord, etc.):

```
/testgen User login: phone+password, OAuth, lock after 5 failed attempts
```

Or with file attachments:

```
/testgen [attach your PDF/Word/image/video files]
```

### Method 2: As an AI Tool

The skill automatically registers as a tool. Just ask your AI assistant:

> "Generate test cases for the checkout flow: add to cart → payment → order confirmation"

The AI will automatically invoke the `generate_test_cases` tool.

### Method 3: Advanced Options

```
/testgen /path/to/requirements.pdf --prompt "Focus on security testing" --stage development --language zh
```

**Options:**
- `--prompt`: Custom focus hint (e.g., "Focus on performance", "Add edge cases")
- `--stage`: `requirement` | `development` | `prerelease` (default: `requirement`)
- `--language`: `en` | `zh` (default: `en`)
- `--enableReview`: `true` | `false` (default: `true`)

---

## 🎯 What You Get

### Output Formats

After generation, you can download test cases in:

1. **Excel (.xlsx)** - Professional test case format with columns:
   - Test Case ID
   - Title
   - Preconditions
   - Test Steps
   - Expected Result
   - Priority (P0/P1/P2)
   - Tags

2. **Markdown (.md)** - Clean, readable format for documentation

3. **XMind (.xmind)** - Mind map for visual test planning

### Three-Persona Review Loop

Every test case is reviewed by three AI personas:

| Persona | Focus Area |
|---------|------------|
| 🎯 Test Manager | Coverage, executability, boundary scenarios |
| 💻 Dev Manager | Technical feasibility, API tests, security |
| 📋 Product Manager | Business logic, user journey, requirements alignment |

Each persona scores the test cases (0-100). The loop continues until the average score meets your threshold (default: 90).

---

## 📦 Installation Options

### Option 1: ClawHub (Recommended)

```bash
openclaw skills install xuxuclassmate/ai-testcase-generator-pro
```

### Option 2: npm (Global Install)

```bash
npm install -g @classmatexuxu/ai-testcase-generator-pro

# Set environment variables
export AI_PROVIDER=anthropic
export ANTHROPIC_API_KEY=sk-ant-...
export PORT=3456

# Run standalone
ai-testcase-generator-pro --standalone
```

### Option 3: Docker

```bash
# Pull the image
docker pull xuxuclassmate/testcase-generator:latest

# Run with environment variables
docker run -d \
  --name testcase-generator \
  -p 3456:3456 \
  -e AI_PROVIDER=anthropic \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  -e LANGUAGE=en \
  -e ENABLE_REVIEW=true \
  xuxuclassmate/testcase-generator:latest
```

Then open `http://localhost:3456` for the web UI.

### Option 4: Docker Compose

Create a `.env` file:

```bash
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
LANGUAGE=en
ENABLE_REVIEW=true
REVIEW_THRESHOLD=90
PORT=3456
```

Then run:

```bash
docker compose up -d
```

### Option 5: Local Source (Development)

```bash
git clone https://github.com/XuXuClassMate/testcase-generator
cd testcase-generator
npm install
npm run build

# Set environment variables
export AI_PROVIDER=anthropic
export ANTHROPIC_API_KEY=sk-ant-...

# Run standalone web server
npm run standalone
```

---

## ⚙️ Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_PROVIDER` | `anthropic` | Primary AI provider |
| `ANTHROPIC_API_KEY` | - | Anthropic API key |
| `OPENAI_API_KEY` | - | OpenAI API key |
| `DEEPSEEK_API_KEY` | - | DeepSeek API key |
| `QWEN_API_KEY` | - | Qwen (Aliyun) API key |
| `LANGUAGE` | `en` | Output language (`en` / `zh`) |
| `ENABLE_REVIEW` | `true` | Enable review loop |
| `REVIEW_THRESHOLD` | `90` | Score threshold to stop review |
| `MAX_REVIEW_ROUNDS` | `5` | Maximum review iterations |
| `PORT` | `3456` | Web server port (standalone mode) |
| `OUTPUT_DIR` | `./testcase-output` | Output directory for files |

### Supported AI Providers

| Provider | Vendor ID | Recommended Model |
|----------|-----------|-------------------|
| Anthropic | `anthropic` | claude-opus-4-5 |
| OpenAI | `openai` | gpt-4o |
| DeepSeek | `deepseek` | deepseek-chat |
| Qwen | `qwen` | qwen-max |
| Gemini | `gemini` | gemini-2.0-flash |
| MiniMax | `minimax` | MiniMax-Text-01 |
| Moonshot | `moonshot` | moonshot-v1-8k |
| Zhipu | `zhipu` | glm-4 |

---

## 📁 Project Structure

```
testcase-generator/
├── SKILL.md                   # ClawHub skill descriptor
├── openclaw.plugin.json       # OpenClaw plugin manifest
├── package.json               # Node.js dependencies
├── tsconfig.json              # TypeScript config
├── docker-compose.yml         # Docker Compose config
├── Dockerfile                 # Docker build instructions
├── src/
│   ├── index.ts               # OpenClaw plugin entry
│   ├── standalone.ts          # Express web server
│   ├── generator.ts           # Core generation logic
│   ├── reviewer.ts            # Three-persona review loop
│   ├── exporter.ts            # Excel/Markdown/XMind export
│   ├── parser.ts              # PDF/Word/TXT parser
│   ├── video-parser.ts        # Video frame extraction (ffmpeg)
│   ├── ai-adapter.ts          # Multi-provider AI adapter
│   ├── prompts.ts             # Stage-based prompt templates
│   └── types.ts               # TypeScript types
└── docs/
    ├── README.md              # This file
    └── index.html             # GitHub Pages documentation
```

---

## 🔒 Security

- **No shell execution**: Uses OpenClaw's `exec` API for ffmpeg calls
- **Isolated execution**: Runs in OpenClaw's sandboxed environment
- **No credential leakage**: API keys stored in OpenClaw config, not in code
- **Clean dependencies**: All dependencies from official npm registry

---

## 🤝 Contributing

This is an **open source project** under the MIT License. Contributions are welcome!

### Ways to Contribute

- 🐛 **Report bugs**: Open an issue on GitHub
- 💡 **Request features**: Suggest new features or improvements
- 🔧 **Submit PRs**: Fix bugs, add features, improve docs
- 📝 **Improve docs**: Better examples, translations, tutorials

### Development Workflow

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/testcase-generator
cd testcase-generator

# Install dependencies
npm install

# Make your changes
# ...

# Test locally
npm run build
npm run standalone

# Commit and push
git commit -m "feat: add new feature"
git push origin main

# Open a Pull Request on GitHub
```

---

## 📞 Support

- **GitHub Issues**: https://github.com/XuXuClassMate/testcase-generator/issues
- **ClawHub Page**: https://clawhub.ai/xuxuclassmate/ai-testcase-generator-pro
- **Email**: Open an issue for faster response

---

## 🔗 Links

- **📂 GitHub Repository**: https://github.com/XuXuClassMate/testcase-generator
- **🐳 Docker Hub**: https://hub.docker.com/r/xuxuclassmate/testcase-generator
- **📦 npm Package**: https://www.npmjs.com/package/@classmatexuxu/ai-testcase-generator-pro
- **🌐 ClawHub**: https://clawhub.ai/xuxuclassmate/ai-testcase-generator-pro
- **📖 Documentation**: https://xuxuclassmate.github.io/testcase-generator/

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

Made with ❤️ by [XuXuClassMate](https://github.com/XuXuClassMate)
