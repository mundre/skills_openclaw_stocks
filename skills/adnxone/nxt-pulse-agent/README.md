# 💓 NXT Pulse Agent v0.2.0

> **A neuro-inclusive, energy-aware proactive partner for OpenClaw.**

NXT Pulse Agent (formerly Proactive Pulse) is a high-performance skill designed to transform your AI assistant into a respectful, proactive partner. Built with ADHD management principles and Hermes-inspired logic, it prioritizes your mental energy over rigid schedules.

[![GitHub license](https://img.shields.io/github/license/adnxone/nxt-pulse-agent)](https://github.com/adnxone/nxt-pulse-agent/blob/main/LICENSE)
[![OpenClaw NXT](https://img.shields.io/badge/OpenClaw-NXT-blueviolet)](https://docs.openclaw.ai)

---

## 🌟 Key Features

- **Energy-Aware Nudging**: Detects user energy (🟢/🟡/🔴) and proactively suggests moving complex tasks to your "Hyperfocus Windows."
- **"Just 2 Minutes" Mode**: When you're in 🔴 (Low Energy), the agent proposes a single micro-step (max 2 min effort) to break executive dysfunction without triggering burnout.
- **Critical Override**: Automatically bypasses "Snooze" modes for deadlines within a configurable threshold (default 6h).
- **Admin Audit Trail**: Every proactive decision is logged in `memory/pulse-history.jsonl` for full transparency and review.
- **Local State Engine**: Powered by `pulse.js` for zero-bloat, efficient context management.

## 🚀 Getting Started

### Installation
```bash
clawhub install adnxone/nxt-pulse-agent
```

### Configuration
The agent automatically uses `pulse.js` to track state. You can customize behavior in your `package.json` or environment variables:
- `PULSE_COOLDOWN`: Default 4 hours.
- `CRITICAL_THRESHOLD`: Default 6 hours.

## 🔍 How it Works
The NXT Pulse Agent doesn't just wait for commands. It monitors your session logs and local calendar to act as an executive function support layer. If it sees you are tired, it protects you. If it sees a deadline, it nudges you respectfully.

---
Created by [adnXone](https://github.com/adnxone) for the OpenClaw community.

<p align="center">
  <img src=".github/icon.png" alt="NXT Pulse Agent Icon" width="128">
</p>
