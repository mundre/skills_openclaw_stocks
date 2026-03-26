---
name: lastfm-spotify-playlists
description: Build Spotify playlists from Last.fm scrobble history and Last.fm artist or track similarity instead of Spotify recommendations. Use when creating playlists from a user's top artists, top tracks, recent scrobbles, manually supplied seed artists, or manually supplied seed tracks; when Last.fm should provide the discovery logic and Spotify should only handle search, matching, and playlist creation.
---

# Last.fm Spotify Playlists

Use Last.fm as the recommendation engine and Spotify as the playback / playlist layer.

## Core rule

Prefer Last.fm similarity for discovery.

- Use `artist.getsimilar` when the user wants artist-adjacent discovery.
- Use `track.getsimilar` when the user wants song-level discovery.
- Use Spotify only to:
  - authenticate the user
  - search for playable matches
  - create playlists
  - add matched items to playlists

## Resources

- `scripts/lastfm_common.py` — shared credential loading and API calls.
- `scripts/lastfm_recent.py` — fetch recent tracks, top artists, and top tracks.
- `scripts/lastfm_similar.py` — fetch similar artists or similar tracks.
- `scripts/lastfm_track_playlist_candidates.py` — build merged Rule C track candidates from an artist's top tracks.
- `scripts/lastfm_spotify_playlist_pipeline.py` — one-command pipeline for Last.fm ranking, optional Spotify matching, and optional playlist creation.
- `scripts/spotify_common.py` — Spotify auth, search, playlist creation, and playlist item insertion.
- `scripts/spotify_auth.py` — one-shot Spotify OAuth helper.
- `scripts/spotify_search.py` — inspect Spotify track matches.
- `scripts/spotify_playlist.py` — create playlists from explicit Spotify URIs.
- `references/credentials.md` — local credential file formats and auth notes.

## Workflow

1. Confirm credentials exist. Read `references/credentials.md` if setup details are needed.
2. Decide the recommendation mode:
   - **Artist mode** for similar artists
   - **Track mode / Rule C** for similar tracks
3. Pull Last.fm seeds from one of:
   - user's top artists / top tracks
   - user's recent scrobbles
   - user-supplied artists or tracks
4. Expand on Last.fm first.
5. Merge and rank candidates before touching Spotify.
6. If the user wants suggestions only, stop after merged candidate ranking and return Last.fm-native results.
7. Authenticate Spotify only if playlist output is requested.
8. Search Spotify for exact artist + track matches when possible.
9. Create the playlist on Spotify.
10. Add tracks through the playlist `/items` endpoint, not the older `/tracks` write endpoint.
11. Report unmatched candidates explicitly instead of silently dropping them.

## Recommended patterns

### A. Similar artists from a seed artist

Use when the user wants nearby artists, not necessarily exact song similarity.

```bash
python skills/lastfm-spotify-playlists/scripts/lastfm_similar.py artist "Placebo" --limit 20
```

Then inspect Spotify manually or with `spotify_search.py`.

### B. Similar tracks from one seed track

Use when the user gives a specific song.

```bash
python skills/lastfm-spotify-playlists/scripts/lastfm_similar.py track "Placebo" "Every You Every Me" --limit 20
```

### C. Rule C playlist candidates from one artist's top tracks

Use when the user wants the most Last.fm-native discovery flow.

```bash
python skills/lastfm-spotify-playlists/scripts/lastfm_track_playlist_candidates.py "Placebo" --seed-count 5 --similar-per-seed 10 --final-limit 20
```

This:
- fetches the artist's top tracks from Last.fm
- expands each track via `track.getsimilar`
- merges duplicate candidates across seed tracks
- ranks results by source count and total similarity score

### D. Suggestion-only mode with no Spotify writes

Use when the user wants a ranked suggestion list but does not want a Spotify playlist created.

```bash
python skills/lastfm-spotify-playlists/scripts/lastfm_spotify_playlist_pipeline.py recent-tracks --output-mode lastfm-only --final-limit 20
```

## Spotify auth

Run this before playlist creation if the token is missing or outdated:

```bash
python skills/lastfm-spotify-playlists/scripts/spotify_auth.py --scopes playlist-modify-private playlist-modify-public playlist-read-private user-read-private
```

## Playlist creation notes

- Create playlists through `/me/playlists`.
- Add tracks through `/playlists/{playlist_id}/items`.
- Do not rely on the older `/tracks` write endpoint in this environment.
- Expect some Last.fm candidates to fail Spotify matching; report them.

## Good outputs

Return:
- seed artist or tracks used
- candidate tracks considered
- ranked Last.fm suggestions when using suggestion-only mode
- matched Spotify tracks when using Spotify mode
- unmatched candidates
- final playlist URL when creation succeeds

## Scope of this skill

Include:
- Last.fm seed collection
- Last.fm similarity expansion
- merged candidate ranking
- optional suggestion-only output
- Spotify track matching
- Spotify playlist creation and population
- one-command artist / recent / top-artist blend pipelines

Exclude from the packaged skill:
- real API keys
- real secrets
- real token files
- user-specific exported candidate JSON unless the user explicitly wants example artifacts kept

## Publishing readiness (new)

- This skill is designed for publishing in controlled environments. Before publish, verify:
  - No embedded credentials or secrets anywhere in code or docs.
  - All credential references point to environment variables or external credential files.
  - Scripts have clear inputs/outputs and error cases documented.
  - Licensing and attribution are in place where applicable.
  - Version tag and a changelog placeholder exist.

## Quickstart for publishing (example)

1) Publish scaffold: ensure SKILL.md, script docs, and credentials guide exist.
2) Run a dry-run of key workflows to verify outputs:
   - artist-rule-c with a seed artist
   - recent-tracks with a user
3) If all good, attach a publish note with a changelog entry and version.

## Credentials and secrets (new)

- Last.fm: API key, shared secret, username
  - Environment: LASTFM_API_KEY, LASTFM_SHARED_SECRET, LASTFM_USERNAME
  - File: ~/.openclaw/lastfm-credentials.json
- Spotify: Client ID, Client Secret, Redirect URI
  - Environment: SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI
  - File: ~/.openclaw/spotify-credentials.json

## Troubleshooting (new)

- Credential not found: verify environment or credentials file path
- Last.fm API rate limits: consider increasing limit or adding backoff
- Spotify auth/token refresh failures: ensure refresh_token exists; run spotify_auth.py to re-authorize

