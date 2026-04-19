# MagicPay Boundaries

## What This Skill Owns

- Attach to a prepared browser page.
- Start or continue the workflow session for that page.
- Discover the supported protected form.
- Resolve protected form targets through MagicPay request paths and fill them
  safely.
- Run protected capabilities through `run-action`.
- Retry submit only when the guarded fill path explicitly leaves work undone.

## Readiness Rules

- Use `magicpay status` before a new protected-form task.
- If `status` reports a missing or invalid API key, run `magicpay init`.
- If `status` reports `cliUpdate`, use only
  `npm i -g @mercuryo-ai/magicpay-cli@latest`, then rerun `status`.
- Use `doctor` only when local config still looks broken after `init`.

## Protected-Form Rules

- Start from a current `find-form` result, not from stale assumptions.
- Do not call `resolve-form` on a stale `fillRef`.
- Use `--item-ref` only when you intentionally want one specific vault item.
- Treat `submit-form` as manual recovery, not as the default next step.
- If `resolve-form` reports stale bindings or no live submit control, refresh
  the page state before retrying.

## Protected-Action Rules

- Start `run-action` only when an active workflow session exists.
- Provide structured JSON params to `run-action`; do not smuggle protected
  values through ad-hoc strings or prompts.
- Use `run-action` for protected capabilities instead of inventing a manual
  form-fill equivalent.

## Secrecy And Safety

- Never type, print, summarize, or log protected values manually.
- Base progress claims on the visible form state.
- After page-level changes, rerun `find-form` before acting on old bindings.

## Ask The User When

- the prepared page context is missing;
- the form remains ambiguous;
- approval reaches a terminal blocked state;
- client-side validation or merchant-specific recovery needs a human choice.
