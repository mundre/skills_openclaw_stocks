---
name: seller-profit-calculator
description: Multi-platform Order Profit Calculator — upload order exports from any e-commerce platform or ERP, get instant profit reports by order, store, SKU, and platform.
display_name: Seller Profit Calculator
version: 1.0.0
author: YKGlobal
tags: [ecommerce, profit-calculation, orders, temu, shein, allegro, tiktok-shop, amazon, shopee, ozon, walmart, ebay]
---

# Seller Profit Calculator

Upload order exports from **any e-commerce platform or ERP** → get instant profit breakdown by order, store, SKU, and platform.

![Profit Report](https://img.shields.io/badge/profit-report-green)
![All Platforms](https://img.shields.io/badge/-All%20Platforms-blue)
![Auto-detect](https://img.shields.io/badge/-Auto--detect-orange)

## What It Does

**Upload one Excel file → get a complete profit breakdown:**

- 📋 **Overall summary**: total orders, completed, cancelled, total revenue, total cost, net profit, net margin %
- 🌍 **By platform**: revenue / expense / cost / profit per platform
- 🏪 **By store**: revenue / expense / cost / profit per store
- 🔴 **Bottom 5 orders**: worst loss-making orders highlighted
- 🟢 **Top 5 orders**: best performing orders highlighted
- ✅ **Cross-check**: calculated profit vs platform-declared profit — validates accuracy per order

---

## How It Works — Agent-Powered Field Mapping

This Skill is not a static field-mapping tool. The AI Agent handles the messy reality of real export files.

### The Workflow

```
You upload any Excel order export
        ↓
Agent reads headers + sample rows (analyze_headers.py)
        ↓
Agent identifies each column's meaning (LLM reasoning)
        ↓
Agent builds field_map JSON → passes to parse_orders.py
        ↓
parse_orders.py calculates with full field context
        ↓
Report with per-order breakdown + accuracy notes
```

### Field Map Example

```json
{
  "buyer_total_paid": "buyer_total_paid",
  "cost_of_goods": "cost_of_goods",
  "net_profit": "net_profit",
  "store_name": "store_name",
  "country": "country"
}
```

### What the Agent Does

1. **Auto-detects standard fields** — 38 standard field names recognized across Allegro, Temu, TikTok, Amazon, etc.
2. **Semantic matching for unknown columns** — if a column isn't in the standard list, the Agent infers its meaning from the column name + sample values
3. **Handles missing fields** — if a required field is absent, the Agent notes it and estimates impact
4. **Produces field_map JSON** — passed directly to the parser via `--field-map`

### CLI Usage

```bash
# Auto-detect (works if column names match standard fields)
python3 scripts/parse_orders.py orders.xlsx

# With Agent-provided field mapping
python3 scripts/parse_orders.py orders.xlsx --field-map '{"buyer_paid":"buyer_paid","item_cost":"item_cost"}'

# Or load from file
python3 scripts/parse_orders.py orders.xlsx --field-map @my_mapping.json

# Analyze file headers first (for Agent to inspect)
python3 scripts/analyze_headers.py orders.xlsx --json headers.json
```

---

## Supported Platforms

All e-commerce platforms and ERPs that export order data with standard fields: order ID, revenue, costs, profit.

| Platform | Export Source | Status |
|----------|-------------|--------|
| Allegro | ERP / Platform backend | ✅ Verified |
| Temu Half-Hosted | ERP / Platform backend | ✅ Verified |
| TikTok Shop | ERP / Platform backend | ✅ Verified |
| SHEIN | ERP / Platform backend | ✅ Verified |
| Fruugo | ERP / Platform backend | ✅ Verified |
| Amazon | Platform backend | ✅ Compatible |
| Shopee / Lazada | ERP / Platform backend | ✅ Compatible |
| Ozon | ERP / Platform backend | ✅ Compatible |
| Walmart | ERP / Platform backend | ✅ Compatible |
| eBay | ERP / Platform backend | ✅ Compatible |
| Other platforms | ERP / Platform backend | ✅ Generic |

**Field mapping is automatic.** Any export file containing standard fields — order ID, transaction revenue, purchase cost, shipping, profit — will work automatically.

---

## Installation

```bash
openclaw skill install seller-profit-calculator
```

Or use the ClawHub import URL:
```
https://clawhub.ai/import
```

---

## Usage

### Quick Start

```bash
# Auto-detects format — works with any platform's export
python scripts/parse_orders.py orders.xlsx

# Output JSON for further processing
python scripts/parse_orders.py orders.xlsx --json result.json
```

### Input

Upload your order export Excel file from **any platform or ERP** — Miaoshou ERP, Qianniu, Dianxiaomi, Allegro backend, Temu backend, Amazon Seller Central, etc.
Supported extensions: `.xlsx`, `.xls`.

### Output

**Markdown report** printed to stdout:

```
📊 Order Profit Analysis Report

## 📋 Overall Summary
| Metric | Value |
|--------|-------|
| Total Orders | 21 |
| Total Platform Revenue | ¥14,145.40 |
| Total Platform Expense | ¥576.66 |
| Total Order Cost | ¥12,554.53 |
| Calculated Net Profit | ¥1,014.21 |
| Net Margin | 7.2% |

## 🌍 By Platform Summary
...

## 🔴 Bottom 5 Loss-Making Orders
...

## 🟢 Top 5 Profitable Orders
...
```

---

## Calculation Logic

### Net Profit Formula

```
Net Profit = Platform Revenue - Platform Expense - Order Cost
```

### Platform Income
```
Platform Income = Transaction Revenue + Shipping Income (absolute)
                + Refunds + Other Platform Subsidies
```

### Platform Expense
```
Platform Expense = Platform Commission + Tech Service Fee
                 + Shipping (platform side) + Refund Amount
                 + Violation Fines + Customs Duty + VAT
                 + Other Platform Fees
```

### Order Cost
```
Order Cost = Purchase Cost + First-Leg Freight + Last-Mile Shipping
           + Packaging Fee + Warehouse Handling Fee
           + Advertising Cost + Operating Cost + Other Costs
```

**Field names are auto-normalized.** Whether the export uses "buyer_paid", "transaction_revenue", or "order_amount" — all are recognized correctly.

---

## Pricing

| Tier | Price | Limits | Target |
|------|-------|--------|--------|
| Free | ¥0 | 20 orders/mo, 1 store | Trial |
| Standard | ¥29/mo | 500 orders/mo, 3 stores | Small sellers |
| Pro | ¥99/mo | Unlimited orders, unlimited stores | Active sellers |
| Enterprise | ¥299/mo | Unlimited + history + multi-user | Teams |

**Note:** This Skill itself is free to install. The tiers above apply to the hosted API version (coming soon at yk-global.com).

---

## Validation

Validated against real order data from multiple platforms — per-order profit match rate 100%:

| Platform | Orders | Per-order Accuracy |
|----------|--------|-------------------|
| Allegro | 21 | ✅ Exact |
| Temu Half-Hosted | 28 | ✅ Exact (28/28) |

---

## FAQ

**Q: My platform is not listed. Will it work?**
A: Yes. As long as your export file contains order ID, revenue, and cost fields, it will work. Automatic field mapping has no platform restrictions.

**Q: Does it support CSV?**
A: Currently only Excel (.xlsx / .xls) is supported. CSV support is in the v2.0 roadmap.

**Q: Why doesn't the profit match the platform backend exactly?**
A: Per-order calculations are precise when fields are transparent. When aggregating, some platforms have additional fees (exchange rate differences, internal settlement adjustments) that don't appear in the export fields and cannot be reconstructed. The value of this tool is: **precisely identify which order lost money and which made money** — providing data for operational decisions.

**Q: Does it support settlement reports?**
A: Settlement report support is in v2.0. Currently v1.0 reads order-level profit data.

---

## File Structure

```
seller-profit-calculator/
├── SKILL.md               ← This file
├── README.md              ← User-facing documentation
└── scripts/
    ├── parse_orders.py    ← Core parser (supports --field-map)
    └── analyze_headers.py ← Header + sample analyzer for Agent use
```

---

## License

MIT — YKGlobal

> For paid plans, visit [YK-Global.com](https://yk-global.com)
