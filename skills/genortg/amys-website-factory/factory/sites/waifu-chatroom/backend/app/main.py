from __future__ import annotations

import base64
import io
import json
import math
import os
import wave
from pathlib import Path
from typing import Literal

import httpx
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None

try:
    from faster_whisper import WhisperModel
except Exception:  # pragma: no cover
    WhisperModel = None

app = FastAPI(title="Waifu Room Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_MESSAGE_ROLES = {"system", "user", "assistant", "tool"}

_whisper_model = None


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str


class ChatRequest(BaseModel):
    model: str = "gpt-4o-mini"
    api_base_url: str | None = None
    api_key: str | None = None
    system_prompt: str = ""
    personality: str = ""
    temperature: float = 0.7
    messages: list[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    emotion: Literal["neutral", "happy", "sad", "angry", "surprised"] = "neutral"


class TtsRequest(BaseModel):
    text: str
    voice: str = "kore"
    model: str = "gpt-4o-mini"
    backend: dict | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    prompt = []
    if request.system_prompt.strip():
        prompt.append(request.system_prompt.strip())
    if request.personality.strip():
        prompt.append(request.personality.strip())

    if request.api_base_url and request.api_key and OpenAI is not None:
        client = OpenAI(base_url=request.api_base_url, api_key=request.api_key)
        messages = []
        if prompt:
            messages.append({"role": "system", "content": "\n\n".join(prompt)})
        messages.extend(
            {"role": m.role, "content": m.content}
            for m in request.messages
            if m.role in _MESSAGE_ROLES
        )
        completion = client.chat.completions.create(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
        )
        reply = completion.choices[0].message.content or ""
        return ChatResponse(reply=reply.strip(), emotion=_guess_emotion(reply))

    user_text = next((m.content for m in reversed(request.messages) if m.role == "user"), "")
    reply = (
        "I’m live, and I can already feel the room warming up. "
        f"You said: {user_text or 'something lovely'}. "
        "Give me a real OpenAI-compatible endpoint and I’ll answer for real."
    )
    return ChatResponse(reply=reply, emotion=_guess_emotion(reply))


@app.post("/stt")
async def stt(file: UploadFile = File(...)):
    model = _load_whisper_model()
    if model is None:
      return {"text": "Whisper is not installed yet."}

    suffix = Path(file.filename or "audio.webm").suffix or ".webm"
    tmp_path = Path("/tmp") / f"waifu-room-stt{suffix}"
    data = await file.read()
    tmp_path.write_bytes(data)
    segments, _info = model.transcribe(str(tmp_path), beam_size=1)
    text = "".join(segment.text for segment in segments).strip()
    return {"text": text}


@app.post("/tts")
def tts(request: TtsRequest):
    text = request.text.strip() or "..."
    kokoro_base_url = os.getenv("KOKORO_BASE_URL", "").strip()
    kokoro_api_key = os.getenv("KOKORO_API_KEY", "").strip()
    if kokoro_base_url:
        audio = _tts_via_kokoro(
            base_url=kokoro_base_url,
            api_key=kokoro_api_key,
            text=text,
            voice=request.voice,
            model=request.model,
        )
        if audio is not None:
            return Response(content=audio, media_type="audio/mpeg")

    audio = _synthesize_tone(text)
    return Response(content=audio, media_type="audio/wav")


def _tts_via_kokoro(
    base_url: str,
    api_key: str,
    text: str,
    voice: str,
    model: str,
) -> bytes | None:
    url = base_url.rstrip("/") + "/v1/audio/speech"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {"model": model, "voice": voice, "input": text, "format": "mp3"}
    try:
        with httpx.Client(timeout=120.0) as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.content
    except Exception as error:  # pragma: no cover
        print(f"kokoro tts fallback: {error}")
        return None


def _guess_emotion(text: str):
    value = text.lower()
    if any(word in value for word in ["sorry", "sad", "lonely", "hurt"]):
        return "sad"
    if any(word in value for word in ["angry", "mad", "annoyed", "grr"]):
        return "angry"
    if any(word in value for word in ["wow", "surprise", "shocked"]):
        return "surprised"
    if any(word in value for word in ["love", "cute", "happy", "yay", "nice", "sweet"]):
        return "happy"
    return "neutral"


def _load_whisper_model():
    global _whisper_model
    if _whisper_model is not None:
        return _whisper_model
    if WhisperModel is None:
        return None

    model_name = os.getenv("WHISPER_MODEL", "base")
    device = os.getenv("WHISPER_DEVICE", "cpu")
    compute_type = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
    _whisper_model = WhisperModel(model_name, device=device, compute_type=compute_type)
    return _whisper_model


def _synthesize_tone(text: str) -> bytes:
    sample_rate = 24_000
    duration = max(0.6, min(5.0, len(text) * 0.055))
    frequency = 220 + (sum(ord(ch) for ch in text) % 280)
    amplitude = 0.18

    frames = bytearray()
    for i in range(int(sample_rate * duration)):
        sample = int(math.sin(2 * math.pi * frequency * i / sample_rate) * 32767 * amplitude)
        frames.extend(sample.to_bytes(2, byteorder="little", signed=True))

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(bytes(frames))
    return buffer.getvalue()
