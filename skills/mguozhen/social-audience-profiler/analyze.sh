#!/usr/bin/env bash
set -euo pipefail
INPUT="${*:-}"
[ -z "$INPUT" ] && echo "Usage: audience profile: <brand/product and target market>" && exit 1
SESSION_ID="audience-$(date +%s)"
PROMPT="You are an audience research expert specializing in social media strategy. Build 3 detailed audience personas for: ${INPUT}

## Persona 1: Primary Audience (Core Buyer)

### Demographics
- Age range: 
- Gender split: 
- Location/market: 
- Income level: 
- Education: 
- Job/role: 

### Psychographics
- Core values (top 5): 
- Identity: how they see themselves
- Aspirations: what they want their life to look like in 3 years
- Fears: top 3 things that keep them up at night
- Frustrations: what makes them rage-quit products/services
- Guilty pleasures: what they secretly enjoy

### Pain Point Matrix
| Level | Pain | How They Describe It |
|-------|------|----------------------|
| Surface (what they say) | | |
| Intermediate (what they mean) | | |
| Root (what they actually feel) | | |

### Content Behavior
- Platforms they actively use (ranked): 
- Time of day they scroll: 
- Content they stop to watch: 
- Content they save: 
- Content they share with friends: 
- Content they immediately swipe past: 
- Accounts they follow in this space: [types, not specific names]

### Language & Vocabulary
- Words they use to describe their problem: [quote-style phrases]
- Words they use to describe their goal: [quote-style phrases]
- Phrases that trigger them: [words that feel salesy or fake]
- Phrases that resonate: [words that feel real]

### Message-Market Fit
The ONE sentence that would stop them mid-scroll: 
[Write it]

---

## Persona 2: Secondary Audience (Aspirers)
[Repeat same structure but for secondary audience]

---

## Persona 3: Aspirational Audience (Dream Customers)
[Repeat same structure for aspirational/future audience]

---

## Platform Strategy by Persona
| Platform | Best Persona | Best Content Type | Best Time |
|----------|-------------|-------------------|-----------|
| Instagram | | | |
| TikTok | | | |
| LinkedIn | | | |
| X/Twitter | | | |
| YouTube | | | |
| Pinterest | | | |

## Content Themes That Resonate
For each persona, the top 5 content topics that will get them to stop, engage, and follow:
- Persona 1: [5 topics]
- Persona 2: [5 topics]
- Persona 3: [5 topics]"

RESULT=$(openclaw agent --local --session-id "$SESSION_ID" --json -m "$PROMPT" 2>/dev/null)
REPORT=$(echo "$RESULT" | python3 -c "
import json,sys
data=json.load(sys.stdin)
texts=[p.get('text','') for p in data.get('payloads',[]) if p.get('text')]
print('\n'.join(texts))
" 2>/dev/null)
[ -z "$REPORT" ] && echo "Error: Could not generate audience profile." && exit 1
echo ""
echo "=== AUDIENCE PROFILER === ${INPUT} ==="
echo ""
echo "$REPORT"
