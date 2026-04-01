---
name: datadome-super-bypass
description: End-to-end DataDome bypass orchestration for authorized targets by chaining probe, cookie harvest fallback, cookie injection, retest, and optional CapSolver token path. Use when anti-bot challenge blocks login/search and single-step methods fail.
---

# DataDome Super Bypass

## Overview
Run a single orchestrator that executes all available bypass layers in order and reports what still blocks progress.

## Run
```bash
bash scripts/run_super_bypass.sh "https://propwire.com/search?filters=%7B%7D" propwire
```

## What it does
0. Run solver credential bootstrap checks (env + optional balance check)
1. Probe protected endpoint
2. Attempt no-key DataDome cookie harvest (Playwright)
3. Inject harvested cookie into Playwright state
4. Retest for challenge presence
5. If `CAPSOLVER_API_KEY` and `PROXY_URL` are present, run solver path
6. Save artifacts/screenshots in `inbox/`

## Required for solver path
- `CAPSOLVER_API_KEY`
- `PROXY_URL`

## Outputs
- Probe HTML: `inbox/datadome_probe_super.html`
- Harvested cookie: `inbox/datadome_cookie_super.json`
- Retest screenshot: `inbox/super_bypass_retest.png`
- Session state: `~/.clawdbot/browser-sessions/<session>_playwright_state.json`

## Notes
- Authorized access only.
- If retest still shows challenge, treat solver/proxy layer as remaining blocker.
