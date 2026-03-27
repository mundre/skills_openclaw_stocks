# Pulse -- Competitive Landscape & Product Positioning
**Research Date:** March 2026  
**Status:** Foundation research -- sharp, honest, no padding

---

## Executive Summary

Every AI assistant on the market today is **reactive**. You open it. You type. It responds. Close it. Done.

Nobody has built an assistant that watches your world and **comes to you** with the right information at the right moment -- without being asked. That gap is real, it's structural, and it's the entire bet Pulse is making.

---

## 1. What Exists Today

### Siri (Apple)
**What it does:** Voice-first assistant baked into Apple devices. Handles timers, calls, messages, reminders, basic web queries, device control. Deep OS integration across iPhone, Mac, Watch, iPad.

**Proactive capability:** Siri Suggestions surface in Spotlight and the lock screen -- "you usually call X at this time" or "leave for your meeting now." Notification summaries in iOS 18. That's basically it.

**What's missing:** Siri suggestions are shallow pattern-matching with no real reasoning. It has access to your entire device but does almost nothing interesting with it. The gap between what Siri *could* know and what it acts on is embarrassing. No outbound "hey, you need to know this" capability. Siri waits.

**Threat to Pulse:** Low. Siri's proactive features are cosmetic window dressing. Apple's privacy stance (on-device processing) actually limits what they can cross-reference.

---

### Google Assistant / Google Gemini
**What it does:** Voice + text assistant across Android and Google Workspace. Searches, summarises, answers questions, drafts emails in Gmail, summarises Docs. Gemini is the rebrand -- much more capable LLM underneath.

**Proactive capability:** Google Now (RIP) was actually the closest thing to proactive AI -- it surfaced cards about your flight, sports scores, packages, before you asked. Gemini has mostly regressed this into a chat model. Some proactive digest features in Gmail. Daily briefings in Assistant. Largely still reactive.

**What's missing:** Google has the data to be *dramatically* more proactive than anyone else (Search, Gmail, Calendar, Location, YouTube, Maps) but doesn't use it aggressively due to privacy optics and regulatory scrutiny. The capability exists; the product courage doesn't.

**Threat to Pulse:** Medium-long term. If Google woke up and decided to be truly proactive, they'd be formidable. They haven't, and the regulatory environment makes it harder.

---

### Microsoft Copilot (M365)
**What it does:** AI embedded across Word, Excel, PowerPoint, Teams, Outlook, Edge. Summarises meetings, drafts docs, surfaces relevant files, answers questions about your org's data via Graph API.

**Proactive capability:** Late 2025 updates showed Copilot moving toward proactive "work partner" framing -- surfacing files you forgot about, suggesting agents in chat. Mobile app gained Reminders (Feb 2026). But it's still fundamentally: you open Teams, Copilot offers suggestions inside the app.

**What's missing:** It lives inside Microsoft's ecosystem. It doesn't come to you; it waits for you to open an M365 app. If you're not in an Outlook tab, Copilot is silent. No cross-app, cross-context proactive reach-out to the human.

**Threat to Pulse:** Medium for enterprise (Copilot will eventually push harder into M365 orgs). Low for SMBs and individuals who aren't deep Microsoft shops.

---

### Amazon Alexa
**What it does:** Voice assistant for smart home control, shopping, timers, music, basic Q&A. Increasingly LLM-powered ("Alexa+"). Deeply embedded in Echo hardware.

**Proactive capability:** Alexa can announce things (reminders, delivery notifications, ring doorbell alerts). Alexa Routines can trigger "good morning" briefings. New Alexa+ claims more proactive, conversational capability (2025).

**What's missing:** Alexa is voice-first and room-bound. You have to be near a device. No mobile-first proactive outreach. The smart home use case is genuinely useful; the productivity/knowledge use case is weak. Nobody trusts Alexa with important information.

**Threat to Pulse:** Very low. Different market segment.

---

### Cortana (Microsoft)
**What it does:** Largely deprecated as a standalone product. Folded into Copilot. Dead end.

**Proactive capability:** Used to have some calendar and email integration. Gone.

**Threat to Pulse:** None.

---

### ChatGPT (OpenAI)
**What it does:** The dominant conversational AI. Best-in-class reasoning, coding, writing, analysis. Custom GPTs. Memory features. Operator capabilities. Voice mode. Now with advanced reasoning (o3, o4).

