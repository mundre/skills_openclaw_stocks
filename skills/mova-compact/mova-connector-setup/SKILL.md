---
name: mova-connector-setup
description: Help the user connect their real business systems (ERP, CRM, AML, market data, etc.) to MOVA by registering custom connector endpoints. Trigger when the user asks "how do I use my real data", "connect my ERP", "use production data", "register a connector", or mentions wanting to replace the MOVA sandbox mock with their own system.
license: MIT-0
metadata: {"openclaw":{"plugin":{"name":"MOVA","installCmd":"openclaw plugins install openclaw-mova"},"dataSentToExternalServices":[{"service":"MOVA API (api.mova-lab.eu)","data":"connector ID, endpoint URL, auth header — to register connector overrides for your org"}]}}
---

> **Ecosystem Skill** — Supports building and managing the MOVA ecosystem. Requires the `openclaw-mova` plugin.

# MOVA Connector Setup

Help the user register their real business system endpoints to replace the MOVA sandbox mock.

## What this skill does

MOVA has 40+ connectors for ERP, CRM, AML, market data, sanctions screening, and more.
By default all connectors use a **sandbox mock** that returns realistic test data.

To use **live data** from your own systems, you register an HTTPS endpoint per connector.
After registration, all contracts your org runs will call your endpoint instead of the mock —
no code changes, no redeployment.

## When to trigger

- User says "how do I connect my ERP / CRM / AML system?"
- User asks "how do I use real data instead of the demo?"
- User says "replace the mock", "use production data", "register my endpoint"
- User asks "what connectors are available?"

## Step 1 — List available connectors

    mova-bridge call mova_list_connectors

Or filter by domain keyword:

    mova-bridge call mova_list_connectors --keyword erp
    mova-bridge call mova_list_connectors --keyword aml
    mova-bridge call mova_list_connectors --keyword crm
    mova-bridge call mova_list_connectors --keyword market

The response shows:
- `connectors` — all available connectors with `has_override: true/false`
- `overrides` — endpoints you have already registered

## Step 2 — Identify the right connector

Show the user the filtered list. Ask which system they want to connect.
Common choices by skill:

| Skill | Key connectors |
|---|---|
| Invoice OCR | `connector.erp.invoice_post_v1`, `connector.finance.duplicate_check_v1`, `connector.tax.vat_validate_v1` |
| PO Approval | `connector.erp.po_lookup_v1`, `connector.erp.vendor_registry_v1`, `connector.erp.budget_check_v1`, `connector.erp.hr_employee_v1` |
| AML Triage | `connector.screening.pep_sanctions_v1`, `connector.aml.transaction_history_v1`, `connector.policy.aml_rules_v1` |
| Complaints | `connector.crm.customer_lookup_v1`, `connector.policy.complaints_rules_v1` |
| Crypto Trade | `connector.market.price_feed_v1`, `connector.wallet.balance_v1`, `connector.market.portfolio_risk_v1` |

## Step 3 — Register the endpoint

Ask the user for:
1. Their HTTPS endpoint URL
2. Auth method (API key header, Bearer token, or none)
3. A label (e.g. "Production ERP")

Then run:

    mova-bridge call mova_register_connector \
      --connector-id CONNECTOR_ID \
      --endpoint https://their-system.example.com/api/endpoint \
      --label "Their label" \
      --auth-header X-Api-Key \
      --auth-value THEIR_KEY

The endpoint must be HTTPS. Auth header and value are optional — omit if not needed.

## Step 4 — Confirm registration

    mova-bridge call mova_list_connectors --keyword KEYWORD

Verify `has_override: true` appears for the registered connector.
Tell the user: "Done — all future contracts in your org will now call your endpoint for [connector name]."

## Removing an override

To revert a connector back to the sandbox mock:

    mova-bridge call mova_delete_connector_override --connector-id CONNECTOR_ID

## Viewing all current overrides

    mova-bridge call mova_list_connectors

Check the `overrides` array in the response.

## What MOVA sends to the user's endpoint

Each connector call is a `POST` with a JSON body matching the connector's schema.
The user's endpoint must return a JSON response. The MOVA runtime does not store or log
the response data beyond what is needed for the current contract execution.

## Rules

- NEVER make HTTP requests manually
- NEVER store or display auth values the user provides beyond what is needed for registration
- Always confirm the endpoint URL before registering — ask if unclear
- Endpoint must be HTTPS — reject HTTP endpoints
- Run exec directly: `mova-bridge call ...` (not wrapped in bash or sh)
