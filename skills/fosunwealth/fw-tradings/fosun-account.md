---
name: fosun-account
description: 复星集团旗下复星财富（Fosun Wealth，星财富 APP）账户查询工具集，支持买卖信息查询（每手股数/可买可卖数量/购买力）、资金持仓查询（资金汇总/持仓列表/账户列表）和资金流水查询（按日期/类型筛选进出明细）。
requires:
  env:
    - FSOPENAPI_API_KEY
    - FSOPENAPI_CLIENT_PRIVATE_KEY
    - FSOPENAPI_SERVER_PUBLIC_KEY
  bins:
    - python3
---

# 复星账户查询工具集

> **⚠️ 数据准确性最高优先级规则：**
> 本 skill 返回的所有数值（持仓数量、可用数量、资金余额、购买力、lotSize、成本价、流水金额等）**必须从脚本输出中原样逐字引用**，严禁凭记忆复述或做任何近似处理。
> - 脚本输出 `quantity=1000`，就必须说 **1000 股**，不能说成 100 股或 10000 股。
> - 脚本输出 `cashPurchasePower=125000.50`，就必须说 **125000.50**，不能说"约 12 万"。
> - 展示查询结果时**必须使用表格格式**，逐字段列出名称和数值，关键数值加粗，单位紧跟数字。
> - 如对某个数值不确定，必须重新执行脚本获取，禁止猜测。

通过命令行脚本查询买卖信息、资金/持仓和资金流水。

> **通用环境约束、市场定义和订单类型请参考 `fosun-trading` skill。**
> 所有脚本位于 `fosun-trading` skill 的 `code/` 目录下（即 `fw-tradings/fosun-trading/code/`）。

运行前先 `cd` 到脚本目录：

```bash
cd <fosun-trading skill 目录>/code
$FOSUN_PYTHON <脚本名>.py <子命令> [参数]
```

---

## 1. 查询买卖信息 — query_bidask.py

> 查询某只股票的**每手股数（lotSize）**、最大可买/可卖数量、购买力等信息。
> 对应 API 接口：`POST /api/v1/trade/BidAskInfo`

### 查询每手股数

```bash
$FOSUN_PYTHON query_bidask.py --stock 00700 --direction buy --order-type limit
$FOSUN_PYTHON query_bidask.py --stock 00700 --lot-size-only           # 仅输出 lotSize 数值
$FOSUN_PYTHON query_bidask.py --stock AAPL --market us --lot-size-only
$FOSUN_PYTHON query_bidask.py --stock 600519 --market sh --lot-size-only
```

### 查询可买/可卖数量

```bash
$FOSUN_PYTHON query_bidask.py --stock 00700 --price 350.000           # 指定价格查更精确的可买数量
$FOSUN_PYTHON query_bidask.py --stock 00700 --direction sell           # 查可卖数量
$FOSUN_PYTHON query_bidask.py --stock AAPL --market us                 # 美股
$FOSUN_PYTHON query_bidask.py --stock 600519 --market sh               # A 股（沪）
```

### 指定订单类型查询

```bash
$FOSUN_PYTHON query_bidask.py --stock 00700 --order-type market           # 市价单
$FOSUN_PYTHON query_bidask.py --stock 00700 --order-type enhanced_limit   # 增强限价单
$FOSUN_PYTHON query_bidask.py --stock 00700 --order-type special_limit    # 特别限价单
```

### 全部参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--stock` | 是 | 股票代码（不含市场前缀） |
| `--market` | 否 | `hk`（默认）/ `us` / `sh` / `sz` |
| `--direction` | 否 | `buy`（默认）/ `sell` |
| `--order-type` | 建议显式传入 | 至少显式指定为 `limit(3)` / `enhanced_limit(4)` / `special_limit(5)` / `market(9)` / `auction_limit(1)` / `auction(2)` / `stop_loss_limit(31)` / `take_profit_limit(32)` / `trailing_stop(33)` / `take_profit_stop_loss(35)` |
| `--price` | 否 | 委托价格（传入可得到更精确的可买数量） |
| `--quantity` | 否 | 委托数量 |
| `--lot-size-only` | 否 | 仅输出每手股数数值 |

### 响应关键字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `maxPurchasePower` | string | 最大购买力（含融资） |
| `cashPurchasePower` | string | 现金购买力 |
| `availableWithdrawBalance` | string | 总账户可用现金 |
| `singleWithdrawBalance` | string | 当前币种可提现金 |
| `currency` | string | 币种（HKD/USD/CNH） |
| `lotSize` | int | **每手股数**（如港股腾讯 = 100，即一手 100 股） |
| `cashQuantityBuy` | int | 现金可买数量 |
| `maxQuantityBuy` | int | 最大可买数量 |
| `baseQuantitySell` | int | 本币种可卖数量 |
| `maxQuantitySell` | int | 持仓可卖数量（含关联币种） |

