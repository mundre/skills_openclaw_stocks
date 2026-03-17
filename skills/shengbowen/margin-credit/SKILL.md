---
name: margin-credit
description: |
  Provides margin financing (两融) and credit account information: queries, rule interpretation, operation guidance, and risk handling (from account opening to trading and risk control). Use when the user asks about 融资、融券、两融、信用账户、担保品、维持担保比例、追保、平仓、展期、授信额度、折算率、融资利率、卖券还款、融资打新、集中度、杠杆比例、信用评级、标的证券、转融通.
metadata: {"openclaw":{"skillKey":"margin-credit","requires":{"env":["GF_AGENT_COOKIE"]},"primaryEnv":"GF_AGENT_COOKIE"}}
---

# Margin & Credit (智享两融)

Margin financing (两融) and credit account: information query, rule interpretation, operation guidance, and risk handling. Covers the full cycle from account opening to trading and risk control.

## Quick start

When the user asks about margin/credit (融资、融券、两融、信用账户、担保品、维持担保比例、追保、平仓、展期、授信、折算率、融资利率、卖券还款、融资打新、集中度、杠杆、信用评级、标的证券、转融通):

1. Read this skill and ensure `GF_AGENT_COOKIE` is configured.
2. Invoke the script with **only the user's question** as the argument (no user info, session, or channel context).
3. Use the script stdout as the reply content to present or summarize.

## Invocation

**Only pass the user's question text.** Do not pass user ID, sender, session, or any unrelated context.

```bash
node {baseDir}/scripts/chat.mjs "用户问题"
```

Examples:

```bash
node {baseDir}/scripts/chat.mjs "维持担保比例怎么算"
node {baseDir}/scripts/chat.mjs "融资展期怎么操作"
node {baseDir}/scripts/chat.mjs "信用账户开户条件"
node {baseDir}/scripts/chat.mjs "追保和平仓规则"
```

If the question contains spaces, pass it as a single quoted argument.

## Configuration

- **GF_AGENT_COOKIE** (required): Cookie string for hiAgentChat API auth (same as investment-analysis). Set in environment; do not hardcode. Do not commit to repo.
- Node 18+ (for `fetch`).

## Testing

From the skill base dir (or with absolute path to the script):

```bash
# 1. 无 Cookie 时应报错
node scripts/chat.mjs "维持担保比例怎么算"
# → Missing GF_AGENT_COOKIE (exit 1)

# 2. 配置 Cookie 后请求（把 <your-cookie> 换成真实 Cookie）
GF_AGENT_COOKIE="<your-cookie>" node scripts/chat.mjs "维持担保比例怎么算"
# → 正常时在 stdout 输出接口返回的 answer 拼接结果
```

Cookie 可从浏览器登录 aigctest.gf.com.cn 后，在开发者工具 → Network → 选 hiAgentChat 请求 → Headers → Cookie 复制。

## Ability boundary and skill coordination

- **This skill**: Margin financing (两融), credit account, collateral, maintenance margin ratio, margin call, liquidation, extension, credit line, conversion rate, margin rate, sell-to-repay, margin IPO, concentration, leverage, credit rating, underlying securities, securities lending. Use when the query contains these or related terms.
- **Not this skill**: Pure market/index/stock trend or “is this stock worth buying.” For those, use **investment-analysis**.
- **Overlap**: If the user asks both margin/credit and market questions, use this skill first for 两融/信用, then investment-analysis for market/trend if needed.

## Output

The script returns the reply as plain text on stdout. The API is SSE; the script buffers the stream and outputs once. If the platform later supports streaming tools, the script can be adapted to stream.

## When the tool fails (do not retry in a loop)

If the script fails (e.g. **Missing GF_AGENT_COOKIE**, API error, or network error), its output will include a line containing **"Do not retry"**.

- **Do NOT** invoke the tool again for the same user request. Repeating the same failed command will not fix the issue and wastes turns.
- **Do** report the failure to the user once: e.g. "两融查询暂时不可用（可能未配置 Cookie 或接口异常），请稍后再试或检查配置。" and optionally suggest checking `GF_AGENT_COOKIE` or trying again later.
- If you see "Do not retry" in the tool output, treat the request as handled and do not call this skill again in this turn.

## Additional resources

- For API URL (agentId=mfis2agent), request body, and **response parsing (answer only)**, see [references/api.md](references/api.md).
