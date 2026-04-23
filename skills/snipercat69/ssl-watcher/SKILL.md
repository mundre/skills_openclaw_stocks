# SSL & Domain Expiry Watcher

**Skill Name:** `ssl-watcher`  
**Version:** `1.1.0`  
**Category:** Security / Monitoring  
**Price:** Free (v1) / $9 Pro / $39 Bundle  
**Author:** EdgeIQ Labs  
**OpenClaw Compatible:** Yes — Python 3, pure stdlib + socket, WSL + Windows

---

## What It Does

Monitors SSL certificate health and domain expiry dates for your web properties. Catch expired certs, misconfigured chains, and domains about to lapse before they become emergencies.

> ⚠️ **Legal Notice:** Only monitor domains you own or have explicit written permission to audit. Unauthorized recon is illegal.

---

## Features

- **SSL Certificate Check** — issuer, validity window, chain completeness, protocol versions, cipher strength
- **Domain Expiry Check** — WHOIS registration and expiration data via socket lookup
- **Days-to-Expiry Alerting** — configurable warning thresholds (30/14/7/3 days)
- **Batch Monitoring** — check multiple domains in one run
- **Silent Mode** — full report, no stdout noise unless issues found
- **Pure Python** — no external dependencies beyond stdlib + socket

---

## Installation

```bash
cp -r /home/guy/.openclaw/workspace/apps/ssl-watcher ~/.openclaw/skills/ssl-watcher
```

---

## Usage

### Check SSL for a Domain

```bash
python3 ssl_watcher.py --domain example.com
```

### Check Multiple Domains

```bash
python3 ssl_watcher.py --domains example.com store.example.com api.example.com
```

### With Expiry Threshold Alerts

```bash
python3 ssl_watcher.py --domain example.com --warn-days 30
```

### Full Report (all details)

```bash
python3 ssl_watcher.py --domain example.com --verbose
```

### As OpenClaw Discord Command

In `#edgeiq-support` channel:
```
!ssl example.com
!ssl example.com store.example.com api.example.com
!ssl example.com --warn-days 14
!domain example.com
```

---

## Parameters

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--domain` | string | — | Single domain to check |
| `--domains` | list | — | Multiple domains to check (space-separated) |
| `--warn-days` | int | 30 | Alert if cert/domain expires within this many days |
| `--verbose` | flag | False | Show full chain and protocol details |
| `--check-http` | flag | False | Also verify site is reachable over HTTPS |
| `--output` | string | — | Write JSON report to file |

---

## Output Example

```
=== SSL Watcher Report ===
example.com
  Status:      ✔ Valid
  Issuer:       Let's Encrypt
  Valid From:  2026-01-15
  Expires:     2026-04-15
  Days Left:   23  ⚠ WARN
  Chain:       complete
  Protocols:   TLS 1.2, TLS 1.3

store.example.com
  Status:      ✔ Valid
  Issuer:      GlobalSign
  Expires:     2026-07-20
  Days Left:   120
```

---

## Tier Comparison

| Feature | Free | Pro ($9/mo) | Bundle ($39/mo) |
|---------|------|-------------|-----------------|
| Single domain check | ✅ | ✅ | ✅ |
| Multiple domains | — | ✅ (up to 10) | ✅ (unlimited) |
| WHOIS expiry data | — | ✅ | ✅ |
| Expiry warning thresholds | — | ✅ | ✅ |
| JSON report export | — | ✅ | ✅ |
| Weekly automated scan | — | — | ✅ |
| Email alert on expiry | — | — | ✅ |

---

## Pro Upgrade

Add Pro to monitor up to 10 domains with WHOIS data, configurable warning thresholds, and JSON export:

👉 [Upgrade to Pro — $9/mo](https://buy.stripe.com/7sYaEZeCn5934nW8AE7wA01)

## Bundle Deal

Get everything — unlimited domains, weekly automated scans, and email alerts — in the EdgeIQ Bundle:

👉 [Get the Bundle — $39/mo](https://buy.stripe.com/aFabJ3am79pjg6E18c7wA02)

---

## Support

Need a custom check or bulk monitoring? Open a ticket in [#edgeiq-support](https://discord.gg/PaP7nsFUJT) or email [gpalmieri21@gmail.com](mailto:gpalmieri21@gmail.com).