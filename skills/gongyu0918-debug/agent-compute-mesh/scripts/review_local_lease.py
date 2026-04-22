#!/usr/bin/env python3
"""Review a stage-1 local lease result and record local acceptance."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lease_root", help="Path to the lease root directory")
    parser.add_argument("decision", choices=["accept", "reject"], help="Local review decision")
    parser.add_argument("--reviewer", default="local-operator", help="Reviewer name")
    parser.add_argument("--notes", default="", help="Review notes")
    parser.add_argument("--json", action="store_true", help="Print machine-readable output")
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    lease_root = Path(args.lease_root).resolve()
    artifacts_dir = lease_root / "artifacts"
    acceptance_path = artifacts_dir / "acceptance.json"
    result_bundle_path = artifacts_dir / "result_bundle.json"
    if not acceptance_path.exists() or not result_bundle_path.exists():
        raise SystemExit("lease artifacts are incomplete")

    acceptance = load_json(acceptance_path)
    result_bundle = load_json(result_bundle_path)
    reviewed_at = utc_now()
    status = "accepted" if args.decision == "accept" else "rejected"
    acceptance.update(
        {
            "status": status,
            "reviewed_at": reviewed_at,
            "reviewer": args.reviewer,
            "notes": args.notes,
        }
    )
    result_bundle["acceptance_status"] = status
    result_bundle["reviewed_by"] = args.reviewer
    result_bundle["reviewed_at"] = reviewed_at
    if status == "accepted":
        result_bundle["accepted_by"] = args.reviewer
        result_bundle["accepted_at"] = reviewed_at
    write_json(acceptance_path, acceptance)
    write_json(result_bundle_path, result_bundle)

    output = {
        "lease_root": str(lease_root),
        "status": status,
        "reviewer": args.reviewer,
        "acceptance": str(acceptance_path),
        "result_bundle": str(result_bundle_path),
    }
    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(f"status={status}")
        print(f"acceptance={acceptance_path}")
        print(f"result_bundle={result_bundle_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
