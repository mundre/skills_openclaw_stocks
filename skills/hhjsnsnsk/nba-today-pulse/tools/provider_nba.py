#!/usr/bin/env python3
"""Direct NBA.com provider helpers for NBA_TR."""

from __future__ import annotations

import json
import os
import socket
import ssl
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from cache_store import cached_json_fetch
from nba_common import NBAReportError
from nba_teams import canonicalize_team_abbr

DEFAULT_STATS_BASE_URL = "https://stats.nba.com/stats"
DEFAULT_LIVE_BASE_URL = "https://cdn.nba.com/static/json/liveData"
USER_AGENT = "nba-tr-openclaw/2.0"
DEFAULT_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": USER_AGENT,
    "Referer": "https://www.nba.com/",
    "Origin": "https://www.nba.com",
    "x-nba-stats-origin": "stats",
    "x-nba-stats-token": "true",
}


def resolve_stats_base_url(base_url: str | None = None) -> str:
    return (base_url or os.environ.get("NBA_TR_NBA_STATS_BASE_URL") or DEFAULT_STATS_BASE_URL).rstrip("/")


def resolve_live_base_url(base_url: str | None = None) -> str:
    return (base_url or os.environ.get("NBA_TR_NBA_BASE_URL") or DEFAULT_LIVE_BASE_URL).rstrip("/")


def _request_json(url: str, timeout_seconds: int) -> dict[str, Any]:
    request = urllib.request.Request(url, headers=DEFAULT_HEADERS, method="GET")
    context = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=timeout_seconds, context=context) as response:
        return json.loads(response.read().decode("utf-8"))


def _fetch_json(url: str, timeout_seconds: int = 20) -> dict[str, Any]:
    try:
        return _request_json(url, timeout_seconds)
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")
        raise NBAReportError(body_text or f"HTTP {exc.code}", status=exc.code, kind="nba_http_error") from exc
    except (urllib.error.URLError, TimeoutError, socket.timeout, ssl.SSLError, json.JSONDecodeError) as exc:
        raise NBAReportError(f"无法连接 NBA 数据源: {exc}", kind="nba_connection_failed") from exc


def _build_url(base_url: str, endpoint: str, params: dict[str, str]) -> str:
    query = urllib.parse.urlencode(params)
    return f"{base_url}/{endpoint}?{query}" if query else f"{base_url}/{endpoint}"


def fetch_scoreboard(date_text: str, *, base_url: str | None = None, timeout_seconds: int = 20) -> dict[str, Any]:
    stats_base = resolve_stats_base_url(base_url)
    month, day, year = date_text[5:7], date_text[8:10], date_text[0:4]
    url = _build_url(
        stats_base,
        "scoreboardv2",
        {
            "GameDate": f"{month}/{day}/{year}",
            "LeagueID": "00",
            "DayOffset": "0",
        },
    )
    payload, freshness = cached_json_fetch(
        namespace="nba:scoreboard",
        key=date_text,
        ttl_seconds=120,
        fetcher=lambda: _fetch_json(url, timeout_seconds),
    )
    return {
        "baseUrl": stats_base,
        "endpoint": "scoreboardv2",
        "request": {"date": date_text},
        "data": payload,
        "dataFreshness": freshness,
    }


def fetch_team_roster(
    team_id: str,
    *,
    season: str | None = None,
    base_url: str | None = None,
    timeout_seconds: int = 20,
) -> dict[str, Any]:
    stats_base = resolve_stats_base_url(base_url)
    target_season = season or os.environ.get("NBA_TR_NBA_SEASON", "2025-26")
    url = _build_url(
        stats_base,
        "commonteamroster",
        {
            "TeamID": team_id,
            "Season": target_season,
            "LeagueID": "00",
        },
    )
    payload, freshness = cached_json_fetch(
        namespace="nba:team_roster",
        key=f"{team_id}:{target_season}",
        ttl_seconds=3600,
        fetcher=lambda: _fetch_json(url, timeout_seconds),
    )
    return {
        "baseUrl": stats_base,
        "endpoint": "commonteamroster",
        "request": {"team": team_id, "season": target_season},
        "data": payload,
        "dataFreshness": freshness,
    }


