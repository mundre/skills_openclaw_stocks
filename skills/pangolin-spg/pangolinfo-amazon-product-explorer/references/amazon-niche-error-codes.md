# Error Codes and Troubleshooting

## Pangolinfo API Error Codes

| Code | Meaning | Resolution |
|------|---------|------------|
| 0 | Success | No action needed |
| 1002 | Invalid parameter | Check required fields for the specific API |
| 1004 | Invalid token | Auto-retried by script |
| 2001 | Insufficient credits | Top up at [pangolinfo.com](https://pangolinfo.com/?referrer=clawhub_niche) |
| 2005 | No active plan | Subscribe at [pangolinfo.com](https://pangolinfo.com/?referrer=clawhub_niche) |
| 2007 | Account expired | Renew at [pangolinfo.com](https://pangolinfo.com/?referrer=clawhub_niche) |
| 2009 | Usage limit reached | Wait for next billing cycle or contact support |
| 4029 | Rate limited | Reduce request frequency |
| 9100 | Service disabled | AmzScope service temporarily disabled. Retry later. |
| 9101 | Data source unavailable | Upstream niche data source is down. Retry later. |
| 9102 | Quota exceeded | Provider-level quota hit. Contact support. |

## Authentication

- API keys are **permanent** (don't expire unless account deactivated)
- Error code `1004` triggers automatic key refresh
- Resolution order: `PANGOLINFO_API_KEY` env > `~/.pangolinfo_api_key` cache > fresh login

## Per-API Required Fields

| API | Required | On violation |
|-----|----------|--------------|
| `category-tree` | -- | -- |
| `category-search` | `keyword` | `1002 keyword is required` |
| `category-paths` | `categoryIds` (non-empty array) | `1002 categoryIds is required` |
| `category-filter` | `timeRange`, `sampleScope` | `1002 timeRange and sampleScope are required` |
| `niche-filter` | `marketplaceId` | `1002` from upstream |

**Page size cap:** `category-filter` and `niche-filter` enforce `size <= 10`. Exceeding returns `1002 pageSize must be less than 10`.

## Credit Costs

| API | Credits |
|-----|---------|
| Category Tree | 2 |
| Category Search | 2 |
| Category Paths | 2 |
| Category Filter | 5 |
| Niche Filter | 10 |

Credits consumed on success (code 0) only. Empty results are not charged.

## Common Issues

**"No authentication credentials" error** -- Set `PANGOLINFO_API_KEY` env var.

**Empty items array** -- Filters may be too narrow. Loosen `*Min`/`*Max` bounds or broaden `timeRange`.

**Timeout errors** -- Script retries 3x with exponential backoff. Check network.

**`9101 Data source temporarily unavailable`** -- Upstream provider is down. Not related to your account.
