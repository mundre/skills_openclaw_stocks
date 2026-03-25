#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ALLOWED_NETLOC = 'help.mikrotik.com'
ALLOWED_SCHEMES = {'https'}


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_script = False
        self.in_style = False
        self.title = ''
        self._in_title = False
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        tag = tag.lower()
        if tag == 'script':
            self.in_script = True
        elif tag == 'style':
            self.in_style = True
        elif tag == 'title':
            self._in_title = True
        elif tag in {'p', 'div', 'section', 'article', 'li', 'tr', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
            self.parts.append('\n')

    def handle_endtag(self, tag: str):
        tag = tag.lower()
        if tag == 'script':
            self.in_script = False
        elif tag == 'style':
            self.in_style = False
        elif tag == 'title':
            self._in_title = False
        elif tag in {'p', 'div', 'section', 'article', 'li', 'tr', 'br', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
            self.parts.append('\n')

    def handle_data(self, data: str):
        if self.in_script or self.in_style:
            return
        text = html.unescape(data)
        if self._in_title:
            self.title += text
        self.parts.append(text)

    def text(self) -> str:
        text = ''.join(self.parts)
        text = re.sub(r'\r', '', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        lines = [line.strip() for line in text.splitlines()]
        return '\n'.join(line for line in lines if line).strip()


def default_root() -> Path:
    return Path.cwd() / '.MikroTik-Encyclopedia'


def validate_url(url: str) -> urllib.parse.ParseResult:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError(f'Only {sorted(ALLOWED_SCHEMES)} URLs are supported')
    if parsed.netloc != ALLOWED_NETLOC:
        raise ValueError(f'Only {ALLOWED_NETLOC} URLs are supported')
    return parsed


def build_output_path(root: Path, parsed: urllib.parse.ParseResult) -> Path:
    path = parsed.path or '/'
    if path.endswith('/'):
        path += 'index'
    safe_path = Path(path.lstrip('/'))
    return root / 'docs' / parsed.netloc / safe_path.with_suffix('.md')


def fetch_html(url: str) -> str:
    req = urllib.request.Request(url, headers={'User-Agent': 'MikroTik-Encyclopedia/1.0'})
    with urllib.request.urlopen(req, timeout=20) as resp:
        charset = resp.headers.get_content_charset() or 'utf-8'
        return resp.read().decode(charset, errors='replace')


def main() -> int:
    parser = argparse.ArgumentParser(description='Fetch and cache a MikroTik docs page into .MikroTik-Encyclopedia.')
    parser.add_argument('--url', required=True, help='help.mikrotik.com/docs URL to cache')
    parser.add_argument('--root', default=str(default_root()), help='MikroTik Encyclopedia data root (default: <cwd>/.MikroTik-Encyclopedia)')
    args = parser.parse_args()

    parsed = validate_url(args.url)
    root = Path(args.root).expanduser().resolve()
    html_body = fetch_html(args.url)
    extractor = TextExtractor()
    extractor.feed(html_body)
    title = extractor.title.strip() or Path(parsed.path).name or 'MikroTik Doc'
    body = extractor.text()
    out = build_output_path(root, parsed)
    out.parent.mkdir(parents=True, exist_ok=True)
    content = (
        f'# {title}\n\n'
        f'- Source: {args.url}\n'
        f'- Cached at: {datetime.now(timezone.utc).isoformat()}\n\n'
        '## Cached text\n\n'
        f'{body}\n'
    )
    out.write_text(content, encoding='utf-8')
    print(out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
