---
name: stress-toolkit
description: A comprehensive stress management toolkit offering quick relaxation techniques and exercises. Suitable for moments of high stress, anxiety, or when you need to unwind and find calm.
---

# Stress Toolkit

> 🟢 **MVP/P0 Complete**: Core features implemented with crisis detection and referral mechanisms.

## Overview

A collection of rapid stress-relief techniques for everyday use:
- Feeling stressed or anxious
- Trouble relaxing or falling asleep
- Emotional overwhelm, can't find calm

## Core Modules

| Feature | Description |
|---------|-------------|
| Breathing Exercises | 4-7-8 breathing, box breathing, diaphragmatic breathing |
| Progressive Muscle Relaxation | 10-15 minute full-body relaxation routine |
| 5-4-3-2-1 Grounding | Sensory-based technique to return to the present moment |
| Guided Meditation | Body scan, breathing meditation |
| Sleep Prep | Bedtime relaxation routine |
| Anxiety Relief | Combination approach |

## How to Trigger

- Keywords: "stressed", "anxious", "relax"
- Specific requests: "deep breath", "meditation", "can't sleep"
- Questions like "how can I relax?"

## Crisis Detection & Referral

### High-Risk Detection (Immediate Referral)
Keywords: suicide, self-harm, don't want to live, death, cutting, jumping, hopeless, depressed, despair

Response: Provide professional crisis hotline, guide user to seek professional help

### Moderate-Risk Detection (Extra Care)
Keywords: anxious, fearful, scared, worried, insomnia, breakdown, powerless, overwhelmed, can't breathe

Response: Express understanding and care, invite user to share or try a technique

## Safety Boundaries

⚠️ **Explicitly NOT provided**:
- Psychological diagnosis
- Psychotherapy
- Replacement for professional counseling

⚠️ **Disclaimer**:
- This tool provides self-help relaxation techniques only
- Cannot replace professional mental health treatment
- For serious emotional concerns, please seek professional help

## Directory Structure

```
stress-toolkit/
├── skill.json
├── SKILL.md
└── scripts/
    ├── handler.py           # Core logic
    └── crisis_detector.py   # Crisis detection module
```

## Testing

### Basic Function Tests
```bash
# Test main entry
python3 ~/.openclaw/skills/stress-toolkit/scripts/handler.py "I'm stressed"

# Test breathing
python3 ~/.openclaw/skills/stress-toolkit/scripts/handler.py "I need to do deep breathing"

# Test grounding
python3 ~/.openclaw/skills/stress-toolkit/scripts/handler.py "anxious"
```

### Crisis Detection Tests
```bash
# Test high-risk detection (should trigger referral)
python3 ~/.openclaw/skills/stress-toolkit/scripts/handler.py "I don't want to live anymore"

# Test moderate-risk detection (should trigger care)
python3 ~/.openclaw/skills/stress-toolkit/scripts/handler.py "I'm so anxious and overwhelmed"
```

### Self-Test Examples

| Input | Expected Output |
|-------|----------------|
| "I'm stressed" | Display feature menu |
| "I need deep breathing" | Show 4-7-8 / box / diaphragmatic breathing |
| "Can't sleep" | Show bedtime relaxation routine |
| "Anxious" | Show anxiety relief combination |
| "I don't want to live" | Trigger crisis referral, show hotline |
| "So anxious and overwhelmed" | Trigger moderate-risk response, show care |

## Version Info

- version: 1.0.0
- author: Golden Bean
- status: MVP complete, ready for testing
