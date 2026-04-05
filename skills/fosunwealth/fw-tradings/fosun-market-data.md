---
name: fosun-market-data
description: 复星集团旗下复星财富（Fosun Wealth，星财富 APP）行情查询工具集，支持股票行情拉取（报价/盘口/K 线/分时/逐笔/经纪队列）、期权行情查询和行情推送订阅，覆盖港股 (L2)、美股 (L1)、A 股 (L1) 及美股期权。
requires:
  env:
    - FSOPENAPI_API_KEY
    - FSOPENAPI_CLIENT_PRIVATE_KEY
    - FSOPENAPI_SERVER_PUBLIC_KEY
  bins:
    - python3
---

# 复星行情查询工具集

> **⚠️ 数据准确性最高优先级规则：**
> 本 skill 返回的所有数值（股价、涨跌幅、成交量、盘口价格/数量、K 线数据、分时数据等）**必须从脚本输出中原样逐字引用**，严禁凭记忆复述或做任何近似处理。
> - 脚本输出 `price=350.200`，就必须说 **350.200**，不能说成"约 350"或"350.2"。
> - 脚本输出 `volume=12345600`，就必须说 **12345600**，不能说"约 1234 万"。
> - 展示行情数据时**优先使用表格格式**，关键数值加粗，单位紧跟数字。
> - 如对某个数值不确定，必须重新执行脚本获取，禁止猜测。

通过命令行脚本查询港股/美股/A股(中华通)的股票行情、期权行情以及行情推送订阅。

> **通用环境约束、市场定义和订单类型请参考 `fosun-trading` skill。**
> 所有脚本位于 `fosun-trading` skill 的 `code/` 目录下（即 `fw-tradings/fosun-trading/code/`）。

运行前先 `cd` 到脚本目录：

```bash
cd <fosun-trading skill 目录>/code
$FOSUN_PYTHON <脚本名>.py <子命令> [参数]
```

---

## 1. 多地上市检查 — query_listed_markets.py

> 当用户只提到股票名、简称或未明确市场的代码时，先用这个脚本判断是否在港股 / 美股 / A 股多地上市。
> 如果结果包含多个市场代码，必须先向用户确认本次要使用的具体标的代码，再继续后续操作。

### 常用示例

```bash
$FOSUN_PYTHON query_listed_markets.py 00700
$FOSUN_PYTHON query_listed_markets.py BABA
$FOSUN_PYTHON query_listed_markets.py 601939
```

> 返回结果会标明是否在 `港股`、`A股`、`美股` 上市，以及对应的 `hk` / `sh|sz` / `us` 代码。

---

## 2. 查询行情 — query_price.py

> `query_price.py` 仅负责主动拉取（API 调用）；推送订阅请使用后文 `market_push.py`。
> - 脚本会自动把接口里的价格整数值还原成真实价格后再输出，不需要再手算。

> 输出说明：
>
> - `quote`、`orderbook`、`kline`、`min`、`tick`、`broker` 的价格字段都会先自动换算，再输出给用户。
> - 盘口档位中的 `p`、K 线中的 `open/high/low/close`、分时中的 `price/avg` 也会自动换算。
> - 输出结果里不再保留内部精度字段，价格可以直接用于阅读和决策。

### 批量报价（最常用）

```bash
$FOSUN_PYTHON query_price.py quote hk00700 usAAPL sh600519
```

### 盘口/买卖档

```bash
$FOSUN_PYTHON query_price.py orderbook hk00700 --count 5
```

### K 线

```bash
$FOSUN_PYTHON query_price.py kline hk00700 --ktype day -n 30
```

`ktype` 可选：`day` / `week` / `month` / `year` / `min1` / `min5` / `min15` / `min30` / `min60`

### 分时

```bash
$FOSUN_PYTHON query_price.py min hk00700 --count 5
```

### 逐笔成交

```bash
$FOSUN_PYTHON query_price.py tick hk00700 -n 20
```

### 经纪商队列（仅港股 L2）

```bash
$FOSUN_PYTHON query_price.py broker hk00700
```

---

## 3. 期权行情 — query_option_price.py

> 该脚本对应 SDK 的 `optmarket` 模块，只覆盖期权行情查询，不负责期权交易确认流程。
>
> - 脚本会自动把 `price`、`bid`、`ask`、盘口档位价格 `p`、K 线/分时价格等字段还原为真实价格后再输出。

> 输出说明：
>
> - `quote`、`orderbook`、`kline`、`tick`、`day-min` 的价格字段都会自动还原。
> - 常见已自动换算字段包括 `price`、`bid`、`ask`、`strikePrice`、盘口档位 `p`、K 线 `open/high/low/close`、分时 `price/avg`。
> - 这些脚本打印出来的价格已经是真实价格，且不会再保留内部精度字段；真正下单时也应继续传真实价格，而不是传接口里的原始整数值。

### 期权代码格式

```text
usAAPL 20260320 270.0 CALL
```

含义依次为：

| 片段 | 说明 |
|------|------|
| `usAAPL` | 标的证券 |
| `20260320` | 到期日 |
| `270.0` | 行权价 |
| `CALL` | 认购方向（也可能为 `PUT`） |

### 期权批量报价

```bash
$FOSUN_PYTHON query_option_price.py quote "usAAPL 20260320 270.0 CALL"
```

### 期权盘口

```bash
$FOSUN_PYTHON query_option_price.py orderbook "usAAPL 20260320 270.0 CALL"
```

### 期权 K 线

```bash
$FOSUN_PYTHON query_option_price.py kline "usAAPL 20260320 270.0 CALL" --ktype day -n 10
```

### 期权逐笔

```bash
$FOSUN_PYTHON query_option_price.py tick "usAAPL 20260320 270.0 CALL" -n 20
```

### 期权多日分时

```bash
$FOSUN_PYTHON query_option_price.py day-min "usAAPL 20260320 270.0 CALL" --days 3
```

---

## 4. 行情推送 — market_push.py

> **⚠️ 这是长连接脚本。**
> 运行后会保持 WebSocket 连接，持续输出 SDK 收到的推送消息。默认订阅 30 秒后退出；`--duration 0` 表示常驻。

### 报价推送

```bash
$FOSUN_PYTHON market_push.py quote hk00700 usAAPL --duration 30
```

### 分时/逐笔/盘口/经纪队列推送

```bash
$FOSUN_PYTHON market_push.py min hk00700 --duration 30
$FOSUN_PYTHON market_push.py tick hk00700 --duration 30
$FOSUN_PYTHON market_push.py orderbook hk00700 --duration 30
$FOSUN_PYTHON market_push.py broker hk00700 --duration 30
```

### 市场状态推送

```bash
$FOSUN_PYTHON market_push.py market-status hk us cn --duration 15
```

### 退出前自动退订

```bash
$FOSUN_PYTHON market_push.py quote hk00700 --duration 10 --auto-unsubscribe
```

> `market-status` 使用市场代码（如 `hk` / `us` / `cn`）；其他主题使用证券代码（如 `hk00700` / `usAAPL`）。
