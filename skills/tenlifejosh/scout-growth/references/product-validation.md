# Product Validation — Reference Guide

Demand validation, keyword research, proof of market, and pre-launch validation methods.
How to verify people will actually pay for something before building it.

---

## 1. THE VALIDATION IMPERATIVE

### Why Validate Before Building
Building a product no one wants is the most expensive mistake in this business.
Validation answers: "Is there sufficient demand to justify the build investment?"

The minimum validation bar: Clear evidence that people pay for solutions to this problem.

---

## 2. VALIDATION LEVELS

### Level 1: Directional Validation (1-2 hours)
```
Sufficient for: Small product (< 10 hours to build)
Method: Market signals research

CHECKLIST:
- [ ] Google Trends shows this topic has search interest
- [ ] At least 3 competing products exist on Amazon/Gumroad
- [ ] Reddit discussions show the problem is real and current
- [ ] At least one competing product has 50+ reviews/sales

VERDICT: Proceed / Investigate further / Abandon
CONFIDENCE: 🟡 Medium
```

### Level 2: Standard Validation (4-8 hours)
```
Sufficient for: Medium product (10-40 hours to build)
Method: Keyword research + competitor analysis + community research

CHECKLIST:
- [ ] Keyword volume > 1,000 searches/month for primary term
- [ ] Competing products show clear sales (Amazon rank < 100,000 in category)
- [ ] Community pain validated (Reddit threads, reviews)
- [ ] Differentiation identified (why ours would be better for specific audience)
- [ ] Price validated (people pay $X for comparable solutions)

VERDICT: Strong Go / Conditional Go / No Go
CONFIDENCE: 🟢 High
```

### Level 3: Full Validation (1-3 weeks)
```
Sufficient for: Large product or major investment
Method: Above + direct customer research

CHECKLIST:
- [ ] All Level 2 checks pass
- [ ] 5+ customer conversations completed
- [ ] Audience confirmed they would pay $X
- [ ] Specific differentiator confirmed as valued
- [ ] Pre-sales or waitlist interest measured

VERDICT: Build / Refine / Kill
CONFIDENCE: 🟢 Very High
```

---

## 3. KEYWORD RESEARCH FOR VALIDATION

### The Keyword Validation Protocol
```
TOOLS: Google Keyword Planner (free) | Ubersuggest | Ahrefs (paid)

STEP 1: Seed keywords
  Start with 5-10 ways your target audience might search for this:
    "[problem] guide"
    "[problem] workbook"
    "how to [solve problem]"
    "best [solution type] for [audience]"
    "[audience] [problem] help"

STEP 2: Volume check
  Monthly search volume targets:
    1K-10K/month: Validated niche demand
    10K-100K/month: Strong market
    100K+/month: Major market (competitive)
    <1K/month: Possible but limited organic reach

STEP 3: Competition check
  SEO difficulty 0-30: Low competition, rankable
  SEO difficulty 30-60: Medium, rankable with effort
  SEO difficulty 60+: High, need to compete on other channels

STEP 4: Intent analysis
  "informational" intent: People learning, not buying
  "commercial" intent: People researching to buy
  "transactional" intent: People ready to buy now
  → For product validation: want commercial or transactional intent

STEP 5: Related keywords
  Look at "People also search for" and "Related searches"
  → Find related pain points and solution terms
  → Build keyword cluster map
```

### Amazon Best Seller Rank as Validation
```
WHAT AMAZON BSR TELLS YOU:
  BSR < 10,000 in category: Strong seller (hundreds/week)
  BSR 10,000-50,000: Moderate seller (dozens/week)
  BSR 50,000-100,000: Slow but selling (several/week)
  BSR 100,000+: Minimal sales

VALIDATION RULE:
  If 3+ competitors have BSR < 50,000 in your product category:
  → Validated demand exists

HOW TO FIND:
  Search Amazon for the product type
  Click on competitor products
  Scroll to "Product details" section
  Find "Best Sellers Rank"
```

---

## 4. SMOKE TEST / PRESELL VALIDATION

