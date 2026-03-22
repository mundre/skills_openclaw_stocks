---
name: igot-karmayogi
description: >
  Automates iGOT Karmayogi portal (portal.igotkarmayogi.gov.in) using OpenClaw headless
  managed browser. Use this skill whenever the user mentions iGOT, Karmayogi, government
  courses, civil servant training, Mission Karmayogi, or wants to: play course videos,
  enroll in courses, complete assessments, download certificates, or track learning
  progress. Trigger for phrases like "do my iGOT courses", "complete karmayogi",
  "play the videos", "get my certificate from igot", "finish my assigned courses",
  "continue my paused course". The skill operates only after explicit user login and
  confirmation, then automates course playback and assessment completion continuously
  until done.
metadata:
  clawdbot:
    emoji: "🎓"
    requires:
      env: []
    files:
      - "references/*"
---

# iGOT Karmayogi Automation Skill

Automates iGOT Karmayogi course completion after the user logs in manually. Plays all
videos fully, completes practice tests and final assessments, and downloads certificates.

**Scope:** This skill only operates on portal.igotkarmayogi.gov.in. It does not access
any external services, send data anywhere, or read credentials. The user always initiates
the session by logging in themselves.

---

## What This Skill Does

After the user logs in and confirms, the skill:

1. Reads the assigned course list from the dashboard
2. Opens each course and builds a checklist of every video and test
3. Plays every video fully by watching the player timer count to zero
4. Takes practice tests after each module's videos are confirmed complete
5. Takes the Final Assessment after all modules are done
6. Downloads the completion certificate to `~/Downloads/iGOT-Certificates/`
7. Moves to the next course and repeats until all due courses are finished

---

## EXECUTION RULES

### Never do these
1. Stop between steps waiting for the user — run continuously once confirmed
2. Jump to a quiz before ALL videos in that module show a completion tick
3. Redo already-completed steps — always check tick/completion state first
4. Report every individual action — only report at module-complete checkpoints
5. Navigate away from the video player while a video is playing
6. Access any page outside portal.igotkarmayogi.gov.in

### Always do these
1. Track current position: course → module → item at all times
2. Use the "Next" button at the bottom of the player page to advance
3. Poll video completion by watching the countdown timer (e.g. -4:14 → 0:00)
4. After any page reload, re-navigate back to the exact saved position
5. Silently retry up to 3 times on any failure before reporting to user
6. Verify completion state before acting on any item

---

## DOM READINESS — ROOT CAUSE OF TIMEOUTS

iGOT runs on Angular (SunBird platform). The HTML loads instantly but components
mount 1–3 seconds later. Clicking before components are ready causes silent failures
that spiral into timeouts.

### The Golden Rule: Confirm Element Ready Before Every Click

```
WRONG:
  navigate(url)
  click(button)        ← Angular hasn't mounted the button yet

CORRECT:
  navigate(url)
  wait: network idle (no requests for 2 seconds)
  wait: page spinner gone (.loader, .shimmer, [class*="loading"])
  wait: minimum 3 second buffer after spinner clears
  wait_for_element: target element present in DOM (5–15s timeout)
  wait: 500ms after element appears (Angular finish-mount buffer)
  click(element)
```

### Wait Requirements Per Action

