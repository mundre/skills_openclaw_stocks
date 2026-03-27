#!/usr/bin/env bash
# shopify-influencer-campaign — Influencer campaign management for Shopify
set -euo pipefail

INPUT="${*:-}"
if [ -z "$INPUT" ]; then
  echo "Usage: influencer campaign plan: <store niche or URL>"
  exit 1
fi

SESSION_ID="shopify-influencer-campaign-$(date +%s)"

PROMPT="You are a Shopify influencer marketing expert specializing in campaign management, creator partnerships, and ROI-driven influencer programs for ecommerce brands. Build a complete influencer campaign strategy for: ${INPUT}

Produce a complete influencer campaign report with these sections:

## 1. Influencer Tiering & Mix Strategy
- Recommended tier breakdown: nano (1K-10K), micro (10K-100K), macro (100K-1M), mega (1M+)
- Budget allocation percentages across tiers
- Platform priorities: Instagram, TikTok, YouTube, Pinterest by niche
- Engagement rate benchmarks by tier and platform

## 2. Creator Discovery & Vetting
- Top hashtags and search terms to find creators in this niche
- Vetting checklist: engagement rate, audience demographics, fake follower signals
- Tools and platforms for influencer discovery (free and paid options)
- Red flags to avoid: engagement pods, purchased followers, brand misalignment

## 3. Outreach Strategy & Templates
- Cold DM template (Instagram/TikTok) with personalization hooks
- Email outreach template for larger creators
- Follow-up sequence (3-touch cadence)
- Subject lines with high open rates for creator emails

## 4. Campaign Brief & Creative Direction
- One-page campaign brief template with all required fields
- Key talking points and messaging guidelines
- Dos and don'ts for content creation
- Content approval process and revision policy

## 5. Compensation & Deal Structures
- Market rate pricing by tier, platform, and content type
- Gifting-only strategy: when it works and how to pitch
- Affiliate + flat fee hybrid model setup
- Performance bonuses tied to sales milestones

## 6. Legal Requirements & Contracts
- FTC disclosure requirements and hashtag guidelines
- Key contract clauses: exclusivity, usage rights, revision rounds
- Content ownership and licensing terms
- Payment schedule and deliverable timeline

## 7. Tracking, Reporting & ROI Plan
- Immediate actions (week 1): outreach list, brief creation, tracking setup
- Short-term (month 1): launch first wave, monitor performance, collect content
- Long-term (month 3+): build ambassador roster, performance-based renewals, attribution

Include specific CPM, EMV, and cost-per-acquisition benchmarks. Provide actionable steps and templates tailored to Shopify store owners."

openclaw agent --local --message "${PROMPT}" --session "${SESSION_ID}"
