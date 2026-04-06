#!/usr/bin/env python3
"""Shared context builders for scene-specific NBA_TR scripts."""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timedelta
from typing import Any

from entity_guard import blocked_names, extract_primary_name, fallback_matchup_text, filter_headlines, filter_named_lines, normalize_player_name, verified_player_names
from nba_game_full_stats import build_full_stats
from nba_head_to_head import build_head_to_head_context
from nba_advanced_report import build_analysis, render_analysis_block
from nba_common import NBAReportError
from nba_player_names import display_player_name, localize_player_line, localize_player_list
from nba_play_digest import build_play_digest
from nba_team_form_snapshot import build_team_form_context
from nba_teams import canonicalize_team_abbr, extract_team_from_text, extract_teams_from_text, format_matchup_display, infer_zh_locale, normalize_team_input, provider_team_id, team_display_name
from nba_today_report import I18N, build_report_payload, format_counts_summary, load_candidate_events, render_compact_player_stat_line, render_compact_team_totals_line, render_detail_blocks, render_team_lines
from nba_today_report import render_full_stats_player_line, render_full_stats_team_line
from provider_nba_injuries import resolve_team_injury_sources
from provider_espn import extract_roster_players as extract_espn_roster_players
from provider_espn import fetch_scoreboard, fetch_team_roster, fetch_team_schedule
from provider_nba import (
    extract_boxscore_players,
    extract_live_boxscore_snapshot,
    extract_team_player_averages,
    extract_play_actions,
    extract_roster_players as extract_nba_roster_players,
    extract_scoreboard_games,
    fetch_team_player_averages,
    find_game_id_by_matchup,
    fetch_live_boxscore,
    fetch_play_by_play,
    fetch_scoreboard as fetch_nba_scoreboard,
    fetch_team_roster as fetch_nba_team_roster,
)
from timezone_resolver import extract_timezone_hint, resolve_timezone

LANG_EN_PATTERNS = [r"\bin english\b", r"\benglish\b", r"\blang\s*=\s*en\b", r"\ben\b", r"\b英文\b"]
LANG_ZH_PATTERNS = [r"\bin chinese\b", r"\bchinese\b", r"\blang\s*=\s*zh\b", r"\bzh\b", r"\b中文\b"]
DATE_PATTERN = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")
PREGAME_PATTERNS = [
    r"比赛前瞻",
    r"前瞻预测",
    r"比赛预测",
    r"对阵预测",
    r"赛前情报",
    r"赛前信息",
    r"赛前预测",
    r"赛前分析",
    r"赛前",
    r"前瞻",
    r"预测",
    r"对局分析",
    r"看好谁",
    r"谁更占优",
    r"\bpreview\b",
    r"\bpregame\b",
    r"\bpre-game\b",
    r"\bgame preview\b",
    r"\bpreview prediction\b",
    r"\bmatch prediction\b",
    r"\bpredict(?:ion)?\b",
    r"\bmatchup analysis\b",
    r"\bwho has the edge\b",
    r"\banaly[sz]e\b",
]
LIVE_PATTERNS = [r"赛中", r"正在进行", r"走势", r"实时", r"\blive\b", r"\bin-game\b", r"\bmomentum\b"]
POST_PATTERNS = [r"复盘", r"回顾", r"赛后", r"\brecap\b", r"\bpostgame\b", r"\breview\b"]
INJURY_PATTERNS = [r"伤病报告", r"伤病名单", r"伤病", r"伤停", r"\binjury report\b", r"\binjuries\b", r"\bavailability\b"]
STATS_DAY_PATTERNS = [
    r"今天比赛谁得分最高",
    r"比赛谁得分最高",
    r"今天谁得分最高",
    r"谁得分最高",
    r"今日得分王",
    r"得分王",
    r"最高得分",
    r"今天谁篮板最多",
    r"谁篮板最多",
    r"今日篮板王",
    r"今天谁助攻最多",
    r"谁助攻最多",
    r"今日助攻王",
    r"今天三分最多的是谁",
    r"三分最多的是谁",
    r"今日三分王",
    r"今天有谁拿到三双",
    r"有谁拿到三双",
    r"今天有谁拿到两双",
    r"有谁拿到两双",
    r"今日最佳表现",
    r"最佳表现",
    r"今天最大分差是哪场",
    r"最大分差是哪场",
    r"今天\s*NBA\s*统计",
    r"今日\s*NBA\s*统计",
    r"\bNBA\s*统计\b",
    r"今日统计",
    r"\b统计\b",
    r"\btoday'?s nba stats\b",
    r"\btoday stats\b",
    r"\btoday top scorer\b",
    r"\btop scorer\b",
    r"\bwho scored the most today\b",
    r"\bwho scored the most\b",
    r"\bwho had the most rebounds today\b",
    r"\bwho had the most rebounds\b",
    r"\bwho had the most assists today\b",
    r"\bwho had the most assists\b",
    r"\bmost threes today\b",
    r"\bmost threes\b",
    r"\bbest performance today\b",
    r"\bbest performance\b",
    r"\blargest margin today\b",
    r"\blargest margin\b",
]
ALL_GAMES_PATTERNS = [r"所有比赛", r"全部比赛", r"全部对局", r"\ball games\b", r"\bevery game\b", r"\ball matchups\b"]
MULTI_MATCHUP_SPLIT_PATTERNS = [r"和", r"以及", r"、", r",", r"，", r"\+", r"\band\b"]
RELATIVE_DATE_PATTERNS = [
    (r"后天", 2),
    (r"明天|明日|\btomorrow\b", 1),
    (r"今天|今日|\btoday\b", 0),
    (r"昨天|昨日|\byesterday\b", -1),
]


def contains_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def detect_lang(command: str) -> str:
    lowered = command.strip()
    if contains_any(lowered, LANG_EN_PATTERNS):
        return "en"
    if contains_any(lowered, LANG_ZH_PATTERNS):
        return "zh"
    zh_chars = len(re.findall(r"[\u4e00-\u9fff]", lowered))
    en_words = len(re.findall(r"\b[a-zA-Z][a-zA-Z'-]*\b", lowered))
    return "zh" if zh_chars > en_words else "en"


def detect_analysis_mode(command: str) -> str:
    lowered = command.strip()
    if contains_any(lowered, PREGAME_PATTERNS):
        return "pregame"
    if contains_any(lowered, LIVE_PATTERNS):
        return "live"
    if contains_any(lowered, POST_PATTERNS):
        return "post"
    return "auto"


def detect_intent(command: str) -> str:
    lowered = command.strip()
    if contains_any(lowered, INJURY_PATTERNS):
        return "injury"
    if contains_any(lowered, STATS_DAY_PATTERNS):
        return "stats_day"
    if contains_any(lowered, POST_PATTERNS):
        return "post"
    if contains_any(lowered, LIVE_PATTERNS):
        return "live"
    if contains_any(lowered, PREGAME_PATTERNS):
        return "pregame"
    return "day"


def _contains_multi_separator(text: str) -> bool:
    return contains_any(text, MULTI_MATCHUP_SPLIT_PATTERNS)


def _all_games_requested(text: str) -> bool:
    return contains_any(text, ALL_GAMES_PATTERNS)


def extract_matchups_from_text(text: str | None) -> list[dict[str, str]]:
    teams = extract_teams_from_text(text or "")
    if len(teams) < 2:
        return []
    if len(teams) == 2:
        return [{"team": teams[0], "opponent": teams[1]}]
    if len(teams) % 2 != 0 or not _contains_multi_separator(text or ""):
        return []
    return [{"team": teams[index], "opponent": teams[index + 1]} for index in range(0, len(teams), 2)]


def detect_scope(command: str, intent: str, matchups: list[dict[str, str]], teams: list[str]) -> str:
    if intent == "stats_day":
        return "multi_all"
    if intent == "pregame":
        if _all_games_requested(command):
            return "multi_all"
        if len(matchups) > 1:
            return "multi_explicit"
    return "single"


def _reference_now(tz: str | None) -> datetime:
    resolved_tz = resolve_timezone(tz)
    env_override = (os.environ.get("NBA_TR_NOW_ISO") or "").strip()
    if env_override:
        parsed = datetime.fromisoformat(env_override.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=resolved_tz.tzinfo)
        return parsed.astimezone(resolved_tz.tzinfo)
    return datetime.now(resolved_tz.tzinfo)


def detect_requested_date(command: str, tz: str | None) -> str | None:
    date_match = DATE_PATTERN.search(command)
    if date_match:
        return date_match.group(1)
    for pattern, offset in RELATIVE_DATE_PATTERNS:
        if re.search(pattern, command, flags=re.IGNORECASE):
            now = _reference_now(tz)
            return (now.date() + timedelta(days=offset)).isoformat()
    return None


def command_has_explicit_date(command: str) -> bool:
    if DATE_PATTERN.search(command):
        return True
    return any(re.search(pattern, command, flags=re.IGNORECASE) for pattern, _ in RELATIVE_DATE_PATTERNS)


def command_options(command: str, tz_hint: str | None = None) -> dict[str, Any]:
    timezone_hint = extract_timezone_hint(tz_hint) if tz_hint else extract_timezone_hint(command)
    tz_name = timezone_hint.name if timezone_hint else None
    lang = detect_lang(command)
    teams = extract_teams_from_text(command)
    matchups = extract_matchups_from_text(command)
    intent = detect_intent(command)
    return {
        "lang": lang,
        "analysis_mode": detect_analysis_mode(command),
        "intent": intent,
        "date": detect_requested_date(command, tz_name),
        "team": teams[0] if teams else extract_team_from_text(command),
        "opponent": teams[1] if len(teams) > 1 else None,
        "teams": teams,
        "matchups": matchups,
        "scope": detect_scope(command, intent, matchups, teams),
        "tz": tz_name,
        "zh_locale": infer_zh_locale(lang=lang, tz_name=tz_name, command_text=command),
    }


def _normalize_injury_status(value: str | None) -> str:
    return str(value or "").strip().casefold()


def _pregame_injury_priority(
    item: dict[str, Any],
    *,
    leader_names: set[str],
    key_player_names: set[str],
    season_average_names: set[str],
) -> tuple[int, int, int, str]:
    player_name = extract_primary_name(str(item.get("playerName") or ""))
    status = _normalize_injury_status(item.get("status"))
    status_rank = {
        "out": 0,
        "doubtful": 1,
        "questionable": 2,
        "day-to-day": 3,
        "probable": 4,
    }.get(status, 5)
    player_rank = 3
    if player_name in leader_names:
        player_rank = 0
    elif player_name in key_player_names:
        player_rank = 1
    elif player_name in season_average_names:
        player_rank = 2
    return (status_rank, player_rank, 0, player_name.casefold())


def _format_injury_item(item: dict[str, Any]) -> str:
    return " - ".join(
        part
        for part in (
            item.get("playerName"),
            item.get("status"),
            item.get("detail"),
        )
        if part
    )


def _select_pregame_injury_lines(game: dict[str, Any], team_abbr: str, *, limit: int | None = None) -> list[str]:
    items = ((game.get("injuryItems") or {}).get(team_abbr) or [])
    if not items:
        return []
    leader_names = {extract_primary_name(line) for line in (game.get("leaders", {}).get(team_abbr) or [])}
    key_player_names = {extract_primary_name(line) for line in (game.get("keyPlayers", {}).get(team_abbr) or [])}
    season_average_names = set(((game.get("gameContext") or {}).get("seasonAverages") or {}).get(team_abbr, {}).keys())
    ordered = sorted(
        items,
        key=lambda item: _pregame_injury_priority(
            item,
            leader_names=leader_names,
            key_player_names=key_player_names,
            season_average_names=season_average_names,
        ),
    )
    lines: list[str] = []
    seen: set[str] = set()
    for item in ordered:
        line = _format_injury_item(item)
        if not line or line in seen:
            continue
        seen.add(line)
        lines.append(line)
    return lines if limit is None else lines[:limit]


def _report_args(*, tz: str | None, date_text: str | None, team: str | None, lang: str, zh_locale: str | None = None) -> argparse.Namespace:
    return argparse.Namespace(
        tz=tz,
        date=date_text,
        team=team,
        view="game" if team else "day",
        lang=lang,
        zh_locale=zh_locale,
        format="json",
        base_url=None,
    )


def build_scene_report(*, tz: str | None, date_text: str | None, team: str | None, lang: str, zh_locale: str | None = None) -> dict[str, Any]:
    return build_report_payload(_report_args(tz=tz, date_text=date_text, team=team, lang=lang, zh_locale=zh_locale))


def _target_date(date_text: str | None, tz: str | None) -> datetime.date:
    if date_text:
        return datetime.strptime(date_text, "%Y-%m-%d").date()
    return _reference_now(tz).date()


def _event_local_date(event: dict[str, Any], tz: str | None) -> datetime.date | None:
    resolved_tz = resolve_timezone(tz)
    competition = (event.get("competitions") or [{}])[0]
    raw_date = competition.get("date") or event.get("date")
    if not raw_date:
        return None
    return datetime.fromisoformat(str(raw_date).replace("Z", "+00:00")).astimezone(resolved_tz.tzinfo).date()


def _event_abbrs(event: dict[str, Any]) -> set[str]:
    competition = (event.get("competitions") or [{}])[0]
    competitors = competition.get("competitors") or []
    abbrs = {
        canonicalize_team_abbr(str(((item.get("team") or {}).get("abbreviation")) or "").upper())
        for item in competitors
    }
    short_name = str(event.get("shortName") or "")
    for abbr in extract_teams_from_text(short_name):
        abbrs.add(abbr)
    return {abbr for abbr in abbrs if abbr}


def _event_matches(event: dict[str, Any], team_abbr: str, opponent_abbr: str | None = None) -> bool:
    abbrs = _event_abbrs(event)
    if team_abbr not in abbrs:
        return False
    if opponent_abbr and opponent_abbr not in abbrs:
        return False
    return True


