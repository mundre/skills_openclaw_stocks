#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


CLAIM_LINE_RE = re.compile(r'^- \[(C\d+(?:\.\d+)*)\]\[([^\]]+)\] (.*)$')


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))


def clean_latex_text(text: str) -> str:
    text = text.replace('~', ' ')
    text = re.sub(r'\\begin\{[^}]+\}', ' ', text)
    text = re.sub(r'\\end\{[^}]+\}', ' ', text)
    text = re.sub(r'\\(cite|ref|label|url|footnote)\{[^}]*\}', ' ', text)
    text = re.sub(r'\\textbf\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\textit\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\emph\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\[a-zA-Z]+\*?(?:\[[^\]]*\])?\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\[a-zA-Z]+\*?', ' ', text)
    text = text.replace('{', '').replace('}', '')
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def section_label(paragraph: dict) -> str:
    section_path = paragraph.get('section_path') or []
    if section_path:
        return ' > '.join(section_path)
    kind = paragraph.get('kind') or ''
    if kind == 'abstract':
        return 'Abstract'
    return 'Front matter / unspecified'


def start_excerpt(text: str, n_words: int = 14) -> str:
    words = clean_latex_text(text).split()
    return ' '.join(words[:n_words])


def end_excerpt(text: str, n_words: int = 14) -> str:
    words = clean_latex_text(text).split()
    return ' '.join(words[-n_words:])


def main() -> None:
    parser = argparse.ArgumentParser(description='Render inline original-paragraph locators into report.md')
    parser.add_argument('--report', required=True)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--paragraphs', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    report_text = Path(args.report).read_text(encoding='utf-8')
    manifest = load_json(Path(args.manifest))
    paragraphs = load_json(Path(args.paragraphs))

    para_map = {item['paragraph_id']: item for item in paragraphs.get('paragraphs', []) if isinstance(item, dict) and item.get('paragraph_id')}
    claim_map = {item['claim_id']: item for item in manifest.get('claims', []) if isinstance(item, dict) and item.get('claim_id')}

    new_lines: list[str] = []
    for line in report_text.splitlines():
        new_lines.append(line)
        match = CLAIM_LINE_RE.match(line)
        if not match:
            continue
        claim_id = match.group(1)
        claim = claim_map.get(claim_id)
        if not claim:
            continue
        evidences = claim.get('evidences', [])
        for idx, evidence in enumerate(evidences, start=1):
            paragraph = para_map.get(evidence.get('paragraph_id'))
            if not paragraph:
                continue
            sec = section_label(paragraph)
            page = evidence.get('page')
            page_text = f'，PDF 第 {page} 页' if page else ''
            new_lines.append(
                f'  - 原文定位 {idx}：`{paragraph["source_path"]}` → `{sec}`，'
                f'行 {paragraph["line_start"]}–{paragraph["line_end"]}{page_text}；'
                f'从“{start_excerpt(paragraph["text"])}”到“{end_excerpt(paragraph["text"])}”。'
            )

    Path(args.output).write_text('\n'.join(new_lines), encoding='utf-8')


if __name__ == '__main__':
    main()
