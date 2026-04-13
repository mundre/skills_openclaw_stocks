---
name: node-connect
description: Diagnose OpenClaw node connection and pairing failures for Android, iOS, and macOS companion apps. Use when QR/setup code/manual connect fails, local Wi-Fi works but VPS/tailnet does not, or errors mention pairing required, unauthorized, bootstrap token invalid or expired, gateway.bind, gateway.remote.url, Tailscale, or plugins.entries.device-pair.config.publicUrl.
---

# Node Connect

Goal: find the one real route from node -> gateway, verify OpenClaw is advertising that route, then fix pairing/auth.

## Instructions

## Step 0: topology gate

Classify the intended route before executing any command. If the route is unclear, ask at most two short questions:

1. Same device, emulator, or USB tunnel? → `same machine`
2. Same local Wi-Fi / LAN? → `same LAN`
3. Same Tailscale tailnet? → `same Tailscale tailnet`
4. Public URL or reverse proxy? → `public URL / reverse proxy`

If the route is still ambiguous after two questions, stop and ask for:

- the intended topology
- whether they used QR/setup code or manual host/port
- the exact app text/status/error, quoted exactly if possible
- whether `openclaw devices list` shows a pending pairing request

Do not guess from `can't connect`.
Do not mix topologies.

- Local Wi-Fi problem: do not switch to Tailscale unless remote access is actually needed.
- VPS / remote gateway problem: do not keep debugging `localhost` or LAN IPs.

## Canonical checks

Prefer `openclaw qr --json`. It uses the same setup-code payload Android scans.

## Execution order

⚠️ Sequential execution only. Do not run primary checks, extra route/auth checks, or fallback commands until the numbered steps explicitly branch to them. Never run commands speculatively.

1. Confirm the intended topology first.
2. Run `openclaw qr --json` first. If this OpenClaw instance points at a remote gateway, run `openclaw qr --remote --json` instead.
3. Read `gatewayUrl` and `urlSource` from that output.
4. Match `urlSource` against the route map below.
5. Only then run extra config checks if the advertised route does not match the intended topology, or if the JSON output is missing the fields you need.

Primary checks:

```bash
openclaw qr --json
openclaw devices list
openclaw nodes status
```

Extra route/auth checks when needed:

```bash
openclaw config get gateway.mode
openclaw config get gateway.bind
openclaw config get gateway.tailscale.mode
openclaw config get gateway.remote.url
openclaw config get gateway.auth.mode
openclaw config get gateway.auth.allowTailscale
openclaw config get plugins.entries.device-pair.config.publicUrl
```

If this OpenClaw instance is pointed at a remote gateway, also run:

```bash
openclaw qr --remote --json
```

If Tailscale is part of the story:

```bash
tailscale status --json
```

## Read the result, not guesses

`openclaw qr --json` success means:

- `gatewayUrl`: this is the actual endpoint the app should use.
- `urlSource`: this tells you which config path won.

## Route map

Match the `urlSource` value against the rows below. Keep the match case-sensitive, but ignore surrounding whitespace. If no row matches, treat the route as unknown and run the fallback checks immediately.

| `urlSource` (case-sensitive match, ignore surrounding whitespace) | Expected topology | If that does not match the intended route |
| --- | --- | --- |
| `gateway.bind=lan` | same Wi-Fi / LAN | keep the diagnosis on LAN; do not switch to Tailscale or public URL unless remote access is actually required |
| `gateway.bind=tailnet` | same Tailscale tailnet | verify the gateway host is actually on Tailscale |
| `gateway.tailscale.mode=serve` | Tailscale route | verify Tailscale Serve is the intended route; do not debug LAN IPs first |
| `gateway.tailscale.mode=funnel` | Tailscale route | verify Tailscale Funnel is the intended route; do not debug LAN IPs first |
| `plugins.entries.device-pair.config.publicUrl` | public URL / reverse proxy | inspect the public URL / proxy path, not LAN-only config |
| `gateway.remote.url` | remote gateway route | inspect the remote gateway route, not local bind settings |
| loopback-only result such as `127.0.0.1`, `localhost`, or `Gateway is only bound to loopback` | wrong for any remote device | fix the route first, then generate a fresh setup code |

If `openclaw qr --json` is malformed, missing `urlSource`, or missing the route you need, fall back to:

```bash
openclaw config get gateway.bind
openclaw config get gateway.tailscale.mode
openclaw config get plugins.entries.device-pair.config.publicUrl
openclaw config get gateway.remote.url
```

Then identify the effective route manually and return to the route map.

## Root-cause map

If `openclaw qr --json` says `Gateway is only bound to loopback`:

- remote node cannot connect yet
- fix the route, then generate a fresh setup code
- `gateway.bind=auto` is not enough if the effective QR route is still loopback
- same LAN: use `gateway.bind=lan`
- same tailnet: prefer `gateway.tailscale.mode=serve` or use `gateway.bind=tailnet`
- public internet: set a real `plugins.entries.device-pair.config.publicUrl` or `gateway.remote.url`

If `gateway.bind=tailnet set, but no tailnet IP was found`:

- gateway host is not actually on Tailscale

If `qr --remote requires gateway.remote.url`:

- remote-mode config is incomplete

If the app says `pairing required`:

- network route and auth worked
- approve the pending device

```bash
openclaw devices list
openclaw devices approve --latest
```

If the app says `bootstrap token invalid or expired`:

- old setup code
- generate a fresh one and rescan
- do this after any URL/auth fix too

If the app says `unauthorized`:

- wrong token/password, or wrong Tailscale expectation
- for Tailscale Serve, `gateway.auth.allowTailscale` must match the intended flow
- otherwise use explicit token/password

## Fast heuristics

- Same Wi-Fi setup + gateway advertises `127.0.0.1`, `localhost`, or loopback-only config: wrong.
- Remote setup + setup/manual uses private LAN IP: wrong.
- Tailnet setup + gateway advertises LAN IP instead of MagicDNS / tailnet route: wrong.
- Public URL set but QR still advertises something else: inspect `urlSource`; config is not what you think.
- `openclaw devices list` shows pending requests: stop changing network config and approve first.

## Fix style

Reply with one concrete diagnosis and one route.

If there is not enough signal yet, ask for setup + exact app text instead of guessing.

Good:

- `The gateway is still loopback-only, so a node on another network can never reach it. Enable Tailscale Serve, restart the gateway, run openclaw qr again, rescan, then approve the pending device pairing.`

Bad:

- `Maybe LAN, maybe Tailscale, maybe port forwarding, maybe public URL.`

## Hard stop & loop limit

- One fix, one verify only. Apply at most one targeted route or config fix. Re-run `openclaw qr --json` exactly once to verify.
- If `gatewayUrl` now matches the intended topology, stop network diagnosis. Tell the user to rescan and approve if pairing is pending.
- If `openclaw qr --json` still fails or still returns loopback after one fix, stop and request the full `openclaw qr --json` output plus `openclaw config get gateway.bind`.
- Do not attempt a second fix or iterate further.
- If the route matches and topology is confirmed, exit immediately. Do not run extra config checks.
