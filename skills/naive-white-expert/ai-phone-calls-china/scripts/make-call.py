#!/usr/bin/env python3
"""
Outbound AI Call - Create Outbound Call
Cross-platform Python version (works on Windows, macOS, Linux)
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def get_config():
    """Load API key and base URL from environment or config file."""
    api_key = os.environ.get("OUTBOUND_API_KEY", "")
    base_url = os.environ.get("OUTBOUND_BASE_URL", "https://www.skill.black")
    
    # Try config file if env not set
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


def validate_phone(phone: str) -> bool:
    """Validate Chinese mobile phone number format."""
    return bool(re.match(r"^1[3-9]\d{9}$", phone))


def make_call(phone: str, messages: list, must_outbound: bool = False, debug: bool = False):
    """Execute outbound call API request."""
    api_key, base_url = get_config()
    
    if not api_key:
        print("Error: OUTBOUND_API_KEY not set")
        print("Run: export OUTBOUND_API_KEY=your-api-key")
        print("Or create ~/.openclaw/secrets/outbound.json")
        sys.exit(1)
    
    # Build request
    url = f"{base_url}/api/voice_call/llmSceneCall"
    request_body = {
        "phone": phone,
        "messages": messages,
        "mustOutbound": must_outbound
    }
    
    if debug:
        print("=== Request Info ===")
        print(f"URL: {url}")
        print(f"Body: {json.dumps(request_body, ensure_ascii=False)}")
        print()
    
    # Send request
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
            result = json.loads(body)
    except HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"HTTP Error: {e.code}")
        print(body)
        sys.exit(1)
    except URLError as e:
        print(f"Network Error: {e.reason}")
        sys.exit(1)
    
    # Parse response - API returns: {"code": "10000", "message": "成功", "data": xxx}
    code = result.get("code", "")
    message = result.get("message", "")
    data = result.get("data", "")
    
    # Handle response
    if code == "10000":
        print("✓ Call created successfully")
        print()
        print(f"Request ID: {data}")
        print(f"Message: {message}")
        
        # Save to requests.jsonl
        skill_dir = Path(__file__).parent.parent
        memory_dir = skill_dir / "memory" / "skills"
        memory_dir.mkdir(parents=True, exist_ok=True)
        requests_file = memory_dir / "requests.jsonl"
        
        record = {
            "request_id": data,
            "phone": phone,
            "status": "pending",
            "messages": messages,
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        with open(requests_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        
        print()
        print(f"Request tracked in: {requests_file}")
        print()
        print("To query call result:")
        print(f'  uv run scripts/query-call.py --request-id "{data}"')
        
        return data
    
    elif code == "190001":
        print("✗ Call blocked by risk control")
        print(f"Code: {code}")
        print(f"Reason: {message}")
        print()
        print("风控拦截，无法外呼。请更换通话内容或联系管理员。")
        sys.exit(2)
    
    elif code == "110000":
        print("✗ Authentication failed")
        print(f"Code: {code}")
        print(f"Message: {message or result_msg}")
        print()
        print("API Key 无效或已过期，请更新配置：")
        print("  1. 申请 Key: https://www.skill.black")
        print("  2. 更新环境变量: export OUTBOUND_API_KEY=your-new-key")
        print("  或更新配置文件: ~/.openclaw/secrets/outbound.json")
        sys.exit(1)
    
    elif code == "430004":
        print("✗ Missing required parameters")
        print(f"Code: {code}")
        print(f"Message: {message}")
        print()
        print("后端判断缺少必填参数，请补充信息后重试。")
        print("或使用 --must-outbound 强制外呼。")
        sys.exit(1)
    
    elif code == "430005":
        print("✗ Missing optional parameters")
        print(f"Code: {code}")
        print(f"Message: {message}")
        print()
        print("后端建议补充更多信息，可以使用 --must-outbound 强制外呼。")
        sys.exit(1)
    
    else:
        print("✗ Call creation failed")
        print(f"Code: {code}")
        print(f"Message: {message}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Create a Outbound AI outbound call",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic call
  uv run scripts/make-call.py --phone "18033009923" --messages '["用户: 帮我给蜀九香预约位子"]'

  # Force outbound (even with incomplete info)
  uv run scripts/make-call.py --phone "15200001111" --messages '["用户: 给我爸打电话"]' --must-outbound
"""
    )
    
    parser.add_argument("--phone", required=True, help="Target phone number (e.g., 13800138000)")
    parser.add_argument("--messages", required=True, help="Conversation messages as JSON array")
    parser.add_argument("--must-outbound", action="store_true", help="Force outbound even with incomplete info")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    
    args = parser.parse_args()
    
    # Validate phone
    if not validate_phone(args.phone):
        print(f"Error: Invalid phone number format (expected: 1xxxxxxxxxx, got: {args.phone})")
        sys.exit(1)
    
    # Parse messages
    try:
        messages = json.loads(args.messages)
        if not isinstance(messages, list):
            raise ValueError("Messages must be a JSON array")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON for messages: {e}")
        sys.exit(1)
    
    make_call(args.phone, messages, args.must_outbound, args.debug)


if __name__ == "__main__":
    main()