---
name: mova-supply-chain-risk
description: Screen suppliers against sanctions lists, PEP registries, ESG ratings, and financial stability data via MOVA HITL, then route findings through a human procurement decision gate. Trigger when the user provides a supplier list, asks to screen vendors, or requests a supply chain due diligence report. Mandatory human sign-off before any procurement decision.
license: MIT-0
metadata: {"openclaw":{"plugin":{"name":"MOVA","installCmd":"openclaw plugins install openclaw-mova"},"dataSentToExternalServices":[{"service":"MOVA API (api.mova-lab.eu)","data":"supplier names, IDs, country of registration, procurement category, AI risk bands, human decision, audit metadata"},{"service":"Sanctions & PEP screening connector (read-only)","data":"supplier name and country screened against OFAC, EU, UN lists and PEP registries"},{"service":"ESG ratings connector (read-only)","data":"supplier ID for ESG score and adverse media lookup"},{"service":"Company registry connector (read-only)","data":"supplier name and country for registration status and financial stability check"}]}}
---

# MOVA Supply Chain Risk Analysis

Screen your supplier list against sanctions registries, PEP databases, ESG ratings, and financial stability indicators — with a per-supplier risk band, source citations, and a mandatory human procurement decision gate backed by a tamper-proof audit trail.

## What it does

1. **Supplier ingestion** — accepts a list of supplier names, IDs, countries, and procurement category
2. **Multi-source screening** — OFAC / EU / UN sanctions, PEP registries, ESG ratings, adverse media, financial stability
3. **Risk report** — per-supplier risk band (low / medium / high / critical) with source citations and finding details
4. **Human gate** — procurement manager reviews findings and chooses: approve all / approve clean only / reject all / escalate
5. **Audit receipt** — all data sources, query timestamps, screening results, and the human decision are logged for supply chain transparency audits

**Mandatory escalation rules enforced by policy:**
- Sanctions hit on any supplier → immediate escalation, cannot approve batch
- Critical risk band (≥ 2 suppliers) → mandatory escalation to compliance team
- PEP flag with procurement value above threshold → escalate required

## Requirements

**Plugin:** MOVA OpenClaw plugin must be installed in your OpenClaw workspace.

**Data flows:**
- Supplier data + procurement category → `api.mova-lab.eu` (MOVA platform, EU-hosted)
- Supplier names/countries → sanctions & PEP screening (OFAC, EU, UN — read-only)
- Supplier IDs → ESG ratings and adverse media lookup (read-only)
- Supplier name/country → company registry and financial stability check (read-only)
- Audit journal → MOVA R2 storage, signed
- No data stored locally or sent to third parties beyond the above

## Demo

**Step 1 — Supplier batch submitted with screening request**
![Step 1](screenshots/01-input.jpg)

**Step 2 — AI screening: sanctions hit on SUP-002, ESG risk on SUP-003, mandatory escalation triggered**
![Step 2](screenshots/02-analysis.jpg)

**Step 3 — Audit receipt + signed decision log**
![Step 3](screenshots/03-audit.jpg)

## Quick start

Say "screen these suppliers for procurement" and provide:

```
suppliers:
  - id: SUP-001, name: Acme GmbH, country: DE
  - id: SUP-002, name: Delta LLC, country: US
category: raw_materials
requestor_id: EMP-2201
```

The agent submits the batch, shows the per-supplier risk report with sanctions and ESG findings, then asks for your procurement decision.

## Why contract execution matters

- **Sanctions rules are policy, not prompts** — any sanctions hit triggers mandatory escalation that cannot be bypassed
- **Multi-source traceability** — every finding is tagged with its source (OFAC / EU / UN / ESG / registry)
- **Immutable audit trail** — when a compliance officer or regulator asks "who cleared supplier SUP-002 and why?" — the answer is in the system
- **EU Supply Chain Due Diligence / OFAC ready** — procurement decisions require documented screening history, source citations, and human sign-off

## What the user receives

| Output | Description |
|--------|-------------|
| Suppliers screened | Total count in batch |
| Critical / high / medium / low | Count per risk band |
| Per-supplier risk band | low / medium / high / critical |
| Sanctions result | OFAC / EU / UN hit or clear with match details |
| PEP flag | PEP status and category |
| ESG score | Rating and adverse media flags |
| Financial stability | Registration status, insolvency signals |
| Findings | Per-supplier structured list with source and severity |
| Recommended action | AI-suggested decision |
| Decision options | approve_all / approve_clean / reject_all / escalate |
| Audit receipt ID | Permanent signed record of the procurement decision |
| Compact journal | Full event log: screening → risk report → human decision |

## When to trigger

Activate when the user:
- Provides a supplier list (names, IDs, or CSV)
- Says "screen these vendors", "run supply chain check", "due diligence on supplier"
- Asks to prepare a procurement risk report before signing contracts

**Before starting**, confirm: "Screen [COUNT] suppliers for MOVA supply chain risk analysis?"

If supplier data is missing — ask once for: supplier names/IDs, country of registration, procurement category.

## Step 1 — Submit supplier list for screening

Call tool `mova_hitl_start_supply_chain` with:
- `suppliers`: array of objects with `id`, `name`, `country` (ISO 3166-1 alpha-2)
- `category`: raw_materials / logistics / technology / services
- `requestor_id`: employee ID of the procurement requestor

## Step 2 — Show risk report and decision options

If `status = "waiting_human"` — show the screening summary:

```
Suppliers screened: COUNT
Critical:           CRITICAL_COUNT
High risk:          HIGH_COUNT
Clean:              CLEAN_COUNT

[Per-supplier table: ID | Name | Country | Risk band | Top finding]
Recommended action: ACTION ← RECOMMENDED
```

| Option | Description |
|---|---|
| `approve_all` | Approve all screened suppliers |
| `approve_clean` | Approve only clean suppliers, block high-risk |
| `reject_all` | Block entire batch pending further review |
| `escalate` | Escalate to compliance team |

Call tool `mova_hitl_decide` with:
- `contract_id`: from the response above — this is `ctr-scr-xxxxxxxx`, NOT a supplier ID
- `option`: chosen decision
- `reason`: procurement manager reasoning (required for reject_all and escalate)

## Step 3 — Show audit receipt

Call tool `mova_hitl_audit` with `contract_id`.
Call tool `mova_hitl_audit_compact` with `contract_id` for the full signed screening chain.

## Connect your real screening systems

By default MOVA uses a sandbox mock. To route checks against your live infrastructure, call `mova_list_connectors` with `keyword: "supply"`.

Relevant connectors:

| Connector ID | What it covers |
|---|---|
| `connector.screening.pep_sanctions_v1` | PEP & sanctions screening (OFAC, EU, UN) |
| `connector.esg.ratings_v1` | ESG ratings and adverse media |
| `connector.data.company_registry_v1` | Company registration status |
| `connector.data.company_enrichment_v1` | Financial stability and enrichment data |

Call `mova_register_connector` with `connector_id`, `endpoint`, optional `auth_header` and `auth_value`.

## Rules

- NEVER make HTTP requests manually
- NEVER invent or simulate screening results — if a tool call fails, show the exact error
- Use MOVA plugin tools directly — do NOT use exec or shell
- CONTRACT_ID is `ctr-scr-xxxxxxxx` from the mova_hitl_start_supply_chain response — NOT a supplier ID
