---
name: ovra-payments
description: Autonomous payments for AI agents with virtual Visa cards. Use when the user asks to buy, purchase, pay for, subscribe to, or order anything online. Handles HTTP 402 paywalls automatically. Provides tokenized card data (DPAN) — never exposes real card numbers. Supports any merchant that accepts Visa.
---

# Ovra — Agentic Payments

Make purchases autonomously with virtual Visa cards. You get tokenized card data (DPAN + cryptogram), never real card numbers. Policy engine controls what you can spend.

## When to Use

- User says "buy", "purchase", "pay for", "subscribe to", "order" anything
- You hit an HTTP 402 Payment Required response
- User asks about card balance, spending limits, or payment history
- User wants to manage cards (issue, freeze, close, rotate)

## Quick Reference

| Action | Tool | Example |
|--------|------|---------|
| Buy something | `ovra_pay` | `{action:"checkout", agentId:"ag_xxx", purpose:"Notion Plan", amount:79, merchant:"Notion"}` |
| Handle 402 paywall | `ovra_pay` | `{action:"handle_402", agentId:"ag_xxx", url:"https://api.example.com", merchant:"Example", amountEuros:0.05}` |
| Check capabilities | `ovra_pay` | `{action:"discover", agentId:"ag_xxx"}` |
| Issue a card | `ovra_card` | `{action:"issue", agentId:"ag_xxx", usage:"multi", purpose:"SaaS"}` |
| View policy | `ovra_policy` | `{action:"get", agentId:"ag_xxx"}` |
| Upload receipt | `ovra_receipt` | `{action:"upload", intentId:"in_xxx", fileBase64:"...", fileName:"receipt.pdf"}` |

## Payment Flow

1. **`ovra_pay { action: "checkout" }`** — one call does everything:
   - Creates intent → policy check → risk check → credential grant → issue → redeem
   - Returns: `dpan`, `expiryMonth`, `expiryYear`, `cryptogram`, `dynamicCvc`
   - If denied: returns reason (policy violation)
   - If pending: human must approve

2. **Fill checkout form** with the tokenized data:
   - Card number → DPAN (e.g. "4319 7261 7668 2936")
   - Expiry → MM/YY (e.g. "12/28")
   - CVC → `dynamicCvc` (NOT cryptogram — they are different)

3. **After payment** (optional):
   - Upload receipt: `ovra_receipt { action: "upload" }`
   - Verify: `ovra_intent { action: "verify", actualAmountEuros, actualMerchant }`

## HTTP 402 Handling

When you hit a paywall:
```
ovra_pay { action: "handle_402", agentId: "ag_xxx", url: "https://api.example.com/data", merchant: "Example API", amountEuros: 0.05 }
```
Returns tokenized card data in one call. Use it to answer the 402 challenge.

## Tools

| Tool | Actions | Description |
|------|---------|-------------|
| `ovra_pay` | checkout, handle_402, discover, status | Main payment tool |
| `ovra_card` | issue, list, freeze, unfreeze, close, rotate | Card lifecycle |
| `ovra_intent` | list, declare, get, cancel, verify | Payment intents |
| `ovra_credential` | obtain, grant, issue, redeem, revoke, status | Advanced credential control |
| `ovra_policy` | get | View spending rules (read-only) |
| `ovra_transaction` | list, get, memo | Payment history |
| `ovra_receipt` | upload, get | Receipt management |
| `ovra_dispute` | list, get, file | Dispute filing |

## Rules

1. **`ovra_pay` is the default.** Only use `ovra_credential` for fine-grained control.
2. **Merchant = name** (e.g. "Notion"), not the URL.
3. **All amounts in EUR.**
4. **Policies are read-only.** Never modify them.
5. **Funding is dashboard-only.** If balance is 0, tell user to fund at getovra.com/dashboard.
6. **CVC = `dynamicCvc`**, not `cryptogram`.
7. **On errors:** create a new intent. Don't fix old ones.
8. **Talk about the purchase**, not technical details (intents, grants, credentials).
9. **Destructive actions** (card close) require `confirm: true`.
