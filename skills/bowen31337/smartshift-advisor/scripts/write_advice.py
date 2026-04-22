#!/usr/bin/env python3
"""
write_advice.py - Writes SmartShift advice JSON to the data directory.
Reads JSON from stdin and saves it with a timestamp.
"""
import json
import sys
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def main():
    try:
        raw = sys.stdin.read().strip()
        advice = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    required = ['export_threshold', 'discharge_floor', 'strategy', 'reasoning']
    for field in required:
        if field not in advice:
            print(f"ERROR: Missing required field: {field}", file=sys.stderr)
            sys.exit(1)

    advice['timestamp'] = datetime.now().isoformat()

    # Write latest advice
    latest_path = os.path.join(DATA_DIR, 'latest_advice.json')
    with open(latest_path, 'w') as f:
        json.dump(advice, f, indent=2)

    # Write timestamped archive
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    archive_path = os.path.join(DATA_DIR, f'advice_{ts}.json')
    with open(archive_path, 'w') as f:
        json.dump(advice, f, indent=2)

    print(f"✅ Advice written to {latest_path}")
    print(f"📁 Archived to {archive_path}")
    print(f"Strategy: {advice['strategy']}")
    print(f"Export threshold: {advice['export_threshold']}c/kWh")
    print(f"Discharge floor: {advice['discharge_floor']}%")
    print(f"Reasoning: {advice['reasoning']}")

if __name__ == '__main__':
    main()
