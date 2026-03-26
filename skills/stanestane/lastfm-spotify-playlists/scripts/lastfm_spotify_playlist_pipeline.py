from __future__ import annotations

import argparse
import json
from typing import Any, Dict, List, Tuple

from lastfm_common import ensure_list, lastfm_get, load_credentials
from lastfm_track_playlist_candidates import get_artist_top_tracks, get_similar_tracks, norm_seed
from spotify_common import add_tracks_to_playlist, create_playlist, current_user, get_access_token, search_tracks


def key_for(artist: str, track: str) -> Tuple[str, str]:
    return (artist.strip().casefold(), track.strip().casefold())


def merge_candidate(merged: Dict[Tuple[str, str], Dict[str, Any]], *, seed_label: str, root_artist: str, artist: str, track: str, match: float, url: str | None) -> None:
    if not artist or not track:
        return
    if artist.casefold() == root_artist.casefold():
        return
    k = key_for(artist, track)
    if k not in merged:
        merged[k] = {
            'artist': artist,
            'track': track,
            'score': 0.0,
            'source_count': 0,
            'sources': [],
            'url': url,
        }
    merged[k]['score'] += float(match or 0.0)
    merged[k]['source_count'] += 1
    merged[k]['sources'].append({'seed': seed_label, 'match': float(match or 0.0)})


def build_from_artist_top_tracks(artist: str, *, api_key: str, seed_count: int, similar_per_seed: int, root_artist: str, autocorrect: int = 1) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    seeds_raw = get_artist_top_tracks(artist, api_key=api_key, limit=seed_count, autocorrect=autocorrect)
    seeds = [norm_seed(item) for item in seeds_raw]
    merged: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for seed in seeds:
        seed_artist = seed.get('artist') or artist
        seed_track = seed.get('track')
        if not seed_track:
            continue
        sim_raw = get_similar_tracks(seed_artist, seed_track, api_key=api_key, limit=similar_per_seed, autocorrect=autocorrect)
        for item in sim_raw:
            item_artist = item.get('artist', {}) if isinstance(item.get('artist'), dict) else {}
            merge_candidate(
                merged,
                seed_label=f"{seed_artist} — {seed_track}",
                root_artist=root_artist,
                artist=item_artist.get('name') or item_artist.get('#text') or '',
                track=item.get('name') or '',
                match=float(item.get('match', 0.0) or 0.0),
                url=item.get('url'),
            )
    ranked = sorted(merged.values(), key=lambda item: (item['source_count'], item['score']), reverse=True)
    return seeds, ranked


def get_recent_track_seeds(user: str, *, api_key: str, limit: int) -> list[dict[str, Any]]:
    data = lastfm_get('user.getrecenttracks', {'user': user, 'limit': limit, 'page': 1, 'extended': 0}, api_key=api_key)
    tracks = ensure_list(data.get('recenttracks', {}).get('track'))
    seeds = []
    seen: set[tuple[str, str]] = set()
    for item in tracks:
        artist = item.get('artist', {}).get('#text') if isinstance(item.get('artist'), dict) else item.get('artist')
        track = item.get('name')
        if not artist or not track:
            continue
        k = key_for(artist, track)
        if k in seen:
            continue
        seen.add(k)
        seeds.append({'artist': artist, 'track': track, 'url': item.get('url')})
    return seeds


def build_from_recent_tracks(user: str, *, api_key: str, recent_count: int, similar_per_seed: int, autocorrect: int = 1) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    seeds = get_recent_track_seeds(user, api_key=api_key, limit=recent_count)
    merged: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for seed in seeds:
        sim_raw = get_similar_tracks(seed['artist'], seed['track'], api_key=api_key, limit=similar_per_seed, autocorrect=autocorrect)
        for item in sim_raw:
            item_artist = item.get('artist', {}) if isinstance(item.get('artist'), dict) else {}
            merge_candidate(
                merged,
                seed_label=f"{seed['artist']} — {seed['track']}",
                root_artist=seed['artist'],
                artist=item_artist.get('name') or item_artist.get('#text') or '',
                track=item.get('name') or '',
                match=float(item.get('match', 0.0) or 0.0),
                url=item.get('url'),
            )
    ranked = sorted(merged.values(), key=lambda item: (item['source_count'], item['score']), reverse=True)
    return seeds, ranked


