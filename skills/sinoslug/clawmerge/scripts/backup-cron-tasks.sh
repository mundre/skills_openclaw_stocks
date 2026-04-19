#!/bin/bash
#
# Backup Cron Tasks for OpenClaw
# Exports all cron jobs to a JSON file for migration
# Usage: ./backup-cron-tasks.sh [output_dir]
#
# v3.0.9: Now reads actual cron jobs from ~/.openclaw/cron/jobs.json
#

set -e

OUTPUT_DIR="${1:-$HOME/.openclaw/backups}"
# Remove trailing / if present to avoid double-slash
OUTPUT_DIR="${OUTPUT_DIR%/}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
CRON_EXPORT_FILE="$OUTPUT_DIR/cron-tasks-$TIMESTAMP.json"
SYSTEM_CRONTAB_FILE="$OUTPUT_DIR/system-crontab-$TIMESTAMP.txt"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Cron Tasks Backup v3.0.9${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

mkdir -p "$OUTPUT_DIR"

# 1. Export OpenClaw Gateway cron jobs (actual data)
echo -e "${YELLOW}[1/2] Exporting OpenClaw cron jobs...${NC}"

CRON_JOBS_FILE="$HOME/.openclaw/cron/jobs.json"

if [ -f "$CRON_JOBS_FILE" ]; then
    # Read actual cron jobs, strip runtime state (lastRunAtMs, consecutiveErrors, etc.)
    # We only want portable job definitions, not machine-specific runtime state
    python3 << 'PYTHON_SCRIPT'
import json
import sys
import os
from datetime import datetime

jobs_file = os.path.expanduser("~/.openclaw/cron/jobs.json")
output_file = sys.argv[1] if len(sys.argv) > 1 else "/tmp/cron-export.json"

with open(jobs_file, 'r') as f:
    data = json.load(f)

jobs = data.get('jobs', [])
exported = []

for job in jobs:
    # Keep everything EXCEPT runtime state fields (machine-specific)
    exportable = {
        'id': job.get('id'),
        'agentId': job.get('agentId'),
        'sessionKey': job.get('sessionKey'),
        'name': job.get('name'),
        'enabled': job.get('enabled'),
        'createdAtMs': job.get('createdAtMs'),
        'updatedAtMs': job.get('updatedAtMs'),
        'schedule': job.get('schedule'),
        'sessionTarget': job.get('sessionTarget'),
        'wakeMode': job.get('wakeMode'),
        'payload': job.get('payload'),
        'delivery': job.get('delivery'),
        'description': job.get('description', ''),
    }
    exported.append(exportable)

output = {
    'exported_at': datetime.now().isoformat(),
    'version': '3.0.9',
    'type': 'openclaw_cron_jobs',
    'total_jobs': len(exported),
    'jobs': exported,
    'auth_token': None  # placeholder - will be filled below if available
}

# Also export gateway auth token if available (for --merge-auth restore)
gw_auth_token = None
try:
    with open(os.path.expanduser('~/.openclaw/openclaw.json'),'r') as f:
        gw_auth = json.load(f).get('gateway',{}).get('auth',{})
        gw_auth_token = gw_auth.get('token','')
except:
    pass

output['auth_token'] = gw_auth_token

with open(output_file, 'w') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"Exported {len(exported)} cron jobs")
PYTHON_SCRIPT
echo "✓ Exported cron jobs exported to $CRON_EXPORT_FILE"
else
    echo -e "  ${YELLOW}⚠ No cron jobs file found at $CRON_JOBS_FILE${NC}"
    # Create empty export
    python3 -c "import json; json.dump({'exported_at': '$(date -Iseconds)', 'version': '3.0.9', 'type': 'openclaw_cron_jobs', 'total_jobs': 0, 'jobs': []}, open('$CRON_EXPORT_FILE','w'))"
fi

echo ""

# 2. Backup system crontab (if exists)
echo -e "${YELLOW}[2/2] Backing up system crontab...${NC}"

if crontab -l &>/dev/null; then
    crontab -l > "$SYSTEM_CRONTAB_FILE"
    echo -e "  ${GREEN}✓ Created: $SYSTEM_CRONTAB_FILE${NC}"
else
    echo -e "  ${BLUE}○ No system crontab found${NC}"
    echo "# No crontab entries" > "$SYSTEM_CRONTAB_FILE"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Cron Backup Complete${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}File created:${NC}"
ls -lh "$CRON_EXPORT_FILE" "$SYSTEM_CRONTAB_FILE" 2>/dev/null
echo ""
echo -e "${BLUE}Note:${NC} Auth tokens (gateway_token, etc.) are NOT included for security."
echo "     Only job definitions are exported, not runtime credentials."
echo ""
