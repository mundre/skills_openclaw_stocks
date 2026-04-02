# MCP 工具使用说明

## 服务配置

### 已配置服务

| 服务名称 | URL | 用途 |
|----------|-----|------|
| `jy-financedata-tool` | `https://api.gildata.com/mcp-servers/aidata-assistant-srv-tool?token=<JY_API_KEY>` | 舆情查询、研报查询 |
| `jy-financedata-api` | `https://api.gildata.com/mcp-servers/aidata-assistant-srv-api?token=<JY_API_KEY>` | 行情查询、智能选股 |

## 工具调用方式

所有工具统一使用 `mcporter call` 命令调用，入参均为 `query`：

```bash
mcporter call <服务名>.<工具名> --query "<查询内容>"
```

## 可用工具列表

### jy-financedata-api 服务

#### 1. AShareLiveQuote（A 股实时行情）

**用途：** 获取最新股价、涨跌幅、昨日收盘价等实时行情数据

**调用示例：**
```bash
mcporter call jy-financedata-api.AShareLiveQuote --query "贵州茅台 实时行情"
mcporter call jy-financedata-api.AShareLiveQuote --query "宁德时代 股价"
mcporter call jy-financedata-api.AShareLiveQuote --query "600519 行情"
```

**返回数据：**
- 证券代码、证券简称
- 最新价、涨跌幅、涨跌额
- 昨收价、开盘价、最高价、最低价
- 成交量、成交额

#### 2. StockDailyQuote（股票日行情）

**用途：** 获取历史行情数据，计算昨日市值

**调用示例：**
```bash
mcporter call jy-financedata-api.StockDailyQuote --query "600519 历史行情"
mcporter call jy-financedata-api.StockDailyQuote --query "贵州茅台 近 30 日行情"
```

**返回数据：**
- 交易日期
- 开盘价、收盘价、最高价、最低价
- 成交量、成交额

#### 3. StockQuoteTechIndex（技术指标）

**用途：** 获取技术分析指标

**调用示例：**
```bash
mcporter call jy-financedata-api.StockQuoteTechIndex --query "600519 MACD RSI"
mcporter call jy-financedata-api.StockQuoteTechIndex --query "贵州茅台 技术指标"
```

**返回数据：**
- MACD、KDJ、RSI 等技术指标
- 布林带、均线系统

#### 4. StockMultipleFactorFilter（智能选股）

**用途：** 替代产品筛选

**调用示例：**
```bash
mcporter call jy-financedata-api.StockMultipleFactorFilter --query "白酒行业 低估值 高股息"
mcporter call jy-financedata-api.StockMultipleFactorFilter --query "锂电池 行业龙头"
```

**返回数据：**
- 符合条件的股票列表
- 各项财务指标

### jy-financedata-tool 服务

#### 5. CorporateResearchViewpoints（公司研究观点）

**用途：** 获取近 2 个月券商研报

**调用示例：**
```bash
mcporter call jy-financedata-tool.CorporateResearchViewpoints --query "贵州茅台 研报"
mcporter call jy-financedata-tool.CorporateResearchViewpoints --query "宁德时代 券商观点"
```

**返回数据：**
- 研报标题
- 发布机构
- 发布时间
- 核心观点
- 评级

#### 6. StockNewslist（股票舆情）

**用途：** 获取近 7 天新闻舆情

**调用示例：**
```bash
mcporter call jy-financedata-tool.StockNewslist --query "贵州茅台 近 7 天新闻"
mcporter call jy-financedata-tool.StockNewslist --query "宁德时代 舆情"
```

**返回数据：**
- 新闻标题
- 发布时间
- 来源
- 情感倾向（正面/负面/中性）
- 摘要

## 查询技巧

### 1. 证券名称规范

使用标准证券简称：
- ✅ "贵州茅台"、"宁德时代"、"招商银行"
- ❌ "茅台"、"宁德"、"招行"

或使用证券代码：
- ✅ "600519"、"300750"、"600036"

### 2. 时间范围指定

```bash
# 近 7 天
--query "贵州茅台 近 7 天新闻"

# 近 2 个月
--query "贵州茅台 近 2 个月研报"

# 近 30 日
--query "600519 近 30 日行情"
```

### 3. 多轮查询

复杂需求可分多次查询：

```bash
# 第一次：获取行情
mcporter call jy-financedata-api.AShareLiveQuote --query "贵州茅台 实时行情"

# 第二次：获取舆情
mcporter call jy-financedata-tool.StockNewslist --query "贵州茅台 近 7 天新闻"

# 第三次：获取研报
mcporter call jy-financedata-tool.CorporateResearchViewpoints --query "贵州茅台 研报"
```

## 数据标注规范

在报告中使用数据时，必须标注：

1. **数据来源：** 如"数据来源：恒生聚源 (gildata)"
2. **数据截止：** 如"数据截至 2026-03-31"
3. **发布时间：** 舆情、研报需标注发布时间

示例：
```
贵州茅台当前股价 1680 元，涨跌幅 +1.2%（数据来源：恒生聚源，截至 2026-03-31 15:00）
```

## 常见问题

### Q1: 查询返回空数据

**可能原因：**
- 证券名称不规范
- 数据源暂无相关数据

**解决方案：**
- 使用标准证券简称或证券代码
- 尝试简化查询关键词

### Q2: 查询超时

**可能原因：**
- 网络延迟
- 数据量较大

**解决方案：**
- 重试查询
- 简化查询条件

### Q3: 鉴权失败

**可能原因：**
- JY_API_KEY 无效或过期
- 服务配置错误

**解决方案：**
- 检查 JY_API_KEY 是否正确
- 重新配置 MCP 服务
- 联系恒生聚源确认 KEY 状态
