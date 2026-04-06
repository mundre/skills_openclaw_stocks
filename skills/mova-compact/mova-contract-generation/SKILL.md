---
name: mova-contract-generation
description: Generate a legal document draft (NDA, service agreement, supply contract, SLA) from a structured template via MOVA HITL, with section-by-section human review gates before finalizing. Trigger when the user asks to create or draft a contract, NDA, agreement, or legal document from a template. Human legal review is required before the document is finalized.
license: MIT-0
metadata: {"openclaw":{"plugin":{"name":"MOVA","installCmd":"openclaw plugins install openclaw-mova"},"dataSentToExternalServices":[{"service":"MOVA API (api.mova-lab.eu)","data":"document type, party names, jurisdiction, key terms, AI-generated section drafts, reviewer edits, human approvals, audit metadata"},{"service":"Legal template repository connector (read-only)","data":"template ID used to fetch the base document structure"},{"service":"Document storage connector","data":"finalized document stored in configured repository after all sections are approved"}]}}
---

> **Contract Skill** — A ready-to-use MOVA HITL workflow. Requires the `openclaw-mova` plugin.

# MOVA Contract Generation

Generate legal document drafts from structured templates — with AI-populated sections, section-by-section human review gates, and a complete chain of custody from template selection to final signed document.

## What it does

1. **Template selection** — choose document type: NDA, service agreement, supply contract, or SLA
2. **Data ingestion** — parties, dates, jurisdiction, pricing, special conditions
3. **Draft generation** — AI populates each section from the selected template with provided parameters
4. **Section-by-section human gates** — legal reviewer approves, edits, or rejects each section individually
5. **Final sign-off** — complete document finalized, stored in document repository with full audit trail

Every draft version, edit, reviewer identity, and approval timestamp is recorded in the MOVA audit trail — providing a complete chain of custody for legal and compliance review.

## Requirements

**Plugin:** MOVA OpenClaw plugin must be installed in your OpenClaw workspace.

**Data flows:**
- Document parameters + party data → `api.mova-lab.eu` (MOVA platform, EU-hosted)
- Template ID → legal template repository (read-only, fetches base structure)
- Finalized document → document storage connector (written on completion)
- Audit journal → MOVA R2 storage, signed
- No data sent to third parties beyond the above

## Demo

**Step 1 — NDA generation request: Vortex Analytics ↔ NordStern Capital, German law**
![Step 1](screenshots/01-input.jpg)

**Step 2 — AI draft generated: 7 sections with full text, risk score 0.2**
![Step 2](screenshots/02-analysis.jpg)

**Step 3 — Section approved, audit receipt with signed decision log**
![Step 3](screenshots/03-audit.jpg)

## Quick start

Say "generate an NDA between Acme Corp and Beta GmbH, governed by German law":

```
doc_type: nda
party_a: Acme Corp
party_b: Beta GmbH
jurisdiction: DE
effective_date: 2026-04-01
```

The agent generates each section from the NDA template, presents it for review, and waits for your decision before moving to the next section.

## Why contract execution matters

- **Section-level accountability** — each reviewer decision (approve / edit / reject) is individually timestamped and signed
- **Full draft lineage** — the audit trail shows exactly which AI-generated text was accepted, what was edited, and by whom
- **Immutable chain of custody** — when a counterparty disputes a clause, the system shows the exact approved version and who signed off
- **EU AI Act ready** — AI-generated legal documents require documented human oversight at each material clause

## What the user receives

| Output | Description |
|--------|-------------|
| Document type | NDA / service_agreement / supply_contract / SLA |
| Parties | Party A and Party B names |
| Section count | Total sections in the document |
| Per-section draft | AI-generated text ready for review |
| Reviewer decision | approve_section / edit_section / reject_section / escalate |
| Edit trail | Every accepted edit captured with original and revised text |
| Document ID | Final stored document reference |
| Audit receipt ID | Permanent signed record of all section approvals |
| Compact journal | Full event log: generate → per-section decisions → finalize |

## When to trigger

Activate when the user:
- Asks to generate, create, or draft a contract, NDA, or legal document
- Provides party names and asks to prepare a document from a template
- Says "create an NDA", "draft a service agreement", "generate a supply contract", "prepare an SLA"

**Before starting**, confirm: "Generate [DOC_TYPE] for [PARTY_A] ↔ [PARTY_B] via MOVA?"

If document type, party names, or jurisdiction is missing — ask once.

## Step 1 — Submit document parameters

Call tool `mova_hitl_start_contract_gen` with:
- `doc_type`: nda / service_agreement / supply_contract / sla
- `party_a`: full legal name of party A
- `party_b`: full legal name of party B
- `jurisdiction`: governing law jurisdiction (ISO country code or US state, e.g. DE, US-NY, EU)
- `effective_date`: ISO date (e.g. 2026-04-01)
- `terms`: optional object with key terms (pricing, duration, notice period, confidentiality scope)
- `template_id`: optional — use a specific template version

## Step 2 — Review sections one by one

For each section, if `status = "waiting_human"` — show the draft:

```
Document:  DOC_TYPE — CONTRACT_ID
Section:   SECTION_NAME  (N of TOTAL)
──────────────────────────────────
SECTION_CONTENT
──────────────────────────────────
```

Ask the legal reviewer to choose:

| Option | Description |
|---|---|
| `approve_section` | Approve this section as written |
| `edit_section` | Accept with edits (provide revised text in reason) |
| `reject_section` | Reject and request AI redraft |
| `escalate` | Escalate to senior legal counsel |

Call tool `mova_hitl_decide` with:
- `contract_id`: from the response above — this is `ctr-ctg-xxxxxxxx`
- `option`: chosen decision
- `reason`: reviewer note or full edited text (for edit_section)

Repeat for each section until all are approved and `status = "completed"`.

## Step 3 — Show audit receipt and final document

Call tool `mova_hitl_audit` with `contract_id` to retrieve the final document details.
Call tool `mova_hitl_audit_compact` with `contract_id` for the full signed approval chain.

## Connect your real document systems

By default MOVA uses a sandbox mock. To use your real template and storage infrastructure, call `mova_list_connectors` with `keyword: "document"`.

Relevant connectors:

| Connector ID | What it covers |
|---|---|
| `connector.legal.template_repository_v1` | Legal document template library |
| `connector.legal.document_storage_v1` | Final document storage and versioning |

Call `mova_register_connector` with `connector_id`, `endpoint`, optional `auth_header` and `auth_value`.

## Rules

- NEVER make HTTP requests manually
- NEVER fabricate legal text outside the MOVA workflow or provide legal advice
- Use MOVA plugin tools directly — do NOT use exec or shell
- CONTRACT_ID is `ctr-ctg-xxxxxxxx` from the mova_hitl_start_contract_gen response
- Human approval is required for every section — never auto-finalize a document
