---
name: council-of-llms
emoji: 🏛️
description: Multi-model deliberation for high-stakes decisions. Don't take one model's word for it.
details: |
  **Council of LLMs** orchestrates structured multi-model debate — routing a single question to multiple LLMs simultaneously, collecting their answers, and surfacing agreements/disagreements.

  ## Best For
  - Security audits
  - Architecture decisions  
  - Policy analysis
  - LLM output evaluation

  ## Pre-requisites
  - OpenClaw with 2+ LLM providers configured
  - Recommended: Ollama Cloud for parallel execution

  ## Quick Start

  ```bash
  # Run with demo question
  council

  # Run with your question
  council "Should we use JWT or session cookies?"

  # Interactive model selection
  council --select-models "Architecture decision"
  ```

  ## Usage

  ### Model Selection
  ```bash
  # List available models
  council --list-models

  # Explicit model list
  council "Security audit" --models "ollama/kimi-k2.5,openai/gpt-4o"

  # Use preset
  council "Code review" --preset security
  ```

  ### Configuration
  ```bash
  # Sequential mode (limited hardware)
  council "Question" --sequential

  # Extended timeout
  council "Question" --timeout 180

  # Export results
  council "Question" --output report.md
  ```

  ## Safeguards
  - Timeout per model: 120s (configurable)
  - Cost cap: 50K tokens
  - Max rounds: 2
  - Model diversity required
  - Rate limiting

  ## When NOT to Use
  - Quick factual lookups
  - Real-time applications
  - Cost-sensitive products
  - Tasks requiring consistent answers

install:
  - npm install -g clawhub
  - clawhub install wahajahmed010/council-of-llms

---

# Council of LLMs

Multi-model deliberation for high-stakes decisions. Don't take one model's word for it.

**Version:** 1.0.0  
**License:** MIT  
**Author:** Wahaj Ahmed

## Overview

The Council of LLMs orchestrates structured multi-model debate — routing a single question to multiple LLMs simultaneously, collecting their answers, and surfacing agreements/disagreements. Built for decisions where being wrong costs more than the overhead of multiple perspectives.

**Best for:** Security audits, architecture decisions, policy analysis, LLM output evaluation  
**Not for:** Quick lookups, casual chat, first drafts

## Pre-requisites

- **OpenClaw with multiple LLM providers configured** (required)
  - Verify: `openclaw status` shows 2+ providers
  - Examples: `ollama/kimi-k2.5`, `openai/gpt-4o`, `anthropic/claude-3-opus`

- **Multi-model access** (recommended)
  - Local Ollama: Can run 1 model at a time (sequential mode)
  - **Recommended: Ollama Cloud** — parallel multi-model execution
    - Sign up: https://ollama.com/cloud
    - Configure: `openclaw config set ollama.cloud.token=YOUR_TOKEN`

## Installation

### Via ClawHub (Recommended)

```bash
clawhub install wahajahmed010/council-of-llms
```

### Manual

```bash
cd ~/.openclaw/skills
git clone https://github.com/wahajahmed010/council-of-llms.git
```

## Usage

### Quick Start (Zero Config)

```bash
# Run with built-in sample question
council

# Run with your own question
council "Should we use JWT or session cookies for auth?"

# Security audit example
council --review "Analyze this Python function for security issues" --input ./auth.py
```

### Model Selection

```bash
# List available models
council --list-models

# Interactive model selection
council "Architecture decision" --select-models

# Explicit model list
council "Security audit" --models "ollama/kimi-k2.5,openai/gpt-4o,anthropic/claude-3-opus"

# Use specific council preset
council "Code review" --preset security
```

### Configuration

```bash
# Sequential mode (for limited hardware)
council "Question" --sequential

# Extended timeout for complex analysis
council "Question" --timeout 180

# Export results
council "Question" --output report.md
```

## How It Works

### Architecture

```
User Question
      ↓
[Pre-flight Check] → Verify 2+ models available
      ↓
[Agent Spawning] → Spawn 2-3 agents with different models
      ↓
[Round 1: Opening] → Each agent provides initial analysis
      ↓
[Round 2: Rebuttal] → Agents respond to each other's points
      ↓
[Synthesis] → Compare positions, find agreements/disagreements
      ↓
[Report] → Structured output with verdict
```

