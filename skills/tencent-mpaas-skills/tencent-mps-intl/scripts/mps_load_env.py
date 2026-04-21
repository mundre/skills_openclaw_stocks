#!/usr/bin/env python3
"""
mps_load_env.py — Tencent Cloud MPS Skill Environment Variable Auto-Loader

Features:
  Scans the following files. If a file contains any of the specified environment
  variable KEYs, all KEY=VALUE lines in that file are loaded into the current
  process's os.environ (without overwriting existing values):
    /etc/environment
    /etc/profile
    ~/.bashrc
    ~/.profile
    ~/.bash_profile
    ~/.env

  Target variables (if any one of them exists in a file, that file will be loaded):
    TENCENTCLOUD_SECRET_ID
    TENCENTCLOUD_SECRET_KEY
    TENCENTCLOUD_COS_BUCKET
    TENCENTCLOUD_COS_REGION
    TENCENTCLOUD_API_REGION  (optional, MPS API call region, default: ap-guangzhou)

Usage (call from other scripts):
    from mps_load_env import ensure_env_loaded
    ensure_env_loaded()
"""

import os
import re
import sys

# Target variables to detect
_TARGET_VARS = {
    "TENCENTCLOUD_SECRET_ID",
    "TENCENTCLOUD_SECRET_KEY",
    "TENCENTCLOUD_COS_BUCKET",
    "TENCENTCLOUD_COS_REGION",
    "TENCENTCLOUD_API_REGION",
}

# Candidate file list to scan (ordered by priority)
_ENV_FILES = [
    "/etc/environment",
    "/etc/profile",
    os.path.expanduser("~/.bashrc"),
    os.path.expanduser("~/.profile"),
    os.path.expanduser("~/.bash_profile"),
    os.path.expanduser("~/.env"),
]

# Regex for KEY=VALUE lines (supports quoted values)
_KV_RE = re.compile(
    r"""^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(['"]?)(.*?)\2\s*$"""
)


def _parse_env_file(filepath: str) -> dict:
    """
    Parse a shell-style environment variable file and return a {key: value} dict.
    Supports:
      KEY=value
      export KEY=value
      KEY="value with spaces"
      KEY='value'
      # comment lines (ignored)
    """
    result = {}
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.rstrip("\n")
                # Skip comments and blank lines
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                m = _KV_RE.match(line)
                if m:
                    key = m.group(1)
                    value = m.group(3)
                    result[key] = value
    except (OSError, IOError):
        pass
    return result


def _file_contains_target(parsed: dict) -> bool:
    """Check whether the parsed result contains at least one target variable."""
    return bool(_TARGET_VARS & set(parsed.keys()))


def load_env_files(verbose: bool = False) -> dict:
    """
    Scan all candidate files and load the contents of files containing target
    variables into os.environ. Existing environment variables are not overwritten
    (setdefault semantics).

    Returns: dict of newly loaded variables {key: value}
    """
    newly_loaded = {}

    for filepath in _ENV_FILES:
        if not os.path.isfile(filepath):
            if verbose:
                print(f"[load_env] Skipping (not found): {filepath}", file=sys.stderr)
            continue

        parsed = _parse_env_file(filepath)

        if not _file_contains_target(parsed):
            if verbose:
                print(f"[load_env] Skipping (no target variables): {filepath}", file=sys.stderr)
            continue

        if verbose:
            print(f"[load_env] Loading file: {filepath}", file=sys.stderr)

        for key, value in parsed.items():
            if key not in os.environ:
                os.environ[key] = value
                newly_loaded[key] = value
                if verbose:
                    # Show only the first 4 characters of secrets
                    display = value[:4] + "****" if len(value) > 4 else "****"
                    print(f"[load_env]   Set {key}={display}", file=sys.stderr)
            else:
                if verbose:
                    print(f"[load_env]   Skipping (already set): {key}", file=sys.stderr)

    return newly_loaded


def check_required_vars(required: list = None) -> list:
    """
    Check whether the required environment variables are set.
    Returns a list of missing variable names (empty list means all are set).
    """
    if required is None:
        required = ["TENCENTCLOUD_SECRET_ID", "TENCENTCLOUD_SECRET_KEY"]
    return [k for k in required if not os.environ.get(k)]


