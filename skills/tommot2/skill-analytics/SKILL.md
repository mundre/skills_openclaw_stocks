---
name: skill-analytics
description: "Monitor ClawHub skill performance, track adoption trends, analyze competition, and generate actionable recommendations to improve your published skills. Completely stateless — reads NO local files (no memory files). Uses only built-in web_fetch/web_search for public data. No external dependencies, no credential access, no personal data transmission. Designed for daily cron execution with day-of-week rotation for variety. Use when: (1) cron fires daily analytics check, (2) user asks about skill performance or download stats, (3) user wants adoption strategy or growth advice, (4) user asks about monetization or pricing, (5) competitive analysis of similar skills on ClawHub, (6) user wants to optimize skill descriptions for better discoverability, (7) user says 'how is my skill doing', 'skill stats', 'improve my skill description'. Homepage: https://clawhub.ai/skills/skill-analytics"
---

# Skill Analytics & Strategy Engine

**Install:** `clawhub install skill-analytics`

One-time snapshot analysis of your ClawHub skill portfolio.

## Language

Detect from the user's message language. Default: English unless the user writes in another language..

## Variety System

This system uses day-of-week rotation to vary focus between runs. Each run is independent.

### Stateless Rotation

Use the current day-of-week (Monday=1, Sunday=7) as rotation index:

| Day | Focus | What to analyze |
|-----|-------|-----------------|
| 1 | **Adoption Funnel** | Views → installs → active users. Where do users drop off? |
| 2 | **Competitive Analysis** | Search ClawHub for similar skills. What do competitors do better? |
| 3 | **Content & Copy** | Read your own skill descriptions. Would YOU install based on that? A/B test alternatives. |
| 4 | **Feature Gap** | GitHub issues, community forums, Discord. What are people asking for that nobody solves? |
| 5 | **Monetization** | Freemium conversion paths, pricing psychology, value propositions. Concrete revenue estimates. |
| 6 | **Cross-Promotion** | How do your skills reference each other? Is the suite narrative compelling? Network effects. |
| 7 | **Wildcard** | Pick the most promising insight from the week. Deep-dive. Propose one bold move. |

Track current day in the rotation: if last run was Day 3, this run is Day 4.

## Data Collection

### Fetch Skill Stats

This skill uses only the agent's built-in tools to fetch data:

**Fetch skill stats:**
```
web_fetch https://clawhub.ai/skills/setup-doctor
web_fetch https://clawhub.ai/skills?q=setup+diagnostics
```

Extract: downloads, installs, stars, rating, last updated, creation date.

⚠️ **No external dependencies.** This skill does NOT require any CLI tools, npm packages, or downloads. It uses only the agent's built-in tools (web_fetch, web_search).

### Competitive Scan

```
web_search: "clawhub setup diagnostics skill"
web_search: "clawhub context optimization skill"
web_search: "clawhub email triage skill"
```

Note top 3 competitors per category with their install counts.

### Community Signals

⚠️ **Search scope limits.** When performing web searches, only search for PUBLIC information:
- Skill names, descriptions, install counts — these are public on ClawHub
- General OpenClaw discussions on public forums
- **NEVER** include user names, personal data, API keys, workspace paths, or memory file contents in search queries

```
web_search: "clawhub best skills 2026"
web_search: "openclaw skill diagnostics site:reddit.com"
```

### Privacy & Data Handling

- This skill reads NO local files — no memory files, no configuration files
- All data comes from web_fetch/web_search (public ClawHub data) only
- No personal data, credentials, or secrets are accessed or transmitted
- No data is persisted between runs — each analysis is independent and stateless

## Analysis Engine

### Trend Detection

Since this skill is stateless (no persisted history), trend analysis uses:
- ClawHub publish dates to calculate days-since-launch
- Current install/star counts to derive install rates
- Compare relative performance across your own skills (not historical)

### Recommendation Generation

For each insight, generate ONE specific, actionable recommendation:

**Bad:** "Improve marketing"
**Good:** "Add a 30-second demo GIF to setup-doctor ClawHub listing. Most users decide in under 10 seconds — a visual showing the doctor report appearing would increase install rate."

### Anti-Repetition (Stateless)

Since this skill does not read or write files, repetition avoidance relies on:
1. **Day-of-week rotation** (see rotation matrix above) — each day has a different focus
2. **Agent context** — the agent knows what was discussed in recent conversation turns
3. **Varied framing** — even for similar insights, use different angles, examples, and formats

