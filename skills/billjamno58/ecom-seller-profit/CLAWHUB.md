# ClawHub Listing — Multi-Platform Order Profit Calculator

## Basic Info

- **Slug**: `ecom-seller-profit` *(pending SkillPay registration)*
- **Name**: Multi-Platform Order Profit Calculator
- **Subtitle**: Upload order exports from any e-commerce platform — automatically calculate net profit per order
- **Category**: Finance / E-commerce Analytics
- **Tags**: `profit`, `orders`, `e-commerce`, `Excel`, `CSV`, `TikTok`, `Amazon`, `Allegro`, `Temu`, `SHEIN`, `Fruugo`

---

## Description

Upload order exports from **any e-commerce platform or ERP** — automatically calculate net profit per order.

**Supported platforms:** TikTok Shop, Allegro, Temu Half-Hosted, Amazon, SHEIN, Fruugo, Shopee, Ozon, Walmart, eBay, and all other major platforms.

**No platform restrictions** — as long as the export file contains standard order fields (order ID, revenue, cost), it works.

---

## Features

- **Multi-platform Support** — Auto-detects any platform format via field aliases (Allegro → TikTok 170-col standard mapping)
- **Profit Calculation** — Net Profit = Revenue - Platform Expense - Order Cost
  - Revenue: Transaction + shipping income + refunds + subsidies
  - Expense: Commission + tech fees + shipping + refunds + fines + taxes
  - Cost: Purchase cost + first-mile freight + last-mile shipping + packaging + warehouse + advertising
- **Field Auto-mapping** — No manual platform configuration needed
- **Excel/CSV Output** — Structured profit report with platform breakdown
- **Multi-format Support** — .xlsx, .xls, .csv

---

## Pricing

**$0.01 USDT per call** via SkillPay.me

No subscription tiers — pay only for what you use.

---

## Requirements

- Python 3.8+
- `openpyxl` (`pip install openpyxl`)

---

## Quick Start

```bash
pip install openpyxl

python3 scripts/parse_orders.py orders.xlsx

# Output JSON
python3 scripts/parse_orders.py orders.xlsx --json result.json

# Markdown report
python3 scripts/parse_orders.py orders.xlsx --markdown report.md
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SKILL_BILLING_API_KEY` | SkillPay Builder API Key |
| `SKILL_BILLING_SKILL_ID` | SkillPay Skill ID |
| `FEISHU_USER_ID` | User ID for billing |

---

## File Structure

```
seller-profit-calculator/
├── SKILL.md              # Skill definition
├── README.md             # Documentation
├── CLAWHUB.md            # ClawHub listing (this file)
├── requirements.txt      # Python dependencies
└── scripts/
    ├── parse_orders.py    # Main parser + profit calculation
    └── analyze_headers.py  # Header analysis utility
```

---

## Supported Platforms

| Platform | Status |
|----------|--------|
| TikTok Shop | ✅ ERP or platform backend export |
| Allegro | ✅ ERP or platform backend export |
| Temu Half-Hosted | ✅ ERP or platform backend export |
| SHEIN | ✅ ERP or platform backend export |
| Fruugo | ✅ ERP or platform backend export |
| Amazon | ✅ Platform backend export |
| Shopee / Lazada | ✅ Platform backend export |
| Ozon | ✅ Platform backend export |
| Walmart / eBay | ✅ Platform backend export |
| Other platforms | ✅ Auto field detection |

---

## Calculation Logic

**Net Profit = Platform Revenue - Platform Expense - Order Cost**

| Module | Description |
|--------|-------------|
| **Platform Revenue** | Transaction income + shipping income + refunds + platform subsidies |
| **Platform Expense** | Commission + tech fees + shipping + refunds + violation fines + taxes |
| **Order Cost** | Purchase cost + first-leg freight + last-mile shipping + packaging + warehouse fees + advertising |
