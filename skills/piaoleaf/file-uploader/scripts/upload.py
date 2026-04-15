#!/usr/bin/env python3
"""
file-uploader skill - Upload files to aliyun and return public URL.

Usage:
    python upload.py <file_path> [--token JWT_TOKEN] [--device-id DEVICE_ID]

Config file (~/.qclaw/skills/file-uploader/config.json) is used as fallback:
    {
        "jwt_token": "your_jwt_token_here",
        "device_id": "your_device_id_here"
    }

Note: JWT token can be obtained by logging in at https://www.szmpy.com
      Device-ID must be obtained from the administrator.
"""

import sys
import os
import json
import argparse
import mimetypes

try:
    import requests
except ImportError:
    print("ERROR: requests library not found. Run: pip install requests")
    sys.exit(1)

UPLOAD_URL = "https://xcx.szmpy.com/api/image/uploadfile"
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")


def load_config():
    """Load config from config.json if it exists."""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_config(config: dict):
    """Save config to config.json."""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"Config saved to: {CONFIG_PATH}")


def upload_file(file_path: str, jwt_token: str, device_id: str) -> dict:
    """Upload a file and return the response dict."""
    if not os.path.exists(file_path):
        return {"success": False, "error": f"File not found: {file_path}"}

    file_name = os.path.basename(file_path)
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "application/octet-stream"

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Device-ID": device_id,
    }

    try:
        with open(file_path, "rb") as f:
            files = {"file": (file_name, f, mime_type)}
            response = requests.post(UPLOAD_URL, headers=headers, files=files, timeout=60)

        response.raise_for_status()
        data = response.json()
        return {"success": True, "raw": data, "status_code": response.status_code}

    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "error": f"HTTP {e.response.status_code}: {e.response.text[:500]}",
        }
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Connection failed. Check network or URL."}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out (60s)."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def extract_url(raw: dict) -> str | None:
    """
    Try common response structures to extract the file URL.
    Adjust this function if the API returns a different structure.
    """
    # Try common patterns
    candidates = [
        raw.get("data", {}).get("url") if isinstance(raw.get("data"), dict) else None,
        raw.get("data", {}).get("path") if isinstance(raw.get("data"), dict) else None,
        raw.get("data", {}).get("fileUrl") if isinstance(raw.get("data"), dict) else None,
        raw.get("url"),
        raw.get("path"),
        raw.get("fileUrl"),
        raw.get("result", {}).get("url") if isinstance(raw.get("result"), dict) else None,
        # If data is a string directly
        raw.get("data") if isinstance(raw.get("data"), str) else None,
    ]
    for c in candidates:
        if c and isinstance(c, str) and c.startswith("http"):
            return c
    return None


def main():
    parser = argparse.ArgumentParser(description="Upload a file to tiaowulan.com.cn")
    parser.add_argument("file", help="Path to the file to upload")
    parser.add_argument("--token", help="JWT token (overrides config)")
    parser.add_argument("--device-id", dest="device_id", help="Device-ID header value (overrides config)")
    parser.add_argument("--save-config", action="store_true", help="Save --token and --device-id to config.json")
    parser.add_argument("--show-raw", action="store_true", help="Print full raw API response")
    args = parser.parse_args()

    config = load_config()

    jwt_token = args.token or config.get("jwt_token")
    device_id = args.device_id or config.get("device_id")

    if args.save_config:
        if args.token:
            config["jwt_token"] = args.token
        if args.device_id:
            config["device_id"] = args.device_id
        save_config(config)

    if not jwt_token:
        print("ERROR: JWT token is required. Use --token or set it in config.json")
        print(f"  Run: python upload.py <file> --token YOUR_TOKEN --device-id YOUR_DEVICE_ID --save-config")
        sys.exit(1)

    if not device_id:
        print("ERROR: Device-ID is required. Use --device-id or set it in config.json")
        sys.exit(1)

    print(f"Uploading: {args.file}")
    result = upload_file(args.file, jwt_token, device_id)

    if not result["success"]:
        print(f"UPLOAD FAILED: {result['error']}")
        sys.exit(1)

    raw = result["raw"]

    if args.show_raw:
        print("Raw response:")
        print(json.dumps(raw, indent=2, ensure_ascii=False))

    url = extract_url(raw)
    if url:
        print(f"SUCCESS")
        print(f"URL: {url}")
        # Output JSON for easy parsing by the skill
        print(json.dumps({"success": True, "url": url, "raw": raw}, ensure_ascii=False))
    else:
        print("Upload succeeded but could not extract URL from response.")
        print("Raw response:")
        print(json.dumps(raw, indent=2, ensure_ascii=False))
        print(json.dumps({"success": True, "url": None, "raw": raw}, ensure_ascii=False))


if __name__ == "__main__":
    main()