> **⚠️ 每手股数（lotSize）说明**
>
> 不同股票的每手股数不同，**必须通过此接口动态查询**，不可硬编码。
>
> | 市场 | 每手规则 | 示例 |
> |------|----------|------|
> | 港股 | 每只股票不同，由交易所定义 | 腾讯(00700) = 100 股/手 |
> | 美股 | 通常 1 股起买，无整手限制 | AAPL lotSize = 1 |
> | A 股（中华通） | 通常 100 股/手 | 贵州茅台(600519) = 100 股/手 |
>
> 港股下单时 quantity 必须是 lotSize 的整数倍，否则会被拒单。

---

## 2. 查询资金/持仓 — query_funds.py

### 资金汇总（可用资金/冻结资金/总资产）

```bash
$FOSUN_PYTHON query_funds.py summary
$FOSUN_PYTHON query_funds.py summary --currency HKD
```

关键字段：

| 字段 | 说明 |
|------|------|
| `summary.cashPurchasingPower` | 现金购买力（可用资金） |
| `summary.frozenBalance` | 冻结资金 |
| `summary.ledgerBalance` | 账面余额（总资产） |
| `summary.maxPurchasingPower` | 最大购买力 |
| `breakdown[]` | 分币种明细（HKD/USD/CNH） |

### 持仓列表（持仓数量/当前市值/成本价）

```bash
$FOSUN_PYTHON query_funds.py holdings
$FOSUN_PYTHON query_funds.py holdings --symbols hk00700 --currencies HKD USD
```

关键字段：

| 字段 | 说明 |
|------|------|
| `list[].stockCode` | 股票代码 |
| `list[].quantity` | 持仓数量 |
| `list[].quantityAvail` | 可用数量 |
| `list[].price` | 当前市价 |
| `list[].avgCost` | 平均成本 |
| `list[].dilutedCost` | 摊薄成本 |

> **⚠️ 成本字段说明：持仓有两种成本，务必区分，没有明确说明哪个成本就必须都告诉用户且区分**
>
> | 字段 | 含义 | 计算方式 |
> |------|------|----------|
> | `avgCost` | **平均成本** | 所有买入交易的加权平均价格，不因卖出而变化 |
> | `dilutedCost` | **摊薄成本** | 在平均成本基础上，将已实现盈亏摊薄到剩余持仓中 |
>
> - 如果只买入未卖出过，两者相同。
> - 一旦部分卖出且产生盈利，`dilutedCost` 会低于 `avgCost`（盈利被摊薄到剩余持仓）；反之亏损卖出时 `dilutedCost` 会高于 `avgCost`。
> - **查看买入均价**用 `avgCost`；**评估真实持仓成本（含已实现盈亏）**用 `dilutedCost`。

### 账户列表

```bash
$FOSUN_PYTHON query_funds.py accounts
```

---

## 3. 查询资金流水 — query_cashflows.py

> 查询账户的资金进出明细（交易结算、出入金、利息、费用等）。
> 对应 API 接口：`POST /api/v1/trade/CashFlows`

### 查询全部流水

```bash
$FOSUN_PYTHON query_cashflows.py
```

### 按日期范围查询

```bash
$FOSUN_PYTHON query_cashflows.py --from-date 2025-01-01 --to-date 2025-01-31
```

### 查询指定日期

```bash
$FOSUN_PYTHON query_cashflows.py --date 2025-03-15
```

### 按类型筛选

```bash
$FOSUN_PYTHON query_cashflows.py --flow-type 1
$FOSUN_PYTHON query_cashflows.py --business-type 1 2
```

### 全部参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--from-date` | 否 | 开始日期 yyyy-mm-dd |
| `--to-date` | 否 | 结束日期 yyyy-mm-dd |
| `--date` | 否 | 指定日期 yyyy-mm-dd（查询单日流水） |
| `--flow-type` | 否 | 流水类型 |
| `--business-type` | 否 | 业务类型（可多个） |

### 输出参数说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | integer | 状态码，`0` 表示成功 |
| `message` | string | 状态消息 |
| `data.count` | integer | 当前返回记录数 |
| `data.list` | array[object] | 资金流水列表 |
| `data.start` | integer | 起始偏移量 |
| `data.total` | integer | 总记录数 |

#### `data.list[]` 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `data.list[].amount` | number | 金额 |
| `data.list[].businessType` | integer | 业务类型 |
| `data.list[].createdAt` | string | 创建时间 |
| `data.list[].currency` | string | 币种 |
| `data.list[].description` | string | 描述 |
| `data.list[].direction` | integer | 资金方向 |
| `data.list[].exchangeCode` | string | 交易所代码 |
| `data.list[].flowId` | string | 流水 ID |
| `data.list[].flowType` | integer | 流水类型 |
| `data.list[].productCode` | string | 产品代码 |
| `data.list[].remark` | string | 备注 |
| `data.list[].tradeDate` | string | 交易日期 |
