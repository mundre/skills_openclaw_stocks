# Amazon Niche Data API Reference

Five APIs for exploring Amazon categories and niche markets using
Pangolinfo's 利基数据 (niche data) service.

## Common

### Base URL

```
https://scrapeapi.pangolinfo.com/api/v1/amzscope
```

### Headers

- `Content-Type: application/json`
- `Authorization: Bearer <token>`

> **Security note:** `<token>` in all curl examples below is a **placeholder**. Replace it with your own API key at runtime. Never paste real credentials into shared documents, issue trackers, or version-controlled files.

### Response envelope

All APIs return the same outer envelope:

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "items": { ... }     // shape varies per API (see below)
  }
}
```

### Pagination

For paginated APIs the `items` object contains:

```json
{
  "data": [ ... ],       // array of records for the current page
  "total": 1,            // total records matching the query
  "page": 1,             // current page (1-based)
  "size": 10,            // page size
  "totalPages": 1        // total pages
}
```

`category-filter` and `niche-filter` cap both `size` and `page` at 10.

### Credits

| API | Credits per request |
|-----|---------------------|
| Category Tree | 2 |
| Search Categories | 2 |
| Batch Category Paths | 2 |
| Category Filter | 5 |
| Niche Filter | 10 |

Empty-result responses are not charged.

### Marketplace IDs

Use the Amazon two-letter region code, e.g. `US`, `UK`, `DE`, `FR`, `JP`, `CA`, `IT`, `ES`, `MX`, `AU`, `BR`, `AE`, `SA`, `IN`.

---

## 1. Category Tree API (browseCategoryTreeAPI)

Walk the Amazon category tree. With no `parentBrowseNodeIdPath` it
returns top-level nodes; with one it returns that node's direct
children.

```
POST /api/v1/amzscope/categories/children
```

### Request body

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `parentBrowseNodeIdPath` | No | string | Parent node path. Examples: `"2619526011"`, `"2619526011/18116197011"`. Omit to get top-level nodes. |
| `page` | No | int | 1-based page number |
| `size` | No | int | Items per page |

### Node record fields (`data.items.data[]`)

| Field | Type | Description |
|-------|------|-------------|
| `browseNodeId` | string | Leaf node ID |
| `browseNodeIdPath` | string | Full path of node IDs, `/`-joined |
| `browseNodeName` | string | Node name (EN) |
| `browseNodeNameCn` | string | Node name (CN) |
| `browseNodeNamePath` | string | Full path of node names (EN) |
| `browseNodeNamePathCn` | string | Full path of node names (CN) |
| `parentBrowseNodeIdPath` | string | Parent path of IDs |
| `parentBrowseNodeNamePath` | string | Parent path of names (EN) |
| `parentBrowseNodeNamePathCn` | string | Parent path of names (CN) |
| `productType` | string | Amazon product type |
| `itemType` | string | Item type |
| `sellable` | int (0/1) | Whether the node is sellable |
| `hasChild` | int (0/1) | Whether the node has children |

### Example

```bash
curl -X POST https://scrapeapi.pangolinfo.com/api/v1/amzscope/categories/children \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{"parentBrowseNodeIdPath": "2619526011", "page": 1, "size": 10}'
```

---

## 2. Search Categories API (searchCategoriesAPI)

Full-text search across Amazon category names (EN and CN).

```
POST /api/v1/amzscope/categories/search
```

### Request body

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `keyword` | **Yes** | string | Search term; matches EN and CN names |
| `page` | No | int | 1-based page number |
| `size` | No | int | Items per page |

### Record fields (`data.items.data[]`)

Same as Category Tree node records (see above).

### Example

```bash
curl -X POST https://scrapeapi.pangolinfo.com/api/v1/amzscope/categories/search \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{"keyword": "headphones", "page": 1, "size": 10}'
```

### Errors

- `1002 Invalid Parameter: keyword is required` — missing or blank keyword.

---

## 3. Batch Category Paths API (batchCategoryPathsAPI)

Resolve one or more category IDs to their full hierarchy paths in a
single call.

```
POST /api/v1/amzscope/categories/paths
```

### Request body

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `categoryIds` | **Yes** | string[] | Non-empty list of category IDs |

### Response shape

Unlike the other APIs, this one returns a flat `items` **array**:

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "items": [
      {
        "categoryId": "2619526011",
        "categoryName": "Cell Phones & Accessories",
        "categoryNameCn": "手机及配件",
        "browseNodeNamePaths":   ["Electronics", "Cell Phones & Accessories"],
        "browseNodeNamePathCns": ["电子产品", "手机及配件"]
      }
    ]
  }
}
```

### Record fields

