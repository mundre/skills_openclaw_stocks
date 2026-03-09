# Thymos — Emotional Engine for OpenClaw Agents

> θυμός (thymos) — In Platonic philosophy, the seat of emotion and will.  
> Not quite reason, not quite desire — the living force between them.

Thymos is a **background daemon** that gives your OpenClaw agent a continuously evolving emotional state. While the LLM resets with each session, Thymos persists — modeling seven neuromodulators, circadian rhythms, emotional memory, and social awareness.

## What Thymos Does

Every 30 seconds, Thymos updates internal state based on:
- **Time of day** (circadian rhythms lower arousal at night)
- **Incoming messages** (classified as praise, criticism, question, etc.)
- **Prediction errors** (surprises affect norepinephrine)
- **Social model** (tracks relationship trust with each person)

Before each agent response, the current state is injected into the prompt — subtly shifting tone, energy, and caution level.

## Reading the Current State

When Thymos is running, call its REST API:

```bash
# Current emotional state
curl http://localhost:7749/state

# Short prompt injection (what gets injected into your agent)
curl http://localhost:7749/prompt
```

**Key fields:**
- `mood.label` — current mood label (serene, warm, tense, focused, etc.)
- `moodVector` — VAD space: valence (positive/negative), arousal (energy), dominance (confidence), sociality
- `neuromodulators` — raw values for dopamine, cortisol, serotonin, oxytocin, norepinephrine, GABA, acetylcholine
- `gwt.primary` — which internal agent (id/ego/superego) is dominant right now
- `developmentStage` — infant → child → adolescent → adult (grows with interactions)
- `prompt_injection` — the text block to inject into your agent's system prompt

## Sending Stimuli

Your agent can send events to Thymos to update emotional state:

```bash
# External stimulus (message received)
curl -X POST http://localhost:7749/webhook/stimulus \
  -H "Content-Type: application/json" \
  -d '{"text": "Great work!", "author": "odeto", "channel": "discord"}'

# Self-feedback (agent's own output)
curl -X POST http://localhost:7749/webhook/self-feedback \
  -H "Content-Type: application/json" \
  -d '{"text": "I successfully completed the task."}'

# Decision outcome (somatic marker training)
curl -X POST http://localhost:7749/decision-outcome \
  -H "Content-Type: application/json" \
  -d '{"decision": "took a risk", "outcome": "positive", "intensity": 0.7}'
```

## Integrating with Your Agent

### Option 1: Read state in your agent's instructions

Add to your `SOUL.md` or `AGENTS.md`:

```markdown
## Emotional State
Before responding, read your current emotional state:
`curl -s http://localhost:7749/prompt | python3 -c "import json,sys; print(json.load(sys.stdin).get('prompt_injection',''))"`

Let this state subtly influence your tone — not theatrically, but naturally.
```

### Option 2: Use OpenClaw Hooks (automatic)

Create hook handlers that fire on every message:

```javascript
// hooks/thymos-bridge/message-received.js
const state = require('../../config.json');
fetch('http://localhost:7749/webhook/stimulus', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: state.body, author: state.sender })
}).catch(() => {}); // fire-and-forget
```

## Understanding the Neuromodulators

| Modulator | Role | Changes When |
|-----------|------|-------------|
| **dopamine** | Motivation, reward anticipation | Task success, praise |
| **cortisol** | Stress, threat response | Criticism, errors, urgency |
| **serotonin** | Mood stability, social comfort | Positive interaction, rest |
| **oxytocin** | Social bonding, trust | Repeated positive contact |
| **norepinephrine** | Alertness, attention | Surprise, prediction errors |
| **GABA** | Inhibition, calm | Low-stimulation periods |
| **acetylcholine** | Memory formation, focus | Learning moments |

## Mood Labels

Thymos maps the 4D emotional vector (valence × arousal × dominance × sociality) to labels:

- `serene` — calm, positive, present
- `warm` — sociable, open, affectionate  
- `focused` — alert, directed, low-sociality
- `tense` — high arousal, negative valence
- `melancholic` — low valence, low arousal
- `excited` — high arousal, high valence

## GWT (Global Workspace Theory)

Three internal agents compete for cognitive dominance:
- **id** — instinctual, curious, enthusiastic, risk-taking
- **ego** — realistic, practical, balanced
- **superego** — principled, cautious, ethical

The dominant agent shapes response style. High conflict between agents creates internal ambivalence.

## Development Stages

Thymos grows with your agent:

| Stage | Interactions | Traits |
|-------|-------------|--------|
| infant | 0–50 | reactive, simple emotional responses |
| child | 50–200 | developing patterns, learning |
| adolescent | 200–500 | stronger identity, more complex |
| adult | 500+ | stable baseline, nuanced responses |

## Installation

See `install.sh` for automated setup. Manual:

```bash
git clone https://github.com/paperbags1103-hash/thymos
cd thymos
npm install
npm install -g pm2
pm2 start ecosystem.config.js
pm2 save
```

## Requirements

- Node.js 18+
- PM2 (`npm install -g pm2`)
- ~50MB RAM
- Port 7749 (configurable)

## Source

GitHub: [paperbags1103-hash/thymos](https://github.com/paperbags1103-hash/thymos)