def fetch_team_player_averages(
    team_id: str,
    *,
    season: str | None = None,
    base_url: str | None = None,
    timeout_seconds: int = 20,
) -> dict[str, Any]:
    stats_base = resolve_stats_base_url(base_url)
    target_season = season or os.environ.get("NBA_TR_NBA_SEASON", "2025-26")
    url = _build_url(
        stats_base,
        "leaguedashplayerstats",
        {
            "College": "",
            "Conference": "",
            "Country": "",
            "DateFrom": "",
            "DateTo": "",
            "Division": "",
            "DraftPick": "",
            "DraftYear": "",
            "GameScope": "",
            "GameSegment": "",
            "Height": "",
            "LastNGames": "0",
            "LeagueID": "00",
            "Location": "",
            "MeasureType": "Base",
            "Month": "0",
            "OpponentTeamID": "0",
            "Outcome": "",
            "PORound": "0",
            "PaceAdjust": "N",
            "PerMode": "PerGame",
            "Period": "0",
            "PlayerExperience": "",
            "PlayerPosition": "",
            "PlusMinus": "N",
            "Rank": "N",
            "Season": target_season,
            "SeasonSegment": "",
            "SeasonType": "Regular Season",
            "ShotClockRange": "",
            "StarterBench": "",
            "TeamID": team_id,
            "TwoWay": "0",
            "VsConference": "",
            "VsDivision": "",
            "Weight": "",
        },
    )
    payload, freshness = cached_json_fetch(
        namespace="nba:team_player_averages",
        key=f"{team_id}:{target_season}",
        ttl_seconds=1800,
        fetcher=lambda: _fetch_json(url, timeout_seconds),
    )
    return {
        "baseUrl": stats_base,
        "endpoint": "leaguedashplayerstats",
        "request": {"team": team_id, "season": target_season},
        "data": payload,
        "dataFreshness": freshness,
    }


def fetch_live_boxscore(game_id: str, *, base_url: str | None = None, timeout_seconds: int = 20) -> dict[str, Any]:
    live_base = resolve_live_base_url(base_url)
    url = f"{live_base}/boxscore/boxscore_{game_id}.json"
    payload, freshness = cached_json_fetch(
        namespace="nba:boxscore",
        key=game_id,
        ttl_seconds=30,
        fetcher=lambda: _fetch_json(url, timeout_seconds),
    )
    return {
        "baseUrl": live_base,
        "endpoint": "boxscore",
        "request": {"gameId": game_id},
        "data": payload,
        "dataFreshness": freshness,
    }


def fetch_play_by_play(game_id: str, *, base_url: str | None = None, timeout_seconds: int = 20) -> dict[str, Any]:
    live_base = resolve_live_base_url(base_url)
    url = f"{live_base}/playbyplay/playbyplay_{game_id}.json"
    payload, freshness = cached_json_fetch(
        namespace="nba:play_by_play",
        key=game_id,
        ttl_seconds=15,
        fetcher=lambda: _fetch_json(url, timeout_seconds),
    )
    return {
        "baseUrl": live_base,
        "endpoint": "playbyplay",
        "request": {"gameId": game_id},
        "data": payload,
        "dataFreshness": freshness,
    }


