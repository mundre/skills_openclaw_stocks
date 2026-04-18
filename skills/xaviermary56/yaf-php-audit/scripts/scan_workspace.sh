#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <workspace-root> [output-dir]" >&2
  exit 1
fi

workspace_root="$1"
output_dir="${2:-$workspace_root/audit-output}"

if [ ! -d "$workspace_root" ]; then
  echo "[ERROR] workspace root not found: $workspace_root" >&2
  exit 1
fi

script_dir="$(cd "$(dirname "$0")" && pwd)"
project_scan="$script_dir/scan_project.sh"

if [ ! -x "$project_scan" ]; then
  echo "[ERROR] missing executable project scanner: $project_scan" >&2
  exit 1
fi

mkdir -p "$output_dir/projects"
summary_csv="$output_dir/summary.csv"
summary_md="$output_dir/summary.md"
high_risk_txt="$output_dir/high-risk.txt"

echo 'project,risk_level,dangerous_hits,raw_input_hits,callback_hits,payment_hits,task_hits,php_new_syntax_hits,hardcoded_hits,loopdb_hits,staticcache_hits,notes' > "$summary_csv"
: > "$high_risk_txt"

{
  echo "# Workspace Audit Summary"
  echo
  echo "- workspace: $workspace_root"
  echo "- generated_at: $(date '+%Y-%m-%d %H:%M:%S %z')"
  echo
  echo "| project | risk | dangerous | raw input | callback | payment | task | php 7.4+/8.x | hardcoded | loop+db | static-cache | notes |"
  echo "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"
} > "$summary_md"

count_hits() {
  local file="$1"
  local section="$2"
  awk -v section="$section" '
    $0 == "=== " section " ===" { in_section=1; next }
    /^=== / && in_section { exit }
    in_section && NF { count++ }
    END { print count+0 }
  ' "$file"
}

risk_level() {
  local dangerous="$1"
  local raw="$2"
  local callback="$3"
  local payment="$4"
  local task="$5"
  local phpnew="$6"
  local hardcoded="$7"

  if [ "$dangerous" -ge 5 ] || { [ "$callback" -ge 10 ] && [ "$payment" -ge 10 ]; } || [ "$task" -ge 15 ] || [ "$hardcoded" -ge 3 ]; then
    echo "high"
  elif [ "$dangerous" -ge 1 ] || [ "$callback" -ge 3 ] || [ "$payment" -ge 3 ] || [ "$raw" -ge 20 ] || [ "$phpnew" -ge 1 ] || [ "$hardcoded" -ge 1 ]; then
    echo "medium"
  else
    echo "low"
  fi
}

project_notes() {
  local dangerous="$1"
  local callback="$2"
  local payment="$3"
  local task="$4"
  local raw="$5"
  local hardcoded="$6"
  local loopdb="$7"
  local staticcache="$8"
  local notes=()

  [ "$dangerous" -ge 1 ] && notes+=("dangerous-fns")
  [ "$callback" -ge 3 ] && notes+=("callback-heavy")
  [ "$payment" -ge 3 ] && notes+=("payment-heavy")
  [ "$task" -ge 5 ] && notes+=("task-heavy")
  [ "$raw" -ge 20 ] && notes+=("raw-input-heavy")
  [ "$hardcoded" -ge 1 ] && notes+=("hardcoded-creds")
  [ "$loopdb" -ge 1 ] && notes+=("loop-db-risk")
  [ "$staticcache" -ge 1 ] && notes+=("static-cache")

  if [ "${#notes[@]}" -eq 0 ]; then
    echo "general-review"
  else
    local IFS=';'
    echo "${notes[*]}"
  fi
}

find "$workspace_root" -mindepth 1 -maxdepth 1 -type d | sort | while read -r project_dir; do
  project_name="$(basename "$project_dir")"

  case "$project_name" in
    .git|dist|skills|audit-output|audit-output-test|vendor|node_modules)
      continue
      ;;
  esac

  report_file="$output_dir/projects/${project_name}.txt"
  if ! bash "$project_scan" "$project_dir" "$report_file" >/dev/null 2>&1; then
    echo "[WARN] scan failed: $project_name" >&2
    echo "$project_name,scan_failed,0,0,0,0,0,0,0,0,0,scan-failed" >> "$summary_csv"
    echo "| $project_name | scan_failed | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | scan-failed |" >> "$summary_md"
    continue
  fi

  dangerous="$(count_hits "$report_file" "dangerous functions")"
  raw="$(count_hits "$report_file" "raw superglobals")"
  callback="$(count_hits "$report_file" "callback and notify keywords")"
  payment="$(count_hits "$report_file" "payment keywords")"
  task="$(count_hits "$report_file" "task and cron keywords")"
  phpnew="$(count_hits "$report_file" "php 7.4+ syntax suspects")"
  hardcoded="$(count_hits "$report_file" "hardcoded credentials suspects")"
  loopdb="$(count_hits "$report_file" "loop with db suspects")"
  staticcache="$(count_hits "$report_file" "static array cache antipattern")"
  risk="$(risk_level "$dangerous" "$raw" "$callback" "$payment" "$task" "$phpnew" "$hardcoded")"
  notes="$(project_notes "$dangerous" "$callback" "$payment" "$task" "$raw" "$hardcoded" "$loopdb" "$staticcache")"

  printf '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' \
    "$project_name" "$risk" "$dangerous" "$raw" "$callback" "$payment" "$task" "$phpnew" \
    "$hardcoded" "$loopdb" "$staticcache" "$notes" >> "$summary_csv"

  printf '| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |\n' \
    "$project_name" "$risk" "$dangerous" "$raw" "$callback" "$payment" "$task" "$phpnew" \
    "$hardcoded" "$loopdb" "$staticcache" "$notes" >> "$summary_md"

  if [ "$risk" = "high" ]; then
    printf '%s | dangerous=%s raw=%s callback=%s payment=%s task=%s phpnew=%s hardcoded=%s loopdb=%s staticcache=%s | %s\n' \
      "$project_name" "$dangerous" "$raw" "$callback" "$payment" "$task" "$phpnew" \
      "$hardcoded" "$loopdb" "$staticcache" "$notes" >> "$high_risk_txt"
  fi
done

echo
printf '[OK] summary csv: %s\n' "$summary_csv"
printf '[OK] summary md: %s\n' "$summary_md"
printf '[OK] high risk list: %s\n' "$high_risk_txt"
printf '[OK] project reports dir: %s\n' "$output_dir/projects"
