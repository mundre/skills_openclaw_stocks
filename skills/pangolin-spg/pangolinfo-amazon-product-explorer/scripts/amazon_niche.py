#!/usr/bin/env python3
"""
Pangolinfo Amazon Niche Data API Client

Zero-dependency Python client for Pangolinfo's Amazon 利基 (niche) data APIs.
Covers 5 endpoints under /api/v1/amzscope/*:

    category-tree     POST /api/v1/amzscope/categories/children
    category-search   POST /api/v1/amzscope/categories/search
    category-paths    POST /api/v1/amzscope/categories/paths
    category-filter   POST /api/v1/amzscope/categories/filter
    niche-filter      POST /api/v1/amzscope/niches/filter

Usage:
    pangolinfo.py --api category-search --keyword "headphones"
    pangolinfo.py --api category-tree --parent-path "2619526011"
    pangolinfo.py --api category-paths --category-ids "2619526011,172282"
    pangolinfo.py --api category-filter --marketplace-id US --time-range l7d --sample-scope all_asin
    pangolinfo.py --api niche-filter --marketplace-id US --niche-title "yoga mat"
    pangolinfo.py --auth-only

Environment:
    PANGOLINFO_API_KEY  - API key (skips login)
    PANGOLINFO_EMAIL    - Account email (for login)
    PANGOLINFO_PASSWORD - Account password (for login)
"""

import argparse
import io
import json
import os
import stat
import sys
import time
import urllib.error
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
AMZSCOPE_BASE = f"{API_BASE}/api/v1/amzscope"
API_KEY_CACHE_PATH = Path.home() / ".pangolinfo_api_key"

# User-facing registration/top-up link (not the API endpoint)
REFERRER_TAG = "clawhub_niche"
PANGOLINFO_URL = f"https://pangolinfo.com/?referrer={REFERRER_TAG}"

CACHE_TO_DISK = False

EXIT_SUCCESS = 0
EXIT_API_ERROR = 1
EXIT_USAGE_ERROR = 2
EXIT_NETWORK_ERROR = 3
EXIT_AUTH_ERROR = 4

# API name -> (path suffix, display label)
API_ROUTES = {
    "category-tree":   ("/categories/children", "browseCategoryTreeAPI"),
    "category-search": ("/categories/search",   "searchCategoriesAPI"),
    "category-paths":  ("/categories/paths",    "batchCategoryPathsAPI"),
    "category-filter": ("/categories/filter",   "categoryFilterAPI"),
    "niche-filter":    ("/niches/filter",       "nicheFilterAPI"),
}

# Known Pangolinfo API error hints
API_ERROR_HINTS = {
    1002: "Invalid parameter. Check required fields for this API.",
    1004: "Invalid token. Will auto-retry with fresh credentials.",
    2001: f"Insufficient credits. Top up at {PANGOLINFO_URL}",
    2005: f"No active plan. Subscribe at {PANGOLINFO_URL}",
    2007: f"Account expired. Renew at {PANGOLINFO_URL}",
    2009: "Usage limit reached for current billing cycle. Contact support.",
    4029: "Rate limited by server. Reduce request frequency.",
    9100: "AmzScope service temporarily disabled. Retry later.",
    9101: "Data source temporarily unavailable. Retry later.",
    9102: "Service quota exceeded. Contact support.",
}


# ---------------------------------------------------------------------------
# Error helper
# ---------------------------------------------------------------------------
def _emit_error(code, message, hint=None, api_code=None, exit_code=None):
    """Print structured error JSON to stderr and optionally exit."""
    envelope = {"success": False, "error": {"code": code, "message": message}}
    if api_code is not None:
        envelope["error"]["api_code"] = api_code
    if hint:
        envelope["error"]["hint"] = hint
    print(json.dumps(envelope, ensure_ascii=False), file=sys.stderr)
    if exit_code is not None:
        sys.exit(exit_code)


def _is_ssl_error(exc):
    msg = str(exc)
    return "CERTIFICATE_VERIFY_FAILED" in msg or "SSL" in msg


def _emit_ssl_error():
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
# API key management
# ---------------------------------------------------------------------------
def load_cached_api_key():
    if API_KEY_CACHE_PATH.exists():
        api_key = API_KEY_CACHE_PATH.read_text().strip()
        if api_key and len(api_key.split(".")) == 3:
            return api_key
    return None


