#!/bin/bash
#
# One-Click Restore for OpenClaw Workspace v3.0.8 (Merge Mode)
# Usage: ./one-click-restore.sh <backup_file> [--dry-run] [--force] [--with-sessions]
#
# Improvements in v3.0.8:
# - FIXED: cron tasks auto-restore (was manual-only)
# - FIXED: merge mode is now the default (--merge or implied)
# - Added version check to prevent script downgrade
#
# Improvements in v2.2.1:
# - FIXED: Cron export files correctly included in archive
#
# Improvements in v2.2:
# - Session records restore (optional)
# - Cron tasks integrated in main archive
# - Better disaster recovery
#

set -e

WORKSPACE_DIR="$HOME/.openclaw/workspace"
OPENCLAW_DIR="$HOME/.openclaw"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURRENT_VERSION="3.0.8"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Parse arguments
DRY_RUN=false
FORCE_MODE=false
WITH_SESSIONS=false
BACKUP_FILE=""

for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN=true
            ;;
        --force)
            FORCE_MODE=true
            ;;
        --with-sessions)
            WITH_SESSIONS=true
            ;;
        *)
            if [ -z "$BACKUP_FILE" ]; then
                BACKUP_FILE="$arg"
            fi
            ;;
    esac
done

show_usage() {
    echo -e "${YELLOW}Usage:${NC} $0 <backup_file> [options]"
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo "  --dry-run        Preview what would be restored"
    echo "  --force          Skip confirmation prompt"
    echo "  --with-sessions  Restore session records (conversation history)"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 ~/backups/clawmerge-20260321-191212.tar.gz"
    echo "  $0 ~/backups/clawmerge-*.tar.gz --with-sessions"
    echo "  $0 ~/backups/clawmerge-*.tar.gz --dry-run --force"
}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  OpenClaw Workspace Restore v3.0.9${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

if [ -z "$BACKUP_FILE" ] || [ "$BACKUP_FILE" = "--help" ]; then
    show_usage
    exit 1
fi

# Expand wildcard
if [[ "$BACKUP_FILE" == *"*"* ]]; then
    BACKUP_FILE=$(ls -t $BACKUP_FILE 2>/dev/null | head -1)
    if [ -z "$BACKUP_FILE" ]; then
        echo -e "${RED}Error: No backup files match the pattern${NC}"
        exit 1
    fi
    echo -e "${YELLOW}Using most recent:${NC} $BACKUP_FILE"
    echo ""
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}Error: Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

# Verify backup
echo -e "${YELLOW}Verifying backup...${NC}"
if ! tar -tzf "$BACKUP_FILE" > /dev/null 2>&1; then
    echo -e "${RED}Error: Invalid or corrupted backup file!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Backup verified${NC}"
echo ""

# Extract to temp
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

echo -e "${YELLOW}Extracting backup...${NC}"
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"
echo -e "${GREEN}✓ Extraction complete${NC}"
echo ""

# ============================================
# Security: Protect machine-specific credentials from being overwritten
# ============================================
echo -e "${YELLOW}[SECURITY] Protecting machine-specific credentials...${NC}"

# Files that are machine-specific and must NEVER be overwritten
PROTECTED_FILES=(
    "agents/main/agent/auth-profiles.json"
    "agents/main/agent/models.json"
    "openclaw.json"
    "exec-approvals.json"
)

PROTECTED_COUNT=0
for rel_path in "${PROTECTED_FILES[@]}"; do
    extracted_file="$TEMP_DIR/$rel_path"
    if [ -f "$extracted_file" ]; then
        mv "$extracted_file" "${extracted_file}.bak-$(date +%Y%m%d%H%M%S)"
        echo "  ✓ Protected (renamed to .bak): $rel_path"
        ((PROTECTED_COUNT++))
    fi
done

if [ "$PROTECTED_COUNT" -gt 0 ]; then
    echo -e "  ${GREEN}Protected $PROTECTED_COUNT machine-specific files${NC}"
    echo "  → These files will NOT be restored (preserves current machine credentials)"
