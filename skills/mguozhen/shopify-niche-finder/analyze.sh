#!/usr/bin/env bash
# shopify-niche-finder — Profitable niche identification for Shopify stores
set -euo pipefail

INPUT="${*:-}"
if [ -z "$INPUT" ]; then
  echo "Usage: find profitable niche: <interest area or budget>"
  exit 1
fi

SESSION_ID="shopify-niche-$(date +%s)"

PROMPT="You are a Shopify ecommerce niche research expert specializing in market demand analysis, competition assessment, and profitability modeling for product niches. Help identify and evaluate profitable Shopify niches for: ${INPUT}

Produce a complete niche identification and evaluation report with these sections:

## 1. Niche Evaluation Framework
- 5 dimensions of a good niche: demand, competition, margin, passion, and defensibility
- Scoring matrix: rate each dimension 1-10 for any niche candidate
- Minimum viable scores to pursue a niche (avoid low-margin, high-competition traps)
- Red flags: commoditized niches, dominated by Amazon, low-ticket, price wars

## 2. Market Research Process & Tools
- Google Trends: how to analyze search volume trends and seasonality
- Amazon Best Sellers and Movers & Shakers: what ranks mean for Shopify viability
- Keyword research: search volume, CPC, and buyer intent for niche keywords
- Facebook Audience Insights and TikTok Creative Center for demand signals

## 3. Competition Analysis Framework
- Shopify store discovery: how to find competitors in any niche
- Alexa, SimilarWeb, and SEMrush for competitor traffic analysis
- Amazon review mining: understanding what customers love and hate
- Differentiation opportunities: what the market is missing

## 4. Profit Margin Modeling
- COGS estimation: product cost, shipping, duties, and fulfillment
- Pricing strategy: positioning above commodity, below premium
- Gross margin targets: minimum 40% for healthy Shopify DTC margins
- Customer acquisition cost modeling: what CAC can you afford at this margin?

## 5. Trend & Longevity Analysis
- Google Trends 5-year trajectory: growing, declining, or stable
- TikTok viral product risk: hot today, dead tomorrow
- Evergreen niches vs trend-driven: strategic consideration
- Adjacent product opportunities for catalog expansion

## 6. Top 10 Niche Recommendations
- Based on the input, 10 specific niche ideas with brief evaluations
- For each: estimated demand level, competition level, typical margin range
- Quick win niches (easier entry) vs premium niches (higher reward, more effort)
- Sub-niche opportunities within broader categories

## 7. Niche Validation Checklist & Launch Plan
- Immediate actions (week 1): 3 validation methods — Etsy listings, Instagram hashtags, keyword tools
- Short-term (month 1): build MVP store, run small paid traffic test, measure conversion
- Long-term (month 3+): full product catalog, established positioning, scaling

Include specific niche examples that are profitable in today's market, typical ROAS expectations by niche type, and common mistakes new Shopify store owners make in niche selection."

openclaw agent --local --message "${PROMPT}" --session "${SESSION_ID}"