def save_cached_api_key(api_key):
    if not CACHE_TO_DISK:
        return
    try:
        fd = os.open(
            str(API_KEY_CACHE_PATH) + ".tmp",
            os.O_WRONLY | os.O_CREAT | os.O_TRUNC,
            stat.S_IRUSR | stat.S_IWUSR,
        )
        with os.fdopen(fd, "w") as f:
            f.write(api_key)
        os.replace(str(API_KEY_CACHE_PATH) + ".tmp", str(API_KEY_CACHE_PATH))
    except OSError:
        API_KEY_CACHE_PATH.write_text(api_key)
        try:
            API_KEY_CACHE_PATH.chmod(0o600)
        except OSError:
            pass


# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------
def _http_post(url, body_dict, headers=None, timeout=30):
    """POST JSON and return parsed response."""
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
    try:
        result = _http_post(AUTH_ENDPOINT, {"email": email, "password": password})
    except urllib.error.URLError:
        _emit_error(
            "NETWORK", "Network error during authentication.",
            hint="Check your internet connection and try again.",
            exit_code=EXIT_NETWORK_ERROR,
        )

    if result.get("code") != 0:
        _emit_error(
            "AUTH_FAILED", "Authentication failed.",
            hint="Verify PANGOLINFO_EMAIL and PANGOLINFO_PASSWORD are correct.",
            api_code=result.get("code"),
            exit_code=EXIT_AUTH_ERROR,
        )

    api_key = result["data"]
    save_cached_api_key(api_key)
    return api_key


def get_api_key():
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
            "MISSING_ENV", "No authentication credentials found.",
            hint="Set PANGOLINFO_API_KEY, or both PANGOLINFO_EMAIL and PANGOLINFO_PASSWORD.",
            exit_code=EXIT_AUTH_ERROR,
        )
    return authenticate(email, password)


def refresh_api_key():
    email = os.environ.get("PANGOLINFO_EMAIL")
    password = os.environ.get("PANGOLINFO_PASSWORD")
    if not email or not password:
        _emit_error(
            "MISSING_ENV", "Cannot refresh API key without credentials.",
            hint="Set PANGOLINFO_EMAIL and PANGOLINFO_PASSWORD environment variables.",
            exit_code=EXIT_AUTH_ERROR,
        )
    return authenticate(email, password)


# ---------------------------------------------------------------------------
# Request body builders
# ---------------------------------------------------------------------------
def _parse_category_ids(raw):
    """Accept either a JSON array ('["a","b"]') or a comma-separated list."""
    raw = raw.strip()
    if raw.startswith("["):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as e:
            _emit_error(
                "USAGE_ERROR", f"Invalid --category-ids JSON: {e}",
                hint="Provide a JSON array or comma-separated IDs.",
                exit_code=EXIT_USAGE_ERROR,
            )
        if not isinstance(parsed, list):
            _emit_error(
                "USAGE_ERROR", "--category-ids JSON must be an array.",
                hint='Example: --category-ids \'["2619526011","172282"]\'',
                exit_code=EXIT_USAGE_ERROR,
            )
        return [str(x) for x in parsed]
    return [part.strip() for part in raw.split(",") if part.strip()]


def _apply_extras(body, extras):
    """Merge --extra key=value pairs into body. Values are JSON-parsed when possible."""
    for item in extras or []:
        if "=" not in item:
            _emit_error(
                "USAGE_ERROR", f"--extra must be key=value, got: {item}",
                hint="Example: --extra 'buyBoxPriceAvgMin=5000'",
                exit_code=EXIT_USAGE_ERROR,
            )
        key, _, value = item.partition("=")
        key = key.strip()
        value = value.strip()
        if not key:
            _emit_error(
                "USAGE_ERROR", f"--extra missing key: {item}",
                exit_code=EXIT_USAGE_ERROR,
            )
        try:
            body[key] = json.loads(value)
        except json.JSONDecodeError:
            body[key] = value
    return body


def _apply_pagination(body, page, size, is_filter=False):
    if page is not None:
        if is_filter and page > 10:
            _emit_error(
                "USAGE_ERROR",
                "Filter APIs limit page to 10 (got %d)." % page,
                hint="Use --page 1..10. Refine filters to narrow results.",
                exit_code=EXIT_USAGE_ERROR,
            )
        body["page"] = page
    if size is not None:
        body["size"] = size


