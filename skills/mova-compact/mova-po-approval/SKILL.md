---
name: mova-po-approval
description: Submit a purchase order for automated risk analysis and procurement approval via MOVA HITL. Trigger when the user mentions a PO number, asks to approve/review a purchase order, or says anything like "check this PO", "approve purchase order", "PO review", "procurement approval".
license: MIT-0
metadata: {"openclaw":{"plugin":{"name":"MOVA","installCmd":"openclaw plugins install openclaw-mova"},"dataSentToExternalServices":[{"service":"MOVA API (api.mova-lab.eu)","data":"PO ID, approver employee ID, AI analysis results, human decision, audit metadata"},{"service":"ERP connector (server-side, read-only)","data":"PO fields, vendor registry, budget data, authority matrix — accessed by MOVA runtime, not by the agent"}]}}
---

> **Contract Skill** — A ready-to-use MOVA HITL workflow. Requires the `openclaw-mova` plugin.

# MOVA Purchase Order Approval

Submit a purchase order to MOVA for automated risk analysis and a human decision gate — with a tamper-proof audit trail of every procurement decision.

## What it does

1. **Risk analysis** — AI checks vendor registry, budget utilisation, authority level, and detects split-PO fraud patterns
2. **Risk snapshot** — scores the PO (0.0–1.0) and surfaces anomaly flags
3. **Human decision gate** — procurement manager chooses: approve / hold / reject / escalate
4. **Audit receipt** — every decision is signed, timestamped, and stored in an immutable compact journal

## Requirements

**Plugin:** MOVA OpenClaw plugin must be installed in your OpenClaw workspace.

**ERP connector — no additional credentials required:**
Vendor registry, budget data, and authority matrix are fetched server-side by the MOVA runtime. The agent does not need separate ERP credentials.

**Data flows:**
- PO ID + approver ID → `api.mova-lab.eu` (MOVA platform, EU-hosted)
- ERP data (vendor/budget/authority) → fetched by MOVA runtime server-side, read-only, not stored
- Audit journal → MOVA R2 storage, signed
- No data sent to third parties beyond the above

## Quick start

Say "review PO-2026-004 with approver EMP-1042":

```
https://raw.githubusercontent.com/mova-compact/mova-bridge/main/test_po_PO-2026-004.png
```

The agent submits it to MOVA, shows the AI risk analysis with findings and anomaly flags, then asks for your procurement decision.

## Demo

**Step 1 — Task submitted with PO document**
![Step 1](screenshots/01-input.jpg)

**Step 2 — AI risk analysis: risk score 0.78, findings, escalate recommended**
![Step 2](screenshots/02-analysis.jpg)

**Step 3 — Audit receipt + compact journal**
![Step 3](screenshots/03-audit.jpg)

## Why contract execution matters

- **Split-PO fraud detection** — policy enforces escalation when the same vendor submits multiple POs within 72h to bypass approval thresholds
- **Authority enforcement** — the approver's authority level is validated against the authority matrix; inadequate authority always routes to escalation
- **Immutable audit trail** — the compact journal records every event with cryptographic proof
- **EU AI Act / DORA ready** — procurement decisions are high-risk financial actions requiring human oversight and full explainability

## What the user receives

| Output | Description |
|--------|-------------|
| Vendor status | registered / pending / blacklisted |
| Budget check | within budget, utilisation %, remaining |
| Authority check | adequate / inadequate + reason |
| Anomaly flags | split_po_pattern, unregistered_vendor, budget_exceedance, unverified_approver |
| Findings | Structured list with severity codes (F001, F002…) |
| Risk score | 0.0 (clean) – 1.0 (high risk) |
| Recommended action | AI-suggested decision |
| Decision options | approve / hold / reject / escalate |
| Audit receipt ID | Permanent signed record of the procurement decision |
| Compact journal | Full event log: analysis → snapshot → human decision |

## When to trigger

Activate when the user:
- Mentions a PO number (e.g. "PO-2026-001")
- Asks to approve, review, or check a purchase order
- Says "procurement approval", "PO review", "check this PO"

**Before starting**, confirm: "Submit PO [PO-ID] for MOVA risk analysis?"

## Step 1 — Submit PO

Call tool `mova_hitl_start_po` with:
- `po_id`: PO number (e.g. PO-2026-001)
- `approver_employee_id`: HR employee ID (e.g. EMP-1042)

## Step 2 — Show analysis and decision options

If `status = "waiting_human"` — show risk summary and ask to choose:

- **approve** — Approve PO
- **hold** — Hold for review
- **reject** — Reject PO
- **escalate** — Escalate to director/board

Show `recommended` option if present (mark ← RECOMMENDED).

Call tool `mova_hitl_decide` with:
- `contract_id`: from the response above (NOT the PO number)
- `option`: chosen decision
- `reason`: human reasoning

## Step 3 — Show audit receipt

Call tool `mova_hitl_audit` with `contract_id`.
Call tool `mova_hitl_audit_compact` with `contract_id` for the full signed event chain.

## Connect your real ERP systems

By default MOVA uses a sandbox mock. To route procurement checks against your live ERP, call `mova_list_connectors` with `keyword: "erp"`.

Relevant connectors:

| Connector ID | What it covers |
|---|---|
| `connector.erp.po_lookup_v1` | Purchase order data from ERP |
| `connector.erp.vendor_registry_v1` | Vendor registration status and bank accounts |
| `connector.erp.budget_check_v1` | Budget availability and utilisation |
| `connector.erp.hr_employee_v1` | Approver authority level from HR |

Call `mova_register_connector` with `connector_id`, `endpoint`, optional `auth_header` and `auth_value`.

## Rules

- NEVER make HTTP requests manually
- NEVER invent or simulate results — if a tool call fails, show the exact error
- Use MOVA plugin tools directly — do NOT use exec or shell
- CONTRACT_ID comes from the mova_hitl_start_po response, not from the PO number
