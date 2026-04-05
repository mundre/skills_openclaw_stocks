---
name: fosun-trading
description: 复星集团旗下复星财富（Fosun Wealth，星财富 APP）证券交易工具集的通用基础配置，定义环境约束、市场规则、订单类型、交易限制与推荐工作流；行情查询见 fosun-market-data，账户查询见 fosun-account，订单管理见 fosun-orders。
requires:
  env:
    - FSOPENAPI_API_KEY
    - FSOPENAPI_CLIENT_PRIVATE_KEY
    - FSOPENAPI_SERVER_PUBLIC_KEY
  bins:
    - python3
---

# 复星交易工具集 — 通用基础

通过命令行脚本完成港股/美股/A股(中华通)的行情查询、行情推送订阅、会话管理、资金查询、资金流水查询、下单/改单/撤单、订单管理和交易订阅管理。所有脚本位于 `code/` 目录下。

> **⚠️ 当前版本不支持期权**：期权行情查询（`query_option_price.py`）和期权交易下单功能暂未开放。文档中保留的期权相关章节（第 11 节期权行情、下单期权参数等）仅供未来版本参考，当前禁止使用。
本 skill 定义了所有复星交易脚本共享的环境约束、市场规则、订单类型和交易限制。
具体操作请参考对应 skill：

| Skill | 用途 |
|----------|------|
| `fosun-market-data` | 行情查询（股票报价、期权行情、行情推送） |
| `fosun-account` | 账户查询（买卖信息、资金/持仓、资金流水） |
| `fosun-orders` | 订单管理（下单、查单、撤单、改单） |

所有脚本位于本 skill 的 `code/` 目录下。

## 前置条件

1. SDK 已安装（参考 `fosun-sdk-setup` skill）
2. `fosun.env` 可由初始化流程自动生成，运行时会自动检查：
   - `FSOPENAPI_SERVER_PUBLIC_KEY` — 服务端公钥（PEM）
   - `FSOPENAPI_CLIENT_PRIVATE_KEY` — 客户端私钥（PEM）
   - `FSOPENAPI_API_KEY` — API Key（也可通过 `--api-key` 传入）
   - `FSOPENAPI_BASE_URL` — 网关地址（可选，默认 `https://openapi.fosunxcz.com`）
   - `FSOPENAPI_MAC_ID` — 本地持久化设备唯一编码
   - `FSOPENAPI_API_KEY_STATUS` / `FSOPENAPI_TICKET_STATUS` — 本地状态缓存

---

## 环境约束（必须遵守）

> **⚠️ 每次运行任何脚本之前，必须先从记忆中获取虚拟环境路径！**

- **优先使用本 skill 或相关 skill 已提供的 bash / python / shell 命令；能直接执行现成命令时，不要临时写代码。**
- **不要自己写 Python 调 SDK**，直接使用 `fosun-trading` skill 的 `code/` 目录脚本。
- **统一使用 `$FOSUN_VENV/bin/python` 和 `$FOSUN_VENV/bin/pip` 完成程序执行与安装**
- **路径从记忆获取**：读取 `MEMORY.md` 中 `Fosun SDK` 记录的虚拟环境路径。下文所有示例中的 `$FOSUN_PYTHON` 均代指 `<虚拟环境路径>/bin/python`。
- **记忆中无记录** → 先执行 `fosun-sdk-setup` skill 完成环境初始化，再回来执行脚本。
- **查询持仓和交易行情前强制先过 `credential_flow.py`**：每次执行 `query_funds.py holdings`、`query_price.py`、`market_push.py` 之前，必须先通过 `credential_flow.py` 检查 `fosun.env` 与必需环境变量是否存在；禁止跳过该脚本直接查询。
- **⚠️ 当前版本不支持期权**：`query_option_price.py` 和期权下单参数（`--product-type 15`、`--expiry`、`--strike`、`--right`）当前不可用，禁止执行任何期权相关操作。

