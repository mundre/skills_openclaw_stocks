#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <project-root> [output-file]" >&2
  exit 1
fi

project_root="$1"
output_file="${2:-}"

if [ ! -d "$project_root" ]; then
  echo "[ERROR] project root not found: $project_root" >&2
  exit 1
fi

project_name="$(basename "$project_root")"

tmp_report="$(mktemp)"
trap 'rm -f "$tmp_report"' EXIT

collect_raw() {
  cd "$project_root"

  echo "=== structure ==="
  for path in public application/controllers application/models application/library application/modules conf; do
    if [ -e "$path" ]; then
      echo "[OK] $path"
    else
      echo "[MISSING] $path"
    fi
  done
  echo

  echo "=== entrypoints ==="
  find public -maxdepth 2 -type f 2>/dev/null | sed 's#^#- #' | sort || true
  echo

  print_hits() {
    label="$1"
    pattern="$2"
    echo "=== $label ==="
    grep -RInE --include='*.php' --include='*.inc' --include='*.phtml' "$pattern" application public conf 2>/dev/null | sed -n '1,120p' || true
    echo
  }

  print_hits "dangerous functions" '(^|[^a-zA-Z0-9_])(eval|exec|shell_exec|system|passthru|proc_open|popen|unserialize)[[:space:]]*\('
  print_hits "raw superglobals" '\$_(GET|POST|REQUEST|COOKIE|FILES)\b'
  print_hits "sql concatenation suspects" '(select|update|delete|insert)[^;\n]*\.[^;\n]*\$|->query\s*\(|->execute\s*\('
  print_hits "select star" 'select\s+\*'
  print_hits "redis high-cost commands" '(sdiff|sdiffstore)[[:space:]]*\('
  print_hits "external http without obvious timeout clues" '(curl_init|curl_setopt|file_get_contents\s*\(|request\s*\()'
  print_hits "callback and notify keywords" '(callback|notify)'
  print_hits "payment keywords" '(pay|order|refund|charge)'
  print_hits "task and cron keywords" '(cron|task|queue|worker)'
  print_hits "php 7.4+ syntax suspects" '(match[[:space:]]*\(|fn[[:space:]]*\(|\?->|readonly|enum[[:space:]]+|public[[:space:]]+[A-Za-z_][A-Za-z0-9_]*[[:space:]]*=)'
  print_hits "hardcoded credentials suspects" '(password|passwd|pwd|api_key|secret|token)\s*=\s*['"'"'"][^'"'"'"]{4,}'
  print_hits "login and auth keywords" '(login|logout|session|token|auth|permission|role|privilege)'
  print_hits "curl without explicit timeout check" 'curl_init\s*\('
  print_hits "static array cache antipattern" 'static\s+\$[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*(array\s*\(|\[)'
  print_hits "loop with db suspects" '(foreach|for\s*\(|while\s*\()[^{]*\{[^}]*(->find|->where|->query|->select|->first|->get|->fetch)'
}

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

print_section() {
  local file="$1"
  local section="$2"
  awk -v section="$section" '
    $0 == "=== " section " ===" { in_section=1; next }
    /^=== / && in_section { exit }
    in_section { print }
  ' "$file"
}

