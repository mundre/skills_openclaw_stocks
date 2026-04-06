# NBA Today Pulse Tool Notes

Version: `1.0.10`

This public bundle returns timezone-aware NBA daily status, compact same-day stats, dedicated pregame/live/post views, and independent injury reports through one bundled command wrapper. The `1.0.10` release keeps the compact day/live output and incorporates the newer NBA_TR live boxscore participant tracking and postgame rendering updates.

## Runtime Entry

Production paths should inject `--tz` whenever timezone is known.

```bash
python3 {baseDir}/tools/nba_today_command.py --command "<raw request>" --tz "<resolved timezone>"
```

## Environment Variables

No credentials are required. The public bundle only uses public sports data and does not require API keys, tokens, cookies, or secrets.

Optional timezone environment variables:

- `OPENCLAW_USER_TIMEZONE`
- `OPENCLAW_TIMEZONE`
- `USER_TIMEZONE`
- `TZ`

Notes:

- any valid timezone variable is sufficient
- if the request already includes a timezone or city, that takes priority
- if no timezone can be resolved from the request or runtime inputs, the runtime should ask once for a city or IANA timezone
- when timezone is already known, the production path should still inject it explicitly through `--tz`
- the public bundle keeps cache behavior in memory only and does not expose cache-specific environment variables

## Example Commands

```bash
python3 {baseDir}/tools/nba_today_command.py --command "Show today's NBA games" --tz Asia/Shanghai
python3 {baseDir}/tools/nba_today_command.py --command "Show today's NBA stats" --tz Asia/Shanghai
python3 {baseDir}/tools/nba_today_command.py --command "Who scored the most today?" --tz Asia/Shanghai
python3 {baseDir}/tools/nba_today_command.py --command "Preview tomorrow's Celtics vs Hornets game" --tz Asia/Shanghai
python3 {baseDir}/tools/nba_today_command.py --command "Show today's Lakers live game flow" --tz Asia/Shanghai
python3 {baseDir}/tools/nba_today_command.py --command "Recap today's Knicks vs Thunder game" --tz Asia/Shanghai
python3 {baseDir}/tools/nba_today_command.py --command "Show tomorrow's Pistons injury report" --tz Asia/Shanghai
python3 {baseDir}/tools/nba_today_command.py --command "今日NBA赛况" --tz Asia/Shanghai
python3 {baseDir}/tools/nba_today_command.py --command "明天NBA赛况" --tz America/Los_Angeles
python3 {baseDir}/tools/nba_today_command.py --command "今天比赛谁得分最高" --tz Asia/Shanghai
```

## Semantic Contract

- `today` means the requestor's local calendar date, not ESPN's default league date
- relative dates such as `today / tomorrow / 今天 / 明天 / 今日 / 明日` are resolved in the requestor timezone
- if the request already contains relative-date semantics, the runtime must not inject a conflicting external `--date`
- `day` returns a mixed-status `dayView` with compact live cards (≤3 player lines per team, no team-total row, no duplicate play line) and compact final-game cards by default
- `stats_day` returns compact cards for top scorer, top rebounder, top assists, most threes, double/triple doubles, and largest margin
- `pregame`, `live`, and `post` return fixed phase-specific product shapes
- `live` key-player section shows at most 3 players per team; each line uses compact PTS/REB/AST/STL/BLK + shooting format without MIN or season-average repetition
- `live` may update the displayed main score and game clock from bundled `nba_live` data when ESPN is behind
- `post` prioritizes compact key performances, play-by-play-backed flow summaries, and compact team comparison over raw stat dumps
- `injury` is an independent route and keeps fact and analysis layers separate
- Chinese team display can reflect locale-aware mappings inside the tool chain; English display remains canonical
- player names must remain grounded in current roster or actual game-participant data
- if data is incomplete, the runtime should degrade gracefully and not invent missing facts
- `stats_day` is day-level only and does not act as a season leaderboard
- never compute the scoreboard from `FG`, `3PT`, `FT`, or partial player-point totals
- the public bundle must not add betting advice or generic web-search supplementation

## Data Access

- ESPN public JSON scoreboards, summaries, rosters, schedules, injuries, and team statistics
- NBA.com public stats and live JSON endpoints for structured fallback behavior
- Official NBA injury report listing and report PDFs for supported injury-report queries

These outbound HTTP requests and remote PDF reads are part of the normal product behavior for supported NBA queries. They are not generic browsing and do not require credentials.
