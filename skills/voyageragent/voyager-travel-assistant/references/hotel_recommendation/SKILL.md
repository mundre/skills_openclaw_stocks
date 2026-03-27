---
name: hotel-recommendation
description: Hotel search and recommendation skill for complex queries based on city, landmark(POI), hotel name, or brand names.
---

Hotel recommendation skill.

## ⚠️ CRITICAL CONSTRAINT - READ FIRST ⚠️

**All hotel recommendations MUST originate exclusively from the actual data returned by the `hotelSearch` tool.**

### **Absolutely Prohibited Actions:**
- ❌ Assuming or fabricating hotel information.
- ❌ Recommending hotels based on prior knowledge.
- ❌ Creating "potential" options when `hotelSearch` returns no data.
- ❌ Recommending hotels from outside the data source.

### **Mandatory Requirements:**
- ✅ All information must come from the `hotelSearch` JSON response.
- ✅ When no data is returned, explicitly state "The `hotelSearch` tool did not return any matching hotels."
- ✅ Display only the actual, parsed hotel data.
- ✅ **Strict Parameter Configuration**: The `subQuery` field must be populated and cannot be empty.

**Violation of this constraint will be considered a critical skill usage error.**

## Usage

When user asks about hotels with explicit geographic or hotel entity identifiers:
- city name (市, 城市)
- point of interest (POI, 地标, 景点, 公园)
- hotel name (酒店名, 饭店名)
- brand names (品牌, 连锁酒店)

## Workflow

1. **Declaration**: First, state: "All hotel recommendations will be based on the actual results from the hotelSearch tool."

2. **Collect Search Parameters**: Extract key parameters from the user's query:
   - `checkInDate`: Check-in date (YYYY-MM-DD), defaults to today + 7 days (T+7)
   - `checkOutDate`: Check-out date (YYYY-MM-DD), defaults to today + 8 days (T+8)
   - `city`: City name, defaults to user's current city
   - `country`: Country name
   - `nearby`: A single POI for proximity search
   - `hotelNames`: List of specific hotel names
   - `brandNames`: List of hotel brand names
   - `subQuery`: **(Required)** Original query segment or user intention

3. **Handle Silent Defaults**: Apply defaults **silently** without asking user:
   - Missing checkInDate → today + 7 days
   - Missing checkOutDate → today + 8 days
   - Missing city → user's current city
   - **Do NOT ask the user for missing information**

4. **Decompose and Structure Queries**:
   - Simple query: "hotels near Disneyland" → single search object
   - Complex query: "hotels near Mong Kok and Yau Ma Tei" → multiple search tasks
   - **Each task needs a separate query object**

5. **Call hotelSearch Tool**:
   - Collect all search query objects into a **List**
   - Serialize the entire list into a single **JSON string**
   - Call `hotelSearch` tool with the JSON string as parameter

      This tool is located at `scripts/hotelSearch.js`. （Path relative to the hotel_recommendation sub-skill）

      **IMPORTANT**: This tool provides the ONLY source of hotel data. ALL recommendations MUST come directly from this tool's actual JSON response. Do NOT create or assume hotels that are not in the response.

      Usage: `node scripts/hotelSearch.js '[{查询对象}]'`

      Example:
      ```bash
      node scripts/hotelSearch.js '[{"subQuery":"新加坡鱼尾狮公园附近的酒店","checkInDate":"2026-03-22","checkOutDate":"2026-03-23","city":"新加坡","country":"新加坡","nearby":"鱼尾狮公园"}]'
      ```

6. **Data Validation**:
   - Parse JSON response
   - Use only actual hotel information from the response
   - If hotelSearch returns no data: explicitly state "hotelSearch未返回符合要求的酒店"
   - **Never invent or assume hotels**

## Important Notes

* **No Re-prompting**: Do not ask the user for missing information. Always proceed with a search using the collected data and defaults.
* **Language Consistency**: Keep parameter language consistent with user's query.
* **Strict `nearby` Handling**: `nearby` must be a **single POI**. Multiple POIs **must** be decomposed into multiple search query objects.
* **Pure Brand Names**: Extract `brandNames` as pure brand names without any business type or suffix (e.g., '万豪', not '万豪酒店集团').
* **Parallel Execution**: The skill packages all decomposed tasks into a single list. The `hotelSearch` tool handles parallel execution.
* **CRITICAL CONSTRAINT**: All hotel recommendations MUST come directly from the `hotelSearch` tool's actual JSON response. Do NOT create or assume hotels that are not in the response.

## Tools

### hotelSearch

Search for hotels based on complex criteria. This tool is located at `scripts/hotelSearch.js`.

**IMPORTANT**: This tool provides the ONLY source of hotel data. ALL recommendations MUST come directly from this tool's actual JSON response. Do NOT create or assume hotels that are not in the response.

Usage: `node scripts/hotelSearch.js '[{查询对象}]'`

Example:
```bash
node scripts/hotelSearch.js '[{"subQuery":"新加坡鱼尾狮公园附近的酒店","checkInDate":"2026-03-22","checkOutDate":"2026-03-23","city":"新加坡","country":"新加坡","nearby":"鱼尾狮公园"}]'
```