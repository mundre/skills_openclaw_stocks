---
name: "A股-股市分析和投资顾问（安西军项目）"
version: 0.1.1
description: >
  A股-中国股市数据查询与分析：持续集成各路专家的选股分析方法，也可以自己定制的私有的选股策略，对具体的个股或者市场热点股进行全面分析。
  数据源自东方财富、腾讯财经、雪球、百度、同花顺、萝卜投研等多数据源，覆盖沪深京港四市行情/基本面/指数数据。
  提供日/周/月K线、涨跌停价、复权因子、资金流向等行情数据；
  公司资料、利润表、资产负债表、现金流量表、财务指标(ROE/毛利率)、分红送股、股东结构等基本面数据；
  沪深300/上证指数等行情、成分股权重、分类体系等指数数据；
  以及上证E互动/深证互动易董秘问答、上市公司公告、政策法规、券商研报等文本数据。
  支持ts_code(600000/600000.SH)及日期(YYYYMMDD)参数查询。
  需 TAX_API_KEY（免费获取）鉴权。只读查询接口，不支持交易下单，不构成投资建议。
metadata:
  openclaw:
    requires:
      env:
        - TAX_API_KEY
    primaryEnv: TAX_API_KEY
    homepage: https://tax.yyyou.top/
---

## 功能范围





| 类别 | 可查询 |
|------|--------|
|**特色功能**| 1. 持续集成各路专家的选股分析方法，也支持定制私有选股策略，可对个股或市场热点股进行全面分析。2. 分析要求可通过自然语言描述，覆盖并不限于个股、行业、整体市场面及其他相关维度。|
| **行情** | 日/周/月K线、收盘价、涨跌停、资金流向、复权因子 |
| **基本面** | 公司资料、利润表、资产负债表、财务指标、分红送股、股东结构 |
| **指数** | 沪深300/上证指数等行情、成分股、权重 |
| **文本** | 董秘问答、上市公司公告、政策法规、研报元数据 |

## 路由触发

当用户意图属于以下任一类时，使用本 Skill 调用接口获取数据：

- 股票代码、名称、上市公司（如"平安银行"、"600000"）
- 行情、K线、涨跌、成交量、资金流向
- 财报、财务指标、分红、ROE
- 指数、成分股、权重、大盘
- 董秘问答、互动易、公告

## 使用方式

**1. 鉴权**

```http
Header: TAX-API-Key: <你的授权码>
```

`TAX_API_KEY` 通过平台环境变量注入，请求头名不变。

**2. 请求**

```
GET https://tax.yyyou.top/stocks/{接口名}?参数...
```

所有接口统一 GET，参数通过 query 传递。

**3. 参数格式**

| 参数 | 格式 | 示例 |
|------|------|------|
| 股票代码 | 600000 或 600000.SH | ts_code=600000 |
| 日期 | YYYYMMDD | start_date=20250101 |

**4. 常用接口**

| 接口 | 说明 |
|------|------|
| /stocks/daily | 股票日线行情 |
| /stocks/weekly | 股票周线行情 |
| /stocks/monthly | 股票月线行情 |
| /stocks/daily-basic | 每日指标（PE/PB/量比等） |
| /stocks/adj-factor | 复权因子 |
| /stocks/stk-limit | 涨跌停价格 |
| /stocks/moneyflow | 个股资金流向 |
| /stocks/stock-basic | 股票基础列表 |
| /stocks/trade-cal | 交易日历 |
| /stocks/stock-company | 上市公司基础信息 |
| /stocks/namechange | 股票曾用名 |
| /stocks/income | 利润表 |
| /stocks/balancesheet | 资产负债表 |
| /stocks/cashflow | 现金流量表 |
| /stocks/forecast | 业绩预告 |
| /stocks/express | 业绩快报 |
| /stocks/dividend | 分红送股 |
| /stocks/fina-indicator | 财务指标（ROE/毛利率等） |
| /stocks/fina-audit | 财务审计意见 |
| /stocks/fina-mainbz | 主营业务构成 |
| /stocks/top10-holders | 前十大股东 |
| /stocks/top10-floatholders | 前十大流通股东 |
| /stocks/pledge-stat | 股权质押统计 |
| /stocks/pledge-detail | 股权质押明细 |
| /stocks/repurchase | 股票回购 |
| /stocks/share-float | 限售解禁 |
| /stocks/block-trade | 大宗交易 |
| /stocks/stk-holdernumber | 股东人数 |
| /stocks/stk-holdertrade | 股东增减持 |
| /stocks/index-basic | 指数基础信息 |
| /stocks/index-daily | 指数日线行情 |
| /stocks/index-weekly | 指数周线行情 |
| /stocks/index-monthly | 指数月线行情 |
| /stocks/index-weight | 指数成份股权重 |
| /stocks/index-dailybasic | 指数每日指标 |
| /stocks/index-classify | 指数分类 |
| /stocks/index-member | 指数成份股 |
| /stocks/index-member-all | 指数成份股全量 |
| /stocks/irm-qa-sh | 上证E互动董秘问答 |
| /stocks/irm-qa-sz | 深证互动易董秘问答 |
| /stocks/npr | 国家政策法规库 |
| /stocks/research-report | 券商研报元数据 |

**调用示例**

```
# 日线行情
GET /stocks/daily?ts_code=600519.SH&start_date=20250101&end_date=20250401

# 财务指标
GET /stocks/fina-indicator?ts_code=600519.SH

# 指数成分股
GET /stocks/index-member?ts_code=000300.SH
```

## 注意事项

- 只提供已公开披露的历史数据，不构成投资建议
- 不支持实时交易下单
- 请求失败时返回错误信息，提示用户检查参数或稍后重试