#!/usr/bin/env python3
"""
Pangolinfo Google SERP & AI Mode API Client

Zero-dependency Python client for Pangolinfo's Google SERP and AI Mode APIs.
Supports AI Mode search (Google AI Overviews), standard SERP results,
SERP Plus (cheaper), multi-turn dialogue, and screenshot capture.

Usage:
    pangolinfo.py --q "quantum computing"
    pangolinfo.py --q "best databases 2025" --mode serp --screenshot
    pangolinfo.py --q "best databases 2025" --mode serp-plus
    pangolinfo.py --q "kubernetes" --follow-up "how to deploy"
    pangolinfo.py --auth-only

Environment:
    PANGOLINFO_API_KEY  - API Key (skips login)
    PANGOLINFO_EMAIL    - Account email (for login)
    PANGOLINFO_PASSWORD - Account password (for login)
"""

import argparse
import io
import json
import os
import stat
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Fix Windows / macOS console encoding for Unicode output
# ---------------------------------------------------------------------------
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace"
    )
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer, encoding="utf-8", errors="replace"
    )

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
API_BASE = "https://scrapeapi.pangolinfo.com"
AUTH_ENDPOINT = f"{API_BASE}/api/v1/auth"
SCRAPE_ENDPOINT = f"{API_BASE}/api/v2/scrape"
API_KEY_CACHE_PATH = Path.home() / ".pangolinfo_api_key"

# User-facing registration/top-up link (not the API endpoint)
REFERRER_TAG = "clawhub_serp"
PANGOLINFO_URL = f"https://pangolinfo.com/?referrer={REFERRER_TAG}"

# Caching credentials to disk is opt-in only.
CACHE_TO_DISK = False

EXIT_SUCCESS = 0
EXIT_API_ERROR = 1
EXIT_USAGE_ERROR = 2
EXIT_NETWORK_ERROR = 3
EXIT_AUTH_ERROR = 4

# Mode-to-parser mapping (must match backend ApiName enum values exactly)
MODE_PARSER_MAP = {
    "ai-mode": "googleAiSearch",
    "serp": "googleSearch",
    "serp-plus": "googleSearchPlus",
}

# Supported regions (must match backend GoogleRegion enum)
SUPPORTED_REGIONS = {
    "us", "uk", "it", "jp", "de", "fr", "nl", "cn",
    "au", "ca", "dk", "nz", "no", "pt", "es", "se",
}


# ---------------------------------------------------------------------------
# Unified error helper
# ---------------------------------------------------------------------------
def _emit_error(code, message, hint=None, api_code=None, exit_code=None):
    """Print a structured error envelope to stderr and optionally exit."""
    envelope = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
        },
    }
    if api_code is not None:
        envelope["error"]["api_code"] = api_code
    if hint:
        envelope["error"]["hint"] = hint
    print(json.dumps(envelope, ensure_ascii=False), file=sys.stderr)
    if exit_code is not None:
        sys.exit(exit_code)


def _is_ssl_error(exc):
    """Check if an exception is SSL-related."""
    msg = str(exc)
    return "CERTIFICATE_VERIFY_FAILED" in msg or "SSL" in msg


def _emit_ssl_error():
    """Emit a standardized SSL certificate error and exit."""
    _emit_error(
        "SSL_CERT",
        "SSL certificate verification failed.",
        hint=(
            "macOS: run '/Applications/Python 3.x/Install Certificates.command' "
            "or set SSL_CERT_FILE. See: python3 -c \"import certifi; print(certifi.where())\""
        ),
        exit_code=EXIT_NETWORK_ERROR,
    )


# ---------------------------------------------------------------------------
# API key caching
# ---------------------------------------------------------------------------
def load_cached_api_key():
    """Load API key from cache file if it exists."""
    if API_KEY_CACHE_PATH.exists():
        api_key = API_KEY_CACHE_PATH.read_text().strip()
        if api_key and len(api_key.split(".")) == 3:
            return api_key
    return None


def save_cached_api_key(api_key):
    """Save API key to cache file (only when explicitly enabled).

    Uses atomic write with restricted permissions to avoid race conditions.
    """
    if not CACHE_TO_DISK:
        return
    # Write to a temp file with restricted permissions, then rename atomically
    try:
        fd = os.open(
            str(API_KEY_CACHE_PATH) + ".tmp",
            os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
            stat.S_IRUSR | stat.S_IWUSR,  # 0o600 from creation
        )
        with os.fdopen(fd, "w") as f:
            f.write(api_key)
        # Atomic rename (on POSIX; best-effort on Windows)
        os.replace(str(API_KEY_CACHE_PATH) + ".tmp", str(API_KEY_CACHE_PATH))
    except OSError:
        # Fallback: direct write
        API_KEY_CACHE_PATH.write_text(api_key)
        try:
            API_KEY_CACHE_PATH.chmod(0o600)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------
