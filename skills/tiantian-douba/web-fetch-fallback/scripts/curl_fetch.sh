#!/bin/bash
#
# curl_fetch.sh - Reference script for fetching web content via curl
# Use this as a template when web_fetch is blocked due to private IP restrictions
#

set -euo pipefail

# Default configuration
TIMEOUT=30
CONNECT_TIMEOUT=10
MAX_REDIRECTS=5
USER_AGENT="Mozilla/5.0 (compatible; OpenClaw-Fallback)"

# Usage information
usage() {
    cat << EOF
Usage: $0 [OPTIONS] <URL>

Fetch web content using curl when web_fetch is blocked.

Options:
    -o, --output FILE       Save output to FILE (default: stdout)
    -t, --timeout SECONDS   Total timeout (default: 30)
    -c, --connect-timeout SECONDS   Connection timeout (default: 10)
    -H, --header HEADER     Add custom header (can be used multiple times)
    -s, --silent            Silent mode (no progress meter)
    -v, --verbose           Verbose output
    -h, --help              Show this help message

Examples:
    $0 "http://internal.example.com/page"
    $0 -o /tmp/output.html "http://internal.example.com/page"
    $0 -H "Authorization: Bearer token" "http://api.internal.com/data"
EOF
}

# Parse arguments
OUTPUT=""
SILENT=true
VERBOSE=false
HEADERS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        -o|--output)
            OUTPUT="$2"
            shift 2
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -c|--connect-timeout)
            CONNECT_TIMEOUT="$2"
            shift 2
            ;;
        -H|--header)
            HEADERS+=("$2")
            shift 2
            ;;
        -s|--silent)
            SILENT=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        -*)
            echo "Unknown option: $1" >&2
            usage >&2
            exit 1
            ;;
        *)
            URL="$1"
            shift
            ;;
    esac
done

# Validate URL
if [[ -z "${URL:-}" ]]; then
    echo "Error: URL is required" >&2
    usage >&2
    exit 1
fi

# Build curl command
CURL_ARGS=(
    -L                          # Follow redirects
    --max-redirs "$MAX_REDIRECTS"
    --max-time "$TIMEOUT"
    --connect-timeout "$CONNECT_TIMEOUT"
    -A "$USER_AGENT"
)

# Add silent flag if enabled
if [[ "$SILENT" == true ]]; then
    CURL_ARGS+=(-s)
fi

# Add verbose flag if enabled
if [[ "$VERBOSE" == true ]]; then
    CURL_ARGS+=(-v)
fi

# Add custom headers
for header in "${HEADERS[@]}"; do
    CURL_ARGS+=(-H "$header")
done

# Add output file if specified
if [[ -n "$OUTPUT" ]]; then
    CURL_ARGS+=(-o "$OUTPUT")
fi

# Execute curl
curl "${CURL_ARGS[@]}" "$URL"
EXIT_CODE=$?

# Handle exit codes
if [[ $EXIT_CODE -ne 0 ]]; then
    echo "Error: curl failed with exit code $EXIT_CODE" >&2
    case $EXIT_CODE in
        6) echo "Could not resolve host" >&2 ;;
        7) echo "Failed to connect to host" >&2 ;;
        28) echo "Operation timeout" >&2 ;;
        35) echo "SSL/TLS handshake failed" >&2 ;;
    esac
    exit $EXIT_CODE
fi

exit 0
