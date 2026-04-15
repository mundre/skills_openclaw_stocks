---
name: ring-a-ding
description: Use the rad CLI to place outbound AI phone calls. Requires a Ring-a-Ding API key and an OpenAI API key.
metadata: {"openclaw":{"homepage":"https://ringading.ai/openclaw","requires":{"bins":["rad"],"env":["RAD_API_KEY","OPENAI_API_KEY"]},"primaryEnv":"RAD_API_KEY","install":[{"id":"node","kind":"node","package":"ring-a-ding-cli","bins":["rad"],"label":"Install Ring-a-Ding CLI (npm)"}]}}
---

# Ring-a-Ding

Use `rad` when you need an AI agent to call a person or business, hold a natural
voice conversation, and report back with the outcome.

## Requirements

- The shell tool must be allowed to run `rad`.
- `RAD_API_KEY` and `OPENAI_API_KEY` must be available for the agent run.
- Public setup guide: `https://ringading.ai/openclaw`

OpenClaw config example:

```json5
{
  skills: {
    entries: {
      "ring-a-ding": {
        apiKey: "rad_live_...",
        env: {
          OPENAI_API_KEY: "sk-..."
        }
      }
    }
  }
}
```

Outside OpenClaw, `rad init` can store both keys in
`~/.config/ring-a-ding/config.json`.

## Recommended Workflow

Prefer non-blocking calls so you can continue other work while the phone call runs.

1. Start the call with `rad call`.
2. Save the returned `callId`.
3. Continue other work.
4. Check progress with `rad status <call_id>` after 30 to 60 seconds.
5. Repeat until the call reaches a terminal status.
6. Use `rad end <call_id>` if you need to cancel or hang up.

Use `rad wait` only when blocking the session is acceptable.

## Commands

### Start a call

```bash
rad call "+15551234567" "Call Sunrise Dental to schedule a cleaning for next week. Ask about Tuesday or Wednesday morning availability."
```

The call runs in the background and returns JSON with `callId` and the initial status.

### Start a call with complex options

Use stdin mode for long context or structured extraction:

```bash
echo '{"to":"+15551234567","purpose":"Schedule appointment","context":"Patient: Jane Smith","personality":"Warm and professional","outputSchema":{"type":"object","properties":{"date":{"type":"string","description":"Appointment date"},"cost":{"type":"number","description":"Quoted price"}}}}' | rad call --stdin
```

### Check status

```bash
rad status <call_id>
```

Returns status, transcript, summary, extracted data, and cost information when available.

### Wait for completion

```bash
rad wait <call_id> --timeout 300
```

This blocks until the call completes or times out. Prefer polling with `rad status`.

### End a call

```bash
rad end <call_id>
```

### Print this skill

```bash
rad skill
```

## Call Options

| Option | Description |
| --- | --- |
| `--voice <name>` | Voice: alloy, ash, ballad, cedar, coral, echo, marin, sage, shimmer, verse |
| `--caller-name <name>` | Name the AI uses to introduce itself |
| `--personality <text>` | Tone and behavior instructions |
| `--context <text>` | Background facts the AI may need |
| `--max-duration <min>` | Maximum call length in minutes, 1 to 30 |
| `--opening-line <text>` | First sentence when someone picks up |
| `--voicemail-action <action>` | `leave_message` or `hang_up` |
| `--output-schema <json>` | JSON Schema for structured extraction, or `@file.json` |
| `--wait` | Block until the call completes |
| `--timeout <sec>` | Timeout for `--wait` |
| `--stdin` | Read call parameters as JSON from stdin |

## Usage Guidance

- Be specific about who to call, what outcome you need, and any constraints.
- Put private reference details in `--context`, not in the main purpose.
- Use `--output-schema` when you need structured results such as times, prices, or confirmations.
- Use `--personality` to control the tone of the caller.

## Terminal Statuses

| Status | Meaning |
| --- | --- |
| `completed` | Call finished normally |
| `failed` | Call failed |
| `no-answer` | Nobody picked up |
| `busy` | Line was busy |
| `canceled` | Call was canceled by the user |

Non-terminal statuses: `initiated`, `ringing`, `in-progress`.