def _http_post(url, body_dict, headers=None, timeout=30):
    """POST JSON and return parsed response. Handles SSL and network errors."""
    payload = json.dumps(body_dict).encode()
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, data=payload, headers=req_headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except urllib.error.URLError as e:
        if _is_ssl_error(e):
            _emit_ssl_error()
        raise
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        _emit_error(
            "PARSE_ERROR",
            "API returned invalid JSON.",
            hint="The API may be temporarily unavailable. Retry in a moment.",
            exit_code=EXIT_NETWORK_ERROR,
        )


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
def authenticate(email, password):
    """Authenticate with Pangolinfo API and return an API key."""
    try:
        result = _http_post(AUTH_ENDPOINT, {"email": email, "password": password})
    except urllib.error.URLError:
        _emit_error(
            "NETWORK",
            "Network error during authentication.",
            hint="Check your internet connection and try again.",
            exit_code=EXIT_NETWORK_ERROR,
        )

    if result.get("code") != 0:
        _emit_error(
            "AUTH_FAILED",
            "Authentication failed.",
            hint="Verify PANGOLINFO_EMAIL and PANGOLINFO_PASSWORD are correct.",
            api_code=result.get("code"),
            exit_code=EXIT_AUTH_ERROR,
        )

    api_key = result["data"]
    save_cached_api_key(api_key)
    return api_key


def get_api_key():
    """Resolve API key from env var, cache file, or fresh login."""
    api_key = os.environ.get("PANGOLINFO_API_KEY")
    if api_key:
        save_cached_api_key(api_key)
        return api_key

    api_key = load_cached_api_key()
    if api_key:
        return api_key

    email = os.environ.get("PANGOLINFO_EMAIL")
    password = os.environ.get("PANGOLINFO_PASSWORD")
    if not email or not password:
        _emit_error(
            "MISSING_ENV",
            "No authentication credentials found.",
            hint=(
                "Set PANGOLINFO_API_KEY, or both PANGOLINFO_EMAIL and PANGOLINFO_PASSWORD "
                "environment variables."
            ),
            exit_code=EXIT_AUTH_ERROR,
        )

    return authenticate(email, password)


def refresh_api_key():
    """Force re-authentication using email/password."""
    email = os.environ.get("PANGOLINFO_EMAIL")
    password = os.environ.get("PANGOLINFO_PASSWORD")
    if not email or not password:
        _emit_error(
            "MISSING_ENV",
            "Cannot refresh API key without credentials.",
            hint="Set PANGOLINFO_EMAIL and PANGOLINFO_PASSWORD environment variables.",
            exit_code=EXIT_AUTH_ERROR,
        )
    return authenticate(email, password)


# ---------------------------------------------------------------------------
# Request building
# ---------------------------------------------------------------------------
def build_request_body(query, mode, screenshot, follow_ups, num, region=None):
    """Build request body for Google SERP / AI Mode APIs."""
    parser_name = MODE_PARSER_MAP[mode]

    if mode == "ai-mode":
        url = (
            f"https://www.google.com/search?num={num}&udm=50"
            f"&q={urllib.parse.quote_plus(query)}"
        )
    else:
        url = (
            f"https://www.google.com/search?num={num}"
            f"&q={urllib.parse.quote_plus(query)}"
        )

    body = {
        "url": url,
        "parserName": parser_name,
    }

    if mode in ("serp", "serp-plus"):
        body["format"] = "json"
        body["scrapeContext"] = {"resultNum": num}
        if region:
            body["scrapeContext"]["region"] = region

    if screenshot:
        body["screenshot"] = True

    if follow_ups:
        body["param"] = follow_ups

    return body


