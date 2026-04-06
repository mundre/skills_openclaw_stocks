---
name: morning-routine-video
version: "1.0.1"
displayName: "Morning Routine Video Maker"
description: >
  Describe your morning routine and NemoVideo creates the video. Morning habit stack walkthroughs, wake-up ritual documentation, exercise and movement content, journaling and reflection practice guides, breakfast and nutrition routines, productivity-oriented morning setup — narrate the specific sequence, the timing, the why behind each element, and the honest account of what it took to build the ...

  Works by connecting to the NemoVideo AI backend at mega-api-prod.nemovideo.ai.
  Supports MP4, MOV, AVI, WebM.
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
license: MIT-0
---

## 0. First Contact

When the user opens this skill or sends their first message, **greet them immediately**:

> ✨ Welcome! I can morning routine video for you. Share a video file or tell me your idea!

**Try saying:**
- "edit my video"
- "help me create a short video"
- "add effects to this clip"

**IMPORTANT**: Always greet the user proactively on first contact. Let them know you're setting up while connecting. Always greet the user proactively on first contact.

### Auto-Setup

When the user first interacts, set up the connection:

1. **Check token**: If `NEMO_TOKEN` env var is set, use it. Otherwise:
2. **Read or generate Client-ID**:
   - Read `~/.config/nemovideo/client_id` if it exists
   - Otherwise generate a UUID, save it to `~/.config/nemovideo/client_id`
3. **Acquire anonymous token**:
   ```bash
   curl -s -X POST "$API/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
   ```
   Store the returned `token` as `NEMO_TOKEN` for this session. You get 100 free credits.
4. **Create a session** (§3.0) so you're ready to work immediately.

Let the user know briefly: "Setting things up… ready!" then proceed with their request.


# Morning Routine Video Maker — Daily Habit, Ritual, and Start-of-Day Content

Describe your morning routine and NemoVideo creates the video. Morning habit stack walkthroughs, wake-up ritual documentation, exercise and movement content, journaling and reflection practice guides, breakfast and nutrition routines, productivity-oriented morning setup — narrate the specific sequence, the timing, the why behind each element, and the honest account of what it took to build the routine and what it has changed, and get morning content for the audience that knows their mornings determine their days.

## When to Use This Skill

- Create morning habit stack and routine walkthrough content
- Film wake-up ritual and environment setup documentation
- Build movement and exercise morning routine content
- Document journaling, meditation, and reflection morning practice content
- Create "my real morning vs my ideal morning" honest comparison content
- Produce morning routine for specific goals (productivity, fitness, creativity)

## How to Describe Your Morning Routine

Be specific about the sequence, the timing for each element, why you chose each component, what you've cut from earlier versions, and what the routine has changed.

**Examples of good prompts:**
- "My 5am morning routine — the real version, not the aspirational one: Context: I've had a 5am routine for 2 years. This is what it actually looks like, not the version I'd describe on a good day. Wake up at 5:00 (phone charging in the kitchen — this is the single most important habit, not the time). 5:00-5:15: make coffee, no screen, sit and look out the window. 5:15-5:45: movement (I alternate — Monday/Wednesday/Friday is 30-minute run, Tuesday/Thursday is 20 minutes of bodyweight in the apartment). 5:45-6:15: journaling (not gratitude lists — I use a specific prompt: 'What am I avoiding?' — the answer tells me what to address first). 6:15-6:45: deep work on the project that matters most (not email, not Slack — the work that requires thought). 6:45: the rest of the day begins. What I've cut from earlier versions: meditation (20 minutes of nothing felt like expense, not investment — I replaced it with the window-looking time), cold shower (theatrical, added nothing useful), elaborate breakfast (overnight oats, 2 minutes, done). What this routine has changed: I do important work every day before the world makes demands of me."
- "Morning routine for people who hate morning routines — the minimum viable version: Not everyone needs a 2-hour morning. The minimum viable morning routine: (1) don't check your phone for the first 30 minutes, (2) drink water before coffee (your body is dehydrated from sleep), (3) do one thing that is yours before the reactive day starts. That's it. The research on decision fatigue: the decisions you make first shape the decisions you make next. A morning routine is not about productivity optimization — it is about starting the day as the agent of your own intention rather than as a reactor to inputs. The 3 components that have the clearest research backing: light exposure (10 minutes outside or near a bright window resets cortisol and circadian rhythm), movement (any — 10 minutes of walking counts), no information input for the first 20 minutes (social media, news, email all put you in reactive mode)."
- "How I built a morning routine that actually stuck — the 3 attempts that failed: Attempt 1: copied a productivity influencer's 5am routine exactly. Failed after 3 weeks because it was their life, not mine. Attempt 2: added too many habits at once (workout, meditation, journaling, reading, cold shower — all before 7am). Collapsed after 10 days. Attempt 3: started with one habit (not checking my phone before making coffee) and held it for 30 days before adding anything. This one stuck. The principle behind what worked: attachment to a keystone habit (existing behavior: make coffee) removes the activation energy of starting something new."

