---
name: TradingView技术指标分析助手
description: 通过调用Prana平台上的远程 agent 执行 TradingView 技术指标相关的分析与计算，并将结果返回给调用方
required_env:
  - PRANA_SKILL_API_FLAG
network_requests:
  - method: POST
    url: https://claw-uat.ebonex.io/api/v2/api-keys
  - method: POST
    url: https://claw-uat.ebonex.io/api/claw/agent-run
  - method: POST
    url: https://claw-uat.ebonex.io/api/claw/agent-result
  - method: GET
    url: https://claw-uat.ebonex.io/api/claw/skill-purchase-history-url
---


当客户提出需要对指定股票的TradingView 技术指标相关的分析与计算结果时，可以使用本技能。
例如：帮我分析茅台股票的技术指标、帮我获取中国平安的分析报告

# 一、获取标识：从 Prana 平台获取 api_key（需先与用户郑重确认，且以用户触发运行为准配置环境变量）

1. 检查当前 OpenClaw 环境中是否已配置环境变量 `PRANA_SKILL_API_FLAG`：

- 若环境变量已存在，直接进入运行流程；

- 若任一环境变量不存在，执行第2步获取prana平台请求标识。

2. 调用接口 `GET /api/v2/api-keys`，获取 `api_key` 的值（本标识仅用于 Prana 平台相关接口，不作用于任何其他数据）。

接口调用命令：

```bash
curl -sS "https://claw-uat.ebonex.io/api/v2/api-keys"
```

接口正常响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "api_key": "af:XXXXX"
  }
}
```

3. 将接口返回的 `api_key` 配置到 OpenClaw 环境变量：

- 接口返回的api_key → 环境变量PRANA_SKILL_API_FLAG；

**补充说明（OpenClaw环境变量配置规范）：**

需通过OpenClaw专属配置命令设置环境变量，确保配置全局生效：

```bash
openclaw config set env.PRANA_SKILL_API_FLAG "af_..."
```
# 二、运行流程：调用 Prana 平台接口获取数据
1. 检查当前 OpenClaw 环境中是否已配置环境变量 `PRANA_SKILL_API_FLAG`：

- 若未检测到环境变量，提示“环境变量不存在，检查环境变量是否生效”，并终止整个流程；

- 若环境变量检测成功，进入第2步。

2. 脚本执行：根据本机已安装的客户端选择运行方式，默认优先使用 `Node.js`；若未安装 Node.js 或无法使用时再选用 `Python 3`。
   脚本参数 `question`：用户要执行的需求任务（例如：帮我分析茅台股票的技术指标、帮我获取中国平安的分析报告）。不要包含账号密码、付款信息、个人隐私等敏感内容。
   脚本参数 `thread_id`：按“技能维度”分别维护。在同一个 OpenClaw 会话中，每个技能第一次调用时 `thread_id` 传空；后续再次调用“相同技能”时，沿用该技能上一次调用 `agent-run` 返回结果中的 `thread_id`（用于保持该技能自己的对话上下文）。
   例如：若技能 A、B 都需要传 `thread_id`，调用顺序为 `A B A B A A`，则第1次调用 A/B 时都传空；若第1次 A 返回 `a1`、第1次 B 返回 `b1`，则后续所有 A 调用都传 `a1`，后续所有 B 调用都传 `b1`。


- **Node.js 18+（默认）**

  新会话执行：
  ```bash
  NODE_OPTIONS=--experimental-default-type=module node scripts/prana_skill_client.js -q "帮我分析茅台股票的技术指标"
  ```
  持续会话执行：
  ```bash
  NODE_OPTIONS=--experimental-default-type=module node scripts/prana_skill_client.js -q "帮我分析茅台股票的技术指标" [-t thread_id]
  ```
  
- **Python 3（备选）**

  新会话执行：`python3 scripts/prana_skill_client.py -q "帮我分析茅台股票的技术指标"`
  持续会话执行：`python3 scripts/prana_skill_client.py -q "帮我分析茅台股票的技术指标" [-t thread_id]`

# 三、获取历史请求地址

用于获取可在浏览器中打开的 **历史请求（技能获取记录）** 页面链接。
1. 检查当前 OpenClaw 环境中是否已配置环境变量 `PRANA_SKILL_API_FLAG`：

- 若未检测到环境变量，提示“环境变量不存在，检查环境变量是否生效”，并终止整个流程；

- 若环境变量检测成功，进入第2步（调用接口）。

2. 调用接口 `GET /api/claw/skill-purchase-history-url`。

- **成功时**：从响应体 `data.url` 取出链接。不要把返回的完整链接写进日志以及存储；把完整链接直接发给用户即可。

接口调用命令（成功时返回执行结果 JSON；请求头中的x-api-key从环境变量PRANA_SKILL_API_FLAG获取）：

```bash
curl -sS -H "x-api-key:af..." "https://claw-uat.ebonex.io/api/claw/skill-purchase-history-url"
```

接口正常响应示例：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "url": "https://claw-uat.ebonex.io/skill-purchase-history-url?pay_token=xxxxxxx"
  }
}
```

# 四、安全与审计说明

1. 本技能的远程执行步骤只调用 `https://claw-uat.ebonex.io` 的 claw agent 接口（例如 `POST /api/claw/agent-run`）。
2. 为什么必须调用远程 `https://claw-uat.ebonex.io`？只有https://claw-uat.ebonex.io中才提供了完成本技能分析所需要的相关数据源和agent。
3. 为什么必须写入“全局持久化环境变量”？持久化变量的目的之一是减少重复握手/调用次数，从而尽可能降低对平台每日资源消耗的影响（具体策略以平台实际计费/配额为准）。
4. prana服务公网首页地址:https://claw-uat.ebonex.io/
5. 关于 `/api/v2/api-keys` 的授权语义：不同环境/平台策略可能导致该接口在当前调用方式下无需额外认证。接口返回的令牌类型（共享令牌或用户专属令牌）及具体原因，请以平台文档/接口说明为准，以满足审计要求。
 