def resolve_requested_game(
    *,
    tz: str | None,
    date_text: str | None,
    team: str,
    opponent: str | None = None,
    base_url: str | None = None,
) -> dict[str, Any]:
    team_abbr = normalize_team_input(team)
    opponent_abbr = normalize_team_input(opponent) if opponent else None
    if not team_abbr:
        raise NBAReportError("未能识别球队缩写。", kind="invalid_arguments")
    if date_text:
        target_date = _target_date(date_text, tz)
        for event in load_candidate_events(target_date, resolve_timezone(tz), base_url):
            if _event_matches(event, team_abbr, opponent_abbr):
                return {
                    "eventId": str(event.get("id") or ""),
                    "source": "espn_scoreboard",
                    "event": event,
                    "requestedDate": target_date.isoformat(),
                }
        raise NBAReportError("当前条件下未找到对应比赛。", kind="not_found")

    if opponent_abbr:
        espn_team_id = provider_team_id(team_abbr, "espn")
        schedule_payload = {}
        if espn_team_id:
            try:
                schedule_payload = fetch_team_schedule(espn_team_id, base_url=base_url)["data"]
            except NBAReportError:
                schedule_payload = {}
        events = [event for event in (schedule_payload.get("events") or []) if _event_matches(event, team_abbr, opponent_abbr)]
        today = _target_date(None, tz)
        future_events = [
            event for event in events if (_event_local_date(event, tz) is not None and _event_local_date(event, tz) >= today)
        ]
        candidate_pool = sorted(future_events, key=lambda item: str(item.get("date") or ""))
        source = "espn_team_schedule"
        if not candidate_pool:
            candidate_pool = sorted(events, key=lambda item: str(item.get("date") or ""), reverse=True)
        if candidate_pool:
            event = candidate_pool[0]
            local_date = _event_local_date(event, tz)
            return {
                "eventId": str(event.get("id") or ""),
                "source": source,
                "event": event,
                "requestedDate": local_date.isoformat() if local_date else None,
            }
    located = locate_game(tz=tz, date_text=date_text, team=team_abbr, base_url=base_url)
    located["requestedDate"] = _target_date(date_text, tz).isoformat()
    return located


def locate_game(*, tz: str | None, date_text: str | None, team: str, base_url: str | None = None) -> dict[str, Any]:
    team_abbr = normalize_team_input(team)
    if not team_abbr:
        raise NBAReportError("未能识别球队缩写。", kind="invalid_arguments")

    target_date = _target_date(date_text, tz)
    resolved_tz = resolve_timezone(tz)
    for offset in (-1, 0, 1):
        provider_date = (target_date + timedelta(days=offset)).strftime("%Y%m%d")
        try:
            payload = fetch_scoreboard(provider_date, base_url=base_url)["data"]
        except NBAReportError:
            payload = {}
        for event in payload.get("events") or []:
            competition = (event.get("competitions") or [{}])[0]
            event_date = competition.get("date") or event.get("date")
            if not event_date:
                continue
            local_date = datetime.fromisoformat(event_date.replace("Z", "+00:00")).astimezone(resolved_tz.tzinfo).date()
            if local_date != target_date:
                continue
            competitors = competition.get("competitors") or []
            abbrs = {
                canonicalize_team_abbr(str(((item.get("team") or {}).get("abbreviation")) or "").upper())
                for item in competitors
            }
            if team_abbr in abbrs:
                return {
                    "eventId": str(event.get("id") or ""),
                    "source": "espn_scoreboard",
                    "event": event,
                }

    espn_team_id = provider_team_id(team_abbr, "espn")
    if espn_team_id:
        try:
            schedule_payload = fetch_team_schedule(espn_team_id, base_url=base_url)["data"]
            for event in schedule_payload.get("events") or []:
                raw_date = str(event.get("date") or "")
                if raw_date:
                    local_date = datetime.fromisoformat(raw_date.replace("Z", "+00:00")).astimezone(resolved_tz.tzinfo).date()
                    if local_date == target_date:
                        return {
                            "eventId": str(event.get("id") or ""),
                            "source": "espn_team_schedule",
                            "event": event,
                        }
        except NBAReportError:
            pass

    try:
        nba_payload = fetch_nba_scoreboard(target_date.isoformat())["data"]
        for game in extract_scoreboard_games(nba_payload):
            if team_abbr in {game.get("awayAbbr"), game.get("homeAbbr")}:
                return {
                    "eventId": str(game.get("gameId") or ""),
                    "source": "nba_scoreboard",
                    "event": game,
                }
    except NBAReportError:
        pass

    raise NBAReportError("当前条件下未找到对应比赛。", kind="not_found")


def fetch_team_roster_snapshot(team_abbr: str) -> dict[str, Any]:
    espn_team_id = provider_team_id(team_abbr, "espn")
    nba_team_id = provider_team_id(team_abbr, "nba")
    if espn_team_id:
        try:
            payload = fetch_team_roster(espn_team_id)
            players = extract_espn_roster_players(payload["data"])
            if players:
                return {
                    "team": team_abbr,
                    "players": players,
                    "source": "espn",
                    "dataFreshness": payload.get("dataFreshness", "fresh"),
                }
        except NBAReportError:
            pass
    if nba_team_id:
        try:
            payload = fetch_nba_team_roster(nba_team_id)
            players = extract_nba_roster_players(payload["data"])
            return {
                "team": team_abbr,
                "players": players,
                "source": "nba",
                "dataFreshness": payload.get("dataFreshness", "fresh"),
            }
        except NBAReportError:
            pass
    return {
        "team": team_abbr,
        "players": [],
        "source": "unavailable",
        "dataFreshness": "fresh",
    }


def fetch_game_rosters(game: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        game["away"]["abbr"]: fetch_team_roster_snapshot(game["away"]["abbr"]),
        game["home"]["abbr"]: fetch_team_roster_snapshot(game["home"]["abbr"]),
    }


def apply_roster_guard(game: dict[str, Any], roster_snapshots: dict[str, dict[str, Any]], *, lang: str) -> dict[str, Any]:
    rosters_by_abbr = {abbr: snapshot.get("players") or [] for abbr, snapshot in roster_snapshots.items()}
    allowed_names = verified_player_names(game, rosters_by_abbr)
    original_candidate_lines: list[str] = []
    for group in (game.get("leaders") or {}, game.get("starters") or {}, game.get("keyPlayers") or {}):
        for lines in group.values():
            original_candidate_lines.extend(lines or [])
    blocked = blocked_names(original_candidate_lines, allowed_names)

    game["leaders"] = {
        abbr: filter_named_lines(lines or [], allowed_names)
        for abbr, lines in (game.get("leaders") or {}).items()
    }
    game["starters"] = {
        abbr: filter_named_lines(lines or [], allowed_names)
        for abbr, lines in (game.get("starters") or {}).items()
    }
    game["keyPlayers"] = {
        abbr: filter_named_lines(lines or [], allowed_names)
        for abbr, lines in (game.get("keyPlayers") or {}).items()
    }
    game["headlines"] = filter_headlines(game.get("headlines") or [], blocked)
    if allowed_names:
        allowed_normalized = {normalize_player_name(name) for name in allowed_names if name}
        filtered_injury_items: dict[str, list[dict[str, Any]]] = {}
        filtered_injuries: dict[str, list[str]] = {}
        for abbr, items in (game.get("injuryItems") or {}).items():
            kept_items: list[dict[str, Any]] = []
            for item in items or []:
                player_name = extract_primary_name(str(item.get("playerName") or ""))
                if player_name and normalize_player_name(player_name) in allowed_normalized:
                    kept_items.append(item)
            filtered_injury_items[abbr] = kept_items
            filtered_injuries[abbr] = [_format_injury_item(item) for item in kept_items if _format_injury_item(item)]
        game["injuryItems"] = filtered_injury_items
        game["injuries"] = filtered_injuries
    game["startersConfirmed"] = bool(game["starters"].get(game["away"]["abbr"])) and bool(game["starters"].get(game["home"]["abbr"]))
    game["verifiedPlayers"] = sorted(allowed_names)
    game["rosters"] = roster_snapshots
    if blocked:
        game["forceFallbackMatchup"] = True
    game["fallbackMatchup"] = fallback_matchup_text(game, lang=lang)
    return game


def _player_line_from_boxscore(player: dict[str, Any]) -> str:
    name = player.get("displayName") or ""
    stats = player.get("stats") or {}
    parts = [name]
    if stats.get("points") is not None:
        parts.append(f"{stats['points']} PTS")
    if stats.get("rebounds") is not None:
        parts.append(f"{stats['rebounds']} REB")
    if stats.get("assists") is not None:
        parts.append(f"{stats['assists']} AST")
    return " | ".join(str(part) for part in parts if part)


def _sync_live_scoreboard(
    game: dict[str, Any],
    *,
    away_score: Any = None,
    home_score: Any = None,
    period: Any = None,
    display_clock: Any = None,
) -> None:
    if away_score not in (None, ""):
        game["away"]["score"] = str(away_score)
    if home_score not in (None, ""):
        game["home"]["score"] = str(home_score)
    if period not in (None, ""):
        game["period"] = period
    if display_clock not in (None, ""):
        game["displayClock"] = str(display_clock)


def _sync_full_stats_scoreboard(game: dict[str, Any]) -> None:
    if game.get("statusState") not in {"in", "post"}:
        return
    full_stats = game.get("fullStats") or {}
    teams = full_stats.get("teams") or {}
    for side in ("away", "home"):
        team = game.get(side) or {}
        abbr = team.get("abbr")
        score = team.get("score")
        if not abbr or score in (None, ""):
            continue
        stats = teams.get(abbr)
        if isinstance(stats, dict):
            stats["PTS"] = str(score)


def augment_game_with_nba_live(game: dict[str, Any], *, requested_date: str) -> dict[str, Any]:
    try:
        game_id = find_game_id_by_matchup(requested_date, game["away"]["abbr"], game["home"]["abbr"])
    except NBAReportError:
        return {"source": None, "dataFreshness": "fresh", "fallbackLevel": "none"}
    if not game_id:
        return {"source": None, "dataFreshness": "fresh", "fallbackLevel": "none"}
    game["nbaGameId"] = str(game_id)
    meta = {"source": None, "dataFreshness": "fresh", "fallbackLevel": "none"}
    should_refresh_live_timeline = game.get("statusState") == "in" or not game.get("playTimeline")
    if should_refresh_live_timeline:
        try:
            payload = fetch_play_by_play(game_id)
            actions = extract_play_actions(payload["data"])
            if actions:
                game["playTimeline"] = [
                    {
                        "id": str(item.get("actionNumber") or ""),
                        "text": item.get("description") or "",
                        "shortDescription": item.get("description") or "",
                        "period": item.get("period"),
                        "clock": item.get("clock"),
                        "homeScore": item.get("homeScore"),
                        "awayScore": item.get("awayScore"),
                        "scoreValue": None,
                        "scoringPlay": True if item.get("homeScore") or item.get("awayScore") else False,
                        "teamId": item.get("teamId") or "",
                        "playerName": item.get("playerName") or "",
                    }
                    for item in actions
                ]
                game["recentPlays"] = [item["text"] for item in game["playTimeline"][-4:] if item.get("text")]
                latest_with_score = next(
                    (
                        item
                        for item in reversed(actions)
                        if item.get("homeScore") not in (None, "") or item.get("awayScore") not in (None, "")
                    ),
                    actions[-1],
                )
                _sync_live_scoreboard(
                    game,
                    away_score=latest_with_score.get("awayScore"),
                    home_score=latest_with_score.get("homeScore"),
                    period=latest_with_score.get("period"),
                    display_clock=latest_with_score.get("clock"),
                )
                meta = {"source": "nba_live", "dataFreshness": payload.get("dataFreshness", "fresh"), "fallbackLevel": "nba_live"}
        except NBAReportError:
            pass
    should_refresh_live_boxscore = (
        game.get("statusState") == "in"
        or not any((game.get("keyPlayers") or {}).values())
        or not any((game.get("starters") or {}).values())
        or game["away"].get("score") in (None, "")
        or game["home"].get("score") in (None, "")
    )
    if should_refresh_live_boxscore:
        try:
            payload = fetch_live_boxscore(game_id)
            game["nbaLiveBoxscore"] = payload["data"]
            live_snapshot = extract_live_boxscore_snapshot(payload["data"])
            away_score = live_snapshot.get("awayScore")
            home_score = live_snapshot.get("homeScore")
            away_score_source = live_snapshot.get("awayScoreSource")
            home_score_source = live_snapshot.get("homeScoreSource")
            _sync_live_scoreboard(
                game,
                away_score=away_score if away_score_source == "explicit" or game["away"].get("score") in (None, "") else None,
                home_score=home_score if home_score_source == "explicit" or game["home"].get("score") in (None, "") else None,
                period=live_snapshot.get("period"),
                display_clock=live_snapshot.get("displayClock"),
            )
            players_by_team = extract_boxscore_players(payload["data"])
            active_participants: list[str] = []
            for abbr, players in players_by_team.items():
                if not game["starters"].get(abbr):
                    starters = [player["displayName"] for player in players if player.get("starter")]
                    game["starters"][abbr] = starters[:5]
                if not game["keyPlayers"].get(abbr):
                    lines = [_player_line_from_boxscore(player) for player in players]
                    game["keyPlayers"][abbr] = [line for line in lines if line][:3]
                # 收集实际上场球员（有 minutes 记录的）
                for player in players:
                    minutes_val = (player.get("stats") or {}).get("minutes")
                    has_minutes = False
                    if minutes_val:
                        # minutesCalculated 格式可能是 "PT12M34.00S" 或数字
                        if isinstance(minutes_val, str):
                            has_minutes = minutes_val not in ("", "PT00M00.00S", "PT0M0.00S")
                        else:
                            has_minutes = float(minutes_val) > 0
                    if has_minutes and player.get("displayName"):
                        active_participants.append(player["displayName"])
            # live boxscore 补充后重新计算 startersConfirmed
            if bool(game["starters"].get(game["away"]["abbr"])) and bool(game["starters"].get(game["home"]["abbr"])):
                game["startersConfirmed"] = True
            game["activeParticipants"] = active_participants
            meta = {"source": "nba_live", "dataFreshness": payload.get("dataFreshness", "fresh"), "fallbackLevel": "nba_live"}
        except NBAReportError:
            pass
    return meta


def _team_player_averages(team_abbr: str) -> dict[str, dict[str, float | None]]:
    nba_team_id = provider_team_id(team_abbr, "nba")
    if not nba_team_id:
        return {}
    try:
        payload = fetch_team_player_averages(nba_team_id)["data"]
    except NBAReportError:
        return {}
    return extract_team_player_averages(payload)


def attach_season_averages(game: dict[str, Any]) -> None:
    full_stats = game.get("fullStats") or {}
    if not full_stats.get("available"):
        return
    players_by_team = full_stats.get("players") or {}
    for abbr in (game["away"]["abbr"], game["home"]["abbr"]):
        averages = _team_player_averages(abbr)
        if not averages:
            continue
        normalized_lookup = {name.casefold(): stats for name, stats in averages.items()}
        for player in players_by_team.get(abbr) or []:
            name = str(player.get("playerName") or "").strip()
            if not name:
                continue
            average_stats = normalized_lookup.get(name.casefold())
            if average_stats:
                player["seasonAverages"] = average_stats


