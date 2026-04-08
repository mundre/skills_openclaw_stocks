---
name: ntriq-esg-regulatory-compliance
description: "Track ESG, AI, and environmental regulations across US and EU. Federal Register and EUR-Lex monitoring, compliance timelines, industry impact analysis. Free government data, pay-per-use."
version: 1.0.0
metadata:
  openclaw:
    primaryTag: data-intelligence
    tags: [compliance,regulatory]
    author: ntriq
    homepage: https://x402.ntriq.co.kr
---

# ESG Regulatory Compliance

Track ESG, AI governance, and environmental regulations across the US and EU. Monitors Federal Register and EUR-Lex for new rules, compliance deadlines, and industry-specific impact analysis. Free government data, pay-per-use.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `topics` | array | ✅ | Topics: `climate`, `ai_governance`, `supply_chain`, `diversity`, `disclosure` |
| `jurisdictions` | array | ❌ | `us`, `eu`, `uk` (default: all) |
| `industries` | array | ❌ | Industry sectors for impact filtering |
| `days_lookback` | integer | ❌ | Recent regulation window (default: 90) |

## Example Response

```json
{
  "regulations_found": 14,
  "high_impact": [
    {
      "title": "SEC Climate-Related Disclosure Rule",
      "agency": "SEC",
      "effective_date": "2024-06-01",
      "compliance_deadline": "2025-01-01",
      "industries_affected": ["public companies"],
      "summary": "Requires disclosure of Scope 1 and Scope 2 GHG emissions in annual reports."
    }
  ],
  "upcoming_deadlines": 3,
  "jurisdiction": "us"
}
```

## Use Cases

- ESG compliance calendar automation for public companies
- Law firm regulatory alert service for clients
- Sustainability report compliance gap analysis

## Access

```bash
# Service catalog
curl https://x402.ntriq.co.kr/services
```

Available on [Apify Store](https://apify.com/ntriqpro/esg-regulatory-compliance) · [x402 micropayments](https://x402.ntriq.co.kr)
