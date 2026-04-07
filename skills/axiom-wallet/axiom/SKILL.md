---
name: axiom_wallet
description: Use Axiom Wallet via MCP to manage payment methods, review account activity, and complete user-requested purchases with single-use payment details.
metadata: {"openclaw":{"homepage":"https://clawhub.ai/bswaidner/axiom-wallet","requires":{"bins":[{"name":"mcporter","version":">=0.8.0"}]}}}
---

# Axiom Wallet

Use this skill when the user wants to interact with their Axiom Wallet through MCP.

Axiom Wallet can be used to:
- check the payment method on file
- review recent transactions
- retrieve single-use payment details for a user-requested purchase (charged to the card on file)
- attach receipt details after a successful purchase

The Axiom MCP endpoint is:

`https://mcp.useaxiom.ai/mcp`

## When to use this skill

Use Axiom Wallet when the user asks you to:
- buy or pay for something with Axiom
- check their Axiom payment method or account info
- inspect recent Axiom transactions
- retrieve payment details for a specific checkout

Do not use this skill for unrelated browsing, account settings changes outside the available MCP tools, or speculative purchases the user has not clearly requested.

## Authentication

If Axiom is not yet authenticated in the current environment, run:

```bash
mcporter auth https://mcp.useaxiom.ai/mcp --browser none --oauth-timeout 300000
```

This opens the OAuth login page in a headless browser. The page automatically enters device-flow mode and displays an activation URL.

1. The page displays an activation URL under the heading "Activation URL".
2. Read the activation URL from the page — it is the link element with a `data-device-auth-url` attribute.
3. Send only the activation URL to the user with a message like: "To connect Axiom Wallet, open this link on your device and approve access: [URL]"
4. Wait — the page polls automatically. When the user approves on their device, mcporter receives the OAuth token and authentication is complete.

**If the page shows a login form instead of the activation URL**, click the "Sign in on another device" button at the bottom of the page. This switches to device-flow mode and displays the activation URL. Then continue from step 1 above.

If the session expires (5-minute TTL), the page shows a "Try again" button. Click it to generate a fresh activation URL and resend to the user.

Only share what is necessary for approval. Never share OAuth tokens, cookies, browser state, or unrelated page content.

If auth fails or expires, tell the user and retry the same command. To clear cached tokens:

```bash
mcporter auth https://mcp.useaxiom.ai/mcp --reset
```

## Available tools

Use the MCP tools exposed by the server when available:

- `whoami` — returns user profile (name, email, shipping address, phone)
- `get_payment_method` — returns the card on file (brand and last 4 digits only). Use this to verify a payment method exists before attempting a purchase.
- `list_transactions` — lists recent transactions (optional `cardId` filter, `limit`)
- `get_payment_details` — issues a single-use virtual card for a purchase and charges the user's card on file. Requires `itemName`, `itemAmount` (dollars), `merchant` (`merchantName`, `merchantWebsite`), and `reasonForPurchase` (`userCommand`, `aiReasoning`). May fail if blocked by spending rules, if approval is required, or if the card on file is declined.
- `create_receipt` — attaches receipt details to a completed transaction

## Purchase workflow

When the user asks you to buy something, use this order:

1. Confirm the purchase details.
   - Use the exact item, merchant, quantity, and price the user asked for.
   - Do not invent purchase-critical facts.

2. Complete all checkout steps that do not require payment.
   - Fill in name, email, shipping address, and any other required fields first.
   - Advance through the checkout until the final step where payment details are needed to proceed.
   - The goal is to reach the final total (including shipping, tax, and fees) before requesting a card.

3. Verify payment method.
   - Call `get_payment_method` to confirm the user has a card on file.
   - If no payment method exists, tell the user to add a card in their account settings and stop.

