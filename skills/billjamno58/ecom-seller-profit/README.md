# Multi-Platform Order Profit Calculator

Upload order exports from **any e-commerce platform or ERP** — automatically calculate net profit per order. Supports TikTok Shop, Allegro, Temu Half-Hosted, Amazon, SHEIN, Fruugo, Shopee, Ozon, and all other major platforms.

## Pricing

| Tier | Price | Order Limit | Store Limit | Features |
|------|------|:-----------:|:-----------:|----------|
| **Free** | ¥0 | 20 orders/mo | 1 | Basic profit calculation |
| **Standard** | ¥29/mo | 500 orders/mo | 3 | Full features + report export |
| **Pro** | ¥99/mo | Unlimited | Unlimited | SKU analysis + trend charts |
| **Enterprise** | ¥299/mo | Unlimited | Unlimited | History + multi-user |

### Upgrade to Pro

Purchase at [https://yk-global.com](https://yk-global.com), get your API Key, then configure:

```bash
export PROFIT_API_KEY=your_secret_key
python3 scripts/parse_orders.py orders.xlsx --api
```

---

## Quick Start

```bash
# Local run (free tier) — auto-detects any platform format
python3 scripts/parse_orders.py orders.xlsx

# Output JSON format
python3 scripts/parse_orders.py orders.xlsx --json result.json
```

**Import from:**
- Miaoshou ERP / Qianniu / Dianxiaomi and other ERP exports
- Allegro / Temu / Amazon / TikTok Shop direct backend exports
- Any Excel file containing order ID, revenue, and cost fields

---

## Supported Platforms

| Platform | Status | Notes |
|----------|:------:|-------|
| TikTok Shop | ✅ | ERP or platform backend export |
| Allegro | ✅ | ERP or platform backend export |
| Temu Half-Hosted | ✅ | ERP or platform backend export |
| SHEIN | ✅ | ERP or platform backend export |
| Fruugo | ✅ | ERP or platform backend export |
| Amazon | ✅ | Platform backend export |
| Shopee / Lazada | ✅ | Platform backend export |
| Ozon | ✅ | Platform backend export |
| Walmart / eBay | ✅ | Platform backend export |
| Other platforms | ✅ | Auto field detection |

> **Field mapping is automatic** — no platform restrictions. As long as the export file contains standard order fields, it will work.

---

## Calculation Logic

**Net Profit = Platform Revenue - Platform Expense - Order Cost**

| Module | Description |
|--------|-------------|
| **Platform Revenue** | Transaction income + shipping income + refunds + platform subsidies |
| **Platform Expense** | Platform commission + tech fees + shipping + refunds + violation fines + taxes |
| **Order Cost** | Purchase cost + first-leg freight + last-mile shipping + packaging + warehouse fees + advertising |

---

## Dependencies

- Python 3.8+
- openpyxl (`pip install openpyxl`)

---

## Support

- Website: [https://yk-global.com](https://yk-global.com)
- Feedback: Contact customer service

---

> The free tier is permanently free with no expiration. Paid tiers provide API hosting and advanced analytics.

> For paid plans, visit [YK-Global.com](https://yk-global.com)
