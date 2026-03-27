# Pulse Integration Strategy & Onboarding Experience
*Product Research Document -- March 2026*

---

## The Thesis

The moment a user connects their first integration and receives their first unsolicited, contextually correct notification is the product's entire value proposition made real. Everything before that moment is friction. Everything after it is retention. Design accordingly.

**The metric that matters:** Time from app install -> first "holy shit" notification. Target: under 4 minutes.

---

## 1. The Integration Connection UX

### How Successful Apps Handle OAuth

**Zapier** -- The market standard. Introduces connections as a "step" in building an automation. You're never asked to connect an app in isolation -- you connect it *because* you're building something. The connection feels purposeful, not extractive. They use a modal that shows the app logo, what's being connected, and a single CTA. OAuth opens in a popup (not a redirect), which keeps the user in context. Critical insight: Zapier makes you connect apps as part of achieving something, not as a prerequisite for someday maybe achieving something.

**Linear** -- Connections are optional at every stage. When you create a project, Linear surfaces "connect GitHub to link PRs" inline, in the exact moment it becomes useful. This is contextual triggering -- you earn the right to ask for a connection by first demonstrating why it matters, in context.

**Notion** -- Role-based onboarding first ("I'm a student / designer / engineer / manager"). Then templates. Then integrations if and when you need them. Notion's insight: get the user to value-land first, then sell integrations as power-ups, not entry fees.

**IFTTT** -- Pioneered the "applet" model: two services, one trigger, one action. Dead simple. But they over-rely on users understanding what they want before they've seen what's possible. Their browse-first model means low intent discovery. Good for browsing, bad for onboarding.

**Superhuman** -- Doesn't have traditional integrations, but its onboarding is the gold standard for trust. White-glove, 1-on-1 Zoom sessions. A real person walks you through your *own* inbox. The lesson: when trust is the barrier, human presence dissolves it faster than any UI copy. Pulse should borrow this for early adopters -- offer a 15-minute "setup call" option as an alternative to self-serve.

**Make (formerly Integromat)** -- Visual flow builder. High power, but integration connection is buried in complexity. The wrong direction for consumer apps.

---

### What Makes a Connection Feel Trustworthy vs Scary

**Trustworthy signals:**
- App logo prominently displayed before OAuth redirect
- Plain-English explanation: *"We'll read your calendar to detect meetings. We won't modify anything."*
- Minimal scope request -- ask for read-only when you don't need write
- "You can disconnect anytime" stated explicitly, with a link to where
- Connection flow stays in-app (popup, not full redirect) when possible
- Show what you *won't* do, not just what you will
- Progress is saved if they pause halfway

**Scary signals:**
- Generic "This app wants access to your Google Account" with a wall of scopes
- Redirect that takes them away from your app with no clear return
- Requesting write permissions when you only need read
- No explanation of why a permission is needed
- Asking for everything at once
- Checkbox lists of permissions with no hierarchy or emphasis

**The pattern that works best:** Before launching OAuth, show a single explanatory card:

```

    Connect Google Calendar            
                                         
  Pulse will:                            
   Read your upcoming events            
   Detect meeting context               
                                         
  Pulse will never:                      
   Create or modify events              
   Access other Google services         
                                         
  [Connect Calendar]   [Not now]         

```

One service per card. Never bundle them. The "Not now" must be visible -- hiding it signals desperation and kills trust.

---

### Communicating Access Without Privacy Policy Vibes

The wall-of-text privacy policy is a trust failure, not a trust signal. Nobody reads it. Nobody trusts it.

**What works:**

1. **Icon + verb pairs.** " Read events" / " Read emails" / " Never writes". Visual, scannable, instant.

2. **Just-in-time explanations.** When requesting calendar access: *"So Pulse can brief you 5 minutes before your next call."* One sentence. Tied to a specific, tangible benefit.

3. **The "why now" frame.** Never ask for a connection before the user understands why they'd want it. Show a simulated notification first: *"Here's what you'd have seen this morning if Pulse was connected..."*

