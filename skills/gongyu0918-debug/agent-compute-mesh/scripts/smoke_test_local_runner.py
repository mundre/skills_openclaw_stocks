#!/usr/bin/env python3
"""Smoke test the stage-1 local runner."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return proc.stdout


def main() -> int:
    job_path = ROOT / "assets" / "stage1_sample_job.json"
    run_script = ROOT / "scripts" / "run_local_lease.py"
    review_script = ROOT / "scripts" / "review_local_lease.py"

    with tempfile.TemporaryDirectory(prefix="agent-compute-mesh-smoke-") as temp_dir:
        runtime_root = Path(temp_dir) / "runtime"
        result = json.loads(
            run(
                [
                    sys.executable,
                    str(run_script),
                    str(job_path),
                    "--runtime-root",
                    str(runtime_root),
                    "--json",
                ]
            )
        )
        lease_root = Path(result["lease_root"])
        artifacts_dir = Path(result["artifacts_dir"])
        for filename in ("result_bundle.json", "sandbox_receipt.json", "billing_receipt.json", "acceptance.json"):
            if not (artifacts_dir / filename).exists():
                raise AssertionError(f"missing artifact: {filename}")

        acceptance_before = json.loads((artifacts_dir / "acceptance.json").read_text(encoding="utf-8"))
        if acceptance_before["status"] != "pending":
            raise AssertionError("acceptance should start in pending state")

        review_result = json.loads(
            run(
                [
                    sys.executable,
                    str(review_script),
                    str(lease_root),
                    "accept",
                    "--reviewer",
                    "smoke-test",
                    "--notes",
                    "stage-1 local runner smoke test",
                    "--json",
                ]
            )
        )
        if review_result["status"] != "accepted":
            raise AssertionError("review script did not accept the lease")

        acceptance_after = json.loads((artifacts_dir / "acceptance.json").read_text(encoding="utf-8"))
        result_bundle_after = json.loads((artifacts_dir / "result_bundle.json").read_text(encoding="utf-8"))
        if acceptance_after["status"] != "accepted":
            raise AssertionError("acceptance file did not update")
        if result_bundle_after["acceptance_status"] != "accepted":
            raise AssertionError("result bundle did not update")

    print("OK: stage-1 local runner smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
