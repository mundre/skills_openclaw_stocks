---
name: sorftime
description: Sorftime 多平台电商数据分析API支持，覆盖亚马逊、Shopee、沃尔玛等平台的类目、产品、关键词、监控等功能
trigger:
  keywords: ["sorftime", "亚马逊数据", "shopee数据", "沃尔玛数据", "电商数据分析"]
  prefix: []
  regex: []
enabled: true
---

# Sorftime API Skills

Sorftime 提供多平台电商数据分析 API，目前已按平台和功能模块拆分为独立的 Skill 文件。

Sorftime provides multi-platform e-commerce data analysis APIs, currently split into independent Skill files by platform and functional module.

## Amazon 亚马逊平台 Skills / Amazon Platform Skills

### 1. 类目市场分析 (amazon-category)
- **路径 / Path**: `resources/amazon-category.md`
- **功能 / Function**: 类目树、Best Sellers、热销产品、市场趋势分析 | Category tree, Best Sellers, hot products, market trend analysis
- **接口数量 / API Count**: 4个核心接口 | 4 core APIs
- **适用场景 / Use Cases**: 类目选择和评估、市场容量分析、竞争程度评估、历史趋势追踪 | Category selection and evaluation, market capacity analysis, competition assessment, historical trend tracking
- **关键接口 / Key APIs**:
  - CategoryTree: 获取类目树结构 | Get category tree structure
  - CategoryRequest: 查询Best Seller产品 | Query Best Seller products
  - CategoryProducts: 查询全部热销产品 | Query all hot-selling products
  - CategoryTrend: 查询40种市场趋势指标 | Query 40 market trend metrics

### 2. 产品数据查询 (amazon-product)
- **路径 / Path**: `resources/amazon-product.md`
- **功能 / Function**: 产品详情、搜索、趋势、评论、子体数据等 | Product details, search, trends, reviews, variation data, etc.
- **接口数量 / API Count**: 13个接口 | 13 APIs
- **适用场景 / Use Cases**: 竞品分析、产品筛选、评论分析、子体销量追踪、图搜相似产品 | Competitive analysis, product filtering, review analysis, variation sales tracking, image-based similar product search
- **关键接口 / Key APIs**:
  - ProductRequest: 产品详情查询（支持批量，最多10个ASIN）| Product detail query (supports batch, up to 10 ASINs)
  - ProductQuery: 多维度产品搜索（16种查询类型）| Multi-dimensional product search (16 query types)
  - ProductReviewsQuery: 产品评论查询 | Product review query
  - AsinSalesVolume: 官方子体销量数据 | Official variation sales volume data
  - SimilarProductRealtimeRequest: 图搜相似产品 | Image-based similar product search

### 3. 关键词研究 (amazon-keyword)
- **路径 / Path**: `resources/amazon-keyword.md`
- **功能 / Function**: 关键词查询、拓展、反查、排名追踪、词库管理 | Keyword query, expansion, reverse lookup, ranking tracking, word library management
- **接口数量 / API Count**: 12个接口 | 12 APIs
- **适用场景 / Use Cases**: 关键词挖掘、ASIN反查关键词、关键词排名追踪、关键词词库管理 | Keyword mining, ASIN reverse keyword lookup, keyword ranking tracking, keyword library management
- **关键接口 / Key APIs**:
  - KeywordRequest: 关键词详情 | Keyword details
  - KeywordExtends: 延伸关键词 | Extended keywords
  - ASINRequestKeywordv2: ASIN反查关键词 | ASIN reverse keyword lookup
  - ASINKeywordRanking: ASIN关键词排名趋势 | ASIN keyword ranking trends
  - FavoriteKeyword: 关键词收藏管理 | Keyword favorites management

### 4. 数据监控 (amazon-monitoring)
- **路径 / Path**: `resources/amazon-monitoring.md`
- **功能 / Function**: 关键词排名监控、榜单监控、跟卖&库存监控 | Keyword ranking monitoring, leaderboard monitoring, hijacker & inventory monitoring
- **接口数量 / API Count**: 14个接口 | 14 APIs
- **适用场景 / Use Cases**: 关键词排名实时监控、Best Seller榜单追踪、跟卖预警、库存监控 | Real-time keyword ranking monitoring, Best Seller leaderboard tracking, hijacker alerts, inventory monitoring
- **注意 / Note**: 监控类接口消耗积分而非request | Monitoring APIs consume points rather than requests
- **关键接口 / Key APIs**:
  - KeywordBatchSubscription: 关键词监控注册 | Keyword monitoring registration
  - BestSellerListSubscription: 榜单监控注册 | Leaderboard monitoring registration
  - ProductSellerSubscription: 跟卖&库存监控 | Hijacker & inventory monitoring
  - KeywordBatchScheduleDetail: 提取监控数据 | Extract monitoring data

### 5. 智能分析助手 (amazon-sorftimeAgent)
- **路径 / Path**: `resources/amazon-sorftimeAgent.md`
- **功能 / Function**: 选品建议、市场洞察、竞品分析、策略优化 | Product selection suggestions, market insights, competitive analysis, strategy optimization
- **适用场景 / Use Cases**: 新产品选品咨询、市场机会发现、竞品深度分析、关键词策略优化、定价策略建议 | New product selection consultation, market opportunity discovery, in-depth competitive analysis, keyword strategy optimization, pricing strategy suggestions

---

## Shopee 虾皮平台 Skill / Shopee Platform Skill

