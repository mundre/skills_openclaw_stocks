#!/usr/bin/env python3
"""
Outbound AI Call - Query Call Records
Cross-platform Python version (works on Windows, macOS, Linux)

Supports automatic retry mechanism and request state tracking.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


# Retry configuration
INITIAL_WAIT = 30      # First query wait time (seconds)
RETRY_INTERVAL = 20    # Retry interval (seconds)
MAX_RETRIES = 12       # Maximum retry attempts (total ~4.5 min)


def get_config():
    """Load API key and base URL from environment or config file."""
    api_key = os.environ.get("OUTBOUND_API_KEY", "")
    base_url = os.environ.get("OUTBOUND_BASE_URL", "https://www.skill.black")
    
    if not api_key:
        config_path = Path.home() / ".openclaw" / "secrets" / "outbound.json"
        if config_path.exists():
            try:
                config = json.loads(config_path.read_text())
                api_key = config.get("api_key", "")
                base_url = config.get("base_url", base_url)
            except (json.JSONDecodeError, IOError):
                pass
    
    return api_key, base_url


def get_memory_paths():
    """Get paths to memory files."""
    skill_dir = Path(__file__).parent.parent
    memory_dir = skill_dir / "memory" / "skills"
    memory_dir.mkdir(parents=True, exist_ok=True)
    return (
        memory_dir / "requests.jsonl",
        memory_dir / "costs.jsonl"
    )


def load_jsonl(path: Path) -> list:
    """Load JSONL file as list of records.
    
    Handles various edge cases:
    - File doesn't exist
    - Invalid JSON lines (skipped)
    - Non-dict values (skipped)
    - Multi-line JSON (attempts to fix)
    """
    if not path.exists():
        return []
    
    records = []
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 尝试按行解析
    for line in content.split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            # 只接受字典类型
            if isinstance(obj, dict):
                records.append(obj)
        except json.JSONDecodeError:
            # 跳过无效行
            pass
    
    return records


def save_jsonl(path: Path, records: list):
    """Save list of records to JSONL file."""
    with open(path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def get_request_state(requests_file: Path, request_id: str) -> dict:
    """Get request state from requests.jsonl."""
    records = load_jsonl(requests_file)
    for record in reversed(records):  # Most recent first
        if isinstance(record, dict) and record.get("request_id") == request_id:
            return record
    return {}


def update_request_state(requests_file: Path, request_id: str, status: str, retry_count: int = 0):
    """Update or create request state in requests.jsonl."""
    records = load_jsonl(requests_file)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Find and update existing record
    found = False
    for record in records:
        if isinstance(record, dict) and record.get("request_id") == request_id:
            record["status"] = status
            record["retry_count"] = retry_count
            record["updated_at"] = timestamp
            found = True
            break
    
    # Create new if not found
    if not found:
        records.append({
            "request_id": request_id,
            "status": status,
            "retry_count": retry_count,
            "created_at": timestamp,
            "updated_at": timestamp
        })
    
    # Deduplicate by request_id (keep most recent)
    seen = set()
    unique_records = []
    for record in reversed(records):
        rid = record.get("request_id")
        if rid not in seen:
            seen.add(rid)
            unique_records.append(record)
    
    save_jsonl(requests_file, list(reversed(unique_records)))


def save_call_record(costs_file: Path, request_id: str, call_data: dict):
    """Save call record to costs.jsonl."""
    records = load_jsonl(costs_file)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Build record
    record = {
        "request_id": request_id,
        "phone": call_data.get("phone", ""),
        "status": call_data.get("status", ""),
        "statusDesc": call_data.get("statusDesc", ""),
        "category": call_data.get("category", ""),
        "callStartTime": call_data.get("callStartTime", ""),
        "sid": call_data.get("sid", ""),
        "chatLogs": call_data.get("chatLogs", []),
        "timestamp": timestamp
    }
    
    # Update or append
    found = False
    for i, r in enumerate(records):
        if r.get("request_id") == request_id:
            records[i] = record
            found = True
            break
    
    if not found:
        records.append(record)
    
    save_jsonl(costs_file, records)


def query_api(request_id: str, debug: bool = False) -> dict:
    """Query API for call record."""
    api_key, base_url = get_config()
    
    if not api_key:
        print("Error: OUTBOUND_API_KEY not set")
        sys.exit(1)
    
    url = f"{base_url}/api/voice_call/llmSceneCallResult"
    request_body = {"reqId": request_id}
    
    if debug:
        print("=== API Request ===")
        print(f"URL: {url}")
        print(f"Body: {json.dumps(request_body)}")
        print()
    
    req = Request(
        url,
        data=json.dumps(request_body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Access-Key": api_key
        },
        method="POST"
    )
    
    try:
        with urlopen(req, timeout=30) as response:
            body = response.read().decode("utf-8")
            return json.loads(body)
    except HTTPError as e:
        print(f"HTTP Error: {e.code}")
        body = e.read().decode("utf-8")
        print(body)
        return None
    except URLError as e:
        print(f"Network Error: {e.reason}")
        return None


def parse_call_response(response: dict) -> dict:
    """Parse API response and extract call data.
    
    API returns: {"code": "10000", "message": "成功", "data": {...}}
    """
    if not response:
        return None
    
    code = response.get("code", "")
    message = response.get("message", "")
    data = response.get("data", {}) or {}
    
    return {
        "code": code,
        "message": message,
        "phone": data.get("phone", ""),
        "status": str(data.get("status", "0")),
        "statusDesc": data.get("statusDesc", ""),
        "category": data.get("category", "UNKNOWN"),
        "callStartTime": data.get("callStartTime", ""),
        "sid": data.get("sid", ""),
        "chatLogs": data.get("chatLogs", [])
    }


def print_call_result(call_data: dict, request_id: str, costs_file: Path):
    """Print call result and save to costs file."""
    print("=== Call Record Retrieved ===")
    print()
    print(f"Phone: {call_data['phone']}")
    print(f"Status: {call_data['statusDesc']} (status: {call_data['status']}, category: {call_data['category']})")
    print(f"Call Start: {call_data['callStartTime']}")
    print(f"Session ID: {call_data['sid']}")
    print()
    print("=== Conversation ===")
    
    chat_logs = call_data.get("chatLogs", [])
    if chat_logs:
        for log in chat_logs:
            msg_time = log.get("msgTime", "")
            role = log.get("role", "")
            content = log.get("content", "")
            print(f"[{msg_time}] {role}: {content}")
    else:
        print("(No conversation logs)")
    
    print()
    
    # Save record
    save_call_record(costs_file, request_id, call_data)
    print(f"Record saved to: {costs_file}")


def query_by_request_id(request_id: str, no_retry: bool = False, debug: bool = False):
    """Query by request ID with optional retry mechanism."""
    requests_file, costs_file = get_memory_paths()
    
    print(f"=== Querying Request: {request_id} ===")
    
    # Check existing state
    existing_state = get_request_state(requests_file, request_id)
    retry_count = existing_state.get("retry_count", 0)
    
    if existing_state.get("status") == "completed":
        print("Request already completed. Checking local logs...")
        records = load_jsonl(costs_file)
        for record in records:
            if record.get("request_id") == request_id:
                print(json.dumps(record, indent=2, ensure_ascii=False))
                return
        print("No local record found.")
        return
    
    if retry_count >= MAX_RETRIES:
        print(f"Max retries ({MAX_RETRIES}) exceeded for this request.")
        print("Status: failed")
        update_request_state(requests_file, request_id, "failed", retry_count)
        sys.exit(1)
    
    # No retry mode
    if no_retry:
        update_request_state(requests_file, request_id, "querying", retry_count)
        response = query_api(request_id, debug)
        
        if not response:
            update_request_state(requests_file, request_id, "pending", retry_count + 1)
            sys.exit(1)
        
        call_data = parse_call_response(response)
        
        if call_data["code"] != "10000":
            print(f"API Error: {call_data['code']} - {call_data['message']}")
            update_request_state(requests_file, request_id, "pending", retry_count + 1)
            sys.exit(1)
        
        # Check call status
        if call_data["status"] == "5" or call_data["category"] == "CONNECTED":
            print_call_result(call_data, request_id, costs_file)
            update_request_state(requests_file, request_id, "completed", retry_count)
        elif call_data["status"] == "8" or call_data["category"] == "UN_CONNECTED":
            print("=== Call Failed ===")
            print(f"Phone: {call_data['phone']}")
            print(f"Status: {call_data['statusDesc']} (status: {call_data['status']})")
            update_request_state(requests_file, request_id, "completed", retry_count)
        else:
            print(f"Call status: {call_data['statusDesc']} (status: {call_data['status']}, category: {call_data['category']})")
            print("Call not completed yet.")
            update_request_state(requests_file, request_id, "pending", retry_count + 1)
        
        return
    
    # With retry mechanism
    while retry_count < MAX_RETRIES:
        if retry_count == 0:
            print(f"First query attempt (waiting {INITIAL_WAIT}s)...")
            time.sleep(INITIAL_WAIT)
        else:
            print(f"Retry attempt {retry_count} (waiting {RETRY_INTERVAL}s)...")
            time.sleep(RETRY_INTERVAL)
        
        update_request_state(requests_file, request_id, "querying", retry_count)
        
        response = query_api(request_id, debug)
        
        if not response:
            print("Query failed")
            retry_count += 1
            update_request_state(requests_file, request_id, "pending", retry_count)
            continue
        
        call_data = parse_call_response(response)
        
        if call_data["code"] != "10000":
            print(f"API Error: {call_data['code']} - {call_data['message']}")
            print("Call not completed yet. Waiting...")
            retry_count += 1
            update_request_state(requests_file, request_id, "pending", retry_count)
            continue
        
        # Check call status
        if call_data["status"] == "5" or call_data["category"] == "CONNECTED":
            print_call_result(call_data, request_id, costs_file)
            update_request_state(requests_file, request_id, "completed", retry_count)
            print()
            print("Note: status=5 means conversation completed, no further polling needed.")
            return
        
        elif call_data["status"] == "8" or call_data["category"] == "UN_CONNECTED":
            print("=== Call Failed ===")
            print(f"Phone: {call_data['phone']}")
            print(f"Status: {call_data['statusDesc']} (status: {call_data['status']})")
            print("No retry needed for failed calls.")
            save_call_record(costs_file, request_id, call_data)
            update_request_state(requests_file, request_id, "completed", retry_count)
            return
        
        else:
            print(f"Call status: {call_data['statusDesc']} (status: {call_data['status']}, category: {call_data['category']})")
            print("Call not completed yet. Waiting...")
            retry_count += 1
            update_request_state(requests_file, request_id, "pending", retry_count)
    
    # Max retries exceeded
    print()
    print(f"Max retries ({MAX_RETRIES}) exceeded.")
    print("Performing final query to save current state...")
    
    final_response = query_api(request_id, debug)
    if final_response:
        call_data = parse_call_response(final_response)
        print(f"Final status: {call_data['statusDesc']} (status: {call_data['status']}, category: {call_data['category']})")
        save_call_record(costs_file, request_id, call_data)
        print(f"Record saved to: {costs_file}")
    
    update_request_state(requests_file, request_id, "failed", retry_count)
    sys.exit(1)


def query_local(status: str = None, phone: str = None, limit: int = 20):
    """Query local call records."""
    _, costs_file = get_memory_paths()
    
    if not costs_file.exists():
        print("No local call records found")
        print(f"Log file: {costs_file}")
        return
    
    print("=== Local Call Records ===")
    print(f"Log file: {costs_file}")
    print()
    
    records = load_jsonl(costs_file)
    
    # Filter
    if status:
        records = [r for r in records if r.get("status") == status]
    if phone:
        records = [r for r in records if r.get("phone") == phone]
    
    # Limit
    records = records[:limit]
    
    for record in records:
        print(json.dumps(record, ensure_ascii=False))
    
    print()
    print(f"Total records: {len(records)}")


def main():
    parser = argparse.ArgumentParser(
        description="Query Outbound AI call records with automatic retry mechanism",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Retry Mechanism:
  - First query after 30 seconds (required for call to complete)
  - Retry every 20 seconds if call not completed
  - Maximum 12 retries (total ~4.5 min)
  - Completed requests won't be re-queried

Examples:
  # Query by request ID (with retry)
  uv run scripts/query-call.py --request-id "e561a439-7b2a-4024-88f2-638cd593f315"

  # Query without retry
  uv run scripts/query-call.py --request-id "e561a439-7b2a-4024-88f2-638cd593f315" --no-retry

  # Query local logs
  uv run scripts/query-call.py --local --status 5 --limit 10
"""
    )
    
    parser.add_argument("--request-id", help="Request ID (returned from make-call)")
    parser.add_argument("--no-retry", action="store_true", help="Disable automatic retry")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--local", action="store_true", help="Query local logs only")
    parser.add_argument("--status", help="Filter by status (for local query)")
    parser.add_argument("--phone", help="Filter by phone (for local query)")
    parser.add_argument("--limit", type=int, default=20, help="Result limit (default: 20)")
    
    args = parser.parse_args()
    
    if args.local:
        query_local(args.status, args.phone, args.limit)
    elif args.request_id:
        query_by_request_id(args.request_id, args.no_retry, args.debug)
    else:
        print("Please specify --request-id or --local")
        print("Run: uv run scripts/query-call.py --help")
        sys.exit(1)


if __name__ == "__main__":
    main()