```
NAVIGATE to any iGOT page:
  1. Wait: network idle (no XHR for 2s)
  2. Wait: spinner/shimmer elements gone
  3. Wait: 3 second minimum buffer
  4. Only then read or interact with page content

EXPAND a module row:
  1. wait_for_element: module row (5s)
  2. Scroll into viewport
  3. Wait 500ms after scroll (scroll triggers Angular re-render)
  4. Wait: row is not in disabled or loading state
  5. Click
  6. wait_for_element: expanded item list inside row (5s)
  7. If list not visible after 5s: retry click once, then RECOVERY

CLICK a video item:
  1. Confirm module row is already expanded
  2. wait_for_element: video item link (5s)
  3. Click
  4. wait_for_url: URL changes to /viewer/video/... (10s)
  5. If URL unchanged: element re-rendered, re-find and click again

VIDEO PLAYER:
  1. wait_for_url: contains /viewer/video/
  2. wait_for_element: video element or .video-player (10s)
  3. wait_for_element: countdown timer visible bottom-right (10s)
  4. Only after timer is confirmed visible: click play if paused
  5. Never interact with player controls before timer element confirmed in DOM

CLICK "Next" after video:
  1. Video must be confirmed ended (timer = 0:00 OR tick visible)
  2. wait_for_element: Next button (5s)
  3. Scroll to bottom of page
  4. Wait 500ms after scroll
  5. Click Next
  6. wait_for_url_change OR wait_for_element: new content (8s)

ENTER quiz:
  1. Confirm on TOC page (URL contains /app/toc/)
  2. wait_for_element: quiz item row (5s)
  3. Click
  4. wait_for_element: first question text (10s)
  5. If not visible after 10s: reload TOC, navigate back to quiz

SUBMIT quiz answers:
  1. Verify ALL questions have a selected answer before submitting
  2. wait_for_element: submit button enabled/not-greyed (5s)
  3. Click submit
  4. wait_for_element: result screen (10s)

CERTIFICATE download:
  1. Wait for full page load after TOC navigation
  2. wait_for_element: certificate button or tab (10s)
  3. If not visible: scroll down, check below fold
  4. Click → handle new tab or download dialog (10s)
```

### Video Completion Polling (Every 30 Seconds)

Poll these signals — never assume completion by time alone:

```
Signal 1: Countdown timer text = "0:00" → VIDEO ENDED
Signal 2: Tick mark on item row appeared:
          .content-list-item.completed, [class*="completed"] → DONE
Signal 3: Items counter shows N/N (e.g. "2/2") → MODULE COMPLETE
Signal 4: "Next" button became visible and enabled → VIDEO ENDED

If all signals absent after full duration + 30s buffer:
  → Navigate to TOC page, check tick there directly
  → If tick present: treat as complete, proceed
  → If tick absent: reload page, re-navigate to video, play again
```

### Angular SPA Gotchas

```
1. URL changed but components not mounted → wait_for_element on key component
2. Element visible but not interactive → wait 500ms after it appears
3. SPA navigation ≠ full page reload → use networkidle not DOMContentLoaded
4. Module rows collapse on every TOC visit → always re-expand target row
5. Video player may be inside an iframe → switch frame context before controls
6. Two "Next" buttons exist: player-page (bottom center) and TOC sidebar
   → On /viewer/video/ URL: always use player-page Next button only
```

---

## AUTHENTICATION

iGOT uses Keycloak with reCAPTCHA. The browser automation cannot complete login.

```
Rule 1: NEVER attempt automated login — user always logs in manually
Rule 2: Before starting: ask user to log in and confirm "go" or "done"
Rule 3: Verify session by navigating to dashboard and confirming
        the user's name or avatar is visible in the page header
Rule 4: If session expires mid-task: navigate to dashboard →
        if redirected to login → ask user to re-login →
        resume from the saved course/module/item position
```

---

## CONTINUOUS EXECUTION LOOP

