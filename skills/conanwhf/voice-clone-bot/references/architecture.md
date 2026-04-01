# Architecture

## Recommended stack

- **Telegram bot**: `aiogram` or `python-telegram-bot`
- **ASR**: `faster-whisper`
- **LLM**: local quantized Qwen-family model
- **TTS**: Qwen3-TTS first, MOSS-TTS second, OpenVoice V2 fallback
- **Audio**: `ffmpeg`
- **Storage**: `SQLite`

## Request flow

```text
Telegram message
→ bot handler
→ ASR if voice
→ local LLM reply
→ TTS synthesis
→ audio post-processing
→ Telegram voice note / audio message
```

## Long reply strategy

1. Split reply text into sentences or short clauses.
2. Synthesize each segment separately.
3. Add 100–200 ms pauses between segments.
4. Join the segments into one final file.

## Model decision guide

- **Choose Qwen3-TTS** when you want the best balance of quality, speed, and ease of use.
- **Choose MOSS-TTS** when long-form stability and dialogue coherence matter more.
- **Choose OpenVoice V2** when the machine is too small for newer models.
- **Choose NeuTTS** only for English-focused low-resource fallback use.

## Telegram output

- Prefer `.ogg` / Opus for voice-note playback.
- Use MP3 or WAV during development.
- Keep bot identity explicit in the UI and description.
