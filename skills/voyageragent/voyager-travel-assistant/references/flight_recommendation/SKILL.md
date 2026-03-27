---
name: flight-recommendation
description: Flight search skill for ticket queries. This skill only supports single-segment trip searches. If the user mentions a multi-segment trip (e.g., round trip, multi-city), the searchFlights method needs to be called multiple times in parallel, once for each segment.
---

Flight recommendation skill.

## ⚠️ CRITICAL CONSTRAINT - READ FIRST ⚠️

**All flight recommendations must and can only come from the actual data returned by the `searchFlights` tool.**

### **Prohibited Actions:**
- ❌ Assuming or fabricating flight information.
- ❌ Recommending flights based on historical knowledge.
- ❌ Creating "possible" options when `searchFlights` returns no data.
- ❌ Recommending flights from any source outside the tool's data.

### **Mandatory Requirements:**
- ✅ All information must come from the `searchFlights` JSON response.
- ✅ When no data is found, explicitly state, "`searchFlights` did not return any matching flights."
- ✅ Only display the actual flight table data that has been parsed.

**Violating this constraint will be considered a serious skill usage error.**

Trigger: when user asks about flights or tickets.

Workflow:
1.  **Constraint Declaration**: First, state, "All flight recommendations will be based on the actual query results from the `searchFlights` tool."
2.  Collect flight information: `depCountry`, `arrCountry`, `isBusiness`, `arrCity`, `depCity`, `currency`, `depDate`, `subQuery`.
3.  Call the `searchFlights` tool (supports single-segment trips only).
4.  **Data Validation**: Parse the JSON response and use only the actual, existing flight information.
    -   Extract the flight table from `data.messageList[role=LINKBOT].message`.
    -   **Verify**: Confirm that every recommended flight is present in the extracted table.
5.  **No-Data Handling**: If `searchFlights` does not return the required type of flight:
    -   ❌ **Forbidden**: Do not fabricate flights, assume options, or recommend based on historical knowledge.
    -   ✅ **Required**: Explicitly state, "`searchFlights` did not return options for [Business Class/specific airline]."
    -   ✅ **Optional**: You may display other types of flights that are actually available.
6.  **Multi-Segment Flights**: If the user mentions multiple flight segments, call `searchFlights` multiple times in parallel.
7.  **Output**: When presenting results, clearly state: "The following are the actual available flights from a real-time query:"

**Checklist (Must be reviewed before use):**
- [ ] All flight information comes from the `searchFlights` JSON response.
- [ ] There are no fabricated or assumed flights.
- [ ] When there are no matches, the status of the `searchFlights` result is clearly stated.
- [ ] The output includes a "real-time query results" indicator.

Parameters:
- depCountry: departure country, e.g., China
- arrCountry: arrival country, e.g., China
- isBusiness: whether business class, e.g., false
- arrCity: arrival city, e.g., Urumqi
- depCity: departure city, e.g., Chengdu
- currency: currency type, e.g., HKD (default if not specified by user)
- depDate: departure date, format YYYY-MM-DD
- subQuery: query description extracted from the user's original question for this flight segment.

Important Notes:
- This method only supports single-segment trip searches.
- If the user mentions a multi-segment trip (e.g., round trip, multi-city), the `searchFlights` method needs to be called multiple times in parallel, once for each segment.
- Show top 5 results.
- Sort by price.
- CRITICAL CONSTRAINT: All recommended flights MUST come from the actual data returned by the `searchFlights` tool. Fabricating, assuming, or recommending flights based on historical knowledge is strictly prohibited. If `searchFlights` does not return options for Business Class or a specific airline, you must not recommend hypothetical flights. Recommendations can only be based on the actual available data.

## Tools

### searchFlights

Search for flight tickets. This tool is located at `scripts/searchFlights.sh`.

**IMPORTANT**: This tool provides the ONLY source of flight data. ALL recommendations MUST come directly from this tool's actual JSON response. Do NOT create or assume flights that are not in the response.

Usage: `scripts/searchFlights.sh <depCountry> <arrCountry> <isBusiness> <depCity> <arrCity> <currency> <depDate> <subQuery>`

Example:
```bash
scripts/searchFlights.sh "中国" "中国" "false" "上海" "北京" "CNY" "2026-03-11" "明天北京到上海的机票推荐"
```