#!/usr/bin/env python3
"""
Persona Sync - Cross-platform Python sync script
Usage: python scripts/sync.py <init|pull|push|status|log> [args...]

Environment variables:
  PERSONA_STORE_DIR  Override default store directory (~/.openclaw/persona-store)

Security:
  Credentials are stored via 'git credential helper' (not embedded in URLs).
  The .gitauth file holds username:token but is read-only during operation.
  Token is never written to .git/config or git logs.
"""

import os
import sys
import json
import subprocess
import re
from pathlib import Path
from datetime import datetime

# ── Config ──────────────────────────────────────────────────────────────────

STORE_DIR = Path(os.environ.get("PERSONA_STORE_DIR", Path.home() / ".openclaw" / "persona-store"))
AUTH_FILE = STORE_DIR / ".gitauth"
LOG_FILE = STORE_DIR / "sync.log"
STATE_FILE = STORE_DIR / "state.json"
MEMORY_FILE = STORE_DIR / "memory.jsonl"


def setup_proxy():
    """Auto-detect and set proxy from git config."""
    if os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY"):
        return
    for key in ["http.proxy", "https.proxy"]:
        try:
            result = subprocess.run(
                ["git", "config", "--global", "--get", key],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0 and result.stdout.strip():
                proxy = result.stdout.strip()
                os.environ["HTTP_PROXY"] = proxy
                os.environ["HTTPS_PROXY"] = proxy
                return
        except Exception:
            pass


def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
    line = f"[{ts}] {msg}"
    print(line)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def read_auth() -> tuple[str, str]:
    if not AUTH_FILE.exists():
        print(f"ERROR: Auth file not found: {AUTH_FILE}", file=sys.stderr)
        print("Run 'sync init <repo-url>' first.", file=sys.stderr)
        sys.exit(1)
    content = AUTH_FILE.read_text(encoding="utf-8").strip()
    m_user = re.search(r"username=([^,]+)", content)
    m_tok = re.search(r"token=(.+)", content)
    if not m_user or not m_tok:
        print("ERROR: Invalid .gitauth format. Expected: username=xxx,token=TOKEN", file=sys.stderr)
        sys.exit(1)
    return m_user.group(1).strip(), m_tok.group(1).strip()


def setup_git_credentials(username: str, token: str, repo_url: str):
    """
    Store credentials securely via 'git credential helper'.
    The token is stored in ~/.git-credentials (mode 0600), NOT in .git/config.
    """
    subprocess.run(
        ["git", "config", "--global", "credential.helper", "store"],
        capture_output=True, check=False
    )
    m = re.match(r"https?://([^/]+)(?:/.*)?", repo_url)
    host = m.group(1) if m else "github.com"
    cred_input = f"protocol=https\nhost={host}\nusername={username}\npassword={token}\n\n"
    subprocess.run(["git", "credential", "fill"], input=cred_input, capture_output=True, text=True, check=False)
    subprocess.run(["git", "credential", "approve"], input=cred_input, capture_output=True, text=True, check=False)


def cd_store():
    if not (STORE_DIR / ".git").exists():
        print(f"ERROR: {STORE_DIR} is not a git repo. Run 'sync init' first.", file=sys.stderr)
        sys.exit(1)
    os.chdir(STORE_DIR)


def run(cmd: list[str], capture: bool = True, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=capture, text=True, check=check, cwd=STORE_DIR)


def strip_auth(url: str) -> str:
    return re.sub(r"https?://[^@]+@", "https://", url)


# ── Commands ────────────────────────────────────────────────────────────────

def cmd_init(repo_url: str):
    if not repo_url:
        print("Usage: sync init <repo-url>", file=sys.stderr)
        sys.exit(1)

    STORE_DIR.mkdir(parents=True, exist_ok=True)
    os.chdir(STORE_DIR)

    if (STORE_DIR / ".git").exists():
        username, token = read_auth()
        setup_git_credentials(username, token, repo_url)
        clean_url = strip_auth(repo_url)
        run(["git", "remote", "set-url", "origin", clean_url], check=False)
        log(f"init: re-authenticated to {clean_url}")
        print("Already initialized. Credentials updated (token no longer in .git/config).")
        return

    if not AUTH_FILE.exists():
        print("No .gitauth found. Creating template...")
        AUTH_FILE.write_text("username=YOUR_GITHUB_USERNAME,token=YOUR_PAT\n", encoding="utf-8")
        os.chmod(AUTH_FILE, 0o600)
        print(f"Created {AUTH_FILE} — please edit it with your GitHub credentials.")
        sys.exit(1)

    username, token = read_auth()
    setup_git_credentials(username, token, repo_url)

    clean_url = strip_auth(repo_url)
    log(f"init: cloning {clean_url}")
    run(["git", "init"], check=False)
    run(["git", "remote", "add", "origin", clean_url], check=False)
    run(["git", "fetch", "origin"])
    run(["git", "checkout", "HEAD"], check=False)

    log("init: done")
    print(f"Initialized persona-store at {STORE_DIR}")
    print("Credentials stored securely via git credential helper.")


def cmd_pull():
    cd_store()
    log("pull: starting")
    before = run(["git", "rev-parse", "HEAD"], check=False).stdout.strip() or ""
    result = run(["git", "pull", "--ff-only", "origin", "HEAD"], check=False)
    if result.returncode != 0:
        log("pull: ff-only failed, trying rebase")
        run(["git", "pull", "--rebase", "origin", "HEAD"])
    after = run(["git", "rev-parse", "HEAD"], check=False).stdout.strip() or ""
    if before != after:
        log(f"pull: updated {before} → {after}")
        print("Pulled updates.")
    else:
        log("pull: already up-to-date")
        print("Already up-to-date.")


def cmd_push(entry: str):
    if not entry:
        print("Usage: sync push \"<json-entry>\"", file=sys.stderr)
        sys.exit(1)

    cd_store()
    log("push: appending entry")
    MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")

    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
    version = 1
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            version = state.get("version", 0) + 1
        except Exception:
            pass

    state = {
        "last_sync": now,
        "last_entry": now,
        "version": version,
        "agents": ["main"]
    }
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    run(["git", "add", "."])
    run(["git", "commit", "-m", f"sync: push entry {datetime.now().strftime('%Y-%m-%d %H:%M')}"])

    log(f"push: committing version {version}")

    result = run(["git", "push", "origin", "HEAD"], check=False)
    if result.returncode != 0:
        log("push: non-fast-forward, rebasing...")
        run(["git", "pull", "--rebase", "origin", "HEAD"])
        run(["git", "push", "origin", "HEAD"])

    log("push: done")
    print(f"Pushed entry (version {version}).")


def cmd_status():
    cd_store()
    if not STATE_FILE.exists():
        print("No state.json found. Run 'sync pull' first.")
        return
    state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    print("=== Persona Sync Status ===")
    print(f"Last sync: {state.get('last_sync', 'unknown')}")
    print(f"Version:   {state.get('version', 0)}")
    result = run(["git", "status", "--porcelain"], check=False)
    pending = len(result.stdout.strip().splitlines()) if result.stdout.strip() else 0
    print(f"Pending changes: {pending}")
    entries = 0
    if MEMORY_FILE.exists():
        entries = len(MEMORY_FILE.read_text(encoding="utf-8").strip().splitlines())
    print(f"Memory entries: {entries}")


def cmd_log(n: int = 20):
    if not LOG_FILE.exists():
        print("No sync log found.")
        return
    lines = LOG_FILE.read_text(encoding="utf-8").strip().splitlines()
    for line in lines[-n:]:
        print(line)


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    setup_proxy()
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    args = sys.argv[2:]

    if cmd == "init":
        cmd_init(*args)
    elif cmd == "pull":
        cmd_pull()
    elif cmd == "push":
        cmd_push(*args)
    elif cmd == "status":
        cmd_status()
    elif cmd == "log":
        cmd_log(int(args[0]) if args else 20)
    else:
        print("Usage: sync <init|pull|push|status|log> [args...]", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
