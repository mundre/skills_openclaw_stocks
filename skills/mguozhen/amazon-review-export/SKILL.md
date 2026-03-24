---
name: amazon-review-export
description: "Amazon product review export and analysis agent. Extract, organize, and analyze Amazon reviews — export to structured format, identify sentiment patterns, surface product insights, and generate competitive intelligence from review data. Triggers: amazon review export, review analysis, export reviews, review data, review csv, sentiment analysis, review insights, customer feedback analysis, review scraper, product reviews, review patterns, voc amazon"
allowed-tools: Bash
metadata:
  openclaw:
    homepage: https://github.com/mguozhen/amazon-review-export
---

# Amazon Review Export & Analyzer

Extract intelligence from Amazon product reviews — organize into structured data, analyze sentiment patterns, identify product improvement opportunities, and generate competitive insights from customer voice data.

## Commands

```
review export <asin>              # structure reviews into exportable format
review analyze <reviews>          # full sentiment and pattern analysis
review sentiment <reviews>        # sentiment scoring breakdown
review patterns <reviews>         # find recurring themes and pain points
review compare <asin1> <asin2>    # compare review profiles between products
review insights <reviews>         # extract product improvement opportunities
review competitive <comp-reviews> # analyze competitor review weaknesses
review summary <reviews>          # executive summary of review data
review csv <reviews>              # format reviews as CSV-ready data
review report <asin>              # comprehensive review intelligence report
```

## What Data to Provide

- **Review text** — paste reviews directly (as many as possible)
- **Star rating distribution** — number of reviews at each star level
- **ASIN** — product identifier
- **Competitor reviews** — for competitive analysis
- **Time period** — recent reviews vs. older reviews for trend analysis

## Review Analysis Framework

### Review Export Format

Structure raw reviews into:
```csv
Date,Rating,Title,Review Text,Verified,Helpful Votes,Reviewer
2024-01-15,5,"Great product","Very satisfied with...",Yes,12,Customer123
2024-01-10,2,"Disappointing","Expected better...",Yes,3,Customer456
```

### Sentiment Analysis Framework

**5-star rating interpretation:**
```
⭐⭐⭐⭐⭐ (5-star): Delighted — read for what exceeds expectations
⭐⭐⭐⭐   (4-star): Satisfied — note any "but" qualifiers
⭐⭐⭐     (3-star): Neutral — mixed feelings, often most useful insights
⭐⭐       (2-star): Dissatisfied — specific complaints, high value for improvement
⭐         (1-star): Angry — often extreme cases, filter for systemic vs. one-off
```

**Sentiment scoring:**
```
Positive signals (+): "love", "perfect", "great", "amazing", "exactly what I needed"
Negative signals (-): "disappointed", "broke", "doesn't work", "waste", "returned"
Neutral signals (=): "okay", "fine", "average", "as expected", "decent"

Net Sentiment Score = (Positive reviews - Negative reviews) / Total reviews × 100
Target: Score > 60 = healthy product sentiment
```

### Theme Identification (Qualitative Coding)

Categorize all reviews into themes:

**Product quality themes:**
```
□ Build quality / durability
□ Materials / finish quality
□ Sizing / dimensions (accurate vs. listing)
□ Performance (does it work as claimed?)
□ Longevity (how long does it last?)
```

**Customer experience themes:**
```
□ Packaging / unboxing experience
□ Instructions / ease of setup
□ Customer service experience
□ Shipping / delivery condition
□ Value for money perception
```

**Use case themes:**
```
□ Intended use (matches expected use case)
□ Alternative uses (how customers use it unexpectedly)
□ Gifting (bought as a gift)
□ Replacement (replacing specific previous product)
□ Professional vs. personal use
```

### Frequency Analysis

Count mentions of each theme:
```
Theme                    Mentions    % of Reviews    Sentiment
Durable/sturdy           45          42%             Positive
Easy to assemble         38          35%             Positive
Instructions unclear     22          20%             Negative
Size smaller than shown  15          14%             Negative
Great value for money    52          48%             Positive
```

**Priority fix threshold**: Any negative theme appearing in >10% of reviews requires action.

### Pain Point Extraction

From negative reviews, extract specific pain points:
```
Pain Point              Frequency   Severity    Fix Category
Product breaks quickly  23 mentions High        Product quality
Wrong size/dimensions   15 mentions Medium      Listing accuracy
No instructions         12 mentions Low         Packaging insert
Hard to clean           8 mentions  Low         Product design
```

**Severity classification:**
- High: Safety, complete product failure, cannot use product
- Medium: Significant disappointment, reduced usefulness
- Low: Minor inconvenience, still satisfied overall

### Competitive Review Intelligence

From competitor reviews, extract:

**Competitor weaknesses** (from their negative reviews):
→ These are your differentiation opportunities

**Competitor strengths** (from their positive reviews):
→ Baseline expectations you must meet or exceed

```
Competitor Pain Points → Your Product Claims
"Instructions are confusing" → "Clear 10-step illustrated guide included"
"Flimsy material" → "Reinforced with aircraft-grade aluminum"
"Customer service ignores" → "24/7 support with 1-hour response guarantee"
```

### Review Trend Analysis

Compare recent vs. older reviews:
```
Period          Avg Rating    Top Complaint        Top Praise
Last 90 days:   4.1           Size issues (18%)    Easy use (42%)
6-12 months:    4.4           No issues dominant   Quality (55%)
12+ months:     4.6           Rare complaints      Durability (60%)

Trend: Rating declining → investigate recent product/supplier change
```

### VOC (Voice of Customer) Summary

Generate a customer perspective summary:
```
WHAT CUSTOMERS LOVE (keep and amplify in marketing):
1. [Most praised attribute + quote]
2. [Second most praised + quote]
3. [Third most praised + quote]

WHAT CUSTOMERS WANT IMPROVED (product/listing fixes):
1. [Top pain point + specific ask]
2. [Second pain point + ask]
3. [Third pain point + ask]

WHAT SURPRISES CUSTOMERS (unintended uses or unexpected positives):
1. [Unexpected use case]
2. [Unexpected benefit]
```

### Review-to-Listing Optimization

Map review insights directly to listing improvements:
```
Review insight → Listing change
"Sturdy, holds 50lbs easily" → Add to bullets: "HEAVY-DUTY CONSTRUCTION — tested to hold up to 50 lbs"
"Works great as a gift" → Title: add "Perfect Gift" / create gift-focused image
"Instructions confusing" → Add instruction image to image gallery
"Looks exactly as shown" → Emphasize "true-to-photo" in listing
```

## Workspace

Creates `~/review-data/` containing:
- `exports/` — structured CSV exports per ASIN
- `analyses/` — full review analysis reports
- `themes/` — coded theme frequency data
- `competitive/` — competitor review intelligence
- `voc/` — voice of customer summaries

## Output Format

Every review analysis outputs:
1. **Rating Distribution** — star breakdown with percentage for each level
2. **Net Sentiment Score** — overall sentiment health (0-100)
3. **Top 5 Positive Themes** — what customers love most (with frequency)
4. **Top 5 Negative Themes** — main pain points (with frequency + severity)
5. **VOC Summary** — customer voice in plain language
6. **Listing Optimization Map** — review insights → specific listing improvements
7. **Product Development Signals** — engineering/sourcing changes implied by feedback
8. **CSV Export** — structured data ready to paste into spreadsheet
