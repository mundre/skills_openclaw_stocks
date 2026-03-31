#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request


def geocode_address(address: str):
    q = urllib.parse.urlencode({"q": address, "format": "json", "limit": 1})
    url = f"https://nominatim.openstreetmap.org/search?{q}"
    req = urllib.request.Request(url, headers={"User-Agent": "openclaw-broadbandmap-skill/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read().decode("utf-8"))
    if not data:
        raise ValueError("No geocoding result found for address")
    return float(data[0]["lat"]), float(data[0]["lon"])


def collect_values(node, wanted_keys, out):
    if isinstance(node, dict):
        for k, v in node.items():
            if k.lower() in wanted_keys:
                if isinstance(v, list):
                    for item in v:
                        out.add(str(item))
                else:
                    out.add(str(v))
            collect_values(v, wanted_keys, out)
    elif isinstance(node, list):
        for item in node:
            collect_values(item, wanted_keys, out)


def print_report(result):
    inp = result.get("input", {})
    summary = result.get("summary", {})
    resp = result.get("response") or {}

    print("Cell Coverage Report")
    print("====================")
    print(f"Location: lat={inp.get('lat')} lng={inp.get('lon')}")

    if result.get("errors"):
        print("\nErrors:")
        for e in result["errors"]:
            print(f"- {e}")
        return

    cov = resp.get("coverage") if isinstance(resp, dict) else None
    if isinstance(cov, list) and cov:
        print(f"\nCoverage entries: {len(cov)}")
        for row in cov:
            network = row.get("network") or row.get("network_slug") or "Unknown"
            tech = row.get("technology") or "Unknown tech"
            dbm = row.get("rsrp_dbm")
            level = row.get("signal_level")
            parts = [f"{network}", f"{tech}"]
            if dbm is not None:
                parts.append(f"{dbm} dBm")
            if level:
                parts.append(level)
            print("- " + " · ".join(parts))

    providers = summary.get("providers") or []
    technologies = summary.get("technologies") or []
    notes = summary.get("notes") or []

    if providers:
        print("\nProviders:")
        for p in providers:
            print(f"- {p}")
    if technologies:
        print("\nTechnologies:")
        for t in technologies:
            print(f"- {t}")
    if notes:
        print("\nNotes:")
        for n in notes:
            print(f"- {n}")


def main():
    p = argparse.ArgumentParser(description="Lookup cell coverage for a location via configurable BroadbandMap API")
    p.add_argument("--address", help="Address or place name to geocode")
    p.add_argument("--lat", type=float)
    p.add_argument("--lon", type=float)
    p.add_argument("--base-url", default=os.getenv("BROADBANDMAP_API_BASE", "https://broadbandmap.com"))
    p.add_argument("--endpoint", default=os.getenv("BROADBANDMAP_API_ENDPOINT", "/api/v1/location/cell"))
    p.add_argument("--param-lat", default="lat")
    p.add_argument("--param-lon", default="lng")
    p.add_argument("--api-key", default=os.getenv("BROADBANDMAP_API_KEY"))
    p.add_argument("--network", help="Filter network slug (att, verizon, t-mobile, us-cellular, dish, gci, cellcom, c-spire)")
    p.add_argument("--tech", help="Filter technology generation (4g or 5g)")
    p.add_argument("--format", choices=["json", "report"], default="json", help="Output format")
    args = p.parse_args()

    result = {"input": {}, "request": {}, "response": None, "summary": {"providers": [], "technologies": [], "notes": []}, "errors": []}

    try:
        lat, lon = (args.lat, args.lon)
        if args.address and (lat is None or lon is None):
            lat, lon = geocode_address(args.address)
        if lat is None or lon is None:
            raise ValueError("Provide --address or both --lat and --lon")

        result["input"] = {"address": args.address, "lat": lat, "lon": lon}

        base = args.base_url.rstrip("/")
        endpoint = args.endpoint if args.endpoint.startswith("/") else f"/{args.endpoint}"
        params = {args.param_lat: lat, args.param_lon: lon}
        if args.network:
            params["network"] = args.network
        if args.tech:
            params["tech"] = args.tech
        query = urllib.parse.urlencode(params)
        url = f"{base}{endpoint}?{query}"

        headers = {"Accept": "application/json", "User-Agent": "openclaw-broadbandmap-skill/1.0"}
        if args.api_key:
            headers["Authorization"] = f"Bearer {args.api_key}"
            headers["x-api-key"] = args.api_key

        result["request"] = {"url": url, "params": params}

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode("utf-8", errors="replace")
            content_type = r.headers.get("content-type", "")

        if "json" in content_type.lower():
            parsed = json.loads(body)
            result["response"] = parsed
        else:
            try:
                parsed = json.loads(body)
                result["response"] = parsed
            except Exception:
                parsed = None
                result["response"] = {"raw": body}
                result["summary"]["notes"].append("Response was not valid JSON; returned raw body.")

        if parsed is not None:
            providers = set()
            tech = set()
            collect_values(parsed, {"providers", "provider", "carriers", "carrier", "operators", "operator", "networkproviders", "network", "networks"}, providers)
            collect_values(parsed, {"technologies", "technology", "networktypes", "networktype", "radio", "radios", "bands"}, tech)
            # Deduplicate case-insensitively while preferring richer labels (e.g., "AT&T" over "att")
            canonical = {}
            for p in providers:
                key = str(p).strip().lower()
                if not key:
                    continue
                current = canonical.get(key)
                if current is None or (len(str(p)) > len(str(current))):
                    canonical[key] = str(p)
            result["summary"]["providers"] = sorted(canonical.values())
            result["summary"]["technologies"] = sorted(tech)
            if not providers and not tech:
                result["summary"]["notes"].append("No standard provider/technology fields detected; inspect raw response.")

    except Exception as e:
        result["errors"].append(str(e))

    if args.format == "report":
        print_report(result)
    else:
        print(json.dumps(result, indent=2))
    return 0 if not result["errors"] else 1


if __name__ == "__main__":
    sys.exit(main())
