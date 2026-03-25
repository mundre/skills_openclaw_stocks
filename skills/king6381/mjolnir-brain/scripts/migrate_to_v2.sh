#!/bin/bash
#
# migrate_to_v2.sh - Mjolnir Brain v1.0 to v2.0 Migration Script
#
# Migrates existing v1.0 single-user installations to v2.0 multi-user structure.
# Preserves all existing data under the 'default' user for backward compatibility.
#
# What this script does:
# 1. Creates new multi-user directory structure (users/, shared/)
# 2. Moves existing memory files to users/default/
# 3. Preserves v1.0 compatibility (single users work without changes)
# 4. Sets appropriate permissions
#
# Usage:
#   scripts/migrate_to_v2.sh
#
# Before running:
# - Backup your workspace (recommended)
# - Ensure you're in the mjolnir-brain project directory
#

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MEMORY_DIR="${PROJECT_ROOT}/templates/memory"
USERS_DIR="${MEMORY_DIR}/users"
SHARED_DIR="${MEMORY_DIR}/shared"

# Colors for output
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

print_error() {
    echo -e "${RED}ERROR: $1${NC}" >&2
}

print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_info() {
    echo -e "${BLUE}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    if [[ ! -d "$MEMORY_DIR" ]]; then
        print_error "Memory directory not found: $MEMORY_DIR"
        print_info "Run this script from the mjolnir-brain project directory"
        exit 1
    fi
}

# Create new directory structure
create_directory_structure() {
    print_info "Creating multi-user directory structure..."
    
    # Create users directory
    mkdir -p "$USERS_DIR"
    
    # Create shared directories
    mkdir -p "$SHARED_DIR"/{projects,decisions,playbooks}
    
    # Create .gitkeep files
    touch "${USERS_DIR}/.gitkeep"
    touch "${SHARED_DIR}/.gitkeep"
    
    print_success "Directory structure created"
}