def get_top_artists(user: str, *, api_key: str, period: str, limit: int) -> list[dict[str, Any]]:
    data = lastfm_get('user.gettopartists', {'user': user, 'period': period, 'limit': limit, 'page': 1}, api_key=api_key)
    artists = ensure_list(data.get('topartists', {}).get('artist'))
    return [{'artist': item.get('name'), 'playcount': int(item.get('playcount', 0) or 0), 'url': item.get('url')} for item in artists if item.get('name')]


def build_from_top_artists(user: str, *, api_key: str, period: str, artist_count: int, seed_count_per_artist: int, similar_per_seed: int, autocorrect: int = 1) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    artists = get_top_artists(user, api_key=api_key, period=period, limit=artist_count)
    merged: Dict[Tuple[str, str], Dict[str, Any]] = {}
    seeds: list[dict[str, Any]] = []
    for artist_item in artists:
        artist = artist_item['artist']
        artist_seeds, artist_ranked = build_from_artist_top_tracks(
            artist,
            api_key=api_key,
            seed_count=seed_count_per_artist,
            similar_per_seed=similar_per_seed,
            root_artist=artist,
            autocorrect=autocorrect,
        )
        for seed in artist_seeds:
            seeds.append({'artist': seed.get('artist') or artist, 'track': seed.get('track'), 'origin_artist': artist})
        for candidate in artist_ranked:
            k = key_for(candidate['artist'], candidate['track'])
            if k not in merged:
                merged[k] = {
                    'artist': candidate['artist'],
                    'track': candidate['track'],
                    'score': 0.0,
                    'source_count': 0,
                    'sources': [],
                    'url': candidate.get('url'),
                }
            merged[k]['score'] += candidate['score']
            merged[k]['source_count'] += candidate['source_count']
            merged[k]['sources'].extend(candidate['sources'])
    ranked = sorted(merged.values(), key=lambda item: (item['source_count'], item['score']), reverse=True)
    return seeds, ranked


def match_candidates_on_spotify(candidates: list[dict[str, Any]], *, final_limit: int, market: str | None = None) -> tuple[list[dict[str, Any]], list[str], list[dict[str, Any]]]:
    token = get_access_token()
    matched: list[dict[str, Any]] = []
    unmatched: list[dict[str, Any]] = []
    uris: list[str] = []
    for candidate in candidates:
        if len(uris) >= final_limit:
            break
        query = f'track:"{candidate["track"]}" artist:"{candidate["artist"]}"'
        result = search_tracks(query, access_token=token, limit=5, market=market)
        items = result.get('tracks', {}).get('items', [])
        pick = None
        for item in items:
            item_name = (item.get('name') or '').strip().casefold()
            artist_names = [(a.get('name') or '').strip().casefold() for a in item.get('artists', [])]
            if item_name == candidate['track'].strip().casefold() and candidate['artist'].strip().casefold() in artist_names:
                pick = item
                break
        if not pick and items:
            pick = items[0]
        if not pick:
            unmatched.append({'artist': candidate['artist'], 'track': candidate['track'], 'score': candidate['score']})
            continue
        if pick['uri'] in uris:
            continue
        uris.append(pick['uri'])
        matched.append({
            'artist': candidate['artist'],
            'track': candidate['track'],
            'score': candidate['score'],
            'spotify_name': pick.get('name'),
            'spotify_artists': ', '.join(a.get('name') for a in pick.get('artists', [])),
            'uri': pick.get('uri'),
            'url': pick.get('external_urls', {}).get('spotify'),
        })
    return matched, uris, unmatched


def maybe_create_playlist(name: str, description: str, uris: list[str]) -> dict[str, Any]:
    token = get_access_token()
    me = current_user(token)
    playlist = create_playlist(me['id'], name, access_token=token, public=False, description=description)
    add_tracks_to_playlist(playlist['id'], uris, access_token=token)
    return {'id': playlist.get('id'), 'name': playlist.get('name'), 'url': playlist.get('external_urls', {}).get('spotify')}


