---
name: voice-clone-bot
description: Design and build a fully local Telegram voice-clone bot that replies in a chosen speaker voice, including model selection, ASR/LLM/TTS pipeline design, long-form synthesis, and packaging for Telegram voice messages. Use when asked to create, refine, or deploy a local voice cloning bot; choose TTS models; or design a Telegram bot that answers with synthesized speech without remote LLM APIs.
---

# Voice Clone Bot

## Overview

Build a local Telegram bot that turns text or voice input into replies spoken in the target speaker's voice. Keep the pipeline fully local unless the user explicitly asks otherwise.

## Core pipeline

1. Receive a Telegram message.
2. If the message is voice, transcribe it locally with ASR.
3. Generate the reply text with a local LLM.
4. Synthesize speech with a local voice-clone TTS model.
5. Return the result as Telegram voice (`.ogg`/Opus) or audio.

## Model selection

Use this order unless the hardware or language target changes it:

1. **Qwen3-TTS** — default choice for balanced quality, speed, and local deployment.
2. **MOSS-TTS Local / Realtime** — choose for longer, more stable dialogue generation.
3. **OpenVoice V2** — use as the lighter fallback when resources are tight.

For English-only low-resource setups, NeuTTS can be a fast fallback, but it is not the default for Chinese-first use.

## Build workflow

### 1. Define the target behavior

- Decide whether the bot answers with text only, voice only, or both.
- Keep the bot identity explicit; do not imply it is the user's personal account.
- Decide the reply length policy: short chat, medium chat, or long-form narration.

### 2. Prepare voice material

- Start with 3–5 minutes of clean reference audio.
- Prefer 10–20 minutes for better stability.
- Use the same microphone and a quiet room.
- Include short, long, formal, and casual sentences.

### 3. Implement generation

- Transcribe voice input with `faster-whisper` or a similar local ASR.
- Use a local LLM for reply text.
- Split long replies into short segments before TTS.
- Reuse one reference voice prompt across segments.
- Insert short pauses between segments for natural cadence.

### 4. Deliver to Telegram

- Prefer Telegram voice messages for the most natural experience.
- Convert final audio to OGG/Opus.
- Fall back to MP3/WAV for debugging or long-form output.

## Long-form synthesis rules

- Do not feed a 2-minute reply as one huge block unless the model explicitly supports it well.
- Break by sentence or clause.
- Keep punctuation intact.
- Reassemble audio after synthesis.
- Use the same speaker reference for every segment.

## Practical defaults

- Prefer a small local LLM first; upgrade only if reply quality is weak.
- Prefer Qwen3-TTS first; switch to MOSS-TTS when long-form stability matters more than simplicity.
- Use OpenVoice V2 when the machine is underpowered.

## Output quality checklist

- Voice sounds like the target speaker.
- Reply latency is acceptable in chat.
- Long replies do not drift or become robotic.
- Telegram playback works as a normal voice note.
- No remote TTS/LLM API is required unless the user asks for it.

## References

Read `references/architecture.md` for the recommended system layout and fallback choices.
