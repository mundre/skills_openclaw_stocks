# OpenCawl API Reference

Base URL: `https://opencawl.com`
Auth: `Authorization: Bearer $OPENCAWL_API_KEY`

All OpenClaw-facing endpoints live under `/api/openclaw/`. Dashboard endpoints use session cookie auth instead.

---

## Outbound Calls

### POST /api/openclaw/call

Dispatch an outbound call. ElevenLabs handles the live call loop and Twilio dialing using per-call overrides from OpenCawl.

**Request:**
```json
{
  "to": "+15551234567",
  "goal": "Schedule a 30-minute Workmate demo. Get name, email, and two availability windows.",
  "context": "Inbound lead from enterprise page. Did not reply to follow-up email.",
  "persona": "professional-friendly",
  "voice_id": "emily",
  "max_duration_seconds": 300,
  "on_completion_webhook": "https://your-gateway.example.com/webhooks/opencawl-complete"
}
```

**Fields:**
- `to` (required): E.164 phone number
- `goal` (required): Plain-language call objective
- `context` (optional): Background information for the agent
- `persona` (optional): Persona slug — resolves to a voice from the library. Takes precedence over `voice_id`.
- `voice_id` (optional): Direct voice library ID (e.g. `rachel`, `thomas`). Falls back to user's dashboard selection.
- `max_duration_seconds` (optional): Hard cap, 30–1800 (default: 300)
- `on_completion_webhook` (optional): HTTPS URL to POST outcome to on completion or failure

**Response (201):**
```json
{
  "call_id": "abc123def456",
  "status": "ringing"
}
```

---

### GET /api/openclaw/status?call_id={call_id}

Get status and outcome of any call.

**Response (completed):**
```json
{
  "call_id": "abc123def456",
  "direction": "outbound",
  "status": "completed",
  "outcome": "success",
  "from_number": "+18005550100",
  "to_number": "+15551234567",
  "goal": "Schedule a 30-minute Workmate demo",
  "persona": "professional-friendly",
  "duration_seconds": 187,
  "credits_charged": 45,
  "summary": "Spoke with Jamie Chen. Scheduled demo for Thursday 2pm ET.",
  "extracted": {
    "name": "Jamie Chen",
    "email": "jamie@acme.com",
    "availability": ["Thursday 2pm ET", "Friday 10am ET"]
  },
  "transcript": "[{\"role\":\"agent\",\"text\":\"Hi, may I speak with Jamie?\"},...]",
  "recording_url": "https://api.twilio.com/...",
  "created_at": "2026-03-28T14:00:00Z",
  "completed_at": "2026-03-28T14:03:07Z"
}
```

**Status values:**
| Status | Description |
|--------|-------------|
| `initiated` | Call record created, not yet dialed |
| `queued` | Waiting to be dialed |
| `ringing` | Dialing, not yet answered |
| `in_progress` | Call active |
| `completed` | Call ended normally |
| `failed` | Error during call |
| `no_answer` | Rang, not answered |
| `voicemail` | Reached voicemail |
| `busy` | Line busy |

**Outcome values (on completed calls):**
| Outcome | Description |
|---------|-------------|
| `success` | Goal achieved |
| `partial` | Partial progress, follow-up needed |
| `failed` | Goal not achieved |
| `wrong_person` | Reached incorrect contact |
| `callback_requested` | Contact asked to be called back |

---

### GET /api/openclaw/calls

List calls with optional filtering.

**Query params:**
- `status` — filter by status
- `from` / `to` — ISO date range
- `limit` — max results (default 20, max 100)
- `cursor` — pagination cursor

**Response:**
```json
{
  "calls": [
    {
      "call_id": "abc123def456",
      "direction": "outbound",
      "status": "completed",
      "outcome": "success",
      "to_number": "+15551234567",
      "goal": "Schedule a Workmate demo",
      "summary": "...",
      "duration_seconds": 187,
      "created_at": "2026-03-28T14:00:00Z"
    }
  ],
  "next_cursor": "2026-03-28T13:00:00Z"
}
```

---

### POST /api/openclaw/hangup

Hang up an in-progress call.

**Request:**
```json
{
  "call_id": "abc123def456",
  "reason": "goal_achieved"
}
```

**Response:**
```json
{
  "call_id": "abc123def456",
  "status": "completed",
  "reason": "goal_achieved"
}
```

---

## Inbound / Autonomous

Inbound calls are handled by the shared ElevenLabs agent. OpenCawl personalizes the call at runtime and can dispatch real work to a user-specific OpenClaw gateway.

---

## Phone Numbers

### GET /api/phone/index

