---
name: Product Localization Advisor
slug: cb-product-localization-advisor
description: Product adaptation framework for international market requirements and cultural preferences
category: cross-border-ecommerce
type: descriptive
language: en
author: Harry (code agent)
version: 1.0.0
---

# Product Localization Advisor

## Overview

Product adaptation framework for international market requirements and cultural preferences. Covers regulatory certifications, labeling requirements, packaging adaptation, and cultural customization for major markets: Germany, France, Japan, Australia, UK, US, Brazil, and India. Generates competitive analysis and phased implementation plans. Pure descriptive skill. No code execution, API calls, or network access.

## Trigger Keywords

Use this skill when the user mentions or asks about any of the following topics:

### Primary Triggers
- product localization for Germany, Japan, France, Australia, UK, US, Brazil, India
- adapt products for a specific country or international market
- regulatory certifications for electronics, apparel, toys, cosmetics, food, or consumer goods
- cultural product adaptation and packaging localization
- product changes needed for cross-border or international markets
- CE marking, UKCA, PSE, RCM, INMETRO, BIS requirements
- label language requirements for export markets
- market-specific packaging regulations

### Secondary Triggers
- "how should I adapt my electronics products for Germany and Japan"
- "what product changes needed for selling in France and Australia"
- "help me localize my apparel brand for international markets"
- "what certifications do I need for the Brazilian market"
- "how to adapt packaging for the Japanese market"
- "product compliance for India and Brazil"
- "cultural considerations when selling to Germany"
- "Australia RCM requirements for electronics"
- "Japan PSE mark and labeling rules"
- "UKCA vs CE marking differences"

## Workflow

1. **Receive input** — Parse target markets, product categories, and localization goals
2. **Regulatory analysis** — Identify required certifications, marks, and labeling per market
3. **Cultural analysis** — Provide cultural adaptation recommendations per market
4. **Competitive analysis** — Generate differentiation and positioning framework
5. **Implementation plan** — Build phased plan with deliverables and timeline

## Input Format

Accepts natural language or structured JSON describing product type, target markets, and localization goals (regulatory compliance, cultural appropriateness, competitive positioning).

## Output Structure

Returns JSON with the following fields:
- `input_analysis`: parsed summary of target markets, product categories, and goals
- `regulatory_adaptations`: required certifications, marks, and labeling per market
- `cultural_adaptations`: cultural priorities and recommended product adaptations per market
- `competitive_analysis_framework`: differentiation opportunities and positioning per market
- `localization_implementation_plan`: phased plan with deliverables and timeline
- `disclaimer`: safety disclaimer

## Supported Markets

| Market | Key Certifications | Language | Special Requirements |
|--------|-------------------|----------|---------------------|
| Germany | CE | German |严谨质量偏好，环保意识强 |
| France | CE | French |文化敏感性，环保法规 |
| Japan | PSE, JIS | Japanese |高品质期望，精致包装 |
| Australia | RCM | English |气候适应性，环保要求 |
| UK | UKCA, CE | English |脱欧后独立体系 |
| US | FCC, UL | English |尺寸规格，州级差异 |
| Brazil | INMETRO | Portuguese |复杂认证流程 |
| India | BIS | Hindi, English |本地测试要求 |

## Safety and Disclaimer

Descriptive guidance only. Not professional legal, regulatory, or business advice. Verify with qualified professionals and official regulatory bodies. Does not guarantee market acceptance or regulatory approval. Regulations change frequently; always verify current requirements.

## Examples

### Example 1: Electronics to Germany and Japan
Input: "how should I adapt my electronics products for Germany and Japan market"
Output: CE marking and PSE mark requirements, German and Japanese language labeling, cultural priorities (Germany: quality over convenience, Japan: precision and durability), competitive positioning emphasizing reliability, 4-phase implementation plan.

### Example 2: Apparel to France and Australia
Input: "help me localize apparel products for France and Australia"
Output: Regulatory requirements for both markets, cultural considerations (France: fashion sensibility and sizing, Australia: climate diversity and outdoor lifestyle), sizing and packaging adaptation, competitive analysis, phased localization roadmap.

### Example 3: Consumer Goods to Brazil and India
Input: "what changes needed to sell my consumer goods in Brazil and India"
Output: INMETRO and BIS certification paths, Portuguese and Hindi labeling requirements, cultural adaptation priorities, local competition analysis, implementation roadmap.

### Example 4: Multiple Markets Electronics
Input: "I want to sell electronics in Germany, Japan, Australia and Brazil, what do I need"
Output: Comprehensive multi-market analysis covering CE/UKCA (Europe), PSE (Japan), RCM (Australia), INMETRO (Brazil) — full certification matrix, labeling language requirements, cultural adaptation framework, phased market entry strategy.

## Acceptance Criteria

- Identifies regulatory adaptations for at least 2 target markets
- Provides cultural adaptation recommendations with specific priorities per market
- Includes competitive analysis framework with differentiation opportunities
- Creates implementation plan with phases, deliverables, and timeline
- Returns valid JSON with all documented fields present
- Contains complete safety disclaimer in every output
- Includes input_analysis summarizing parsed input
- Pure descriptive — no code execution, API calls, network access
