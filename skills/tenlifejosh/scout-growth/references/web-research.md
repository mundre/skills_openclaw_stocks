# Web Research — Reference Guide

Effective search strategies, source evaluation, data extraction, and research efficiency.
How to find the right information faster.

---

## 1. ADVANCED SEARCH OPERATORS

### Google Search Operators
```
EXACT PHRASE: "family organization system"
EXCLUDE: family organization -app -software
SITE SEARCH: site:reddit.com "family schedule chaos"
FILE TYPE: filetype:pdf "market research" family organization
DATE RANGE: family organization after:2023-01-01
RELATED: related:gumroad.com
INTITLE: intitle:"family planner" PDF
INURL: inurl:family-organization
DEFINE: define:TAM market

POWER COMBINATIONS:
  Competitor research: site:[competitor.com] pricing
  Find PDFs to analyze: [topic] filetype:pdf market size
  Find forums: [topic] site:reddit.com OR site:quora.com
  Find data: [topic] "market size" OR "market research" 2023 OR 2024
  Find pricing: [product type] "how much" OR "pricing" site:reddit.com
```

### Research Query Templates
```
FOR MARKET SIZE:
  "[category] market size [year]"
  "[category] industry report [year]"
  "[category] TAM SAM"

FOR COMPETITOR RESEARCH:
  "[problem] best tools/guides/systems"
  "[problem] alternative to [known solution]"
  "top [product category] [year]"

FOR AUDIENCE RESEARCH:
  "[audience] "[problem]" reddit.com
  "[audience] "[problem]" solutions
  "[audience] frustrated with [solution type]"

FOR TREND DATA:
  "[topic] trend [year]"
  "[topic] growing OR declining"
  "[topic] interest over time"
```

---

## 2. RESEARCH TOOL STACK

### Free Tools
```
Google Trends: trends.google.com
  → Search interest over time, geographic distribution, related queries

Google Keyword Planner: ads.google.com/keywordplanner
  → Search volume estimates, keyword ideas

AnswerThePublic: answerthepublic.com
  → Questions people ask about a topic

Reddit Search: reddit.com/search
  → Community discussions, real customer language

Amazon: amazon.com
  → Product validation, category analysis, review mining

Wayback Machine: web.archive.org
  → Historical website content, competitor history

LinkedIn: linkedin.com
  → Company research, team size, B2B intelligence

Statista (limited free): statista.com
  → Market statistics (limited without subscription)
```

### Paid Tools (If Access Available)
```
Ahrefs or SEMrush:
  → Keyword research, traffic estimates, competitor SEO

SimilarWeb:
  → Website traffic estimates, traffic sources

SparkToro:
  → Audience research, where audiences spend time
```

---

## 3. SOURCE EVALUATION

### Source Quality Scoring
```
SCORE EACH SOURCE 1-5 on:

AUTHORITY (1-5):
  5 = Primary research, government data, academic research
  4 = Industry publications, established media
  3 = Expert blogs, credible trade publications
  2 = General media, aggregators
  1 = Anonymous, unknown, no credentials

FRESHNESS (1-5):
  5 = Published within last 6 months
  4 = 6-18 months old
  3 = 18-36 months old (use with caution for fast-moving markets)
  2 = 3-5 years old (flag as potentially outdated)
  1 = 5+ years old (almost always outdated for market data)

SPECIFICITY (1-5):
  5 = Directly addresses the exact topic with specific data
  4 = Closely related, high relevance
  3 = Moderate relevance, need to extrapolate
  2 = Loosely related, significant extrapolation needed
  1 = Barely relevant, speculative connection

MINIMUM ACCEPTABLE: Source with Authority + Freshness + Specificity ≥ 9/15
IDEAL: Score ≥ 12/15
```

### Red Flags in Sources
```
ALWAYS INVESTIGATE FURTHER IF:
  - No author name or publication date
  - Statistics cited without primary source
  - Findings suspiciously aligned with seller's interest (conflict of interest)
  - Numbers that are exactly round (e.g., "exactly 75% of businesses..." — suspiciously precise)
  - Dramatic claims without methodology
  - Published by unknown or promotional source
  
THE CROSS-REFERENCE RULE:
  Any critical stat should be corroborated by at least 2 independent sources
  before including in a briefing.
```

---

## 4. RESEARCH EFFICIENCY PROTOCOLS

### The 80/20 Research Approach
```
20% of research sources provide 80% of insight.
Stop digging when additional sources confirm what you already found.

SIGNALS TO STOP RESEARCHING:
  - Last 5 sources added nothing new
  - Same 3-4 facts keep appearing
  - You're reading abstracts without finding new angles
  - Confidence level is "High" already

SIGNALS TO KEEP RESEARCHING:
  - Key sources contradict each other
  - Confidence level is "Low" on critical claims
  - Decision stakes are very high
  - Finding unexpected information that changes the picture
```

### Timed Research Protocol
```
For standard research tasks, timebox strictly:

15-MINUTE RESEARCH:
  5 min: Google for the main data points
  5 min: Reddit search for community validation
  5 min: Synthesize and write brief summary

2-HOUR RESEARCH:
  30 min: Market sizing (Google Trends, keyword data, competitor analysis)
  30 min: Audience research (Reddit, community analysis)
  30 min: Competitive analysis (top 3 competitors profiled)
  30 min: Synthesize into full briefing

8-HOUR RESEARCH:
  2h: Market and competitive landscape
  2h: Deep audience research (community analysis + any interviews)
  2h: Opportunity analysis and scoring
  2h: Full briefing writing and review
```

---

## 5. DATA EXTRACTION TECHNIQUES

### Extracting Data from Competitor Sites
```
PRODUCT PRICING: Usually on pricing page or directly in product listings
TEAM SIZE: About page + LinkedIn company page
CUSTOMER COUNT: About page, case studies, testimonials ("trusted by X companies")
REVENUE SIGNALS: Job listings (hiring = growing), press releases
PRODUCT ROADMAP: Blog, social media, changelog pages
Customer pain points: Review sites (G2, Trustpilot), their own FAQs
```

### Extracting Insights from Reviews
```
PROCESS:
1. Find product on Amazon/G2/Trustpilot/Gumroad
2. Sort by LOWEST rating (1-2 stars)
3. Read 20-30 reviews
4. For each: extract the SPECIFIC complaint (not "it's bad")
5. Group complaints by theme
6. Count themes (frequency = importance)
7. Top 3 themes = product improvement opportunities

WHAT TO EXTRACT:
  What they thought they'd get (vs. what they got)
  What specific feature failed
  What they wish it had
  What would have made them give 5 stars
  The exact language they use to describe their disappointment
```