List your assigned phone number.

**Response:**
```json
{
  "type": "shared",
  "number": "+18005550100",
  "status": "active"
}
```

### POST /api/phone/provision

Provision a dedicated number (Pro plan only).

**Request:**
```json
{
  "area_code": "415"
}
```

### POST /api/phone/configure

Configure inbound handling for your number.

Dashboard session auth required.

**Request:**
```json
{
  "inbound_mode": "autonomous",
  "voicemail_enabled": true,
  "voicemail_transcription": true,
  "inbound_prompt": "You are OpenCawl for this user. Confirm tasks before acting.",
  "inbound_first_message": "OpenCawl. What do you need?",
  "gateway_webhook": "https://your-gateway.example.com/webhooks/opencawl",
  "gateway_token": "<your-gateway-token>"
}
```

### GET /api/phone/configure

Fetch the current inbound and gateway configuration for the dashboard.

Dashboard session auth required.

**`inbound_mode` options:**
| Mode | Description |
|------|-------------|
| `autonomous` | Preferred mode; ElevenLabs handles the live call loop with OpenCawl-provided voice/prompt overrides |
| `voicemail_only` | Always goes to voicemail |

Additional fields:
- `inbound_prompt` — optional per-user default prompt for inbound autonomous calls
- `inbound_first_message` — optional per-user default first greeting
- `gateway_webhook` — optional HTTPS webhook for dispatching tasks to the user's OpenClaw gateway
- `gateway_token` — optional bearer token OpenCawl will send to that gateway webhook

---

## Voicemail

### GET /api/openclaw/voicemail

List voicemails.

**Query params:** `unread_only`, `limit`, `cursor`

**Response:**
```json
{
  "voicemails": [
    {
      "id": "vm_abc123",
      "from": "+15559876543",
      "received_at": "2026-03-28T09:15:00Z",
      "duration_seconds": 42,
      "transcription": "Hi, this is Sarah from Acme. Calling back about the demo you mentioned...",
      "recording_url": "https://api.twilio.com/...",
      "read": false
    }
  ],
  "next_cursor": null
}
```

---

## Account

### GET /api/openclaw/credits

Check balance.

**Response:**
```json
{
  "balance": 847,
  "plan": "starter",
  "estimated_minutes_remaining": 56,
  "reset_date": "2026-04-01"
}
```

---

### POST /api/openclaw/setup

First-time setup check. Returns current configuration and ElevenLabs webhook/tool endpoints.

**Response:**
```json
{
  "message": "OpenCawl setup complete",
  "phone": { "type": "shared", "number": "+18005550100", "status": "active" },
  "inbound": { "mode": "autonomous", "webhook": null, "voicemail_enabled": true, "prompt": null, "first_message": null },
  "gateway": { "webhook": null, "configured": false },
  "credits": { "balance": 250, "plan": "free" },
  "elevenlabs": {
    "agent_id": "agent_123",
    "shared_phone_number_id": "phone_123",
    "twilio_personalization_webhook": "https://opencawl.com/api/webhooks/elevenlabs/twilio-personalization",
    "post_call_webhook": "https://opencawl.com/api/webhooks/elevenlabs/post-call",
    "tool_dispatch_task": "https://opencawl.com/api/webhooks/elevenlabs/tools/dispatch-task",
    "tool_task_status": "https://opencawl.com/api/webhooks/elevenlabs/tools/task-status"
  }
}
```

---

### POST /api/openclaw/tasks/complete

Used by the user's OpenClaw gateway to mark a dispatched task as `in_progress`, `completed`, or `failed`.

**Request:**
```json
{
  "task_id": "task_123",
  "status": "completed",
  "summary": "Rescheduled for Tuesday at 2pm.",
  "result": {
    "appointment_time": "Tuesday 2pm"
  }
}
```

## Completion Webhook (OpenCawl → Your Server)

If `on_completion_webhook` is set on a call, OpenCawl POSTs the outcome when the call ends.

### `call_completed`
```json
{
  "event": "call_completed",
  "call_id": "abc123def456",
  "direction": "outbound",
  "status": "completed",
  "outcome": "success",
  "to_number": "+15551234567",
  "from_number": "+18005550100",
  "goal": "Schedule a Workmate demo",
  "duration_seconds": 187
}
```

### `call_failed`
```json
{
  "event": "call_failed",
  "call_id": "abc123def456",
  "direction": "outbound",
  "status": "no_answer",
  "outcome": null,
  "to_number": "+15551234567",
  "from_number": "+18005550100",
  "goal": "Schedule a Workmate demo",
  "duration_seconds": 30
}
```

---