- **用户提到某只股票时必须先检查是否多地上市**：如果用户只提到股票名、简称或一个未明确市场的股票代码，先使用 `code/query_listed_markets.py` 查询其是否同时在港股 / 美股 / A 股上市。
- **多地上市时必须主动确认具体代码**：只要查询结果显示该股票存在多个市场代码，就必须先向用户确认本次要使用哪一个标的代码（如 `hk00700`、`usBABA`、`sh601939`），确认前不要直接默认市场执行行情、下单或其他交易相关操作。
- **脚本输出的数值必须原样引用，严禁篡改**：向用户转述任何脚本返回的数值（数量、价格、余额、lotSize、成交量等）时，必须从脚本输出原文逐字复制，禁止凭记忆复述、四舍五入、省略零、添加零、换算单位或做任何近似处理。展示时优先使用表格/列表格式，关键数值加粗，单位紧跟数字。详见 `fw-tradings` skill 的「数据准确性强制规则」。
- **条件单对用户的回复必须使用自然语言**：凡是向用户解释、确认、复述、汇总任何条件单信息时，必须使用中文或英文自然语言表述订单含义、触发条件和委托价格，**绝对不允许直接把代码参数字段名回复给用户**（如 `--trig-price`、`--price`、`--profit-price`、`--stop-loss-price`、`stop_loss_limit`、`take_profit_limit` 等）。这些字段名只能用于内部命令构造，不能直接当作面对用户的回复内容。
- **只要用户提到任何条件单，必须先熟悉专用说明文档**：凡是用户提到条件单、止损单、止盈单、跟踪止损、组合止盈止损，或提到 `stop_loss_limit`、`take_profit_limit`、`trailing_stop`、`take_profit_stop_loss` 等相关概念时，**大模型必须先阅读 `doc/ConditionalOrders.md`，熟悉对应场景、触发语义、适用方向、示例和常见误区后，才能继续回复或执行后续操作**；禁止跳过该文档直接凭印象回答。

所有脚本运行格式：

```bash
$FOSUN_PYTHON <脚本名>.py <子命令> [参数]
```

### 自动初始化行为

所有脚本进入 `get_client()` 前都会统一执行以下前置检查，**只会产生 3 种结果**：

| 结果 | 触发条件 | 系统行为 |
|------|----------|----------|
| **1️⃣ 直接执行** | API Key 已生效（`valid`） | 自动加载凭证，直接执行您的交易命令 |
| **2️⃣ 生成新二维码** | API Key 失效/不存在 或 Ticket 过期 | 自动申请新的 API Key 和开通 URL，生成二维码供扫码 |
| **3️⃣ 复用现有二维码** | Ticket 有效但未完成授权 | 直接返回已有的开通 URL，生成二维码供扫码 |

> 对"查询持仓"和"交易行情"这两类请求，这个前置检查不是可选优化，而是强制步骤。

---

## 🔒 强制前置检查（必须遵守）

每次查询资金、持仓或交易行情前，系统会自动执行以下检查：

1. 检查 `FSOPENAPI_MAC_ID`（设备编码）
2. 检查 `FSOPENAPI_CLIENT_PRIVATE_KEY`（客户端私钥）
3. 检查 `FSOPENAPI_API_KEY_STATUS`（API Key 状态）
4. 根据校验结果，只会产生 3 种结果之一：
   - **结果 1**：API Key 有效 → 直接执行您的命令
   - **结果 2**：需重新申请 → 生成新二维码供扫码
   - **结果 3**：Ticket 有效 → 返回现有二维码供扫码

**请勿跳过此检查，直接运行业务脚本即可自动完成。**

## 支持的市场

| 市场代码 | 说明 | 行情级别 | 币种 |
|----------|------|----------|------|
| `hk` | 港股 | L1,L2（含盘口、经纪商队列） | HKD |
| `us` | 美股 | L1（支持盘前/盘中/盘后） | USD |
| `sh` | 上交所（中华通） | L1 | CHY |
| `sz` | 深交所（中华通） | L1 | CHY |

**标的代码格式**：`marketCode + stockCode`

