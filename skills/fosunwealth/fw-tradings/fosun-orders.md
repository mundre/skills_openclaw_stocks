---
name: fosun-orders
description: 复星集团旗下复星财富（Fosun Wealth，星财富 APP）下单与订单查询工具集，支持下单（普通单/条件单/跟踪止损/止盈止损/期权单）和订单查询，覆盖港/美/A 股市场；撤单和改单见 fosun-order-modify skill。
requires:
  env:
    - FSOPENAPI_API_KEY
    - FSOPENAPI_CLIENT_PRIVATE_KEY
    - FSOPENAPI_SERVER_PUBLIC_KEY
  bins:
    - python3
---

# 复星下单与订单查询工具集

> **⚠️ 数据准确性最高优先级规则：**
> 本 skill 返回的所有数值（订单数量 quantity、委托价格 price、成交数量 filledQuantity、成交价格 filledPrice、lotSize、可买可卖数量等）**必须从脚本输出中原样逐字引用**，严禁凭记忆复述或做任何近似处理。
> - 脚本输出 `quantity=1000`，就必须说 **1000 股**，不能说成 100 股或 10000 股。
> - 脚本输出 `filledPrice=350.200`，就必须说成交价 **350.200**，不能说"约 350"。
> - 展示订单信息时**必须使用表格格式**，逐字段列出，关键数值加粗，单位紧跟数字。
> - 如对某个数值不确定，必须重新执行脚本获取，禁止猜测。

通过命令行脚本完成下单和订单查询操作。撤单和改单请参考 `fosun-order-modify` skill。

> **通用环境约束、市场定义、订单类型和交易限制请参考 `fosun-trading` skill。**
> 所有脚本位于 `fosun-trading` skill 的 `code/` 目录下（即 `fw-tradings/fosun-trading/code/`）。

运行前先 `cd` 到脚本目录：

```bash
cd <fosun-trading skill 目录>/code
$FOSUN_PYTHON <脚本名>.py <子命令> [参数]
```

---

## 1. 下单 — place_order.py

> 支持普通单、条件单、跟踪止损单、止盈止损组合单和期权单，覆盖港/美/A 股市场。

> **⚠️ 重要：下单前必须与用户二次确认！**
> 当已解析出明确的订单参数（股票代码、方向、数量、价格等）后，**禁止直接执行下单命令**。
> 必须先将完整的订单参数汇总展示给用户（适合用户阅读的格式），等待用户明确确认后才能执行。
> 这是一项涉及真实资金的操作，任何情况下都不得跳过确认步骤。

> **⚠️ 重要：用户说"买/卖 N 手"时，必须先查询每手股数再换算成股数！**
> 当用户的指令中使用"手"作为数量单位（如"帮我买 1 手腾讯"、"卖 3 手 00700"），**必须先调用 `query_bidask.py --lot-size-only` 查询该股票的每手股数（lotSize）**，再将手数换算为股数（quantity = 手数 × lotSize），最终以股数下单。
>
> ```bash
> # 示例：用户说"买 2 手腾讯 (00700)"
> # 第一步：查询每手股数
> $FOSUN_PYTHON query_bidask.py --stock 00700 --lot-size-only
> # 假设输出 100，即一手 = 100 股
> # 第二步：计算 quantity = 2 × 100 = 200
> # 第三步：下单时 --quantity 200
> ```
> **禁止假设每手股数**，不同股票的 lotSize 不同，必须动态查询。

> **⚠️ 重要：最大可买/可卖数量必须通过接口查询，禁止自行计算！**
> 下单前需要确认可买/可卖数量时，**必须调用 `query_bidask.py` 接口查询**，不得根据资金余额、股价、持仓数量等信息自行推算。
> 接口返回的 `maxQuantityBuy`（最大可买）和 `maxQuantitySell`（最大可卖）已综合考虑购买力、保证金、风控规则等因素，手动计算无法覆盖这些逻辑，极易导致下单失败或数量错误。
>
> ```bash
> # 查询最大可买数量（指定价格更精确）
> $FOSUN_PYTHON query_bidask.py --stock 00700 --price 350.000 --order-type limit
> # 查询最大可卖数量
> $FOSUN_PYTHON query_bidask.py --stock 00700 --direction sell --order-type limit
> ```

