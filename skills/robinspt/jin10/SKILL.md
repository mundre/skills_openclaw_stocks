---
name: jin10
description: |
  金十数据财经信息查询 skill。查询黄金/白银/原油等行情报价、最新财经快讯、资讯新闻、财经日历数据时使用。
  触发场景：问"黄金价格"、"XAUUSD报价"、"原油快讯"、"财经日历"、"非农什么时候"、"资讯详情"等。
metadata:
  openclaw:
    primaryEnv: JIN10_API_TOKEN
---

# Jin10 金十数据 Skill

> **致谢**：感谢金十数据提供 MCP 服务。本 skill 仅进行使用方式转换，将 MCP 协议调用转换为 Python SDK，无意替代或模仿金十数据官方服务。

## 概述

此 skill 提供金十数据的行情、快讯、资讯和日历查询功能。通过原生 HTTP 调用金十数据的 MCP 协议端点（`https://mcp.jin10.com/mcp`），无需配置 MCP Server。

## 配置

在 `~/.openclaw/.env` 中配置环境变量：
```bash
echo 'JIN10_API_TOKEN="sk-xxxxxxx"' >> ~/.openclaw/.env
```

之后使用时客户端会自动读取：
```python
from jin10 import Jin10Client
client = Jin10Client()
```

## 代码调用方式

### Python 直接调用

```python
from jin10 import Jin10Client

client = Jin10Client(api_token='YOUR_TOKEN')

# 行情查询
result = client.quotes.get_quote('XAUUSD')
print(client.quotes.format_quote(result))

# 快讯搜索
result = client.flash.search('美联储')

# 资讯列表
result = client.news.list()

# 财经日历
result = client.calendar.list()
```

### 按需导入模块

```python
from jin10.quotes import QuotesClient
from jin10.flash import FlashClient
from jin10.news import NewsClient
from jin10.calendar import CalendarClient
```

## 功能模块

### 1. 行情报价 (quotes)

| 方法 | 说明 |
|------|------|
| `get_codes()` | 获取支持的品种代码列表 |
| `get_quote(code)` | 获取单个品种实时行情 |
| `get_quotes([codes])` | 批量获取多个品种行情 |

**常用品种代码**：
- `XAUUSD` - 现货黄金
- `XAGUSD` - 现货白银
- `USOIL` - WTI原油
- `EURUSD` - 欧元/美元
- `USDJPY` - 美元/日元

### 2. 快讯 (flash)

| 方法 | 说明 |
|------|------|
| `list(cursor?)` | 获取最新快讯列表 |
| `search(keyword)` | 按关键词搜索快讯 |
| `list_all(max_pages?)` | 获取所有快讯（自动翻页） |

### 3. 资讯 (news)

| 方法 | 说明 |
|------|------|
| `list(cursor?)` | 获取最新资讯列表 |
| `search(keyword, cursor?)` | 按关键词搜索资讯 |
| `get(id)` | 获取单篇资讯详情 |
| `list_all(max_pages?)` | 获取所有资讯（自动翻页） |

### 4. 财经日历 (calendar)

| 方法 | 说明 |
|------|------|
| `list()` | 获取财经日历 |
| `get_high_importance()` | 获取高重要性事件（星级≥3） |
| `search(keyword)` | 按关键词筛选事件 |

## 输出格式化

每个模块都提供 `format_*` 方法将数据格式化为可读字符串：

```python
from jin10 import QuotesClient, FlashClient, NewsClient, CalendarClient

# 格式化报价
QuotesClient.format_quote(quote_data)

# 格式化快讯列表
FlashClient.format_flash_list(flash_data)

# 格式化资讯列表
NewsClient.format_news_list(news_data)

# 格式化资讯详情
NewsClient.format_news_detail(news_detail)

# 格式化日历
CalendarClient.format_calendar(calendar_data)
CalendarClient.format_high_importance(events)
```

## 使用示例

### 对话场景

**用户**: 黄金现在多少钱？

**助手**: 使用 `quotes.get_quote('XAUUSD')` 查询黄金报价，格式化后展示给用户。

**用户**: 有什么最新的财经快讯？

**助手**: 使用 `flash.list()` 获取最新快讯，格式化展示。

**用户**: 本周有什么重要数据发布？

**助手**: 使用 `calendar.get_high_importance()` 获取高重要性事件，格式化展示。

## 数据来源

金十数据 MCP 协议端点: `https://mcp.jin10.com/mcp`

该 skill 直接调用 MCP 协议端点，不依赖 Claude Code 的 MCP Server 配置，减少 token 开销。