| Field | Type | Description |
|-------|------|-------------|
| `categoryId` | string | Category ID (echo of input) |
| `categoryName` | string | English category name |
| `categoryNameCn` | string | Chinese category name |
| `browseNodeNamePaths` | string[] | EN name path, root → leaf |
| `browseNodeNamePathCns` | string[] | CN name path, root → leaf |

### Example

```bash
curl -X POST https://scrapeapi.pangolinfo.com/api/v1/amzscope/categories/paths \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{"categoryIds": ["2619526011", "172282"]}'
```

### Errors

- `1002 Invalid Parameter: categoryIds is required` — missing or empty array.

---

## 4. Category Filter API (categoryFilterAPI)

Filter Amazon categories by a large set of business metrics
(units sold, search volume, returns, price tiers, trends, etc.).
Returns aggregated metrics per category.

```
POST /api/v1/amzscope/categories/filter
```

### Required fields

| Field | Type | Description |
|-------|------|-------------|
| `marketplaceId` | string | Amazon marketplace (`US`, `UK`, `DE`, ...) |
| `timeRange` | string | Aggregation time range (e.g. `l7d`, `l30d`, `l90d`) |
| `sampleScope` | string | Sample scope (e.g. `all_asin`) |

### Optional scalar fields

| Field | Type | Description |
|-------|------|-------------|
| `categoryId` | string | Single-category detail (returns 1 record) |
| `page` | int | Page number (**max 10**) |
| `size` | int | Records per page (**max 10**) |
| `sortField` | string | Any response field name |
| `sortOrder` | string | `asc` or `desc` |

### Numeric range filters

All support `*Min` and `*Max` variants, e.g. `buyBoxPriceAvgMin: 5000`.

Available prefixes:

`unitSoldSum`, `glanceViewsSum`, `searchVolumeSum`,
`netShippedGmsSum`, `buyBoxPriceAvg`, `searchToPurchaseRatio`,
`returnRatio`, `asinCount`, `offersPerAsin`, `newAsinCount`,
`newBrandCount`, `avgAdSpendPerClick`

### Tier / level filters

Array fields — send the allowed tokens for values you want to keep:

| Field | Allowed values |
|-------|----------------|
| `buyBoxPriceTiers` | `budget`, `mainstream`, `premium`, `luxury` |
| `searchToPurchaseRatioLevels` | `to_improve`, `average`, `excellent` |
| `returnRatioLevels` | `excellent`, `average`, `risk` |
| `asinCountLevels` | `<P25`, `P25-P50`, `P50-P75`, `>P75` |
| `offersPerAsinLevels` | `<P25`, `P25-P50`, `P50-P75`, `>P75` |
| `newAsinCountLevels` | `<P25`, `P25-P50`, `P50-P75`, `>P75` |
| `newBrandCountLevels` | `<P25`, `P25-P50`, `P50-P75`, `>P75` |
| `avgAdSpendPerClickLevels` | `<P25`, `P25-P50`, `P50-P75`, `>P75` |

### Trend filters

Apply to the metrics `unitSold`, `glanceViews`, `searchVolume`,
`netShippedGms`. Pattern:
`{metric}TrendDirections`, `{metric}VolatilityLevels`,
`{metric}ChangeRateBuckets`, `{metric}LastVsSelfAvgBuckets`.

| Filter type | Allowed values |
|-------------|----------------|
| TrendDirections | `strong_up`, `up`, `stable`, `down`, `strong_down` |
| VolatilityLevels | `low`, `medium`, `high` |
| ChangeRateBuckets | `high_growth`, `medium_growth`, `low_growth`, `stable`, `low_decline`, `medium_decline`, `high_decline` |
| LastVsSelfAvgBuckets | `above_baseline`, `around_baseline`, `below_baseline` |

### Quantile bucket filters

| Field | Allowed values |
|-------|----------------|
| `unitSoldQuantileBuckets` | `<P25`, `P25-P50`, `P50-P75`, `>P75` |
| `glanceViewsQuantileBuckets` | (same) |
| `searchVolumeQuantileBuckets` | (same) |
| `netShippedGmsQuantileBuckets` | (same) |

### Response record fields (partial)

Each record in `data.items.data[]` aggregates metrics for a category.
Key fields:

