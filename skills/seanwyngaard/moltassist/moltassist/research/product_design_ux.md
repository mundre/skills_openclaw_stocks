# Pulse -- Product Design & UX Specification
**Version:** 0.1 (Foundation Research)  
**Date:** March 2026  
**Status:** Research & Spec Phase

---

## Table of Contents

1. [App Architecture](#1-app-architecture)
2. [Onboarding Flow](#2-onboarding-flow)
3. [The Always-On Problem](#3-the-always-on-problem)
4. [Notification Design](#4-notification-design)
5. [Recipe System UX](#5-recipe-system-ux)
6. [Privacy & Trust UX](#6-privacy--trust-ux)
7. [On-the-Fly Job Detection](#7-on-the-fly-job-detection)

---

## 1. App Architecture

### The Core Tension

Pulse is a **proactive background assistant** -- which means the architecture decision isn't primarily about UI framework, it's about *background execution*. A beautiful cross-platform UI is worthless if the app can't watch for context and act on it while the user is doing something else.

This changes everything about how you evaluate frameworks.

### Option Comparison

#### Option A: Flutter (Recommended for MVP)

**Why it works for Pulse:**
- Single codebase for iOS, Android, macOS, Windows -- true multiplatform with one team
- AOT-compiled Dart: fast startup, low memory overhead (critical for background tasks)
- `flutter_background_service` and platform channels give you a path to real native background execution
- Strong ecosystem for the integrations Pulse needs: `google_sign_in`, `googleapis`, calendar APIs
- 60/120fps rendering via Impeller -- the UI will feel premium

**Tradeoffs:**
- Background execution still routes through native platform APIs (you're not escaping iOS limits)
- Desktop support (Windows/macOS) is good but not as polished as mobile -- some native UI conventions need extra work
- Dart is a smaller talent pool than JS/Swift/Kotlin

**Background approach in Flutter:**
- Mobile: `flutter_background_service` -> runs a Dart isolate as a foreground service (Android) or uses BGTaskScheduler (iOS)
- Desktop: proper system daemon via platform channels or a companion native process

---

#### Option B: React Native + Tauri (Hybrid)

**Why it's tempting:**
- Largest developer ecosystem (JavaScript)
- Tauri 2.0 covers Windows/macOS/Linux with Rust backend -- tiny binaries, low memory
- React Native new architecture (JSI) is genuinely fast now

**Why it's complicated for Pulse:**
- You're essentially maintaining *two* separate frameworks (RN for mobile, Tauri for desktop) with a shared business logic layer
- Background processing in React Native is still a pain: `react-native-background-fetch` works but has quirks
- The integration story between RN and Tauri is not battle-tested for a live assistant

**Verdict:** More complexity for marginal benefit unless you're JS-first team.

---

#### Option C: Native (Swift + Kotlin)

**Why it's the "right" answer technically:**
- Maximum control over background execution, battery usage, OS integrations
- No framework abstractions between you and `BGTaskScheduler` / `WorkManager`
- Best-in-class notification handling, widget support, Live Activities (iOS), Dynamic Island

**Why it's wrong for a startup:**
- Two completely separate codebases = 2x everything: dev time, bugs, feature lag
- Shared AI/business logic needs a separate layer anyway (maybe Rust/C++)
- Very high burn rate

**Verdict:** Consider native for v2 on the platform that gets traction first. Build a bridge to your business logic in Rust/shared library so the migration isn't starting from scratch.

---

#### Option D: Electron (Hard No)

Memory hungry (100MB+ baseline), bad battery story, no real background service architecture. Fine for dev tools. Not for an always-on assistant. Cross it off.

---

### **Recommendation: Flutter (Mobile MVP) + Tauri (Desktop companion)**

**Phase 1 (0-6 months):** Flutter for iOS + Android. This is where users are, this is where the always-on assistant story is validated or killed.

**Phase 2 (6-12 months):** Tauri desktop app for Windows/macOS. Tauri's Rust backend is actually *ideal* for a desktop daemon -- lightweight, full system access, no sandbox restrictions.

**Architecture diagram (conceptual):**

```

                    PULSE CORE (Shared)                   
        
   Recipe Engine    AI Inference    Context Watch  
   (Dart/Rust)      (Cloud API)     (Platform)     
        

                         
        
                                         
   Flutter           Flutter           Tauri
   (iOS)            (Android)        (Windows/Mac)
```

**The daemon model:** On desktop (Tauri), Pulse runs a persistent Rust daemon as a system service. It watches file changes, clipboard, calendar events, and pushes context to the AI layer. The Flutter UI just surfaces the results. This is the right architecture for desktop -- lightweight, battery-friendly, full access.

---

## 2. Onboarding Flow

### Research: Best-in-Class Onboarding

**Duolingo:** Delivers value *before* asking for commitment. You learn a sentence before you create an account. Teaches the core loop in the first 3 minutes. Progressive commitment escalation -- small asks build toward big ones.

**Superhuman:** Concierge onboarding (white-glove 30-min call). Signals premium positioning. Teaches keyboard shortcuts by doing, not watching. Creates a "I'm already good at this" feeling early.

**Calm:** Asks what you need ("reduce stress", "sleep better", "focus") before showing you anything. Every subsequent step feels personally relevant. Uses calm animation and audio to model the product's purpose from screen 1.

**Notion:** Shows a pre-built workspace tailored to your use case. You're not starting blank -- you're *editing* something that already works. Dramatically reduces setup anxiety.

**Key patterns to steal for Pulse:**
1. Value before commitment (show a sample "Pulse moment" before permissions)
2. Role-based personalisation from step 1
3. Progressive permission requests (don't ask for everything upfront)
4. Trust building as an explicit feature, not an afterthought
5. A "first win" within 24 hours

---

### Pulse Onboarding Flow (Step-by-Step)

#### Screen 0: The "What Is This" Moment (Pre-signup)

**Mockup description:**  
Dark background. Centered. Animated icon -- a small pulse/heartbeat line that morphs into a subtle notification badge.

Copy:  
> **"Pulse knows what you need before you ask."**  
> *A proactive assistant that watches your work and reaches out -- at the right moment, with the right nudge.*

Below: Three short animated vignettes (auto-playing, 4 seconds each):
- *"Your 3pm call just moved. You've got a conflict -- here's a reschedule link."*
- *"You haven't replied to Marcus in 4 days. His project deadline is tomorrow."*
- *"Looks like you're writing a proposal. Here's the client's last email for context."*

CTA: **"Try Pulse free"** | Small link: "See how it works ->"

**Design principle:** Show the product promise viscerally, before any friction.

---

#### Screen 1: Job Type Selection (The Recipe)

**Mockup description:**  
Title: **"What kind of work do you do?"**  
Subtitle: *"Pulse uses this to decide what's worth your attention."*

Grid layout (2 columns, scrollable). Cards with icon + label + one-liner:

```
  
   Freelancer        Account Mgr  
  Client work,        Relationships   
  invoices, comms     & pipelines     
  
  
   Developer         Designer     
  PRs, deploys,       Feedback, briefs
  incidents           & revisions     
  
  
   Marketer          Founder      
  Campaigns,          Everything,     
  metrics, copies     all the time    
  
         [   My job isn't here  ]
              (triggers AI flow -- see Section 7)
```

Selection: tap to highlight (checkmark appears). User can select one primary.

Below the grid: **"Don't overthink it -- you can always change this."** (reduces commitment anxiety)

CTA: **"This is me ->"**

---

#### Screen 2: Connect Your World

**Mockup description:**  
Title: **"Where does your work actually live?"**  
Subtitle: *"Pulse watches these so you don't have to."*

Integration cards, each with:
- Icon + name
- One-sentence explanation of *what Pulse watches* (not "access to calendar" -- specific)
- Connect button / Connected badge

```

    Google Calendar                    
  "Spot conflicts, prep reminders, flag  
   back-to-backs before they hurt you"  
                          [Connect]      


    Gmail / Outlook                    
  "Flag threads going cold, surface      
   replies you haven't sent"             
                          [Connect]      


    Slack                              
  "Catch messages that need you, ignore  
   the noise"                            
                          [Connect]      


    Location (optional)                
  "Know when you're commuting, in a      
   meeting room, or working late"        
                     [Maybe later]       

```

**Key design decision:** Location is optional and framed as a benefit, not buried in permissions. Each integration shows *specifically* what Pulse will do with it -- this is the trust layer baked into onboarding.

Progress pill at top:  (step 2 of 4)

CTA: **"Set up Pulse ->"** (works even with zero connected -- you can always add later)

---

#### Screen 3: Notification Preferences

**Mockup description:**  
Title: **"How should Pulse talk to you?"**  
Subtitle: *"You can change this anytime."*

**Three preset modes** (card-based, select one):

```

    Quiet Pulse                         
  Only the most important stuff           
  Max 2-3 nudges per day                  
   Good if you hate notifications       

   Default highlighted
    Active Pulse                        
  Helpful nudges when it matters          
  Typically 5-8 per day                   
   Recommended for most people          


    Full Pulse                          
  Everything Pulse notices                
  10-15+ per day                          
   For high-stakes roles                

```

Below: **Focus hours toggle** -- "Don't bother me during..."  
Time range picker: 9am-6pm shown, user can drag endpoints.

Optional: "Quiet on weekends" toggle (default: off -- user decides).

CTA: **"Almost there ->"**

---

#### Screen 4: The Trust-Building Handoff

**Mockup description:**  
Title: **"Your first week with Pulse"**  
Subtitle: *"We start slow. No spam. No surprises."*

Visual: A week timeline (Mon-Sun) with dots appearing gradually, getting denser midweek, then tapering.

Three promises, in large clear text:
```
Week 1: Pulse watches, barely speaks

  Day 1-2: Pulse learns your patterns silently

  Day 3-4: First suggestions -- calendar conflicts,
             cold email threads

  Day 5-7: You rate what's useful. Pulse adapts.
```

Below: **Feedback mechanism explained** -- "Every Pulse notification has a  / . Your ratings teach it what matters to *you*."

**Micro-copy:** *"Most users see their first genuinely useful nudge within 48 hours."*

CTA: **"Start Pulse ->"** (green, large, confident)

---

#### Post-Onboarding: The First 7 Days (Trust-Building Mode)

**Day 1-2: Silent observer**
- Pulse indexes calendar, email (past 30 days only), connected apps
- No notifications except one: "Setup complete. Pulse is watching. "
- In-app shows: "Learning your patterns... check back tomorrow"

**Day 3: First contact**
- Single notification. Deliberately chosen to be *obviously* useful
- E.g.: "You have 4 meetings tomorrow with no breaks. Want me to block lunch?"
- Rate it:  "Useful" /  "Not useful" /  "Never this type"

**Day 4-5: Calibration mode**
- Max 3 notifications/day regardless of preset
- Each shows a confidence score: "85% sure this matters to you"
- App surface: "Pulse has learned X things about how you work"

**Day 6-7: Graduation**
- Notification: "You've been using Pulse for a week. Want to see what it's learned?"
- Summary card: "I've noticed you tend to miss emails from [name]. I've started prioritising those."
- Option: "Adjust what Pulse watches" -> settings

---

## 3. The Always-On Problem

### Platform Reality Check

This is the hardest technical problem in Pulse. Here's what you're actually dealing with:

---

### iOS: The Locked Garden

**Hard constraints (no exceptions):**
- Apps are suspended ~30 seconds after entering background
- Background App Refresh (BAR): minimum 15-minute intervals, and iOS *decides* when -- you schedule a request, the OS runs it when it wants
- BAR is killed if: low battery, Low Power Mode, user disables it, or iOS deems your app "not used enough"
- Processing tasks (BGProcessingTaskRequest): up to "several minutes" but only when device is charging + idle
- You get ~30 seconds in a BAR task, up to a few minutes in a processing task
- **No persistent background process. Full stop.**

**What actually works on iOS:**

1. **Push notifications as the trigger mechanism** -- Your server watches the data (calendar, email via OAuth), detects a nudge-worthy event, sends a silent push notification (`content-available: 1`) that wakes your app for ~30 seconds to process and display a local notification. This is the correct architecture for iOS.

2. **Background App Refresh** -- Supplement for local processing (scanning cached data). Schedule a BGAppRefreshTask. iOS will run it "sometime in the next few hours." Not reliable for time-sensitive events.

3. **Significant Location Changes** -- If Pulse uses location, `CLLocationManager` can wake the app on significant movement (cell tower changes). Available even when BAG is disabled. Useful for "user just arrived at office" type triggers.

4. **Local notifications scheduled on the server** -- Server sends silent push -> app wakes -> checks context -> schedules local notification for the right moment.

**iOS architecture reality:**
```
User's phone (suspended)
       
Silent push (APNs)
       
Pulse Server watches:
  - Calendar API (Google/Apple via OAuth)
  - Email API
  - Any webhook-capable integrations
       
AI inference layer
(detects nudge-worthy moments)
```

The phone is essentially a *display terminal* for a server-side intelligence layer. This is not a compromise -- it's actually the right architecture for reliability and battery life.

**Key user friction:** Explaining to users why they need to keep "Background App Refresh" enabled. This needs to be a guided setup step with a clear benefit statement.

---

### Android: More Freedom, More Fragmentation

**The layers of restriction:**

1. **Doze Mode** -- kicks in when device is stationary, screen off, unplugged. Restricts network, wakelocks, jobs, syncs. Has "maintenance windows" where normal access is briefly restored.

2. **App Standby** -- if user hasn't used the app recently, it's bucketed. Bucket determines how often jobs can run (Active -> Working Set -> Frequent -> Rare -> Restricted).

3. **OEM Battery Optimisation** -- Samsung, Xiaomi, OnePlus all have *additional* aggressive kill switches *beyond* AOSP restrictions. This is where most "Android notification reliability" horror stories come from.

**What actually works on Android:**

1. **FCM (Firebase Cloud Messaging)** -- Same server-push approach as iOS. High-priority FCM messages can wake apps even in Doze. This is the primary mechanism.

2. **Foreground Service** -- If Pulse needs truly persistent monitoring (e.g., watching clipboard, active file work), a foreground service with a visible notification keeps the process alive. Users see a persistent notification ("Pulse is watching"). This is what alarm clocks, fitness trackers, and navigation apps use. Acceptable for a proactive assistant if the notification is designed well ("Pulse is active -- ready to help").

3. **WorkManager** -- Google's recommended API for deferrable background work. Respects Doze and battery constraints, but runs *eventually*. Good for non-time-sensitive syncs and indexing jobs.

4. **REQUEST_IGNORE_BATTERY_OPTIMIZATIONS** -- You can ask the user to exempt Pulse from battery optimisation. Should be presented as an optional "reliability upgrade" in settings, with a clear explanation. **Do not ask for this in onboarding** -- it's a red flag to users who don't trust you yet.

**Android architecture reality:**
```
Foreground Service (persistent)   Keeps process alive on flagship/premium users
       +
FCM high-priority push           Primary trigger for time-sensitive nudges  
       +
WorkManager jobs                 Background sync, indexing, non-urgent
```

**The OEM fragmentation problem:**  
Create a "Reliability Setup" screen in settings that detects OEM and provides specific instructions:
- Samsung: Settings -> Device Care -> Battery -> App Power Management -> Never sleeping apps -> Add Pulse
- Xiaomi/MIUI: Settings -> Apps -> Manage Apps -> Pulse -> Autostart -> Enable
- Link to [dontkillmyapp.com](https://dontkillmyapp.com) for long-tail OEMs

This is what apps like Tasker, Alarmy, and Headspace do. It's not elegant, but it's the only honest answer.

---

### macOS: Your Happy Path

macOS has the most permissive background execution model of any Pulse platform. A proper daemon can:
- Run as a LaunchAgent (user-level, starts on login, persists always)
- Full network access
- File system watching (FSEvents)
- Calendar access via EventKit
- Mail access via AppleScript/Automation
- No meaningful battery restrictions when plugged in
- Sandboxed (App Store) or unsandboxed (direct download) -- unsandboxed gives more power

**Tauri approach:**  
A small Rust binary registered as a LaunchAgent. Low memory (~5-15MB). Watches configured sources. Pushes events to the UI layer (Tauri webview) and fires native macOS notifications.

**Architecture:**
```
~/.config/pulse/daemon.toml  (config)
          
LaunchAgent (Rust binary, always running)
   CalendarWatcher (EventKit via FFI)
   MailWatcher (IMAP idle connection)  
   FileWatcher (FSEvents -- Documents, Desktop)
   ClipboardWatcher (polling every 5s)
   AILayer (calls cloud API on trigger events)
          
macOS Notification Center
          
Tauri UI (opens on notification tap)
```

**Battery consideration on macOS:** The Rust daemon should use event-driven patterns (not polling loops) wherever possible. FSEvents is push-based. IMAP IDLE is push-based. Calendar changes via EventKit can use change notifications. Only clipboard requires polling -- do it at 5-10s intervals, not 500ms.

---

### Windows: Underrated Platform for This Use Case

Windows actually has strong background task support via:
- **Windows Background Tasks** (UWP/WinRT) -- but restricted in modern Windows
- **Win32 service** -- full background process, most powerful option
- **Startup folder / Task Scheduler** -- user-level persistence
- **Toast Notifications** -- rich interactive notifications via Windows Notification Platform

**Tauri approach:**  
Tauri on Windows can register as a startup app and run in the system tray. The Rust backend has full Win32 access. Register as a Windows service for maximum persistence, or use Task Scheduler for lower-privilege operation.

**Windows-specific opportunity:** Deep integration with Windows Copilot APIs and the Windows AI Platform (available in Windows 11). Could differentiate Pulse on desktop vs competitors.

---

### Architecture Summary Table

| Platform | Primary Mechanism | Reliability | Battery Impact | Complexity |
|---|---|---|---|---|
| iOS | Server push (APNs) + BAR | Medium (depends on server uptime) | Low (server does work) | High |
| Android | FCM + Foreground Service | High (with OEM setup) | Medium (foreground service) | Very High |
| macOS | LaunchAgent daemon | Very High | Low (event-driven Rust) | Medium |
| Windows | Tauri tray + Task Scheduler | High | Low | Medium |

**The honest summary:** iOS is the hardest. Android is complex but doable. Desktop is relatively easy. If Pulse struggles anywhere, it'll be iOS -- and the solution is server-side intelligence, not trying to fight Apple's sandboxing.

---

## 4. Notification Design

### The Life-or-Death Problem

Proactive assistants fail in one of two ways:
1. **Too noisy** -> users disable notifications, app becomes useless
2. **Too quiet** -> users forget the app exists, churn

The goal isn't "send useful notifications." The goal is **"be the notification the user is glad they got."**

Research from notification systems:
- Users disable notifications from apps within 1 week if they feel spammed
- The acceptable rate is ~2-5 "useful" notifications per day for a proactive assistant
- Personalisation dramatically changes what "useful" means -- a developer and an account manager have completely different signal:noise ratios
- **Timing matters more than content** -- the same message at the wrong time feels intrusive

---

### The Pulse Notification Hierarchy

**Tier 1: Action-Required (Red)**  
Time-sensitive. Something will go wrong if ignored.  
Examples: meeting conflict detected, deadline in 2 hours, critical email waiting >48h  
*Frequency target: max 1-2/day*

**Tier 2: Helpful Nudge (Blue)**  
Non-urgent but genuinely useful. Can be ignored without consequences.  
Examples: email thread going cold, prep material for tomorrow's meeting, weekly review reminder  
*Frequency target: 3-5/day*

**Tier 3: Ambient Intelligence (Gray)**  
Low-priority context. Shows up in the in-app feed, not as a push notification.  
Examples: article relevant to current project, pattern Pulse noticed, usage insight  
*Frequency target: unlimited in-app, never as push*

---

### Notification Anatomy

Every Pulse notification has these elements:

```

    PULSE                              9:42 AM 
                                                
    Meeting conflict tomorrow                 
  Your 2pm with Sarah overlaps your team        
  standup. One needs to move.                   
                                                
  [Reschedule Sarah]  [Move standup]  [Ignore]  

```

**Anatomy breakdown:**

1. **App icon + name + timestamp** -- always visible, always Pulse-branded
2. **Context icon** -- tells you the source at a glance ( calendar,  email,  Slack,  location)
3. **Headline** -- one line, max 50 chars, plain English. Not "Calendar event conflict detected." Just "Meeting conflict tomorrow."
4. **Body** -- 1-2 sentences max. The context that makes the headline make sense.
5. **Action buttons** -- 2-3 max. At least one "dismiss without action." Tapping the notification body opens the full context in-app.

**What to never do:**
- Never use jargon or AI-ese ("I've identified a potential scheduling conflict in your calendar")
- Never send without at least one actionable button
- Never send the same type of notification twice in a row (vary the category)
- Never send during user's defined focus hours
- Never send at night (11pm-7am default, configurable)

---

### The Rating Feedback Loop

Every notification includes a discreet thumbs up/down. This is not just UX polish -- it's the core ML training signal.

After tapping a notification:
```

           Was this useful?              
                                         
    Yes, good catch     Not for me   
                                         
   Or: [Never notify me about this] ->    

```

Three outcomes:
- **** -> Reinforce this pattern. Send similar nudges.
- **** -> Note the miss. Downweight this category.
- **Never this type** -> Hard mute for this notification category. Logged as strong negative signal.

**The compounding effect:** After 50 ratings, Pulse's accuracy should be dramatically higher for that user than its baseline. This is the trust-building mechanism -- users who give feedback get a better product.

---

### Notification Timing Intelligence

Pulse should learn when *this specific user* is receptive:

- Track open rates by time of day
- Track which notifications get rated  vs dismissed unread
- Learn "focus windows" from calendar (if someone has 2-hour blocks, they're probably not checking their phone)
- Use device motion/usage signals (Android) to detect active vs idle periods

**The Goldilocks zone:**  
Most proactive assistant users have a window between "just finished something, brief mental gap, open to a nudge" -- typically transitions: after a meeting, before the next task starts, during a commute. Learn this per user.

---

### Anti-Patterns to Avoid

| Pattern | Why It Kills Engagement |
|---|---|
| "Just checking in" notifications | Zero value. Pure noise. |
| Sending at the same time every day | Feels like cron job, not intelligence |
| Long body text | Nobody reads it. If it needs more than 2 lines, it's not a notification -- it's an email |
| Multiple notifications in quick succession | Feels like spam, triggers "mark as spam" reflex |
| Generic notifications ("You have things to do") | Lazy. Users see through it. |
| Notifying about things users can't act on | Creates anxiety with no resolution |

---

## 5. Recipe System UX

### The Concept

A "Recipe" is a curated profile of:
- **What Pulse watches** (integrations + signals)
- **What counts as nudge-worthy** (relevance thresholds)
- **How it communicates** (tone, frequency, format)
- **What it ignores** (noise filters)

Recipes let users get a well-tuned Pulse out of the box without weeks of manual calibration. Think of them as the equivalent of iPhone's default apps for different users -- sensible defaults, fully customisable.

---

### Recipe Discovery UI

**Mockup: Recipe Library screen**

```

   Back        Recipe Library               Search 

                                                      
   Recommended for you                              
                 
    Founder         Developer                 
     1.2k         3.8k                 
   "Keeps me on      "Perfect for                
    top of every-     async teams"               
    thing"                                       
                 
                                                      
   Trending                                         
                 
    Growth Hkr      Deep Work                
     892          2.1k                 
   "Great for        "Fewer nudges,              
    launch week"      higher signal"             
                 
                                                      
  Browse by category:                                 
  [Creative] [Technical] [Sales] [Management] [+more] 
                                                      

```

**Key design principles:**
- App Store-style card browsing with ratings and review counts
- Social proof front and center -- "3,800 developers use this"
- User-generated quotes as social proof
- Category filters + search
- "Recommended for you" based on job type selected in onboarding

---

### Recipe Detail Screen

```

        Developer Recipe                    Save  

                                                      
    4.8    3,847 users    Updated 2 weeks ago 
                                                      
  "The only assistant that actually understands       
  how software development works."                    
  -- Maya R., Senior Engineer at Stripe               
                                                      
     
    What this recipe watches:                      
     GitHub -- PR reviews, CI failures             
     Calendar -- standup prep, sprint reviews      
     Slack -- mentions, DMs > 4 hours old          
     Email -- critical + client threads only       
     
                                                      
     
    What it ignores:                               
     Marketing emails                             
     Slack #general and #random                   
     Calendar events < 30 min                     
     
                                                      
  Sample nudges:                                      
   "PR #247 has been waiting for your review 6h"    
   "Jenkins failed on main -- 3 commits ago"         
   "You're in 4 meetings tomorrow, no prep time"    
                                                      
       [   Use This Recipe  ]   [Customise First]   
                                                      

```

---

### Recipe Customisation

After tapping "Customise First":

```

    Customise: Developer Recipe                      

                                                      
  Notification sensitivity           [] Quiet    
                        [] Balanced  default
                        [] Full              
                                                      
  What to watch:                                      
   GitHub PRs + CI          [Configure ->]           
   Calendar conflicts        [Configure ->]           
   Slack DMs                 [Configure ->]           
    Email threads             [Connect email first]  
    Linear/Jira tickets       [Connect ->]            
                                                      
  Tone:                                               
   Casual    Professional    Terse                 
                                                      
  Focus hours (no notifications):                     
                        
  6am         12pm        6pm       12am             
  Drag to set protected time                          
                                                      
  Advanced:  [Edit raw recipe JSON] (power users)     
                                                      
      [Save & Activate]                               

```

**Power user escape hatch:** "Edit raw recipe JSON" lets technical users tune the recipe at the parameter level. This is important -- developers will want full control, and giving them an escape hatch makes the default UX more trustworthy.

---

### Recipe Sharing

Users can submit their custom recipes to the community library:
- Name your recipe
- Write a one-sentence description  
- Tag it (role + tools)
- Optional: write a longer description

Community recipes show: submitter username, star rating, number of users, last updated date. Flagging system for low-quality submissions. Staff picks section for high-quality curated recipes.

**Incentive:** Users with top-rated recipes get a "Pulse Expert" badge on their profile and early access to new features.

---

## 6. Privacy & Trust UX

### The Trust Gap

Users handing an app access to their calendar, email, and location are making a significant trust decision. Most privacy policies fail because they're:
- Written for lawyers, not users
- Shown at the worst possible moment (the "I Agree" barrier)
- Framed as legal protection for the company, not a promise to the user

Pulse should be radically transparent -- not because it's legally required, but because **trust is the product**.

---

### Privacy Principles for Pulse

**1. Plain English, always.** Not "We may process your personal data in accordance with GDPR Article 6(1)(b)" -- just "We read your calendar to spot conflicts. We never store your email content."

**2. Show your work.** Every notification should be traceable to the source. "I flagged this because: email from Marcus, 4 days no reply, he's in your 'Important' contacts."

**3. Data minimisation visible to users.** Show them the footprint: what you've indexed, when you last synced, what you've deleted.

**4. Control without friction.** Revoke access with one tap. Delete all data with one tap. No "are you sure? are you really sure?" dark patterns.

---

### The "Pulse is Watching" Dashboard

A dedicated screen showing exactly what Pulse has access to, in real-time:

```

       What Pulse Can See                            

                                                      
   Calendar                              Connected  
  Last synced: 2 min ago                             
  Sees: Event titles, times, attendees               
  Doesn't see: Private notes, personal events        
  Events indexed: 847 (last 90 days)                 
  [Manage]  [Revoke]                                 
                                                      
   Gmail                                 Connected  
  Last synced: 8 min ago                             
  Sees: Sender, subject, date only                   
  Doesn't see: Email body content                    
  Threads tracked: 234 (unarchived)                  
  [Manage]  [Revoke]                                 
                                                      
   Slack                                 Connected  
  Sees: Channels you're in, messages to you          
  Doesn't see: DMs you're not part of, private       
              channels you haven't joined             
  [Manage]  [Revoke]                                 
                                                      
   Location                             Off         
  [Turn on]                                          
                                                      
    
  Your data is processed in: Frankfurt, EU           
  Stored for: 90 days (configurable)                 
  Shared with: Nobody                               
                                                      
  [Download My Data]   [Delete Everything]           
                                                      

```

**Design principle:** This screen should feel like looking through a window, not reading a policy. Specificity builds trust -- "we index event titles but not private notes" is more reassuring than "we access your calendar."

---

### Permission Request Timing

Never ask for all permissions at once. The research is clear: batch permission requests kill conversion.

**Permission sequence:**
1. **Onboarding step 2:** Calendar -- first ask, lowest risk, highest value
2. **After first calendar nudge:** "Want me to watch email too? I can catch threads going cold."
3. **After 3 positive ratings:** "Some users find location helpful for commute timing. Want to try?"
4. **Never surfaced unless asked:** Microphone, contacts

**The ask pattern for each permission:**
```
Before tapping [Connect]:
-> What Pulse will see (plain English)
-> What Pulse will never see
-> Why this makes Pulse better for you specifically
-> How to revoke it
-> [Connect] / [Not now]
```

---

### Trust-Building Moments

These are designed interactions that demonstrate trustworthiness through action:

**"I didn't act on that"** -- Occasionally, Pulse should surface: "I noticed you had an email from X but decided it wasn't important enough to nudge you about. Was that right?" This shows restraint, which is rare and trustworthy.

**Transparency reports** -- Weekly: "Here's what Pulse noticed but chose not to bother you about." Shows the filter is working.

**Data birthday notifications** -- "Your data from 90 days ago was just deleted." Nobody sends these. It would be remarkable and trust-building.

**Incident communication** -- If Pulse sends a wrong or intrusive notification, the next interaction should acknowledge it: "That nudge yesterday about [X] was a miss. I've adjusted my threshold."

---

## 7. On-the-Fly Job Detection

### The Problem

The recipe library covers the 80% case -- developer, designer, marketer, account manager, etc. But:
- A "Technical Due Diligence Specialist at a VC firm" is not in any library
- A "Chief of Staff at a biotech startup" needs a very specific recipe
- A user who selects "My job isn't here" needs a path that feels premium, not broken

This is actually an opportunity to demonstrate Pulse's core AI capability *during onboarding*.

---

### The Flow

**Step 1: Trigger**  
User taps " My job isn't here" on the recipe selection screen.

---

**Step 2: Tell Me More**

```

                                                     
                                                      
          Let's build your recipe                   
                                                      
  Tell me about your work in a sentence or two.       
  Don't overthink it.                                 
                                                      
    
   e.g. "I'm a freelance UX researcher who works    
   with startups on product validation..."          
                                                    
   _                                                
    
                                                      
  Or just tell me your job title:                     
                     
   Job title (optional)                            
                     
                                                      
                       [Build My Recipe ->]            
                                                      

```

**UX note:** Free text is the primary input. Job title is secondary. The free text trains the AI better and also feels like Pulse is actually listening, not just looking up a table.

---

**Step 3: Pulse is Thinking (The Magic Moment)**

```

                                                      
            Building your recipe...                 
                                                      
   Researching "Technical Due Diligence Specialist"  
                                                      
     65%                          
                                                      
   Found it. Here's what I learned:                  
                                                      
   "This role involves rapid deep-dives into         
    technical stacks -- usually 1-2 week sprints.     
    High email volume from portfolio companies.      
    Calendar is project-sprint-based, not routine." 
                                                      
   Building your notification model...               
                                                      

```

**Technical implementation:**
- On "Build My Recipe", send user input to AI layer
- Prompt: "Research this job role: [input]. Identify: primary tools/apps used, communication patterns, common time pressures, what constitutes an urgent event vs background noise for this role. Output as structured JSON."
- Parse response into a recipe template
- Total time: 3-8 seconds (acceptable for a "we're building something custom" moment)
- Show progress indicator with genuine AI output snippets to make the wait feel productive

**Error handling:** If AI can't confidently identify the role (confidence < 0.7), fall back to: "This role is pretty unique -- let's start with a base recipe and you can tune it." -> offer top 3 closest recipes.

---

**Step 4: Review Your Custom Recipe**

```

       Your Custom Recipe                     Edit  

                                                      
   Built for: Technical Due Diligence Specialist    
                                                      
  Based on your description, I'll watch for:         
                                                      
   Email from portfolio founders (high priority)   
   Calendar: new meeting requests during sprints    
   Data room / file sharing notifications          
   Deadline proximity (sprint end dates)           
                                                      
  I'll go easy on:                                    
   Slack (not your primary channel?)                
   Recurring team standups                          
                                                      
  Does this sound right?                             
                                                      
     
     Mostly yes, let's go                         
    ~ It's close but needs tweaking                
     No, let me start over                        
     
                                                      

```

If "needs tweaking" -> inline editing of each bullet point (toggle on/off, adjust priority level).

---

**Step 5: Name and Save**

```

                                                      
  Give your recipe a name:                           
    
   Tech Due Diligence                               
    
                                                      
  Share with the Pulse community?                    
  Others with similar roles could benefit.           
                                                      
   Keep it private    Share anonymously            
                                                      
  [Activate Recipe]                                  
                                                      

```

**The community flywheel:** Custom AI-generated recipes that get shared and rated become the recipe library's long tail. Every niche job that users describe trains the system. Over time, the library grows without manual curation -- it's a crowdsourced recipe graph where AI fills the gaps.

---

## Appendix: Key Technical Decisions Summary

| Decision | Recommendation | Rationale |
|---|---|---|
| Mobile framework | Flutter | True cross-platform, best background service story, fast |
| Desktop framework | Tauri (Rust) | Lightweight daemon, full system access, tiny binaries |
| iOS background | Server-push via APNs | Only reliable approach given Apple's sandboxing |
| Android background | FCM + Foreground Service | FCM for realtime, service for persistent monitoring |
| macOS background | LaunchAgent (Rust daemon) | Full permissions, event-driven, low memory |
| Windows background | Tray app + Task Scheduler | Good enough for v1, Windows service for v2 |
| Recipe storage | JSON, version-controlled | Human-readable, shareable, diffable |
| AI inference | Cloud API (server-side) | Avoids on-device limits; enables server-push trigger model |
| Privacy model | Data minimisation + transparency dashboard | Trust is the product |

---

## Open Questions for Next Research Phase

1. **Monetisation model** -- Free tier with N notifications/day? Pro subscription for unlimited + custom recipes? Enterprise tier for teams?
2. **The "why Pulse and not a widget/shortcut"** story -- How do we clearly differentiate from iOS/Android's built-in focus modes and smart notifications?
3. **Offline behaviour** -- What happens when the server can't reach the device? Queue and batch? Skip and move on?
4. **Recipe versioning** -- When a recipe creator updates their recipe, do all users get the update? How do you handle breaking changes?
5. **Team/shared recipes** -- Can a company deploy a standard Pulse recipe to all employees? B2B angle.
6. **Notification explainability** -- How much detail should be shown about *why* Pulse sent a nudge? Power users want this; mainstream users might not care.

---

*Next document: `technical_architecture.md` -- detailed backend spec, AI inference pipeline, data models.*
