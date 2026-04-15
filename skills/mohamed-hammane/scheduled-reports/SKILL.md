---
name: scheduled-reports
version: 1.0.0
description: Create, validate, approve, and manage saved recurring report definitions for OpenClaw agents. Use when the user asks for a scheduled report, recurring report, automatic report, or wants to convert an ad hoc report into a repeatable one. Also use when the user needs to update, pause, resume, or retire an existing recurring report. Scheduled reports are saved definitions, not scheduled prompts.
metadata:
  openclaw:
    emoji: "SR"
    requires:
      bins:
        - python3
---

# Scheduled Reports

Use this skill to turn a conversational reporting request into a deterministic saved report definition.

## Core doctrine

- Treat a scheduled report as a saved business object, not a prompt replay.
- Require explicit approval before activation.
- Save the schedule, delivery target, output type, data logic, and report structure.
- Reuse the saved definition on every recurring run.
- Keep scheduler wiring, persistence, credentials, and transport integration local to the host agent.
- Treat `conversation` as the generic chat delivery abstraction; let host agents map it to WhatsApp or other messaging channels.
- Treat `cron` as a host-specific extension, not part of the generic package contract.

## Use this workflow

1. Confirm that the user wants a recurring report, not a one-off analysis.
2. Gather the missing fields required for a saved definition.
3. Draft the report definition in a deterministic format.
4. Validate the definition before approval.
5. Present the final definition summary and get explicit approval.
6. Save the definition using the local agent's storage conventions.
7. Activate or update local scheduler wiring only after the definition is approved and stored.

## Required fields

Every scheduled report definition must contain at least:

- `reportId`
- `name`
- `purpose`
- `owner`
- `status`
- `schedule`
- `delivery`
- `output`
- `data`
- `rendering`

Read `references/REPORT_DEFINITION.md` for the canonical shape and field rules.

## Validation

Validate every final definition with:

```bash
python3 skills/scheduled-reports/scripts/validate_report_definition.py \
  --input config/scheduled-reports/weekly-sales-summary.json
```

Do not activate a report definition that fails validation.

## Lifecycle rules

- `create`: gather missing fields, draft, validate, approve, save, activate
- `update`: edit the saved definition instead of re-deriving the report from scratch
- `pause`: set status to `paused` and stop scheduling new runs
- `resume`: restore status to `enabled` only after confirming the saved definition is still valid
- `retire`: move to `archived` only when the user explicitly asks

## Integration rules

Use existing execution skills when the saved definition requires them:

- `mssql` for SQL Server data extraction
- `chart-mpl` for deterministic chart images
- `pdf-report` for PDF rendering
- `excel-export` for `.xlsx` rendering
- `imap-smtp-mail` for email delivery

For `flconnect.openclaw`, prefer composing those skills instead of reimplementing their behavior here.

## Operational boundaries

- Do not schedule a free-form prompt.
- Do not leave the query or data-selection logic implicit.
- Do not infer recipients, filters, or output structure from scratch at run time.
- Do not auto-send or auto-activate without approval.
- Do not treat ad hoc reporting and recurring reporting as the same mode.
- Do not store persisted report definitions in conversational memory paths.

## Recommended storage conventions

These are recommendations, not hard requirements:

- store definitions under `config/scheduled-reports/<reportId>.json`
- store run artifacts under `exports/reports/<reportId>/`
- store execution logs or run metadata next to the persisted definition or in a local scheduler store

Adjust the exact paths to the host agent's workspace conventions.
