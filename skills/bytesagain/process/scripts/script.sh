#!/usr/bin/env bash
# process — Process manager
# Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
set -euo pipefail
VERSION="3.0.1"

BOLD='\033[1m'; GREEN='\033[0;32m'; RED='\033[0;31m'; DIM='\033[2m'; RESET='\033[0m'
die() { echo -e "${RED}Error: $1${RESET}" >&2; exit 1; }

cmd_list() {
    local filter="${1:-}"
    echo -e "${BOLD}Running Processes${RESET}"
    echo ""
    if [ -n "$filter" ]; then
        ps aux | head -1
        ps aux | grep -i "$filter" | grep -v "grep.*$filter"
    else
        ps aux --sort=-%mem | head -21
    fi
}

cmd_top() {
    local n="${1:-10}"
    echo -e "${BOLD}Top $n by CPU${RESET}"
    ps aux --sort=-%cpu | head -$((n + 1))
    echo ""
    echo -e "${BOLD}Top $n by Memory${RESET}"
    ps aux --sort=-%mem | head -$((n + 1))
}

cmd_find() {
    local name="${1:?Usage: process find <name>}"
    local pids
    pids=$(pgrep -f "$name" 2>/dev/null || true)
    if [ -z "$pids" ]; then
        echo "  No processes matching '$name'"
    else
        echo -e "${BOLD}Processes matching '$name'${RESET}"
        echo ""
        ps -fp $pids 2>/dev/null
    fi
}

cmd_kill() {
    local pid="${1:?Usage: process kill <pid> [signal]}"
    local sig="${2:-TERM}"
    if ! kill -0 "$pid" 2>/dev/null; then
        die "Process $pid not found"
    fi
    local name
    name=$(ps -p "$pid" -o comm= 2>/dev/null || echo "unknown")
    kill -"$sig" "$pid"
    echo -e "${GREEN}✓${RESET} Sent SIG$sig to $pid ($name)"
}

cmd_tree() {
    local pid="${1:-1}"
    if command -v pstree >/dev/null 2>&1; then
        pstree -p "$pid" 2>/dev/null || pstree -p
    else
        ps -ef --forest | head -40
    fi
}

cmd_ports() {
    local port="${1:-}"
    echo -e "${BOLD}Listening Ports${RESET}"
    echo ""
    if [ -n "$port" ]; then
        ss -tlnp 2>/dev/null | grep ":$port " || echo "  Port $port not in use"
    else
        ss -tlnp 2>/dev/null | head -20
    fi
}

cmd_watch() {
    local pid="${1:?Usage: process watch <pid>}"
    if ! kill -0 "$pid" 2>/dev/null; then
        die "Process $pid not found"
    fi
    local name
    name=$(ps -p "$pid" -o comm= 2>/dev/null || echo "unknown")
    echo -e "${BOLD}Watching PID $pid ($name)${RESET}"
    echo ""
    for i in $(seq 1 10); do
        if kill -0 "$pid" 2>/dev/null; then
            local cpu mem vsz rss
            cpu=$(ps -p "$pid" -o %cpu= 2>/dev/null || echo "0")
            mem=$(ps -p "$pid" -o %mem= 2>/dev/null || echo "0")
            rss=$(ps -p "$pid" -o rss= 2>/dev/null || echo "0")
            local rss_mb
            rss_mb=$((rss / 1024))
            printf "  [%s] CPU: %s%%  MEM: %s%% (%dMB)\n" "$(date +%H:%M:%S)" "$cpu" "$mem" "$rss_mb"
        else
            echo "  Process $pid has exited"
            break
        fi
        sleep 1
    done
}

cmd_stats() {
    echo -e "${BOLD}System Process Stats${RESET}"
    echo ""
    local total running sleeping stopped zombie
    total=$(ps aux | wc -l)
    running=$(ps aux | awk '$8~/R/' | wc -l)
    sleeping=$(ps aux | awk '$8~/S/' | wc -l)
    stopped=$(ps aux | awk '$8~/T/' | wc -l)
    zombie=$(ps aux | awk '$8~/Z/' | wc -l)
    echo "  Total:    $total"
    echo "  Running:  $running"
    echo "  Sleeping: $sleeping"
    echo "  Stopped:  $stopped"
    echo "  Zombie:   $zombie"
    echo ""
    echo -e "${BOLD}Load Average${RESET}"
    echo "  $(cat /proc/loadavg 2>/dev/null || uptime | sed 's/.*load average://')"
    echo ""
    echo -e "${BOLD}Memory${RESET}"
    free -h 2>/dev/null | head -3
    echo ""
    echo -e "${BOLD}Uptime${RESET}"
    echo "  $(uptime -p 2>/dev/null || uptime)"
}

