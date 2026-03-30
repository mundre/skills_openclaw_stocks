---
name: bumblebee
description: "Two modes: (1) BUMBLEBEE — Communicate through music by playing exact lyric lines on Spotify, like Bumblebee from Transformers speaking through radio snippets. (2) R2-DJ — Contextual music curation that reads the moment (time, mood, recent listening, activity) and builds the perfect queue. Use when: expressing something through song lyrics, playing music for the current vibe, curating a playlist for a mood/activity, responding to 'play music' or 'what should I listen to', DJ requests, or any music playback control (play, pause, skip, volume, search). Triggers: 'say it with music', 'bumblebee mode', 'play that lyric', 'speak through songs', 'play music', 'play the right music', 'DJ mode', 'what should I listen to', 'set the vibe', or any Spotify playback request. Requires: Spotify Premium with active device, OAuth tokens in projects/spotify/."
---

# Bumblebee + R2-DJ — Talk Through Music & Curate the Vibe 🐝🎧

Two sides of the same coin:
- **Bumblebee** speaks through exact lyric clips — chaining song lines into sentences
- **R2-DJ** reads the room and curates the perfect queue for the moment

## Prerequisites

- Spotify Premium account with an active device (phone, desktop, speaker)
- OAuth tokens at `projects/spotify/tokens.json` (auto-refreshes)
- Spotify app credentials at `projects/spotify/.env` (`SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`)
- **Your own lyric index** — see `scripts/build-lyric-index.md` for how to build one. Lyrics are copyrighted and not included in this skill. You'll need to curate your own `lyric-index.json` and optionally `lyrics-db.json`.

## Core Workflow

### 1. Find the Right Lyrics

Search the lyric index for lines that literally say what you mean:

```bash
node scripts/lyric-engine.js search "phrase to find"
```

Returns matching lines with IDs, timestamps, and scores. **Use literal phrases** — search for what the lyrics actually say, not metaphors.

### 2. Play Lyric Clips

Send specific lyric lines to the active Spotify device:

```bash
node scripts/lyric-engine.js speak "artist::track::lineNum" "artist::track::lineNum"
```

Each clip plays its exact timestamp window, then advances to the next with a brief pause. Chain multiple IDs to build a sentence.

### 3. Check Devices

```bash
node scripts/bumblebee.js devices
```

Verify an active Spotify device exists before attempting playback. 🟢 = active.

## Composing Messages

**Think literally.** Search for words/phrases the lyrics actually contain:

```bash
# Find lyrics about being present
node lyric-engine.js search "aquí me tienes"
# Find lyrics about commitment  
node lyric-engine.js search "no te fallaré"
# Find lyrics about love
node lyric-engine.js search "lo que más quiero"
```

Then chain the best line IDs into a `speak` command. Typical message = 2-4 clips.

## Managing the Library

- **Add a song:** `node scripts/lyric-engine.js index "Artist" "Track"`
- **Batch-index starter library:** `node scripts/lyric-engine.js batch-index`
- **View all indexed songs:** `node scripts/lyric-engine.js catalog`
- **Song details and moods:** See [references/song-library.md](references/song-library.md)

## Intent-Based Playback (Legacy)

The original `bumblebee.js` supports mood-based playback from a curated clips database:

```bash
node scripts/bumblebee.js play greeting
node scripts/bumblebee.js say greeting motivation celebration
```

Available intents: greeting, motivation, freedom, empathy, celebration, goodnight, warning, pride, lets_go.

## Tips — Bumblebee

- **Always check devices first** — "No active device" is the most common failure
- **Bilingual library** — index has English and Spanish songs; search in either language
- **Clip duration** = gap between lyric timestamps (typically 3-8 seconds per line)
- **Present the lyrics** — after playing, show the user what was said with translations if needed
- **Build emotional arcs** — start soft, build to the punchline (e.g., setup → commitment → crescendo)

---

# R2-DJ — Contextual Music Curation 🎧🤖

An AI DJ that reads the moment and plays the right music. Knows 5 frequency profiles that map to different states of mind and times of day.

## Frequency Profiles

| Frequency | Vibe | Time | Key Artists |
|---|---|---|---|
| **Architect** | Solo builder, focus, flow state | 9AM-5PM, 10PM-2AM | C418, Jarre, Tangerine Dream, Vangelis |
| **Dreamer** | Synthwave, retro-futurism, night cruising | 8PM-3AM | Kavinsky, M83, Com Truise, Perturbator |
| **Mexican Soul** | Heritage, roots, identity | Anytime | José José, Vicente, Natalia, Café Tacvba |
| **Seeker** | Post-midnight processing, healing | 11PM-6AM | Solfeggio, 528Hz, 639Hz, ambient |
| **Cinephile** | Film scores, thinking, reflecting | 7PM-2AM | Jóhannsson, Zimmer, Richter, Greenwood |

## Core Commands

### Auto-Vibe (Let R2 Pick)

```bash
node scripts/r2-dj.js vibe
```

Reads time of day + recent listening → detects the right frequency → builds and plays a queue. Outputs a JSON summary for the agent's reply.

### Force a Frequency

```bash
node scripts/r2-dj.js vibe --frequency seeker
node scripts/r2-dj.js vibe --frequency architect --device iPhone
```

### Playback Control

```bash
node scripts/r2-dj.js now        # What's playing
node scripts/r2-dj.js pause      # Pause
node scripts/r2-dj.js skip       # Next track
node scripts/r2-dj.js volume 50  # Set volume
node scripts/r2-dj.js play "Nils Frahm Says"        # Search + play
node scripts/r2-dj.js play spotify:track:xxx         # Play URI directly
node scripts/r2-dj.js search "ambient electronic"    # Search tracks
```

### Context & Info

```bash
node scripts/r2-dj.js context      # Time, recent plays, detected frequency, devices
node scripts/r2-dj.js frequencies   # List all frequency profiles
node scripts/r2-dj.js history       # Recent listening history
node scripts/r2-dj.js devices       # Spotify devices
```

## How the Agent Should Use R2-DJ

1. **"Play music" / "what should I listen to"** → `r2-dj.js vibe` (auto-detect)
2. **"I need to focus"** → `r2-dj.js vibe --frequency architect`
3. **"Something for the drive"** → `r2-dj.js vibe --frequency dreamer`
4. **"Wind me down"** → `r2-dj.js vibe --frequency seeker`
5. **"Play [specific song]"** → `r2-dj.js play "song name"`
6. **Mood descriptions** → Pick the closest frequency, then `vibe --frequency <key>`

## Tips — R2-DJ

- Auto-vibe uses time + recent listening to pick the frequency — it's smart, trust it
- The agent can also manually build curated queues with inline Spotify API calls for special moments
- Frequencies aren't rigid — if recent listening suggests Architect at midnight, that wins over time-based detection
- **Present the tracklist** after playing — show what you queued and why
- JSON summary after `---JSON_SUMMARY---` is for agent parsing, not user display
