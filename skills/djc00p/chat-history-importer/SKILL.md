---
name: chat-history-importer
description: "Import AI conversation exports (OpenAI ChatGPT and Anthropic Claude) into your agent's episodic memory. Parses export files, writes daily memory summaries, and deduplicates on re-runs. Trigger phrases: import chat history, ingest conversation export, import chatgpt export, import claude export, load AI conversation history."
metadata: {"clawdbot":{"emoji":"📥","requires":{"bins":["python3"]},"env":[],"os":["linux","darwin","win32"],"homepage":"https://clawhub.com/djc00p/chat-history-importer"}}
---

# Chat History Importer

Import years of AI conversations into searchable episodic memory. Parse ChatGPT and Claude exports and create dated daily memory files your agent can search and reference.

## Quick Start

1. Export from OpenAI: Settings → Data Controls → Export data → `conversations.json`
2. Export from Anthropic: Settings → Privacy → Export data → `conversations.json` in zip
3. Dry run first: `python3 scripts/batch.py --dir ~/Downloads/chat_exports --dry-run`
4. Import: `python3 scripts/batch.py --dir ~/Downloads/chat_exports`

## Key Concepts

- **Auto-detection:** Identifies OpenAI vs Anthropic format automatically — no flags needed
- **Episodic memory:** Writes daily summaries to `memory/episodic/YYYY-MM-DD.md`
- **Deduplication:** Chat IDs tracked — re-running the same export never creates duplicates
- **OPENCLAW_WORKSPACE:** Set this env var to point imports to the right agent workspace

## Common Usage

```text
# Dry run — preview what would be imported without writing anything
python3 scripts/batch.py --dir ~/Downloads/chat_exports --dry-run

# Import all conversations
python3 scripts/batch.py --dir ~/Downloads/chat_exports

# Import only conversations since a date
python3 scripts/batch.py --dir ~/Downloads/chat_exports --since 2025-01-01

# Force a specific format (auto-detects by default)
python3 scripts/batch.py --dir ~/Downloads/chat_exports --format anthropic

# Verbose — show message count + first user message per chat
python3 scripts/batch.py --dir ~/Downloads/chat_exports --dry-run --verbose
```

**Tip:** Use `--dry-run --verbose` first to see message counts and previews — great for identifying meaty conversations worth deeper analysis.

## References

- `references/export-formats.md` — Detailed OpenAI and Anthropic export formats, normalization rules

---

**Original implementation by @djc00p**
