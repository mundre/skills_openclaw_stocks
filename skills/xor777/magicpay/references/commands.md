# MagicPay Command Guide

## Setup And Readiness

### `magicpay init <apiKey> [--api-url <url>]`

Save the API key to `~/.magicpay/config.json`. When `--api-url` is provided,
`init` also stores the gateway base URL there.

### `magicpay status`

Check CLI health, authenticated identity, and update state. Use this as the
normal preflight command before a protected-form task.

### `magicpay doctor`

Inspect the local config file when `status` still fails after `init`.

### `magicpay --version`

Print the installed CLI version.

## Browser Attach And Session Control

### `magicpay attach <cdp-url> [--provider <name>]`

Connect MagicPay to an already running browser through CDP.

### `magicpay start-session [name] [--merchant-name <name>]`

Bind the attached browser to a MagicPay workflow session.

### `magicpay end-session`

Complete the active workflow session without closing the browser.

## Protected-Form Flow

### `magicpay find-form [--purpose <auto|login|identity|payment_card>]`

Discover the supported protected form on the current page and return the
current protected-form contract.

### `magicpay resolve-form <fillRef> [--item-ref <vaultItemId>] [--no-submit]`

Resolve one protected form target through MagicPay. The CLI creates the
request, waits for the result, fills the target, and auto-submits when a safe
form-bound submit control is still live. Use `--item-ref` to pin one vault
item instead of letting MagicPay choose from the available candidates. Use
`--no-submit` when you want the filled result without the guarded auto-submit.

### `magicpay resolve-fields <targetRef...> [--refresh-snapshot]`

Match one or more observed non-secret target refs against the session-local
open-data snapshot (name, email, phone, locale, date of birth, address, and
similar reusable public facts). Returns `matched`, `ambiguous`, or `no_match`
per target. Targets already owned by the protected lane stay excluded. The
target refs come from the companion browser tool's latest observation. In
orchestration, auto-fill only `matched` results — never invent values for
`ambiguous` or `no_match`. Pass `--refresh-snapshot` to force a re-fetch of
the snapshot from the MagicPay service.

### `magicpay run-action <capability> [--item-ref <vaultItemId>] --params-json <json>`

Run a protected capability through the same MagicPay request model. This is
the canonical path for capabilities such as confirmation, provider-backed
authorization, or other protected actions that are not direct form fills.

### `magicpay submit-form <fillRef>`

Manually submit the current protected form when `resolve-form` explicitly
leaves submission unfinished or when you intentionally retry on a fresh
protected-form snapshot.