calc_risk() {
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

report_note() {
  local risk="$1"
  local callback="$2"
  local payment="$3"
  local task="$4"
  local dangerous="$5"

  if [ "$risk" = "high" ]; then
    echo "高优先级项目，建议人工深审支付、回调、任务和危险函数命中区域。"
  elif [ "$callback" -ge 3 ] || [ "$payment" -ge 3 ]; then
    echo "存在明显业务敏感链路，建议优先复核回调和支付状态变更。"
  elif [ "$task" -ge 5 ] || [ "$dangerous" -ge 1 ]; then
    echo "存在任务链路或高敏函数使用，建议补充人工复核。"
  else
    echo "首轮命中有限，可作为低优先级项目保留跟踪。"
  fi
}

collect_raw > "$tmp_report"

dangerous="$(count_hits "$tmp_report" "dangerous functions")"
raw="$(count_hits "$tmp_report" "raw superglobals")"
sqlsus="$(count_hits "$tmp_report" "sql concatenation suspects")"
selectstar="$(count_hits "$tmp_report" "select star")"
redisrisk="$(count_hits "$tmp_report" "redis high-cost commands")"
httprisk="$(count_hits "$tmp_report" "external http without obvious timeout clues")"
callback="$(count_hits "$tmp_report" "callback and notify keywords")"
payment="$(count_hits "$tmp_report" "payment keywords")"
task="$(count_hits "$tmp_report" "task and cron keywords")"
phpnew="$(count_hits "$tmp_report" "php 7.4+ syntax suspects")"
hardcoded="$(count_hits "$tmp_report" "hardcoded credentials suspects")"
authkw="$(count_hits "$tmp_report" "login and auth keywords")"
curlinit="$(count_hits "$tmp_report" "curl without explicit timeout check")"
staticcache="$(count_hits "$tmp_report" "static array cache antipattern")"
loopdb="$(count_hits "$tmp_report" "loop with db suspects")"
risk="$(calc_risk "$dangerous" "$raw" "$callback" "$payment" "$task" "$phpnew" "$hardcoded")"
summary_note="$(report_note "$risk" "$callback" "$payment" "$task" "$dangerous")"

generate_report() {
  echo "# 项目审计报告"
  echo
  echo "## 1. 项目基本信息"
  echo "- 项目名：$project_name"
  echo "- 项目路径：$project_root"
  echo "- 生成时间：$(date '+%Y-%m-%d %H:%M:%S %z')"
  echo "- 首轮风险等级：$risk"
  echo
  echo "## 2. 审计结论"
  echo "- 结论：$summary_note"
  echo
  echo "## 3. 结构概览"
  print_section "$tmp_report" "structure"
  echo
  echo "## 4. 入口文件"
  print_section "$tmp_report" "entrypoints"
  echo
  echo "## 5. 风险统计"
  echo "- dangerous functions：$dangerous"
  echo "- raw superglobals：$raw"
  echo "- sql concatenation suspects：$sqlsus"
  echo "- select star：$selectstar"
  echo "- redis high-cost commands：$redisrisk"
  echo "- external http clues：$httprisk"
  echo "- callback and notify keywords：$callback"
  echo "- payment keywords：$payment"
  echo "- task and cron keywords：$task"
  echo "- php 7.4+/8.x syntax suspects：$phpnew"
  echo "- hardcoded credentials suspects：$hardcoded"
  echo "- login and auth keywords：$authkw"
  echo "- curl without explicit timeout check：$curlinit"
  echo "- static array cache antipattern：$staticcache"
  echo "- loop with db suspects：$loopdb"
  echo
  echo "## 6. 风险明细"
  echo
  echo "### 6.1 dangerous functions"
  print_section "$tmp_report" "dangerous functions"
  echo
  echo "### 6.2 raw superglobals"
  print_section "$tmp_report" "raw superglobals"
  echo
  echo "### 6.3 sql concatenation suspects"
  print_section "$tmp_report" "sql concatenation suspects"
  echo
  echo "### 6.4 select star"
  print_section "$tmp_report" "select star"
  echo
  echo "### 6.5 redis high-cost commands"
  print_section "$tmp_report" "redis high-cost commands"
  echo
  echo "### 6.6 external http without obvious timeout clues"
  print_section "$tmp_report" "external http without obvious timeout clues"
  echo
  echo "### 6.7 callback and notify keywords"
  print_section "$tmp_report" "callback and notify keywords"
  echo
  echo "### 6.8 payment keywords"
  print_section "$tmp_report" "payment keywords"
  echo
  echo "### 6.9 task and cron keywords"
  print_section "$tmp_report" "task and cron keywords"
  echo
  echo "### 6.10 php 7.4+ syntax suspects"
  print_section "$tmp_report" "php 7.4+ syntax suspects"
  echo
  echo "### 6.11 hardcoded credentials suspects"
  print_section "$tmp_report" "hardcoded credentials suspects"
  echo
  echo "### 6.12 login and auth keywords"
  print_section "$tmp_report" "login and auth keywords"
  echo
  echo "### 6.13 curl without explicit timeout check"
  print_section "$tmp_report" "curl without explicit timeout check"
  echo
  echo "### 6.14 static array cache antipattern"
  print_section "$tmp_report" "static array cache antipattern"
  echo
  echo "### 6.15 loop with db suspects"
  print_section "$tmp_report" "loop with db suspects"
  echo
  echo "## 7. 审计建议"
  echo "- 建议优先人工复核支付、回调、登录态、任务链路。"
  echo "- 建议核实外部 HTTP 调用是否设置 timeout / connect_timeout。"
  echo "- 建议结合调用链确认幂等、事务边界、N+1 查询和缓存一致性问题。"
  echo
  echo "## 8. 说明"
  echo "- 本报告属于首轮静态审计报告，用于风险筛查与优先级排序。"
  echo "- 命中项不等于最终漏洞结论，高风险项目仍需人工深审。"
}

if [ -n "$output_file" ]; then
  mkdir -p "$(dirname "$output_file")"
  generate_report > "$output_file"
  printf '[OK] report written: %s\n' "$output_file"
else
  generate_report
fi