def main() -> None:
    parser = argparse.ArgumentParser(description='Build Last.fm-driven Spotify playlists in one command.')
    subparsers = parser.add_subparsers(dest='mode', required=True)

    artist_parser = subparsers.add_parser('artist-rule-c', help='Use one artist\'s top tracks as Last.fm similar-track seeds.')
    artist_parser.add_argument('artist')
    artist_parser.add_argument('--seed-count', type=int, default=5)
    artist_parser.add_argument('--similar-per-seed', type=int, default=10)

    recent_parser = subparsers.add_parser('recent-tracks', help='Use recent scrobbles as track-level Last.fm seeds.')
    recent_parser.add_argument('--user')
    recent_parser.add_argument('--recent-count', type=int, default=10)
    recent_parser.add_argument('--similar-per-seed', type=int, default=5)

    top_parser = subparsers.add_parser('top-artists-blend', help='Use the user\'s top artists for a period, then blend Rule C candidates across them.')
    top_parser.add_argument('--user')
    top_parser.add_argument('--period', default='1month', choices=['7day', '1month', '3month', '6month', '12month', 'overall'])
    top_parser.add_argument('--artist-count', type=int, default=5)
    top_parser.add_argument('--seed-count-per-artist', type=int, default=3)
    top_parser.add_argument('--similar-per-seed', type=int, default=5)

    parser.add_argument('--final-limit', type=int, default=20)
    parser.add_argument('--market')
    parser.add_argument('--autocorrect', type=int, choices=[0, 1], default=1)
    parser.add_argument('--output-mode', choices=['spotify', 'lastfm-only'], default='spotify', help='Use Spotify matching/playlist creation, or return Last.fm-only ranked suggestions.')
    parser.add_argument('--create-playlist', action='store_true')
    parser.add_argument('--playlist-name')
    parser.add_argument('--playlist-description')
    parser.add_argument('--creds', help='Path to Last.fm credentials JSON file.')
    args = parser.parse_args()

    if args.output_mode == 'lastfm-only' and args.create_playlist:
        raise SystemExit('--create-playlist cannot be used with --output-mode lastfm-only.')

    creds = load_credentials(args.creds)
    api_key = creds['api_key']
    username = getattr(args, 'user', None) or creds.get('username')

    if args.mode == 'artist-rule-c':
        seeds, ranked = build_from_artist_top_tracks(args.artist, api_key=api_key, seed_count=args.seed_count, similar_per_seed=args.similar_per_seed, root_artist=args.artist, autocorrect=args.autocorrect)
        summary = {'mode': args.mode, 'seed_artist': args.artist, 'seed_tracks': seeds}
        default_name = f'Last.fm Rule C — {args.artist}'
        default_description = f'Built from {args.artist} top tracks expanded through Last.fm similar tracks.'
    elif args.mode == 'recent-tracks':
        if not username:
            raise SystemExit('Missing Last.fm username. Pass --user or set LASTFM_USERNAME / credentials file username.')
        seeds, ranked = build_from_recent_tracks(username, api_key=api_key, recent_count=args.recent_count, similar_per_seed=args.similar_per_seed, autocorrect=args.autocorrect)
        summary = {'mode': args.mode, 'user': username, 'seed_tracks': seeds}
        default_name = f'Last.fm Recent Blend — {username}'
        default_description = 'Built from recent Last.fm scrobbles expanded through Last.fm similar tracks.'
    else:
        if not username:
            raise SystemExit('Missing Last.fm username. Pass --user or set LASTFM_USERNAME / credentials file username.')
        seeds, ranked = build_from_top_artists(username, api_key=api_key, period=args.period, artist_count=args.artist_count, seed_count_per_artist=args.seed_count_per_artist, similar_per_seed=args.similar_per_seed, autocorrect=args.autocorrect)
        summary = {'mode': args.mode, 'user': username, 'period': args.period, 'seed_tracks': seeds[:50]}
        default_name = f'Last.fm Top Artists Blend — {username} — {args.period}'
        default_description = f'Built from top Last.fm artists for {args.period}, expanded through similar tracks.'

    candidates = ranked[: max(args.final_limit * 3, args.final_limit)]

    if args.output_mode == 'lastfm-only':
        output = {
            **summary,
            'output_mode': args.output_mode,
            'candidate_count_considered': len(candidates),
            'suggestion_count': min(len(ranked), args.final_limit),
            'suggestions': ranked[: args.final_limit],
        }
    else:
        matched, uris, unmatched = match_candidates_on_spotify(candidates, final_limit=args.final_limit, market=args.market)
        output = {
            **summary,
            'output_mode': args.output_mode,
            'candidate_count_considered': len(candidates),
            'matched_count': len(matched),
            'matched_tracks': matched,
            'unmatched_tracks': unmatched,
        }
        if args.create_playlist:
            playlist = maybe_create_playlist(args.playlist_name or default_name, args.playlist_description or default_description, uris)
            output['playlist'] = playlist

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