### 港股限价买入

```bash
$FOSUN_PYTHON place_order.py --stock 00700 --direction buy --quantity 100 --price 350.000 --order-type limit
```

### 港股增强限价买入

```bash
$FOSUN_PYTHON place_order.py --stock 00700 --direction buy --quantity 100 --price 350.000 --order-type enhanced_limit
```

### 港股特别限价买入

```bash
$FOSUN_PYTHON place_order.py --stock 00700 --direction buy --quantity 100 --price 350.000 --order-type special_limit
```

### 港股市价买入

```bash
$FOSUN_PYTHON place_order.py --stock 00700 --direction buy --quantity 100 --order-type market
```

### 港股竞价限价买入

```bash
$FOSUN_PYTHON place_order.py --stock 00700 --direction buy --quantity 100 --price 350.000 --order-type auction_limit
```

### 港股竞价买入

```bash
$FOSUN_PYTHON place_order.py --stock 00700 --direction buy --quantity 100 --order-type auction
```

### 美股市价买入（盘中）

```bash
$FOSUN_PYTHON place_order.py --stock AAPL --market us --direction buy --quantity 5 --order-type market
```

### 美股限价卖出

```bash
$FOSUN_PYTHON place_order.py --stock AAPL --market us --direction sell --quantity 5 --price 180.00 --currency USD --order-type limit
```

### 美股盘前盘后限价买入

```bash
$FOSUN_PYTHON place_order.py --stock AAPL --market us --direction buy --quantity 5 --order-type limit --price 180.00 --time-in-force 2
```

### A 股（中华通）限价买入

```bash
$FOSUN_PYTHON place_order.py --stock 600519 --market sh --direction buy --quantity 100 --price 1800.00 --order-type limit
```

### 港股暗盘订单

```bash
$FOSUN_PYTHON place_order.py --stock 00700 --direction buy --quantity 100 --price 350.000 --order-type dark
```

### 港股止损限价单

```bash
$FOSUN_PYTHON place_order.py --stock 00700 --direction sell --quantity 100 --order-type stop_loss_limit --price 380.000 --trig-price 385.000
```

### 港股止盈限价单

```bash
$FOSUN_PYTHON place_order.py --stock 00700 --direction sell --quantity 100 --order-type take_profit_limit --price 390.000 --trig-price 385.000
```

### 港股跟踪止损单（按比例）

```bash
$FOSUN_PYTHON place_order.py --stock 00700 --direction sell --quantity 100 --order-type trailing_stop --tail-type 2 --tail-pct 0.05
```

### 港股止盈止损单

```bash
$FOSUN_PYTHON place_order.py --stock 00700 --direction sell --quantity 100 --order-type take_profit_stop_loss --price 400.000 --profit-price 420.000 --profit-quantity 100 --stop-loss-price 390.000 --stop-loss-quantity 100
```

### 美股止损限价单

```bash
$FOSUN_PYTHON place_order.py --stock AAPL --market us --direction sell --quantity 5 --order-type stop_loss_limit --price 175.00 --trig-price 176.00
```

### 美股止盈限价单

```bash
$FOSUN_PYTHON place_order.py --stock AAPL --market us --direction sell --quantity 5 --order-type take_profit_limit --price 185.00 --trig-price 184.00
```

### 美股止盈止损单

```bash
$FOSUN_PYTHON place_order.py --stock AAPL --market us --direction sell --quantity 5 --order-type take_profit_stop_loss --price 180.00 --profit-price 185.00 --profit-quantity 5 --stop-loss-price 175.00 --stop-loss-quantity 5
```

