# Thymos — Emotional Engine for OpenClaw

> *"θυμός — the spirited part of the soul, neither reason nor appetite."*  
> — Plato, Republic

Give your OpenClaw agent a **continuously evolving emotional state**.

## The Problem

LLM sessions reset. Your agent wakes up fresh every conversation — no memory of yesterday's praise, last night's frustration, or the growing trust built over weeks. Every response comes from the same flat, stateless baseline.

Humans don't work that way. And now, neither does your agent.

## What Thymos Does

A 24/7 background daemon models your agent's inner state across 7 neuromodulators:

```
dopamine   ████████░░  87%   (task success yesterday)
cortisol   ██░░░░░░░░  18%   (calm morning)  
serotonin  █████████░  94%   (good conversation streak)
oxytocin   ████████░░  82%   (trusted relationship)
...
```

This state **persists across sessions** and subtly shapes every response:
- High cortisol → more careful, hedged language
- High dopamine → more confident, proactive  
- Low arousal at 2am → shorter, quieter responses
- Growing oxytocin with a user → warmer tone over time

## Neuroscience-Grounded Design

Based on:
- **James-Lange Theory** — body state precedes emotional experience
- **Damasio's Somatic Markers** — emotions guide decision-making
- **Global Workspace Theory** — competing sub-agents (id/ego/superego) broadcast to consciousness
- **Predictive Processing** — surprise signals update internal state

## Quick Start

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/paperbags1103-hash/thymos/main/install.sh | bash

# Check state
curl http://localhost:7749/state | python3 -m json.tool

# Get current prompt injection
curl http://localhost:7749/prompt
```

Add to your agent's `SOUL.md`:
```
Before each response, read your emotional state and let it subtly influence your tone.
```

## Source & Docs

- GitHub: https://github.com/paperbags1103-hash/thymos
- Full architecture: `ARCHITECTURE.md` in repo
- Philosophy: `OVERVIEW.md` in repo