**Proactive capability:** Zero. ChatGPT is entirely reactive. You open it, you type, it answers. Memory lets it recall past conversations, but it has no mechanism to reach out, no background monitoring, no triggers. It is a brilliant on-demand tool, not a proactive assistant.

**What's missing:** Proactivity is architecturally absent. OpenAI has hinted at "agent" features but these are still user-initiated flows. ChatGPT does not watch your world and interrupt you.

**Threat to Pulse:** Moderate. OpenAI could build this. They have the distribution. But ChatGPT's product identity is the chat interface -- pivoting to proactive push is a different product paradigm, and they'd risk alienating their core use case.

---

### Claude (Anthropic)
**What it does:** Conversational AI, strong at reasoning, safety, long context, nuanced writing. Claude.ai web/mobile. API available for developers.

**Proactive capability:** None as a consumer product. Entirely reactive. Anthropic's focus is alignment and safety -- always-on proactive monitoring is philosophically uncomfortable territory for them.

**What's missing:** Same as ChatGPT. No background monitoring, no push capability, no triggers.

**Threat to Pulse:** Low directly. High as infrastructure -- Pulse could run on Claude under the hood, and so could competitors.

---

### Perplexity
**What it does:** AI-native search engine. Real-time web + AI synthesis. Ask a question, get a sourced answer. Daily Discover feed (curated news). Pro Search for deeper research.

**Proactive capability:** The Discover feed is arguably the most proactive thing on this list -- it pushes curated content to you. Perplexity Spaces let you monitor topics. But it's still a pull model: you open the app and consume what it surfaces.

**What's missing:** No personalised proactive alerts based on *your* context (your calendar, your projects, your conversations). "Here's today's news" is not the same as "you have a meeting about X in 2 hours -- here's a briefing specific to that meeting."

**Threat to Pulse:** Low-medium. Perplexity is moving toward more proactive content delivery, but its DNA is search. Contextual, personalised proactivity isn't their roadmap.

---

### Notion AI
**What it does:** AI embedded inside Notion workspaces. Summarise notes, draft content, answer questions about your docs, autofill databases, generate action items from meeting notes.

**Proactive capability:** None. Notion AI is passive -- it helps when you're already in Notion. It doesn't monitor your workspace and surface things unprompted. No push, no alerts, no reach-out.

**What's missing:** Notion has all your project data but does zero proactive synthesis. It could notice "this project's deadline is tomorrow and three action items are unchecked" and tell you -- it doesn't.

**Threat to Pulse:** Low. Notion's DNA is document creation, not proactive monitoring.

---

### Motion (Calendar AI)
**What it does:** AI-first task and calendar manager. Auto-schedules tasks around meetings, reshuffles your day when things change, adapts in real-time to the chaos of work.

**Proactive capability:** Closest to proactive of any tool here. Motion does reschedule things for you without being asked. It does notify you when your day is overloaded. This is genuine automated agency.

**What's missing:** Motion's proactivity is confined to scheduling. It doesn't know about your emails, your project updates, external news, or anything beyond calendar + task list. It also doesn't initiate conversations -- it silently reshuffles, which is different from "here's something you need to know."

**Threat to Pulse:** Low-medium. Motion owns a specific narrow lane. The scheduling automation is a feature Pulse might want to incorporate or integrate, not compete with directly.

---

### Reclaim.ai
**What it does:** AI calendar optimizer. Protects focus time, auto-schedules habits and tasks, coordinates team scheduling, smart meeting links.

**Proactive capability:** Similar to Motion -- it acts autonomously on your calendar without being asked. Reclaim will move a habit block if a meeting lands on it. But it's silent automation, not a conversation or alert.

**What's missing:** Same structural gap as Motion. Scheduling intelligence only. No cross-domain proactivity.

**Threat to Pulse:** Low.

---

### Superhuman
**What it does:** Premium email client ($30/month). Blazing-fast keyboard shortcuts, AI drafts in your voice, smart triage, read receipts, follow-up reminders, "Superhuman Go" -- a proactive AI assistant that offers help without being asked (their words).

**Proactive capability:** "Superhuman Go" is the most interesting move here -- explicitly branded as proactive, offering suggestions inside email without you asking. But it's still *inside the email app*. It knows what's in your inbox. It doesn't know about your calendar context, your Slack, your projects.