- **Identity:** `id`, `categoryId`, `marketplaceId`, `timeRange`, `sampleScope`, `snapshotDate`
- **Volume sums:** `unitSoldSum`, `glanceViewsSum`, `searchVolumeSum`, `clickCountSum`, `netShippedGmsSum`
- **Period counts:** `*PeriodCount` variants of the above
- **Price:** `buyBoxPriceAvg`, `buyBoxPriceTier`
- **Ratios:** `searchToPurchaseRatio`, `returnRatio`, `searchToPurchaseRatioLevel`, `returnRatioLevel`
- **Supply side:** `asinCount`, `offersPerAsin`, `newAsinCount`, `newBrandCount`, plus `*Level` variants
- **Ads:** `avgAdSpendPerClick`, `medianAdSpendPerClick`, plus `*Level` variants
- **Keyword reach:** `maxKeywordSearchVolume`
- **Quantile buckets:** `{metric}QuantileBucket`
- **Trend block (per metric):**
  `{metric}TrendDirection`,
  `{metric}VolatilityLevel`,
  `{metric}ChangeRateBucket`,
  `{metric}SelfAvg`,
  `{metric}LastVsSelfAvgPct`,
  `{metric}LastVsSelfAvgBucket`

  applied to: `unitSold`, `glanceViews`, `searchVolume`, `clickCount`,
  `netShippedGms`, `buyBoxPrice`.

### Example

```bash
curl -X POST https://scrapeapi.pangolinfo.com/api/v1/amzscope/categories/filter \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "marketplaceId": "US",
    "timeRange": "l7d",
    "sampleScope": "all_asin",
    "categoryId": "979832011",
    "page": 1,
    "size": 10
  }'
```

### Errors

- `1002 Invalid Parameter: timeRange and sampleScope are required`
- `1002 Invalid Parameter: pageSize must be less than 10` — when `pageSize > 10`
- `9101 Data source temporarily unavailable`

---

## 5. Niche Filter API (nicheFilterAPI)

Filter Amazon **niches** (curated product clusters) by a wide range of
business metrics. Same envelope shape as the category filter, but
operates over niches rather than categories.

```
POST /api/v1/amzscope/niches/filter
```

### Required fields

| Field | Type | Description |
|-------|------|-------------|
| `marketplaceId` | string | Amazon marketplace |

### Optional scalar fields

| Field | Type | Description |
|-------|------|-------------|
| `nicheId` | string | Specific niche ID for detailed report |
| `nicheTitle` | string | Keyword match on niche title |
| `page` | int | Page number (**max 10**) |
| `size` | int | Records per page (**max 10**) |
| `sortField` | string | Any response field name |
| `sortOrder` | string | `asc` or `desc` |

### Numeric range filters

All support `*Min` / `*Max` variants, e.g. `searchVolumeT90Min: 1000`.

Available prefixes:

- **Search volume:** `searchVolumeT90`, `searchVolumeT360`,
  `searchVolumeGrowthT90`, `searchVolumeGrowthT180`, `searchVolumeGrowthT360`
- **Units sold:** `minimumUnitsSoldT360`, `maximumUnitsSoldT360`,
  `minimumAverageUnitsSoldT360`, `maximumAverageUnitsSoldT360`
- **Price:** `minimumPrice`, `maximumPrice`, `avgProductPrice`
- **Quality / reviews:** `avgReviewCount`, `avgReviewRating`,
  `avgDetailPageQuality`, `avgBestSellerRank`
- **Catalog:** `productCount`, `brandCount`, `sellingPartnerCountT360`,
  `avgBrandAgeT360`, `avgSellingPartnerAge`
- **Share / concentration:** `top5ProductsClickShareT360`,
  `top20ProductsClickShareT360`, `top5BrandsClickShare`, `top20BrandsClickShare`
- **Ad/Prime mix:** `sponsoredProductsPercentageT360`, `primeProductsPercentageT360`
- **Operations:** `returnRateT360`, `avgOosRateT360`
- **Launch activity:** `successfulLaunchesT90`, `successfulLaunchesT180`,
  `successfulLaunchesT360`, `newProductsLaunchedT180`, `newProductsLaunchedT360`

### Response record fields (partial)

Each record in `data.items.data[]`:

- **Identity:** `id`, `nicheId`, `nicheTitle`
- **Volume:** `searchVolumeT90`, `searchVolumeT360`, `avgPrice`
- **Catalog counts:** `productCount`, `brandCount`, `sellingPartnerCountT360`
- All metric prefixes listed above are returned as response fields.

### Example

```bash
curl -X POST https://scrapeapi.pangolinfo.com/api/v1/amzscope/niches/filter \
  -H 'Authorization: Bearer <token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "marketplaceId": "US",
    "nicheTitle": "yoga mat",
    "page": 1,
    "size": 10
  }'
```

### Errors

- `1002 Invalid Parameter: pageSize must be less than 10` — when `pageSize > 10`
- `9101 Data source temporarily unavailable`

---

## Notes

- Average response time for these APIs is about 5–10 seconds.
- The `items` field is returned as an **object** (with pagination) for
  tree / search / filter APIs, and as a **flat array** for
  `categories/paths`. The included Python client normalizes both
  shapes when `--raw` is not used.
