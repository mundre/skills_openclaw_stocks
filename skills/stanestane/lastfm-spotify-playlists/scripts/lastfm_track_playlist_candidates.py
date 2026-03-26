from __future__ import annotations

import argparse
from collections import defaultdict
from typing import Any, Dict, List, Tuple

from lastfm_common import dump_json, ensure_list, lastfm_get, load_credentials


def get_artist_top_tracks(artist: str, *, api_key: str, limit: int, autocorrect: int = 1) -> List[Dict[str, Any]]:
    data = lastfm_get(
        "artist.gettoptracks",
        {"artist": artist, "limit": limit, "autocorrect": autocorrect},
        api_key=api_key,
    )
    tracks = ensure_list(data.get("toptracks", {}).get("track"))
    return tracks


def get_similar_tracks(artist: str, track: str, *, api_key: str, limit: int, autocorrect: int = 1) -> List[Dict[str, Any]]:
    data = lastfm_get(
        "track.getsimilar",
        {"artist": artist, "track": track, "limit": limit, "autocorrect": autocorrect},
        api_key=api_key,
    )
    return ensure_list(data.get("similartracks", {}).get("track"))


def norm_seed(track: Dict[str, Any]) -> Dict[str, Any]:
    artist = track.get("artist", {}) if isinstance(track.get("artist"), dict) else {}
    return {
        "track": track.get("name"),
        "artist": artist.get("name") or artist.get("#text"),
        "playcount": int(track.get("playcount", 0) or 0),
        "listeners": int(track.get("listeners", 0) or 0),
        "url": track.get("url"),
    }


def norm_similar(track: Dict[str, Any], seed_artist: str, seed_track: str) -> Dict[str, Any]:
    artist = track.get("artist", {}) if isinstance(track.get("artist"), dict) else {}
    return {
        "track": track.get("name"),
        "artist": artist.get("name") or artist.get("#text"),
        "match": float(track.get("match", 0.0) or 0.0),
        "url": track.get("url"),
        "seed_artist": seed_artist,
        "seed_track": seed_track,
    }


def key_for(artist: str, track: str) -> Tuple[str, str]:
    return (artist.strip().casefold(), track.strip().casefold())


def main() -> None:
    parser = argparse.ArgumentParser(description="Build playlist candidates from Last.fm similar tracks seeded by an artist's top tracks.")
    parser.add_argument("artist", help="Seed artist, e.g. Placebo")
    parser.add_argument("--seed-count", type=int, default=5, help="How many top tracks to use as seeds.")
    parser.add_argument("--similar-per-seed", type=int, default=10, help="How many similar tracks to fetch for each seed track.")
    parser.add_argument("--final-limit", type=int, default=20, help="How many merged candidates to return.")
    parser.add_argument("--autocorrect", type=int, choices=[0, 1], default=1)
    parser.add_argument("--creds", help="Path to credentials JSON file.")
    args = parser.parse_args()

    creds = load_credentials(args.creds)
    api_key = creds["api_key"]

    seeds_raw = get_artist_top_tracks(args.artist, api_key=api_key, limit=args.seed_count, autocorrect=args.autocorrect)
    seeds = [norm_seed(item) for item in seeds_raw]

    merged: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for seed in seeds:
        sim_raw = get_similar_tracks(
            seed["artist"] or args.artist,
            seed["track"],
            api_key=api_key,
            limit=args.similar_per_seed,
            autocorrect=args.autocorrect,
        )
        for item in sim_raw:
            candidate = norm_similar(item, seed["artist"] or args.artist, seed["track"])
            c_artist = candidate.get("artist") or ""
            c_track = candidate.get("track") or ""
            if not c_artist or not c_track:
                continue
            if c_artist.casefold() == args.artist.casefold():
                continue
            k = key_for(c_artist, c_track)
            if k not in merged:
                merged[k] = {
                    "artist": candidate["artist"],
                    "track": candidate["track"],
                    "score": 0.0,
                    "source_count": 0,
                    "sources": [],
                    "url": candidate.get("url"),
                }
            merged[k]["score"] += candidate["match"]
            merged[k]["source_count"] += 1
            merged[k]["sources"].append({
                "seed_artist": candidate["seed_artist"],
                "seed_track": candidate["seed_track"],
                "match": candidate["match"],
            })

    ranked = sorted(
        merged.values(),
        key=lambda item: (item["source_count"], item["score"]),
        reverse=True,
    )[: args.final_limit]

    dump_json({
        "seed_artist": args.artist,
        "seed_tracks": seeds,
        "candidate_count": len(ranked),
        "candidates": ranked,
    })


if __name__ == "__main__":
    main()