**What's missing:** Email-silo proactivity. "Go" is impressive within Superhuman but it doesn't integrate across your full work context. Also: $30/month for email is a hard sell to non-power-users.

**Threat to Pulse:** Medium for email-heavy users. Superhuman is explicitly moving toward the "proactive assistant" positioning, which means they're heading into the same territory. Their moat is inbox + high-end UX; Pulse's moat would be multi-source cross-context proactivity.

---

### Clara (claralabs.com)
**What it does:** AI scheduling assistant that operates over email. CC clara@claralabs.com on an email, it takes over the back-and-forth to schedule meetings. 10+ years, 1M+ meetings scheduled.

**Proactive capability:** Narrow but real. Clara does initiate outbound emails (to the other party) on your behalf. However, it only triggers when you CC it -- it doesn't monitor your world and decide to act.

**What's missing:** One-trick pony. Scheduling only, email only, and it requires human initiation to get started. It's an automation, not an intelligent proactive agent.

**Threat to Pulse:** Negligible.

---

## 2. The Core Gap -- Why Nobody Does This Well

This is the real question. Why, in 2026, with GPT-4o, Claude 3.5, Gemini 2.0, and billions in AI investment, does no tool actually *come to you* with relevant information without being asked?

### Technical reasons

**a) The polling problem.** To be genuinely proactive, a system needs to continuously monitor multiple data sources (email, calendar, Slack, news, your browser, your files) and run inference on that data constantly. That's expensive. Running an LLM continuously in the background on every user's data stream is 10-100x more expensive than serving a response when someone asks. The economics haven't worked -- until now, with faster, cheaper models.

**b) Trigger logic is hard.** Knowing *when* to interrupt someone is an unsolved problem. What's the threshold? One company has built reminders (easy). Scheduling reshuffling (Motion -- moderate). But "this email + this calendar event + this industry news = you should know X right now" requires multi-source reasoning across ambiguous signals. Nobody has built this trigger layer well.

**c) Integration depth is painful.** Being genuinely proactive requires reading across Gmail, Google Calendar, Slack, Notion, Jira, HubSpot, news feeds, etc. Every integration is OAuth, permissions, rate limits, schema differences, edge cases. This is boring, expensive engineering that doesn't demo well.

**d) Context window  proactivity.** Long context windows let you dump your whole life into a chat and ask questions. That's still reactive. True proactivity requires background processes, event-driven triggers, and a model that decides *when* something is worth surfacing -- not just *how* to answer when asked.

### Product/business reasons

**e) Privacy optics.** "Always-on AI watching everything" is a terrible headline. Every big tech company (Google, Apple, Microsoft) has learned to be conservative here. They have the data and capability but won't use it aggressively because the backlash risk is real. This is actually an opportunity for an indie product: a smaller company can make a transparency-first privacy pitch that big tech can't credibly make.

**f) Notification trauma.** Every app wants your attention. Users have been burned badly by apps that spammed them into turning off all notifications. Any new entrant into the "we'll reach out to you" space starts with a massive deficit of user trust. The solution isn't to not do it -- it's to be so precise and valuable the first 10 times that users never turn it off.

**g) The product identity problem.** ChatGPT is a chat interface. Notion is a document tool. Superhuman is email. Adding proactive push to these products creates product identity confusion. It's easier for them to stay in their lane. Pulse has no lane conflict -- its entire identity is proactivity.

**h) Nobody has built the "recipe" abstraction.** Proactive AI needs a programmable ruleset: "watch for X, synthesise with Y, deliver Z at the right moment." Nobody has packaged this as a user-friendly product layer. It's been left to Zapier power-users and developers building custom automations. That's the gap Pulse fills with its recipe concept.

---

## 3. Pulse's Unique Angle

**Every other tool waits. Pulse doesn't.**

Every AI assistant on the market -- from Siri to ChatGPT to Motion -- is fundamentally a **pull model**. You pull information from them. You open the app. You ask the question. You wait for a response. The value only exists in the moment you remember to invoke it.

Pulse is a **push model**. It monitors your context (calendar, email, news, integrations), applies your defined "recipes" (watch-for-X + synthesise-with-Y + deliver-Z), and reaches out to you with the right information at the right moment, before you knew to ask.

