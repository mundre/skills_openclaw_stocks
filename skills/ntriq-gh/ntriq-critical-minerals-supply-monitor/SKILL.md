---
name: ntriq-critical-minerals-supply-monitor
description: "Monitor critical mineral supply chain risks using USGS, Federal Register, and OECD data. Risk scoring, regulatory tracking, and country dependency analysis for lithium, cobalt, rare earths, and 50+..."
version: 1.0.0
metadata:
  openclaw:
    primaryTag: data-intelligence
    tags: [mining,supply-chain]
    author: ntriq
    homepage: https://x402.ntriq.co.kr
---

# Critical Minerals Supply Monitor

Monitor critical mineral supply chain risks across 50+ minerals using USGS, Federal Register, and OECD data. Covers lithium, cobalt, rare earths, nickel, and more. Returns country dependency scores, regulatory tracking, and risk alerts.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `minerals` | array | ✅ | Mineral names: `lithium`, `cobalt`, `neodymium`, etc. |
| `supplier_countries` | array | ❌ | Filter by country ISO codes |
| `include_regulations` | boolean | ❌ | Include Federal Register rule tracking (default: true) |

## Example Response

```json
{
  "mineral": "cobalt",
  "global_supply_concentration": {
    "top_producer": "Congo, DRC",
    "top_producer_share_pct": 68,
    "herfindahl_index": 0.54,
    "risk_level": "critical"
  },
  "price_trend_30d": "+12.4%",
  "recent_regulations": [
    {"date": "2024-03-15", "title": "Critical Minerals Incentive Program Final Rule", "agency": "DOE"}
  ],
  "substitution_difficulty": "high"
}
```

## Use Cases

- EV battery supply chain risk management
- Defense contractor critical mineral sourcing compliance
- ESG portfolio screening for mining exposure

## Access

```bash
# Service catalog
curl https://x402.ntriq.co.kr/services
```

Available on [Apify Store](https://apify.com/ntriqpro/critical-minerals-supply-monitor) · [x402 micropayments](https://x402.ntriq.co.kr)
