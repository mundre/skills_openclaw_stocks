# Report Definition

This file defines the canonical shape for a saved scheduled-report definition.

The goal is stability:
- the user describes the report through conversation
- the agent drafts and refines it
- the final approved definition is saved
- recurring execution reuses the saved definition without reinterpreting the business request

## Required top-level fields

| Field | Type | Notes |
|---|---|---|
| `reportId` | string | Stable machine identifier |
| `name` | string | Human-readable report name |
| `purpose` | string | Business purpose and audience |
| `owner` | object | Human or team responsible for the report |
| `status` | string | `draft`, `enabled`, `paused`, or `archived` |
| `schedule` | object | Timezone plus machine-readable trigger |
| `delivery` | object | Channel plus explicit target |
| `output` | object | Artifact type and naming rules |
| `data` | object | Saved data backend and query/data logic |
| `rendering` | object | Saved template, structure, or workbook definition |

## Canonical JSON shape

```json
{
  "reportId": "weekly-sales-summary",
  "name": "Weekly Sales Summary",
  "purpose": "Send sales leadership a Monday morning summary of revenue, volume, and region trends.",
  "owner": {
    "id": "sales-director",
    "displayName": "Sales Director"
  },
  "status": "enabled",
  "schedule": {
    "timezone": "Africa/Casablanca",
    "summary": "Every Monday at 08:00",
    "trigger": {
      "type": "weekly",
      "days": ["MON"],
      "time": "08:00"
    }
  },
  "delivery": {
    "channel": "email",
    "executionSkill": "imap-smtp-mail",
    "target": {
      "to": ["sales@example.com"],
      "cc": []
    },
    "definition": {
      "subject": "Weekly Sales Summary",
      "bodyTemplate": "Please find attached the weekly sales summary."
    }
  },
  "output": {
    "type": "pdf",
    "filenameTemplate": "weekly-sales-summary-{{ run_date }}.pdf"
  },
  "data": {
    "backend": "mssql",
    "executionSkill": "mssql",
    "definition": {
      "query": "SELECT Region, Revenue, Volume FROM sales.vw_weekly_summary WHERE WeekStart = CAST(GETDATE() AS date);",
      "parameters": {
        "period": "current-week"
      }
    }
  },
  "rendering": {
    "kind": "pdf-report",
    "executionSkill": "pdf-report",
    "definition": {
      "template": "skills/pdf-report/templates/report.html",
      "sections": [
        "summary",
        "regional_breakdown",
        "exceptions"
      ]
    }
  },
  "postProcessing": {
    "charts": [
      {
        "executionSkill": "chart-mpl",
        "kind": "bar",
        "title": "Revenue by Region"
      }
    ]
  },
  "metadata": {
    "createdAt": "2026-04-15T14:30:00Z",
    "updatedAt": "2026-04-15T14:30:00Z",
    "lastRunAt": null,
    "nextRunAt": null,
    "lastStatus": null,
    "failureReason": null
  }
}
```

## Field rules

### `reportId`

- Use lowercase letters, digits, hyphens, or underscores.
- Keep it stable across updates.
- Do not derive it from volatile details like the current date.

### `status`

Allowed values:
- `draft`
- `enabled`
- `paused`
- `archived`

Recommended lifecycle:
- use `draft` before approval
- switch to `enabled` only after approval and successful save
- use `paused` for temporary suspension
- use `archived` when the user explicitly retires the report

### `schedule`

The schedule must contain:
- `timezone`
- `summary`
- `trigger`

The `trigger` object should be machine-readable and stable. Keep it local-agent friendly. Do not store only a human sentence.

Supported trigger shapes in this package:
- `hourly`: `trigger.type = "hourly"`, optional `intervalHours`, optional `minute`
- `daily`: `trigger.type = "daily"`, required `time`
- `weekly`: `trigger.type = "weekly"`, required `days[]`, required `time`
- `monthly`: `trigger.type = "monthly"`, required `dayOfMonth`, required `time`

Time values must use `HH:MM` 24-hour format.
Timezone values must use valid IANA names such as `Africa/Casablanca` or `Europe/Paris`.
Treat `cron` as a host-specific extension rather than part of the generic package contract.

### `delivery`

The delivery target must be explicit. Examples:
- email recipients
- target conversation id
- destination folder
- webhook endpoint alias

Do not leave delivery implicit or "same as last time".

Supported delivery channels in this package:
- `email`: `target.to[]` or `target.contact`
- `conversation`: `target.conversationId` or `target.threadId`
- `thread`: `target.threadId` or `target.conversationId`
- `webhook`: `target.endpointAlias` or `target.url`
- `folder`: `target.path`

Reject unknown delivery channels unless the host agent deliberately extends the validator and the runtime contract together.
Use `conversation` as the generic chat transport abstraction. Host agents may map it to WhatsApp or other messaging channels.
When a delivery channel maps to a known transport skill, keep `channel` and `executionSkill` consistent. For example, `email` maps to `imap-smtp-mail`.

### `output`

The output object defines the report artifact, for example:
- `text`
- `pdf`
- `excel`
- `image`

If the artifact name matters, store a deterministic `filenameTemplate`.
When the output type maps to a known renderer, keep `output.type`, `rendering.kind`, and `rendering.executionSkill` consistent.

### `data`

The `data` object must capture the saved data logic:
- backend or source system
- execution skill if relevant
- the approved query, dataset reference, or equivalent deterministic logic

Do not store a vague business request in place of real data logic.
The `definition` value must be an object, not a scalar or free-form note.
When the backend maps to a known execution skill, keep `backend` and `executionSkill` consistent.
Recommended deterministic keys include:
- `query`
- `queryFile`
- `storedProcedure`
- `datasetRef`
- `sourceRef`
- `pipelineRef`
- `jobRef`

Optional companion fields may include:
- `parameters`

### `rendering`

The `rendering` object must capture the saved report structure:
- template path
- fixed sections
- workbook definition
- chart recipe
- formatting rules

Do not let recurring runs invent a fresh structure.
The `definition` value must be an object, not a scalar or free-form note.
Recommended deterministic keys include:
- `template`
- `sections`
- `workbook`
- `sheets`
- `chart`
- `charts`
- `layout`
- `rendererConfig`

## Storage convention

Use a configuration path for persisted report definitions, for example:
- `config/scheduled-reports/<reportId>.json`

Do not store persisted report definitions under conversational `memory/` paths.

## Recommended skill mapping

Map the saved definition to installed OpenClaw skills when possible:

| Need | Preferred skill |
|---|---|
| SQL Server data extraction | `mssql` |
| chart image generation | `chart-mpl` |
| PDF rendering | `pdf-report` |
| Excel rendering | `excel-export` |
| email delivery | `imap-smtp-mail` |

## Validation command

Validate a definition before activation:

```bash
python3 skills/scheduled-reports/scripts/validate_report_definition.py \
  --input config/scheduled-reports/weekly-sales-summary.json
```

The validator checks:
- required fields
- allowed status values
- supported trigger types and machine-readable schedule details
- valid IANA timezone names
- allowed delivery channels and explicit delivery target
- consistency between known delivery channels and transport skills
- consistency between known output types and rendering backends
- consistency between known data backends and execution skills
- structured saved data logic
- structured saved rendering logic
