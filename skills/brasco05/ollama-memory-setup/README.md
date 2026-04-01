# ollama-memory-setup

Fix OpenClaw's `node-llama-cpp is missing` error and enable semantic memory search using Ollama locally — no API keys, no cloud, fully private.

## Problem

OpenClaw's native memory search requires `node-llama-cpp` which frequently fails to install:

```
Local embeddings unavailable.
Reason: optional dependency node-llama-cpp is missing (or failed to install).
```

## Solution

This skill routes memory embeddings through Ollama's local API using `nomic-embed-text` — a fast, small (~270MB), high-quality embedding model. No API keys needed.

## Quick Start

```bash
bash ~/.openclaw/workspace/skills/ollama-memory-setup/scripts/setup.sh
openclaw gateway restart
```

## Requirements

- macOS (Homebrew) or Linux
- OpenClaw installed
- ~300MB disk space for the embedding model

## Verify

After setup, test in your agent session:
```
memory_search("test")
```
Response should include `"provider": "ollama"`.

## Links

- [Ollama](https://ollama.com)
- [nomic-embed-text](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5)
- [OpenClaw docs](https://docs.openclaw.ai)
