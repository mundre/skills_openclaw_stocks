#!/usr/bin/env python3
"""One-time setup script for Gmail API OAuth credentials.

Creates ~/.openclaw/credentials/gmail.json with a refresh token.
Requires: google-auth-oauthlib, google-api-python-client

See references/setup.md for full setup guide.
"""

import json
import os
import sys

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDS_PATH = os.path.expanduser("~/.openclaw/credentials/gmail.json")
CREDS_DIR = os.path.dirname(CREDS_PATH)


def check_dependencies():
    missing = []
    try:
        import google_auth_oauthlib  # noqa: F401
    except ImportError:
        missing.append("google-auth-oauthlib")
    try:
        import googleapiclient  # noqa: F401
    except ImportError:
        missing.append("google-api-python-client")
    if missing:
        print("Missing required packages. Install with:")
        print(f"  pip install {' '.join(missing)}")
        sys.exit(1)


def save_credentials(creds_data):
    os.makedirs(CREDS_DIR, exist_ok=True)
    with open(CREDS_PATH, "w") as f:
        json.dump(creds_data, f, indent=2)
    os.chmod(CREDS_PATH, 0o600)
    print(f"\nCredentials saved to {CREDS_PATH}")


def run_oauth_flow():
    from google_auth_oauthlib.flow import InstalledAppFlow

    print("\nPaste your Google OAuth credentials (from Google Cloud Console > Credentials):")
    print("  Application type: Desktop app\n")

    client_id = input("Client ID: ").strip()
    client_secret = input("Client Secret: ").strip()

    if not client_id or not client_secret:
        print("Error: Client ID and Client Secret are required.")
        sys.exit(1)

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }

    print("\nOpening browser for Google authorization...")
    print("(If no browser opens, a URL will be printed below to paste manually)\n")

    try:
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
        creds = flow.run_local_server(port=0, open_browser=True, timeout_seconds=120)
    except Exception as e:
        print(f"\nOAuth flow failed: {e}")
        print("Make sure your Gmail address is added as a Test User in the OAuth consent screen.")
        sys.exit(1)

    save_credentials({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": creds.refresh_token,
    })

    print("Setup complete! Test with:")
    print("  python3 scripts/check_gmail.py")


def main():
    check_dependencies()

    print("Gmail Checker — OAuth Setup")
    print("=" * 35)

    if os.path.exists(CREDS_PATH):
        print(f"\nCredentials already exist at {CREDS_PATH}")
        overwrite = input("Overwrite? [y/N] ").strip().lower()
        if overwrite != "y":
            print("Aborted.")
            return

    run_oauth_flow()


if __name__ == "__main__":
    main()
