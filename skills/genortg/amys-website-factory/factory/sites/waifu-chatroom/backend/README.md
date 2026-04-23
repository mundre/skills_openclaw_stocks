# Backend

FastAPI backend for the waifu chatroom.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Endpoints

- `GET /health`
- `POST /chat`
- `POST /stt`
- `POST /tts`