# Migrate existing files to default user
migrate_existing_files() {
    print_info "Migrating existing v1.0 files to 'default' user..."
    
    local default_user_dir="${USERS_DIR}/default"
    local migrated_count=0
    
    # Create default user directory
    mkdir -p "$default_user_dir"
    
    # Move daily log files (YYYY-MM-DD.md pattern)
    for log_file in "${MEMORY_DIR}"/*.md; do
        if [[ -f "$log_file" ]]; then
            local filename
            filename=$(basename "$log_file")
            
            # Skip template files that should stay at root level
            case "$filename" in
                .gitkeep)
                    continue
                    ;;
            esac
            
            # Check if it looks like a daily log (YYYY-MM-DD.md pattern)
            if [[ "$filename" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}\.md$ ]]; then
                mv "$log_file" "${default_user_dir}/"
                print_info "  Moved: $filename → users/default/"
                ((migrated_count++))
            fi
        fi
    done
    
    # Move MEMORY.md if it exists at root level
    if [[ -f "${MEMORY_DIR}/MEMORY.md" ]]; then
        mv "${MEMORY_DIR}/MEMORY.md" "${default_user_dir}/MEMORY.md"
        print_info "  Moved: MEMORY.md → users/default/"
        ((migrated_count++))
    fi
    
    if [[ $migrated_count -eq 0 ]]; then
        print_info "  No existing files to migrate (fresh installation)"
    else
        print_success "Migrated $migrated_count file(s) to default user"
    fi
}

# Create README files
create_readme_files() {
    print_info "Creating README files..."
    
    # Users directory README
    cat > "${USERS_DIR}/README.md" << 'EOF'
# User Memory Isolation

This directory contains per-user memory files for multi-user Mjolnir Brain deployments.

## Structure

```
users/
├── default/           # Default user (v1.0 compatibility)
│   ├── MEMORY.md      # Long-term personal memory
│   └── YYYY-MM-DD.md  # Daily session logs
├── alice/             # User: alice
│   ├── MEMORY.md
│   └── YYYY-MM-DD.md
└── bob/               # User: bob
    ├── MEMORY.md
    └── YYYY-MM-DD.md
```

## How User Resolution Works

The system determines the current user using this priority:

1. **Environment variable** `MJOLNIR_USER` (highest priority)
2. **File** `~/.mjolnir_current_user` (session persistence)
3. **Default**: `default` (v1.0 backward compatibility)

## Privacy & Permissions

- **Personal memory** (`users/{user}/`): Mode 600 — only readable by the user
- **Shared memory** (`shared/`): Mode 644 — readable by all users

## Usage

```bash
# List all users
scripts/user.sh list

# Create a new user
scripts/user.sh create alice

# Switch to a user
scripts/user.sh switch alice

# Check current user
scripts/user.sh whoami
```

## v1.0 Compatibility

Single-user deployments don't need to configure anything. All existing memory files work as before under the `default` user.

EOF
    
    # Shared directory README
    cat > "${SHARED_DIR}/README.md" << 'EOF'
# Shared Memory

This directory contains memory shared across all users in a multi-user Mjolnir Brain deployment.

## Structure

```
shared/
├── projects/       # Project-specific memory (shared)
├── decisions/      # Team decisions (shared)
└── playbooks/      # Shared playbooks and procedures
```

## Access

All files in this directory are readable by all users (permission 644).

## Usage

- **projects/**: Store project context that multiple team members need
- **decisions/**: Record team decisions that affect everyone
- **playbooks/**: Shared procedures and runbooks

## Personal vs Shared

| Type | Location | Access |
|------|----------|--------|
| Personal logs | `users/{user}/YYYY-MM-DD.md` | Owner only (600) |
| Personal memory | `users/{user}/MEMORY.md` | Owner only (600) |
| Team decisions | `shared/decisions/` | All users (644) |
| Project context | `shared/projects/` | All users (644) |

EOF
    
    print_success "README files created"
}

# Set permissions
set_permissions() {
    print_info "Setting file permissions..."
    
    # User directories: 700 for dirs, 600 for files
    find "$USERS_DIR" -mindepth 1 -maxdepth 1 -type d -exec chmod 700 {} \;
    find "$USERS_DIR" -type f -exec chmod 600 {} \;
    
    # Shared directories: 755 for dirs, 644 for files
    chmod 755 "$SHARED_DIR"
    find "$SHARED_DIR" -type d -exec chmod 755 {} \;
    find "$SHARED_DIR" -type f -exec chmod 644 {} \;
    
    print_success "Permissions set"
}

# Show migration summary
show_summary() {
    echo ""
    print_success "=========================================="
    print_success "Migration to v2.0 Complete!"
    print_success "=========================================="
    echo ""
    print_info "What changed:"
    print_info "  ✓ Created multi-user directory structure"
    print_info "  ✓ Migrated existing files to 'default' user"
    print_info "  ✓ Set appropriate file permissions"
    print_info "  ✓ Created README documentation"
    echo ""
    print_info "Your existing data is now in:"
    print_info "  ${USERS_DIR}/default/"
    echo ""
    print_info "Next steps:"
    print_info "  1. Test that everything works: scripts/user.sh whoami"
    print_info "  2. Create additional users: scripts/user.sh create <name>"
    print_info "  3. Read the docs: docs/multi-user.md"
    echo ""
    print_warning "Note: v1.0 compatibility is preserved. Single-user setups"
    print_warning "      continue to work without any configuration changes."
}

# Main function
main() {
    print_info "Mjolnir Brain v1.0 → v2.0 Migration"
    print_info "===================================="
    echo ""
    
    check_prerequisites
    
    print_warning "This script will reorganize your memory directory structure."
    print_warning "Your data will be preserved under the 'default' user."
    echo ""
    read -p "Continue? [y/N] " confirm
    
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        print_info "Migration cancelled."
        exit 0
    fi
    
    echo ""
    create_directory_structure
    migrate_existing_files
    create_readme_files
    set_permissions
    
    show_summary
}

main "$@"