### Fallback Mode

If `sessions_spawn` is unavailable, the skill automatically switches to **single-prompt multi-persona simulation** — all "agents" represented as sections in one prompt. Slightly less authentic but works everywhere.

## Output Format

```markdown
# Council Report: [Question]

## Participants
- Strategist (ollama/kimi-k2.5)
- Security Expert (openai/gpt-4o)
- Pragmatist (anthropic/claude-3-opus)

## Individual Positions

### Strategist
**Stance:** JWT with short expiry
**Key Points:**
- Stateless authentication scales horizontally
- Reduces database lookups
- Industry standard for microservices

### Security Expert
**Stance:** Session cookies with httpOnly
**Key Points:**
- XSS protection via httpOnly flag
- Easier revocation on compromise
- No token storage complexity

### Pragmatist
**Stance:** Hybrid approach
**Key Points:**
- Sessions for web, JWT for API
- Best of both worlds
- Implementation overhead worth it

## Agreement Matrix

| Point | Strategist | Security | Pragmatist |
|-------|------------|----------|------------|
| Stateless scaling | ✅ | ⚠️ | ✅ |
| XSS protection | ⚠️ | ✅ | ✅ |
| Revocation ease | ⚠️ | ✅ | ✅ |
| Implementation | ✅ | ✅ | ⚠️ |

## Key Disagreements

1. **Security vs Scalability**: Security Expert prioritizes safety over performance
2. **Complexity**: Strategist sees JWT as simpler; Security Expert sees sessions as simpler

## Synthesis

**Consensus:** Hybrid approach recommended for most teams
**Dissent:** Security Expert maintains pure sessions for high-security contexts
**Confidence:** Medium (genuine disagreement on trade-offs)

## Recommendation

Start with session cookies. Migrate to JWT only if:
- Horizontal scaling becomes bottleneck
- Stateless requirement is critical
- Team has JWT expertise

---
*Generated by Council of LLMs v1.0.0*
*Models: kimik2.5, gpt-4o, claude-3-opus*
*Time: 45s | Tokens: 12,847*
```

## Safeguards

The skill includes automatic protections:

| Safeguard | Default | Description |
|-----------|---------|-------------|
| Timeout per model | 120s | Kills slow models, proceeds with others |
| Cost cap | 50K tokens | Hard stop if projection exceeds limit |
| Max rounds | 2 | Prevents infinite deliberation |
| Model diversity | Required | Rejects if all models same provider |
| Rate limiting | 10/min | Prevents accidental spam |
| Partial failure | Continue | Works even if 1 model fails |
| Context budget | 70% window | Fails fast before overflow |
| User opt-in | Required | Shows cost estimate before run |

## Configuration

`~/.openclaw/council-config.json`:

```json
{
  "default_models": [
    "ollama/kimi-k2.5",
    "openai/gpt-4o",
    "anthropic/claude-3-opus"
  ],
  "timeout": 120,
  "max_tokens_per_model": 8192,
  "cost_warning_threshold": 25000,
  "sequential_fallback": true,
  "output_format": "markdown",
  "presets": {
    "security": {
      "models": ["openai/gpt-4o", "anthropic/claude-3-opus"],
      "system_prompt": "security-expert"
    },
    "architecture": {
      "models": ["ollama/kimi-k2.5", "anthropic/claude-3-opus"],
      "system_prompt": "systems-architect"
    }
  }
}
```

## Limitations

- **Speed:** 2-3x slower than single model (parallel helps)
- **Cost:** Multiplies by number of models
- **Not for:** Simple facts, casual chat, first drafts
- **Diversity is limited:** Most models share training data biases

## When NOT to Use

- Simple factual queries (weather, definitions)
- Real-time applications (chat, support bots) where latency matters
- Cost-sensitive products with limited API budgets
- Tasks requiring authoritative, consistent answers (legal, medical — a council of conflicting advice is dangerous)

## License

MIT © 2026 Wahaj Ahmed