def extract_scoreboard_games(payload: dict[str, Any]) -> list[dict[str, Any]]:
    games: list[dict[str, Any]] = []
    result_sets = payload.get("resultSets") or []
    rows_by_name = {entry.get("name"): entry for entry in result_sets if isinstance(entry, dict)}
    headers = rows_by_name.get("GameHeader", {}).get("headers") or []
    rows = rows_by_name.get("GameHeader", {}).get("rowSet") or []
    for row in rows:
        record = {headers[index]: row[index] for index in range(min(len(headers), len(row)))}
        home_abbr = canonicalize_team_abbr(record.get("HOME_TEAM_ABBREVIATION"))
        away_abbr = canonicalize_team_abbr(record.get("VISITOR_TEAM_ABBREVIATION"))
        games.append(
            {
                "gameId": str(record.get("GAME_ID") or ""),
                "gameCode": str(record.get("GAMECODE") or ""),
                "homeAbbr": home_abbr,
                "awayAbbr": away_abbr,
                "statusText": str(record.get("GAME_STATUS_TEXT") or ""),
            }
        )
    if games:
        return games

    scoreboard = payload.get("scoreboard") or {}
    for game in scoreboard.get("games") or []:
        home_team = game.get("homeTeam") or {}
        away_team = game.get("awayTeam") or {}
        games.append(
            {
                "gameId": str(game.get("gameId") or ""),
                "gameCode": str(game.get("gameCode") or ""),
                "homeAbbr": canonicalize_team_abbr(home_team.get("teamTricode") or home_team.get("teamCode")),
                "awayAbbr": canonicalize_team_abbr(away_team.get("teamTricode") or away_team.get("teamCode")),
                "statusText": str((game.get("gameStatusText") or game.get("gameStatus")) or ""),
            }
        )
    return games


def find_game_id_by_matchup(
    date_text: str,
    away_abbr: str,
    home_abbr: str,
    *,
    base_url: str | None = None,
    timeout_seconds: int = 20,
) -> str | None:
    payload = fetch_scoreboard(date_text, base_url=base_url, timeout_seconds=timeout_seconds)["data"]
    for game in extract_scoreboard_games(payload):
        if game["awayAbbr"] == canonicalize_team_abbr(away_abbr) and game["homeAbbr"] == canonicalize_team_abbr(home_abbr):
            return game["gameId"] or None
    return None


def extract_roster_players(payload: dict[str, Any]) -> list[dict[str, str]]:
    players: list[dict[str, str]] = []
    result_sets = payload.get("resultSets") or []
    row_set = None
    headers = None
    for entry in result_sets:
        if isinstance(entry, dict) and (entry.get("name") == "CommonTeamRoster" or not headers):
            headers = entry.get("headers") or headers
            row_set = entry.get("rowSet") or row_set
    if headers and row_set:
        for row in row_set:
            record = {headers[index]: row[index] for index in range(min(len(headers), len(row)))}
            display_name = str(record.get("PLAYER") or "").strip()
            if display_name:
                players.append(
                    {
                        "id": str(record.get("PLAYER_ID") or ""),
                        "displayName": display_name,
                        "shortName": display_name,
                        "jersey": str(record.get("NUM") or ""),
                        "position": str(record.get("POSITION") or ""),
                    }
                )
        return players

    game = payload.get("game") or {}
    for side_key in ("homeTeam", "awayTeam"):
        for player in ((game.get(side_key) or {}).get("players") or []):
            name = player.get("name") or player.get("familyName")
            if name:
                players.append(
                    {
                        "id": str(player.get("personId") or ""),
                        "displayName": str(name),
                        "shortName": str(name),
                        "jersey": str(player.get("jerseyNum") or ""),
                        "position": str(player.get("position") or ""),
                    }
                )
    return players


def extract_play_actions(payload: dict[str, Any]) -> list[dict[str, Any]]:
    game = payload.get("game") or {}
    actions = game.get("actions") or payload.get("actions") or []
    results: list[dict[str, Any]] = []
    for item in actions:
        player_name = item.get("playerName") or item.get("personName") or ""
        results.append(
            {
                "actionNumber": item.get("actionNumber"),
                "clock": str((item.get("clock") or "")).removeprefix("PT"),
                "period": item.get("period") or item.get("periodNumber"),
                "description": item.get("description") or item.get("actionType") or "",
                "homeScore": item.get("scoreHome"),
                "awayScore": item.get("scoreAway"),
                "teamId": str(item.get("teamId") or ""),
                "playerName": str(player_name),
            }
        )
    return results