def _print_setup_hint(missing_vars: list) -> None:
    """Print a detailed configuration guide to the user when environment variable loading fails."""
    env_files_str = "\n".join(f"    • {f}" for f in _ENV_FILES)
    missing_str = "\n".join(f"    {k}=<your_value>" for k in missing_vars)
    hint = f"""
╔══════════════════════════════════════════════════════════════════╗
║              Tencent Cloud MPS Environment Variables Not Set     ║
╚══════════════════════════════════════════════════════════════════╝

The following environment variables are missing:
{missing_str}

Enable MPS service at: https://console.cloud.tencent.com/mps
Get your API keys at: https://console.cloud.tencent.com/cam/capi
Get bucket info at: https://console.cloud.tencent.com/mps/workflows/buckets

[Configuration] Please add the above variables to any of the following files,
then restart the conversation:
{env_files_str}

  Example (using ~/.profile):
    export TENCENTCLOUD_SECRET_ID=<your SecretId>
    export TENCENTCLOUD_SECRET_KEY=<your SecretKey>
    export TENCENTCLOUD_COS_BUCKET=<your Bucket name>
    export TENCENTCLOUD_COS_REGION=<Bucket region, e.g. ap-guangzhou>
    export TENCENTCLOUD_API_REGION=<MPS API call region, optional, default ap-guangzhou>

⚠️  Security notice: Configure your credentials through a secure channel (e.g., by directly editing the config file).

Once configured, restart the conversation to apply the changes.
"""
    print(hint, file=sys.stderr)


def ensure_env_loaded(
    required: list = None,
    verbose: bool = False,
) -> bool:
    """
    Ensure that the required environment variables are loaded.

    Execution flow:
      1. Check whether the required variables are already in os.environ
      2. If any are missing, scan candidate files and load them
      3. Check again and return whether all variables are ready

    Parameters:
      required  — list of variables that must be present; defaults to SECRET_ID / SECRET_KEY
      verbose   — whether to print loading logs to stderr

    Returns: True if all required variables are ready, False if any are still missing
    """
    if required is None:
        required = ["TENCENTCLOUD_SECRET_ID", "TENCENTCLOUD_SECRET_KEY"]

    missing_before = check_required_vars(required)
    if not missing_before:
        # All variables are ready, no loading needed
        return True

    if verbose:
        print(
            f"[load_env] Missing variables detected: {missing_before}, scanning environment variable files...",
            file=sys.stderr,
        )

    load_env_files(verbose=verbose)

    missing_after = check_required_vars(required)
    if missing_after:
        return False

    if verbose:
        print("[load_env] All required variables have been loaded.", file=sys.stderr)
    return True


# ─── Standalone execution: diagnostic mode ─────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Scan system environment variable files and load Tencent Cloud MPS required variables (diagnostic mode)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed loading logs"
    )
    parser.add_argument(
        "--check-only", action="store_true", help="Only check current environment variable status, do not load"
    )
    args = parser.parse_args()

    if args.check_only:
        print("=== Current Environment Variable Status ===")
        for var in sorted(_TARGET_VARS):
            val = os.environ.get(var, "")
            if val:
                display = val[:4] + "****" if len(val) > 4 else "****"
                status = f"✅ Set ({display})"
            else:
                status = "❌ Not set"
            print(f"  {var}: {status}")
        sys.exit(0)

    print("=== Scanning Environment Variable Files ===", flush=True)
    newly = load_env_files(verbose=True)
    sys.stderr.flush()

    print("\n=== Load Results ===")
    for var in sorted(_TARGET_VARS):
        val = os.environ.get(var, "")
        if val:
            display = val[:4] + "****" if len(val) > 4 else "****"
            status = f"✅ Set ({display})"
        else:
            status = "❌ Not set"
        print(f"  {var}: {status}")

    if newly:
        print(f"\n{len(newly)} new variable(s) loaded this time: {list(newly.keys())}")
    else:
        print("\nNo new variables loaded (all already set or no target variables found in files)")

    # Check whether required variables are ready; print configuration guide if missing
    required = ["TENCENTCLOUD_SECRET_ID", "TENCENTCLOUD_SECRET_KEY"]
    missing = check_required_vars(required)
    if missing:
        _print_setup_hint(missing)
        sys.exit(1)