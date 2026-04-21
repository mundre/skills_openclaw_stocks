# Output Schema Reference

## Envelope Structure

### Success Envelope (stdout)

```json
{
  "success": true,
  "api": "<string>",
  "items": [ ... ],
  "total": "<int>",
  "page": "<int>",
  "size": "<int>",
  "totalPages": "<int>",
  "results_count": "<int>"
}
```

### Error Envelope (stderr)

```json
{
  "success": false,
  "error": {
    "code": "<string>",
    "api_code": "<int>",
    "message": "<string>",
    "hint": "<string>"
  }
}
```

## Success Fields

| Field | Type | Guaranteed | Description |
|-------|------|------------|-------------|
| `success` | boolean | Yes | Always `true` |
| `api` | string | Yes | API label (e.g. `browseCategoryTreeAPI`) |
| `items` | array | Yes | Data records for this page |
| `results_count` | int | Yes | Number of items in current page |
| `total` | int | No | Total matching records (paginated APIs only) |
| `page` | int | No | Current page number (paginated APIs only) |
| `size` | int | No | Page size (paginated APIs only) |
| `totalPages` | int | No | Total pages (paginated APIs only) |

## Per-API Item Fields

### Category Tree / Category Search (`items[]`)

| Field | Type | Description |
|-------|------|-------------|
| `browseNodeId` | string | Node ID |
| `browseNodeIdPath` | string | Full path of node IDs (`/`-joined) |
| `browseNodeName` | string | Node name (EN) |
| `browseNodeNameCn` | string | Node name (CN) |
| `browseNodeNamePath` | string | Full name path (EN) |
| `browseNodeNamePathCn` | string | Full name path (CN) |
| `parentBrowseNodeIdPath` | string | Parent node ID path |
| `parentBrowseNodeNamePath` | string | Parent name path (EN) |
| `parentBrowseNodeNamePathCn` | string | Parent name path (CN) |
| `productType` | string | Amazon product type |
| `itemType` | string | Item type |
| `sellable` | int (0/1) | Whether sellable |
| `hasChild` | int (0/1) | Whether has children |

### Category Paths (`items[]`)

| Field | Type | Description |
|-------|------|-------------|
| `categoryId` | string | Category ID (echo of input) |
| `categoryName` | string | English category name |
| `categoryNameCn` | string | Chinese category name |
| `browseNodeNamePaths` | string[] | EN name path, root to leaf |
| `browseNodeNamePathCns` | string[] | CN name path, root to leaf |

Note: Category Paths returns a flat array without pagination metadata (`total`, `page`, `size`, `totalPages` are absent).

### Category Filter (`items[]`)

Key fields (partial -- full response has 70+ fields):

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Record ID |
| `categoryId` | string | Amazon category ID |
| `marketplaceId` | string | Marketplace code |
| `timeRange` | string | Aggregation time range |
| `sampleScope` | string | Sample scope |
| `snapshotDate` | string | Data snapshot date |
| `unitSoldSum` | float | Total units sold |
| `glanceViewsSum` | float | Total glance views |
| `searchVolumeSum` | float | Total search volume |
| `netShippedGmsSum` | float | Total net shipped GMS |
| `buyBoxPriceAvg` | float | Average buy box price |
| `buyBoxPriceTier` | string | Price tier: `budget`, `mainstream`, `premium`, `luxury` |
| `searchToPurchaseRatio` | float | Search-to-purchase ratio |
| `returnRatio` | float | Return ratio |
| `asinCount` | float | ASIN count |
| `newAsinCount` | float | New ASIN count |
| `newBrandCount` | float | New brand count |
| `{metric}TrendDirection` | string | Trend: `strong_up`, `up`, `stable`, `down`, `strong_down` |
| `{metric}VolatilityLevel` | string | Volatility: `low`, `medium`, `high` |
| `{metric}ChangeRateBucket` | string | Change: `high_growth` ... `high_decline` |
| `{metric}LastVsSelfAvgBucket` | string | vs baseline: `above_baseline`, `around_baseline`, `below_baseline` |
| `{metric}QuantileBucket` | string | Quantile: `<P25`, `P25-P50`, `P50-P75`, `>P75` |

Metrics with trend blocks: `unitSold`, `glanceViews`, `searchVolume`, `clickCount`, `netShippedGms`, `buyBoxPrice`.

### Niche Filter (`items[]`)

Key fields (partial -- full response has 100+ fields):

| Field | Type | Description |
|-------|------|-------------|
| `id` | int | Record ID |
| `nicheId` | string | Unique niche identifier |
| `nicheTitle` | string | Niche title |
| `searchVolumeT90` | float | 90-day search volume |
| `searchVolumeT360` | float | 360-day search volume |
| `searchVolumeGrowthT90` | float | 90-day search volume growth rate |
| `avgPrice` | float | Average product price |
| `productCount` | int | Product count |
| `brandCount` | int | Brand count |
| `sellingPartnerCountT360` | int | Selling partner count (360d) |
| `returnRateT360` | float | Return rate (360d) |
| `sponsoredProductsPercentageT360` | float | Sponsored products % (360d) |
| `primeProductsPercentageT360` | float | Prime products % (360d) |
| `top5ProductsClickShareT360` | float | Top 5 products click share (360d) |
| `top5BrandsClickShare` | float | Top 5 brands click share |
| `referenceAsinImageUrl` | string | Reference ASIN image URL |
| `currency` | string | Currency code (e.g. USD) |

## Error Fields

| Field | Type | Guaranteed | Description |
|-------|------|------------|-------------|
| `success` | boolean | Yes | Always `false` |
| `error.code` | string | Yes | Machine-readable error code |
| `error.api_code` | int | No | Pangolinfo API error code (when applicable) |
| `error.message` | string | Yes | Human-readable description |
| `error.hint` | string | No | Suggested resolution |

## Auth-Only Output (stdout)

```json
{
  "success": true,
  "message": "Authentication successful",
  "api_key_preview": "eyJh...ab1c"
}
```

## Raw Mode

When using `--raw`, the unprocessed Pangolinfo API response is output. The envelope structure above does **not** apply.