4. **Scope laddering.** Start with read-only. Add write permissions only when the user explicitly asks for a feature that requires it. Never ask for more than the current feature needs.

5. **Visible data trail.** Show users exactly what Pulse saw and why it acted. "I noticed you have a meeting with Sarah at 2pm. Her last email mentioned a budget concern, so I flagged it." Transparency is the product.

---

### Ideal Number of Integrations to Request in Onboarding

**The answer: 1.**

Ask for exactly one integration during the setup flow. Make it the most impactful one (calendar, almost always). Let the first proactive notification speak for itself. Then, in that notification, surface the offer to connect more.

The psychological pattern:
- 1 integration: Low commitment, high curiosity. Users say yes.
- 2-3 integrations: Medium friction. Completion rate drops ~40%.
- 4+ integrations: Users feel like they're being processed. Bail.

**Zapier's mistake**: Zapier shows you 100+ apps on first load. Overwhelming. Users freeze.

**The right model**: Airbnb's "one more step" pattern. Complete one step, see value, get invited to the next step. Never show the full staircase upfront.

---

### Handling Partial Connections

When a user connects calendar but not email, don't block them or nag them. Do this:

1. **Activate immediately with what you have.** Start sending calendar-based notifications right away. Establish the habit loop before pushing for more.

2. **Show the gap, not the ask.** In a notification: *"I noticed your 3pm call with Marcus. I could have pulled his last email to brief you, but you haven't connected Gmail yet. [Connect now ->]"*

3. **Soft capability unlock.** In settings, show all integration slots with a "locked" state that previews what unlocking does. Not guilt -- curiosity.

4. **Never block the flow.** A partial connection is still a connection. Don't make users feel like they failed onboarding by not connecting everything.

---

## 2. The "First Moment of Value" Design

### The Fastest Path: Download -> "Holy Shit"

**Target: 4 minutes from install to first notification.**

```
Install (0:00)
  
Signup -- email + name only, no phone, no credit card (0:30)
  
Role selector -- 5 options, pick one (1:00)
  
Single integration connect -- Calendar only (2:00)
  
"Scanning your next 48 hours..." animation (2:15)
  
First notification appears (3:30-4:00)
```

The signup screen should have exactly 2 fields. Not 4. Not 6. Two. The role selector should be big tappable tiles with icons, not a dropdown. The calendar connection should be one button tap that opens OAuth in a sheet -- no intermediate screens.

**The waiting moment is critical.** While Pulse scans, show: *"Looking at your week... Found 3 meetings in the next 24 hours. Checking for context..."* Progress copy, not a spinner. This teaches the user what Pulse is doing and builds anticipation.

---

### The ONE Integration

**Google Calendar (or Apple Calendar).** Every professional has one. It's read-only. The scope is narrow and understood. And it immediately unlocks the most universal use case: pre-meeting briefs.

Why not email?
- Email feels more invasive. "Reading my emails" triggers more anxiety than "reading my calendar."
- Calendar has a clear structure -- events have participants, titles, times. Immediate actionable signal.
- The mental model is simple: Pulse watches your schedule.

Why not Slack?
- Not universal. Work-specific.
- Notifications from Slack are high-volume and lower-signal.
- No natural "wow" moment tied directly to Slack alone.

Calendar is the keystone integration. Everything else is additive.

---

### The First Notification Design

This notification must be designed to be unmistakably different from every other notification the user gets. It should feel like a thoughtful colleague tapped them on the shoulder.

**Bad first notification:**
> "You have a meeting in 30 minutes."

That's a calendar app. That's not Pulse.

**Good first notification:**
> " You've got a call with Jamie at 2pm (30 min). Last time you two spoke, you were aligned on Q2 budget. The meeting has no agenda set -- want me to draft one?"

That's Pulse. Context + history (when available) + optional action. Three layers in one push.

**The rule:** The first notification must demonstrate something the calendar app *cannot* do. It must prove that Pulse is reading between the lines, not just reading the lines.

