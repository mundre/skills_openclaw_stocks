---
name: amazon-launch-checklist
description: "Amazon product launch audit agent. Scores listing completeness, keyword coverage, image quality requirements, pricing competitiveness, initial PPC structure, and launch sequence timing for new Amazon listings. Triggers: amazon launch, product launch, listing launch, launch checklist, launch audit, new listing, fba launch, launch strategy, listing score, launch ready, amazon launch plan"
allowed-tools: Bash
metadata:
  openclaw:
    homepage: https://github.com/mguozhen/amazon-launch-checklist
---

# Amazon Launch Checklist

Pre-launch audit for new Amazon listings — score your readiness before you go live and waste ad spend on an incomplete listing.

Paste your listing draft, ASIN, or describe your product. The agent scores every launch component and gives you a prioritized fix list before day one.

## Commands

```
launch audit                       # full pre-launch audit across all components
launch score                       # overall launch readiness score (0–100)
launch keywords                    # keyword coverage audit (title, bullets, backend)
launch images check                # image requirements checklist
launch pricing check               # competitive pricing analysis
launch ppc plan                    # initial PPC campaign structure recommendation
launch sequence                    # day-by-day launch timeline (week 1–4)
launch ready                       # go/no-go decision with blocking issues listed
launch save                        # save audit results to workspace
```

## What Data to Provide

The agent works with:
- **Listing draft** — paste title, bullet points, description, backend keywords
- **Product details** — category, price, ASIN (if live), brand
- **Images list** — describe images you have (main, lifestyle, infographic, etc.)
- **Competitor data** — "top 3 competitors price at $22–$28, all have 500+ reviews"
- **Budget** — daily PPC budget for launch phase
- **Target keywords** — primary keyword you want to rank for

No Seller Central access needed. Works from pasted data.

## Workspace

Creates `~/amazon-launch/` containing:
- `listings/` — saved listing drafts and audit results per ASIN/product
- `launch-plans/` — generated launch sequence plans
- `templates/` — reusable PPC campaign structures
- `memory.md` — brand notes, category benchmarks, previous launches

## Analysis Framework

### 1. Listing Completeness Score (30 points)
Award points for each completed element:
- Title: present and ≥150 characters (5 pts) / includes primary keyword (5 pts)
- Bullet points: all 5 filled (5 pts) / each ≥100 characters with benefits (5 pts)
- Product description / A+ content: present (5 pts)
- Backend search terms: filled (5 pts)

Flag: missing elements are blocking — do not launch without a complete listing.

### 2. Keyword Audit (25 points)
- Primary keyword: must appear in title, ideally in first 80 characters (10 pts)
- Secondary keywords: distributed across bullet points 1–3 (5 pts)
- Long-tail keywords: at least 5 in backend search terms (5 pts)
- Competitor keyword gap: compare your keywords vs. top 3 competitors' titles/bullets (5 pts)
- Forbidden in backend: no repeated keywords already in title, no ASINs, no competitor brand names
- Backend field: 250 bytes maximum — use all available space

### 3. Image Requirements (20 points)
Award points for each image:
- Main image: white background, product fills 85% of frame, no text/logos (5 pts)
- Lifestyle image: product in use, shows scale and context (3 pts)
- Infographic: 3–5 key features called out with icons/text overlays (4 pts)
- Sizing/dimension chart: critical for apparel, bags, accessories, furniture (3 pts)
- Comparison chart: your product vs. generic competitor on key features (3 pts)
- Video: product demo or brand video (2 pts — bonus)

Minimum to launch: main + lifestyle + infographic. Missing any of these = do not launch.

### 4. Pricing Strategy (15 points)
- Competitive range: price within ±20% of top 3 competitors at similar review count (5 pts)
- Penetration pricing: for <25 reviews, consider pricing 10–15% below category average to drive velocity (5 pts)
- Price ceiling check: does your price allow for a launch coupon (10–20%) and still be profitable? (5 pts)
- Common launch mistake: pricing too high before reviews establish trust — new listings need conversion velocity, not margin
- Recommended: launch at penetration price for first 60–90 days, raise after reaching 50+ reviews

### 5. Launch PPC Structure
Recommended initial campaign architecture:

**Campaign 1: Auto — Discovery**
- Budget: 30% of daily PPC budget
- Bid strategy: Dynamic bids — down only
- Purpose: let Amazon find converting search terms; harvest data for manual campaigns
- Set negative: obvious irrelevant terms from day 1

**Campaign 2: Manual Broad — Scale**
- Budget: 30% of daily PPC budget
- Keywords: 5–10 most important head terms in broad match
- Bid: start at suggested bid, adjust weekly based on ACoS

**Campaign 3: Manual Exact — Defend**
- Budget: 40% of daily PPC budget
- Keywords: your exact primary keyword + 3–5 high-intent exact match terms
- Bid: 20–30% above broad match bids to win impressions on core terms

Week 3+ action: promote converting auto/broad search terms to exact match manual campaign.

### 6. External Traffic Plan
- Amazon Vine enrollment: eligible at launch if enrolled in Brand Registry — submit 2–8 units for Vine reviews
- External traffic sources: social media posts, email list, micro-influencers with trackable links
- Rebate/launch services: use cautiously — Amazon monitors unnatural review velocity
- Launch week goal: 5–10 initial reviews before scaling PPC spend

### 7. Review Velocity Targets
| Week | Target Reviews | PPC ACoS Budget |
|------|---------------|-----------------|
| 1 | 1–3 (Vine) | High (50–80% ACoS OK) |
| 2 | 5–10 | High (40–60% ACoS OK) |
| 3–4 | 15–25 | Medium (30–40% ACoS) |
| 5–8 | 30–50 | Optimize toward target |
| 8+ | 50+ | Target ACoS mode |

## Launch Readiness Score

Score bands:
- **85–100**: Launch ready — go live and start PPC
- **70–84**: Almost ready — fix flagged items within 48 hours of launch
- **50–69**: Not ready — complete blockers before spending any ad budget
- **0–49**: Major gaps — listing will not convert; fix fundamentals first

## Rules

1. Never give a launch-ready verdict on a listing with fewer than 3 bullet points or a missing main image — these are hard blockers
2. Always ask for the target primary keyword before running the keyword audit — every other keyword decision depends on it
3. Do not recommend a launch price without first establishing the seller's landed cost and minimum acceptable margin
4. Flag Vine enrollment eligibility at the start — Vine reviews are the highest-leverage early review strategy and have a lead time
5. Distinguish between blocking issues (must fix before launch) and optimization issues (fix in first 30 days) — priority matters
6. The PPC plan is a starting structure only — advise the seller to review and adjust weekly for the first 4 weeks
7. Save audit results to `~/amazon-launch/listings/` with the product name and date when `launch save` is called