4. Request payment details.
   - Call `get_payment_details` with:
     - `itemName` — name of the item being purchased
     - `itemAmount` — the final total in dollars
     - `merchant` — `{ merchantName, merchantWebsite }`
     - `reasonForPurchase` — `{ userCommand: "the user's original request", aiReasoning: "why this purchase fulfills it" }`
   - This issues a single-use virtual card and charges the user's card on file for the total amount.
   - Treat the returned card as single-use and intended for one authorization only.
   - Do not request payment details until you have the complete total — the user's card is charged at this point.

5. Complete checkout.
   - Enter the returned card number, expiry, CVV, and **billing address** to finalize payment.
   - Always use the billing address returned by `get_payment_details` — not the user's shipping address. These are different. Verify the billing fields match before submitting.
   - Do not store or reuse card details outside the active checkout flow.

6. Record the receipt.
   - After a successful purchase, call `create_receipt` with the transaction ID and accurate purchase facts.
   - Do not include hidden chain-of-thought, internal reasoning, secrets, tokens, or unrelated context.

   **Items**: For each item include:
   - `imageUrl` — product image URL (see `references/enrichment.md` for how to find these reliably)
   - `url` — link to the product page
   - `description` — short variant info (size, color, etc.)

   **Order confirmation**: Include `orderConfirmationUrl` with the merchant's order confirmation page URL and `orderNumber` with the confirmation number.

   **Audit trail**: Provide categorized `steps`. Each step has a `category`, an `action` (short title), and optional `detail` (extra context).

   Categories:
   - `request_initiated` — what the user asked for, product identification
   - `purchase_in_progress` — checkout steps (shipping, tax, etc.)
   - `approval_required` — if user approval was needed via Axiom
   - `purchase_complete` — payment and order confirmation
   - `receipt_created` — final receipt attachment

   Example steps for a typical purchase:
   ```
   { category: "request_initiated", action: "User requested item", detail: "I want this in size medium https://shop.example.com/product" }
   { category: "request_initiated", action: "Product identified", detail: "Heavyweight Tee - Jet Black at $25.00 (flash sale, regular $35)" }
   { category: "purchase_in_progress", action: "Size confirmed in stock" }
   { category: "purchase_in_progress", action: "Shipping address entered", detail: "123 Main St, McLean VA 22101" }
   { category: "purchase_in_progress", action: "Shipping method selected", detail: "Standard Shipping (2-4 Business Days) at $6.57" }
   { category: "purchase_in_progress", action: "Tax calculated", detail: "VA Tax $1.51" }
   { category: "purchase_in_progress", action: "Final total", detail: "$33.08" }
   { category: "purchase_complete", action: "Payment completed", detail: "Axiom virtual card" }
   { category: "purchase_complete", action: "Order confirmed", detail: "Order #7XC9R4NGX" }
   { category: "receipt_created", action: "Receipt attached" }
   ```

## Safety and behavior rules

- Always verify a payment method is on file before requesting payment details.
- Never claim a purchase succeeded unless checkout actually completed.
- If spending rules, approval requirements, or policy checks block the purchase, stop and tell the user what happened.
- Never bypass approval flows.
- Never expose OAuth tokens, session details, cookies, or browser state.
- Never include internal reasoning in receipts or any external system.
- Never fabricate merchant, amount, tax, shipping, or transaction details.

## Troubleshooting

### `mcporter` not found or outdated
`mcporter` ≥0.8.0 must be installed and available on PATH. Check with `mcporter --version`. OpenClaw checks required binaries at skill load time.

### Auth expired or failed
Retry:

```bash
mcporter auth https://mcp.useaxiom.ai/mcp
```

### Cross-device approval timed out
Start a fresh auth flow and send the new approval link or activation code.

### No payment method on file
Tell the user to add a card in their Axiom account settings and stop.

### Card declined
Tell the user their card was declined and suggest they check their card details or try a different card.

### Spending rules blocked the transaction
Tell the user Axiom's rules prevented the purchase and do not retry blindly.
