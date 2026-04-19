#!/bin/bash
#
# Restore Cron Tasks for OpenClaw (Merge Mode)
# Imports cron jobs from a backup file, MERGE strategy = additive only
# Usage: ./restore-cron-tasks.sh <cron_export_file> [--dry-run] [--merge-auth]
#
# v3.0.9: Full rewrite with actual merge logic
#
# Merge rules (cron):
# - Job with same ID exists locally → SKIP (preserve local)
# - Job with same ID not exists locally → ADD (install new)
#
# Merge rules (auth token):
# - Current has no gateway token → FILL from backup (additive only)
# - Current already has gateway token → SKIP (never overwrite existing)
#

set -e

CRON_EXPORT_FILE="$1"
DRY_RUN=false
MERGE_AUTH=false
for arg in "$@"; do
    case $arg in
        --dry-run) DRY_RUN=true ;;
        --merge-auth) MERGE_AUTH=true ;;
    esac
done

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

show_usage() {
    echo -e "${YELLOW}Usage:${NC} $0 <cron_export_file> [--dry-run] [--merge-auth]"
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo "  --dry-run        Preview merge without modifying files"
    echo "  --merge-auth     Also merge gateway token (fill empty slots only)"
    echo ""
    echo -e "${YELLOW}Merge Strategy (cron jobs):${NC}"
    echo "  • Job exists locally (same ID) → SKIP (keep local)"
    echo "  • Job not exists locally → ADD (install from backup)"
    echo ""
    echo -e "${YELLOW}Merge Strategy (auth token):${NC}"
    echo "  • Current has token → SKIP (never overwrite)"
    echo "  • Current is empty + backup has → FILL from backup"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 ~/backups/cron-tasks-20260322.json --dry-run"
    echo "  $0 ~/backups/cron-tasks-20260322.json --merge-auth"
}

if [ -z "$CRON_EXPORT_FILE" ] || [ "$CRON_EXPORT_FILE" = "--help" ]; then
    show_usage
    exit 1
fi

if [ ! -f "$CRON_EXPORT_FILE" ]; then
    echo -e "${RED}Error: File not found: $CRON_EXPORT_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Cron Tasks Restore (Merge Mode)${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Optional: auth token merge
echo -e "${YELLOW}[OPTIONAL] Auth Token Merge${NC}"
if [ "$MERGE_AUTH" = true ]; then
    echo "Mode: --merge-auth enabled"
    python3 - "$CRON_EXPORT_FILE" "$DRY_RUN" "$MERGE_AUTH" << 'PYEOF'
import json, os, sys

export_file = sys.argv[1]
dry_run = sys.argv[2] == "--dry-run"
merge_auth = sys.argv[3] == "true"

gw_current = json.load(open(os.path.expanduser("~/.openclaw/openclaw.json"),'r')).get('gateway',{})
current_token = gw_current.get('auth',{}).get('token','')

auth_export_file = export_file.replace('cron-tasks','auth-tokens')
if not os.path.exists(auth_export_file):
    auth_export_file = export_file  # fallback: look in same file

try:
    auth_backup = json.load(open(auth_export_file,'r')).get('auth_token','')
except:
    auth_backup = ''

if current_token:
    print(f"  Current has gateway token: {current_token[:12]}...")
    print(f"  SKIP (preserve existing)")
    print(f"  → Use --merge-auth only if target has NO token")
elif auth_backup:
    print(f"  Current: NO gateway token")
    print(f"  Backup: HAS token {auth_backup[:12]}...")
    if not dry_run:
        gw = json.load(open(os.path.expanduser("~/.openclaw/openclaw.json"),'r')).get('gateway',{})
        gw.setdefault('auth',{})['token'] = auth_backup
        json.dump(json.load(open(os.path.expanduser("~/.openclaw/openclaw.json"),'r')), open(os.path.expanduser("~/.openclaw/openclaw.json"),'w'), indent=2)
        print(f"  → FILLED from backup")
    else:
        print(f"  → Would fill from backup (DRY RUN)")
else:
    print(f"  Current: NO gateway token")
    print(f"  Backup: NO token either")
    print(f"  → Nothing to merge")
PYEOF
    echo ""
else
    echo "Mode: --merge-auth not enabled (skip auth token merge)"
    echo ""
fi
echo ""

# Python merge logic - reads from cron export file
python3 - "$CRON_EXPORT_FILE" "$DRY_RUN" << 'PYEOF'
import json
import os
import sys

export_file = sys.argv[1]
dry_run = sys.argv[2] == "--dry-run"
cron_file = os.path.expanduser("~/.openclaw/cron/jobs.json")

# Load export
try:
    with open(export_file, 'r') as f:
        data = json.load(f)
except json.JSONDecodeError as e:
    print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
    sys.exit(1)

if 'jobs' not in data:
    print("ERROR: Not a valid cron export file (no 'jobs' key)", file=sys.stderr)
    sys.exit(1)

backup_jobs = data['jobs']
print(f"Export: {data.get('version', '?')} | {len(backup_jobs)} jobs | {data.get('exported_at', '?')}")
print("")

# Load current
with open(cron_file, 'r') as f:
    current = json.load(f)
current_jobs_list = current['jobs']
current_jobs_by_id = {j['id']: j for j in current_jobs_list}

print(f"Current: {len(current_jobs_list)} jobs")

# Merge: additive only
added = []
skipped_existing = []

for bjob in backup_jobs:
    bid = bjob.get('id')
    if bid in current_jobs_by_id:
        skipped_existing.append(bjob.get('name', '?'))
    else:
        # Strip runtime state
        clean_job = {k: v for k, v in bjob.items() if k not in [
            'state', 'lastRunAtMs', 'lastRunStatus', 'lastStatus',
            'lastDurationMs', 'lastDelivered', 'lastErrorReason',
            'consecutiveErrors', 'lastError', 'nextRunAtMs',
            'lastDeliveryStatus'
        ]}
        added.append(clean_job)

print(f"  → Will ADD (new): {len(added)}")
print(f"  → Will SKIP (exists): {len(skipped_existing)}")

if skipped_existing:
    print(f"\nSkipped (already exists locally):")
    for name in skipped_existing[:10]:
        print(f"  - {name}")
    if len(skipped_existing) > 10:
        print(f"  ... and {len(skipped_existing)-10} more")

if added:
    print(f"\nNew jobs to install:")
    for job in added:
        print(f"  + {job.get('name', '?')} [{str(job.get('id', '?'))[:8]}...]")
    print("")
    if not dry_run:
        new_jobs = current_jobs_list + added
        current['jobs'] = new_jobs
        with open(cron_file, 'w') as f:
            json.dump(current, f, indent=2, ensure_ascii=False)
        os.utime(cron_file, None)
        print(f"OK: {len(added)} jobs merged into {cron_file}")
        print("")
        print("Restart gateway to activate: openclaw gateway restart")
else:
    print("Nothing to add - all backup jobs already exist locally.")

if dry_run:
    print("")
    print("[DRY RUN] No files modified.")
PYEOF

echo ""
[ "$DRY_RUN" = true ] && echo -e "${BLUE}[DRY RUN]${NC} Remove --dry-run to actually merge."
[ "$DRY_RUN" = false ] && echo -e "${GREEN}Merge complete${NC}"
