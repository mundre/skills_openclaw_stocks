#!/bin/bash
# archive.sh — Self-improvement Hot/Cold ETL
# v4.0 — silent 模式：无交互确认，dry-run 预览后自动执行
# 设计原则：「脚本做机械，AI 做语义」
# Modes:
#   --dry-run   — 只输出预览，不写入文件
#   (no args)   — Silent 执行：预览 + 自动归档，无交互
#   (no args)   — 执行归档（先 dry-run 显示摘要，等待确认）

WORKSPACE="${HOME}/.openclaw/workspace"
LEARNINGS_DIR="$WORKSPACE/.learnings"
ARCHIVE_DIR="$LEARNINGS_DIR/archive"
TIMESTAMP=$(date '+%Y-%m-%dT%H:%M:%S+08:00')
TODAY_MONTH=$(date '+%Y-%m')
DRY_RUN=false

# ── Parse args ──────────────────────────────────────────────
if [ "$1" = "--dry-run" ]; then
    DRY_RUN=true
fi
if [ "$1" = "--write-notified" ]; then
    JSON_FILE="$2"
    [ -z "$JSON_FILE" ] && echo "Error: --write-notified requires JSON file" && exit 1
    [ ! -f "$JSON_FILE" ] && echo "Error: JSON file not found: $JSON_FILE" && exit 1
    WRITE_NOTIFIED_PY="$WORKSPACE/scripts/self-improvement/write_notified.py"
    python3 "$WRITE_NOTIFIED_PY" "$JSON_FILE" "$LEARNINGS_DIR"
    exit $?
fi




# ── Ensure archive dir exists ────────────────────────────────
mkdir -p "$ARCHIVE_DIR"

# ── Source file → source tag mapping ─────────────────────────
source_tag() {
    case "$1" in
        *LEARNINGS*)       echo "LEARNINGS" ;;
        *ERRORS*)          echo "ERRORS" ;;
        *FEATURE*)         echo "FEATURE" ;;
        *)                 echo "UNKNOWN" ;;
    esac
}

# ── Normalize status for outcome field ──────────────────────
normalize_outcome() {
    case "$1" in
        promoted)  echo "promoted" ;;
        resolved)  echo "resolved" ;;
        *)         echo "resolved" ;;
    esac
}

# ── Extract field value from MD entry ──────────────────────
extract_field() {
    local entry="$1"
    local field="$2"
    # Handle two formats: ### Field (value on next line) or **Field**: value (same line)
    local val
    # Try: ### Field (value on next line)
    val=$(echo "$entry" | awk -v f="### $field" 'index($0,f)==1{getline; print}')
    [ -z "$val" ] && val=$(echo "$entry" | awk -v f="$field" 'index($0,f)==1{ sub(/.*:[[:space:]]*/,""); print }')
    echo "$val" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//'
}

extract_meta() {
    local entry="$1"
    local key="$2"
    # Handle: - Key: value (standard) or **Key**: value (bold inline)
    local val
    val=$(echo "$entry" | grep "^[[:space:]]*- $key:" | sed 's/.*:[[:space:]]*//')
    [ -z "$val" ] && val=$(echo "$entry" | grep "^[[:space:]]*\*\*$key" | sed 's/.*\*://')
    echo "$val" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//'
}

