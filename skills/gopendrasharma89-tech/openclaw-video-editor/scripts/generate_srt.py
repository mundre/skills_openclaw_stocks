#!/usr/bin/env python3
"""
Generate SRT/ASS/VTT subtitle files from transcription JSON output.

Usage:
  python3 generate_srt.py <transcript.json> <output.srt> [options]

Supported input formats: Whisper, Deepgram, AssemblyAI, generic {word,start,end} lists.
Supported output formats: .srt, .ass, .vtt (auto-detected from extension).
"""

import json
import sys
import argparse
from pathlib import Path


def format_srt_ts(seconds: float) -> str:
    """Convert seconds to SRT timestamp (HH:MM:SS,mmm)."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def format_vtt_ts(seconds: float) -> str:
    """Convert seconds to VTT timestamp (HH:MM:SS.mmm)."""
    return format_srt_ts(seconds).replace(",", ".")


def format_ass_ts(seconds: float) -> str:
    """Convert seconds to ASS timestamp (H:MM:SS.cc)."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int((seconds % 1) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def chunk_words(words: list, max_chars: int = 42, max_words: int = 8) -> list:
    """Group words into subtitle chunks based on character and word limits."""
    chunks = []
    current_words = []
    current_text = ""
    chunk_start = None

    for word_info in words:
        word = word_info.get("word", word_info.get("text", "")).strip()
        start = word_info.get("start", 0)
        end = word_info.get("end", start + 0.5)

        if not word:
            continue

        test_text = f"{current_text} {word}".strip() if current_text else word

        if (len(test_text) > max_chars or len(current_words) >= max_words) and current_words:
            chunks.append({
                "text": current_text,
                "start": chunk_start,
                "end": current_words[-1].get("end", chunk_start + 1)
            })
            current_words = []
            current_text = ""
            chunk_start = None

        if chunk_start is None:
            chunk_start = start

        current_words.append(word_info)
        current_text = f"{current_text} {word}".strip() if current_text else word

    if current_words:
        chunks.append({
            "text": current_text,
            "start": chunk_start,
            "end": current_words[-1].get("end", chunk_start + 1)
        })

    return chunks


def generate_srt(chunks: list) -> str:
    lines = []
    for i, c in enumerate(chunks, 1):
        lines.append(f"{i}")
        lines.append(f"{format_srt_ts(c['start'])} --> {format_srt_ts(c['end'])}")
        lines.append(c["text"])
        lines.append("")
    return "\n".join(lines)


def generate_vtt(chunks: list) -> str:
    lines = ["WEBVTT", ""]
    for i, c in enumerate(chunks, 1):
        lines.append(f"{i}")
        lines.append(f"{format_vtt_ts(c['start'])} --> {format_vtt_ts(c['end'])}")
        lines.append(c["text"])
        lines.append("")
    return "\n".join(lines)


def generate_ass(chunks: list, font: str = "Arial", fontsize: int = 24,
                 primary: str = "&H00FFFFFF", outline: str = "&H00000000") -> str:
    header = f"""[Script Info]
Title: Auto-generated subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font},{fontsize},{primary},&H000000FF,{outline},&H80000000,-1,0,0,0,100,100,0,0,1,2,1,2,20,20,50,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"""
    lines = [header]
    for c in chunks:
        lines.append(f"Dialogue: 0,{format_ass_ts(c['start'])},{format_ass_ts(c['end'])},Default,,0,0,0,,{c['text']}")
    return "\n".join(lines)


def parse_transcript(data) -> list:
    """Extract word-level timing from various transcription JSON formats."""
    if isinstance(data, list):
        if data and ("word" in data[0] or "text" in data[0]):
            return data
        words = []
        for seg in data:
            if "words" in seg:
                words.extend(seg["words"])
            elif "text" in seg and "start" in seg:
                words.append(seg)
        return words

    if isinstance(data, dict):
        # Whisper-style
        if "segments" in data:
            words = []
            for seg in data["segments"]:
                if "words" in seg:
                    words.extend(seg["words"])
                else:
                    text = seg.get("text", "").strip()
                    start = seg.get("start", 0)
                    end = seg.get("end", start + 1)
                    seg_words = text.split()
                    if seg_words:
                        dur = (end - start) / len(seg_words)
                        for j, w in enumerate(seg_words):
                            words.append({"word": w, "start": start + j * dur, "end": start + (j + 1) * dur})
            return words

        # Deepgram-style
        if "results" in data:
            words = []
            for ch in data["results"].get("channels", []):
                for alt in ch.get("alternatives", []):
                    words.extend(alt.get("words", []))
            return words

        # AssemblyAI / generic
        if "words" in data:
            return data["words"]
        if "text" in data and "start" in data:
            return [data]

    return []


def main():
    parser = argparse.ArgumentParser(description="Generate subtitles from transcription JSON")
    parser.add_argument("input", help="Path to transcription JSON file")
    parser.add_argument("output", help="Output path (.srt, .vtt, or .ass)")
    parser.add_argument("--max-chars", type=int, default=42, help="Max characters per line (default: 42)")
    parser.add_argument("--max-words", type=int, default=8, help="Max words per line (default: 8)")
    parser.add_argument("--font", default="Arial", help="Font name for ASS format (default: Arial)")
    parser.add_argument("--fontsize", type=int, default=24, help="Font size for ASS format (default: 24)")
    args = parser.parse_args()

    with open(args.input, "r") as f:
        data = json.load(f)

    words = parse_transcript(data)
    if not words:
        print("Error: Could not extract word timings from transcript.", file=sys.stderr)
        print("Supported: Whisper, Deepgram, AssemblyAI, or list of {word, start, end}.", file=sys.stderr)
        sys.exit(1)

    chunks = chunk_words(words, max_chars=args.max_chars, max_words=args.max_words)
    ext = Path(args.output).suffix.lower()

    if ext == ".vtt":
        content = generate_vtt(chunks)
    elif ext == ".ass":
        content = generate_ass(chunks, font=args.font, fontsize=args.fontsize)
    else:
        content = generate_srt(chunks)

    with open(args.output, "w") as f:
        f.write(content)

    print(f"Generated {len(chunks)} subtitle entries ({ext}) → {args.output}")


if __name__ == "__main__":
    main()