cmd_mem() {
    local pid="${1:?Usage: process mem <pid>}"
    if ! kill -0 "$pid" 2>/dev/null; then
        die "Process $pid not found"
    fi
    local name
    name=$(ps -p "$pid" -o comm= 2>/dev/null)
    echo -e "${BOLD}Memory for PID $pid ($name)${RESET}"
    echo ""
    local rss vsz
    rss=$(ps -p "$pid" -o rss= 2>/dev/null | tr -d ' ')
    vsz=$(ps -p "$pid" -o vsz= 2>/dev/null | tr -d ' ')
    echo "  RSS:     $((rss / 1024)) MB"
    echo "  VSZ:     $((vsz / 1024)) MB"
    if [ -f "/proc/$pid/status" ]; then
        echo ""
        grep -E "VmPeak|VmRSS|VmSwap|Threads" /proc/$pid/status 2>/dev/null | while IFS= read -r line; do
            echo "  $line"
        done
    fi
}

cmd_cpu() {
    local pid="${1:?Usage: process cpu <pid>}"
    if ! kill -0 "$pid" 2>/dev/null; then
        die "Process $pid not found"
    fi
    local name
    name=$(ps -p "$pid" -o comm= 2>/dev/null)
    echo -e "${BOLD}CPU for PID $pid ($name)${RESET}"
    echo ""
    ps -p "$pid" -o pid,pcpu,pmem,etime,args 2>/dev/null
    if [ -f "/proc/$pid/stat" ]; then
        echo ""
        local utime stime
        utime=$(awk '{print $14}' /proc/$pid/stat 2>/dev/null)
        stime=$(awk '{print $15}' /proc/$pid/stat 2>/dev/null)
        local clk_tck
        clk_tck=$(getconf CLK_TCK 2>/dev/null || echo 100)
        echo "  User time:   $((utime / clk_tck))s"
        echo "  System time: $((stime / clk_tck))s"
    fi
}

cmd_env() {
    local pid="${1:?Usage: process env <pid>}"
    if [ -f "/proc/$pid/environ" ]; then
        echo -e "${BOLD}Environment for PID $pid${RESET}"
        tr '\0' '\n' < /proc/$pid/environ 2>/dev/null | sort | head -30
    else
        die "Cannot read environment for PID $pid"
    fi
}

show_help() {
    cat << EOF
process v$VERSION — Process manager

Usage: process <command> [args]

View:
  list [filter]          List processes (filter by name)
  top [n]                Top N processes by CPU/memory
  find <name>            Find processes by name
  tree [pid]             Process tree
  ports [port]           Show listening ports

Monitor:
  watch <pid>            Watch process for 10 seconds
  mem <pid>              Memory details for process
  cpu <pid>              CPU details for process
  env <pid>              Show process environment

Manage:
  kill <pid> [signal]    Send signal to process (default: TERM)
  stats                  System process statistics

  help                   Show this help
  version                Show version
EOF
}

[ $# -eq 0 ] && { show_help; exit 0; }
case "$1" in
    list|ls)  shift; cmd_list "${1:-}" ;;
    top)      shift; cmd_top "${1:-10}" ;;
    find)     shift; cmd_find "$@" ;;
    kill)     shift; cmd_kill "$@" ;;
    tree)     shift; cmd_tree "${1:-1}" ;;
    ports)    shift; cmd_ports "${1:-}" ;;
    watch)    shift; cmd_watch "$@" ;;
    stats)    cmd_stats ;;
    mem)      shift; cmd_mem "$@" ;;
    cpu)      shift; cmd_cpu "$@" ;;
    env)      shift; cmd_env "$@" ;;
    help|-h)  show_help ;;
    version|-v) echo "process v$VERSION"; echo "Powered by BytesAgain | bytesagain.com | hello@bytesagain.com" ;;
    *)        echo "Unknown: $1"; show_help; exit 1 ;;
esac
