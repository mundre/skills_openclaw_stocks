---
name: openclaw-channel-doctor
description: Diagnose and fix OpenClaw messaging channel failures across Telegram, Discord, WhatsApp, Slack, and webchat. Use when users report no replies, no active listener, proxy/fetch failures, wrong thread/topic routing, broken quote/reply/mention behavior, duplicate deliveries, or message send succeeds without expected channel effect (e.g., poll/reply not rendered).
metadata:
  openclaw:
    emoji: "🩺"
    requires:
      bins: ["openclaw"]
      permissions:
        - "ability to run openclaw status/health/log commands"
        - "authorization to restart gateway when explicitly approved"
---

# OpenClaw Channel Doctor

Run symptom-first diagnostics for channel problems. Keep responses short, command-first, and verifiable.

## Core Operating Rules

1. Start with read-only checks.
2. Isolate one failure mode at a time.
3. Apply smallest safe fix first.
4. Verify with both inbound and outbound checks.
5. If unresolved, provide a compact escalation bundle.
6. Ask explicit user confirmation before any gateway restart or disruptive action.
7. Redact secrets before sharing logs (tokens, API keys, auth headers, phone numbers, emails, account IDs).

## Output Template

## Command
[exact command]

## What It Checks
[one line]

## Expected
[success signal]

## If Not
[next branch]

---

## Baseline (always run first)

```bash
openclaw status
openclaw gateway health
openclaw gateway status
openclaw logs --limit 200
```

If gateway is unhealthy, fix gateway first before channel-level debugging.

---

## Symptom A: "Bot receives messages but does not reply"

### A1) Check runtime health and recent channel errors

```bash
openclaw status
openclaw logs --limit 300
```

Look for: stalled loops, gateway closed, auth/session errors, provider routing failures.

### A2) Fast containment

```bash
openclaw gateway restart
openclaw status
```

### A3) Verification gate

- Send one inbound test message from target channel.
- Confirm one outbound response arrives within expected latency.

If still failing, collect escalation bundle (see end).

---

## Symptom B: "No active listener" / session dropped (common in relink scenarios)

### B1) Check logs around account startup/relink

```bash
openclaw logs --limit 400
```

Look for: listener init failure, 401/session invalid, account mismatch.

### B2) Restart gateway after confirming config/account mapping

```bash
openclaw gateway restart
openclaw status
```

### B3) Verification gate

- inbound test succeeds
- outbound send succeeds

---

## Symptom C: Proxy/fetch failures on channel startup or send

### C1) Confirm failure signature in logs

```bash
openclaw logs --limit 400
```

Look for patterns like `fetch failed`, partial startup success, REST vs gateway path mismatch.

### C2) Restart and re-check health

```bash
openclaw gateway restart
openclaw gateway health
```

### C3) Verification gate

- command path works twice in a row (to avoid false green)
- inbound + outbound channel test both pass

---

## Symptom D: Wrong thread/topic routing (Telegram topics, Slack/Discord thread mode)

### D1) Confirm message target metadata is being used

Check run logs and command inputs for thread/topic identifiers.

### D2) Run a controlled send test to explicit target

Use one known channel + one explicit thread/topic target. Avoid multi-recipient tests first.

### D3) Verification gate

- message appears in correct thread/topic
- no duplicate in parent/general channel

---

## Symptom E: reply/quote/mention appears ignored

### E1) Confirm tool call or reply tag path from logs

```bash
openclaw logs --limit 400
```

Check whether reply metadata is accepted upstream but dropped before provider send.

### E2) Controlled A/B send

1. plain send
2. reply/quote send

Compare behavior in same channel within 2 minutes.

### E3) Verification gate

- quoted/replied message renders correctly in channel UI

---

## Symptom F: duplicate deliveries / repeated sends

### F1) Confirm duplicates in logs and timestamps

```bash
openclaw logs --limit 500
```

Look for queue drain loops, stale websocket/session, repeated send attempts.

### F2) Containment

```bash
openclaw gateway restart
```

### F3) Verification gate

- send exactly one test message
- confirm only one outbound delivery

---

## Channel-Specific Quick Notes

- **Telegram:** verify poll/reply/topic behavior directly in chat UI (API success may still render wrong).
- **Discord:** watch startup races, stale sockets, proxy REST vs gateway path mismatch.
- **WhatsApp:** relink/account listener edge-cases are common; verify listener + outbound in sequence.
- **Slack:** test channel vs thread routing explicitly; avoid mixed-mode assumptions.
- **webchat:** verify UI transport/rendering separately from gateway health.

---

## Safe Change Policy

Before risky actions (broad config edits, credential rotations, irreversible steps), request explicit user confirmation.

---

## Escalation Bundle (if unresolved)

Provide exactly:

1. Symptom (single sentence)
2. Channel + account/context
3. Commands run (exact)
4. Key log lines (trimmed, with timestamps, and sensitive fields redacted)
5. What is already ruled out
6. Top 2 likely root causes
7. Next highest-signal test