def build_body(args):
    body = {}

    if args.api == "category-tree":
        if args.parent_path:
            body["parentBrowseNodeIdPath"] = args.parent_path
        _apply_pagination(body, args.page, args.size)

    elif args.api == "category-search":
        if not args.keyword:
            _emit_error(
                "USAGE_ERROR", "category-search requires --keyword.",
                hint="Provide --keyword <term>.",
                exit_code=EXIT_USAGE_ERROR,
            )
        body["keyword"] = args.keyword
        _apply_pagination(body, args.page, args.size)

    elif args.api == "category-paths":
        if not args.category_ids:
            _emit_error(
                "USAGE_ERROR", "category-paths requires --category-ids.",
                hint="Provide --category-ids '2619526011,172282' or a JSON array.",
                exit_code=EXIT_USAGE_ERROR,
            )
        body["categoryIds"] = _parse_category_ids(args.category_ids)

    elif args.api == "category-filter":
        missing = [
            name
            for name, val in (
                ("--marketplace-id", args.marketplace_id),
                ("--time-range", args.time_range),
                ("--sample-scope", args.sample_scope),
            )
            if not val
        ]
        if missing:
            _emit_error(
                "USAGE_ERROR",
                f"category-filter requires: {', '.join(missing)}.",
                hint="Example: --marketplace-id US --time-range l7d --sample-scope all_asin",
                exit_code=EXIT_USAGE_ERROR,
            )
        body["marketplaceId"] = args.marketplace_id
        body["timeRange"] = args.time_range
        body["sampleScope"] = args.sample_scope
        if args.category_id:
            body["categoryId"] = args.category_id
        _apply_pagination(body, args.page, args.size, is_filter=True)

    elif args.api == "niche-filter":
        if not args.marketplace_id:
            _emit_error(
                "USAGE_ERROR", "niche-filter requires --marketplace-id.",
                hint="Example: --marketplace-id US",
                exit_code=EXIT_USAGE_ERROR,
            )
        body["marketplaceId"] = args.marketplace_id
        if args.niche_id:
            body["nicheId"] = args.niche_id
        if args.niche_title:
            body["nicheTitle"] = args.niche_title
        _apply_pagination(body, args.page, args.size, is_filter=True)

    _apply_extras(body, args.extra)
    return body


# ---------------------------------------------------------------------------
# API call with retry
# ---------------------------------------------------------------------------
def call_api(api_key, body, endpoint, max_retries=3, timeout=120):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "Pangolinfo-CLI/2.0",
    }

    for attempt in range(max_retries):
        try:
            result = _http_post(endpoint, body, headers=headers, timeout=timeout)
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
                    "RATE_LIMIT", "Rate limited by API server.",
                    hint="Wait a moment and retry, or reduce request frequency.",
                    exit_code=EXIT_NETWORK_ERROR,
                )

            # 4xx errors are not retryable (except 429 above)
            if 400 <= e.code < 500:
                try:
                    parsed = json.loads(error_body) if error_body else {}
                    if isinstance(parsed, dict) and "code" in parsed:
                        return parsed
                except (json.JSONDecodeError, ValueError):
                    pass
                detail = ""
                if error_body:
                    try:
                        err_json = json.loads(error_body)
                        detail = f" Server: {err_json.get('message', error_body[:200])}"
                    except (json.JSONDecodeError, ValueError):
                        detail = f" Server: {error_body[:200]}"
                _emit_error(
                    "API_ERROR", f"HTTP {e.code} from API.{detail}",
                    hint="Check your request parameters and try again.",
                    exit_code=EXIT_NETWORK_ERROR,
                )

            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue

            detail = ""
            if error_body:
                try:
                    err_json = json.loads(error_body)
                    detail = f" Server: {err_json.get('message', error_body[:200])}"
                except (json.JSONDecodeError, ValueError):
                    detail = f" Server: {error_body[:200]}"

            _emit_error(
                "API_ERROR", f"HTTP {e.code} from API.{detail}",
                hint="Check your request parameters and try again.",
                exit_code=EXIT_NETWORK_ERROR,
            )
        except urllib.error.URLError:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            _emit_error(
                "NETWORK", "Network error communicating with API.",
                hint="Check your internet connection and try again.",
                exit_code=EXIT_NETWORK_ERROR,
            )

    _emit_error(
        "NETWORK", "API call failed after retries.",
        hint="Check your internet connection and try again.",
        exit_code=EXIT_NETWORK_ERROR,
    )


def handle_response(result, api_key, body, endpoint, timeout=120):
    if result.get("code") == 1004:
        new_api_key = refresh_api_key()
        return call_api(new_api_key, body, endpoint, timeout=timeout)
    return result


