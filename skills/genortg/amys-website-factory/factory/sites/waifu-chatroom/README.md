# waifu-chatroom

Fullstack waifu chatroom built with **Next.js + Tailwind + three.js** on the frontend and a **Python FastAPI backend** for OpenAI-compatible chat, Whisper STT, and Kokoro TTS.

## Frontend

```bash
npm install
npm run dev
```

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Env

- `backend` defaults to `http://127.0.0.1:8000`
- Frontend can point at any OpenAI-compatible chat endpoint
- Whisper + Kokoro are optional adapters in the backend scaffold

## What it does

- Upload VRM avatars
- Chat in-browser
- Record mic audio and transcribe with Whisper
- Speak replies with Kokoro-style TTS
- Drive mouth movement while audio plays