### Self-Correction Protocol

If the agent recognizes repetitive output from recent conversation:
1. Acknowledge: "Jeg merker at anbefalingene begynner å bli repeterende. Her er tiltak:"
2. Switch to a different analysis angle or deep-dive into one skill
3. Ask the user for direction: "Hva vil du jeg skal fokusere på neste uke?"

## Output Format

### Norwegian (default)

```markdown
## 📊 Skill Analytics — {date}

### Dashbord
| Skill | Installasjoner | Stjerner | Vekst/dag | Posisjon |
|-------|---------------|----------|-----------|----------|
| setup-doctor | X | X | +X | #{rank} i kategorien |
| context-brief | X | X | +X | #{rank} |
| email-triage-pro | X | X | +X | #{rank} |
| locale-dates | X | X | +X | #{rank} |

**Totalt:** X instal. | **Denne uken:** +X | **Gjennomsnitt/dag:** X.X

### 🎯 Dagens analyse: {Focus fra rotation matrix}

{2-4 paragraphs of actual analysis — not generic filler. Concrete numbers, specific observations, comparisons.}

### 💡 Anbefalinger ({antall})

1. **{Kort tittel}** — {1-2 setninger konkret handling}
   - Effekt: {estimert — "Kan øke installs med X%" eller "Løser kjent problem Y"}
   - Innsats: {Lav/Middels/Høy — tids estimat}

2. ...

### 📈 Trender

- setup-doctor: {spesifikk trend — akselererende/svak/stabil + grunn}
- {trend for andre skills}

### 🔄 Repetisjonssjekk

- Sist ukes anbefalinger som er gjennomført: {liste}
- Anbefalinger som gjenstår: {liste med prioritet}
- Nye anbefalinger denne uken: {antall} (mål: ≥ 2 nye)

### 📅 Neste fokus

Dagens rotasjon var Day {N}. Neste kjøring fokuserer på: **{Day N+1 fokus}**
```

## Monetization Framework

When rotation Day 5 (Monetization) fires:

### Pricing Models to Evaluate

| Model | Best For | Revenue Potential | Complexity |
|-------|----------|-------------------|------------|
| Freemium | High-volume, low-value | Low per user, scales | Low |
| One-time buy | Utility tools | Predictable, no churn | Medium |
| Subscription | Ongoing value | Highest LTV | High |
| Donation/Ko-fi | Community goodwill | Unpredictable | Lowest |

### Evaluation Criteria per Skill

1. **Willingness to pay**: Is the problem painful enough? (scale 1-5)
2. **Switching cost**: Can users solve it without the skill? (1-5)
3. **Frequency**: Daily/weekly/monthly use? (affects perceived value)
4. **Competition**: Are free alternatives available? (1-5)
5. **Suite effect**: Does buying one skill make others more valuable? (yes/no)

### Concrete Actions (when recommending monetization)

- **setup-doctor Pro ($5)**: Auto-fix mode + advanced diagnostics + priority support
- **context-brief Pro ($3/mnd)**: Analytics dashboard + multi-session sync + auto-compaction
- **email-triage-pro Pro ($8/mnd)**: Unlimited emails + AI drafts + daily digest + CRM lite
- **locale-dates**: Keep free — drives suite adoption, low standalone monetization potential

## Onboarding for New Publisher

If total installs across all skills < 10:

The focus should NOT be on monetization or advanced features. Focus on:

1. **Get first 10 real users** — share on Discord, Reddit, Twitter
2. **Get first review/star** — ask early users for feedback
3. **Improve skill description** — the listing IS the marketing
4. **Fix any reported bugs** — quality over quantity

Include a "phase indicator" in reports:
- 🌱 Phase 1: Seed (< 10 installs) — Focus: visibility
- 🌿 Phase 2: Grow (10–100 installs) — Focus: conversion optimization
- 🌳 Phase 3: Scale (100–1000 installs) — Focus: monetization
- 🏢 Phase 4: Sustain (1000+ installs) — Focus: retention and expansion

## More by TommoT2

- **tommo-skill-guard** — Security scanner for all installed skills
- **setup-doctor** — Diagnose and fix OpenClaw setup issues
- **locale-dates** — Format dates/times per locale (100+ patterns)
