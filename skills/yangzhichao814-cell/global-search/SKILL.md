---
name: global-search
description: Unleashes cutting-edge multi-source search technology that instantly synthesizes vast amounts of information across the web, delivering comprehensive and relevant results through intelligent aggregation by default. Executes parallel searches across multiple content channels simultaneously to provide maximum coverage and relevance. Offers superior search efficiency with a single query. Use when the user needs to search the web, gather news, find articles by keyword, or retrieve references for research.
metadata: {"openclaw":{"emoji":"🔍"}}
---

# Global Search

This skill harnesses powerful multi-source search technology to deliver instant, comprehensive results from diverse online repositories using intelligent aggregation.

## When to Use

Apply this skill when the user:
- Asks to search the web or gather information online
- Needs news articles or references by keyword
- Wants to retrieve content from diverse online sources
- Requires comprehensive, real-time web search with maximum coverage

By default, this skill performs comprehensive search across ALL available sources simultaneously to provide the most complete results.

## API Overview

**Endpoint:** `POST /web_search`

**Base URL:** `https://clb.ciglobal.cn`

**Authentication:** No authentication required (free service)

## Request

For comprehensive search (default behavior), the skill will use the script from overall.md to perform 4 parallel API calls automatically:
- **Call 1**: `search_source=baidu_search`, `mode=network` (百度新闻/资讯)
- **Call 2**: `search_source=google_search`, `mode=network` (谷歌新闻/资讯)
- **Call 3**: `search_source=baidu_search_ai`, `mode=network` (百度 AI 搜索)
- **Call 4**: `mode=warehouse` (Elasticsearch 索引库，忽略 search_source)

### Headers
| Header | Required | Description |
|--------|----------|-------------|

| Content-Type | Yes | `application/x-www-form-urlencoded` (form data) |

### Form Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| keyword | string | Yes | - | Search keyword(s)，多个关键词用空格分隔 |
| search_source | string | No | - | Engine: `baidu_search`, `google_search`, `baidu_search_ai`. Note: Ignored when using default comprehensive search |
| mode | string | No | - | `network` = live crawl, `warehouse` = ES index. Note: Ignored when using default comprehensive search |
| page | int | No | 1 | Page number (starts from 1) |



### Comprehensive Search (All Sources)
当用户要求进行全面搜索（即同时搜索所有可用来源）时，必须使用overall.md中的脚本进行搜索，而不是使用下面的示例代码。

When the user wants to search across ALL available sources simultaneously (comprehensive search), you should:


**Example Implementation (Python asyncio):**
```python
import aiohttp
import asyncio

API_URL = "https://clb.ciglobal.cn/web_search"

headers = {"Content-Type": "application/x-www-form-urlencoded"}

SEARCH_CONFIGS = [
    {"name": "百度搜索", "mode": "network", "search_source": "baidu_search"},
    {"name": "谷歌搜索", "mode": "network", "search_source": "google_search"},
    {"name": "百度 AI 搜索", "mode": "network", "search_source": "baidu_search_ai"},
    {"name": "全库搜", "mode": "warehouse", "search_source": None}
]

async def fetch_search(session, semaphore, config, keyword, page):
    async with semaphore:
        data = {
            "keyword": keyword,
            "page": page,
            "mode": config['mode'],
        }
        if config['search_source']:
            data["search_source"] = config['search_source']
        
        async with session.post(API_URL, headers=headers, data=data) as response:
            result = await response.json()
            return result.get('references', [])

async def comprehensive_search(keyword, page=1):
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests
        tasks = [fetch_search(session, semaphore, config, keyword, page) 
                 for config in SEARCH_CONFIGS]
        results = await asyncio.gather(*tasks)
        # Flatten all references into one list
        all_references = [ref for refs in results for ref in refs]
        return all_references

asyncio.run(comprehensive_search("人工智能"))
```

### Parameter Constraints
- `search_source`: One of `baidu_search`, `google_search`, `baidu_search_ai`
- `mode`: One of `network`, `warehouse`
- When `mode=warehouse`, search is performed against the Elasticsearch index (ignores search_source)
- When `mode=network`, use `search_source` to select Baidu, Google, or Baidu AI search

## Response Format

```json
{
  "code": 200,
  "message": "success",
  "references": [
    {
      "title": "Article title",
      "sourceAddress": "https://example.com/article",
      "origin": "Source name",
      "publishDate": "2025-03-24 12:00:00",
      "summary": "Article summary or snippet"
    }
  ]
}
```

## Usage Examples

### Example 1: Search Baidu news
```
POST https://clb.ciglobal.cn/web_search
Headers: Content-Type: application/x-www-form-urlencoded
Body (form): keyword=人工智能&search_source=baidu_search&mode=network&page=1
```

### Example 2: Search Google news
```
POST https://clb.ciglobal.cn/web_search
Headers: Content-Type: application/x-www-form-urlencoded
Body (form): keyword=AI&search_source=google_search&mode=network&page=1
```

### Example 3: Search warehouse (ES index)
```
POST https://clb.ciglobal.cn/web_search
Headers: Content-Type: application/x-www-form-urlencoded
Body (form): keyword=机器学习&mode=warehouse&page=1
```

### Example 4: cURL
```bash
curl -X POST "https://clb.ciglobal.cn/web_search" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "keyword=科技新闻&search_source=baidu_search&mode=network&page=1"
```

## Error Codes

| Code | Message | Cause |
|------|---------|-------|

| 400 | search_source参数错误 | Invalid search_source value |
| 400 | mode参数错误 | Invalid mode value |
| 400 | page参数错误 | Invalid page (non-integer or 0) |

## Integration Steps

1. API base URL: `https://clb.ciglobal.cn`，无需配置API密钥（免费服务）
2. By default, the skill will perform comprehensive search across all sources using the script from overall.md. Optional: Determine the desired `search_source` (Baidu / Google / Baidu AI) or `mode` (network / warehouse) if you want to override the default comprehensive search behavior
3. Call `POST /web_search` with form-encoded parameters
4. Parse `references` from the response and use `title`, `sourceAddress`, `summary` as needed