def _collect_context_candidate_names(game: dict[str, Any], team_abbr: str) -> list[str]:
    candidates: list[str] = []
    for group_name in ("leaders", "keyPlayers", "starters"):
        for line in (game.get(group_name, {}).get(team_abbr) or []):
            name = extract_primary_name(line)
            if name and name not in candidates:
                candidates.append(name)
    return candidates[:6]


def build_season_averages_context(game: dict[str, Any]) -> dict[str, dict[str, Any]]:
    by_team: dict[str, dict[str, Any]] = {}
    for abbr in (game["away"]["abbr"], game["home"]["abbr"]):
        averages = _team_player_averages(abbr)
        players: dict[str, Any] = {}
        for name in _collect_context_candidate_names(game, abbr):
            stats = averages.get(name)
            if stats:
                players[name] = stats
        by_team[abbr] = players
    return by_team


def build_game_context(game: dict[str, Any]) -> dict[str, Any]:
    info = {
        "eventId": game["eventId"],
        "matchup": {
            "text": f"{game['away']['abbr']} @ {game['home']['abbr']}",
            "away": game["away"],
            "home": game["home"],
        },
        "requestedDate": game.get("requestedDate"),
        "statusState": game.get("statusState"),
        "statusDetail": game.get("statusDetail"),
        "startTimeLocal": game.get("startTimeLocal"),
        "venue": game.get("venue"),
        "broadcasts": game.get("broadcasts") or [],
        "standings": {
            game["away"]["abbr"]: (game.get("context", {}).get("teamForm", {}).get(game["away"]["abbr"], {}).get("standings") or {}),
            game["home"]["abbr"]: (game.get("context", {}).get("teamForm", {}).get(game["home"]["abbr"], {}).get("standings") or {}),
        },
    }
    lineups = {
        "startersConfirmed": bool(game.get("startersConfirmed")),
        "starters": game.get("starters") or {},
        "keyPlayers": game.get("keyPlayers") or {},
        "leaders": game.get("leaders") or {},
        "verifiedPlayers": game.get("verifiedPlayers") or [],
        "activeParticipants": game.get("activeParticipants") or [],
    }
    injuries = {
        "items": game.get("injuryItems") or {},
        "byTeam": game.get("injuries") or {},
        "meta": game.get("injuryMeta") or {},
    }
    live_state = {
        "displayClock": game.get("displayClock"),
        "period": game.get("period"),
        "recentPlays": game.get("recentPlays") or [],
        "playTimeline": game.get("playTimeline") or [],
        "winProbabilityTimeline": game.get("winProbabilityTimeline") or [],
    }
    return {
        "info": info,
        "lineups": lineups,
        "injuries": injuries,
        "teamForm": (game.get("context") or {}).get("teamForm") or {},
        "headToHead": (game.get("context") or {}).get("headToHead") or {},
        "seasonAverages": build_season_averages_context(game),
        "liveState": live_state,
        "fullStats": game.get("fullStats") or {"available": False, "teams": {}, "players": {}},
    }