---

### Time Target: < 4 Minutes to First Notification

This requires:
- Immediate calendar sync on OAuth complete (no "your calendar syncs every hour" garbage)
- Pre-computation of the next 48 hours on first connect
- Instant notification trigger if there's an event within 2 hours
- If no event within 2 hours: generate a morning brief for tomorrow

The worst UX pattern: connecting the integration and then... silence. If nothing fires for 12 hours, the user forgets why they connected it. **If there are no upcoming events, send a daily digest immediately.** Never let the post-connection moment fall flat.

---

## 3. Integration Tiers / Progressive Disclosure

### Quick Start (Days 1-3): The Core 3

| Integration | Why |
|---|---|
| Calendar (Google or Apple) | Keystone. Meeting briefs, schedule awareness. |
| Email (Gmail or Outlook) | Context for who you're meeting, follow-up detection. |
| Slack | Async context, action item detection. |

These three together unlock: pre-meeting briefs, follow-up reminders, action item tracking, schedule-aware Slack summaries.

**Don't ask for all three on day 1.** Ask for Calendar. On first notification, offer Gmail. After first Gmail-enhanced notification, offer Slack.

---

### Power User (Week 2+): Role-Specific Add-Ons

| Category | Integrations |
|---|---|
| Sales | Salesforce / HubSpot, LinkedIn, Gong |
| Engineering | GitHub, Linear, Jira |
| Management | Asana, Notion, Google Drive |
| Finance | QuickBooks, Stripe |
| Personal | Todoist/Things, WhatsApp (limited), Apple Health |

Show these through the recipe system (see Section 6), not as a raw list.

---

### Showing What Users Are Missing

**Don't use empty states.** Use "preview notifications" -- ghost versions of what a notification would have said if the integration was connected.

Example (in notification feed, faded/greyed out):
>  *"If Gmail was connected, I'd have briefed you on Marcus's pricing email before your 2pm call. [Connect Gmail]"*

This is a concrete, contextual, in-the-moment demo of what the integration would have done. It's infinitely more persuasive than a feature list in settings.

Another pattern: the **Integration Health Card** in the app dashboard.

```
Your Pulse is 40% connected


Connected: Calendar 
Missing: Email -- add this to get pre-meeting email context
Missing: Slack -- add this to catch action items in channels
```

Progress bar creates completionist pull. Use it.

---

### Recipe-Based Onboarding

Role selector on signup screen (big tiles, not dropdown):

```
I'm a...
[ Sales Rep]  [ Engineer]  [ Manager]
[ Designer]  [ Exec]      [ Other]
```

Each role auto-selects a recipe. User doesn't see a list of 50 integrations -- they see "Your Sales Stack" with 3-4 relevant connections pre-selected.

This reduces cognitive load from "which of 300 integrations should I connect?" to "do I want to use the sales pack?" (Yes, obviously.)

---

## 4. Integration Categories: Value-to-Friction Matrix

### The Matrix

| Integration | Value | Friction | Strategy |
|---|---|---|---|
| Google Calendar |  Very High |  Very Low | **Connect first, during onboarding** |
| Apple Calendar |  Very High |  Very Low | **Connect first (iOS), during onboarding** |
| Gmail |  Very High |  Medium | Connect second, after first calendar notification |
| Outlook |  Very High |  Medium | Same as Gmail for M365 users |
| Slack |  High |  Medium | Connect third, sell with action item detection |
| Google Drive |  Medium |  Medium | Power user tier, sell with doc-before-meeting feature |
| GitHub |  Medium |  Low | Engineers only -- recipe-triggered |
| HubSpot / Salesforce |  Very High (for sales) |  High | Sales recipe only; guide them through it manually |
| Notion |  Medium |  Medium | Productivity recipe |
| Linear / Jira |  Medium |  Medium | Engineering recipe |
| WhatsApp |  High |  Very High | Skip for v1 -- no official API |
| Twitter/X |  Low |  Very High | Don't bother -- cost > benefit |
| Todoist / Things |  Medium |  Low | Personal recipe only |
| Spotify / music |  Low |  Very Low | Novelty, not value -- skip |
| Apple Health / Fitbit |  Medium |  Medium | Wellbeing recipe -- "Your focus time is low today" |