### Shopee API (shopee-api)
- **路径 / Path**: `resources/shopee-api.md`
- **支持站点 / Supported Sites**: 越南、印尼、新加坡、泰国、马来西亚、中国台湾、菲律宾、巴西（8个站点）| Vietnam, Indonesia, Singapore, Thailand, Malaysia, Taiwan, Philippines, Brazil (8 sites)
- **Domain范围 / Domain Range**: 201-208
- **功能 / Function**: 类目、产品、店铺数据查询 | Category, product, and shop data query
- **关键接口 / Key APIs**: CategoryTree、CategoryRequest、ProductRequest、ProductTrend、ShopRequest

---

## Walmart 沃尔玛平台 Skill / Walmart Platform Skill

### Walmart API (walmart-api)
- **路径 / Path**: `resources/walmart-api.md`
- **支持站点 / Supported Sites**: 美国站 | US Site
- **Domain范围 / Domain Range**: 21
- **功能 / Function**: 类目、产品、关键词数据查询 | Category, product, and keyword data query
- **关键接口 / Key APIs**: CategoryTree、CategoryRequest、ProductRequest、ProductTrendRequest、KeywordQuery

---

## 快速开始 / Quick Start

### 1. 安装sorftime-cli / Install sorftime-cli
```bash
npm install -g sorftime-cli
```

### 2. 配置账户 / Configure Account
```bash
# 添加账户 / Add account
sorftime add <profile-name> <your-account-sk>

# 切换到默认账户 / Switch to default account
sorftime use <profile-name>
```

### 3. 选择对应的 Skill / Select the Appropriate Skill
根据你要分析的平台和功能，查看对应的 Skill 文档获取详细的 API 使用说明。
Choose the corresponding Skill documentation based on the platform and function you want to analyze for detailed API usage instructions.

---

## Amazon 支持站点 / Amazon Supported Sites

| domain值 | 站点代码 | 站点名称 | 所属区域 |
|---------|---------|---------|---------|
| 1 | us | 美国站 | 北美 |
| 6 | ca | 加拿大站 | 北美 |
| 10 | mx | 墨西哥站 | 北美 |
| 13 | br | 巴西站 | 南美 |
| 2 | gb | 英国站 | 欧洲 |
| 3 | de | 德国站 | 欧洲 |
| 4 | fr | 法国站 | 欧洲 |
| 8 | es | 西班牙站 | 欧洲 |
| 9 | it | 意大利站 | 欧洲 |
| 11 | ae | 阿联酋站 | 中东 |
| 14 | sa | 沙特站 | 中东 |
| 7 | jp | 日本站 | 亚洲 |
| 5 | in | 印度站 | 亚洲 |
| 12 | au | 澳大利亚站 | 大洋洲 |

---

## 通用说明 / General Notes

### 返回结构 / Response Structure
所有接口返回统一结构：
```json
{
  "Code": 0,
  "Message": null,
  "Data": {},
  "RequestLeft": 9999,
  "RequestConsumed": 1,
  "RequestCount": 1
}
```

### 常见错误 / Common Errors
| 错误码 | 说明 / Description | 解决方案 / Solution |
|--------|------|----------|
| 0 | 成功 / Success | - |
| 4 | 积分余额不足 / Insufficient points | 充值或等待下月重置 / Recharge or wait for monthly reset |
| 97 | ASIN不存在 / ASIN not found | 检查ASIN是否正确 / Verify ASIN is correct |
| 98 | 采集失败 / Collection failed | 稍后重试 / Retry later |
| 99 | 正在实时抓取 / Real-time crawling in progress | 等待5分钟后重试 / Wait 5 minutes and retry |
| 401 | 认证失败 / Authentication failed | 检查Account-SK是否有效 / Verify Account-SK is valid |
| 403 | 权限不足 / Insufficient permissions | 检查套餐权限或请求次数 / Check plan permissions or request count |
| 429 | 请求频率超限 / Rate limit exceeded | 降低请求速度 / Reduce request rate |
| 500 | 服务器内部错误 / Internal server error | 稍后重试 / Retry later |

---

## Skill 组织结构 / Skill Directory Structure

```
skill/
└── sorftime/
    ├── SKILL.md                          # 本文件：总索引 / This file: master index
    └── resources/
        ├── amazon-category.md            # 亚马逊类目数据 / Amazon category data
        ├── amazon-product.md             # 亚马逊产品数据查询 / Amazon product data query
        ├── amazon-keyword.md             # 亚马逊关键词研究 / Amazon keyword research
        ├── amazon-monitoring.md          # 亚马逊数据监控 / Amazon data monitoring
        ├── amazon-sorftimeAgent.md       # Sorftime智能分析助手 / Sorftime AI analysis assistant
        ├── shopee-api.md                 # Shopee平台API / Shopee platform API
        └── walmart-api.md                # Walmart平台API / Walmart platform API
```

---

## 使用建议 / Usage Guide

### 亚马逊相关数据获取 / Amazon Data Access
1. 从 `resources/amazon-category.md` 开始学习类目分析 / Start with `resources/amazon-category.md` to learn category analysis
2. 逐步掌握 `resources/amazon-product.md` 的产品查询 / Progress to product queries in `resources/amazon-product.md`
3. 深入学习 `resources/amazon-keyword.md` 的关键词研究 / Dive deeper into keyword research in `resources/amazon-keyword.md`
4. 根据需要设置 `resources/amazon-monitoring.md` 的监控任务 / Set up monitoring tasks in `resources/amazon-monitoring.md` as needed
5. 根据需求通过 `resources/amazon-sorftimeAgent.md` 创建智能分析任务 / Create intelligent analysis tasks via `resources/amazon-sorftimeAgent.md` as needed

### Shopee相关数据获取 / Shopee Data Access
从 `resources/shopee-api.md` 学习提供的数据接口 / Learn the available data APIs from `resources/shopee-api.md`

### 沃尔玛相关数据获取 / Walmart Data Access
从 `resources/walmart-api.md` 学习提供的数据接口 / Learn the available data APIs from `resources/walmart-api.md`
