# Release Gates

Use this reference before any public GitHub or ClawHub publication step.

## Public surface rule

ClawHub is public. Published skills and their `SKILL.md` content are visible to
everyone.

Source:
- https://docs.openclaw.ai/tools/clawhub

## The bundle must fail closed on

- placeholder text such as `TODO`, `TBD`, `replace me`, or sample URLs
- absolute local paths such as `/Users/...`, `/home/...`, or `C:\Users\...`
- loopback or debugging endpoints such as `localhost`, `127.0.0.1`, `ws://`,
  `wss://`, or `devtools/browser`
- secret-shaped strings such as API keys, GitHub personal access tokens, or
  inline passwords
- known Drive file IDs copied from the project manifests
- drift between the public skill copy and the bundled plugin copy

## Required command

- `python3 scripts/check_publication_bundle.py`

Do not publish if that script exits non-zero.
