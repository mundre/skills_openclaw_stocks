from __future__ import annotations

import argparse
import json

from spotify_common import add_tracks_to_playlist, create_playlist, current_user, get_access_token


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a Spotify playlist and optionally add track URIs.")
    parser.add_argument("name", help="Playlist name.")
    parser.add_argument("--description", default="")
    parser.add_argument("--public", action="store_true")
    parser.add_argument("--track-uri", action="append", default=[], help="Track URI to add. Repeat for multiple tracks.")
    parser.add_argument("--creds")
    parser.add_argument("--token")
    args = parser.parse_args()

    token = get_access_token(args.creds, args.token)
    me = current_user(token)
    playlist = create_playlist(me["id"], args.name, access_token=token, public=args.public, description=args.description)
    result = {
        "playlist_id": playlist.get("id"),
        "playlist_name": playlist.get("name"),
        "playlist_url": playlist.get("external_urls", {}).get("spotify"),
        "added": 0,
    }
    if args.track_uri:
        add_tracks_to_playlist(playlist["id"], args.track_uri, access_token=token)
        result["added"] = len(args.track_uri)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
