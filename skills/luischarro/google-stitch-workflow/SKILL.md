---
name: google-stitch-workflow
description: Use when working with Google Stitch through a disciplined MCP-first workflow. Prefer this skill for project inspection, controlled screen generation and editing, prompt structuring, and failure recovery.
---

# Google Stitch Workflow

Use Google Stitch as a design exploration and screen-iteration system, not as a production implementation tool.

This skill separates three concerns that are often conflated:

- verified MCP capabilities in the current environment
- browser-only Stitch product features
- optional local workflow conventions that improve traceability

## When to use this skill

Use this skill when the task involves one or more of these goals:

- inspect Stitch projects and screens before making changes
- generate a new screen from a text prompt
- refine an existing generated screen with small, controlled edits
- organize a multi-screen redesign effort without losing revision history
- convert vague design requests into structured prompts

Do not assume the browser UI, the public product marketing, and the MCP surface expose the same operations.

## Design principles

- prefer verified MCP behavior over product-level assumptions
- use Stitch for exploration and iteration, not implementation
- keep prompts narrow, explicit, and preservation-oriented
- treat local workflow enhancements as optional conventions

## Read only what you need

- Prompt reference: [`references/prompt-structuring.md`](./references/prompt-structuring.md)
- Keep the main skill focused on operating rules. Use the prompt reference only when the request needs prompt shaping or prompt repair.

## Operating model

Stitch is most reliable when treated as an iterative design system:

1. inspect the current project and target screen
2. generate or edit one screen at a time
3. review the visual output immediately
4. preserve what must stay stable
5. move to code only after the screen direction is coherent

Avoid using Stitch as if it were a deterministic code generator or a full-product planner in a single prompt.

## Capability boundaries

### Verified MCP capabilities

These tools have been validated in live use and are the default safe surface:

- `list_projects`
- `get_project`
- `list_screens`
- `get_screen`
- `create_project`
- `generate_screen_from_text`
- `edit_screens`

### Known weak or unverified areas

Treat these as unstable until revalidated in the active environment:

- `generate_variants`
- screenshot-driven redesign through MCP
- prototype creation through MCP
- browser-style canvas operations beyond basic project and screen inspection

### Browser-only product features

The Stitch web product may expose richer flows such as:

- image or screenshot redesign
- prototype-oriented workflows
- broader canvas interactions
- newer browser-facing product features

Do not infer that MCP can perform those actions directly.

## Parameter discipline

The MCP surface is parameter-sensitive. Incorrect casing or identifier shape can produce generic invalid-argument failures.

### `deviceType`

Use uppercase enum values when explicitly setting a device:

- `"MOBILE"`
- `"DESKTOP"`

If uncertain, omit the parameter instead of guessing.

### `modelId`

Use only verified model identifiers for direct MCP calls in the current environment.

Known working values from live testing:

- `"GEMINI_3_FLASH"`
- `"GEMINI_3_PRO"`

If a local wrapper maps model names differently, treat that as wrapper-specific behavior, not as a direct MCP guarantee.

### `selectedScreenIds`

For `edit_screens`, pass bare screen IDs rather than full resource names.

Example:

```json
{
  "projectId": "15190935684505273965",
  "selectedScreenIds": ["69b3228b6c5f4b9f9efceea4b6a30168"],
  "deviceType": "MOBILE",
  "prompt": "Make the primary button darker and add a small secondary text link below it."
}
```

## Recommended workflows

### Workflow A: inspect before editing

Before any edit:

- inspect the project
- inspect the target screen
- verify whether the screen is actually generated content

Practical heuristic:

- if `htmlCode` exists, the screen is more likely to be safely editable
- if the target is only an uploaded image or reference asset, do not assume `edit_screens` will behave well

### Workflow B: generate first, then refine

For new directions:

1. create or choose the right project
2. generate a first screen with the minimum safe parameter set
3. review output quality
4. move to small edits rather than repeating large generation prompts

Default safe starting point:

- `projectId`
- a short, structured prompt

Then add:

- `deviceType: "MOBILE"` or `"DESKTOP"` if needed
- `modelId` only when there is a reason to choose one

