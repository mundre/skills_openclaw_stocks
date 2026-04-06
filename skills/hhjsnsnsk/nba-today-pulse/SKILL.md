---
name: nba-today-pulse
description: Timezone-aware NBA daily intelligence using bundled public ESPN/NBA fetchers plus official NBA injury-report PDFs, with compact day view, same-day stats, phase-specific game routes, play-by-play-driven recaps, and compact key-player cards with direct tool-output delivery.
user-invocable: true
metadata: {"openclaw":{"skillKey":"nba-today-pulse","requires":{"bins":["python3"]}}}
---

# NBA Today Pulse v10

Version: `1.0.10`

Get a compact mixed-status NBA day view, same-day stat leaders, dedicated pregame/live/post reports, and independent injury reports in one skill. This public `1.0.10` bundle keeps the compact day/live cards and carries forward the NBA_TR live boxscore participant tracking, the new `activeParticipants` handoff into live injury rendering, and the postgame auto-render routing updates.

Do not invent scores, injuries, lineups, player stats, matchup reasons, or turning-point narratives that are not supported by the bundled tool output.

## Single Execution Command

Production paths must resolve timezone first and inject `--tz` explicitly.

If the user message already includes a timezone or city:

```bash
python3 {baseDir}/tools/nba_today_command.py --command "<raw request>" --tz "<resolved timezone>"
```

If the user message does not include a timezone but the runtime already knows the user's timezone preference:

```bash
python3 {baseDir}/tools/nba_today_command.py --command "<raw request>" --tz "<resolved timezone>"
```

Only the single branch that asks the user for timezone is allowed to omit `--tz`.

Relative-date requests must stay grounded in the same injected timezone:

```bash
python3 {baseDir}/tools/nba_today_command.py --command "今日NBA赛况" --tz "Asia/Shanghai"
python3 {baseDir}/tools/nba_today_command.py --command "明天NBA赛况" --tz "America/Los_Angeles"
python3 {baseDir}/tools/nba_today_command.py --command "今天比赛谁得分最高" --tz "Asia/Shanghai"
```

## Intent Mapping

- `day`: today's or tomorrow's NBA slate, daily status, all games, mixed-status day view
- `stats_day`: today's NBA stats, who scored the most today, best performance today, rebounds leader, assists leader, most threes, largest margin
- `pregame`: preview, pregame, prediction, matchup preview, all-games preview, multi-matchup preview
- `live`: live game, in-game direction, current momentum, current game flow
- `post`: recap, review, postgame, what happened in the game
- `injury`: injury report, team injuries, matchup injury report

Injury requests take priority over preview phrasing. Explicit preview phrasing takes priority over generic analysis wording.

## Follow-up Refresh Handling

- If the previous turn only asked the user for timezone and the next reply is just a city or IANA timezone, continue the same NBA request silently
- If the user says `更新`, `刷新`, `再看一下`, or `比分不对` while the conversation is already about one NBA matchup, rerun the same request silently and return only the latest tool output
- Refresh follow-ups must not add commentary, score explanations, or rewritten summaries

## Fixed Output Shapes

- `stats_day`: Best Performance → Top Scorer → Top Rebounder → Top Assists → Most Threes → Double/Triple Doubles → Largest Margin → Summary
- `pregame`: Game Info → Lineups & Key Players → Injuries → Team Form → Prediction Analysis → Summary
- `live`: Game Info → Lineups & Key Players → Injuries → Live Momentum → Team Comparison → Key Player Stats (3 players per team, compact PTS/REB/AST/STL/BLK + shooting) → Play Digest → Summary
- `post`: Game Info → Starting Lineups → Result & Flow Summary → Key Performances → Team Comparison → Injuries → Turning Point → Summary
- `day`: grouped cards ordered by `Live → Final → Upcoming`; live cards show at most 3 compact player lines per team, without team-total rows or duplicate play lines; final cards stay compact
- `injury`: Fact Layer → Analysis Layer

## Timezone Behavior

- First use any explicit timezone or city in the user message
- Otherwise use a valid timezone input supplied by the runtime and inject it through `--tz`
- If no timezone can be resolved, ask once for a city or IANA timezone and stop there
- If the request already carries relative-date semantics, do not invent a conflicting external `--date`
- Never explain internal runtime provenance or inspect memory files

## Parameter Mapping Examples

- `今日NBA赛况，按上海时区` -> `--tz Asia/Shanghai`
- `今天比赛谁得分最高，按上海时区` -> `--tz Asia/Shanghai`
- `明天NBA赛况，按洛杉矶时区` -> `--tz America/Los_Angeles`
- `Show today's NBA games in America/Los_Angeles` -> `--tz America/Los_Angeles`
- runtime-known timezone, no explicit timezone in the message -> `--tz <resolved timezone>`

## Data Access Behavior

This skill makes outbound HTTP requests through bundled providers to fetch public ESPN and NBA data. For supported injury-report requests it also downloads and parses official NBA injury-report PDFs, which means the runtime processes remote PDF content as part of normal product behavior. This is declared scope, not generic browsing, and it must not be replaced with freeform web search or unrelated host inspection.

## Output Rules

- Run only the bundled `nba_today_command.py` entrypoint
- Do not switch scripts, reconstruct parameters, or retry alternate command formats
- On success, return the tool output directly
- Prefer compact cards and concise sections; `day` and `live` should stay readable without raw stat dumps or repeated season-average lines
- For live requests, trust the explicit scoreboard returned by the bundled tool chain; the runtime may refresh it from `nba_live` play-by-play or boxscore before rendering
- For postgame requests, trust the bundled play-by-play-driven recap and turning-point text instead of rewriting it in the skill layer
- On user-fixable issues such as missing timezone or no matching game, return the final short tool result directly
- Keep `AWAY @ HOME` ordering unchanged
- Match the user's language; Chinese output should prefer Chinese team names and controlled player-name mappings
- Chinese team-name display may vary by locale-aware mapping inside the tool chain, while English display remains canonical and non-regionalized
- Keep relative dates such as `today / tomorrow / 今天 / 明天 / 今日 / 明日` grounded in the resolved requestor timezone
- Do not compute or guess the game score from `FG`, `3PT`, `FT`, player-point subtotals, or team-total snippets

## Forbidden Behaviors

- Do not expose process narration, tool exploration, file inspection, or command retry chatter
- Do not mention internal memory files, host runtime details, or prior-record reasoning
- Do not use web search or generic browsing to patch missing facts unless the user explicitly asks for online verification
- Do not inspect unrelated host files or request secrets, API keys, tokens, or credentials
- Do not add betting advice, odds, spreads, totals, or gambling language
- Do not add future speculation, unverified lineup guesses, or unsupported injury assumptions
- Do not rewrite the tool result into a different structure
