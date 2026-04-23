---
name: skylv-feature-flag
slug: skylv-feature-flag
version: 1.0.0
description: "Feature flag management. Creates and toggles feature flags for A/B testing. Triggers: feature flag, a b test, toggle feature, abtesting."
author: SKY-lv
license: MIT
tags: [automation, tools]
keywords: [automation, tools]
triggers: feature-flag
---

# Feature Flag Manager

## Overview
Implements feature flags for controlled rollouts and A/B testing.

## When to Use
- User asks to "add a feature flag"
- User wants to "A/B test" or "gradually roll out"

## Implementation

if (isFeatureEnabled("new_checkout_flow", userId)) {
  renderNewCheckout();
} else {
  renderLegacyCheckout();
}

## Rollout Strategy
1-5% = internal users
10-25% = beta users
25-50% = canary
100% = full rollout

Monitor: error rate, conversion, latency

## Anti-Patterns
- Do not use flags for permanent features
- Limit active flags to under 20
- Clean up flags after rollout
