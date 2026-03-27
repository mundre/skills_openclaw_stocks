#!/usr/bin/env python3
"""
Conference Search Script

Two-step chained workflow:
  Step 1 — query conferences (SkillConferenceSearch)
  Step 2 — query presentations/abstracts (SkillConferencePresentationSearch)

When both --conference-params and --presentation-params are supplied (chained mode),
the top conference_name from Step 1 is automatically injected into Step 2.

Usage:
  # Chained (recommended): search conferences then presentations
  python scripts/search.py \
      --conference-params '{"series_name": "ASCO", "conference_start_date": "2024-01-01"}' \
      --presentation-params '{"targets": ["PD-1"]}'

  # Step 1 only
  python scripts/search.py \
      --conference-params '{"series_area": ["oncology"], "conference_location": "Chicago"}' \
      --step conference

  # Step 2 only (conference_name already known)
  python scripts/search.py \
      --presentation-params '{"conference_name": "2024 ASCO Annual Meeting", "drugs": ["pembrolizumab"]}' \
      --step presentation

  # Raw JSON output
  python scripts/search.py --conference-params '{"series_name": "ESMO"}' --step conference --raw

  # Save to file
  python scripts/search.py \
      --conference-params '{"series_name": "ASCO"}' \
      --presentation-params '{"diseases": ["NSCLC"]}' \
      --output results.txt

Environment variables:
  NOAH_API_TOKEN  — API authentication token (required)
  NOAH_API_URL    — Base URL (optional, defaults to http://localhost:8000)
"""

import argparse
import json
import os
import sys

try:
    import requests
except ImportError:
    print("[ERROR] Missing dependency: requests\nInstall it with: pip install requests", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def _post(endpoint, payload):
    api_url = os.environ.get("NOAH_API_URL", "https://noah.bio").strip()
    api_token = os.environ.get("NOAH_API_TOKEN", "").strip()

    url = f"{api_url}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}",
    }
    print(f"[INFO] Endpoint: {url}", file=sys.stderr)
    print(f"[INFO] Query payload:\n{json.dumps(payload, indent=2)}", file=sys.stderr)
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
    except requests.exceptions.ConnectionError as e:
        raise ConnectionError(f"Cannot connect to API server: {url}\nDetails: {e}")
    except requests.exceptions.Timeout:
        raise TimeoutError("Request timed out (30s). Check your network or API server status.")
    except requests.exceptions.HTTPError:
        body = ""
        try:
            body = resp.text
        except Exception:
            pass
        raise RuntimeError(
            f"API returned HTTP {resp.status_code}\n"
            f"Response body: {body}"
        )
    return resp.json()


# ---------------------------------------------------------------------------
# Step 1 -- Conference Search
# ---------------------------------------------------------------------------

CONFERENCE_DEFAULTS = {
    "conference_name": "",
    "conference_start_date": "",
    "conference_end_date": "",
    "conference_location": "",
    "series_name": "",
    "series_organization": "",
    "series_area": [],
    "from_n": 0,
    "size": 5,
}

CONFERENCE_ENDPOINT = "/api/skills/conference_search/"


def _build_conference_payload(user_params):
    payload = CONFERENCE_DEFAULTS.copy()
    for key, value in user_params.items():
        if key in payload:
            payload[key] = value
        else:
            print(f"[WARN] Unknown conference field ignored: {key}", file=sys.stderr)
    return payload


def search_conferences(params):
    return _post(CONFERENCE_ENDPOINT, _build_conference_payload(params))