### A 股（中华通）止损限价单

```bash
$FOSUN_PYTHON place_order.py --stock 600519 --market sh --direction sell --quantity 100 --order-type stop_loss_limit --price 1780.00 --trig-price 1790.00
```

### A 股（中华通）止盈限价单

```bash
$FOSUN_PYTHON place_order.py --stock 600519 --market sh --direction sell --quantity 100 --order-type take_profit_limit --price 1820.00 --trig-price 1810.00
```

### A 股（中华通）跟踪止损单

```bash
$FOSUN_PYTHON place_order.py --stock 600519 --market sh --direction sell --quantity 100 --order-type trailing_stop --tail-type 2 --tail-pct 0.03
```

### 美股期权限价买入

```bash
$FOSUN_PYTHON place_order.py --stock AAPL --market us --direction buy --quantity 1 --order-type limit --price 5.50 --product-type 15 --expiry 20260630 --strike 200.00 --right CALL
```

### 下单前校验（不实际下单）

```bash
$FOSUN_PYTHON place_order.py --stock 00700 --direction buy --quantity 100 --price 350.000 --order-type limit --check-only
```

`--check-only` 返回可买/可卖数量、购买力、每手股数等信息。

### 全部参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--stock` | 是 | 股票代码（不含市场前缀） |
| `--direction` | 是 | `buy` / `sell` |
| `--quantity` | 是 | 委托数量 |
| `--order-type` | 是 | 必须显式传入：`auction_limit`(1) / `auction`(2) / `limit`(3) / `enhanced_limit`(4) / `special_limit`(5) / `dark`(6) / `market`(9) / `stop_loss_limit`(31) / `take_profit_limit`(32) / `trailing_stop`(33) / `take_profit_stop_loss`(35) |
| `--price` | 条件 | 非 `auction(2)` / `market(9)` / `trailing_stop(33)` 时必填 |
| `--market` | 否 | `hk`（默认）/ `us` / `sh` / `sz` |
| `--currency` | 否 | 自动根据 market 选择（HKD/USD/CHY）；**A 股必须用 CHY** |
| `--check-only` | 否 | 仅校验，不下单 |
| `--exp-type` | 否 | 订单时效类型，如 `1`=当日有效 |
| `--time-in-force` | 否 | 时段控制，`0`=当日有效，`2`=允许美股盘前盘后，`4`=允许夜盘 |
| `--client-id` | 否 | 客户 ID |
| `--apply-account-id` | 否 | 下单申购账号 |
| `--short-sell-type` | 否 | 沽空类型，如 `A/B/C/F/M/N/S/Y` |
| `--trig-price` | 条件 | `stop_loss_limit(31)` / `take_profit_limit(32)` 必填 |
| `--tail-type` | 条件 | `trailing_stop(33)` 必填；`1`=金额，`2`=比例 |
| `--tail-amount` | 条件 | `trailing_stop(33)` 且 `--tail-type 1` 时必填 |
| `--tail-pct` | 条件 | `trailing_stop(33)` 且 `--tail-type 2` 时必填 |
| `--spread` | 否 | 跟踪止损单价差 |
| `--profit-price` | 条件 | `take_profit_stop_loss(35)` 必填，止盈触发价格 |
| `--profit-quantity` | 条件 | `take_profit_stop_loss(35)` 必填，止盈触发数量 |
| `--stop-loss-price` | 条件 | `take_profit_stop_loss(35)` 必填，止损触发价格 |
| `--stop-loss-quantity` | 条件 | `take_profit_stop_loss(35)` 必填，止损触发数量 |
| `--product-type` | 条件 | 期权单必填，如 `15`=期权 |
| `--expiry` | 条件 | 期权单必填，到期日，如 `20260630` |
| `--strike` | 条件 | 期权单必填，行权价 |
| `--right` | 条件 | 期权单必填，`CALL` / `PUT` |

### 条件字段规则

