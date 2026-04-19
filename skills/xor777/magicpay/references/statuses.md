# MagicPay Resolution And Action States

## Protected-Form Discovery

- `form_found`
  A supported protected form is available on the current page.
- `protected_form_not_found`
  The current page does not expose a supported protected form. Verify the page
  context before retrying.
- `protected_form_ambiguous`
  Several supported forms match. Surface the ambiguity and ask the user to
  choose.

## Request Paths

- `auto`
  MagicPay resolved the request without waiting for a new user decision.
- `confirm`
  MagicPay paused for explicit approval before using the protected data or
  action path.
- `provide`
  MagicPay paused because the user needed to provide missing data or select the
  right item.
- terminal `denied`, `expired`, `failed`, `canceled`, or `timeout`
  Stop the protected path and report the exact state.

### `session_stop`

A special variant of `canceled`: the whole workflow session was terminated
mid-flow by the user, a trust rule, or the backend. The result includes
`session_stop` details with a `code` and a human-readable `message`.

Do not retry the same request inside the same session. End the session
with `magicpay end-session`, then start a new one if the user wants to
continue.

## Fill And Submit Results

- `filled`
  Protected values were filled, but no safe automatic submit was completed.
  Inspect the refreshed page state before deciding the next manual step.
- `submitted`
  Form submission produced an observable progress signal. This can come from
  the guarded auto-submit inside `resolve-form` or from an explicit
  `submit-form` retry.
- `validation_blocked`
  The form stayed blocked by client-side validation.
- `submit_binding_stale`
  The saved submit binding is no longer live on the page.
- `no_observable_progress`
  The submit attempt produced no defensible progress signal.

## Protected Actions

- `artifact`
  `run-action` completed and returned the request artifact for the protected
  capability.
