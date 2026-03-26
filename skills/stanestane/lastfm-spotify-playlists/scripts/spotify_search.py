from __future__ import annotations

import argparse
import json

from spotify_common import get_access_token, search_tracks


def main() -> None:
    parser = argparse.ArgumentParser(description="Search Spotify tracks.")
    parser.add_argument("query", help="Search query string.")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--market")
    parser.add_argument("--creds")
    parser.add_argument("--token")
    args = parser.parse_args()

    token = get_access_token(args.creds, args.token)
    data = search_tracks(args.query, access_token=token, limit=args.limit, market=args.market)
    items = data.get("tracks", {}).get("items", [])
    simplified = [
        {
            "name": item.get("name"),
            "artists": ", ".join(artist.get("name") for artist in item.get("artists", [])),
            "album": item.get("album", {}).get("name"),
            "uri": item.get("uri"),
            "id": item.get("id"),
            "url": item.get("external_urls", {}).get("spotify"),
        }
        for item in items
    ]
    print(json.dumps({"query": args.query, "items": simplified}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
