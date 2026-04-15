"""
assemble_result.py — Assemble the final JSON output for the update-advisor skill.

Usage:
  python3 assemble_result.py <current> <latest> <has_update>
                             <changelog_result.json> <update_status.txt> <doctor_output.txt>
"""
import sys
import json
import re

current     = sys.argv[1]
latest      = sys.argv[2]
has_update  = sys.argv[3] == "true"
changelog_f = sys.argv[4]
status_f    = sys.argv[5]
doctor_f    = sys.argv[6]

# ── Changelog parse result ────────────────────────────────────────────────────
with open(changelog_f, 'r', encoding='utf-8') as f:
    cl = json.load(f)

changelog_delta      = cl.get('delta', '')
flagged_items        = cl.get('flagged', [])
latest_not_local     = cl.get('latest_not_local', False)
changelog_not_found  = cl.get('changelog_not_found', False)
changelog_empty      = cl.get('changelog_empty', False)
# Pass through semantic flags from parse step
same_version         = cl.get('same_version', False)
already_latest       = cl.get('already_latest', False)

# ── Update status output ──────────────────────────────────────────────────────
with open(status_f, 'r', encoding='utf-8') as f:
    update_status = f.read().strip()

# ── Doctor output analysis ────────────────────────────────────────────────────
with open(doctor_f, 'r', encoding='utf-8') as f:
    doctor_raw = f.read()

doctor_ok = True
doctor_issues = []

for line in doctor_raw.splitlines():
    # Skip summary count lines (e.g. "Errors: 0", "Warnings: 2")
    if re.search(r'(?:Errors|Warnings|Issues):\s*\d+', line):
        continue
    # Detect failure indicators
    has_fail = re.search(r'✗|\bfailed\b|\binvalid\b|\bunrecognized\b', line, re.IGNORECASE)
    has_error = re.search(r'\berror\b', line, re.IGNORECASE) and not re.search(r'Errors:\s*\d+', line)
    if has_fail or has_error:
        doctor_ok = False
        stripped = line.strip()
        if stripped:
            doctor_issues.append(stripped)

doctor_issues = doctor_issues[:10]  # cap at 10 entries

# ── Rollback command ──────────────────────────────────────────────────────────
rollback_cmd = f"openclaw update --tag {current} --yes"

# ── Final output ─────────────────────────────────────────────────────────────
result = {
    "current_version":      current,
    "latest_version":       latest,
    "has_update":           has_update,
    "same_version":         same_version,
    "already_latest":       already_latest,
    "rollback_cmd":         rollback_cmd,
    "latest_not_local":     latest_not_local,
    "changelog_not_found":  changelog_not_found,
    "changelog_empty":      changelog_empty,
    "update_status":        update_status,
    "doctor_ok":            doctor_ok,
    "doctor_issues":        doctor_issues,
    "flagged_count":        len(flagged_items),
    "flagged_items":        flagged_items,
    "changelog_delta":      changelog_delta,
}

print(json.dumps(result, ensure_ascii=False, indent=2))