| 场景 | 必填字段 |
|------|----------|
| 止损限价单 / 止盈限价单 | `--trig-price` |
| 跟踪止损单 | `--tail-type` |
| 跟踪止损单且按金额追踪 | `--tail-type 1` + `--tail-amount` |
| 跟踪止损单且按比例追踪 | `--tail-type 2` + `--tail-pct` |
| 止盈止损单 | `--profit-price` + `--profit-quantity` + `--stop-loss-price` + `--stop-loss-quantity` |
| 期权单 | `--product-type 15` + `--expiry` + `--strike` + `--right` |

### 止盈止损单触发语义

`take_profit_stop_loss(35)` 是一张同时带有"止盈条件"和"止损条件"的组合条件单。两侧条件互斥：

- 当市场价格跌至止盈价时，系统提交对应的限价单，并自动撤销止损单。
- 当市场价格涨至止损价时，系统提交对应的限价单，并自动撤销止盈单。
- 因此，`--profit-price` / `--profit-quantity` 表示止盈侧触发条件与数量，`--stop-loss-price` / `--stop-loss-quantity` 表示止损侧触发条件与数量。
- `--price` 仍然是触发后真正提交出去的限价委托价。

方向理解补充：

- 卖出方向下，通常表示给已有持仓同时设置一档止盈和一档止损，哪一侧先触发就执行哪一侧，并撤销另一侧。
- 买入平仓方向下，止盈价格应低于当前市价，止损价格应高于当前市价。
- 使用前应结合当前市价、`--direction`、`--profit-price`、`--stop-loss-price` 与 `--price` 一起检查，避免触发方向设置错误。

### 止损限价单 / 止盈限价单触发语义

这两类单子都不是"立即按 `price` 报出"的普通限价单，而是先等待 `--trig-price` 触发，触发后再按 `--price` 发出限价委托。

| 订单类型 | `--direction sell`（卖出） | `--direction buy`（买入） |
|----------|----------------------------|---------------------------|
| `stop_loss_limit(31)` | 跌到或跌破某个价格后止损卖出 | 涨到某个价格后触发买入，常用于突破追价，触发价通常高于当前市价 |
| `take_profit_limit(32)` | 涨到某个价格后止盈卖出 | 跌到某个价格后触发买入，常用于回落承接，触发价通常低于当前市价 |

补充理解：

- `--trig-price` 决定"什么时候触发"。
- `--price` 决定"触发后按什么限价报单"。
- 卖出止损示例通常会看到 `--price` 略低于 `--trig-price`，这样触发后更容易成交。
- 卖出止盈示例通常会看到 `--price` 高于 `--trig-price`，表示达到目标价位后以设定限价卖出。
- 买入方向下，`stop_loss_limit` 与 `take_profit_limit` 的语义不要只看名称，必须结合价格触发方向理解：前者偏"向上突破买入"，后者偏"向下回落买入"。

### 下单约束

- 必须显式传入 `--order-type`，不要依赖任何默认订单类型
- 港股支持全部订单类型
- 美股仅支持 `limit(3)`、`market(9)`、`stop_loss_limit(31)`、`take_profit_limit(32)`、`trailing_stop(33)`、`take_profit_stop_loss(35)`
- A 股仅支持 `limit(3)`、`stop_loss_limit(31)`、`take_profit_limit(32)`、`trailing_stop(33)`

### price 小数位规则

- 港股：3 位小数（如 `350.000`）
- 美股：3 位小数（如 `180.000`）
- A 股：2 位小数（如 `1800.00`）

### 输出参数说明（实际下单）

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | integer | 状态码，`0` 表示成功 |
| `message` | string | 状态消息 |
| `data.orderId` | string | 订单 ID，系统生成的唯一订单标识 |
| `data.orderStatus` | integer | 订单状态 |

`data.orderStatus` 常见取值：