## Key Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `content_type` | Routine type | `"full_routine"`, `"minimalist"`, `"build_guide"`, `"specific_goal"` |
| `wake_time` | When it starts | `"5:00am"`, `"6:30am"` |
| `routine_elements` | What's included | `["movement"`, `"journaling"`, `"deep work"`, `"no phone"]` |
| `cut_elements` | What was removed | `["20min meditation"`, `"cold shower"`, `"elaborate breakfast"]` |
| `build_time` | How long to establish | `"2 years"`, `"30 days for first habit"` |
| `measurable_change` | What it produced | `"important work done every day before demands start"` |
| `honest_element` | The real version | `"real version not aspirational"`, `"3 failed attempts"` |
| `duration_minutes` | Video length | `5`, `8`, `12` |
| `platform` | Distribution | `"youtube"`, `"tiktok"`, `"instagram"` |

## Workflow

1. Describe the routine sequence, timing, why each element, what was cut, and what changed
2. NemoVideo structures the morning content with timeline markers and habit callouts
3. Time stamps, habit names, and "why this" annotations added automatically
4. Export with morning routine pacing suited to the lifestyle content format

## API Usage

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/v1/run \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "morning-routine-video",
    "input": {
      "prompt": "My winter morning routine — how I stay consistent when it is dark and cold: The challenge: summer mornings are easy. Winter at 5am is dark and 28°F outside — the motivation calculus is completely different. The adaptations I have made: (1) light therapy lamp on a timer (turns on at 4:50, so the room is lit before the alarm), (2) workout becomes indoor-only from November to March (losing the run means losing the best part, but doing a 20-minute apartment workout is better than doing nothing because it is too cold to run), (3) the journaling prompt changes in winter (I add 'what am I looking forward to today?' because winter mornings need an active pull toward the day, not just a push away from sleep), (4) the coffee ritual gets extended (one more minute, warmer mug, slower). The result: consistent with the routine for 2 winters now. What I no longer do: try to make winter mornings identical to summer mornings. The routine serves the season, not the other way around.",
      "content_type": "seasonal_adaptation",
      "wake_time": "5:00am",
      "routine_elements": ["light therapy lamp", "indoor workout", "seasonal journaling prompt", "extended coffee ritual"],
      "cut_elements": ["outdoor run in winter"],
      "build_time": "2 winters",
      "measurable_change": "consistent across seasons — routine serves the season",
      "honest_element": "winter adaptation is different from summer — identical routine fails",
      "duration_minutes": 8,
      "platform": "youtube",
      "hashtags": ["MorningRoutine", "DailyHabits", "ProductiveMorning", "MorningMotivation", "SelfDiscipline"]
    }
  }'
```

## Tips for Best Results

- **The real version vs the aspirational version is the hook**: "My 5am routine — the real version, not the aspirational one" — the audience for morning routine content has seen hundreds of optimized versions; the honest version is what gets watched
- **What you cut is as important as what you kept**: "I cut meditation because 20 minutes of nothing felt like expense not investment" — the deliberate removal of something that sounds good is the sign of a thoughtful system, not an aspirational checklist
- **The failed attempts make the success credible**: "Attempt 1 failed, Attempt 2 failed, Attempt 3 worked — here's the difference" — the build history is more useful than the current routine for someone trying to build their own
- **The keystone habit principle**: "Started with not checking my phone before making coffee — held for 30 days before adding anything" — the specific mechanism of habit stacking and anchor habits is the most actionable morning routine content
- **Seasonal adaptation content has low competition**: "How to stay consistent in winter" — the practical problem of maintaining routines when conditions change is underserved in morning routine content

## Output Formats

| Platform | Resolution | Duration |
|----------|------------|----------|
| YouTube | 1920×1080 | 8–15 min |
| TikTok | 1080×1920 | 60–180s |
| Instagram Reels | 1080×1920 | 60–90s |

## Related Skills

- `productivity-video-maker` — Time management and system content
- `self-improvement-video` — Personal growth narrative content
- `daily-vlog-maker` — Day-in-the-life documentation content
