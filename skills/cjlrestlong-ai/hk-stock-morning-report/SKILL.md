---
name: hk-stock-morning-report
description: >
  Generate HK stock market morning report (股市晨報) for Chinese bank trading desk.
  Use when user asks "生成晨报", "股市晨报", "今日股市", "港股晨報", or any similar HK stock market report request.
  Produces a 4-section daily report: market review, southbound capital flow, hot market news, and top HK stock.
  Follows strict format rules and sends via WeChat personal + Feishu group.
---

# HK Stock Morning Report (股市晨報)

## Workflow (执行步骤)

### Step 1: Read Format Template
Read `references/stock_report_format.md` — this is the source of truth for all format rules. Do not deviate.

### Step 2: Determine Date Header
**⚠️ Big title date (x.xx) = Report generation date (natural day), NOT last trading day — confirmed by Stephen on 2026-04-19**

Example: Report generated on Sunday Apr 19 but covering Friday Apr 18 trading → big title = `4.19`, Section 1 = `上週五股巿回顧`

Find the last trading day and determine the Section 1 header:
- Same week, no gap → `📍一、昨日股巿回顧`
- Same week, gap (holiday) → `📍週X股巿回顧`
- Last week → `📍上週X股巿回顧`

### Step 3: Fetch Index Data
- Hang Seng Index: `https://qt.gtimg.cn/q=r_hkHSI`
  - Field[3] = current price, Field[4] = previous close
  - Calculate: change points = price - prev_close; change% = (price-prev_close)/prev_close × 100
- Hang Seng Tech Index: `https://qt.gtimg.cn/q=r_hkHSTECH` (same parsing)

### Step 4: Search Section 1 (Market Review)
- Search: `site:gelonghui.com "港股收評" "昨日日期"`
- Extract: market overview (30-50 chars), strong/weak stocks with exact figures, sector performance
- Fallback: futunn or Yahoo Finance

### Step 5: Search Section 2 (Southbound Capital)
- Primary: `site:stcn.com "南向資金" "昨日日期"`
- Also: `site:gelonghui.com "南向資金" "昨日日期"`
- Extract: total southbound amount (HK$ XX億), breakdown by 港股通(滬)/港股通(深), top net buy/sell stocks
- Fallback: `site:futunn.com "南下" "昨日日期"`
- ⚠️ **重要區分**：stcn.com的「成交活躍股」口徑（如XX億）不等於全市場南向資金總數，必須使用全市場總數字
- ⚠️ **當細分（滬/深）數字不確定時：保留📈📉兩行並填入「待更新」，不得刪除行**

### Step 6: Search Section 3 (Hot News) — ⚠️ Search TODAY's date
- Search today's date + "港股" + "熱點" or "最新"
- Must search today's news, NOT last trading day's market data
- Even if HK market is closed, there are macro policy, international market, broker reports with today's date
- If no results → write "待更新", do NOT fabricate data
- Select 3 most relevant news items

### Step 7: Search Section 4 (Top HK Stock) — Select 1 stock
- Search today's date + hot HK stock individual news
- Select 1 stock only

### Step 8: Generate Report
Assemble the report strictly following the format template. Big title = 3 Section 3 ▶️ titles joined by semicolons. Write `🚨待更新` if data unavailable — never estimate.

### Step 9: Pre-Send Verification
Read `references/errors.md` and verify each item. Check:
- [ ] Big title = Section 3 ▶️ titles (do not rewrite)
- [ ] Arrow direction: 📈=net buy, 📉=net sell
- [ ] No estimated numbers (write 🚨待更新 if uncertain)
- [ ] Format: 📍 has no space after, ▶️ has no bold, Section 4 has only 1 stock, **▶️ title and content must have an empty line between them**
- [ ] 📈📉 rows with uncertain data: keep the rows, write "待更新", do NOT delete the rows

### Step 10: Send
**⚠️ 飛書必須同時發送兩種格式（不可只發一種）：**
1. **卡片**：完整晨報內容，header為「🔴股市晨報」
2. **代碼塊**：純文字版本，方便用戶一鍵複製

卡片→代碼塊，依序發送。

微信個人：純文字格式（不需卡片）

### 香港政府假日官網（2026-04-20 新增）
- **原則**：查香港假日資訊，**只使用香港政府官網**
- 官網：`https://www.gov.hk/sc/about/abouthk/holiday/2026.htm`
- 示例：復活節日期、核證交易日等，均以官網為準

## Key Format Rules (7 Rigid Constraints)

1. Big title contains 🔴 and 🔵
2. 📍一: X = 昨日 / 週一~週五 / 上週一~上週五
3. 📍二: Direction from actual data (📈=net buy, 📉=net sell)
4. Numbers with（港元）: only the first line of Section 2 header (e.g., `凈買入xx億（港元）`), the 📈📉 lines and summary do NOT repeat （港元）
5. ▶️ Title and content **must have an empty line between** (Error 9 — most frequently violated)
6. Section 4: only 1 stock
7. 📍 followed directly by text, no space

## Data Sources

| Content | Source |
|---------|--------|
| Index (close/change) | Tencent Finance API qt.gtimg.cn |
| Section 1 (market overview) | gelonghui.com 港股收評 |
| Section 2 (southbound) | **stcn.com (primary) + gelonghui.com; futunn.com (fallback)** |
| Section 3 (hot news) | Web search for today's date |
| Section 4 (top stock) | Web search for today's individual stock news |
