# Parse and summarize scan reports

Load when the user shares a scan report for analysis.

## Reading the Report

- Accept a JSON file path (use Read tool) or pasted JSON content directly.
- If Markdown format, extract score from the header and findings from sections.
- Handle both camelCase (browser export) and snake_case (API export) field names.
- Validate that `findings` is an array and `score` is 0-100 before proceeding.

## JSON Schema (Key Fields)

```
ScanReport {
  score: number (0-100)
  scan_level: "L1" | "L2" | "L3A" | "L3B"
  execution_profile: string
  created_at: string (ISO 8601)
  rulepack_version: string
  report_id: string
  schema_version: string
  session_id: string | null
  platform: string
  findings: Finding[]
  coverage: CoverageItem[]
  severity_summary: { CRITICAL: n, HIGH: n, MEDIUM: n, LOW: n }
  category_summary: Record<string, number>  # maps category name to finding count
  coverage_summary: Record<CoverageStatus, number>
  metadata: { execution_profile, rulepack_id, rule_count, browser_profile_opt_in }
}

Finding {
  rule_id: string (e.g. "OC-001")
  title: string
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
  status: "pass" | "fail" | "warn" | "best_effort"
  coverage_status: "checked_pass" | "checked_fail" | "best_effort"
                 | "not_checked" | "not_applicable"
  message: string
  remediation: string
  evidence: EvidenceItem[]
  confidence: number
  compensatingControls: CompensatingControl[]
  attackScenario: string
  fixSuggestion: { action, patches[], description, configBefore?, configAfter? }
  alternativeFix: { action, description }
  aiHint: string
  relatedRuleEffects: RelatedRuleEffect[]
  environmentHint: { environment, signals[], confidence }
}
```

## Summary Generation Template

Output this format after reading:

```
## Scan Summary
- Score: {score}/100 (Grade: A/B/C/D/F based on 90/80/60/40 thresholds)
- Scan Mode: {scan_level}
- Date: {created_at}
- Rules Checked: {checked_pass + checked_fail} / {total coverage items}

### Severity Breakdown
| Severity | Failed | Warned | Passed |
| --- | --- | --- | --- |
| CRITICAL | n | n | n |
| HIGH | n | n | n |
| MEDIUM | n | n | n |
| LOW | n | n | n |

### Immediate Attention ({count})
(List all status=fail AND severity=CRITICAL or HIGH: rule_id - title)

### Next Steps
(1-2 actionable suggestions based on results)
```

Grade thresholds: A >= 90, B >= 80, C >= 60, D >= 40, F < 40.

> Note: `severity_summary` only has totals per severity. Compute the Failed/Warned/Passed columns by iterating `findings[]` and cross-tabulating severity x status, or use `{baseDir}/scripts/parse-report.py` which outputs pre-computed `severity_fail`, `severity_warn`, `severity_pass` breakdowns.

## Sorting Priority

Sort findings for display using this order:
1. Status weight: fail=0, warn=1, best_effort=2, pass=3
2. Severity weight: CRITICAL=0, HIGH=1, MEDIUM=2, LOW=3
3. Confidence: exact > heuristic (higher confidence first)

## Large Report Handling (50+ findings)

- **Pre-processing**: For reports with 50+ findings, run `{baseDir}/scripts/parse-report.py <file>` first. Use its summary JSON (score, severity counts, urgent items) for Layer 1. Only read the full JSON if the user requests details.
- **Layer 1** (always show): Summary above -- score, severity table, top critical/high fails.
- **Layer 2** (on request): Category breakdown table from `category_summary`.
- **Layer 3** (on request): Individual finding details with evidence and remediation.
- Never dump all findings at once.
- Prompt: "Want to drill into a specific category or finding?"

## Report Comparison

When the user provides two reports:
- Show score delta and direction.
- List new fails, resolved fails, and degraded items (pass/warn -> fail).
- Show coverage changes (rules added/removed).
- Warn if `rulepack_version` differs between reports.
- Warn if `scan_level` differs (L1 vs L2 have different coverage scope).

## Field Notes

- `evidence[].redacted === true`: Value is masked. Tell user to check locally.
- `not_checked` does NOT mean safe. Always mention unchecked rule count in summary.
- `best_effort` means incomplete evidence. Flag reliability concern for those findings.
- `compensatingControls`: If present, note them when discussing a fail -- they may reduce effective risk.
- `environmentHint`: Use to contextualize findings (dev vs staging vs prod).
- `category_summary`: A flat map of category name to finding count. Use it to show per-category totals, not per-status breakdowns.