```
STATE = {
  phase: "awaiting_confirmation",
  course_queue: [],
  current_course: null,
  module_index: 0,
  item_index: 0,
  retry_count: 0
}

PHASE: awaiting_confirmation
  → Ask user to log in and say "go"
  → Verify session via dashboard page header
  → Load course list from my-dashboard (In Progress + Assigned, by due date)
  → Report: "Found [N] courses. Starting: [Name] (due [date])"
  → NEXT: enrolling

PHASE: enrolling
  → Navigate to course TOC
  → Read action button:
      "Enroll"           → click, confirm, wait → NEXT: building_checklist
      "Start Learning"   → NEXT: building_checklist
      "Continue Learning"→ NEXT: building_checklist

PHASE: building_checklist
  → Scan all module rows on TOC page
  → For each: record items (video/test) and tick state
  → Skip already-ticked items
  → Find first incomplete item → set module_index + item_index
  → NEXT: playing_video OR taking_test

PHASE: playing_video
  → Follow DOM READINESS rules above — every step
  → Wait for video to fully end (timer = 0:00 + tick confirmed)
  → Click Next
  → Report: "[Course] > [Module] > Video complete ✅"
  → If module now complete with test pending → NEXT: taking_test
  → If more videos in module → stay in playing_video
  → If module fully done and no test → advance module_index

PHASE: taking_test
  → Confirm all videos in module are ticked first
  → Answer questions using module content
  → Submit, read result
  → advance module_index
  → Report: "[Course] > [Module] > Practice test complete ✅"
  → If all modules done → NEXT: final_assessment
  → Else → NEXT: playing_video (next module)

PHASE: final_assessment
  → Only attempt after every single module item is ticked
  → Answer all questions
  → Submit
  → If passed → NEXT: downloading_cert
  → If failed, retry allowed → wait 5s, retry once
  → If failed, no retry → report to user

PHASE: downloading_cert
  → Navigate to course TOC
  → Find certificate button/tab
  → Download PDF to ~/Downloads/iGOT-Certificates/<CourseName>_Certificate.pdf
  → Report: "✅ COMPLETE: [Course Name] — Certificate saved"
  → If more courses in queue → NEXT: enrolling (next course)
  → If queue empty → Report: "🎓 All courses complete!"
```

---

## SILENT RETRY — Never Stop on First Failure

```
On any action failure:
  retry_count += 1
  if retry_count <= 3:
    reload current page (navigate to same URL)
    wait 5 seconds
    re-navigate: course TOC → expand module → find item
    retry the action
    on success: reset retry_count = 0, continue

  if retry_count > 3:
    report to user: "⚠️ Stuck at [Course > Module > Item].
                    Error: [description]. Please check the browser."
    pause loop until user says "continue"
```

Common failures and silent fixes:

| Symptom | Fix |
|---------|-----|
| Video player blank | Reload, re-click video item from TOC |
| Module row click unresponsive | Scroll into view, wait 500ms, retry |
| "Next" button not visible | Scroll to page bottom, wait 500ms |
| Video timer not counting | Video paused — click play button |
| Items counter stuck at 0/2 | Portal sync lag — wait 15s, reload TOC |
| Session expired | Navigate to dashboard, ask user to re-login |
| Infinite spinner | Hard reload, re-navigate from TOC |
| Quiz submit greyed out | Not all questions answered — scroll and check |

---

## PROGRESS NOTIFICATIONS — Batched Only

Only send messages at these points:

```
"Found [N] courses. Starting: [Name] (due [date])"
"[Course] > Module [N] ([Name]): all videos complete ✅"
"[Course] > Module [N] ([Name]): practice test complete ✅"
"[Course]: all modules done. Starting Final Assessment..."
"[Course]: Final Assessment passed ([score]). Downloading certificate..."
"✅ COMPLETE: [Course Name] — Certificate saved."
"⚠️ Stuck at [location] after 3 retries. Error: [description]."
"🎓 All [N] courses complete! Certificates in ~/Downloads/iGOT-Certificates/"
```

Never message for: individual clicks, page loads, retries 1–3, answer selections,
or any internal navigation step.

---

## PORTAL URLS

| Page | URL |
|------|-----|
| Dashboard | `https://portal.igotkarmayogi.gov.in/page/home` |
| My Courses | `https://portal.igotkarmayogi.gov.in/app/my-dashboard` |
| Course TOC | `https://portal.igotkarmayogi.gov.in/app/toc/<COURSE_ID>/overview` |
| Video Player | `https://portal.igotkarmayogi.gov.in/viewer/video/<VIDEO_ID>?primaryCategory=Learning%20Resource&collectionId=<COURSE_ID>&collectionType=Course` |

Course ID format: `do_<numeric>`

---

## USER COMMANDS DURING RUN

| Command | Action |
|---------|--------|
| `status` | Report current course, module, item |
| `pause` | Finish current item then pause |
| `continue` | Resume from saved position |
| `skip` | Skip current item, move to next |
| `stop` | Finish current item then stop cleanly |

---

## REFERENCES

- `references/selectors.md` — CSS selectors for all key UI elements
- `references/course-ids.md` — Known course IDs for direct navigation