| 值 | 说明 |
|----|------|
| `10` | 未报 |
| `20` | 待报 |
| `21` | 条件单-待触发 |
| `22` | 待处理 |
| `23` | 待复核 |
| `40` | 已报 |
| `50` | 全成 |
| `60` | 部成 |
| `70` | 已撤 |
| `71` | 条件单-已撤销 |
| `80` | 部撤 |
| `90` | 废单 |
| `91` | 条件单-已取消 |
| `92` | 复核未通过 |
| `100` | 已失效 |
| `101` | 条件单-过期 |
| `901` | 条件单废单 |

> `--check-only` 不会创建订单，实际调用的是买卖信息查询接口，返回的是可买/可卖数量、购买力、每手股数等校验信息。

### 输出参数说明（`--check-only`）

| 字段 | 类型 | 说明 |
|------|------|------|
| `data.maxPurchasePower` | string | 最大购买力（含融资） |
| `data.cashPurchasePower` | string | 现金购买力 |
| `data.availableWithdrawBalance` | string | 总账户可用现金 |
| `data.singleWithdrawBalance` | string | 当前币种可提现金 |
| `data.currency` | string | 币种（HKD/USD/CHY） |
| `data.lotSize` | integer | 每手股数 |
| `data.cashQuantityBuy` | integer | 现金可买数量 |
| `data.maxQuantityBuy` | integer | 最大可买数量 |
| `data.baseQuantitySell` | integer | 本币种可卖数量 |
| `data.maxQuantitySell` | integer | 持仓可卖数量（含关联币种） |

---

## 2. 查询订单 — list_orders.py

```bash
$FOSUN_PYTHON list_orders.py
$FOSUN_PYTHON list_orders.py --stock 00700 --status 20 40
$FOSUN_PYTHON list_orders.py --status-group pending             # 快捷: 未成交
$FOSUN_PYTHON list_orders.py --status-group filled              # 快捷: 已成交
$FOSUN_PYTHON list_orders.py --status-group cancelled           # 快捷: 已撤销
$FOSUN_PYTHON list_orders.py --from-date 2025-01-01 --to-date 2025-01-31
$FOSUN_PYTHON list_orders.py --direction buy --market hk
$FOSUN_PYTHON list_orders.py --market sh sz                     # A 股订单
```

| 参数 | 说明 |
|------|------|
| `--stock` | 按股票代码筛选 |
| `--status` | 按状态筛选（可多个） |
| `--status-group` | 快捷状态分组（与 `--status` 互斥） |
| `--from-date` / `--to-date` | 日期范围 |
| `--direction` | `buy` / `sell` |
| `--market` | `hk` / `us` / `sh` / `sz`（可多个） |
| `--count` | 返回数量（默认 20） |

### 状态分组快捷筛选

| --status-group | 包含状态 | 说明 |
|----------------|----------|------|
| `pending` | 10, 20, 21, 40, 60 | 未成交（未报/待报/条件单待触发/已报/部成） |
| `filled` | 50 | 已成交（全部成交） |
| `cancelled` | 70, 80, 90, 100 | 已撤销（已撤/部撤/废单/已失效） |

### 订单状态枚举

| 值 | 说明 |
|----|------|
| `10` | 未报 |
| `20` | 待报 |
| `21` | 条件单-待触发 |
| `40` | 已报 |
| `50` | 全成 |
| `60` | 部成 |
| `70` | 已撤 |
| `80` | 部撤 |
| `90` | 废单 |
| `100` | 已失效 |

### 订单响应关键字段

| 字段 | 说明 |
|------|------|
| `orderId` | 订单 ID |
| `stockCode` | 股票代码 |
| `orderType` | 订单类型 (3=限价单, 9=市价单) |
| `orderStatus` | 订单状态 |
| `price` | 委托价格 |
| `quantity` | 委托数量 |
| `filledPrice` | 成交价格 |
| `filledQuantity` | 成交数量 |
| `canCancel` | 是否可撤单 (0=否, 1=是) |

