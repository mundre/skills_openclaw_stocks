#!/usr/bin/env python3

import argparse
import http.client
import json
import sys
import debug_utils

API_BASE_URL = "https://eagle-api.xplai.ai"
API_ENDPOINT = "/api/solve/audio_generate_skill"


def generate_audio(text):
    url = f"{API_BASE_URL}{API_ENDPOINT}"

    payload = {"text": text}

    debug_utils.log_request("POST", url, json=payload)

    try:
        conn = http.client.HTTPSConnection("eagle-api.xplai.ai", timeout=30)
        headers = {"Content-Type": "application/json"}
        conn.request("POST", API_ENDPOINT, json.dumps(payload), headers)
        response = conn.getresponse()
        response_body = response.read().decode("utf-8")
        
        if response.status >= 400:
            print(f"HTTP Error: {response.status} {response.reason}", file=sys.stderr)
            sys.exit(1)
        
        debug_utils.log_response(response, response_body)
        
        result = json.loads(response_body)
        conn.close()

        if result.get("code") == 0:
            data = result.get("data", {})
            video_id = data.get("video_id")
            status = data.get("card", {}).get("status")
            print(f"Audio generation request submitted successfully!")
            print(f"Audio ID: {video_id}")
            print(f"Status: {status}")
            return video_id
        else:
            print(f"Error: {result.get('msg')}", file=sys.stderr)
            sys.exit(1)
    except (http.client.HTTPException, OSError) as e:
        print(f"Request failed: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Generate audio using xplai API")
    parser.add_argument("text", type=str, help="Text content to convert to audio")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode to print request/response details")

    args = parser.parse_args()

    debug_utils.set_debug(args.debug)

    audio_id = generate_audio(args.text)
    if audio_id:
        print(f"use ./xplai_status.py {audio_id} to check the status")


if __name__ == "__main__":
    main()
