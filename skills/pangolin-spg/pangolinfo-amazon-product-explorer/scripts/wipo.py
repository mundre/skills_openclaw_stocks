#!/usr/bin/env python3
"""
Pangolinfo WIPO API Client

Zero-dependency Python client for Pangolinfo's WIPO Global Design Database API.
Searches industrial design registrations by IRN, holder, product, Locarno class, etc.

Usage:
    pangolinfo.py --irn "000298" --ds AL
    pangolinfo.py --hol "Apple" --ds US
    pangolinfo.py --prod "chair" --ds US --status ACT
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
WIPO_ENDPOINT = f"{API_BASE}/api/v3/wipo"
API_KEY_CACHE_PATH = Path.home() / ".pangolinfo_api_key"

REFERRER_TAG = "clawhub_wipo"
PANGOLINFO_URL = f"https://pangolinfo.com/?referrer={REFERRER_TAG}"

CACHE_TO_DISK = False

EXIT_SUCCESS = 0
EXIT_API_ERROR = 1
EXIT_USAGE_ERROR = 2
EXIT_NETWORK_ERROR = 3
EXIT_AUTH_ERROR = 4


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
# WIPO request builder
# ---------------------------------------------------------------------------
def build_wipo_body(args):
    """Build the WIPO API request body from CLI args."""
    body = {}

    if args.irn:
        body["irn"] = args.irn
    if args.ds:
        body["ds"] = args.ds
    if args.hol:
        body["hol"] = args.hol
    if args.prod:
        body["prod"] = args.prod
    if args.lcs:
        body["lcs"] = args.lcs
    if args.status:
        body["status"] = args.status
    if args.record_id:
        body["id"] = args.record_id
    if args.id_search:
        body["id_search"] = args.id_search
    if args.source:
        body["source"] = args.source
    if args.rd:
        body["rd"] = args.rd
    if args.ed:
        body["ed"] = args.ed

    body["from"] = args.offset
    body["num"] = args.num

    return body


# ---------------------------------------------------------------------------
# API call with retry
# ---------------------------------------------------------------------------
def call_api(api_key, body, max_retries=3, timeout=120):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "Pangolinfo-CLI/2.0",
    }

    for attempt in range(max_retries):
        try:
            result = _http_post(WIPO_ENDPOINT, body, headers=headers, timeout=timeout)
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


# ---------------------------------------------------------------------------
# Output extraction
# ---------------------------------------------------------------------------
def extract_wipo_output(result):
    """Transform raw WIPO API response into clean output."""
    data = result.get("data")
    if data is None:
        # Check for error code in top-level response
        code = result.get("code")
        if code is not None and code != 0:
            return {
                "success": False,
                "error": {
                    "code": "API_ERROR",
                    "api_code": code,
                    "message": result.get("message", "Unknown API error"),
                    "hint": f"Pangolinfo API error code {code}. Retry or check request.",
                },
            }
        return {
            "success": False,
            "error": {
                "code": "API_ERROR",
                "message": "No data returned from WIPO API.",
                "hint": "Check your search parameters and try again.",
            },
        }

    total = data.get("total", 0)
    hits = data.get("hits", [])

    results = []
    for hit in hits:
        record = {
            "irn": hit.get("IRN", ""),
            "status": hit.get("STATUS", ""),
            "registration_date": hit.get("RD", ""),
            "expiry_date": hit.get("ED", ""),
            "holder": hit.get("HOL", []),
            "product": hit.get("PROD", []),
            "locarno_class": hit.get("LCS", []),
            "designated_states": hit.get("DS", []),
            "source": hit.get("SOURCE", ""),
            "id": hit.get("ID", ""),
            "doc": hit.get("DOC", ""),
            "dc": hit.get("DC", ""),
        }
        img_data = hit.get("IMG_DATA", [])
        if img_data:
            record["images"] = img_data
        detail_url = hit.get("DETAIL_URL")
        if detail_url:
            record["detail_url"] = detail_url
        detail_data = hit.get("DETAIL_DATA")
        if detail_data:
            record["detail_data"] = detail_data
        results.append(record)

    return {
        "success": True,
        "total": total,
        "results_count": len(results),
        "results": results,
    }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Pangolinfo WIPO Global Design Database API Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            '  python3 pangolinfo.py --irn "000298" --ds AL\n'
            '  python3 pangolinfo.py --hol "Apple" --ds US\n'
            '  python3 pangolinfo.py --prod "chair" --ds US --status ACT\n'
            '  python3 pangolinfo.py --lcs "23-01" --ds AL\n'
            "  python3 pangolinfo.py --auth-only\n"
        ),
    )
    parser.add_argument("--irn", help="International registration number")
    parser.add_argument("--ds", help="Designated state (country code, e.g. US, AL, CN)")
    parser.add_argument("--hol", help="Holder / rights owner name")
    parser.add_argument("--prod", help="Product name")
    parser.add_argument("--lcs", help="Locarno classification code (e.g. 23-01)")
    parser.add_argument("--status", help="Legal status filter (e.g. ACT for active)")
    parser.add_argument("--id", dest="record_id", help="Unique record identifier")
    parser.add_argument("--id-search", dest="id_search", help="ID variant search")
    parser.add_argument("--source", help="Data source filter")
    parser.add_argument("--rd", help="Registration date filter (e.g. 2022-01-01)")
    parser.add_argument("--ed", help="Expiry date filter")
    parser.add_argument(
        "--from", dest="offset", type=int, default=0,
        help="Pagination offset, 0-based (default: 0)",
    )
    parser.add_argument(
        "--num", type=int, default=10,
        help="Results per page (default: 10)",
    )
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

    # Validate: need at least one search parameter (unless auth-only)
    has_search_param = any([
        args.irn, args.ds, args.hol, args.prod, args.lcs,
        args.status, args.record_id, args.id_search, args.source,
        args.rd, args.ed,
    ])
    if not args.auth_only and not has_search_param:
        parser.error(
            "At least one search parameter is required (e.g. --irn, --hol, --prod, --lcs, --ds). "
            "Use --auth-only for auth check."
        )

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

    # Build request body
    body = build_wipo_body(args)

    # Call API
    result = call_api(api_key, body, timeout=args.timeout)

    if result is None:
        _emit_error(
            "NETWORK", "API call failed after retries.",
            hint="Check your internet connection and try again.",
            exit_code=EXIT_NETWORK_ERROR,
        )

    # Handle token refresh on 1004
    if isinstance(result, dict) and result.get("code") == 1004:
        new_api_key = refresh_api_key()
        result = call_api(new_api_key, body, timeout=args.timeout)
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
        output = extract_wipo_output(result)
        if output.get("success"):
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(output, indent=2, ensure_ascii=False), file=sys.stderr)

    # Exit code based on success
    if isinstance(result, dict):
        code = result.get("code")
        if code is not None and code != 0:
            sys.exit(EXIT_API_ERROR)
        if result.get("data") is None:
            sys.exit(EXIT_API_ERROR)

    sys.exit(EXIT_SUCCESS)


if __name__ == "__main__":
    main()
