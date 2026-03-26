from __future__ import annotations

import argparse
import json

from spotify_common import authorize, current_user, get_access_token


def main() -> None:
    parser = argparse.ArgumentParser(description="Authorize Spotify access for local helper scripts.")
    parser.add_argument("--scopes", nargs="*", default=["playlist-modify-private", "playlist-modify-public"], help="OAuth scopes.")
    parser.add_argument("--creds", help="Path to Spotify credentials JSON.")
    parser.add_argument("--token", help="Path to Spotify token JSON.")
    parser.add_argument("--print-auth-url", action="store_true", help="Print auth URL instead of opening a browser automatically.")
    args = parser.parse_args()

    authorize(args.scopes, creds_path=args.creds, token_path=args.token, open_browser=not args.print_auth_url)
    access_token = get_access_token(args.creds, args.token)
    me = current_user(access_token)
    print(json.dumps({"authorized_as": me.get("id"), "display_name": me.get("display_name")}, indent=2))


if __name__ == "__main__":
    main()