**One-sentence pitch:**  
*Pulse is the AI assistant that comes to you -- monitoring your world, applying your recipes, and delivering sharp, relevant briefings exactly when they matter, without you having to ask.*

**Why this is fundamentally different:**
- Every chatbot requires you to remember it exists. Pulse doesn't.
- Every AI tool is passive. Pulse is active.
- Every notification system is dumb (app-level pings). Pulse is intelligent (multi-source contextual synthesis).
- Recipes make proactivity programmable and shareable -- it's not just an alert, it's a defined workflow with AI reasoning at its core.

---

## 4. Revenue Models

### Tier 1 -- Personal ($12-15/month)
- Core recipe engine: up to 10 active recipes
- 5 integrations (Gmail, Google Calendar, Slack, Notion, news feeds)
- Delivery via email, SMS, or preferred messaging app
- Community recipe library access (read-only)
- Target: high-agency individuals, freelancers, solopreneurs

### Tier 2 -- Professional ($29-39/month)
- Unlimited recipes
- 20+ integrations (CRM, GitHub, Jira, Linear, HubSpot, etc.)
- Custom delivery schedules and channels
- Recipe creation tools (visual + natural language)
- Priority support
- Target: knowledge workers, PMs, founders, sales leaders

### Tier 3 -- Team ($79-99/month per team of 5, or per-seat pricing)
- Shared team recipes (role-based recipe packs auto-applied to new joiners)
- Team-wide context (shared Slack channels, project boards, shared calendars)
- Admin dashboard: recipe analytics, delivery logs, team performance insights
- Target: ops teams, RevOps, small startup teams

### Tier 4 -- Enterprise (custom pricing, $500-5k/month)
- SSO, SOC2, data residency
- Custom integrations via API
- White-label deployment (resellers, embedded in SaaS products)
- Dedicated onboarding + recipe building service
- SLA + support

### Recipe Marketplace (platform revenue)
- Open marketplace where users sell/buy recipe packs
- Role-specific packs: "VC Deal Flow Monitor," "Sales Pipeline Pulse," "Founder Daily Brief," "Customer Success Watchlist"
- Revenue split: 70% creator / 30% Pulse
- Creators can build a business on top of Pulse -- aligned incentive to grow the ecosystem
- Annual subscription bundles for top-rated packs

### White-Label (B2B2C)
- SaaS companies embed Pulse as their "proactive AI layer"
- Example: HubSpot embeds Pulse to surface "this deal hasn't been touched in 7 days" alerts for sales reps
- Sold as an add-on to existing SaaS products
- Revenue: per-seat or flat platform fee

---

## 5. Target User Personas

### Persona 1: The Overloaded Founder (highest pain, earliest adopter)
- **Profile:** 1-10 person startup, wearing 5 hats simultaneously
- **Pain:** Information scattered across Gmail, Slack, Notion, Linear, Twitter. Missing critical signals daily. No EA. No time.
- **What Pulse does:** "Your investor meeting is tomorrow. Here's a 3-line brief on their portfolio moves this week. You haven't responded to their last email 3 days ago."
- **Willingness to pay:** High ($30-50/month, no hesitation if it saves 30 min/day)
- **How to reach:** Twitter/X, HackerNews, indie hacker communities, founder Slack groups

### Persona 2: The Revenue/Sales Operator
- **Profile:** Head of Sales, RevOps, Account Executive at a B2B company
- **Pain:** Deal visibility requires opening Salesforce every morning. Deals go cold. Renewal risk goes unnoticed. Follow-up timing is always reactive.
- **What Pulse does:** "Deal X hasn't moved in 8 days. Last email read but no reply. Contact went to competitor's website yesterday."
- **Willingness to pay:** Very high. Directly tied to revenue. Expense it without blinking.
- **How to reach:** LinkedIn, G2 comparisons, Salesforce AppExchange adjacent marketing

### Persona 3: The Senior Knowledge Worker / Manager
- **Profile:** Director/VP at a mid-size company. 50+ emails/day, 6+ meetings, 3 Slack workspaces
- **Pain:** Drowning in information. Never feels on top of things. Constantly surprised.
- **What Pulse does:** Morning brief, pre-meeting prep, flagged urgencies, end-of-day digest
- **Willingness to pay:** Medium-high ($20-30/month personal, expense-able at professional tier)
- **How to reach:** LinkedIn thought leadership, productivity newsletters (Ness Labs, Morning Brew)