def build_pregame_view(game: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
    featured_injuries = {
        game["away"]["abbr"]: _select_pregame_injury_lines(game, game["away"]["abbr"]),
        game["home"]["abbr"]: _select_pregame_injury_lines(game, game["home"]["abbr"]),
    }
    compact_injuries = {
        game["away"]["abbr"]: _select_pregame_injury_lines(game, game["away"]["abbr"], limit=2),
        game["home"]["abbr"]: _select_pregame_injury_lines(game, game["home"]["abbr"], limit=2),
    }
    return {
        "info": game.get("gameContext", {}).get("info") or {},
        "lineups": game.get("gameContext", {}).get("lineups") or {},
        "injuries": {
            **(game.get("gameContext", {}).get("injuries") or {}),
            "featuredByTeam": featured_injuries,
            "compactByTeam": compact_injuries,
        },
        "teamForm": game.get("gameContext", {}).get("teamForm") or {},
        "prediction": {
            "summary": analysis.get("summary") or "",
            "reasons": analysis.get("reasons") or [],
            "trend": analysis.get("trend") or "",
            "keyMatchup": analysis.get("keyMatchup") or "",
        },
        "summary": analysis.get("summary") or "",
    }


def build_live_view(game: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
    game_context = game.get("gameContext", {}) or {}
    lineups = game_context.get("lineups") or {}
    full_stats = game_context.get("fullStats") or {"available": False, "teams": {}, "players": {}}
    matchup = (game_context.get("info") or {}).get("matchup") or {}
    _, coverage = _build_live_player_display(full_stats=full_stats, lineups=lineups, matchup=matchup, limit=5)
    return {
        "info": game_context.get("info") or {},
        "lineups": lineups,
        "injuries": game_context.get("injuries") or {},
        "liveState": game_context.get("liveState") or {},
        "momentum": {
            "trend": analysis.get("trend") or "",
            "reasons": analysis.get("reasons") or [],
        },
        "playerStatsCoverage": coverage,
        "summary": analysis.get("summary") or "",
    }


def build_postgame_view(game: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
    return {
        "info": game.get("gameContext", {}).get("info") or {},
        "lineups": game.get("gameContext", {}).get("lineups") or {},
        "injuries": game.get("gameContext", {}).get("injuries") or {},
        "fullStats": game.get("gameContext", {}).get("fullStats") or {"available": False, "teams": {}, "players": {}},
        "turningPoint": analysis.get("turningPoint") or "",
        "summary": analysis.get("summary") or "",
    }


def _phase_labels(lang: str) -> dict[str, str]:
    if lang == "zh":
        return {
            "live_title": "NBA 单场实时走势",
            "post_title": "NBA 单场赛后复盘",
            "info": "比赛信息",
            "lineups": "阵容与关键球员",
            "starters_section": "首发名单",
            "injuries": "伤病情况",
            "live_flow": "实时走势",
            "post_flow": "比赛结果与走势总结",
            "team_totals": "球队整体数据对比",
            "post_team_totals": "球队整体对比",
            "key_player_lines": "关键球员数据",
            "post_key_players": "关键球员表现",
            "play_digest": "回合摘要",
            "turning_point": "转折点",
            "summary": "总结",
            "starters_pending": "首发尚未公布或当前免费数据源不可确认。",
            "none": "无",
        }
    return {
        "live_title": "NBA Live Game Report",
        "post_title": "NBA Postgame Recap",
        "info": "Game Info",
        "lineups": "Lineups and Key Players",
        "starters_section": "Starting Lineups",
        "injuries": "Injuries",
        "live_flow": "Live Momentum",
        "post_flow": "Game Result and Flow",
        "team_totals": "Team Totals Comparison",
        "post_team_totals": "Team Comparison",
        "key_player_lines": "Key Player Lines",
        "post_key_players": "Key Performances",
        "play_digest": "Play Digest",
        "turning_point": "Turning Point",
        "summary": "Summary",
        "starters_pending": "Starting lineups are not yet confirmed or cannot be confirmed from the free data source.",
        "none": "None",
    }


def _day_labels(lang: str) -> dict[str, str]:
    if lang == "zh":
        return {
            "title": "NBA 综合赛况",
            "view": "综合赛况视图",
            "live_title": "进行中比赛",
            "post_title": "已结束比赛",
            "pre_title": "未开赛比赛",
            "counts": "场次摘要",
            "phase_pregame": "赛前",
            "phase_live": "赛中",
            "phase_post": "赛后",
            "team_form": "球队状态",
            "prediction": "预测摘要",
            "latest_play": "最新回合",
            "turning_point": "转折点",
            "none": "无",
        }
    return {
        "title": "NBA Mixed Status Day View",
        "view": "mixed-status day view",
        "live_title": "Live Games",
        "post_title": "Final Games",
        "pre_title": "Scheduled Games",
        "counts": "Counts",
        "phase_pregame": "Pregame",
        "phase_live": "Live",
        "phase_post": "Postgame",
        "team_form": "Team Form",
        "prediction": "Prediction",
        "latest_play": "Latest Play",
        "turning_point": "Turning Point",
        "none": "None",
    }


def _stats_day_labels(lang: str) -> dict[str, str]:
    if lang == "zh":
        return {
            "title": "NBA 今日统计",
            "view": "当日统计视图",
            "completed_games": "已统计比赛",
            "best_performance": "今日最佳表现",
            "top_scorer": "最高得分",
            "top_rebounder": "最高篮板",
            "top_assists": "最高助攻",
            "top_three": "最高三分",
            "double_triple": "两双 / 三双",
            "largest_margin": "最大分差",
            "no_completed_games": "当前该日期还没有已结束比赛，暂时无法汇总当日统计。",
            "none": "无",
            "double_double": "两双",
            "triple_double": "三双",
            "summary_prefix": "统计摘要",
            "points": "分",
            "rebounds": "板",
            "assists": "助攻",
            "made_threes": "记三分",
            "won_by": "赢",
        }
    return {
        "title": "NBA Daily Stats",
        "view": "day stats view",
        "completed_games": "Completed Games Counted",
        "best_performance": "Best Performance",
        "top_scorer": "Top Scorer",
        "top_rebounder": "Top Rebounder",
        "top_assists": "Top Assists",
        "top_three": "Top Three-Point Shooter",
        "double_triple": "Double-Doubles / Triple-Doubles",
        "largest_margin": "Largest Margin",
        "no_completed_games": "No completed games are available for day-level stats on the requested date yet.",
        "none": "None",
        "double_double": "double-double",
        "triple_double": "triple-double",
        "summary_prefix": "Summary",
        "points": "PTS",
        "rebounds": "REB",
        "assists": "AST",
        "made_threes": "3PM",
        "won_by": "won by",
    }


def _display_team(abbr: str | None, lang: str, zh_locale: str | None = None) -> str:
    return team_display_name(abbr, lang, zh_locale=zh_locale) or (abbr or "")


def _matchup_team_abbrs(matchup: dict[str, Any] | None) -> list[str]:
    if not matchup:
        return []
    abbrs: list[str] = []
    for side in ("away", "home"):
        abbr = canonicalize_team_abbr((matchup.get(side) or {}).get("abbr"))
        if abbr and abbr not in abbrs:
            abbrs.append(abbr)
    return abbrs


def _localize_team_mentions(
    text: str | None,
    *,
    lang: str,
    zh_locale: str | None = None,
    team_abbrs: list[str] | None = None,
) -> str:
    rendered = str(text or "").strip()
    if not rendered:
        return ""
    for abbr in team_abbrs or []:
        canonical = canonicalize_team_abbr(abbr)
        display = _display_team(canonical, lang, zh_locale)
        if not display:
            continue
        rendered = re.sub(rf"(?<![A-Z]){re.escape(canonical)}(?![A-Z])", display, rendered)
        if canonical == "WAS":
            rendered = re.sub(r"(?<![A-Z])WSH(?![A-Z])", display, rendered)
    return rendered


def _ordinal_period(period: Any) -> str:
    try:
        number = int(period)
    except (TypeError, ValueError):
        return str(period or "?")
    if 10 <= number % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    return f"{number}{suffix}"


def _append_unique_line(lines: list[str], text: str | None) -> None:
    normalized = str(text or "").strip()
    if not normalized:
        return
    candidate = f"- {normalized}"
    if lines and lines[-1] == candidate:
        return
    lines.append(candidate)


def _narrative_team_form(team_name: str, recent: str, rest_text: str, lang: str) -> str:
    if lang == "zh":
        return f"{team_name}近况是最近 {recent}，休息天数 {rest_text}。"
    rest_phrase = "rest pending" if rest_text == "Pending" else f"{rest_text} day{'s' if str(rest_text) != '1' else ''} of rest"
    return f"{team_name} come in at {recent} over the last five with {rest_phrase}."


def _narrative_team_totals(team_name: str, compact: str, lang: str) -> str:
    if lang == "zh":
        return f"数据层面，{team_name}是 {compact}。"
    return f"On the numbers, {team_name} finished at {compact}."


def _narrative_key_lines(team_name: str, lines_text: str, lang: str) -> str:
    if lang == "zh":
        return f"{team_name}这边的主要输出来自 {lines_text}。"
    return f"Most of {team_name}'s production came from {lines_text}."


def _narrative_latest_play(play_text: str, lang: str) -> str:
    if not str(play_text or "").strip():
        return ""
    if lang == "zh":
        return f"最新一次明显波动出现在 {play_text}。"
    return f"The latest swing came on {play_text}."


def _narrative_turning_point(turning_point: str, lang: str) -> str:
    value = str(turning_point or "").strip()
    if not value or value in {"无", "None"}:
        return value or ""
    if lang == "zh" and ("，" in value or "。" in value):
        return value if value.endswith("。") else f"{value}。"
    if lang == "en" and (value.startswith("With ") or value.startswith("In ") or value.startswith("The ") or value.endswith(".")):
        return value if value.endswith(".") else f"{value}."
    if lang == "zh":
        return f"比赛的关键片段出现在 {value}。"
    return f"The key stretch turned on {value}."


def _post_reasons_sentence(reasons: list[str], *, lang: str) -> str:
    cleaned = [str(reason or "").strip().rstrip(".。") for reason in reasons if str(reason or "").strip()]
    if not cleaned:
        return ""
    if lang == "zh":
        return f"支撑这场走势的依据包括：{'；'.join(cleaned)}。"
    return f"The supporting evidence included: {'; '.join(cleaned)}."


def _english_reason_fragment(reason: str) -> str:
    value = str(reason or "").strip().rstrip(".")
    if not value:
        return ""
    won_match = re.match(r"^(?P<team>.+?) won by (?P<margin>\d+)(?: points?)?$", value)
    if won_match:
        team = won_match.group("team").strip()
        margin = won_match.group("margin").strip()
        return f"a {margin}-point win for {team}"
    if value.startswith("Decisive stretch:"):
        detail = value.split(":", 1)[1].strip()
        return f"the decisive stretch in {detail}"
    if value.startswith("Lead performer:"):
        detail = value.split(":", 1)[1].strip().replace(" | ", ", ")
        return f"{detail} setting the tone"
    if value.startswith("Rebounding edge:"):
        detail = value.split(":", 1)[1].strip()
        return f"a rebounding edge of {detail}"
    return value[0].lower() + value[1:] if value[:1].isupper() else value


def _narrative_reasons(reasons: list[str], *, lang: str) -> str:
    if not reasons:
        return ""
    if lang == "zh":
        joined = " / ".join(reasons)
        return f"关键依据主要在于 {joined}。"
    english_reasons = [_english_reason_fragment(reason) for reason in reasons if str(reason or "").strip()]
    joined = "; ".join(fragment for fragment in english_reasons if fragment)
    return f"The edge was backed by {joined}."


LEADER_LINE_PATTERN = re.compile(r"^(?P<name>.+?)\s*\((?P<stats>.+)\)$")
LEADER_STAT_PATTERN = re.compile(r"(?P<value>\d+(?:\.\d+)?)\s*(?P<label>PTS|REB|AST)\b", re.IGNORECASE)


def _numeric_value(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return int(number)


def _three_pt_made(value: Any) -> int | None:
    if value is None or value == "":
        return None
    text = str(value).strip()
    if not text:
        return None
    if "-" in text:
        text = text.split("-", 1)[0]
    return _numeric_value(text)


def _leader_stats_from_line(line: str) -> tuple[str, dict[str, int]]:
    match = LEADER_LINE_PATTERN.match(str(line or "").strip())
    if not match:
        return "", {}
    stats_map: dict[str, int] = {}
    for stat_match in LEADER_STAT_PATTERN.finditer(match.group("stats")):
        key = str(stat_match.group("label") or "").upper()
        value = _numeric_value(stat_match.group("value"))
        if value is not None:
            stats_map[key] = value
    return str(match.group("name") or "").strip(), stats_map


def _format_stat_matchup(entry: dict[str, Any], lang: str, zh_locale: str | None = None) -> str:
    return format_matchup_display(
        str(entry.get("awayAbbr") or ""),
        str(entry.get("homeAbbr") or ""),
        lang=lang,
        zh_locale=zh_locale,
        away_score=entry.get("awayScore"),
        home_score=entry.get("homeScore"),
    )


def _build_stat_entry(
    *,
    player_name: str,
    team_abbr: str,
    away_abbr: str,
    home_abbr: str,
    away_score: Any,
    home_score: Any,
    value: int,
    stat_label: str,
    lang: str,
    zh_locale: str | None,
    source: str,
    extra_stats: dict[str, int] | None = None,
) -> dict[str, Any]:
    return {
        "playerName": player_name,
        "displayName": display_player_name(player_name, lang),
        "teamAbbr": team_abbr,
        "teamName": _display_team(team_abbr, lang, zh_locale),
        "awayAbbr": away_abbr,
        "homeAbbr": home_abbr,
        "awayScore": away_score,
        "homeScore": home_score,
        "matchup": _format_stat_matchup(
            {
                "awayAbbr": away_abbr,
                "homeAbbr": home_abbr,
                "awayScore": away_score,
                "homeScore": home_score,
            },
            lang,
            zh_locale,
        ),
        "value": value,
        "displayValue": f"{value} {stat_label}",
        "source": source,
        "stats": extra_stats or {},
    }


def _update_best_entries(current: list[dict[str, Any]], candidate: dict[str, Any], *, top_n: int = 2) -> list[dict[str, Any]]:
    if not current:
        return [candidate]
    current_value = int(current[0].get("value") or 0)
    candidate_value = int(candidate.get("value") or 0)
    if candidate_value > current_value:
        return [candidate]
    if candidate_value < current_value:
        return current
    merged = current + [candidate]
    return merged[:top_n]


def _double_double_tier(player_stats: dict[str, Any]) -> tuple[str, dict[str, int]] | None:
    categories = {
        "PTS": _numeric_value(player_stats.get("PTS")),
        "REB": _numeric_value(player_stats.get("REB")),
        "AST": _numeric_value(player_stats.get("AST")),
        "STL": _numeric_value(player_stats.get("STL")),
        "BLK": _numeric_value(player_stats.get("BLK")),
    }
    achieved = {key: value for key, value in categories.items() if value is not None and value >= 10}
    if len(achieved) >= 3:
        return "tripleDouble", achieved
    if len(achieved) >= 2:
        return "doubleDouble", achieved
    return None


def _performance_sort_key(entry: dict[str, Any]) -> tuple[int, int]:
    tier = str(entry.get("tier") or "")
    priority = 1 if tier == "tripleDouble" else 0
    return (priority, int(entry.get("value") or 0))


def _stats_block(
    leaders: list[dict[str, Any]],
    *,
    none_text: str,
) -> dict[str, Any]:
    if not leaders:
        return {"value": None, "leaders": [], "summary": none_text}
    top_value = leaders[0].get("value")
    return {
        "value": top_value,
        "leaders": leaders,
        "summary": ", ".join(str(item.get("displayValue") or "") for item in leaders if item.get("displayValue")) or none_text,
    }


def build_day_stats_view(*, tz: str | None, date_text: str | None, lang: str, zh_locale: str | None = None) -> dict[str, Any]:
    day_payload = build_day_view(tz=tz, date_text=date_text, lang=lang, zh_locale=zh_locale)
    labels = _stats_day_labels(lang)
    completed_games = [game for game in (day_payload.get("games") or []) if game.get("phase") == "post"]
    top_scorer: list[dict[str, Any]] = []
    top_rebounder: list[dict[str, Any]] = []
    top_assists: list[dict[str, Any]] = []
    top_three: list[dict[str, Any]] = []
    double_doubles: list[dict[str, Any]] = []
    triple_doubles: list[dict[str, Any]] = []
    largest_margin_game: dict[str, Any] | None = None

    for entry in completed_games:
        teams = entry.get("teams") or {}
        away_abbr = str((teams.get("away") or {}).get("abbr") or "")
        home_abbr = str((teams.get("home") or {}).get("abbr") or "")
        away_score = (teams.get("away") or {}).get("score")
        home_score = (teams.get("home") or {}).get("score")
        game_context = entry.get("gameContext") or {}
        full_stats = game_context.get("fullStats") or {}
        players_by_team = full_stats.get("players") or {}
        lineups = game_context.get("lineups") or {}

        away_score_value = _numeric_value(away_score)
        home_score_value = _numeric_value(home_score)
        if away_score_value is not None and home_score_value is not None:
            margin = abs(home_score_value - away_score_value)
            if largest_margin_game is None or margin > int(largest_margin_game.get("margin") or 0):
                winner_abbr = home_abbr if home_score_value > away_score_value else away_abbr
                loser_abbr = away_abbr if winner_abbr == home_abbr else home_abbr
                largest_margin_game = {
                    "margin": margin,
                    "winnerAbbr": winner_abbr,
                    "winnerName": _display_team(winner_abbr, lang, zh_locale),
                    "loserAbbr": loser_abbr,
                    "loserName": _display_team(loser_abbr, lang, zh_locale),
                    "awayAbbr": away_abbr,
                    "homeAbbr": home_abbr,
                    "awayScore": away_score,
                    "homeScore": home_score,
                    "matchup": _format_stat_matchup(
                        {
                            "awayAbbr": away_abbr,
                            "homeAbbr": home_abbr,
                            "awayScore": away_score,
                            "homeScore": home_score,
                        },
                        lang,
                        zh_locale,
                    ),
                    "summary": f"{_display_team(winner_abbr, lang, zh_locale)} {labels['won_by']} {margin}",
                }

        for abbr in (away_abbr, home_abbr):
            team_players = list(players_by_team.get(abbr) or [])
            if team_players:
                for player in team_players:
                    name = str(player.get("playerName") or "")
                    if not name:
                        continue
                    player_stats = player.get("stats") or {}
                    points = _numeric_value(player_stats.get("PTS"))
                    rebounds = _numeric_value(player_stats.get("REB"))
                    assists = _numeric_value(player_stats.get("AST"))
                    made_threes = _three_pt_made(player_stats.get("3PT"))
                    extra_stats = {
                        key: value
                        for key, value in {
                            "PTS": points,
                            "REB": rebounds,
                            "AST": assists,
                            "STL": _numeric_value(player_stats.get("STL")),
                            "BLK": _numeric_value(player_stats.get("BLK")),
                        }.items()
                        if value is not None
                    }
                    if points is not None:
                        top_scorer = _update_best_entries(
                            top_scorer,
                            _build_stat_entry(
                                player_name=name,
                                team_abbr=abbr,
                                away_abbr=away_abbr,
                                home_abbr=home_abbr,
                                away_score=away_score,
                                home_score=home_score,
                                value=points,
                                stat_label="PTS",
                                lang=lang,
                                zh_locale=zh_locale,
                                source="fullStats",
                                extra_stats=extra_stats,
                            ),
                        )
                    if rebounds is not None:
                        top_rebounder = _update_best_entries(
                            top_rebounder,
                            _build_stat_entry(
                                player_name=name,
                                team_abbr=abbr,
                                away_abbr=away_abbr,
                                home_abbr=home_abbr,
                                away_score=away_score,
                                home_score=home_score,
                                value=rebounds,
                                stat_label="REB",
                                lang=lang,
                                zh_locale=zh_locale,
                                source="fullStats",
                                extra_stats=extra_stats,
                            ),
                        )
                    if assists is not None:
                        top_assists = _update_best_entries(
                            top_assists,
                            _build_stat_entry(
                                player_name=name,
                                team_abbr=abbr,
                                away_abbr=away_abbr,
                                home_abbr=home_abbr,
                                away_score=away_score,
                                home_score=home_score,
                                value=assists,
                                stat_label="AST",
                                lang=lang,
                                zh_locale=zh_locale,
                                source="fullStats",
                                extra_stats=extra_stats,
                            ),
                        )
                    if made_threes is not None:
                        top_three = _update_best_entries(
                            top_three,
                            _build_stat_entry(
                                player_name=name,
                                team_abbr=abbr,
                                away_abbr=away_abbr,
                                home_abbr=home_abbr,
                                away_score=away_score,
                                home_score=home_score,
                                value=made_threes,
                                stat_label="3PM",
                                lang=lang,
                                zh_locale=zh_locale,
                                source="fullStats",
                                extra_stats=extra_stats,
                            ),
                        )
                    tier = _double_double_tier(player_stats)
                    if tier:
                        tier_name, achieved = tier
                        achievement = _build_stat_entry(
                            player_name=name,
                            team_abbr=abbr,
                            away_abbr=away_abbr,
                            home_abbr=home_abbr,
                            away_score=away_score,
                            home_score=home_score,
                            value=points or 0,
                            stat_label="PTS",
                            lang=lang,
                            zh_locale=zh_locale,
                            source="fullStats",
                            extra_stats=achieved,
                        )
                        achievement["tier"] = tier_name
                        achievement["achievement"] = (
                            labels["triple_double"] if tier_name == "tripleDouble" else labels["double_double"]
                        )
                        if tier_name == "tripleDouble":
                            triple_doubles.append(achievement)
                        else:
                            double_doubles.append(achievement)
                continue

            for line in (lineups.get("leaders") or {}).get(abbr) or []:
                name, leader_stats = _leader_stats_from_line(line)
                if not name:
                    continue
                extra_stats = {key: leader_stats[key] for key in ("PTS", "REB", "AST") if key in leader_stats}
                if leader_stats.get("PTS") is not None:
                    top_scorer = _update_best_entries(
                        top_scorer,
                        _build_stat_entry(
                            player_name=name,
                            team_abbr=abbr,
                            away_abbr=away_abbr,
                            home_abbr=home_abbr,
                            away_score=away_score,
                            home_score=home_score,
                            value=int(leader_stats["PTS"]),
                            stat_label="PTS",
                            lang=lang,
                            zh_locale=zh_locale,
                            source="leaders",
                            extra_stats=extra_stats,
                        ),
                    )
                if leader_stats.get("REB") is not None:
                    top_rebounder = _update_best_entries(
                        top_rebounder,
                        _build_stat_entry(
                            player_name=name,
                            team_abbr=abbr,
                            away_abbr=away_abbr,
                            home_abbr=home_abbr,
                            away_score=away_score,
                            home_score=home_score,
                            value=int(leader_stats["REB"]),
                            stat_label="REB",
                            lang=lang,
                            zh_locale=zh_locale,
                            source="leaders",
                            extra_stats=extra_stats,
                        ),
                    )
                if leader_stats.get("AST") is not None:
                    top_assists = _update_best_entries(
                        top_assists,
                        _build_stat_entry(
                            player_name=name,
                            team_abbr=abbr,
                            away_abbr=away_abbr,
                            home_abbr=home_abbr,
                            away_score=away_score,
                            home_score=home_score,
                            value=int(leader_stats["AST"]),
                            stat_label="AST",
                            lang=lang,
                            zh_locale=zh_locale,
                            source="leaders",
                            extra_stats=extra_stats,
                        ),
                    )

    double_doubles = sorted(double_doubles, key=lambda item: (int(item.get("value") or 0)), reverse=True)[:2]
    triple_doubles = sorted(triple_doubles, key=lambda item: (int(item.get("value") or 0)), reverse=True)[:2]
    best_performance_candidates = sorted(triple_doubles + top_scorer, key=_performance_sort_key, reverse=True)
    best_performance = best_performance_candidates[:2]
    if completed_games:
        summary = (
            ", ".join(
                f"{entry.get('displayName')} {entry.get('displayValue')}"
                for entry in best_performance
                if entry.get("displayName") and entry.get("displayValue")
            )
            or labels["none"]
        )
    else:
        summary = labels["no_completed_games"]

    return {
        "intent": "stats_day",
        "scope": "multi_all",
        "requestedDate": day_payload["requestedDate"],
        "timezone": day_payload["timezone"],
        "lang": lang,
        "zhLocale": day_payload.get("zhLocale"),
        "leaders": {
            "topScorer": top_scorer,
            "topRebounder": top_rebounder,
            "topAssists": top_assists,
            "topThreePointMade": top_three,
        },
        "notableGames": [largest_margin_game] if largest_margin_game else [],
        "statsView": {
            "completedGamesCount": len(completed_games),
            "bestPerformance": best_performance,
            "topScorer": _stats_block(top_scorer, none_text=labels["none"]),
            "topRebounder": _stats_block(top_rebounder, none_text=labels["none"]),
            "topAssists": _stats_block(top_assists, none_text=labels["none"]),
            "topThreePointMade": _stats_block(top_three, none_text=labels["none"]),
            "doubleDoubles": double_doubles,
            "tripleDoubles": triple_doubles,
            "largestMarginGame": largest_margin_game,
            "summary": summary,
        },
    }


def _render_stat_leader_block(title: str, block: dict[str, Any], *, labels: dict[str, str]) -> list[str]:
    lines = [f"## {title}"]
    leaders = block.get("leaders") or []
    if not leaders:
        lines.extend(["", f"- {labels['none']}", ""])
        return lines
    lines.append("")
    for entry in leaders:
        context_parts: list[str] = []
        if entry.get("teamName"):
            context_parts.append(str(entry["teamName"]))
        if entry.get("matchup"):
            context_parts.append(str(entry["matchup"]))
        context_text = f" | {' | '.join(context_parts)}" if context_parts else ""
        lines.append(f"- {entry.get('displayName') or entry.get('playerName')} | {entry.get('displayValue')}{context_text}")
    lines.append("")
    return lines


def render_day_stats_markdown(payload: dict[str, Any]) -> str:
    lang = str(payload.get("lang") or "zh")
    base_labels = I18N.get(lang, I18N["en"])
    labels = _stats_day_labels(lang)
    stats_view = payload.get("statsView") or {}
    lines = [
        f"# {labels['title']} ({payload['requestedDate']})",
        f"> {base_labels['timezone']}: {payload['timezone']}",
        f"> {base_labels['requested_date']}: {payload['requestedDate']}",
        f"> {base_labels['view']}: {labels['view']}",
        f"> {labels['completed_games']}: {stats_view.get('completedGamesCount', 0)}",
        "",
    ]
    if not stats_view.get("completedGamesCount"):
        lines.append(f"- {labels['no_completed_games']}")
        return "\n".join(lines)
    best_performance = stats_view.get("bestPerformance") or []
    lines.extend([f"## {labels['best_performance']}", ""])
    if best_performance:
        for entry in best_performance:
            extras = entry.get("stats") or {}
            extras_text = ", ".join(f"{value} {key}" for key, value in extras.items())
            suffix = f" | {extras_text}" if extras_text else ""
            lines.append(
                f"- {entry.get('displayName') or entry.get('playerName')} | {entry.get('teamName') or ''} | {entry.get('matchup') or ''}{suffix}".replace(" |  | ", " | ")
            )
    else:
        lines.append(f"- {labels['none']}")
    lines.append("")
    lines.extend(_render_stat_leader_block(labels["top_scorer"], stats_view.get("topScorer") or {}, labels=labels))
    lines.extend(_render_stat_leader_block(labels["top_rebounder"], stats_view.get("topRebounder") or {}, labels=labels))
    lines.extend(_render_stat_leader_block(labels["top_assists"], stats_view.get("topAssists") or {}, labels=labels))
    lines.extend(_render_stat_leader_block(labels["top_three"], stats_view.get("topThreePointMade") or {}, labels=labels))
    lines.extend([f"## {labels['double_triple']}", ""])
    double_doubles = stats_view.get("doubleDoubles") or []
    triple_doubles = stats_view.get("tripleDoubles") or []
    if triple_doubles or double_doubles:
        for entry in triple_doubles + double_doubles:
            achievement = entry.get("achievement") or labels["none"]
            extras = ", ".join(f"{value} {key}" for key, value in (entry.get("stats") or {}).items())
            extras_text = f" | {extras}" if extras else ""
            lines.append(
                f"- {entry.get('displayName') or entry.get('playerName')} | {achievement} | {entry.get('teamName') or ''} | {entry.get('matchup') or ''}{extras_text}".replace(" |  | ", " | ")
            )
    else:
        lines.append(f"- {labels['none']}")
    lines.extend(["", f"## {labels['largest_margin']}", ""])
    largest_margin = stats_view.get("largestMarginGame") or {}
    if largest_margin:
        lines.append(
            f"- {largest_margin.get('matchup')} | {largest_margin.get('winnerName')} {labels['won_by']} {largest_margin.get('margin')}"
        )
    else:
        lines.append(f"- {labels['none']}")
    lines.extend(["", f"## {labels['summary_prefix']}", "", f"- {stats_view.get('summary') or labels['none']}"])
    return "\n".join(lines).rstrip()


def _render_info_section(
    info: dict[str, Any],
    labels: dict[str, str],
    phase_labels: dict[str, str],
    *,
    zh_locale: str | None = None,
) -> list[str]:
    lang = "zh" if labels.get("timezone") == "请求方时区" else "en"
    lines = [f"## {phase_labels['info']}"]
    matchup = info.get("matchup") or {}
    team_abbrs = _matchup_team_abbrs(matchup)
    away_abbr = ((matchup.get("away") or {}).get("abbr"))
    home_abbr = ((matchup.get("home") or {}).get("abbr"))
    away_score = (matchup.get("away") or {}).get("score")
    home_score = (matchup.get("home") or {}).get("score")
    if away_abbr and home_abbr:
        if info.get("statusState") in {"in", "post"} and (away_score not in (None, "") or home_score not in (None, "")):
            lines.append(f"- {format_matchup_display(away_abbr, home_abbr, lang=lang, zh_locale=zh_locale, away_score=away_score, home_score=home_score)}")
        else:
            lines.append(f"- {format_matchup_display(away_abbr, home_abbr, lang=lang, zh_locale=zh_locale)}")
    elif matchup.get("text"):
        lines.append(f"- {_localize_team_mentions(matchup['text'], lang=lang, zh_locale=zh_locale, team_abbrs=team_abbrs)}")
    if info.get("startTimeLocal"):
        lines.append(f"- {labels['start_time']}: {info['startTimeLocal']}")
    status_detail = info.get("statusDetail")
    if status_detail:
        lines.append(f"- {labels['status']}: {status_detail}")
    if info.get("venue"):
        lines.append(f"- {labels['venue']}: {info['venue']}")
    broadcasts = info.get("broadcasts") or []
    if broadcasts:
        lines.append(f"- {labels['broadcasts']}: {', '.join(broadcasts)}")
    standings = info.get("standings") or {}
    for side in ("away", "home"):
        team = matchup.get(side) or {}
        abbr = team.get("abbr")
        if not abbr:
            continue
        record = team.get("record") or labels["none"]
        standing = standings.get(abbr) or {}
        rank_bits: list[str] = []
        if standing.get("wins") is not None and standing.get("losses") is not None:
            rank_bits.append(f"{standing['wins']}-{standing['losses']}")
        if standing.get("streak"):
            rank_bits.append(str(standing["streak"]))
        suffix = f" ({', '.join(rank_bits)})" if rank_bits else ""
        if lang == "zh":
            lines.append(f"- {_display_team(abbr, lang, zh_locale)} {labels['records']}: {record}{suffix}")
        else:
            lines.append(f"- {_display_team(abbr, lang, zh_locale)} enter at {record}{suffix}.")
    lines.append("")
    return lines


def _render_lineups_section(
    lineups: dict[str, Any],
    season_averages: dict[str, Any],
    matchup: dict[str, Any],
    labels: dict[str, str],
    phase_labels: dict[str, str],
    *,
    zh_locale: str | None = None,
) -> list[str]:
    lang = "zh" if labels.get("timezone") == "请求方时区" else "en"
    lines = [f"## {phase_labels['lineups']}"]
    if lineups.get("startersConfirmed"):
        for side in ("away", "home"):
            team = matchup.get(side) or {}
            abbr = team.get("abbr")
            if not abbr:
                continue
            starters = (lineups.get("starters") or {}).get(abbr) or []
            rendered = ", ".join(localize_player_list(starters, lang)) if starters else phase_labels["none"]
            lines.append(f"- {_display_team(abbr, lang, zh_locale)} {labels['starters']}: {rendered}")
    else:
        lines.append(f"- {phase_labels['starters_pending']}")
    for side in ("away", "home"):
        team = matchup.get(side) or {}
        abbr = team.get("abbr")
        if not abbr:
            continue
        key_players = (lineups.get("keyPlayers") or {}).get(abbr) or (lineups.get("leaders") or {}).get(abbr) or []
        if not key_players:
            continue
        lines.append(f"- {_display_team(abbr, lang, zh_locale)}:")
        for line in key_players[:3]:
            lines.append(f"  - {localize_player_line(line, lang)}")
    lines.append("")
    return lines


def _render_injuries_section(
    injuries: dict[str, Any],
    matchup: dict[str, Any],
    labels: dict[str, str],
    phase_labels: dict[str, str],
    *,
    zh_locale: str | None = None,
    active_players: list[str] | None = None,
) -> list[str]:
    lang = "zh" if labels.get("timezone") == "请求方时区" else "en"
    lines = [f"## {phase_labels['injuries']}"]
    by_team = injuries.get("byTeam") or {}
    # 如果有已确认上场球员名单，则过滤掉其中的人（名字子字符串匹配）
    active_lower: set[str] = {n.lower() for n in (active_players or []) if n}
    for side in ("away", "home"):
        team = matchup.get(side) or {}
        abbr = team.get("abbr")
        if not abbr:
            continue
        items = by_team.get(abbr) or []
        filtered: list[str] = []
        for item in items[:6]:
            player_name = extract_primary_name(item).lower()
            if active_lower and any(
                player_name in active.lower() or active.lower() in player_name
                for active in active_lower
            ):
                continue
            filtered.append(item)
        localized = [localize_player_line(item, lang) for item in filtered]
        lines.append(f"- {_display_team(abbr, lang, zh_locale)}: {'; '.join(localized) if localized else phase_labels['none']}")
    lines.append("")
    return lines


def _render_team_totals_section(
    full_stats: dict[str, Any],
    matchup: dict[str, Any],
    labels: dict[str, str],
    phase_labels: dict[str, str],
    *,
    zh_locale: str | None = None,
) -> list[str]:
    lang = "zh" if labels.get("timezone") == "请求方时区" else "en"
    lines = [f"## {phase_labels['team_totals']}"]
    teams = full_stats.get("teams") or {}
    emitted = False
    for side in ("away", "home"):
        team = matchup.get(side) or {}
        abbr = team.get("abbr")
        if not abbr:
            continue
        stats = teams.get(abbr) or {}
        compact = render_full_stats_team_line(stats)
        if compact:
            lines.append(f"- {_display_team(abbr, lang, zh_locale)}: {compact}")
            emitted = True
    if not emitted:
        lines.append(f"- {phase_labels['none']}")
    lines.append("")
    return lines


def _render_key_player_lines_section(
    full_stats: dict[str, Any],
    matchup: dict[str, Any],
    labels: dict[str, str],
    phase_labels: dict[str, str],
    *,
    limit: int = 3,
    zh_locale: str | None = None,
) -> list[str]:
    lang = "zh" if labels.get("timezone") == "请求方时区" else "en"
    lines = [f"## {phase_labels['key_player_lines']}"]
    players_by_team = full_stats.get("players") or {}
    emitted = False
    for side in ("away", "home"):
        team = matchup.get(side) or {}
        abbr = team.get("abbr")
        if not abbr:
            continue
        players = players_by_team.get(abbr) or []
        if not players:
            continue
        top_lines = [render_compact_player_stat_line(player, lang=lang, include_secondary=True, include_shooting=True) for player in players[:limit]]
        lines.append(f"- {_display_team(abbr, lang, zh_locale)}: {'; '.join([line for line in top_lines if line])}")
        emitted = True
    if not emitted:
        lines.append(f"- {phase_labels['none']}")
    lines.append("")
    return lines


def _render_post_starters_section(
    lineups: dict[str, Any],
    matchup: dict[str, Any],
    phase_labels: dict[str, str],
    *,
    lang: str,
    zh_locale: str | None = None,
) -> list[str]:
    lines = [f"## {phase_labels['starters_section']}"]
    if lineups.get("startersConfirmed"):
        for side in ("away", "home"):
            team = matchup.get(side) or {}
            abbr = team.get("abbr")
            if not abbr:
                continue
            starters = (lineups.get("starters") or {}).get(abbr) or []
            rendered = ", ".join(localize_player_list(starters, lang)) if starters else phase_labels["none"]
            lines.append(f"- {_display_team(abbr, lang, zh_locale)}: {rendered}")
    else:
        lines.append(f"- {phase_labels['starters_pending']}")
    lines.append("")
    return lines


def _render_post_key_performances_section(
    full_stats: dict[str, Any],
    lineups: dict[str, Any],
    matchup: dict[str, Any],
    phase_labels: dict[str, str],
    *,
    lang: str,
    limit: int = 3,
    zh_locale: str | None = None,
) -> list[str]:
    lines = [f"## {phase_labels['post_key_players']}"]
    players_by_team = full_stats.get("players") or {}
    emitted = False
    for side in ("away", "home"):
        team = matchup.get(side) or {}
        abbr = team.get("abbr")
        if not abbr:
            continue
        players = players_by_team.get(abbr) or []
        rendered_players = []
        for player in players[:limit]:
            # 从结构体直接构建 Name | PTS | REB | AST
            display_name = player.get("displayName") or player.get("name") or ""
            player_stats = player.get("stats") or {}
            pts = player_stats.get("points")
            reb = player_stats.get("rebounds")
            ast = player_stats.get("assists")
            parts = [localize_player_line(display_name, lang)]
            if pts is not None:
                parts.append(f"{pts} PTS")
            if reb is not None:
                parts.append(f"{reb} REB")
            if ast is not None:
                parts.append(f"{ast} AST")
            line = " | ".join(parts)
            if line:
                rendered_players.append(line)
        if rendered_players:
            lines.append(f"- {_display_team(abbr, lang, zh_locale)}:")
            lines.extend([f"  - {line}" for line in rendered_players])
            emitted = True
            continue
        fallback_players = (lineups.get("keyPlayers") or {}).get(abbr) or (lineups.get("leaders") or {}).get(abbr) or []
        if fallback_players:
            lines.append(f"- {_display_team(abbr, lang, zh_locale)}: {', '.join(localize_player_line(item, lang) for item in fallback_players[:limit])}")
            emitted = True
    if not emitted:
        lines.append(f"- {phase_labels['none']}")
    lines.append("")
    return lines


def _render_post_team_totals_section(
    full_stats: dict[str, Any],
    matchup: dict[str, Any],
    phase_labels: dict[str, str],
    *,
    lang: str,
    zh_locale: str | None = None,
) -> list[str]:
    lines = [f"## {phase_labels['post_team_totals']}"]
    teams = full_stats.get("teams") or {}
    emitted = False
    for side in ("away", "home"):
        team = matchup.get(side) or {}
        abbr = team.get("abbr")
        if not abbr:
            continue
        compact = render_compact_team_totals_line(teams.get(abbr) or {}, lang=lang)
        if compact:
            lines.append(f"- {_display_team(abbr, lang, zh_locale)}: {compact}")
            emitted = True
    if not emitted:
        lines.append(f"- {phase_labels['none']}")
    lines.append("")
    return lines


def _player_impact_sort_key(player: dict[str, Any]) -> tuple[float, float, float, float, float, float]:
    stats = player.get("stats") or {}
    def num(key: str) -> float:
        value = stats.get(key)
        try:
            return float(value)
        except (TypeError, ValueError):
            return -1.0
    return (
        num("PTS"),
        num("REB"),
        num("AST"),
        num("STL"),
        num("BLK"),
        num("MIN"),
    )


def _select_live_players_for_display(
    *,
    abbr: str,
    players_by_team: dict[str, list[dict[str, Any]]],
    lineups: dict[str, Any],
    limit: int = 5,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    players = list(players_by_team.get(abbr) or [])
    starters = (lineups.get("starters") or {}).get(abbr) or []
    normalized_players = {
        normalize_player_name(str(player.get("playerName") or "")): player
        for player in players
        if player.get("playerName")
    }
    selected: list[dict[str, Any]] = []
    seen: set[str] = set()
    matched_starters: list[str] = []
    unmatched_starters: list[str] = []
    for starter_name in starters:
        normalized = normalize_player_name(starter_name)
        player = normalized_players.get(normalized)
        if player:
            selected.append(player)
            seen.add(normalized)
            matched_starters.append(starter_name)
        else:
            unmatched_starters.append(starter_name)
    remaining: list[tuple[int, dict[str, Any]]] = []
    for index, player in enumerate(players):
        normalized = normalize_player_name(str(player.get("playerName") or ""))
        if not normalized or normalized in seen:
            continue
        remaining.append((index, player))
    remaining.sort(
        key=lambda item: (
            0 if item[1].get("starter") else 1,
            -_player_impact_sort_key(item[1])[0],
            -_player_impact_sort_key(item[1])[1],
            -_player_impact_sort_key(item[1])[2],
            -_player_impact_sort_key(item[1])[3],
            -_player_impact_sort_key(item[1])[4],
            -_player_impact_sort_key(item[1])[5],
            item[0],
        )
    )
    selected.extend(player for _, player in remaining[: max(0, limit - len(selected))])
    return selected[:limit], {
        "availableCount": len(players),
        "renderedCount": len(selected[:limit]),
        "matchedStarters": matched_starters,
        "unmatchedStarters": unmatched_starters,
    }


def _build_live_player_display(
    *,
    full_stats: dict[str, Any],
    lineups: dict[str, Any],
    matchup: dict[str, Any],
    limit: int = 5,
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, dict[str, Any]]]:
    players_by_team = full_stats.get("players") or {}
    selected_by_team: dict[str, list[dict[str, Any]]] = {}
    coverage_by_team: dict[str, dict[str, Any]] = {}
    for side in ("away", "home"):
        team = matchup.get(side) or {}
        abbr = team.get("abbr")
        if not abbr:
            continue
        selected, coverage = _select_live_players_for_display(
            abbr=abbr,
            players_by_team=players_by_team,
            lineups=lineups,
            limit=limit,
        )
        selected_by_team[abbr] = selected
        coverage_by_team[abbr] = coverage
    return selected_by_team, coverage_by_team


def _status_to_phase(status_state: str) -> str:
    if status_state == "in":
        return "live"
    if status_state == "post":
        return "post"
    return "pregame"


def _day_card_status_title(phase: str, labels: dict[str, str]) -> str:
    if phase == "live":
        return labels["live_title"]
    if phase == "post":
        return labels["post_title"]
    return labels["pre_title"]


def _compact_lineups_for_day(scene: dict[str, Any]) -> dict[str, Any]:
    game = scene["game"]
    lineups = (game.get("gameContext") or {}).get("lineups") or {}
    season_averages = (game.get("gameContext") or {}).get("seasonAverages") or {}
    compact: dict[str, list[str]] = {}
    for abbr in (game["away"]["abbr"], game["home"]["abbr"]):
        candidates = (lineups.get("keyPlayers") or {}).get(abbr) or (lineups.get("leaders") or {}).get(abbr) or []
        lines: list[str] = []
        for line in candidates[:2]:
            primary = extract_primary_name(line)
            averages = _format_average_line((season_averages.get(abbr) or {}).get(primary) or {})
            suffix = f" ({averages})" if averages else ""
            lines.append(f"{line}{suffix}")
        compact[abbr] = lines
    return {
        "startersConfirmed": bool(lineups.get("startersConfirmed")),
        "starters": lineups.get("starters") or {},
        "keyPlayersByTeam": compact,
    }


def _build_pregame_card(scene: dict[str, Any]) -> dict[str, Any]:
    game = scene["game"]
    pregame = scene.get("pregame") or {}
    prediction = pregame.get("prediction") or {}
    return {
        "type": "pregameCard",
        "info": pregame.get("info") or {},
        "lineups": _compact_lineups_for_day(scene),
        "injuries": {
            "featuredByTeam": (pregame.get("injuries") or {}).get("compactByTeam") or (pregame.get("injuries") or {}).get("featuredByTeam") or {},
        },
        "teamForm": pregame.get("teamForm") or {},
        "prediction": {
            "summary": prediction.get("summary") or "",
            "trend": prediction.get("trend") or "",
            "keyMatchup": prediction.get("keyMatchup") or "",
        },
        "summary": pregame.get("summary") or "",
        "teams": {
            "away": game["away"],
            "home": game["home"],
        },
    }


def _build_live_card(scene: dict[str, Any]) -> dict[str, Any]:
    live = scene.get("live") or {}
    live_state = live.get("liveState") or {}
    full_stats = ((scene["game"].get("gameContext") or {}).get("fullStats") or {"available": False, "teams": {}, "players": {}})
    lineups = live.get("lineups") or {}
    matchup = ((live.get("info") or {}).get("matchup") or {})
    _, coverage = _build_live_player_display(full_stats=full_stats, lineups=lineups, matchup=matchup, limit=5)
    latest_play = ""
    if live_state.get("playTimeline"):
        item = (live_state.get("playTimeline") or [])[-1]
        latest_clock = " ".join(
            part
            for part in (
                f"P{item.get('period')}" if item.get("period") else "",
                item.get("clock") or "",
            )
            if part
        ).strip()
        latest_text = item.get("text") or item.get("shortDescription") or ""
        latest_play = f"{latest_clock} {latest_text}".strip()
    return {
        "type": "liveCard",
        "info": live.get("info") or {},
        "lineups": _compact_lineups_for_day(scene),
        "injuries": live.get("injuries") or {},
        "liveState": {
            "displayClock": live_state.get("displayClock"),
            "period": live_state.get("period"),
            "latestPlay": latest_play,
            "winProbabilityTimeline": live_state.get("winProbabilityTimeline") or [],
        },
        "momentum": live.get("momentum") or {},
        "fullStats": full_stats,
        "playerStatsCoverage": coverage,
        "digest": {
            "plays": (scene.get("digest") or {}).get("plays") or [],
        },
        "summary": live.get("summary") or "",
    }


def _build_postgame_card(scene: dict[str, Any]) -> dict[str, Any]:
    postgame = scene.get("postgame") or {}
    return {
        "type": "postgameCard",
        "info": postgame.get("info") or {},
        "lineups": _compact_lineups_for_day(scene),
        "injuries": postgame.get("injuries") or {},
        "fullStats": postgame.get("fullStats") or {"available": False, "teams": {}, "players": {}},
        "turningPoint": postgame.get("turningPoint") or "",
        "summary": postgame.get("summary") or "",
        "trend": scene.get("analysis", {}).get("trend") or "",
        "reasons": scene.get("analysis", {}).get("reasons") or [],
    }


def _build_day_card(scene: dict[str, Any], phase: str) -> dict[str, Any]:
    if phase == "live":
        return _build_live_card(scene)
    if phase == "post":
        return _build_postgame_card(scene)
    return _build_pregame_card(scene)


def build_day_view(*, tz: str | None, date_text: str | None, lang: str, zh_locale: str | None = None) -> dict[str, Any]:
    report = build_scene_report(tz=tz, date_text=date_text, team=None, lang=lang, zh_locale=zh_locale)
    day_labels = _day_labels(lang)
    bucket_defs = [
        ("live", "in", day_labels["live_title"]),
        ("post", "post", day_labels["post_title"]),
        ("pregame", "pre", day_labels["pre_title"]),
    ]
    raw_games = sorted(
        report["games"],
        key=lambda game: (
            {"in": 0, "post": 1, "pre": 2}.get(str(game.get("statusState") or "pre"), 3),
            str(game.get("startTimeLocal") or ""),
            str(game.get("eventId") or ""),
        ),
    )
    scenes: list[dict[str, Any]] = []
    for game in raw_games:
        phase = _status_to_phase(str(game.get("statusState") or "pre"))
        scenes.append(finalize_scene_game(report=report, game=game, lang=lang, analysis_mode=phase, intent="day", scope="multi_all"))
    games_payload: list[dict[str, Any]] = []
    status_buckets: list[dict[str, Any]] = []
    for phase, state, title in bucket_defs:
        event_ids = [scene["game"]["eventId"] for scene in scenes if scene["game"].get("statusState") == state]
        status_buckets.append(
            {
                "phase": phase,
                "statusState": state,
                "title": title,
                "count": len(event_ids),
                "eventIds": event_ids,
            }
        )
    for scene in scenes:
        game = scene["game"]
        phase = _status_to_phase(str(game.get("statusState") or "pre"))
        games_payload.append(
            {
                "eventId": game["eventId"],
                "phase": phase,
                "teams": {
                    "away": game["away"],
                    "home": game["home"],
                },
                "gameContext": game.get("gameContext") or {},
                "card": _build_day_card(scene, phase),
            }
        )
    summary = format_counts_summary(report["gameCounts"], report["labels"])
    return {
        "intent": "day",
        "scope": "multi_all",
        "requestedDate": report["requestedDate"],
        "timezone": report["timezone"],
        "lang": lang,
        "zhLocale": report.get("zhLocale"),
        "dayView": {
            "counts": report["gameCounts"],
            "statusBuckets": status_buckets,
            "summary": summary,
        },
        "games": games_payload,
    }


def render_day_view_markdown(payload: dict[str, Any]) -> str:
    lang = str(payload.get("lang") or "zh")
    zh_locale = payload.get("zhLocale")
    labels = I18N.get(lang, I18N["en"])
    day_labels = _day_labels(lang)
    lines = [
        f"# {labels['title_day']} ({payload['requestedDate']})",
        f"> {labels['timezone']}: {payload['timezone']}",
        f"> {labels['requested_date']}: {payload['requestedDate']}",
        f"> {labels['view']}: {day_labels['view']}",
        f"> {payload['dayView']['summary']}",
        "",
        labels["local_tip"],
        "",
    ]
    games = payload.get("games") or []
    if not games:
        lines.append(f"- {labels['no_games']}")
        return "\n".join(lines)
    section_order = [
        ("live", day_labels["live_title"]),
        ("post", day_labels["post_title"]),
        ("pregame", day_labels["pre_title"]),
    ]
    for phase, title in section_order:
        section_games = [game for game in games if game.get("phase") == phase]
        if not section_games:
            continue
        lines.extend([f"## {title}", ""])
        for entry in section_games:
            info = (entry.get("gameContext") or {}).get("info") or {}
            matchup = info.get("matchup") or {}
            team_abbrs = _matchup_team_abbrs(matchup)
            away_abbr = entry["teams"]["away"]["abbr"]
            home_abbr = entry["teams"]["home"]["abbr"]
            away_score = (entry["teams"]["away"] or {}).get("score")
            home_score = (entry["teams"]["home"] or {}).get("score")
            text = format_matchup_display(away_abbr, home_abbr, lang=lang, zh_locale=zh_locale, away_score=away_score, home_score=home_score)
            lines.append(f"### {text}")
            info_parts: list[str] = []
            if info.get("startTimeLocal"):
                info_parts.append(f"{labels['start_time']}: {info['startTimeLocal']}")
            if info.get("venue"):
                info_parts.append(f"{labels['venue']}: {info['venue']}")
            if info_parts:
                lines.append(f"- {'，'.join(info_parts) if lang == 'zh' else ' | '.join(info_parts)}")
            card = entry.get("card") or {}
            if phase == "pregame":
                injuries = (card.get("injuries") or {}).get("featuredByTeam") or {}
                for abbr in (away_abbr, home_abbr):
                    items = injuries.get(abbr) or []
                    if items:
                        localized = [localize_player_line(item, lang) for item in items[:2]]
                        prefix = "伤病重点" if lang == "zh" else "Injury watch"
                        lines.append(f"- {_display_team(abbr, lang, zh_locale)} {prefix}: {'; '.join(localized)}")
                team_form = card.get("teamForm") or {}
                for abbr in (away_abbr, home_abbr):
                    snapshot = team_form.get(abbr) or {}
                    if not snapshot:
                        continue
                    recent = (snapshot.get("recentForm") or {}).get("record") or "N/A"
                    rest_days = (snapshot.get("schedule") or {}).get("restDays")
                    rest_text = labels["pending"] if rest_days is None else str(rest_days)
                    lines.append(f"- {_narrative_team_form(_display_team(abbr, lang, zh_locale), recent, rest_text, lang)}")
                prediction = card.get("prediction") or {}
                if prediction.get("summary"):
                    _append_unique_line(
                        lines,
                        _localize_team_mentions(prediction["summary"], lang=lang, zh_locale=zh_locale, team_abbrs=team_abbrs),
                    )
                if card.get("summary"):
                    _append_unique_line(
                        lines,
                        _localize_team_mentions(card["summary"], lang=lang, zh_locale=zh_locale, team_abbrs=team_abbrs),
                    )
            elif phase == "live":
                live_state = card.get("liveState") or {}
                momentum = card.get("momentum") or {}
                lineups = card.get("lineups") or {}
                if live_state.get("displayClock") or live_state.get("period"):
                    if lang == "zh":
                        lines.append(f"- 比赛进程：第 {live_state.get('period') or '?'} 节，{labels['clock']} {live_state.get('displayClock') or labels['pending']}")
                    else:
                        lines.append(
                            f"- The game is in the {_ordinal_period(live_state.get('period'))} quarter with {live_state.get('displayClock') or labels['pending']} on the clock."
                        )
                if momentum.get("trend"):
                    _append_unique_line(
                        lines,
                        _localize_team_mentions(momentum["trend"], lang=lang, zh_locale=zh_locale, team_abbrs=team_abbrs),
                    )
                if live_state.get("latestPlay"):
                    lines.append(f"- {_narrative_latest_play(live_state['latestPlay'], lang)}")
                full_stats = card.get("fullStats") or {}
                players, _ = _build_live_player_display(full_stats=full_stats, lineups=lineups, matchup=matchup, limit=3)
                for abbr in (away_abbr, home_abbr):
                    player_lines = [
                        render_compact_player_stat_line(player, lang=lang, include_secondary=False, include_shooting=False)
                        for player in (players.get(abbr) or [])
                    ]
                    player_lines = [line for line in player_lines if line]
                    if player_lines:
                        lines.append(f"- {_narrative_key_lines(_display_team(abbr, lang, zh_locale), '; '.join(player_lines), lang)}")
                if card.get("summary"):
                    _append_unique_line(
                        lines,
                        _localize_team_mentions(card["summary"], lang=lang, zh_locale=zh_locale, team_abbrs=team_abbrs),
                    )
            else:
                if card.get("summary"):
                    _append_unique_line(
                        lines,
                        _localize_team_mentions(card["summary"], lang=lang, zh_locale=zh_locale, team_abbrs=team_abbrs),
                    )
                if card.get("turningPoint"):
                    localized_turning_point = _localize_team_mentions(card["turningPoint"], lang=lang, zh_locale=zh_locale, team_abbrs=team_abbrs)
                    lines.append(f"- {_narrative_turning_point(localized_turning_point, lang)}")
            lines.append("")
    return "\n".join(lines).rstrip()


def render_live_scene_markdown(scene: dict[str, Any]) -> str:
    report = scene["report"]
    labels = report["labels"]
    phase_labels = _phase_labels(report["lang"])
    zh_locale = report.get("zhLocale")
    live = scene.get("live") or {}
    info = live.get("info") or {}
    matchup = info.get("matchup") or {}
    team_abbrs = _matchup_team_abbrs(matchup)
    lineups = live.get("lineups") or {}
    injuries = live.get("injuries") or {}
    live_state = live.get("liveState") or {}
    momentum = live.get("momentum") or {}
    game_context = scene["game"].get("gameContext") or {}
    full_stats = game_context.get("fullStats") or {"available": False, "teams": {}, "players": {}}
    selected_players, _ = _build_live_player_display(full_stats=full_stats, lineups=lineups, matchup=matchup, limit=5)
    lines = [
        f"# {phase_labels['live_title']} ({report['requestedDate']})",
        f"> {labels['timezone']}: {report['timezone']}",
        f"> {labels['requested_date']}: {report['requestedDate']}",
        f"> {labels['view']}: game",
        f"> {labels['filter_team']}: {report['teamFilter']}",
        "",
        labels["local_tip"],
        "",
    ]
    lines.extend(_render_info_section(info, labels, phase_labels, zh_locale=zh_locale))
    lines.extend(_render_lineups_section(lineups, game_context.get("seasonAverages") or {}, matchup, labels, phase_labels, zh_locale=zh_locale))
    lines.extend(_render_injuries_section(injuries, matchup, labels, phase_labels, zh_locale=zh_locale, active_players=lineups.get("activeParticipants") or lineups.get("verifiedPlayers")))
    lines.append(f"## {phase_labels['live_flow']}")
    if live.get("summary"):
        _append_unique_line(lines, _localize_team_mentions(live["summary"], lang=report["lang"], zh_locale=zh_locale, team_abbrs=team_abbrs))
    if momentum.get("trend"):
        _append_unique_line(lines, _localize_team_mentions(momentum["trend"], lang=report["lang"], zh_locale=zh_locale, team_abbrs=team_abbrs))

    if live_state.get("displayClock") or live_state.get("period"):
        if report["lang"] == "zh":
            lines.append(f"- 比赛已经来到第 {live_state.get('period') or '?'} 节，{labels['clock']} {live_state.get('displayClock') or labels['pending']}")
        else:
            lines.append(f"- The game is in the {_ordinal_period(live_state.get('period'))} quarter with {live_state.get('displayClock') or labels['pending']} on the clock.")
    if live_state.get("playTimeline"):
        latest_play = (live_state.get("playTimeline") or [])[-1]
        latest_clock = " ".join(part for part in (f"P{latest_play.get('period')}" if latest_play.get("period") else "", latest_play.get("clock") or "") if part).strip()
        latest_text = latest_play.get("text") or latest_play.get("shortDescription") or ""
        if latest_text:
            prefix = f"{latest_clock} " if latest_clock else ""
            lines.append(f"- {_narrative_latest_play(f'{prefix}{latest_text}'.strip(), report['lang'])}")
    if live_state.get("winProbabilityTimeline"):
        latest_win_probability = (live_state.get("winProbabilityTimeline") or [])[-1]
        home_probability = latest_win_probability.get("homeWinPercentage")
        if home_probability is not None:
            home_name = _display_team((matchup.get("home") or {}).get("abbr"), report["lang"], zh_locale)
            if report["lang"] == "zh":
                lines.append(f"- {home_name}此刻的主场胜率大约在 {home_probability:.0%}。")
            else:
                lines.append(f"- {home_name}'s live home win probability sits around {home_probability:.0%}.")
    if scene.get("analysis", {}).get("turningPoint"):
        lines.append(f"- {_narrative_turning_point(scene['analysis']['turningPoint'], report['lang'])}")
    if momentum.get("reasons"):
        localized_reasons = [
            _localize_team_mentions(reason, lang=report["lang"], zh_locale=zh_locale, team_abbrs=team_abbrs)
            for reason in (momentum.get("reasons") or [])
        ]
        lines.append(f"- {_narrative_reasons(localized_reasons, lang=report['lang'])}")
    lines.append("")

    if scene["digest"]["plays"]:
        lines.extend([f"## {phase_labels['play_digest']}", ""])
        for item in scene["digest"]["plays"]:
            lines.append(f"- {item}")
        lines.append("")
    localized_summary = _localize_team_mentions(live.get("summary") or phase_labels["none"], lang=report["lang"], zh_locale=zh_locale, team_abbrs=team_abbrs)
    lines.extend([f"## {phase_labels['summary']}", "", f"- {localized_summary}", ""])
    lines.extend(
        [
            f"> sources: {', '.join(scene['sources'])}",
            f"> fallbackLevel: {scene['fallbackLevel']}",
            f"> dataFreshness: {scene['dataFreshness']}",
        ]
    )
    return "\n".join(lines)


def render_postgame_scene_markdown(scene: dict[str, Any]) -> str:
    report = scene["report"]
    labels = report["labels"]
    phase_labels = _phase_labels(report["lang"])
    lang = report["lang"]
    zh_locale = report.get("zhLocale")
    postgame = scene.get("postgame") or {}
    info = postgame.get("info") or {}
    matchup = info.get("matchup") or {}
    team_abbrs = _matchup_team_abbrs(matchup)
    lineups = postgame.get("lineups") or {}
    injuries = postgame.get("injuries") or {}
    full_stats = postgame.get("fullStats") or {"available": False, "teams": {}, "players": {}}
    lines = [
        f"# {phase_labels['post_title']} ({report['requestedDate']})",
        f"> {labels['timezone']}: {report['timezone']}",
        f"> {labels['requested_date']}: {report['requestedDate']}",
        f"> {labels['view']}: game",
        f"> {labels['filter_team']}: {report['teamFilter']}",
        "",
        labels["local_tip"],
        "",
    ]
    lines.extend(_render_info_section(info, labels, phase_labels, zh_locale=zh_locale))
    lines.extend(_render_post_starters_section(lineups, matchup, phase_labels, lang=lang, zh_locale=zh_locale))
    lines.append(f"## {phase_labels['post_flow']}")
    if postgame.get("summary"):
        _append_unique_line(lines, _localize_team_mentions(postgame["summary"], lang=lang, zh_locale=zh_locale, team_abbrs=team_abbrs))
    if scene.get("analysis", {}).get("trend"):
        _append_unique_line(lines, _localize_team_mentions(scene["analysis"]["trend"], lang=lang, zh_locale=zh_locale, team_abbrs=team_abbrs))
    if scene.get("analysis", {}).get("reasons"):
        localized_reasons = [
            _localize_team_mentions(_localize_analysis_reason(reason, lang), lang=lang, zh_locale=zh_locale, team_abbrs=team_abbrs)
            for reason in (scene.get("analysis", {}).get("reasons") or [])
        ]
        lines.append(f"- {_post_reasons_sentence(localized_reasons, lang=lang)}")
    lines.append("")
    lines.extend(_render_post_key_performances_section(full_stats, lineups, matchup, phase_labels, lang=lang, zh_locale=zh_locale))
    lines.extend(_render_post_team_totals_section(full_stats, matchup, phase_labels, lang=lang, zh_locale=zh_locale))
    lines.extend(_render_injuries_section(injuries, matchup, labels, phase_labels, zh_locale=zh_locale))
    localized_turning_point = _localize_team_mentions(postgame.get("turningPoint") or phase_labels["none"], lang=lang, zh_locale=zh_locale, team_abbrs=team_abbrs)
    lines.extend([f"## {phase_labels['turning_point']}", "", f"- {_narrative_turning_point(localized_turning_point, lang)}", ""])
    localized_summary = _localize_team_mentions(postgame.get("summary") or phase_labels["none"], lang=lang, zh_locale=zh_locale, team_abbrs=team_abbrs)
    lines.extend([f"## {phase_labels['summary']}", "", f"- {localized_summary}", ""])
    lines.extend(
        [
            f"> sources: {', '.join(scene['sources'])}",
            f"> fallbackLevel: {scene['fallbackLevel']}",
            f"> dataFreshness: {scene['dataFreshness']}",
        ]
    )
    return "\n".join(lines)


def harden_game_injuries(game: dict[str, Any], *, tz: str | None) -> None:
    reference_time = _reference_now(tz)
    game.setdefault("injuryMeta", {})
    game.setdefault("injuryItems", {})
    merged_injuries: dict[str, list[str]] = {}
    for side in ("away", "home"):
        team = game[side]
        abbr = team["abbr"]
        resolution = resolve_team_injury_sources(
            team_abbr=abbr,
            team_id=team.get("id") or provider_team_id(abbr, "espn"),
            team_display_name=team.get("displayName") or "",
            summary_lines=(game.get("injuries") or {}).get(abbr, []),
            start_time_utc=game.get("startTimeUtc") or "",
            away_abbr=game["away"]["abbr"],
            home_abbr=game["home"]["abbr"],
            reference_time=reference_time,
        )
        game["injuryItems"][abbr] = [dict(item) for item in resolution["items"]]
        merged_injuries[abbr] = [
            " - ".join(
                part
                for part in (
                    item.get("playerName"),
                    item.get("status"),
                    item.get("detail"),
                )
                if part
            )
            for item in resolution["items"]
        ]
        game["injuryMeta"][abbr] = {
            "primarySource": resolution["primarySource"],
            "sources": resolution["sources"],
            "reportDateTime": resolution["reportDateTime"],
            "provisional": resolution["provisional"],
        }
    game["injuries"] = merged_injuries


def finalize_scene_game(
    *,
    report: dict[str, Any],
    game: dict[str, Any],
    lang: str,
    analysis_mode: str,
    intent: str,
    scope: str = "single",
) -> dict[str, Any]:
    game["requestedDate"] = report["requestedDate"]
    harden_game_injuries(game, tz=report.get("timezone"))
    roster_snapshots = fetch_game_rosters(game)
    game = apply_roster_guard(game, roster_snapshots, lang=lang)
    sources = ["espn"]
    freshness = "fresh"
    fallback_level = "none"
    should_refresh_nba_live = (
        analysis_mode in {"live", "post", "auto"}
        and (
            game.get("statusState") == "in"
            or not game.get("playTimeline")
            or not any((game.get("keyPlayers") or {}).values())
        )
    )
    if should_refresh_nba_live:
        augment_meta = augment_game_with_nba_live(game, requested_date=report["requestedDate"])
        if augment_meta.get("source"):
            sources.append("nba_live")
            freshness = augment_meta.get("dataFreshness", freshness)
            fallback_level = augment_meta.get("fallbackLevel", fallback_level)
    game["context"] = {
        "teamForm": build_team_form_context(game),
        "headToHead": build_head_to_head_context(
            game,
            away_schedule=_team_schedule_payload(game["away"].get("id")),
            home_schedule=_team_schedule_payload(game["home"].get("id")),
        ),
    }
    game["fullStats"] = build_full_stats(game, allowed_names=set(game.get("verifiedPlayers") or []))
    _sync_full_stats_scoreboard(game)
    attach_season_averages(game)
    game["meta"] = {
        "sections": {
            "analysis": {
                "sources": sources[:],
                "fallbackLevel": fallback_level,
            },
            "context": {
                "teamForm": {"source": "espn_summary+espn_team_statistics+espn_team_schedule"},
                "headToHead": {"source": (game["context"]["headToHead"].get("source") or "unavailable")},
            },
            "fullStats": {
                "source": game["fullStats"].get("source") or "unavailable",
            },
        }
    }
    game["gameContext"] = build_game_context(game)
    analysis = build_analysis(game, analysis_mode, report["labels"])
    if game.get("forceFallbackMatchup") and game.get("fallbackMatchup"):
        analysis["keyMatchup"] = game["fallbackMatchup"]
    elif not analysis.get("keyMatchup") and game.get("fallbackMatchup"):
        analysis["keyMatchup"] = game["fallbackMatchup"]
    digest = build_play_digest(game, lang=lang)
    scene = {
        "intent": intent,
        "scope": scope,
        "report": report,
        "game": game,
        "analysis": analysis,
        "digest": digest,
        "sources": sources,
        "fallbackLevel": fallback_level,
        "dataFreshness": freshness,
    }
    phase = analysis.get("mode") or analysis_mode
    if phase == "pregame":
        scene["pregame"] = build_pregame_view(game, analysis)
    elif phase == "live":
        scene["live"] = build_live_view(game, analysis)
    elif phase == "post":
        scene["postgame"] = build_postgame_view(game, analysis)
    return scene


def _team_schedule_payload(team_id: str | None) -> dict[str, Any]:
    if not team_id:
        return {}
    try:
        return fetch_team_schedule(team_id)["data"]
    except NBAReportError:
        return {}


def build_game_scene(
    *,
    tz: str | None,
    date_text: str | None,
    team: str,
    lang: str,
    analysis_mode: str,
    zh_locale: str | None = None,
) -> dict[str, Any]:
    report = build_scene_report(tz=tz, date_text=date_text, team=team, lang=lang, zh_locale=zh_locale)
    game = report["games"][0]
    intent = analysis_mode if analysis_mode in {"pregame", "live", "post"} else "scene"
    return finalize_scene_game(report=report, game=game, lang=lang, analysis_mode=analysis_mode, intent=intent)


def _pregame_labels(lang: str) -> dict[str, str]:
    if lang == "zh":
        return {
            "title_single": "NBA 赛前前瞻",
            "title_multi": "NBA 多场赛前前瞻",
            "info": "比赛信息",
            "lineups": "阵容与关键球员",
            "injuries": "伤病情况",
            "team_form": "球队状态",
            "prediction": "预测分析",
            "summary": "总结",
            "starters_pending": "首发尚未公布或当前免费数据源不可确认。",
            "none": "无",
            "all_games_none": "该日期没有可用的赛前比赛。",
        }
    return {
        "title_single": "NBA Pregame Preview",
        "title_multi": "NBA Multi-Game Pregame Preview",
        "info": "Game Info",
        "lineups": "Lineups and Key Players",
        "injuries": "Injuries",
        "team_form": "Team Form",
        "prediction": "Prediction",
        "summary": "Summary",
        "starters_pending": "Starting lineups are not yet confirmed or cannot be confirmed from the free data source.",
        "none": "None",
        "all_games_none": "No scheduled pregame matchups were found for the requested date.",
    }


def _format_average_line(stats: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("PTS", "REB", "AST", "STL", "BLK"):
        value = stats.get(key)
        if value is None:
            continue
        try:
            number = float(value)
        except (TypeError, ValueError):
            parts.append(f"{key} {value}")
            continue
        parts.append(f"{key} {int(number) if number.is_integer() else number:.1f}".replace(".0", ""))
    return ", ".join(parts)


def _localize_analysis_reason(reason: str, lang: str) -> str:
    text = str(reason or "")
    if lang != "zh" or not text:
        return text
    replacements = (
        (r"(\d+(?:\.\d+)?)\s+PTS\b", r"\1分"),
        (r"(\d+(?:\.\d+)?)\s+REB\b", r"\1板"),
        (r"(\d+(?:\.\d+)?)\s+AST\b", r"\1助"),
        (r"\s+\|\s+", " / "),
    )
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)
    return text


def render_pregame_scene_markdown(scene: dict[str, Any]) -> str:
    report = scene["report"]
    game = scene["game"]
    pregame = scene.get("pregame") or {}
    labels = _pregame_labels(report["lang"])
    lang = report["lang"]
    zh_locale = report.get("zhLocale")
    team_abbrs = [game["away"]["abbr"], game["home"]["abbr"]]
    lines = [
        f"# {labels['title_single']} ({report['requestedDate']})",
        f"> {report['labels']['timezone']}: {report['timezone']}",
        f"> {report['labels']['requested_date']}: {report['requestedDate']}",
        f"> {report['labels']['filter_team']}: {report['teamFilter']}",
        "",
        f"## {labels['info']}",
        "",
        *render_team_lines(game, report["labels"]),
        "",
        f"## {labels['lineups']}",
    ]
    lineups = pregame.get("lineups") or {}
    if lineups.get("startersConfirmed"):
        for abbr in (game["away"]["abbr"], game["home"]["abbr"]):
            starters = (lineups.get("starters") or {}).get(abbr) or []
            rendered = ", ".join(localize_player_list(starters, lang)) if starters else labels["none"]
            lines.append(f"- {_display_team(abbr, lang, zh_locale)} starters: {rendered}")
    else:
        lines.append(f"- {labels['starters_pending']}")
    season_averages = (game.get("gameContext") or {}).get("seasonAverages") or {}
    for abbr in (game["away"]["abbr"], game["home"]["abbr"]):
        key_players = (lineups.get("keyPlayers") or {}).get(abbr) or []
        if not key_players:
            continue
        lines.append(f"- {_display_team(abbr, lang, zh_locale)}:")
        for line in key_players[:3]:
            primary = extract_primary_name(line)
            averages = _format_average_line((season_averages.get(abbr) or {}).get(primary) or {})
            suffix = f" ({averages})" if averages else ""
            lines.append(f"  - {localize_player_line(line, lang)}{suffix}")
    lines.extend(["", f"## {labels['injuries']}"])
    injuries = pregame.get("injuries") or {}
    for abbr in (game["away"]["abbr"], game["home"]["abbr"]):
        items = (injuries.get("featuredByTeam") or {}).get(abbr) or (injuries.get("byTeam") or {}).get(abbr) or []
        localized = [localize_player_line(item, lang) for item in items]
        lines.append(f"- {_display_team(abbr, lang, zh_locale)}: {'; '.join(localized) if localized else labels['none']}")
    lines.extend(["", f"## {labels['team_form']}"])
    team_form = pregame.get("teamForm") or {}
    for abbr in (game["away"]["abbr"], game["home"]["abbr"]):
        snapshot = team_form.get(abbr) or {}
        if not snapshot:
            continue
        recent = (snapshot.get("recentForm") or {}).get("record") or "N/A"
        rest_days = (snapshot.get("schedule") or {}).get("restDays")
        rest_text = report["labels"]["pending"] if rest_days is None else str(rest_days)
        injury_count = (snapshot.get("injuries") or {}).get("count")
        base_sentence = _narrative_team_form(_display_team(abbr, lang, zh_locale), recent, rest_text, lang)
        if lang == "zh":
            suffix = f" 伤病人数 {injury_count if injury_count is not None else labels['none']}。"
        else:
            suffix = f" Injury count: {injury_count if injury_count is not None else labels['none']}."
        lines.append(f"- {base_sentence[:-1]}，{suffix.lstrip()}" if lang == "zh" else f"- {base_sentence[:-1]}. {suffix.strip()}")
    prediction = pregame.get("prediction") or {}
    lines.extend(["", f"## {labels['prediction']}"])
    if prediction.get("summary"):
        _append_unique_line(lines, _localize_team_mentions(prediction["summary"], lang=lang, zh_locale=zh_locale, team_abbrs=team_abbrs))
    if prediction.get("trend"):
        _append_unique_line(lines, _localize_team_mentions(prediction["trend"], lang=lang, zh_locale=zh_locale, team_abbrs=team_abbrs))
    if prediction.get("keyMatchup"):
        key_matchup = _localize_team_mentions(prediction["keyMatchup"], lang=lang, zh_locale=zh_locale, team_abbrs=team_abbrs)
        lines.append(f"- {'关键对位会落在' if lang == 'zh' else 'The matchup should turn on '}{key_matchup}{'' if lang == 'zh' else '.'}")
    if prediction.get("reasons"):
        localized_reasons = [
            _localize_team_mentions(reason, lang=lang, zh_locale=zh_locale, team_abbrs=team_abbrs)
            for reason in (prediction.get("reasons") or [])
        ]
        lines.append(f"- {_narrative_reasons(localized_reasons, lang=lang)}")
    localized_summary = _localize_team_mentions(pregame.get("summary") or labels["none"], lang=lang, zh_locale=zh_locale, team_abbrs=team_abbrs)
    lines.extend(["", f"## {labels['summary']}", "", f"- {localized_summary}", ""])
    lines.extend(
        [
            f"> sources: {', '.join(scene['sources'])}",
            f"> fallbackLevel: {scene['fallbackLevel']}",
            f"> dataFreshness: {scene['dataFreshness']}",
        ]
    )
    return "\n".join(lines)


def build_pregame_collection(
    *,
    tz: str | None,
    date_text: str | None,
    lang: str,
    matchups: list[dict[str, str]] | None = None,
    zh_locale: str | None = None,
) -> dict[str, Any]:
    report = build_scene_report(tz=tz, date_text=date_text, team=None, lang=lang, zh_locale=zh_locale)
    scenes: list[dict[str, Any]] = []
    scope = "multi_all"
    if matchups:
        scope = "multi_explicit"
        for matchup in matchups:
            resolved = resolve_requested_game(tz=tz, date_text=date_text, team=matchup["team"], opponent=matchup["opponent"])
            resolved_date = str(resolved.get("requestedDate") or report["requestedDate"])
            scene = build_game_scene(tz=tz, date_text=resolved_date, team=matchup["team"], lang=lang, analysis_mode="pregame", zh_locale=zh_locale)
            if not any(existing["game"]["eventId"] == scene["game"]["eventId"] for existing in scenes):
                scenes.append(scene)
    else:
        for game in report["games"]:
            if game.get("statusState") != "pre":
                continue
            scenes.append(build_game_scene(tz=tz, date_text=report["requestedDate"], team=game["away"]["abbr"], lang=lang, analysis_mode="pregame", zh_locale=zh_locale))
    return {
        "intent": "pregame",
        "scope": scope,
        "requestedDate": report["requestedDate"],
        "timezone": report["timezone"],
        "lang": lang,
        "zhLocale": report.get("zhLocale"),
        "games": scenes,
    }


def render_pregame_collection_markdown(payload: dict[str, Any]) -> str:
    labels = _pregame_labels(payload["lang"])
    lang = payload["lang"]
    zh_locale = payload.get("zhLocale")
    lines = [
        f"# {labels['title_multi']} ({payload['requestedDate']})",
        f"> {'请求方时区' if lang == 'zh' else 'Requestor Timezone'}: {payload['timezone']}",
        f"> {'请求日期' if lang == 'zh' else 'Requested Date'}: {payload['requestedDate']}",
        "",
    ]
    if not payload["games"]:
        lines.append(f"- {labels['all_games_none']}")
        return "\n".join(lines)
    for scene in payload["games"]:
        game = scene["game"]
        pregame = scene.get("pregame") or {}
        prediction = pregame.get("prediction") or {}
        team_abbrs = [game["away"]["abbr"], game["home"]["abbr"]]
        lines.append(f"## {format_matchup_display(game['away']['abbr'], game['home']['abbr'], lang=lang, zh_locale=zh_locale)}")
        lines.append(f"- {'时间' if lang == 'zh' else 'Time'}: {game['startTimeLocal']}")
        if game.get("venue"):
            lines.append(f"- {'球馆' if lang == 'zh' else 'Venue'}: {game['venue']}")
        for abbr in (game["away"]["abbr"], game["home"]["abbr"]):
            snapshot = (pregame.get("teamForm") or {}).get(abbr) or {}
            if snapshot:
                recent = (snapshot.get("recentForm") or {}).get("record") or "N/A"
                injury_count = (snapshot.get("injuries") or {}).get("count")
                form_sentence = _narrative_team_form(_display_team(abbr, lang, zh_locale), recent, labels["pending"] if lang == "zh" else "Pending", lang)
                extra = f"伤病人数 {injury_count if injury_count is not None else labels['none']}。" if lang == "zh" else f"Injury count: {injury_count if injury_count is not None else labels['none']}."
                lines.append(f"- {form_sentence} {extra}" if lang == "en" else f"- {form_sentence[:-1]}，{extra}")
        for abbr in (game["away"]["abbr"], game["home"]["abbr"]):
            injuries = pregame.get("injuries") or {}
            items = (injuries.get("compactByTeam") or {}).get(abbr) or (injuries.get("featuredByTeam") or {}).get(abbr) or (injuries.get("byTeam") or {}).get(abbr) or []
            if items:
                localized = [localize_player_line(item, lang) for item in items[:2]]
                if lang == "zh":
                    lines.append(f"- {_display_team(abbr, lang, zh_locale)}的伤病关注点是 {'; '.join(localized)}。")
                else:
                    lines.append(f"- Injury watch for {_display_team(abbr, lang, zh_locale)} centers on {'; '.join(localized)}.")
        if prediction.get("summary"):
            _append_unique_line(lines, _localize_team_mentions(prediction["summary"], lang=lang, zh_locale=zh_locale, team_abbrs=team_abbrs))
        if prediction.get("keyMatchup"):
            key_matchup = _localize_team_mentions(prediction["keyMatchup"], lang=lang, zh_locale=zh_locale, team_abbrs=team_abbrs)
            lines.append(f"- {'关键对位会落在' if lang == 'zh' else 'The matchup should turn on '}{key_matchup}{'' if lang == 'zh' else '.'}")
        if pregame.get("summary"):
            _append_unique_line(lines, _localize_team_mentions(pregame["summary"], lang=lang, zh_locale=zh_locale, team_abbrs=team_abbrs))
        lines.append("")
    return "\n".join(lines).rstrip()


def render_game_scene_markdown(scene: dict[str, Any]) -> str:
    if scene.get("intent") == "pregame":
        return render_pregame_scene_markdown(scene)
    if scene.get("intent") == "live":
        return render_live_scene_markdown(scene)
    if scene.get("intent") == "post":
        return render_postgame_scene_markdown(scene)
    # auto 模式：根据实际比赛状态自动选择渲染路径
    status_state = (scene.get("game") or {}).get("statusState") or ""
    if status_state == "in":
        return render_live_scene_markdown(scene)
    if status_state == "post":
        return render_postgame_scene_markdown(scene)
    # 赛前或状态未知，走 pregame
    return render_pregame_scene_markdown(scene)


def render_day_scene(*, tz: str | None, date_text: str | None, lang: str, zh_locale: str | None = None) -> str:
    return render_day_view_markdown(build_day_view(tz=tz, date_text=date_text, lang=lang, zh_locale=zh_locale))


def scene_payload(scene: dict[str, Any]) -> dict[str, Any]:
    game = scene["game"]
    payload = {
        "intent": scene.get("intent") or (scene.get("analysis", {}).get("mode") or "scene"),
        "scope": scene.get("scope") or "single",
        "eventId": game["eventId"],
        "requestedDate": scene["report"]["requestedDate"],
        "timezone": scene["report"]["timezone"],
        "lang": scene["report"]["lang"],
        "zhLocale": scene["report"].get("zhLocale"),
        "statusState": game["statusState"],
        "teams": {
            "away": game["away"],
            "home": game["home"],
        },
        "verifiedPlayers": game.get("verifiedPlayers") or [],
        "rosters": game.get("rosters") or {},
        "analysis": scene["analysis"],
        "digest": scene["digest"],
        "gameContext": game.get("gameContext") or {},
        "context": game.get("context") or {},
        "fullStats": game.get("fullStats") or {"available": False, "teams": {}, "players": {}},
        "meta": game.get("meta") or {"sections": {}},
        "sources": scene["sources"],
        "fallbackLevel": scene["fallbackLevel"],
        "dataFreshness": scene["dataFreshness"],
    }
    if scene.get("pregame"):
        payload["pregame"] = scene["pregame"]
    if scene.get("live"):
        payload["live"] = scene["live"]
    if scene.get("postgame"):
        payload["postgame"] = scene["postgame"]
    return payload