### Priority Stack (in order of when to surface to user)
1. Google/Apple Calendar
2. Gmail / Outlook
3. Slack
4. Role-specific CRM or project tool
5. Everything else (power user settings)

---

## 5. Technical Integration Architecture

### OAuth Token Storage

**Never store tokens in plaintext.** This is table stakes.

- **Access tokens:** Store in encrypted column (AES-256) in your database. Short-lived (typically 1 hour for Google). Retrieved from memory/cache during request window.
- **Refresh tokens:** Store encrypted, separately from access tokens. Column-level encryption + field-level encryption if your database supports it. Consider AWS Secrets Manager or HashiCorp Vault for the encryption key itself.
- **Key rotation:** Refresh tokens must survive key rotation. Build rotation into your token vault from day one -- retrofitting it is painful.
- **Per-user encryption keys:** Derive a unique key per user from a master key + user UUID. This limits blast radius if one user's data is compromised.

```
User -> encrypted_access_token (expires 1h)
     -> encrypted_refresh_token (long-lived, used to get new access tokens)
     -> token_expires_at (unix timestamp)
     -> scopes_granted (json array)
     -> connected_at
     -> last_used_at
```

**Refresh strategy:** Before every API call, check if the access token expires within 5 minutes. If yes, refresh proactively. Never let a token expire mid-request. Queue a background refresh if `last_used_at` is recent.

---

### Webhook vs Polling -- Per Integration

| Integration | Strategy | Reason |
|---|---|---|
| Google Calendar | **Webhook (Push)** | Google Calendar API supports push notifications via channel registration. Near-realtime event changes. |
| Gmail | **Webhook (Push via Pub/Sub)** | Gmail supports push via Google Pub/Sub. Use `watch()` API. Refresh watch every 7 days. |
| Outlook / Microsoft 365 | **Webhook (Graph API subscriptions)** | Microsoft Graph subscriptions. Renew every 3 days. Fallback to polling on failure. |
| Slack | **Webhook (Event API)** | Slack's Events API is mature. Subscribe to `message`, `reaction_added`, `channel_archive`. |
| GitHub | **Webhook** | GitHub webhooks are reliable. Retry on 5xx. |
| HubSpot | **Webhook** | HubSpot has a webhook API. Use it for deal/contact changes. |
| Salesforce | **Polling (Streaming API)** | Salesforce's Streaming API is effectively push, but via CometD long-polling. Works well. |
| Notion | **Polling (15 min)** | Notion's API has no webhooks. Poll the databases/pages you care about. Cache last `last_edited_time`. |
| Linear | **Webhook** | Linear has webhooks for issues, projects, cycles. Reliable. |
| Todoist | **Webhook** | Todoist supports webhooks for task creation/completion. |
| Apple Calendar | **Polling (EventKit, iOS only)** | No server-side webhook. On iOS, use EventKit with background fetch. |

**Hybrid pattern for unreliable webhooks:**
Register webhook + set a polling fallback at 15-minute intervals. If webhook fires, skip the next poll cycle. If polling detects changes not caught by webhook, log and investigate. This gives you realtime delivery with resilience.

---

### Handling Revocation and Disconnection

