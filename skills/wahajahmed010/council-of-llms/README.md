# Council of LLMs

> **Don't take one model's word for it.**

Multi-model deliberation for high-stakes decisions. The Council of LLMs routes a single question to multiple AI models simultaneously, surfaces their agreements and disagreements, and presents a structured analysis — so you get rigorous, cross-model insight instead of a single potentially-biased answer.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Quick Start

```bash
# Install
clawhub install wahajahmed010/council-of-llms

# Run with default question (demo)
council

# Run with your own question
council "Should we use JWT or session cookies for auth?"

# Interactive model selection
council --select-models "Architecture decision"
```

## What It Does

```
Your Question
     ↓
[Multiple LLMs] → Parallel deliberation
     ↓
[Analysis] → Agreements, disagreements, synthesis
     ↓
[Report] → Structured verdict with confidence
```

## When to Use

| ✅ Use Council | ❌ Skip Council |
|----------------|-----------------|
| Security audits | Quick lookups |
| Architecture decisions | Casual chat |
| Policy analysis | First drafts |
| LLM output evaluation | Simple facts |

## Pre-requisites

- **OpenClaw with 2+ LLM providers** (required)
- **Recommended:** Ollama Cloud for parallel execution

## Documentation

- [SKILL.md](SKILL.md) — Full usage guide
- [examples/outputs.md](examples/outputs.md) — Sample outputs

## License

MIT © 2026 Wahaj Ahmed