# ---------------------------------------------------------------------------
# Output extraction
# ---------------------------------------------------------------------------
def extract_output(result, api_name):
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

    data = result.get("data") or {}
    output = {"success": True, "api": api_name}

    # Upstream shapes:
    #   data: { items: { data: [...], total, page, size, totalPages } }  -- most APIs
    #   data: { items: [...] }                                           -- category-paths
    items_wrapper = data.get("items")
    if isinstance(items_wrapper, dict):
        output["items"] = items_wrapper.get("data", [])
        for key in ("total", "page", "size", "totalPages"):
            if key in items_wrapper:
                output[key] = items_wrapper[key]
    elif isinstance(items_wrapper, list):
        output["items"] = items_wrapper
    else:
        output["data"] = data

    if isinstance(output.get("items"), list):
        output["results_count"] = len(output["items"])

    return output


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Pangolinfo Amazon Niche Data API Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            '  python3 pangolinfo.py --api category-search --keyword "headphones"\n'
            '  python3 pangolinfo.py --api category-tree --parent-path "2619526011"\n'
            '  python3 pangolinfo.py --api category-paths --category-ids "2619526011,172282"\n'
            "  python3 pangolinfo.py --api category-filter --marketplace-id US --time-range l7d --sample-scope all_asin\n"
            '  python3 pangolinfo.py --api niche-filter --marketplace-id US --niche-title "yoga mat"\n'
            "  python3 pangolinfo.py --auth-only\n"
        ),
    )
    parser.add_argument(
        "--api", choices=sorted(API_ROUTES.keys()),
        help="Which niche API to call",
    )

    # Pagination
    parser.add_argument("--page", type=int, help="1-based page number (max 10 for filter APIs)")
    parser.add_argument("--size", type=int, help="Items per page (max 10 for filter APIs)")

    # category-tree
    parser.add_argument("--parent-path", help="category-tree: parent browseNodeIdPath")

    # category-search
    parser.add_argument("--keyword", help="category-search: keyword (EN or CN)")

    # category-paths
    parser.add_argument("--category-ids", help="category-paths: comma-separated IDs or JSON array")

    # category-filter / niche-filter
    parser.add_argument("--marketplace-id", help="Marketplace code (e.g. US, UK, DE)")
    parser.add_argument("--time-range", help="Aggregation range (e.g. l7d, l30d, l90d)")
    parser.add_argument("--sample-scope", help="Sample scope (e.g. all_asin)")
    parser.add_argument("--category-id", help="category-filter: single-category detail")

    # niche-filter
    parser.add_argument("--niche-id", help="niche-filter: specific niche ID")
    parser.add_argument("--niche-title", help="niche-filter: keyword match on title")

    # Extra filters
    parser.add_argument(
        "--extra", action="append", default=[],
        help="Extra request field as key=value (JSON-parsed); repeatable",
    )

    # Common
    parser.add_argument("--auth-only", action="store_true", help="Auth check only")
    parser.add_argument("--raw", action="store_true", help="Output raw API response")
    parser.add_argument("--timeout", type=int, default=120, help="Timeout in seconds (default: 120)")
    parser.add_argument(
        "--cache-key", action="store_true",
        help="Persist API key to ~/.pangolinfo_api_key. Also: PANGOLINFO_CACHE=1.",
    )

    args = parser.parse_args()

    # Configure caching
    global CACHE_TO_DISK
    CACHE_TO_DISK = bool(args.cache_key) or os.environ.get("PANGOLINFO_CACHE", "").strip().lower() in (
        "1", "true", "yes", "on",
    )

    if not args.api and not args.auth_only:
        parser.error("--api is required unless using --auth-only")

    # Authenticate
    api_key = get_api_key()

    if args.auth_only:
        preview = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 12 else "***"
        print(json.dumps({
            "success": True,
            "message": "Authentication successful",
            "api_key_preview": preview,
        }, indent=2))
        sys.exit(EXIT_SUCCESS)

    # Build request
    path, label = API_ROUTES[args.api]
    endpoint = f"{AMZSCOPE_BASE}{path}"
    body = build_body(args)

    # Call API
    result = call_api(api_key, body, endpoint, timeout=args.timeout)

    if result is None:
        _emit_error(
            "NETWORK", "API call failed after retries.",
            hint="Check your internet connection and try again.",
            exit_code=EXIT_NETWORK_ERROR,
        )

    result = handle_response(result, api_key, body, endpoint, timeout=args.timeout)

    if result is None:
        _emit_error(
            "NETWORK", "API call failed after token refresh.",
            hint="Check your internet connection and try again.",
            exit_code=EXIT_NETWORK_ERROR,
        )

    # Output
    if args.raw:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        output = extract_output(result, label)
        if output.get("success"):
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(output, indent=2, ensure_ascii=False), file=sys.stderr)

    if result.get("code") != 0:
        sys.exit(EXIT_API_ERROR)

    sys.exit(EXIT_SUCCESS)


if __name__ == "__main__":
    main()