When a user revokes access (from your settings or from Google's security page):
1. Google/Slack/Microsoft will invalidate the token immediately
2. Your next API call returns 401 or a specific error code
3. On 401: clear the stored tokens, mark the integration as `disconnected`, send in-app notification: *"Your Google Calendar connection was disconnected. Pulse can't send meeting briefs without it. [Reconnect ->]"*
4. Never retry indefinitely on auth failure -- after 3 consecutive 401s, back off and notify

**Graceful degradation:**
When an integration disconnects, don't fail silently. Show in the notification feed:
>  *"Google Calendar disconnected. I can't prep your 2pm call today. [Fix this ->]"*

This turns a failure into a re-engagement moment.

**Voluntary disconnection flow (from settings):**
- "Remove [Gmail]" button
- Confirmation: "Removing Gmail means Pulse won't be able to brief you on email context before meetings. Are you sure?"
- On confirm: revoke token via API, delete from DB, show confirmation
- Log the reason if they provide one (dropdown: "Privacy concern / Not useful / Switching accounts / Other")

---

### Multi-Account Support

This is underbuilt by most apps and massively undervalued by users who have work + personal accounts.

**Data model:**
```
User (1)
  IntegrationAccounts (many)
        provider: "google"
        provider_account_id: "user@work.com"
        label: "Work"           user-editable
        encrypted_tokens: ...
        scopes: [...]

       provider: "google"
       provider_account_id: "user@personal.com"
       label: "Personal"
       ...
```

**UX pattern:** In the integrations section, show each connected account as a separate chip with its label. "Work Google" / "Personal Google." Allow adding a second Google account with a clear "Add another Google Account" button that goes through a fresh OAuth flow with `prompt=select_account` to force account chooser.

**Cross-account intelligence:** Allow users to set rules: "Work calendar + Work email are paired. Personal calendar stands alone." Pulse should know not to mix work meeting briefs with personal email context.

---

## 6. The Recipe Concept

### What a Recipe Is

A Recipe = a named bundle of:
- Required integrations (must connect for recipe to activate)
- Optional integrations (enhance but don't block)
- A set of trigger rules (what events matter)
- Notification templates (how Pulse talks about those events)
- A persona/context frame ("as a Sales Rep, what matters to you")

Recipes are the product's opinion about what's useful for a type of person. They replace the blank-slate "connect whatever you want" model with something that feels curated and human.

---

### How Recipes Present to Users

**On signup (role selector):**
Each role tile previews the recipe:

```
 Sales Rep

"Pre-meeting deal briefs, 
follow-up reminders, 
pipeline change alerts"

Connects: Calendar + Gmail + HubSpot
```

One tap installs the recipe and queues up the connection flow for the required integrations, in order. The user connects Calendar -> Gmail -> HubSpot one at a time, with recipe-specific copy:
*"Connect Gmail so Pulse can pull the prospect's last email before your call."*

Not generic OAuth. Tied to a specific outcome the user already said they want.

---

### Built-In Recipe Library (v1)

| Recipe | Required | Optional | Key Notifications |
|---|---|---|---|
| **Sales Rep** | Calendar, Gmail | HubSpot/Salesforce, LinkedIn | Pre-call brief, follow-up reminder, deal stage change |
| **Engineering Lead** | Calendar, Slack | GitHub, Linear | PR review requests, blocked PRs, standup summary |
| **Executive** | Calendar, Gmail, Slack | Google Drive, Notion | Daily brief, key email surface, decision nudges |
| **Founder** | Calendar, Gmail | Slack, Linear, Stripe | Meeting brief, key deal emails, MRR change |
| **Designer** | Calendar, Slack | Notion, Figma (polling) | Review requests, feedback threads, weekly digest |
| **Student / Personal** | Calendar, Gmail | Todoist, Apple Health | Assignment reminders, focus time blocks, habit check-ins |

---

### Recipe Discovery After Onboarding

In the Pulse home screen, a **Recipes** tab shows:
- Your active recipe (customisable)
- Suggested additions: *"Add the Engineering recipe to get GitHub PR alerts alongside your Sales briefs"*
- Community recipes (later): user-created, starred, cloned

Each recipe card shows:
- Name + icon
- "What you'll get" -- 3 bullets of concrete notifications
- Required integrations (with  for already connected ones)
- One-tap install -> connects missing integrations in sequence

---

### Recipe Customisation

After installing, every recipe is editable:

```
Sales Rep Recipe

Triggers:
   Pre-meeting brief (30 min before)
   Follow-up reminder (24h after meeting)
   Pipeline change alerts -- [Enable]

Notification style:
   Concise (1-2 lines)
   Detailed (bullet breakdown)

Quiet hours: 8pm - 8am
```

Users can toggle individual triggers without understanding the underlying logic. They're editing the outcome, not the rule.

---

### "On the Fly" Job Detection

When a user selects "Other" on the role screen, Pulse runs a short intent interview:

**Screen 1:**
> "Tell me what a typical day looks like for you." (free text, 2-3 sentences)

**Screen 2 (AI-generated):**
> Based on their input, Pulse proposes a recipe:
> *"Sounds like you're in client-facing consulting work. I've built you a starter setup focused on meeting prep and client email tracking. Does this sound right?"*
> [Yes, looks good] [Tweak it]

The AI maps free-text job description -> nearest recipe archetype, with modifications. If it can't confidently match, it defaults to the Executive recipe (broad coverage) and flags for the user to customize.

For ongoing detection: after 2 weeks, Pulse can suggest recipe adjustments based on observed patterns:
> *"You've been getting a lot of GitHub-related context in your meetings. Want me to add the Engineering recipe to your setup?"*

This is proactive UX: the app learns the user's job from behavior, not just from a form answer.

---

## The "Holy Shit" Moment: Detailed Sequence

**T+0:00 -- Install complete.** App opens to a full-screen welcome with a single sentence: *"Pulse watches your world so you don't have to."*

**T+0:30 -- Signup.** Name + email. Google SSO is primary CTA. Two fields max.

**T+1:00 -- Role selector.** 5-6 tiles. One tap. No next button -- tapping a tile auto-advances.

**T+1:15 -- Recipe preview.** *"Here's your [Sales Rep] setup. It needs Calendar + Gmail to get started."* One screen. Two bullet points about what Pulse will do.

**T+1:30 -- Calendar connection.** Single card with icon + plain English. [Connect Calendar] -> OAuth sheet (popup, not redirect). User logs in, approves.

**T+2:00 -- "Let me take a look at your week..." animation.** Animated scan with real copy: *"Found 4 meetings in the next 24 hours... Checking for context... Done."*

**T+2:30 -- Gmail connection prompt.** *"Nice. I can see you have a call with Sarah at 2pm. If you connect Gmail, I can brief you on her last email."* [Connect Gmail] [Skip for now]

**T+3:00 -- Connected.** Pulse has both.

**T+3:30 -- First notification fires.** If there's a meeting within 2 hours: immediate brief. If not: a "Here's tomorrow" digest with meeting prep for the next day, already surfacing email context.

**The notification reads like a person, not an alert.**

> *"You've got a call with Sarah Chen at 2pm (45 min, Google Meet). She's VP of Growth at Acme -- you last spoke 3 weeks ago about the enterprise tier. Her last email (Mon) mentioned she's pushing back on annual pricing. Worth addressing early."*

That's the moment. Everything else is follow-through.

---

## Key Anti-Patterns to Avoid

1. **Asking for integrations before showing why they matter.** Earn the ask.
2. **Showing a settings page full of 50 integration logos.** Overwhelm = paralysis.
3. **Silent post-connection.** If nothing fires in 10 minutes, send something. Anything. A morning brief. A "here's what I found" summary. Never silence.
4. **Requesting write permissions when you only need read.** Kills trust immediately.
5. **Full-page OAuth redirect.** Always use a sheet/popup. Keep context.
6. **Blocking on incomplete setup.** Partial connections must still deliver value.
7. **Generic notifications.** "You have 3 meetings tomorrow" is not Pulse. It's a calendar app. Every notification must demonstrate intelligence.
8. **Hiding the disconnect option.** Users need to feel in control. Bury revocation = users uninstall instead of disconnecting.

---

*Last updated: March 2026. Owned by Product Research.*