# ── Process a single MD file, emit JSONL lines ───────────────
process_file() {
    local file="$1"
    [ ! -f "$file" ] && return

    local src_tag
    src_tag=$(source_tag "$file")

    local in_entry=false
    local entry_id="" entry_cat="" entry_lines="" current_status=""
    local title="" summary="" details="" suggested_action="" tags_str=""

    while IFS= read -r line; do
        case "$line" in
            "## ["*)
                # Emit previous entry if it's resolved/promoted
                if $in_entry && [ -n "$entry_id" ]; then
                    case "$current_status" in
                        resolved|promoted)
                            local outcome
                            outcome=$(normalize_outcome "$current_status")
                            local logged_at resolved_at archived_at
                            logged_at=$(extract_meta "$entry_lines" "Logged")
                            # resolved_at: use archived_at as proxy (entry doesn't store resolve time)
                            resolved_at="$TIMESTAMP"
                            local pattern_key entry_id_short title_text
                            pattern_key=$(extract_meta "$entry_lines" "Pattern-Key")
                            entry_id_short=$(echo "$entry_id" | sed 's/^## \[//;s/\].*//')
                            title_text=$(echo "$entry_id" | sed -n 's/^## \[[^]]*] //p')
                            summary=$(extract_field "$entry_lines" "Summary")
                            details=$(extract_field "$entry_lines" "Details")
                            suggested_action=$(extract_field "$entry_lines" "Suggested Action")
                            tags_str=$(extract_meta "$entry_lines" "Tags")
                            local recurrence
                            recurrence=$(extract_meta "$entry_lines" "Recurrence-Count")

                            # Escape JSON strings
                            summary=${summary//\\/\\\\}
                            summary=${summary//\"/\\\"}
                            details=${details//\\/\\\\}
                            details=${details//\"/\\\"}
                            suggested_action=${suggested_action//\\/\\\\}
                            suggested_action=${suggested_action//\"/\\\"}
                            tags_str=${tags_str//\\/\\\\}
                            tags_str=${tags_str//\"/\\\"}
                            title_text=${title_text//\\/\\\\}
                            title_text=${title_text//\"/\\\"}
                            pattern_key=${pattern_key//\\/\\\\}
                            pattern_key=${pattern_key//\"/\\\"}

                            # Build tags JSON array
                            if [ -n "$tags_str" ]; then
                                local tag_json
                                tag_json=$(echo "$tags_str" | sed "s/, *//g; s/^/\"/; s/$/\"/; s/\"/\\\"\"/g" | tr '\n' ',' | sed 's/,$//')
                                tag_json="[${tag_json}]"
                            else
                                tag_json="[]"
                            fi

                            echo "{\"archived_at\":\"$TIMESTAMP\",\"source_file\":\"$src_tag\",\"outcome\":\"$outcome\",\"entry_id\":\"$entry_id_short\",\"pattern_key\":\"$pattern_key\",\"category\":\"$entry_cat\",\"logged_at\":\"$logged_at\",\"resolved_at\":\"$resolved_at\",\"title\":\"$title_text\",\"summary\":\"$summary\",\"details\":\"$details\",\"suggested_action\":\"$suggested_action\",\"tags\":$tag_json,\"recurrence_count\":$recurrence}"
                            ;;
                    esac
                fi
                # Start new entry
                in_entry=true
                entry_id="$line"
                entry_cat=$(echo "$line" | sed -n 's/^## \[[^ ]*] //p' | tr -d '[:space:]')
                [ -z "$entry_cat" ] && entry_cat="uncategorized"
                entry_lines="$line"$'\n'
                current_status=""
                title=""
                ;;
            *)
                if $in_entry; then
                    entry_lines="$entry_lines$line"$'\n'
                    if echo "$line" | grep -qi "^[[:space:]]*\*\*Status"; then
                        current_status=$(echo "$line" | sed 's/\*\*/./g; s/.*://' | sed 's/^[[:space:]]*//; s/[[:space:]].*//' | tr -d '[:space:]' | tr "[:upper:]" "[:lower:]")
                    fi
                fi
                ;;
        esac
    done < "$file"

    # Flush last entry
    if $in_entry && [ -n "$entry_id" ]; then
        case "$current_status" in
            resolved|promoted)
                local outcome
                outcome=$(normalize_outcome "$current_status")
                local logged_at resolved_at
                logged_at=$(extract_meta "$entry_lines" "Logged")
                resolved_at="$TIMESTAMP"
                local pattern_key entry_id_short title_text
                pattern_key=$(extract_meta "$entry_lines" "Pattern-Key")
                entry_id_short=$(echo "$entry_id" | sed 's/^## \[//;s/\].*//')
                title_text=$(echo "$entry_id" | sed -n 's/^## \[[^]]*] //p')
                summary=$(extract_field "$entry_lines" "Summary")
                details=$(extract_field "$entry_lines" "Details")
                suggested_action=$(extract_field "$entry_lines" "Suggested Action")
                tags_str=$(extract_meta "$entry_lines" "Tags")
                local recurrence
                recurrence=$(extract_meta "$entry_lines" "Recurrence-Count")

                summary=${summary//\\/\\\\}; summary=${summary//\"/\\\"}
                details=${details//\\/\\\\}; details=${details//\"/\\\"}
                suggested_action=${suggested_action//\\/\\\\}; suggested_action=${suggested_action//\"/\\\"}
                tags_str=${tags_str//\\/\\\\}; tags_str=${tags_str//\"/\\\"}
                title_text=${title_text//\\/\\\\}; title_text=${title_text//\"/\\\"}
                pattern_key=${pattern_key//\\/\\\\}; pattern_key=${pattern_key//\"/\\\"}

                if [ -n "$tags_str" ]; then
                    tag_json=$(echo "$tags_str" | sed "s/, */\",\"/g; s/^/\"/; s/$/\"/")
                    tag_json="[$tag_json]"
                else
                    tag_json="[]"
                fi

                echo "{\"archived_at\":\"$TIMESTAMP\",\"source_file\":\"$src_tag\",\"outcome\":\"$outcome\",\"entry_id\":\"$entry_id_short\",\"pattern_key\":\"$pattern_key\",\"category\":\"$entry_cat\",\"logged_at\":\"$logged_at\",\"resolved_at\":\"$resolved_at\",\"title\":\"$title_text\",\"summary\":\"$summary\",\"details\":\"$details\",\"suggested_action\":\"$suggested_action\",\"tags\":$tag_json,\"recurrence_count\":$recurrence}"
                ;;
        esac
    fi
}

# ── Collect all archive candidates ────────────────────────────
PREVIEW_FILE="/tmp/archive-preview-$(date '+%Y%m%d').txt"
> "$PREVIEW_FILE"

total_candidates=0
for file in "$LEARNINGS_DIR/LEARNINGS.md" "$LEARNINGS_DIR/ERRORS.md" "$LEARNINGS_DIR/FEATURE_REQUESTS.md"; do
    [ ! -f "$file" ] && continue
    count=$(grep -c "^## \[" "$file" 2>/dev/null || echo 0)
    resolved_count=$( { grep -ciE "resolved|promoted" "$file" || true; } | tail -1 )
    if [ "$resolved_count" -gt 0 ] 2>/dev/null; then
        echo ">>> $file ($resolved_count / $count entries will be archived)" >> "$PREVIEW_FILE"
        process_file "$file" >> "$PREVIEW_FILE"
        echo "" >> "$PREVIEW_FILE"
        total_candidates=$(( total_candidates + resolved_count ))
    fi
done

# ── Dry-run: show preview and exit ──────────────────────────
echo "=== Archive Dry-Run — $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "Archive dir: $ARCHIVE_DIR"
echo "Target file: $ARCHIVE_DIR/$TODAY_MONTH.jsonl"
echo ""
if [ "$total_candidates" -eq 0 ]; then
    echo "No resolved/promoted entries found. Nothing to archive."
    echo ""
    cat "$PREVIEW_FILE"
    echo ""
    echo "[DRY-RUN complete — no files modified]"
    exit 0
fi

echo "Total entries to archive: $total_candidates"
echo ""
echo "--- PREVIEW (first 20 entries) ---"
head -20 "$PREVIEW_FILE"
if [ "$(wc -l < "$PREVIEW_FILE")" -gt 20 ]; then
    echo "... (truncated, $total_candidates entries total)"
fi
echo ""

if [ "$DRY_RUN" = true ]; then
    echo "[DRY-RUN — no files modified]"
    exit 0
fi

# ── Execute: write JSONL ─────────────────────────────────────
ARCHIVE_FILE="$ARCHIVE_DIR/$TODAY_MONTH.jsonl"
touch "$ARCHIVE_FILE"
cat "$PREVIEW_FILE" >> "$ARCHIVE_FILE"
echo "Appended to $ARCHIVE_FILE"

# ── Execute: remove archived entries from MD files ───────────
remove_archived_entries() {
    local file="$1"
    [ ! -f "$file" ] && return

    local tmpfile
    tmpfile=$(mktemp)
    local in_entry=false
    local current_status=""
    local entry_lines=""
    local entry_id=""

    while IFS= read -r line; do
        case "$line" in
            "## ["*)
                # Process previous entry
                if $in_entry && [ -n "$entry_id" ]; then
                    case "$current_status" in
                        resolved|promoted)
                            # Skip: do not write resolved/promoted entries
                            ;;
                        *)
                            # Keep: write accumulated lines
                            printf '%s\n' "$entry_lines" >> "$tmpfile"
                            ;;
                    esac
                fi
                in_entry=true
                entry_id="$line"
                entry_lines="$line"$'\n'
                current_status=""
                ;;
            *)
                if $in_entry; then
                    entry_lines="$entry_lines$line"$'\n'
                    if echo "$line" | grep -qi "^[[:space:]]*\*\*Status"; then
                        current_status=$(echo "$line" | sed 's/\*\*/./g; s/.*://' | sed 's/^[[:space:]]*//; s/[[:space:]].*//' | tr -d '[:space:]' | tr "[:upper:]" "[:lower:]")
                    fi
                fi
                ;;
        esac
    done < "$file"

    # Flush last entry
    if $in_entry && [ -n "$entry_id" ]; then
        case "$current_status" in
            resolved|promoted) ;;  # skip
            *) printf '%s\n' "$entry_lines" >> "$tmpfile" ;;
        esac
    fi

    mv "$tmpfile" "$file"
}

for file in "$LEARNINGS_DIR/LEARNINGS.md" "$LEARNINGS_DIR/ERRORS.md" "$LEARNINGS_DIR/FEATURE_REQUESTS.md"; do
    [ ! -f "$file" ] && continue
    if grep -qi "Status.*resolved\\|Status.*promoted" "$file" 2>/dev/null; then
        remove_archived_entries "$file"
        echo "Cleaned: $file"
    fi
done

echo ""
echo "=== Archive Complete ==="
echo "Archived $total_candidates entries to $ARCHIVE_DIR/$TODAY_MONTH.jsonl"
echo "MD files cleaned."
