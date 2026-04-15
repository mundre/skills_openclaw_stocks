---
name: trend-demand-forecaster
description: Turn sales notes, trend signals, seasonal context, promo plans, and inventory constraints into a practical demand forecast brief with base, upside, and downside scenarios, leading indicators, and replenishment cues. Use when planners, ecommerce operators, founders, or consultants need forecasting support without live ERP, BI, ads, or marketplace APIs.
---

# Trend Demand Forecaster

## Overview

Use this skill to convert rough demand signals into a practical forecast narrative. It is built for teams that need a fast planning layer for the next few weeks, quarter, or seasonal window.

This MVP is heuristic. It does **not** pull live sales, ads, weather, ERP, marketplace, or competitor data. It relies on the user's provided notes, exports, and planning context.

## Trigger

Use this skill when the user wants to:
- forecast demand for the next month, quarter, or seasonal event
- estimate promo lift or post-promo normalization
- plan replenishment against demand uncertainty
- interpret whether demand is recovering, stabilizing, or softening
- turn messy trend notes into a base, upside, downside planning brief

### Example prompts
- "Forecast next month's demand using these sales and inventory notes"
- "Build a base, upside, downside demand view for our holiday campaign"
- "Should we buy deeper inventory or stay cautious?"
- "Help me interpret whether demand is rebounding or just promo noise"

## Workflow

1. Clarify the planning question, decision horizon, and risk tolerance.
2. Normalize the strongest signals, such as traffic, orders, conversion, price, inventory, and seasonality.
3. Separate baseline demand from promo distortion, stockout distortion, or one-off events.
4. Build base, upside, and downside scenarios with trigger conditions.
5. Return a markdown brief with indicators, action cues, and assumptions.

## Inputs

The user can provide any mix of:
- weekly or monthly sales summaries
- traffic, conversion, pricing, and promo notes
- stockout periods, inventory cover, or inbound timing
- launch, seasonal, holiday, or campaign context
- return rate, customer service, or marketplace feedback
- constraints such as cash, lead time, MOQ, or warehouse limits

## Outputs

Return a markdown forecast brief with:
- demand narrative and likely mode
- planning horizon and key signals
- base, upside, downside scenarios
- leading indicators to monitor
- inventory and commercial implications
- risk watchlist and next-step actions
- assumptions, confidence notes, and limits

## Safety

- Do not claim access to live systems or external trend feeds.
- Treat all scenarios as planning heuristics, not guaranteed forecasts.
- Do not auto-commit buys, budgets, or inventory transfers.
- Downgrade confidence when the user only provides promo-distorted or stockout-distorted history.
- Keep final purchasing and budget decisions human-approved.

## Best-fit Scenarios

- ecommerce teams planning 2 to 16 weeks ahead
- operators working from rough exports instead of a forecasting platform
- founders who need a quick demand-planning memo before placing inventory bets
- consultants preparing scenario-based planning recommendations

## Not Ideal For

- formal statistical forecasting that requires model calibration and backtesting
- highly granular store-SKU-day forecasting at enterprise scale
- workflows that require automatic PO creation or system sync
- regulated forecasts that need audited financial controls

## Acceptance Criteria

- Return markdown text.
- Include scenario, indicator, implication, and risk sections.
- Make the advisory and heuristic framing explicit.
- Keep the output practical for planning and replenishment decisions.