### Persona 4: The High-Agency Freelancer / Consultant
- **Profile:** Independent consultant, freelance designer/writer/developer. Multiple clients, no ops support
- **Pain:** Client context switches. Missing follow-ups. No system for watching multiple projects simultaneously.
- **What Pulse does:** Client-specific recipes. "Client A hasn't responded to proposal in 5 days. Client B's retainer renews in 3 days."
- **Willingness to pay:** Medium. Price-sensitive but pays for things that save time/money directly.
- **How to reach:** Twitter, freelancer communities, Toptal, Reddit

### Who to ignore at launch:
- Enterprise (too slow to close, too complex to onboard without white-glove)
- Non-technical consumers (too much education required, too low pain tolerance)
- People who "hate notifications" (no product solves this -- they're not the market)

---

## 6. Risks and Challenges

###  Risk 1: Privacy backlash ("you're spying on me")
**Threat level: High**

An always-on assistant that monitors your email, calendar, Slack, and browser is -- correctly -- a massive privacy concern. One bad headline ("Pulse employees read your emails") or one security breach kills the company overnight.

**What would kill Pulse:** Storing email content unencrypted. Selling data. Getting hacked. Building without privacy-first architecture.

**How to survive it:**
- Be transparent about exactly what is read, what is stored, what is processed
- End-to-end encryption where possible; zero-retention logs
- On-device processing for sensitive data (running local LLMs for email synthesis)
- SOC 2 Type II certification as early as feasible
- Privacy as a marketing differentiator, not an afterthought: "Pulse reads your context. Nobody else does."
- Don't store email content -- process and discard, surface only the synthesis

---

###  Risk 2: Notification fatigue -- becoming the annoying thing
**Threat level: Critical**

If Pulse sends 10 pings a day and 6 of them aren't useful, users mute it. If they mute it, the product is dead. The entire value proposition depends on the signal-to-noise ratio being exceptional.

**What would kill Pulse:** Default recipes that fire too often. Bad targeting logic. False positives on "urgent" flags.

**How to survive it:**
- Hard limit on daily proactive pushes during onboarding (max 3-5/day until trust is established)
- Every notification must be rateable:  -- use this as a training signal
- "Quiet hours" built in from day one, not added later
- Frequency learning: Pulse adapts to when you actually engage with alerts
- The recipe design philosophy: "Would a brilliant human assistant send this?" If no, don't send it.
- Default to under-delivering. It's easier to increase frequency once trusted than to recover from being muted.

---

###  Risk 3: Integration complexity -- the engineering moat becomes a swamp
**Threat level: High**

Every integration is a liability. OAuth breaks. APIs change rate limits. Slack revokes app permissions. Gmail updates terms. Every new integration = new maintenance burden, new failure surface.

**What would kill Pulse:** Building 50 integrations badly instead of 10 exceptionally. API deprecation at a critical integration point.

**How to survive it:**
- Launch with 5-8 rock-solid integrations, not 50 mediocre ones
- Priority stack: Gmail, Google Calendar, Slack, Notion, Linear/Jira, HubSpot
- Build on top of established integration platforms (Nango, Merge.dev, Airbyte) rather than raw OAuth implementations
- Webhook-first architecture: don't poll, listen
- Community-contributed integration layer (recipes that use Zapier/Make as the integration bridge)

---

###  Risk 4: Big tech wakes up
**Threat level: Medium (long-term)**

Google has your Gmail, Calendar, Search, Location, YouTube. If they decided to build Pulse, they could. Apple has your iPhone, Health, Messages, Calendar. Microsoft has your email + M365. Any of them could announce "Proactive Copilot / Proactive Gemini" and absorb this market.

**Why this hasn't happened and might not:**
- Regulatory pressure (EU AI Act, FTC scrutiny) makes "always-on monitoring" radioactive for Big Tech
- Product identity risk: Google's core product is you going *to* Google, not Google coming *to* you
- Privacy marketing war means none of them can credibly say "we're reading everything to help you"
- Big Tech moves slowly; by the time they ship something real, Pulse could be the default

**How to survive it:** Be three years ahead of them. Win the category before they decide to compete.

---

###  Risk 5: LLM costs
**Threat level: Medium**

If Pulse is running background monitoring + synthesis for 10,000 users, that's continuous LLM inference cost. At $29/month per user, margins get crushed if synthesis is expensive.

**How to survive it:**
- Use cheap/fast models for monitoring/triage (Gemini Flash, GPT-4o-mini, local models)
- Reserve expensive models for high-stakes synthesis (pre-meeting briefs, urgent flags)
- Cache aggressively: don't re-synthesise what hasn't changed
- Tiered model quality: Free = local model, Pro = frontier model

---

###  Risk 6: Trust takes time to build
**Threat level: Real but manageable**

Users won't hand over Gmail access on day one. The trust curve is slow. Early churn happens because the product hasn't learned the user's context yet (cold start problem -- Pulse is dumb before it knows you).

**How to survive it:**
- Onboarding that demonstrates value within 24 hours of setup
- "First week" recipe pack: curated recipes designed to impress immediately, before users have set up their own
- Show the receipts: "Here's what I monitored today. Here's what I decided wasn't worth sending."
- Build in explainability: every alert shows why it was sent ("Triggered because: email from X + calendar event tomorrow")

---

## 7. Moat -- What Makes Pulse Hard to Copy

### Moat 1: Recipe Library Network Effect (strongest)
A recipe marketplace with 10,000 role-specific recipes is a moat. The more people use Pulse, the more recipes get created, refined, and rated. A competitor starting from zero has no library. The library is the proprietary dataset. This is the Shopify App Store play -- the platform becomes more valuable than the product.

### Moat 2: Personalisation Depth
After 6 months of use, Pulse knows your communication style, your project context, your scheduling patterns, your notification preferences, what you engaged with vs. dismissed. This personalisation is non-transferable. A user switching to a competitor starts from cold. The switching cost grows every week.

### Moat 3: Delivery Intelligence
The hardest part isn't monitoring or synthesis -- it's knowing *when* to send. Pulse's "when to interrupt" model, trained on millions of engagements/dismissals across users, is a compound asset. This takes years to build. A new entrant has no training signal.

### Moat 4: Integration Depth + Reliability
Being the most reliable, deepest-integrated proactive layer takes years to build. Once a company trusts Pulse enough to give it access to Slack, Gmail, HubSpot, and Notion simultaneously, switching requires re-authorising everything with a new provider. Deep enterprise integrations create contractual stickiness.

### Moat 5: Recipe Creator Ecosystem
If creators can make $500-5000/month selling recipe packs on the Pulse marketplace, they're not building for any other platform. Creator lock-in drives product lock-in.

### What is NOT a moat:
- The LLM. Anyone can swap in the same model.
- The chat interface. There is no chat interface -- that's the point.
- The "proactivity idea." The idea can be copied; the execution, personalisation data, and recipe library cannot.

---

## 8. What Would Actually Make This Succeed

1. **The first 10 alerts are sacred.** If the first week of Pulse sends 10 things and 8 of them feel genuinely useful, users are hooked. If 5 are noise, they churn. The onboarding recipe pack is the most important product decision.

2. **Killer recipes, not killer features.** "You have a meeting with X in 90 minutes. They tweeted this yesterday. Their last email mentioned Y. Here's a 3-line brief." That single recipe, working reliably, is enough to sell the product. Don't build 100 features. Build 10 recipes that feel like magic.

3. **Transparency as the product, not the disclaimer.** Show users exactly what Pulse is watching. Make the "what I saw today" log visible. Trust is built by showing your work, not hiding it.

4. **Start with one profession, dominate it.** Don't be "AI assistant for everyone." Be "the AI assistant for founders" or "for sales reps." Nail one vertical with recipes so specific and good that it spreads by word of mouth. Expand from there.

5. **Quiet periods are a feature, not a limitation.** Pulse that knows when to shut up is more valuable than Pulse that's always talking. Market the silence as much as the signal.

---

## What Could Kill It

1. One privacy incident. One. That's all it takes.
2. Being annoying within the first 48 hours. Churn at this stage is terminal.
3. Building too many integrations too fast, causing instability.
4. OpenAI or Google shipping a better version 18 months in with built-in distribution.
5. Pricing too high before establishing value -- early adopters are price-sensitive until they see ROI.
6. Trying to be everything: don't build a chat interface, don't build a task manager, don't build a calendar. Be the layer that watches and tells. Let everything else be an integration.

---

*Research compiled for Pulse product strategy. Review and update quarterly.*