| 示例 | 说明 |
|------|------|
| `hk00700` | 腾讯控股（港股） |
| `usAAPL` | 苹果（美股） |
| `sh600519` | 贵州茅台（A 股-沪） |
| `sz000001` | 平安银行（A 股-深） |

## 支持的订单类型

| 名称 | order_type 值 | 常用 CLI 传值 | 是否需要 price | 适用市场 | 说明 |
|------|---------------|---------------|----------------|----------|------|
| 竞价限价单 | `1` | `auction_limit` 或 `1` | 是 | 港股 | 竞价时段以指定价格参与竞价 |
| 竞价单 | `2` | `auction` 或 `2` | 否 | 港股 | 竞价时段以市场价参与竞价 |
| 限价单 | `3` | `limit` 或 `3` | 是 | 港/美/A | 普通限价委托 |
| 增强限价单 | `4` | `enhanced_limit` 或 `4` | 是 | 港股 | 最多配对 10 个价位，未成交部分保留为限价单 |
| 特殊限价单 | `5` | `special_limit` 或 `5` | 是 | 港股 | 最多配对 10 个价位，未成交部分自动取消 |
| 暗盘订单 | `6` | `dark` 或 `6` | 视接口规则而定 | 港股 | 港股暗盘交易场景使用 |
| 市价单 | `9` | `market` 或 `9` | 否 | 港/美 | 以当前市场价成交 |
| 止损限价单 | `31` | `stop_loss_limit` 或 `31` | 是 | 港/美/A | 触发后按限价委托，需同时传 `--trig-price` |
| 止盈限价单 | `32` | `take_profit_limit` 或 `32` | 是 | 港/美/A | 触发后按限价委托，需同时传 `--trig-price` |
| 跟踪止损单 | `33` | `trailing_stop` 或 `33` | 否 | 港/美/A | 需同时传 `--tail-type`，按金额或比例追踪 |
| 止盈止损单 | `35` | `take_profit_stop_loss` 或 `35` | 是 | 港/美 | 互斥双条件单；一侧触发后提交限价单，并自动撤销另一侧条件单 |

> `stop_loss_limit(31)` / `take_profit_limit(32)` 都属于"先触发、后挂限价单"的条件单：`--trig-price` 是触发价，`--price` 是触发后真正报出的限价委托价。
>
> **⚠️ 对用户回复的表达规则（条件单强制遵守）：**
> - 向用户解释条件单时，必须说"触发价 / 委托价 / 止盈价 / 止损价 / 跟踪比例 / 跟踪金额"等中文术语，或对应英文自然语言表达。
> - **绝对禁止**直接把 `--trig-price`、`--price`、`--tail-pct`、`--profit-price`、`--stop-loss-price`、`stop_loss_limit`、`take_profit_limit` 这类代码字段名原样回复给用户。
> - 代码字段名只允许出现在内部命令、脚本示例、参数表或实现细节中；面向用户的最终表述必须转换成人类可读的自然语言。
> - **只要用户提到任何条件单相关问题，必须先查看 `doc/ConditionalOrders.md`**，按该文档的场景解释、触发逻辑和示例来理解与回复，禁止绕过该文档直接作答。
>
> 方向语义补充：
> - 止损限价单，卖出时一般表示"跌到或跌破某价格后止损卖出"；买入时一般表示"涨到某个价格后追价买入"，因此买入方向下触发价通常高于当前市价。
> - 止盈限价单，卖出时一般表示"涨到某个价格后止盈卖出"；买入时一般表示"跌到某个价格后逢低买入"，因此买入方向下触发价通常低于当前市价。
> - 实务上应结合当前市价、`--direction`、`--trig-price` 与 `--price` 一起检查，确保触发条件与下单意图一致。

> 执行 `place_order.py` 前，必须先按市场校验订单类型是否合法，并显式传入 `--order-type`；禁止省略为默认值。

## 运行方式

所有脚本位于本 skill 的 `code/` 目录下。运行前先 `cd` 到该目录：

```bash
cd {skill_dir}/code
$FOSUN_PYTHON <脚本名>.py <子命令> [参数]
```