Recommended model usage:

- use `"GEMINI_3_FLASH"` for faster exploratory passes
- use `"GEMINI_3_PRO"` when the direction is already clear and quality matters more than latency

### Workflow C: full-app redesign

For an existing product redesign:

1. create a dedicated Stitch project
2. define the main screen families
3. generate one canonical screen per family
4. refine those canonical screens with preservation-first prompts
5. only then add alternate states and edge cases
6. move to code after the family set is coherent

This is slower than opportunistic one-off generation, but it reduces design drift.

### Workflow D: reference-driven redesign

When redesigning a real app:

- gather reliable reference captures first
- work one screen family at a time
- name the relevant reference images explicitly in the prompt
- treat those references as the source of truth for current structure

Good pattern:

```text
Use the uploaded real app references in this project.
The relevant images are named today_top.png, today_day_actions.png, and today_meals_mid.png.
Those images show what exists now.
Keep the real structure and improve only hierarchy, spacing, and polish.
Do not invent new sections.
```

## Optional local workflow enhancements

These conventions are useful, but they are not native Stitch capabilities. Treat them as local workflow layers.

### Screen aliases

Use human-readable identifiers for screens when the project grows beyond a few artifacts.

Benefits:

- easier collaboration
- easier revision tracking
- lower dependence on opaque screen IDs

### Execution artifacts

Store local outputs for each operation in a dedicated run directory.

Recommended contents:

- prompt used
- project and screen identifiers
- downloaded HTML if available
- downloaded preview image if available
- timestamp

### Operation history

Maintain a chronological local log of design operations and alias changes.

This is useful for:

- traceability
- recovery
- auditability of screen evolution

### Screen derivation history

Track parent-child relationships between generated, edited, and variant-derived screens.

### Last-active-screen state

Keep a small local state file that records the latest project and screen used.

Use it to reduce needless ID lookup, but never let it override explicit user intent.

## Session discipline

- inspect before editing
- review the returned screen before issuing another large prompt
- prefer one short generation followed by controlled edits
- stop repeating the same failing payload
- move to code only after the screen family is coherent

## Failure handling

### `Request contains an invalid argument.`

Check in this order:

1. `deviceType` casing
2. `modelId` spelling
3. `selectedScreenIds` shape
4. whether the screen is genuinely editable generated output
5. whether the prompt is trying to change too much at once

Do not brute-force retries with the same payload.

### Generation or edit timeout

Long-running operations may time out even when Stitch completes them asynchronously.

Safe reconciliation pattern:

1. do not immediately resend the same request
2. re-check `list_screens`
3. inspect whether a new screen appeared
4. retry only if no result landed

### Incomplete or lagging screen lists

`list_screens` may lag behind a successful operation.

If the originating call indicated success, re-check before retrying. Do not assume immediate list lag means failure.

## Review gate before code translation

Do not port a Stitch output into code until these conditions are true:

- required elements are still present
- the primary user task is clearer than before
- mobile density and hierarchy are acceptable
- the screen fits the rest of the project direction
- the design can be implemented coherently in the current application architecture

If the answer is not clearly yes, keep iterating in Stitch.

## Naming guidance for larger projects

If the project will contain many screens, use stable ordered titles from the start.

Recommended pattern:

- `01 Onboarding - Welcome`
- `02 Onboarding - Personal Info`
- `10 Today - Main`
- `20 Progress - Overview`
- `30 History - Browse`
- `40 Settings - Profile`

This improves canvas scanning and reduces later cleanup.

## Practical defaults

- start with the smallest prompt that can produce a useful screen
- prefer one short generation followed by tiny edits
- preserve explicitly during redesign work
- inspect before editing
- treat wrapper enhancements as optional, not as part of the Stitch contract

## Not recommended

- copying browser-product claims into MCP instructions without revalidation
- treating `generate_variants` as fully dependable unless the current environment has confirmed it
- using design boards or mood boards as substitutes for real app screens in a product redesign
- attempting to redesign a whole app from memory in a single prompt
- moving into implementation code before the design family is coherent
