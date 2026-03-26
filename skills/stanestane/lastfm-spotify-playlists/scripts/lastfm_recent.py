from __future__ import annotations

import argparse
from typing import Any, Dict

from lastfm_common import dump_json, ensure_list, lastfm_get, load_credentials


TRACK_FIELDS = ("name", "artist", "album", "date", "url", "streamable", "loved")
ARTIST_FIELDS = ("name", "playcount", "url")


def normalize_recent_track(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "track": item.get("name"),
        "artist": item.get("artist", {}).get("#text") if isinstance(item.get("artist"), dict) else item.get("artist"),
        "album": item.get("album", {}).get("#text") if isinstance(item.get("album"), dict) else item.get("album"),
        "nowplaying": item.get("@attr", {}).get("nowplaying") == "true",
        "played_at": item.get("date", {}).get("#text"),
        "uts": item.get("date", {}).get("uts"),
        "url": item.get("url"),
        "loved": item.get("loved") == "1",
    }


def normalize_top_artist(item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "artist": item.get("name"),
        "playcount": int(item.get("playcount", 0) or 0),
        "listeners": int(item.get("listeners", 0) or 0),
        "mbid": item.get("mbid") or None,
        "url": item.get("url"),
    }


def normalize_top_track(item: Dict[str, Any]) -> Dict[str, Any]:
    artist = item.get("artist", {}) if isinstance(item.get("artist"), dict) else {}
    return {
        "track": item.get("name"),
        "artist": artist.get("name") or artist.get("#text"),
        "playcount": int(item.get("playcount", 0) or 0),
        "listeners": int(item.get("listeners", 0) or 0),
        "mbid": item.get("mbid") or None,
        "url": item.get("url"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch recent or top Last.fm listening data.")
    parser.add_argument("mode", choices=["recent-tracks", "top-artists", "top-tracks"])
    parser.add_argument("--user", help="Last.fm username. Defaults to LASTFM_USERNAME or credentials file value.")
    parser.add_argument("--period", default="1month", choices=["7day", "1month", "3month", "6month", "12month", "overall"])
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--creds", help="Path to credentials JSON file.")
    args = parser.parse_args()

    creds = load_credentials(args.creds)
    user = args.user or creds.get("username")
    if not user:
        raise SystemExit("Missing Last.fm username. Pass --user or set LASTFM_USERNAME / credentials file username.")

    if args.mode == "recent-tracks":
        data = lastfm_get(
            "user.getrecenttracks",
            {"user": user, "limit": args.limit, "page": args.page, "extended": 0},
            api_key=creds["api_key"],
        )
        tracks = ensure_list(data.get("recenttracks", {}).get("track"))
        dump_json({
            "user": user,
            "mode": args.mode,
            "page": args.page,
            "limit": args.limit,
            "items": [normalize_recent_track(item) for item in tracks],
        })
        return

    if args.mode == "top-artists":
        data = lastfm_get(
            "user.gettopartists",
            {"user": user, "period": args.period, "limit": args.limit, "page": args.page},
            api_key=creds["api_key"],
        )
        artists = ensure_list(data.get("topartists", {}).get("artist"))
        dump_json({
            "user": user,
            "mode": args.mode,
            "period": args.period,
            "page": args.page,
            "limit": args.limit,
            "items": [normalize_top_artist(item) for item in artists],
        })
        return

    data = lastfm_get(
        "user.gettoptracks",
        {"user": user, "period": args.period, "limit": args.limit, "page": args.page},
        api_key=creds["api_key"],
    )
    tracks = ensure_list(data.get("toptracks", {}).get("track"))
    dump_json({
        "user": user,
        "mode": args.mode,
        "period": args.period,
        "page": args.page,
        "limit": args.limit,
        "items": [normalize_top_track(item) for item in tracks],
    })


if __name__ == "__main__":
    main()