else
    echo "  ○ No protected files found in backup"
fi
echo ""

# ============================================
# Version check: prevent old scripts from corrupting new configs
# ============================================
echo -e "${YELLOW}[VERSION CHECK]${NC}"
if [ -f "$TEMP_DIR/.backup-version" ]; then
    BACKUP_VER=$(cat "$TEMP_DIR/.backup-version")
    echo "  Backup version: $BACKUP_VER"
    echo "  Restore version: $CURRENT_VERSION"
    if [ "$BACKUP_VER" != "$CURRENT_VERSION" ]; then
        echo -e "  ${YELLOW}⚠ Version mismatch!${NC}"
        echo "  This restore script (v$CURRENT_VERSION) may not be fully compatible with backup (v$BACKUP_VER)."
        read -p "Continue anyway? [y/N] " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}Restore cancelled${NC}"
            exit 1
        fi
    else
        echo -e "  ${GREEN}✓ Version match${NC}"
    fi
else
    echo "  ○ No version tag in backup (old format)"
fi
echo ""

# Preview
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Restore Preview${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

MEMORY_COUNT=$(ls -1 "$TEMP_DIR/memory/"*.md 2>/dev/null | wc -l || echo 0)
SKILLS_COUNT=$(ls -1d "$TEMP_DIR/skills/"*/ 2>/dev/null | wc -l || echo 0)
HAS_SESSIONS=false
[ -d "$TEMP_DIR/.backup-sessions" ] && HAS_SESSIONS=true

echo -e "${YELLOW}Contents:${NC}"
[ -f "$TEMP_DIR/MEMORY.md" ] && echo "  ✓ MEMORY.md"
[ "$MEMORY_COUNT" -gt 0 ] && echo "  ✓ $MEMORY_COUNT memory files"
[ "$SKILLS_COUNT" -gt 0 ] && echo "  ✓ $SKILLS_COUNT skills"
[ "$HAS_SESSIONS" = true ] && echo "  ✓ Session records (conversation history)"

# Check for cron files
CRON_FILES=$(ls "$TEMP_DIR"/cron-tasks-*.json 2>/dev/null || true)
[ -n "$CRON_FILES" ] && echo "  ✓ Cron tasks configuration"

echo ""

# Dry run
if [ "$DRY_RUN" = true ]; then
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  DRY RUN - No files will be modified${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}Would merge:${NC}"
    echo "  - memory/ files: Copy new, skip existing"
    echo "  - MEMORY.md: Append unique date entries"
    echo "  - skills/: Install new only"
    [ "$HAS_SESSIONS" = true ] && echo "  - sessions/: Restore conversation history"
    [ -n "$CRON_FILES" ] && echo "  - cron tasks: Import configuration"
    echo ""
    echo -e "${GREEN}Done! (no files modified)${NC}"
    exit 0
fi

# Confirm
if [ "$FORCE_MODE" != true ]; then
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    read -p "Proceed with restore? [y/N] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Restore cancelled${NC}"
        exit 0
    fi
fi

# ============================================
# Disaster Recovery
# ============================================
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}  Creating disaster recovery backup...${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

DISASTER_BACKUP_DIR="$OPENCLAW_DIR/.local-backup/restore-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$DISASTER_BACKUP_DIR"

if [ -d "$WORKSPACE_DIR" ]; then
    echo -e "${YELLOW}Backing up current workspace...${NC}"
    
    for file in MEMORY.md USER.md IDENTITY.md SOUL.md AGENTS.md TOOLS.md HEARTBEAT.md; do
        if [ -f "$WORKSPACE_DIR/$file" ]; then
            cp "$WORKSPACE_DIR/$file" "$DISASTER_BACKUP_DIR/" 2>/dev/null || true
            echo "  ✓ Backed up: $file"
        fi
    done
    
    if [ -d "$WORKSPACE_DIR/memory" ]; then
        cp -r "$WORKSPACE_DIR/memory" "$DISASTER_BACKUP_DIR/" 2>/dev/null || true
        echo "  ✓ Backed up: memory/"
    fi
    
    if [ -d "$WORKSPACE_DIR/skills" ]; then
        cp -r "$WORKSPACE_DIR/skills" "$DISASTER_BACKUP_DIR/" 2>/dev/null || true
        echo "  ✓ Backed up: skills/"
    fi
    
    echo ""
    echo -e "${GREEN}✓ Disaster recovery backup created${NC}"
    echo -e "${BLUE}  Location: $DISASTER_BACKUP_DIR${NC}"
fi
echo ""

# Create workspace if needed
mkdir -p "$WORKSPACE_DIR"

# ============================================
# 1. Merge memory/ files
# ============================================
echo -e "${BLUE}[1/5] Merging memory/ files...${NC}"
if [ -d "$TEMP_DIR/memory" ]; then
    mkdir -p "$WORKSPACE_DIR/memory"
    COPIED=0
    SKIPPED=0
    
    for file in "$TEMP_DIR/memory/"*.md; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            dest="$WORKSPACE_DIR/memory/$filename"
            
            if [ ! -f "$dest" ]; then
                cp "$file" "$dest"
                echo "  ✓ Copied: $filename"
                ((COPIED++))
            else
                echo "  ○ Skipped (exists): $filename"
                ((SKIPPED++))
            fi
        fi
    done
    
    echo -e "  ${GREEN}Copied: $COPIED, Skipped: $SKIPPED${NC}"
else
    echo "  ○ No memory/ files in backup"
fi
echo ""

# ============================================
# 2. Merge MEMORY.md
# ============================================
echo -e "${BLUE}[2/5] Merging MEMORY.md...${NC}"
if [ -f "$TEMP_DIR/MEMORY.md" ]; then
    if [ ! -f "$WORKSPACE_DIR/MEMORY.md" ]; then
        cp "$TEMP_DIR/MEMORY.md" "$WORKSPACE_DIR/MEMORY.md"
        echo -e "  ${GREEN}Created new MEMORY.md${NC}"
    else
        EXISTING_DATES=$(grep -oP '^## \d{4}-\d{2}-\d{2}' "$WORKSPACE_DIR/MEMORY.md" | sort -u || true)
        NEW_ENTRIES=0
        
        current_entry=""
        current_date=""
        
        while IFS= read -r line; do
            if [[ "$line" =~ ^##\ ([0-9]{4}-[0-9]{2}-[0-9]{2}) ]]; then
                if [ -n "$current_date" ] && [ -n "$current_entry" ]; then
                    if ! echo "$EXISTING_DATES" | grep -q "## $current_date"; then
                        echo -e "\n$current_entry" >> "$WORKSPACE_DIR/MEMORY.md"
                        echo "  ✓ Added entry: $current_date"
                        ((NEW_ENTRIES++))
                    fi
                fi
                current_date="${BASH_REMATCH[1]}"
                current_entry="$line"
            elif [ -n "$current_date" ]; then
                current_entry="$current_entry"$'\n'"$line"
            fi
        done < "$TEMP_DIR/MEMORY.md"
        
        if [ -n "$current_date" ] && [ -n "$current_entry" ]; then
            if ! echo "$EXISTING_DATES" | grep -q "## $current_date"; then
                echo -e "\n$current_entry" >> "$WORKSPACE_DIR/MEMORY.md"
                echo "  ✓ Added entry: $current_date"
                ((NEW_ENTRIES++))
            fi
        fi
        
        echo -e "  ${GREEN}Added $NEW_ENTRIES new entries${NC}"
    fi
else
    echo "  ○ No MEMORY.md in backup"
fi
echo ""

# ============================================
# 3. Merge skills/
# ============================================
echo -e "${BLUE}[3/5] Merging skills/...${NC}"
if [ -d "$TEMP_DIR/skills" ]; then
    mkdir -p "$WORKSPACE_DIR/skills"
    INSTALLED=0
    SKIPPED=0
    
    for skill_dir in "$TEMP_DIR/skills/"*/; do
        if [ -d "$skill_dir" ]; then
            skill_name=$(basename "$skill_dir")
            dest="$WORKSPACE_DIR/skills/$skill_name"
            
            if [ ! -d "$dest" ]; then
                cp -r "$skill_dir" "$dest"
                echo "  ✓ Installed: $skill_name"
                ((INSTALLED++))
            else
                echo "  ○ Skipped (exists): $skill_name"
                ((SKIPPED++))
            fi
        fi
    done
    
    echo -e "  ${GREEN}Installed: $INSTALLED, Skipped: $SKIPPED${NC}"
else
    echo "  ○ No skills/ in backup"
fi
echo ""

# ============================================
# 4. Restore session records (optional)
# ============================================
if [ "$WITH_SESSIONS" = true ] || [ "$HAS_SESSIONS" = true ]; then
    echo -e "${BLUE}[4/5] Restoring session records...${NC}"
    
    if [ -d "$TEMP_DIR/.backup-sessions" ]; then
        SESSIONS_DIR="$OPENCLAW_DIR/agents/main/sessions"
        
        if [ -d "$SESSIONS_DIR" ]; then
            echo -e "${YELLOW}Backing up current sessions...${NC}"
            BACKUP_SESSIONS_DIR="$OPENCLAW_DIR/.local-backup/sessions-$(date +%Y%m%d-%H%M%S)"
            mkdir -p "$BACKUP_SESSIONS_DIR"
            cp -r "$SESSIONS_DIR"/* "$BACKUP_SESSIONS_DIR/" 2>/dev/null || true
            echo "  ✓ Sessions backed up to: $BACKUP_SESSIONS_DIR"
        fi
        
        echo -e "${YELLOW}Restoring sessions...${NC}"
        mkdir -p "$SESSIONS_DIR"
        cp -r "$TEMP_DIR/.backup-sessions/"* "$SESSIONS_DIR/" 2>/dev/null || true
        echo -e "  ${GREEN}✓ Session records restored${NC}"
    else
        echo "  ○ No session records in backup (use --with-sessions to include)"
    fi
    echo ""
else
    echo -e "${BLUE}[4/5] Skipping session records${NC}"
    echo "  ○ Use --with-sessions to restore conversation history"
    echo ""
fi

# ============================================
# 5. Restore cron tasks
# ============================================
echo -e "${BLUE}[5/5] Restoring cron tasks (merge mode)...${NC}"

CRON_FILES=$(ls "$TEMP_DIR"/cron-tasks-*.json 2>/dev/null || true)
if [ -n "$CRON_FILES" ]; then
    echo -e "${YELLOW}Found cron tasks in backup${NC}"
    LATEST_CRON=$(ls -t $TEMP_DIR/cron-tasks-*.json 2>/dev/null | head -1)
    echo "  → $LATEST_CRON"
    echo ""
    echo -e "${BLUE}Running merge restore...${NC}"
    bash "$SCRIPT_DIR/restore-cron-tasks.sh" "$LATEST_CRON" --dry-run
    echo ""
    read -p "Proceed with merge? [y/N] " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        bash "$SCRIPT_DIR/restore-cron-tasks.sh" "$LATEST_CRON"
        echo ""
        echo -e "${YELLOW}Restart gateway to activate:${NC}"
        echo "  openclaw gateway restart"
    else
        echo "Skipped cron merge."
    fi
else
    echo "  ○ No cron tasks backup found"
fi
echo ""

# ============================================
# Summary
# ============================================
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Restore Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Workspace: ${YELLOW}$WORKSPACE_DIR${NC}"
echo ""

if [ -d "$DISASTER_BACKUP_DIR" ]; then
    echo -e "${CYAN}Disaster Recovery Backup:${NC}"
    echo -e "  ${BLUE}$DISASTER_BACKUP_DIR${NC}"
    echo ""
fi

echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Review merged files if needed"
echo "  2. Restart OpenClaw: openclaw gateway restart"
echo ""
echo -e "${GREEN}Done!${NC}"
