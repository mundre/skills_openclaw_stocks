# EmoCity Biometric Scan

**Real-time facial biometric analysis powered by EmoPulse on-device ML.**

Live at [emo.city](https://emo.city) | Built by [EmoPulse](https://www.emopulse.app)

---

## What It Does

EmoCity is a browser-based biometric intelligence platform that analyzes your face, voice, and physiological signals in real time. No downloads required. All biometric processing runs on-device using MediaPipe Face Landmarker with GPU acceleration.

Point your camera at a face and EmoCity detects:

- Whether someone is **lying or telling the truth** (Deception Index)
- Real-time **stress levels** from facial micro-tension
- **Emotions** — happy, sad, angry, fearful, surprised, disgusted, neutral
- **Heart rate** without any contact (rPPG forehead analysis)
- **Voice stress** via spectral frequency analysis
- **Micro-expressions** — involuntary facial movements lasting milliseconds
- **Eye contact** stability and gaze aversion patterns
- **Authenticity** — Duchenne smile detection (genuine vs fake)

## 47 Biometric Parameters

EmoCity processes **478 facial landmarks** and **52 blendshapes** every frame to extract:

| Category | Parameters |
|----------|-----------|
| Emotions | 7 emotions with competitive scoring + confidence |
| Action Units | AU1, AU2, AU4, AU6, AU7, AU9, AU12, AU15, AU25, AU26, AU45 |
| Stress | Composite score (facial + cardiac + vocal) |
| Deception | Multi-factor index (stress + authenticity + gaze + micro-expressions) |
| Cardiac | Heart rate (BPM), HRV (RMSSD), RR intervals |
| Gaze | Eye contact %, gaze stability, aversion detection |
| Voice | Stress %, voice detection, frequency analysis |
| Expression | Micro-expression count, blink rate, Duchenne markers |
| Tracking | Face count (up to 4), face position, 478 landmark coordinates |

## How to Use

### Quick Start
1. Say **"scan my face"** or **"lie detector test"**
2. Open [emo.city](https://emo.city) in Chrome or Edge
3. Click **SCAN** and allow camera + microphone
4. The 478-point face mesh confirms detection
5. Speak during the scan for voice stress analysis
6. Results auto-summarize when the scan completes

### Scan Modes

- **LIVE** — Real-time camera analysis (up to 2 minutes)
- **UPLOAD** — Analyze a photo (JPG/PNG) or video (MP4/MOV)
- **CHALLENGE** — Share a deception test link with friends

### Example Commands

```
"scan my face"
"am I lying?"
"check my stress level"
"lie detector test"
"analyze this photo"
"what's my heart rate?"
"challenge my friend"
"how do I look — stressed or relaxed?"
"read my emotions"
"give me a full biometric report"
```

## Technology

- **MediaPipe Face Landmarker** v0.10.18 — 478 landmarks + 52 blendshapes, GPU-accelerated
- **rPPG** — Remote photoplethysmography for contactless heart rate
- **Adaptive baseline calibration** — 30-frame personalized baseline per session
- **Competitive emotion normalization** — dominant emotion suppression for accurate classification
- **Duchenne detection** — AU6 + AU12 co-activation for genuine smile verification
- **Web Audio API** — Real-time spectral analysis for voice stress detection
- **Next.js 16 + React 19 + Tailwind v4** — Modern web stack with Turbopack

## Privacy

All biometric processing runs on-device in the browser. No video, audio, or raw biometric data is sent to any server. The camera feed is analyzed frame-by-frame using WebAssembly + WebGL. Export features (Share to X, Copy Text, Download Report) only share aggregated text summaries — never raw video or biometric signals. Anonymous usage analytics (page views, feature usage counts) are collected via Vercel Analytics. When you close the tab, all local biometric data is gone.

## Links

- **Live app:** [emo.city](https://emo.city)
- **Built by:** [EmoPulse](https://www.emopulse.app)
- **Repository:** [github.com/gv66co/Emo-City](https://github.com/gv66co/Emo-City)

## Plans

| Plan | Price | Scans |
|------|-------|-------|
| Free | $0 | 3 scans |
| Basic | $9.99/mo | 30 scans/month |
| Pro | $29.99/mo | 100 scans/month |

---

## License

This software is **proprietary** and protected by copyright and filed patents (EU 2026-502, 2026-508, 2026-503). Unauthorized copying, modification, distribution, reverse engineering, or use to train AI models is strictly prohibited. See [emopulse.app/license](https://www.emopulse.app/license.html).

Built by EmoPulse. All rights reserved.