def format_conferences(data):
    lines = []
    results = data.get("results", [])
    from_n = data.get("from_n", 0)
    lines.append(f"=== Conferences: {len(results)} found (offset: {from_n}) ===\n")

    if not results:
        lines.append("No conferences found. Try:")
        lines.append("  - Shorter partial name (e.g. 'ASCO' not full title)")
        lines.append("  - Remove date filters")
        lines.append("  - Broaden series_area")
        return "\n".join(lines)

    for i, c in enumerate(results, 1):
        name = c.get("conference_name") or c.get("series_name") or "(no name)"
        abbr = c.get("conference_abbreviation", "")
        lines.append(f"[{i}] {name}" + (f" ({abbr})" if abbr else ""))

        if c.get("conference_website"):
            lines.append(f"  Website    : {c['conference_website']}")

        start, end = c.get("conference_start_date", ""), c.get("conference_end_date", "")
        if start or end:
            lines.append(f"  Date       : {start}" + (f" -> {end}" if end and end != start else ""))

        if c.get("conference_location"):
            lines.append(f"  Location   : {c['conference_location']}")

        series = c.get("series_name", "")
        series_abbr = c.get("series_abbreviation", "")
        if series:
            lines.append(f"  Series     : {series}" + (f" ({series_abbr})" if series_abbr else ""))

        if c.get("series_organization"):
            lines.append(f"  Organizer  : {c['series_organization']}")

        if c.get("series_area"):
            lines.append(f"  Area       : {c['series_area']}")

        desc = c.get("conferene_description") or c.get("conference_description", "")
        if desc:
            lines.append(f"  Description: {desc[:200]}" + ("..." if len(desc) > 200 else ""))

        lines.append("")

    top_name = results[0].get("conference_name", "")
    if top_name:
        lines.append(
            f"-> Next step: run with --presentation-params '{{\"conference_name\": \"{top_name}\", ...}}'"
        )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Step 2 -- Presentation Search
# ---------------------------------------------------------------------------

PRESENTATION_DEFAULTS = {
    "authors": [],
    "institutions": [],
    "drugs": [],
    "diseases": [],
    "targets": [],
    "conference_name": "",
    "series_name": "",
    "from_n": 0,
    "size": 5,
}

PRESENTATION_ENDPOINT = "/api/skills/conference_presentation_search/"


def _build_presentation_payload(user_params):
    payload = PRESENTATION_DEFAULTS.copy()
    for key, value in user_params.items():
        if key in payload:
            payload[key] = value
        else:
            print(f"[WARN] Unknown presentation field ignored: {key}", file=sys.stderr)
    return payload


def search_presentations(params):
    return _post(PRESENTATION_ENDPOINT, _build_presentation_payload(params))


def format_presentations(data):
    lines = []
    results = data.get("results", [])
    from_n = data.get("from_n", 0)
    lines.append(f"=== Presentations: {len(results)} found (offset: {from_n}) ===\n")

    if not results:
        lines.append("No presentations found. Try:")
        lines.append("  - More general disease / drug terms")
        lines.append("  - Use series_name instead of conference_name")
        lines.append("  - Verify conference_name exactly matches a conference-search result")
        return "\n".join(lines)

    for i, p in enumerate(results, 1):
        lines.append(f"[{i}] {p.get('presentation_title') or '(no title)'}")

        if p.get("session_title"):
            lines.append(f"  Session    : {p['session_title']}")

        conf = p.get("conference_name") or p.get("series_name", "")
        if conf:
            lines.append(f"  Conference : {conf}")

        if p.get("presentation_website"):
            lines.append(f"  Link       : {p['presentation_website']}")

        author = p.get("main_author", "")
        inst = p.get("main_author_institution", "")
        if author:
            lines.append(f"  Presenter  : {author}" + (f" ({inst})" if inst else ""))

        for label, field in [("Drug(s)", "drugs"), ("Disease(s)", "diseases"), ("Target(s)", "targets")]:
            val = p.get(field, "")
            if val:
                if isinstance(val, list):
                    val = ", ".join(val)
                lines.append(f"  {label:<11}: {val}")

        for label, field, limit in [
            ("Abstract", "abstract", 300),
            ("Design", "design", 200),
            ("Efficacy", "efficacy", 200),
            ("Safety", "safety", 200),
        ]:
            val = p.get(field, "")
            if val:
                lines.append(f"  {label:<11}: {val[:limit]}" + ("..." if len(val) > limit else ""))

        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Chained workflow
# ---------------------------------------------------------------------------

def run_chained(conference_params, presentation_params, raw):
    conf_result = search_conferences(conference_params)
    conf_output = json.dumps(conf_result, indent=2) if raw else format_conferences(conf_result)

    conf_results = conf_result.get("results", [])
    if conf_results and not presentation_params.get("conference_name"):
        top_name = conf_results[0].get("conference_name", "")
        if top_name:
            presentation_params["conference_name"] = top_name
            print(f"[INFO] Auto-injected conference_name: {top_name}", file=sys.stderr)

    pres_result = search_presentations(presentation_params)
    pres_output = json.dumps(pres_result, indent=2) if raw else format_presentations(pres_result)

    separator = "\n" + "=" * 60 + "\n\n"
    return f"{conf_output}{separator}{pres_output}"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _load_params_from_file(path, label):
    try:
        with open(path, "r", encoding="utf-8") as f:
            params = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Parameter file not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] {label} file is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    return params