> `{skill_dir}` 为本 `fosun-trading.md` 所在目录的绝对路径（即 `fw-tradings/fosun-trading`）。

---

## 下单工作流（推荐步骤）

```
1. 查询行情      → $FOSUN_PYTHON query_price.py quote hk00700
2. 查看盘口      → $FOSUN_PYTHON query_price.py orderbook hk00700
3. 查询每手股数  → $FOSUN_PYTHON query_bidask.py --stock 00700 --lot-size-only
4. 确认资金      → $FOSUN_PYTHON query_funds.py summary
5. 提交订单      → $FOSUN_PYTHON place_order.py --stock 00700 --direction buy --quantity 100 --price 350.000 --order-type limit
6. 确认结果      → $FOSUN_PYTHON list_orders.py --stock 00700
```

**A 股下单示例：**

```
1. 查询行情      → $FOSUN_PYTHON query_price.py quote sh600519
2. 查询每手股数  → $FOSUN_PYTHON query_bidask.py --stock 600519 --market sh --lot-size-only
3. 确认资金      → $FOSUN_PYTHON query_funds.py summary --currency CHY
4. 下单前校验    → $FOSUN_PYTHON place_order.py --stock 600519 --market sh --direction buy --quantity 100 --price 1800.00 --order-type limit --check-only
5. 提交订单      → $FOSUN_PYTHON place_order.py --stock 600519 --market sh --direction buy --quantity 100 --price 1800.00 --order-type limit
6. 确认结果      → $FOSUN_PYTHON list_orders.py --market sh
```

---

## ⛔ AI 交易限制（必须遵守）

> 通用调用频率、IP 白名单等基础限制见 `fosun-sdk-setup` skill。

### 下单频率限制

| 维度 | 限制 | 超限处理 |
|------|------|---------|
| 每小时下单次数（买卖一起） | 单个客户 ≤ 10 笔/小时 | 该小时内拒绝新委托 |
| 每日总下单次数（买卖一起） | 单个客户 ≤ 50 笔/天 | 当日拒绝新委托 |

### 美股市场

| 限制项 | 具体规则 |
|--------|---------|
| 可交易品种 | 仅开放美股正股交易（当前版本不支持期权） |
| 交易单位 | 1 股起买，仅支持整股，不允许碎股委托 |
| 单笔委托买入 | ≤ 10 股 且 ≤ 50 USD（市价单没有价格，只有股数限制） |

### 港股市场

| 限制项 | 具体规则 |
|--------|---------|
| 交易单位 | 必须按手交易，每手股数以交易所官方定义为准 |
| 单笔委托买入 | 仅允许委托 1 手，不允许多手 且 ≤ 2000 HKD（竞价单、市价单没有价格，仅检验手数股数） |

### A 股市场（中华通）

| 限制项 | 具体规则 |
|--------|---------|
| 交易单位 | 必须按手交易，每手股数以交易所官方定义为准 |
| 单笔委托买入 | 仅允许委托 1 手，不允许多手 且 ≤ 2000 CHY |

> 市场代码：上交所 `sh`，深交所 `sz`。币种为 CHY（人民币），价格保留 2 位小数。**A 股下单必须使用 `CHY` 作为币种，不可使用 `CNH` 或 `CNY`。**

### 统一客户额度限制

| 限制项 | 具体规则 |
|--------|---------|
| 单日累计交易金额（成交 + 未完成订单总额） | 单个客户 AI 渠道买卖总和 ≤ 15000 HKD（港美A不区分） |
| 每小时下单次数（买卖一起） | 单个客户 AI 渠道 ≤ 10 笔/小时 |

## 常见错误处理

| 场景 | 处理方式 |
|------|---------|
| 鉴权过期 | SDK 自动续期，一般无需处理 |
| 资金不足 | 先用 `query_funds.py summary` 确认 |
| 价格不合法 | 先用 `query_price.py quote` 获取最新价|
| 数量不合法 | 港股注意整手（查 `lotSize`），美股可 1 股起 |
| 订单类型不支持 | 参考上方订单类型表，按市场校验 |
