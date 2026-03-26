# google-stitch-workflow

Public OpenClaw skill bundle for disciplined use of Google Stitch.

## Positioning

This bundle is intentionally MCP-first.
It distinguishes between:

- what has been verified through the MCP surface
- what exists only in the Stitch browser product
- what may be useful as an optional local workflow convention

## What is included

- `SKILL.md`
  Main operating instructions.
- `references/prompt-structuring.md`
  Supporting reference for prompt shaping and prompt repair.
- `CHANGELOG.md`
  Version notes for publication.

## Intended use

This bundle is for agents and users who want a reliable Stitch workflow:

- clear boundary between MCP and browser-only capabilities
- strong parameter discipline
- practical redesign workflows
- optional local conventions for aliases, artifacts, and revision tracking

## Publishing notes

This folder is structured as a ClawHub skill bundle.

Typical publish command:

```bash
clawhub publish ./google-stitch-workflow --slug google-stitch-workflow --name "Google Stitch Workflow" --version 1.0.0 --tags latest
```

## License

This bundle is released under the MIT License. See [`LICENSE`](./LICENSE).
