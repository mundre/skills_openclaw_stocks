#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlencode, urlparse, parse_qs
import subprocess


def fetch_json(url: str) -> dict:
    proc = subprocess.run(
        ["curl", "-fsSL", url],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"curl failed: {proc.returncode}")
    return json.loads(proc.stdout)


def download_file(url: str, out_path: Path) -> None:
    proc = subprocess.run(
        ["curl", "-fsSL", url, "-o", str(out_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"curl failed: {proc.returncode}")


def parse_unknown_args(unknown: list[str]) -> dict[str, str]:
    params: dict[str, str] = {}
    i = 0
    while i < len(unknown):
        token = unknown[i]
        if not token.startswith("--"):
            raise ValueError(f"Unexpected token: {token}")
        key = token[2:]
        if not key:
            raise ValueError("Empty parameter name")
        if i + 1 >= len(unknown) or unknown[i + 1].startswith("--"):
            params[key] = "1"
            i += 1
            continue
        params[key] = unknown[i + 1]
        i += 2
    return params


def parse_search_url(search_url: str) -> dict[str, str]:
    parsed = urlparse(search_url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    params: dict[str, str] = {}
    for key, values in query.items():
        if not values:
            continue
        params[key] = values[-1]
    if "top" in params and "topRange" not in params:
        params["topRange"] = params.pop("top")
    return params


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch download wallpapers from Wallhaven API")
    parser.add_argument("--apikey", default=os.environ.get("WALLHAVEN_API_KEY", ""))
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--out", required=True)
    parser.add_argument("--base-url", default="https://wallhaven.cc/api/v1/search")
    parser.add_argument("--search-url", default="")
    parser.add_argument("--sleep-ms", type=int, default=300)

    args, unknown = parser.parse_known_args()

    try:
        params = parse_unknown_args(unknown)
    except ValueError as e:
        print(f"[error] {e}", file=sys.stderr)
        return 2

    url_params: dict[str, str] = {}
    if args.search_url:
        try:
            url_params = parse_search_url(args.search_url)
        except Exception as e:
            print(f"[error] invalid --search-url: {e}", file=sys.stderr)
            return 2

    params = {**url_params, **params}

    if args.apikey and "apikey" not in params:
        params["apikey"] = args.apikey

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    requested = max(args.count, 0)
    if requested == 0:
        print("downloaded=0")
        return 0

    page = int(params.get("page", "1"))
    downloaded = 0
    items = []
    seen_ids = set()

    last_page = None

    while downloaded < requested:
        query = dict(params)
        query["page"] = str(page)
        url = f"{args.base_url}?{urlencode(query)}"

        try:
            payload = fetch_json(url)
        except Exception as e:
            print(f"[error] request failed on page {page}: {e}", file=sys.stderr)
            return 1

        data = payload.get("data") or []
        meta = payload.get("meta") or {}
        if last_page is None:
            last_page = meta.get("last_page")

        if not data:
            break

        for entry in data:
            if downloaded >= requested:
                break
            wid = entry.get("id")
            img_url = entry.get("path")
            if not wid or not img_url:
                continue
            if wid in seen_ids:
                continue
            seen_ids.add(wid)
            ext = img_url.rsplit(".", 1)[-1].lower()
            if ext not in {"jpg", "jpeg", "png", "webp"}:
                ext = "jpg"
            fname = f"{downloaded+1:02d}-wallhaven-{wid}.{ext}"
            target = out_dir / fname
            try:
                download_file(img_url, target)
            except Exception as e:
                print(f"[warn] skip {wid}: {e}", file=sys.stderr)
                continue
            downloaded += 1
            items.append({
                "index": downloaded,
                "id": wid,
                "url": entry.get("url"),
                "path": img_url,
                "file": str(target),
                "purity": entry.get("purity"),
                "category": entry.get("category"),
            })

        if last_page is not None and page >= int(last_page):
            break
        page += 1
        time.sleep(max(args.sleep_ms, 0) / 1000)

    manifest = {
        "requested": requested,
        "downloaded": downloaded,
        "params": params,
        "last_page": last_page,
        "items": items,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"downloaded={downloaded}")
    print(f"manifest={out_dir / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
