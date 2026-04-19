# Deposit — Fund the Wallet with USDC

Request a USDC deposit into the agent's wallet. Generates an approval URL where the user can deposit funds. If the wallet isn't configured yet, this command bundles setup automatically.

## Command

```bash
lobstercash crypto deposit --amount <amount> --description "<desc>"
```

## When to use

- The user wants to add funds or top up their wallet
- Balance is insufficient for a crypto operation (`crypto send`, `crypto x402 fetch`, `crypto tx`)
- The wallet isn't configured and the user needs crypto (not card) — this bundles setup + deposit in one step

## What you need before running

- `amount`: how much USDC to deposit (e.g. `25.00`)
- `description`: what the agent will spend the funds on — derived from the user's task, not generic filler. Good: `"Pay for 3 Exa searches on competitor pricing"`. Bad: `"Top up wallet"`, `"Fund wallet for API calls"`.

Calculate the amount based on what the user needs. If topping up for a specific operation, use: `needed amount - current balance`.

Always check balance first with `lobstercash crypto balance` to know the current state.

## Reading the output

The output contains:

- `agentId`: the agent this deposit is for
- `amount`: the requested deposit amount in USDC
- `description`: what the deposit is for
- `approvalUrl`: the URL the user must open to deposit
- `setupSessionId`: present if wallet setup was bundled (first-time use)

## After running

Show the approval URL to the user:

> To deposit $[amount] USDC, open this link:
>
> [approvalUrl]
>
> Come back here when you've completed the deposit.

Do not proceed until the user confirms they have deposited.

## After user confirms

Run `lobstercash status` to verify the deposit landed and the wallet is ready. Then proceed with the user's original task (`crypto send`, `crypto x402 fetch`, etc.).

## Gotchas

- If the wallet isn't configured, setup is bundled automatically — do not run `lobstercash setup` first
- Only needed for crypto operations — virtual cards (`cards request`) don't require USDC, so don't use this when `paymentMethods` includes `card`
- Always check balance first (`lobstercash crypto balance`) — know the current state before requesting
- Write operation — do not retry automatically or if the user declines