def _float_or_none(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def extract_team_player_averages(payload: dict[str, Any]) -> dict[str, dict[str, float | None]]:
    result_sets = payload.get("resultSets") or payload.get("resultSet") or []
    if isinstance(result_sets, dict):
        result_sets = [result_sets]
    if not result_sets:
        return {}
    first = next((entry for entry in result_sets if isinstance(entry, dict)), None)
    if not first:
        return {}
    headers = first.get("headers") or []
    rows = first.get("rowSet") or []
    results: dict[str, dict[str, float | None]] = {}
    for row in rows:
        record = {headers[index]: row[index] for index in range(min(len(headers), len(row)))}
        name = str(record.get("PLAYER_NAME") or record.get("PLAYER") or "").strip()
        if not name:
            continue
        results[name] = {
            "MIN": _float_or_none(record.get("MIN")),
            "PTS": _float_or_none(record.get("PTS")),
            "REB": _float_or_none(record.get("REB")),
            "AST": _float_or_none(record.get("AST")),
            "STL": _float_or_none(record.get("STL")),
            "BLK": _float_or_none(record.get("BLK")),
            "TOV": _float_or_none(record.get("TOV")),
            "FG_PCT": _float_or_none(record.get("FG_PCT")),
            "FG3_PCT": _float_or_none(record.get("FG3_PCT")),
            "FT_PCT": _float_or_none(record.get("FT_PCT")),
            "GP": _float_or_none(record.get("GP")),
        }
    return results


def extract_boxscore_players(payload: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    game = payload.get("game") or {}
    result: dict[str, list[dict[str, Any]]] = {}
    for side_key in ("awayTeam", "homeTeam"):
        side = game.get(side_key) or {}
        abbr = canonicalize_team_abbr(side.get("teamTricode") or side.get("teamCode"))
        team_players: list[dict[str, Any]] = []
        for player in side.get("players") or []:
            name = player.get("name") or player.get("familyName")
            if not name:
                continue
            stats_raw = player.get("statistics") or {}
            team_players.append(
                {
                    "displayName": str(name),
                    "starter": bool(player.get("starter")),
                    "stats": {
                        "points": stats_raw.get("points") or player.get("points"),
                        "rebounds": stats_raw.get("reboundsTotal") or player.get("rebounds"),
                        "assists": stats_raw.get("assists") or player.get("assists"),
                        "minutes": stats_raw.get("minutesCalculated") or stats_raw.get("minutes") or player.get("minutes"),
                    },
                }
            )
        if abbr:
            result[abbr] = team_players
    return result


def extract_live_boxscore_snapshot(payload: dict[str, Any]) -> dict[str, Any]:
    """从 NBA Live boxscore payload 中提取实时比赛快照（比分、节次、时钟）。"""
    game = payload.get("game") or {}

    away_team = game.get("awayTeam") or {}
    home_team = game.get("homeTeam") or {}

    away_score = away_team.get("score")
    home_score = home_team.get("score")

    # 解析比赛时钟：NBA Live 格式通常是 "PT08M47.00S"
    raw_clock = game.get("gameClock") or game.get("gameTimeQtr") or ""
    display_clock = ""
    if raw_clock:
        # 去掉 PT 前缀和 S 后缀，转成 MM:SS 格式
        import re as _re
        m = _re.match(r"PT(?P<min>\d+)M(?P<sec>[\d.]+)S", raw_clock)
        if m:
            minutes = int(m.group("min"))
            seconds = int(float(m.group("sec")))
            display_clock = f"{minutes}:{seconds:02d}"
        else:
            display_clock = raw_clock

    return {
        "awayScore": away_score,
        "homeScore": home_score,
        "awayScoreSource": "explicit" if away_score is not None else "none",
        "homeScoreSource": "explicit" if home_score is not None else "none",
        "period": game.get("period"),
        "displayClock": display_clock,
    }

