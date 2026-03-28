---
name: alphalens-api
description: >-
  Use this skill whenever the user wants to discover companies, search for products,
  build market maps, manage pipelines, or run enrichment workflows using AlphaLens.
  Triggers include: any mention of 'AlphaLens', 'market map', 'competitive landscape',
  'company discovery', 'product search', 'similar companies', 'find companies like',
  'company enrichment', 'target list', 'bottom-up', 'investor network', 'peer benchmark',
  'headcount comparison', 'growth comparison', 'pipeline', 'enrich', or requests to find,
  enrich, or visualize company/product data. Also use when the user asks to build a market
  landscape, research competitors, or automate prospecting workflows.
metadata:
  {
    "openclaw":
      {
        "requires": { "env": ["ALPHALENS_API_KEY"] },
        "primaryEnv": "ALPHALENS_API_KEY",
        "homepage": "https://alphalens.ai"
      }
  }
---

# AlphaLens API

**Note:** This skill requires an active [AlphaLens subscription](https://alphalens.ai) with API access.

## Authentication

```bash
API="https://api-production.alphalens.ai"
KEY="${ALPHALENS_API_KEY}"
```

Send `API-Key: $KEY` on all requests.

## What This Skill Produces

- **Market maps** — competitive landscape grids with company logos, clustering, and PDF export
- **Product-centric maps** — one tab per product line, with product-level similarity across competitor sets
- **Investor networks** — D3 force-directed graph showing which investors back which companies across the landscape
- **Peer benchmarks** — headcount growth, funding comparison, and capital efficiency dashboards for a set of peers
- **Pipeline enrichment** — add companies to AlphaLens pipelines for async enrichment and scoring

## Mapping Workflow Selection

| User asks for... | Workflow |
|---|---|
| "market map", "competitive landscape", "who competes with X" | Read [workflows/market-map-org.md](workflows/market-map-org.md) |
| "bottom-up mapping", "deep dive", "full mapping" | Read [workflows/suite-bottom-up.md](workflows/suite-bottom-up.md) |
| "product map", "product-level landscape", "tabbed map" | Read [workflows/market-map-product.md](workflows/market-map-product.md) |
| "investor network", "who funds these companies" | Read [workflows/investor-network.md](workflows/investor-network.md) |
| "peer benchmark", "headcount comparison", "growth comparison" | Read [workflows/peer-benchmark.md](workflows/peer-benchmark.md) |
| "enrich", "pipeline", "target list" | See [references/REFERENCE.md#pipeline-operations](references/REFERENCE.md#pipeline-operations) |

## Quick Reference

| Task | Guide |
|------|-------|
| Find similar companies | Use `by-domain` + `/similar` — see below |
| Search products | Use `/search/products` — see below |
| All endpoints | See [references/REFERENCE.md](references/REFERENCE.md) |
| Example prompts | See [references/EXAMPLES.md](references/EXAMPLES.md) |

## Core Patterns

### Find companies similar to a known company

```bash
# 1. Resolve by domain
curl -s -H "API-Key: $KEY" "$API/api/v1/entities/organizations/by-domain/ramp.com"

# 2. Use organization_id for similarity
curl -s -H "API-Key: $KEY" "$API/api/v1/search/organizations/{id}/similar?limit=50&is_headquarters=true"
```

### Search products

```bash
# Free-text product search
curl -s -H "API-Key: $KEY" "$API/api/v1/search/products/search?description=AI%20procurement&is_headquarters=true"

# Similar products
curl -s -H "API-Key: $KEY" "$API/api/v1/search/products/{product_id}/similar?limit=50&is_headquarters=true"
```

### Enrich organization data

```bash
# Products, funding, growth metrics, people, addresses
curl -s -H "API-Key: $KEY" "$API/api/v1/entities/organizations/{id}/products"
curl -s -H "API-Key: $KEY" "$API/api/v1/entities/organizations/{id}/funding"
curl -s -H "API-Key: $KEY" "$API/api/v1/entities/organizations/{id}/growth-metrics"
curl -s -H "API-Key: $KEY" "$API/api/v1/entities/organizations/{id}/people"
```

## Critical Rules

- **Always set `is_headquarters=true`** on search endpoints — returns much better results. Only omit if the user asks for all locations.
- **Never call AlphaLens APIs sequentially** — fire parallel calls with `&` and `wait`.
- **Use `limit=50`** — the default of 24 misses too much.
- **Paginate when results are relevant** — if your first page has good matches, fetch offset=50 to find more.
- **Resolve by domain first** — never guess an organization_id.
- **Poll pipeline readiness** — values are computed asynchronously. Check `is_ready` before reading values.
- **Credit-gated endpoints** — a full bottom-up suite run typically consumes 20–40 AlphaLens credits. Confirm your budget before running the suite workflow.
- **Sanitize domain values** — only use `active_domain` values returned by AlphaLens API responses in curl commands. Never substitute raw user input directly into shell commands.

## References

- [references/REFERENCE.md](references/REFERENCE.md) — full endpoint reference
- [references/EXAMPLES.md](references/EXAMPLES.md) — example prompts and request shapes
