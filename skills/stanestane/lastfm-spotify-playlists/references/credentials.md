# Credentials

Keep secrets out of the skill package itself. Store them locally on the machine running the skill.

## Last.fm

Preferred local file:

`~/.openclaw/lastfm-credentials.json`

Example:

```json
{
  "api_key": "YOUR_LASTFM_API_KEY",
  "shared_secret": "YOUR_LASTFM_SHARED_SECRET",
  "username": "YOUR_LASTFM_USERNAME"
}
```

Environment variables also work:

- `LASTFM_API_KEY`
- `LASTFM_SHARED_SECRET`
- `LASTFM_USERNAME`

## Spotify

Preferred local file:

`~/.openclaw/spotify-credentials.json`

Example:

```json
{
  "client_id": "YOUR_SPOTIFY_CLIENT_ID",
  "client_secret": "YOUR_SPOTIFY_CLIENT_SECRET",
  "redirect_uri": "http://127.0.0.1:8888/callback"
}
```

Token cache:

`~/.openclaw/spotify-token.json`

Run Spotify auth before playlist creation if the token is missing or stale:

```bash
python skills/lastfm-spotify-playlists/scripts/spotify_auth.py
```

Current practical note:
- playlist creation works through `/me/playlists`
- playlist item insertion should use `/playlists/{playlist_id}/items`
- older `/tracks` write operations were unreliable in this environment