### The Landing Page Test
```
Strongest validation: people give you money before you build it

SETUP (2-3 days work):
  1. Create a simple landing page describing the product
     - What problem it solves
     - Who it's for
     - What's included
     - Price
     - "Pre-order" or "Join waitlist" CTA

  2. Drive traffic (choose one):
     - Post in relevant Reddit communities
     - Post on Twitter/X
     - Post in Facebook Groups
     - Small paid ads ($50-100 test budget)

  3. Measure:
     - Clicks to page vs. signups: Conversion > 5% = promising
     - Signups: > 50 signups in 7 days = strong signal
     - Pre-orders: > 10 = very strong validation

VERDICT THRESHOLDS:
  0-10 signups in 7 days from 500+ visitors: Low demand, reconsider
  10-50 signups: Moderate interest, proceed with reduced scope
  50+ signups: Strong demand, build the full product
```

---

## 5. COMMUNITY VALIDATION

### Reddit Validation Method
```
SUBREDDITS TO CHECK BY PRODUCT TYPE:
  Family organization: r/mommit, r/Parenting, r/slatestarcodex, r/productivity
  Personal finance: r/personalfinance, r/povertyfinance, r/financialindependence
  Faith: r/Christianity, r/Reformed, r/LifeAdvice
  Career: r/jobs, r/careerguidance, r/findapath
  Productivity: r/productivity, r/getdisciplined, r/selfimprovement

SEARCH METHOD:
  site:reddit.com/r/[subreddit] "[problem]"
  Count posts per month asking about this problem
  Read comments for language they use

VALIDATION SIGNALS:
  Strong: 5+ posts/month about this problem with 50+ upvotes
  Moderate: 2-5 posts/month with engagement
  Weak: Occasional mentions, low engagement
```

---

## 6. VALIDATION REPORT TEMPLATE

```markdown
# Product Validation Report: [Product Name]

**Date:** [Date]  
**Researcher:** Scout Agent  
**Validation Level:** [1 / 2 / 3]  

## Verdict
**RECOMMENDATION:** ✅ BUILD / ⚠️ BUILD WITH CONDITIONS / ❌ DO NOT BUILD

**Confidence:** 🟢 High / 🟡 Medium / 🔴 Low

**One-sentence summary:** [Why we're recommending this verdict]

## Evidence

### Keyword Demand
| Keyword | Monthly Volume | SEO Difficulty | Intent |
|---|---|---|---|
| [term 1] | [X/mo] | [difficulty] | [commercial] |
| [term 2] | [X/mo] | [difficulty] | [transactional] |

**Interpretation:** [What this data means for product viability]

### Competitive Proof
| Competitor | Price | Sales Signal | Reviews |
|---|---|---|---|
| [Name] | $[X] | BSR [X] or [X] sales | [X] stars, [N] reviews |

**Interpretation:** [What this means — is the market proven?]

### Community Signals
- r/[subreddit]: [X] posts/month about this problem ([sentiment])
- Reddit quote: "[Exact quote showing real pain]"
- Amazon review quote: "[Exact review showing unmet need]"

## Conditions (if conditional go)
1. Must differentiate by: [Specific differentiation]
2. Must price at: $[X] to be competitive
3. Must target specifically: [Audience segment]

## Risk Factors
1. [What could make this fail]
2. [What assumption must be true for this to succeed]

## Recommended Next Step
[Specific action: Build it / Run a smoke test / Validate price point / Interview 5 customers]
```

---

## 7. COMMON VALIDATION MISTAKES

### Mistakes That Lead to Wrong Verdicts

**False Positive:**
- Seeing interest in a topic, not a paid solution
- Friends and family saying "I'd buy that" (they won't)
- Validating with wrong audience (tech-savvy vs. target)

**False Negative:**
- Assuming low competition = no market (sometimes = missed opportunity)
- Stopping at one failed channel when the audience is on a different channel
- Validating at wrong price point ($97 fails, $27 would have succeeded)

**The Golden Rule:**
Never validate with people who would say yes to be nice.
Only valid signal: strangers giving you money or meaningful effort.
