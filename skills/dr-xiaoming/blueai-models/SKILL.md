---
name: blueai-models
description: |
  Configure and manage AI models from BlueAI unified proxy service for OpenClaw.
  Use when: (1) adding new models to openclaw.json, (2) choosing the right model for a task,
  (3) setting up multi-model strategy, (4) switching or comparing models,
  (5) troubleshooting model connectivity, (6) user asks about available models or pricing.
  Covers: Claude, GPT, Gemini, DeepSeek, Qwen, Doubao, Kimi, Grok, MiniMax via BlueAI relay.
---

# BlueAI Models for OpenClaw

## Quick Start

Add a model to OpenClaw:
```bash
python3 scripts/add_model.py gemini-2.5-flash --alias flash
python3 scripts/add_model.py claude-sonnet-4-6 --alias sonnet
openclaw gateway restart
```

Test connectivity:
```bash
python3 scripts/test_model.py gemini-2.5-flash
python3 scripts/test_model.py --all-configured
```

List available models:
```bash
python3 scripts/add_model.py --list
```

## Endpoints

| Type | Base URL | Note |
|------|----------|------|
| Claude (Anthropic) | `https://bmc-llm-relay.bluemediagroup.cn` | **No /v1** |
| Everything else (OpenAI) | `https://bmc-llm-relay.bluemediagroup.cn/v1` | **With /v1** |

Same API key works for all models.

## Model Selection Quick Guide

| Need | Model | Why |
|------|-------|-----|
| Cheapest + good | `gemini-2.5-flash` | $0.15/M in, 1M context |
| Best Chinese | `DeepSeek-V3.2` | Top Chinese quality, cheap |
| Vision + cheap | `gpt-4o-mini` or `gemini-2.5-flash` | Image input, low cost |
| Strong reasoning | `o4-mini` or `DeepSeek-R1` | CoT reasoning |
| Best overall | `claude-opus-4-6-v1` | 128K output, Agent coding |
| Balanced | `claude-sonnet-4-6` | 1/5 Opus price, most tasks |
| Code specialist | `gpt-5.2-codex` | 128K output, code focused |
| Ultra-long context | `xai.grok-4-fast-non-reasoning` | 2M tokens |

## References

- **Full model catalog**: Read `references/model-catalog.md` for all 100+ models with specs
- **OpenClaw config guide**: Read `references/openclaw-config.md` for JSON structure and examples
- **Model selection decision tree**: Read `references/model-selection.md` for task-based recommendations

## Key Rules

1. Claude models use `api: "anthropic-messages"`, baseUrl without `/v1`
2. All other models use `api: "openai-completions"`, baseUrl with `/v1`
3. DeepSeek/Qwen text models: set `input: ["text"]` only (no image)
4. MiniMax: must use OpenAI endpoint, does not support Claude endpoint
5. `gemini-3-pro-preview` deprecated 2026-03-26 → use `gemini-3.1-pro-preview`
6. After config changes: `openclaw gateway restart`