def _load_params_from_string(payload, label):
    try:
        return json.loads(payload)
    except json.JSONDecodeError as e:
        print(f"[ERROR] {label} is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)


def _resolve_params(params, params_file, label):
    if params:
        return _load_params_from_string(params, label)
    if params_file:
        return _load_params_from_file(params_file, label)
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Conference + Presentation two-step search",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Chained: ASCO 2024 PD-1 data
  python scripts/search.py \
      --conference-params '{"series_name": "ASCO", "conference_start_date": "2024-01-01", "conference_end_date": "2024-12-31"}' \
      --presentation-params '{"targets": ["PD-1"]}'

  # Conferences only
  python scripts/search.py \
      --conference-params '{"series_area": ["oncology"], "conference_location": "Chicago"}' \
      --step conference

  # Presentations only
  python scripts/search.py \
      --presentation-params '{"drugs": ["pembrolizumab"], "diseases": ["lung cancer"], "series_name": "ESMO"}' \
      --step presentation

  # Raw JSON + save to file
  python scripts/search.py \
      --conference-params '{"series_name": "ASCO"}' \
      --presentation-params '{"diseases": ["NSCLC"]}' \
      --raw --output results.json
        """,
    )
    parser.add_argument(
        "--conference-params",
        type=str,
        default=None,
        help="Conference query parameters as a JSON string",
    )
    parser.add_argument(
        "--conference-params-file",
        type=str,
        default=None,
        help="Path to a JSON file containing conference query parameters",
    )
    parser.add_argument(
        "--presentation-params",
        type=str,
        default=None,
        help="Presentation query parameters as a JSON string",
    )
    parser.add_argument(
        "--presentation-params-file",
        type=str,
        default=None,
        help="Path to a JSON file containing presentation query parameters",
    )
    parser.add_argument(
        "--step",
        choices=["conference", "presentation"],
        default=None,
        help="Run only one step. Omit to run chained (requires both conference and presentation params).",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Print raw JSON response instead of formatted output",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Save results to the specified file path",
    )

    args = parser.parse_args()

    conf_params = _resolve_params(
        args.conference_params,
        args.conference_params_file,
        "--conference-params",
    )
    pres_params = _resolve_params(
        args.presentation_params,
        args.presentation_params_file,
        "--presentation-params",
    )

    if args.step == "conference" and not conf_params:
        print("[ERROR] --step conference requires --conference-params or --conference-params-file", file=sys.stderr)
        sys.exit(1)
    if args.step == "presentation" and not pres_params:
        print("[ERROR] --step presentation requires --presentation-params or --presentation-params-file", file=sys.stderr)
        sys.exit(1)
    if args.step is None and not (conf_params and pres_params):
        print(
            "[ERROR] Chained mode requires both conference and presentation params.\n"
            "Use --step conference or --step presentation for single-step mode.",
            file=sys.stderr,
        )
        sys.exit(1)

    if conf_params is not None and not isinstance(conf_params, dict):
        print("[ERROR] Conference parameters must be a JSON object.", file=sys.stderr)
        sys.exit(1)
    if pres_params is not None and not isinstance(pres_params, dict):
        print("[ERROR] Presentation parameters must be a JSON object.", file=sys.stderr)
        sys.exit(1)

    try:
        if args.step == "conference":
            result = search_conferences(conf_params)
            output_text = json.dumps(result, indent=2) if args.raw else format_conferences(result)

        elif args.step == "presentation":
            result = search_presentations(pres_params)
            output_text = json.dumps(result, indent=2) if args.raw else format_presentations(result)

        else:
            output_text = run_chained(conf_params, pres_params, args.raw)

    except (EnvironmentError, ConnectionError, TimeoutError, RuntimeError) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_text)
        print(f"[INFO] Results saved to: {args.output}", file=sys.stderr)
    else:
        print(output_text)


if __name__ == "__main__":
    main()
