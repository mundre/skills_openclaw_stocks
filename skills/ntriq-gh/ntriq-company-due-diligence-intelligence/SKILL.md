---
name: ntriq-company-due-diligence-intelligence
description: "Complete company due diligence API from 5 federal sources: OSHA violations, EPA compliance, SEC filings, OFAC sanctions, USASpending contracts. No subscription needed. Integrated risk scoring for M..."
version: 1.0.0
metadata:
  openclaw:
    primaryTag: data-intelligence
    tags: [compliance,due-diligence]
    author: ntriq
    homepage: https://x402.ntriq.co.kr
---

# Company Due Diligence Intelligence

Complete company due diligence from 5 federal sources in one API call: OSHA violations, EPA compliance, SEC filings, OFAC sanctions, and USASpending contracts. Returns integrated risk score for M&A, supplier vetting, and investment screening.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `company_name` | string | ✅ | Legal entity name to screen |
| `ein` | string | ❌ | Employer Identification Number for precise matching |
| `state` | string | ❌ | US state code for jurisdiction filter |
| `sources` | array | ❌ | Subset of `osha`, `epa`, `sec`, `ofac`, `usaspending` |

## Example Response

```json
{
  "company": "Acme Manufacturing Inc.",
  "risk_score": 67,
  "risk_level": "medium",
  "findings": {
    "osha": {"violations_3yr": 4, "penalty_total": 38500, "willful": 0},
    "epa": {"violations": 1, "status": "resolved"},
    "sec": {"filings_found": true, "material_events": 2},
    "ofac": {"match": false},
    "usaspending": {"contracts": 12, "total_value": 4200000}
  }
}
```

## Use Cases

- M&A pre-LOI screening workflow
- Vendor onboarding compliance automation
- Private equity portfolio risk monitoring

## Access

```bash
# Service catalog
curl https://x402.ntriq.co.kr/services
```

Available on [Apify Store](https://apify.com/ntriqpro/company-due-diligence-intelligence) · [x402 micropayments](https://x402.ntriq.co.kr)
