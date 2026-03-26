from __future__ import annotations

import argparse
from typing import Any, Dict

from lastfm_common import dump_json, ensure_list, lastfm_get, load_credentials


def normalize_similar_artist(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artist": item.get("name"),
        "match": float(item.get("match", 0.0) or 0.0),
        "mbid": item.get("mbid") or None,
        "url": item.get("url"),
    }


def normalize_similar_track(item: Dict[str, Any]) -> Dict[str, Any]:
    artist = item.get("artist", {}) if isinstance(item.get("artist"), dict) else {}
    return {
        "track": item.get("name"),
        "artist": artist.get("name") or artist.get("#text"),
        "match": float(item.get("match", 0.0) or 0.0),
        "mbid": item.get("mbid") or None,
        "url": item.get("url"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch Last.fm similar artists or tracks.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    artist_parser = subparsers.add_parser("artist", help="Find artists similar to a seed artist.")
    artist_parser.add_argument("name", help="Seed artist name.")
    artist_parser.add_argument("--limit", type=int, default=25)
    artist_parser.add_argument("--autocorrect", type=int, choices=[0, 1], default=1)
    artist_parser.add_argument("--creds", help="Path to credentials JSON file.")

    track_parser = subparsers.add_parser("track", help="Find tracks similar to a seed track.")
    track_parser.add_argument("artist", help="Seed artist name.")
    track_parser.add_argument("track", help="Seed track name.")
    track_parser.add_argument("--limit", type=int, default=25)
    track_parser.add_argument("--autocorrect", type=int, choices=[0, 1], default=1)
    track_parser.add_argument("--creds", help="Path to credentials JSON file.")

    args = parser.parse_args()
    creds = load_credentials(getattr(args, "creds", None))

    if args.command == "artist":
        data = lastfm_get(
            "artist.getsimilar",
            {"artist": args.name, "limit": args.limit, "autocorrect": args.autocorrect},
            api_key=creds["api_key"],
        )
        artists = ensure_list(data.get("similarartists", {}).get("artist"))
        dump_json({
            "seed_artist": args.name,
            "limit": args.limit,
            "items": [normalize_similar_artist(item) for item in artists],
        })
        return

    data = lastfm_get(
        "track.getsimilar",
        {
            "artist": args.artist,
            "track": args.track,
            "limit": args.limit,
            "autocorrect": args.autocorrect,
        },
        api_key=creds["api_key"],
    )
    tracks = ensure_list(data.get("similartracks", {}).get("track"))
    dump_json({
        "seed_artist": args.artist,
        "seed_track": args.track,
        "limit": args.limit,
        "items": [normalize_similar_track(item) for item in tracks],
    })


if __name__ == "__main__":
    main()