# ---------------------------------------------------------------------------
# API call with retry
# ---------------------------------------------------------------------------
def call_api(api_key, body, max_retries=3, timeout=120):
    """Call the scrape API with retry and exponential backoff."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "Pangolinfo-CLI/2.0",
    }

    for attempt in range(max_retries):
        try:
            result = _http_post(SCRAPE_ENDPOINT, body, headers=headers, timeout=timeout)
            return result
        except urllib.error.HTTPError as e:
            error_body = ""
            try:
                error_body = e.read().decode() if e.fp else ""
            except Exception:
                pass

            if e.code == 429:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                _emit_error(
                    "RATE_LIMIT",
                    "Rate limited by API server.",
                    hint="Wait a moment and retry, or reduce request frequency.",
                    exit_code=EXIT_NETWORK_ERROR,
                )

            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue

            # Include server error details if available
            detail = ""
            if error_body:
                try:
                    err_json = json.loads(error_body)
                    detail = f" Server: {err_json.get('message', error_body[:200])}"
                except (json.JSONDecodeError, ValueError):
                    detail = f" Server: {error_body[:200]}"

            _emit_error(
                "API_ERROR",
                f"HTTP {e.code} from API.{detail}",
                hint="Check your request parameters and try again.",
                exit_code=EXIT_NETWORK_ERROR,
            )
        except urllib.error.URLError:
            # SSL errors already handled by _http_post; this is a non-SSL network error
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            _emit_error(
                "NETWORK",
                "Network error communicating with API.",
                hint="Check your internet connection and try again.",
                exit_code=EXIT_NETWORK_ERROR,
            )

    # Should not reach here, but guard against it
    _emit_error(
        "NETWORK",
        "API call failed after retries.",
        hint="Check your internet connection and try again.",
        exit_code=EXIT_NETWORK_ERROR,
    )


# ---------------------------------------------------------------------------
# Response handling
# ---------------------------------------------------------------------------
# Known Pangolinfo API error code hints
API_ERROR_HINTS = {
    1004: "Invalid token. Will auto-retry with fresh credentials.",
    1009: "Invalid parser name. Check --mode value.",
    2001: f"Insufficient credits. Top up at {PANGOLINFO_URL}",
    2005: f"No active plan. Subscribe at {PANGOLINFO_URL}",
    2007: f"Account expired. Renew at {PANGOLINFO_URL}",
    2009: "Usage limit reached for current billing cycle. Contact support.",
    2010: "Bill day not configured. Contact support.",
    4029: "Rate limited by server. Reduce request frequency.",
    10000: "Task execution failed. Retry or check query format.",
    10001: "Task execution failed. Likely a temporary server issue.",
}


def handle_response(result, api_key, body, timeout=120):
    """Handle API response, retrying auth on 1004 error."""
    if result.get("code") == 1004:
        new_api_key = refresh_api_key()
        return call_api(new_api_key, body, timeout=timeout)
    return result


def extract_output(result):
    """Extract structured output from Google SERP / AI Mode API response."""
    code = result.get("code")
    if code != 0:
        hint = API_ERROR_HINTS.get(code, f"Pangolinfo API error code {code}. See references/error-codes.md.")
        return {
            "success": False,
            "error": {
                "code": "API_ERROR",
                "api_code": code,
                "message": result.get("message", "Unknown API error"),
                "hint": hint,
            },
        }

    data = result.get("data", {})
    output = {
        "success": True,
        "task_id": data.get("taskId"),
    }

    json_data = data.get("json", {})

    # V1/V2 response format handling:
    # Some parsers return json as array: [{code, data: {items: [...]}}]
    # Others return json as object: {items: [...]} or {type, items: [...]}
    if isinstance(json_data, list) and len(json_data) > 0:
        inner = json_data[0]
        items = inner.get("data", {}).get("items", [])
    elif isinstance(json_data, dict):
        items = json_data.get("items", [])
    else:
        items = []

    ai_overviews = []
    organic_results = []

    for item in items:
        item_type = item.get("type")
        if item_type == "ai_overview":
            overview = {"content": [], "references": []}
            for sub in item.get("items", []):
                if sub.get("type") == "ai_overview_elem":
                    overview["content"].extend(sub.get("content", []))
            for ref in item.get("references", []):
                overview["references"].append({
                    "title": ref.get("title"),
                    "url": ref.get("url"),
                    "domain": ref.get("domain"),
                })
            ai_overviews.append(overview)
        elif item_type == "organic":
            for sub in item.get("items", []):
                organic_results.append({
                    "title": sub.get("title"),
                    "url": sub.get("url"),
                    "text": sub.get("text"),
                })

    # Use parsed counts; fall back to API-reported counts
    output["ai_overview_count"] = len(ai_overviews) if ai_overviews else data.get("ai_overview", 0)
    output["results_num"] = len(organic_results) if organic_results else data.get("results_num", 0)

    if ai_overviews:
        output["ai_overview"] = ai_overviews
    if organic_results:
        output["organic_results"] = organic_results

    screenshot_url = data.get("screenshot")
    if screenshot_url:
        output["screenshot"] = screenshot_url

    return output


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Pangolinfo Google SERP & AI Mode API Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            '  python3 pangolinfo.py --q "what is quantum computing"\n'
            '  python3 pangolinfo.py --q "best databases 2025" --mode serp --screenshot\n'
            '  python3 pangolinfo.py --q "best databases 2025" --mode serp-plus\n'
            '  python3 pangolinfo.py --q "kubernetes" --follow-up "how to deploy"\n'
            "  python3 pangolinfo.py --auth-only\n"
        ),
    )
    parser.add_argument("--q", dest="query", help="Search query")
    parser.add_argument(
        "--mode",
        choices=["ai-mode", "serp", "serp-plus"],
        default="ai-mode",
        help="API mode (default: ai-mode)",
    )
    parser.add_argument("--screenshot", action="store_true", help="Capture page screenshot")
    parser.add_argument(
        "--follow-up",
        action="append",
        dest="follow_ups",
        help="Follow-up question (ai-mode only, repeatable, max 5 recommended)",
    )
    parser.add_argument("--num", type=int, default=10, help="Number of results (default: 10)")
    parser.add_argument(
        "--region",
        default=None,
        help="Geographic region (serp/serp-plus only). E.g., us, uk, de, jp.",
    )
    parser.add_argument("--auth-only", action="store_true", help="Auth check only")
    parser.add_argument("--raw", action="store_true", help="Output raw API response")
    parser.add_argument("--timeout", type=int, default=120, help="Request timeout in seconds (default: 120)")
    parser.add_argument(
        "--cache-key",
        action="store_true",
        help="Persist API key to ~/.pangolinfo_api_key. Also: PANGOLINFO_CACHE=1.",
    )

    args = parser.parse_args()

    # Configure optional credential caching
    global CACHE_TO_DISK
    CACHE_TO_DISK = bool(args.cache_key) or os.environ.get("PANGOLINFO_CACHE", "").strip().lower() in (
        "1", "true", "yes", "on",
    )

    # --- Input validation ---
    if not args.query and not args.auth_only:
        parser.error("--q is required unless using --auth-only")

    if args.follow_ups and args.mode != "ai-mode":
        parser.error("--follow-up is only supported in ai-mode")

    if args.region and args.mode == "ai-mode":
        parser.error("--region is only supported in serp or serp-plus mode")

    if args.region and args.region.lower() not in SUPPORTED_REGIONS:
        parser.error(
            f"Unsupported region '{args.region}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_REGIONS))}"
        )

    if args.num < 1 or args.num > 100:
        parser.error("--num must be between 1 and 100")

    if args.follow_ups and len(args.follow_ups) > 5:
        print(
            json.dumps({"warning": f"Using {len(args.follow_ups)} follow-ups (>5). Response may be slower."}),
            file=sys.stderr,
        )

    # Normalize region to lowercase
    if args.region:
        args.region = args.region.lower()

    # --- Authenticate ---
    api_key = get_api_key()

    if args.auth_only:
        # Mask the key: show only first 4 and last 4 chars
        if len(api_key) > 12:
            preview = f"{api_key[:4]}...{api_key[-4:]}"
        else:
            preview = "***"
        print(json.dumps({
            "success": True,
            "message": "Authentication successful",
            "api_key_preview": preview,
        }, indent=2))
        sys.exit(EXIT_SUCCESS)

    # --- Build and send request ---
    body = build_request_body(
        args.query, args.mode, args.screenshot, args.follow_ups, args.num,
        region=args.region,
    )

    result = call_api(api_key, body, timeout=args.timeout)

    if result is None:
        _emit_error(
            "NETWORK",
            "API call failed after retries.",
            hint="Check your internet connection and try again.",
            exit_code=EXIT_NETWORK_ERROR,
        )

    result = handle_response(result, api_key, body, timeout=args.timeout)

    if result is None:
        _emit_error(
            "NETWORK",
            "API call failed after token refresh.",
            hint="Check your internet connection and try again.",
            exit_code=EXIT_NETWORK_ERROR,
        )

    # --- Output ---
    if args.raw:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        output = extract_output(result)
        if output.get("success"):
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            # Errors go to stderr, matching documented behavior
            print(json.dumps(output, indent=2, ensure_ascii=False), file=sys.stderr)

    if result.get("code") != 0:
        sys.exit(EXIT_API_ERROR)

    sys.exit(EXIT_SUCCESS)


if __name__ == "__main__":
    main()
