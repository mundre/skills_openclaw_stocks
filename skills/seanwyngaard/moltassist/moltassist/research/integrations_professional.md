# Pulse -- Professional Integrations Research
**Principle:** Start with the customer moment. Work backwards to the tech.

> "People don't want quarter-inch drills. They want quarter-inch holes." -- Levitt (after Jobs)
> Pulse doesn't integrate with calendars. It makes sure you never walk into a meeting unprepared.

---

## 1. CALENDAR

### Google Calendar API

**The Moment:**
It's 9:47 AM. You're deep in code, or on another call, or just distracted. At 10:00 you have a meeting with a client you haven't spoken to in three months. You have no idea what you last discussed, what you promised, or who else is attending. You feel the low-grade dread of being caught flat-footed -- but only notice it at 9:59 when it's too late. Pulse catches this at 9:47 and closes the gap before you even feel it.

**Data Exposed:**
- Events (title, start/end time, attendees, location, description, conferencing links)
- Recurring events and exceptions
- Free/busy status
- Calendar list (personal, shared, resource calendars)
- Event changes and cancellations in real-time via push notifications (webhooks)

**MCP Server:**
- No official Google MCP server for Calendar specifically
- Community: `mcp-google-workspace` (j3k0/mcp-google-workspace) covers Gmail + Calendar via OAuth2
- Third-party hosted: workspacemcp.com offers a managed solution

**Triggers:**
- Meeting starting in N minutes (configurable: 10/15/30 min)
- Meeting with external attendees (higher-value prep trigger)
- Meeting has no agenda/description set
- Back-to-back meetings detected (no buffer)
- Attendee list changed within last hour
- Event location changed or conferencing link missing
- Day starts with 3+ meetings (high-load day warning)
- Meeting cancelled within 30 minutes of start

**Example Notification:**
```
 10-min warning: "Q1 Review -- Acme Corp" at 10:00

Attendees: Sarah Chen (CEO), Marcus Roy (CPO) -- 2 externals
Last meeting: Dec 12 (47 days ago)
No agenda set.

From your email thread: Sarah asked about the API pricing change. 
You said you'd "follow up in January." You didn't.

Want me to pull the full email thread before you join?
```

---

### Microsoft Graph -- Outlook Calendar

**The Moment:**
Same as above, but in enterprise environments where Outlook is law. The additional unlock here is visibility into *other people's* calendars -- colleagues, direct reports, shared meeting rooms. Pulse can see when your manager's calendar suddenly opens up and nudge you: "Your 1:1 with David got cancelled. He has 30 min free at 3 PM if you want to reschedule." That's the moment -- recapturing lost sync time before it becomes a missed week.

**Data Exposed:**
- Events, attendees, recurrence patterns
- Delegate calendar access (view others' schedules with permission)
- Room and resource bookings
- Online meeting links (Teams integration)
- Calendar sharing settings
- Category labels and importance flags

**MCP Server:**
- No dedicated official MCP; covered under Microsoft's broader Graph API
- Community: multiple Graph API wrappers exist but none with official MS backing as of Mar 2026

**Triggers:**
- Same as Google Calendar triggers
- Meeting room double-booked (Graph can detect conflicts)
- 1:1 with direct report hasn't happened in 14+ days
- All-hands or company-wide event detected (prep trigger)
- Meeting organizer changed (ownership transferred)

**Example Notification:**
```
 Your 1:1 with David got cancelled (he moved it to next week).

He has a 30-min open slot today at 3:00 PM. 
You haven't synced in 11 days. Two of your shared tasks are overdue.

Want me to request the 3 PM slot?
```

---

### Apple CalDAV

**The Moment:**
Same core meeting prep moment, but for users who live in Apple's ecosystem (iPhone, Mac, iCloud Calendar). The specific unlock is personal calendar events -- family commitments, personal appointments -- that corporate tools don't see. Pulse can bridge both worlds: "You have a dentist appointment at 2 PM and a client call just got booked for 2:30. That's going to be tight."

**Data Exposed:**
- iCloud Calendar events (via CalDAV protocol)
- Personal calendar feeds
- Shared family calendars
- Subscription calendars (public holiday feeds etc.)

**MCP Server:**
- No official MCP server
- CalDAV is a standard protocol; can be read by any CalDAV-compliant client
- Integration typically done via Apple's CalDAV endpoint with app-specific passwords

**Triggers:**
- Personal appointment within 2 hours of a work meeting
- Travel time not accounted for (location-based events)
- Birthday/anniversary reminders
- iCloud shared calendar event changes

**Example Notification:**
```
 Heads up: your dentist is at 2:00 PM (Claremont) and 
your Zoom with the dev team is at 2:30 PM.

Claremont to home is ~25 min. That's tight. 
Should I ask if the dev call can move to 3:30?
```

---

## 2. EMAIL

### Gmail API

**The Moment:**
You sent a proposal three days ago. Or asked a question that needed an answer before you could move forward. Or made a commitment in writing that you've now forgotten. Gmail's thread history is a goldmine of dropped balls -- promises made and not tracked, follow-ups that were mentally delegated to "I'll reply later" and then vanished. Pulse reads your sent mail and watches for the silence on the other end.

**Data Exposed:**
- Full thread history (read/unread status, sender, recipients, subject, body, attachments)
- Labels and categories (Priority Inbox, Promotions, etc.)
- Draft status
- Send/receive timestamps
- Thread participants
- Real-time push via Gmail watch API (webhooks)
- Thread modification events (label changes, starring)

**MCP Server:**
- No official Google MCP for Gmail specifically
- Community: `mcp-google-workspace` (j3k0) covers Gmail + Calendar
- workspacemcp.com (third-party managed, OAuth2)

**Triggers:**
- You sent an email 48+ hours ago with no reply
- Important contact replied for the first time in weeks
- Email from VIP sender (unread for 2+ hours)
- You said "I'll get back to you" and haven't
- Contract/proposal attached to outbound email, no acknowledgment
- Thread with 5+ back-and-forths with no resolution
- Your email contains a date commitment ("by Friday", "end of week") -- Pulse tracks it

**Example Notification:**
```
 No reply from Marcus at TechCorp -- it's been 4 days.

You sent the revised proposal on Monday with updated pricing.
He said he'd "loop in the CFO and get back to you by Thursday."

It's Friday. Want me to draft a gentle follow-up?
```

---

### Microsoft Graph -- Outlook Mail

**The Moment:**
Same follow-up gap as Gmail, but in enterprise contexts. The additional unlock: shared mailboxes and delegation. Support@ or sales@ inboxes that no one feels personally responsible for. Pulse notices the email that's been sitting in sales@ for 3 days because everyone assumed someone else would handle it.

**Data Exposed:**
- Message threads (all folders including shared mailboxes)
- Read receipts and delivery status
- Message categories and flags
- Focus Inbox / Other inbox sorting
- Attachment metadata
- Calendar meeting invites embedded in email
- Delta sync for changes (efficient polling)

**MCP Server:**
- No official Microsoft MCP for Outlook Mail
- Covered by Graph API; community wrappers exist

**Triggers:**
- Shared mailbox email unanswered for >24 hours
- High-importance email (flag set by sender)
- Customer email with negative sentiment (requires NLP layer)
- Your own Out-of-Office reply detected (remind you it's still on)
- Missed meeting request in email (not accepted in calendar)

**Example Notification:**
```
 sales@ has had an unanswered email from a new prospect for 61 hours.

Subject: "Interested in enterprise pricing"
Sender: procurement@bigcorp.com

No one has replied or claimed it. Want me to draft a response and assign it to you?
```

---

## 3. TEAM COMMUNICATION

### Slack API + MCP Server

**The Moment:**
Someone @-mentioned you in a channel four hours ago asking for a decision. You saw it, thought "I'll come back to this," closed the app, and it's now buried under 200 new messages. The decision is blocking three people. The team has moved on -- or worse, made a bad decision without you. Pulse catches the buried @mention and brings it back before the damage is done.

**Data Exposed:**
- Messages and threads (channels + DMs)
- @mentions and reactions
- Channel membership and activity
- File shares
- Workflow/bot messages
- User status (Active, Away, DND)
- Channel history and search
- Real-time events via WebSocket (RTM) or Events API

**MCP Server:**
- **Official Slack MCP Server** -- docs.slack.dev/ai/slack-mcp-server
  - Launched early 2025; also available via `@modelcontextprotocol/server-slack` on npm
  - Supports: search channels, send messages, read history, manage channels
  - Workspace admin controls MCP client access

**Triggers:**
- @mention with no response after X hours
- Direct message left on read for 2+ hours
- You're added to a channel you haven't visited
- Keyword in any channel (your name, your project, a client name)
- Thread you're in has gone active again after silence
- High-priority channel sees 10+ messages since your last read
- Someone uses  or  in a channel you're a member of

**Example Notification:**
```
 You were @mentioned in #product 4 hours ago -- still unread.

James: "@you -- are we shipping the new onboarding flow this sprint 
or pushing to next? Team is blocked on this."

3 people have replied asking for an update. James pinged again at 2 PM.

What's your call?
```

---

### Microsoft Teams -- Graph API

**The Moment:**
Same buried message moment as Slack, but in corporate environments. The additional unlock: Teams is also where meetings happen, files live, and wiki pages get updated. A Teams chat is often where key decisions get made -- and lost -- in sprawling group threads that no one can track.

**Data Exposed:**
- Chat messages (1:1, group, channels)
- @mentions and reactions
- Meeting chat transcripts
- Teams and channels list
- Files shared in Teams (via SharePoint/OneDrive)
- Meeting recordings (via Graph)
- User presence (Available, Busy, DND, Offline)
- Activity feed notifications

**MCP Server:**
- No official Microsoft Teams MCP server as of Mar 2026
- Microsoft Graph API covers Teams via REST
- Community: some Graph API MCP wrappers cover Teams endpoints

**Triggers:**
- @mention in any team channel (unread for 2+ hours)
- High-priority chat message marked urgent by sender
- Someone shares a file in a channel and asks for review
- Meeting transcript contains your name with an action item
- Team you own has had no activity in 7+ days

**Example Notification:**
```
 You were @mentioned in Teams (Engineering All-Hands) 3 hours ago.

Priya: "@you the deployment script is throwing 403s in prod. 
Can you check? We're blocked on the release."

You haven't opened Teams since 11 AM.
```

---

## 4. PROJECT MANAGEMENT

### Jira -- API + MCP

**The Moment:**
The sprint ends in two days. You have a ticket assigned to you that's still "In Progress" -- but you haven't touched it in a week because you got pulled into other things. Nobody flagged it. The PM doesn't know. The story that was supposed to ship this sprint quietly becomes tech debt. Pulse watches your velocity and catches the ticket that's about to miss without anyone realising it.

**Data Exposed:**
- Issues (title, description, status, priority, assignee, reporter, labels, components)
- Sprint data (active sprint, backlog, sprint end dates)
- Transitions (status changes over time)
- Comments and attachments
- Linked issues (blocks/blocked by, relates to)
- Epics and versions
- Worklogs (time logged)
- Webhooks for real-time events (issue created/updated/transitioned)

**MCP Server:**
- **Official Atlassian MCP Server** (Remote Beta) -- covers Jira + Confluence
  - Remote SSE transport with OAuth
  - Confirmed in Atlassian dev blog; available for Jira Cloud
  - Supports: search issues (JQL), create/update issues, read comments

**Triggers:**
- Your assigned ticket hasn't been updated in 3+ days (sprint is active)
- Sprint ends in <48 hours and ticket still not "Done"
- Ticket blocked by another issue that's now resolved
- PR linked to ticket merged -- ticket still not closed
- High-priority bug assigned to you with no activity for 24 hours
- You're added as reviewer on a ticket
- SLA breach imminent (Jira Service Management)

**Example Notification:**
```
 Sprint ends Friday. "PULSE-47: Fix webhook retry logic" is still In Progress.

Last update: 6 days ago (you moved it from To Do).
No comments. No PR linked.

Sprint velocity at risk. What's the status -- should I flag this in standup?
```

---

### Linear -- API + MCP

**The Moment:**
Your team moves fast on Linear. Issues get created, triaged, and closed at speed. The problem: in the noise, a P1 bug that got quietly assigned to you on Tuesday afternoon got missed because you were in meetings all day and your Linear notification badge hit 40+. It's now Thursday. The customer is waiting.

**Data Exposed:**
- Issues (title, description, status, priority, assignee, label, cycle)
- Cycles (Linear's sprint equivalent)
- Projects and milestones
- Teams and members
- Comments and mentions
- Workflow states and transitions
- Webhooks for real-time issue events
- Git integration (branch/PR linked to issues)

**MCP Server:**
- **Official Linear MCP Server** -- launched May 1, 2025
  - Hosted at `mcp.linear.app/sse`
  - OAuth2 auth; also supports API key in Bearer header
  - Supports: read/create/update issues, search, list cycles, manage projects
  - Native Claude integration available

**Triggers:**
- P0/P1 issue assigned to you with no activity within 2 hours
- Issue you own is blocking 2+ other issues
- Cycle ends in <24 hours with incomplete issues assigned to you
- Issue moved back to "Todo" from "In Review" (rejection)
- @mention in issue comment (no response in 1 hour for P1+)
- PR merged but linked issue still not marked Done

**Example Notification:**
```
 P1 assigned to you 18 hours ago -- no activity.

"Auth tokens not invalidating on logout" (LIN-891)
Reported by: customer@bigcorp.com
Blocking: LIN-892, LIN-895

You were in meetings yesterday. This one slipped. 
Want me to add a comment updating the team on status?
```

---

### Asana -- API

**The Moment:**
You're the DRI on a project. Five tasks are assigned to other people, all due this week. You have no idea which ones are actually on track. Everyone says "on it" in standups. Three of the five haven't been touched in four days. Pulse watches task activity so you don't have to chase people -- it tells you *exactly* what's at risk before the deadline lands.

**Data Exposed:**
- Tasks (title, description, assignee, due date, completion status, custom fields)
- Projects and sections
- Subtasks
- Task stories (comments, status updates, activity log)
- Portfolios and goals
- Milestones
- Webhooks for real-time task events

**MCP Server:**
- No official Asana MCP server as of Mar 2026
- Community: Composio offers an Asana integration via their MCP layer
- Asana has a robust REST API that covers all key objects

**Triggers:**
- Task due today with no recent activity
- Subtask of a milestone overdue
- Task assigned to someone but not accepted/started (stuck in limbo)
- Task due date changed (someone quietly moved it)
- Project milestone missed
- Task assigned to a user who is OOO (calendar cross-reference)

**Example Notification:**
```
 3 of 5 tasks due this week haven't been touched in 4+ days.

- "Design final mockups" -- Alex (due Thu, last update: Mon)
- "Legal review of ToS" -- Priya (due Wed, no activity since assigned)
- "Set up staging environment" -- You (due Fri, not started)

The legal one is gating everything. Want me to ping Priya?
```

---

### Notion -- API + MCP

**The Moment:**
You wrote the spec. You put it in Notion two weeks ago. The engineer started building from a different version of the doc -- the one they had open in a tab before you made the update. The build is wrong. Pulse watches Notion documents that matter and tells stakeholders when critical pages change.

**Data Exposed:**
- Pages (title, content blocks, last edited time, editor)
- Databases (properties, rows/entries, filters)
- Comments and inline mentions
- Database views and filters
- Page hierarchy (parent/child)
- Block-level content (text, tables, code, callouts, etc.)

**MCP Server:**
- **Official Notion MCP Server** -- `makenotion/notion-mcp-server` on GitHub
  - Maintained by Notion team
  - v2.0.0 uses Notion API 2025-09-03
  - Supports: search pages, read page content, query databases, create/update pages

**Triggers:**
- A spec/PRD page you own was edited by someone else
- Database row status changed to "Blocked" or "At Risk"
- Page linked in active Jira/Linear ticket was last updated >14 days ago (potentially stale)
- New comment on a page you haven't read
- Team meeting notes page created (post-meeting action items)
- Task database has items past due date

**Example Notification:**
```
 The Product Spec for Pulse v2 was edited 2 hours ago.

Editor: Marcus (Engineering)
Section changed: "API Rate Limits" -- values were modified.

This doc is linked to 4 active Jira tickets. 
Engineers might be building from the new version. 
Was this intentional? [View diff]
```

---

### ClickUp -- API

**The Moment:**
ClickUp is where nothing gets finished but everything gets created. Tasks pile up. Due dates drift. The moment Pulse unlocks: the weekly "what did we actually ship?" review that reveals six things were supposed to be done and three quietly rolled to next week. Pulse makes the invisible visible -- before the weekly review, not during it.

**Data Exposed:**
- Tasks (name, status, priority, assignee, due date, time estimates, custom fields)
- Spaces, folders, lists
- Subtasks and checklists
- Time tracking entries
- Goals and targets
- Comments and attachments
- Webhooks for task events

**MCP Server:**
- No official ClickUp MCP server as of Mar 2026
- Community: Composio MCP covers ClickUp

**Triggers:**
- Tasks overdue for 3+ days
- High-priority task with no time tracked
- Task in "Review" status for >48 hours (reviewer not acting)
- Sprint/list goal percentage falling behind trajectory
- Task assigned to you added while you were offline

**Example Notification:**
```
 End of week: 6 tasks were due this week.

 Shipped: 3
 Overdue (quietly rolled): 2  
 Still in review: 1

The two that rolled: both assigned to you. Want a summary 
to share in #weekly-sync before the call?
```

---

### Trello -- API

**The Moment:**
A card moved to "Done" on the board but the actual work isn't done -- the designer just moved it to clear their column. Or a card has been sitting in "In Progress" for three weeks because everyone forgot it existed. Trello boards are graveyards of good intentions. Pulse watches for cards that have stopped moving.

**Data Exposed:**
- Cards (name, description, members, labels, due dates, checklists)
- Lists and boards
- Card movements (list changes)
- Comments and attachments
- Due date completion status
- Activity log

**MCP Server:**
- No official Trello MCP server
- Community wrappers exist; Trello REST API is well-documented

**Triggers:**
- Card overdue with incomplete checklists
- Card has been in the same list for 10+ days
- Your card has a comment with a question unanswered for 48+ hours
- Card due date changed (someone extended without note)

**Example Notification:**
```
 "Redesign onboarding email sequence" has been in "In Progress" for 19 days.

Assigned to: you + Lisa
Last activity: Lisa added a comment 12 days ago asking a question.
No reply.

Is this still active or should it move to Backlog?
```

---

## 5. CRM / SALES

### Salesforce -- API + MCP

**The Moment:**
You have a deal in the pipeline. The prospect went quiet 10 days ago after you sent the contract. Your manager is asking for a forecast update. You say "it's warm" but you have no idea. Pulse reads the actual Salesforce activity log -- no emails opened, no calls logged, deal stage hasn't changed in two weeks -- and tells you the truth before your forecast call.

**Data Exposed:**
- Accounts, Contacts, Leads, Opportunities
- Activities (calls, emails, meetings logged)
- Opportunity stage and close date
- Notes and attachments
- Tasks and events (Salesforce activities)
- Cases (if Service Cloud)
- Custom objects and fields
- Reports and dashboards
- Real-time via Salesforce Streaming API (PushTopic/Platform Events)

**MCP Server:**
- **Official Salesforce MCP Server** -- in Beta (announced Oct 2025)
  - Hosted MCP server from Salesforce directly
  - Also: Salesforce DX MCP (salesforcecli/mcp on GitHub) -- Dev Preview since May 2025, for developer/admin use
  - Supports: query data (SOQL), read/write records, run Apex tests (DX version)

**Triggers:**
- Opportunity close date within 7 days, no activity in 5+ days
- Deal stage stagnant for 14+ days
- High-value prospect email received (contact matches an Opportunity)
- No activity logged after a meeting with a prospect
- Lead assigned to you not contacted within 24 hours (SLA)
- Deal moved back a stage by manager

**Example Notification:**
```
 "Acme Corp -- Enterprise" closes in 6 days. Last activity: 11 days ago.

Stage: Proposal Sent
Value: $84,000 ARR
Last logged activity: you sent the contract (Feb 10)
No email opens tracked. No calls logged.

This is at risk. Want me to draft a re-engagement email 
or flag it for your forecast call?
```

---

### HubSpot -- API + MCP

**The Moment:**
A lead just visited your pricing page for the third time in two days. They're clearly evaluating. They filled out a form six weeks ago and got put into a nurture sequence. No one has talked to them live. Pulse sees the signal before your sales rep does -- and fires at the exact moment the prospect is warm, not after they've gone cold again.

**Data Exposed:**
- Contacts, Companies, Deals, Tickets
- Contact timeline (page visits, email opens, form fills, calls)
- Deal pipeline and stages
- Email engagement (open, click, reply tracking)
- Meeting booked/completed
- Workflow enrollment status
- Lists and segmentation
- Webhooks for contact/deal property changes

**MCP Server:**
- **Official HubSpot MCP Server** -- developers.hubspot.com/mcp
  - Launched 2025; OAuth 2.0 auth
  - Supports: read/write contacts, companies, deals; search CRM; create/update deal stages

**Triggers:**
- Contact visits pricing page 3+ times in 48 hours
- High-fit lead (ICP match) submits form and isn't contacted within 1 hour
- Deal idle for 14 days in "Decision Maker Engaged" stage
- Email sequence completed with no response (lead needs human touch)
- Contact replies after being marked "churned"

**Example Notification:**
```
 Hot lead: Jordan Wells (CTO, DataMesh) visited /pricing 3x today.

First visit: 9:14 AM | Last visit: 3:47 PM
Form fill: Jan 28 (6 weeks ago) -- went into nurture sequence
No live contact made.

This is the window. Want me to pull their company profile 
and draft a direct outreach?
```

---

### Pipedrive -- API

**The Moment:**
Your Pipedrive is full of deals that were "almost closed" three months ago. Everyone's too optimistic with their pipeline. The moment Pulse unlocks: honest pipeline hygiene. A deal that hasn't moved in 30 days is not a deal -- it's hope. Pulse surfaces the truth and prompts you to either advance or kill it.

**Data Exposed:**
- Deals (title, stage, value, close date, owner, probability)
- Contacts and Organizations
- Activities (calls, emails, meetings, tasks)
- Notes
- Email integration (if Pipedrive email sync enabled)
- Stage change history
- Lost reasons

**MCP Server:**
- No official Pipedrive MCP server as of Mar 2026
- Community: Merge.dev offers a Pipedrive MCP layer
- Pipedrive REST API is well-documented

**Triggers:**
- Deal with no activity in 21+ days
- Deal close date passed without closing
- Activity (call, meeting) overdue for 3+ days
- New deal created with no activity scheduled
- Deal probability hasn't changed in 30 days despite stage movement

**Example Notification:**
```
 Pipeline cleanup: 4 deals haven't moved in 30+ days.

Total stale value: $210,000
Oldest: "RetailCo -- Pro Plan" -- 47 days, no activity, close date was Jan 15.

Real pipeline or wishful thinking? 
Let me help you mark won/lost and clean this up.
```

---

## 6. CUSTOMER SUPPORT

### Zendesk -- API + MCP

**The Moment:**
A ticket from your biggest customer has been sitting in the queue for 6 hours. Your SLA is 4 hours. No one grabbed it because it got routed to a group with five agents, and everyone assumed someone else would take it. The customer is about to send a follow-up email -- the kind that starts with "We're reconsidering our contract." Pulse fires the moment the SLA is breached, not after.

**Data Exposed:**
- Tickets (subject, description, status, priority, requester, assignee, group, tags)
- SLA policies and breach times
- CSAT scores and ratings
- Comments and internal notes
- Organizations and users
- Ticket satisfaction ratings
- Views and queues
- Webhooks for ticket events (create, update, status change)

**MCP Server:**
- No official Zendesk MCP server (confirmed as of Mar 2026 per plain.com research)
- Community: `koundinya-zendesk` on PulseMCP (community-built)
- Zendesk has a REST API; integrations commonly built via Zendesk Apps Framework or webhooks

**Triggers:**
- SLA first reply time breached (or <15 min to breach)
- SLA resolution time approaching breach
- VIP/enterprise customer ticket unassigned for >1 hour
- High-priority ticket re-opened after "Solved"
- CSAT score of 1 received
- 5+ tickets from same customer in 7 days (churn signal)
- Ticket pending for 3+ days (customer waiting on you)

**Example Notification:**
```
 SLA breached: Ticket #84521 -- "API returning 500 errors in production"

Customer: Acme Corp (Enterprise tier, $120k ARR)
Opened: 4 hours 22 minutes ago
SLA target: 4 hours
Currently: Unassigned (Group: Tier 1)

This is your highest-value customer. Who should I escalate to?
```

---

### Intercom -- API + MCP

**The Moment:**
A user sent a message in the product chat at 11 PM asking a billing question. It sat in the inbox overnight. By the morning, they'd already emailed support@, tweeted about it, and started a trial of a competitor. The moment: catching the in-app message before it becomes a churn event -- especially for high-value or at-risk users where speed of response is a retention signal.

**Data Exposed:**
- Conversations (messages, status, assignee, tags, priority)
- Contacts (user attributes: plan, MRR, usage, last seen)
- Companies and their health scores
- Conversation events (opened, replied, snoozed, resolved)
- Product tours and checklist completion
- Custom attributes (e.g., days_since_last_login, plan_tier)
- Webhooks for conversation events

**MCP Server:**
- **Official Intercom MCP Server** -- developers.intercom.com/docs/guides/mcp
  - Released May 2025 (US-hosted workspaces only as of late 2025)
  - Supports: read conversations, search contacts, retrieve company data

**Triggers:**
- High-MRR user sends a message in-app (unread >30 min)
- User sends message outside business hours (triage/auto-flag)
- Conversation re-opened after resolution
- User attribute trigger: days_since_last_login > 14 AND on paid plan
- User in trial sends message within 48 hours of trial expiry
- Negative sentiment detected in message (NLP)

**Example Notification:**
```
 High-value user messaged in-app 4 hours ago -- no reply.

User: jordan.wells@datacorp.com
Plan: Business ($899/mo) | Last login: 3 days ago
Message: "Hi -- we're getting charged for seats we removed 
last month. This is the 3rd time I've raised this."

3rd time. This is a churn risk. Want me to pull their billing history 
and draft an apology + resolution?
```

---

### Freshdesk -- API

**The Moment:**
Your support team is stretched. A ticket from a casual free user is getting prioritized over a ticket from your biggest enterprise customer -- because the free user submitted theirs first and the queue is FIFO. Pulse cross-references Freshdesk ticket data with your CRM to surface the enterprise ticket and flag the priority inversion before a $200k account churns over a $5 problem.

**Data Exposed:**
- Tickets (subject, description, status, priority, type, tags, due date, requester)
- Agents and groups
- SLA policies and violation data
- CSAT scores
- Contact and company info
- Ticket watchers and CC'd users
- Webhooks for ticket lifecycle events
- Time logs and satisfaction surveys

**MCP Server:**
- No official Freshdesk MCP server as of Mar 2026
- Community: Composio offers Freshdesk via their MCP layer
- Freshdesk REST API v2 is comprehensive

**Triggers:**
- Ticket due date within 1 hour and status still "Open"
- SLA violation logged
- Enterprise customer ticket stuck in queue (priority below actual account value)
- Ticket transferred/reassigned 3+ times (thrashing -- no clear owner)
- Ticket reopen rate spike (same customer, 3 reopens in a week)
- Agent resolution time >2x their average (struggling)

**Example Notification:**
```
 Priority mismatch detected in Freshdesk queue.

Ticket #10284: "Cannot export reports" -- Priority: Low
Requester: mike@megacorp.com (Enterprise, $180k ARR)
In queue: 5 hours | SLA: 2 hours -> BREACHED

3 free-tier tickets are ahead of it in the queue.

Recommend: escalate to Priority: Urgent and assign to Sarah (enterprise queue).
Do it now?
```

---

## MCP Server Status Summary

| Integration | Official MCP | Status |
|---|---|---|
| Google Calendar |  | Community only (mcp-google-workspace) |
| Gmail |  | Community only (mcp-google-workspace) |
| Outlook Calendar |  | Graph API; no dedicated MCP |
| Outlook Mail |  | Graph API; no dedicated MCP |
| Slack |  | Official -- docs.slack.dev/ai/slack-mcp-server |
| Microsoft Teams |  | Graph API; no dedicated MCP |
| Jira |  | Official (Atlassian) -- Remote Beta with OAuth |
| Linear |  | Official -- mcp.linear.app/sse (May 2025) |
| Asana |  | Community (Composio MCP layer) |
| Notion |  | Official -- makenotion/notion-mcp-server |
| ClickUp |  | Community (Composio MCP layer) |
| Trello |  | Community wrappers only |
| Salesforce |  | Official Beta (Oct 2025) + DX MCP (May 2025) |
| HubSpot |  | Official -- developers.hubspot.com/mcp |
| Pipedrive |  | Community (Merge.dev MCP layer) |
| Zendesk |  | Community only (no official MCP confirmed) |
| Intercom |  | Official -- developers.intercom.com/docs/guides/mcp |
| Freshdesk |  | Community (Composio MCP layer) |

---

## Recommended Integration Priority for Pulse MVP

**Tier 1 -- Highest moment density, best API/MCP maturity:**
1. Google Calendar / Gmail (same OAuth, covers the biggest daily moments)
2. Slack (official MCP, ubiquitous, high message volume = many triggers)
3. Linear (official MCP, high-growth engineering teams = target users)
4. HubSpot (official MCP, sales follow-up is a killer use case)

**Tier 2 -- High value, slightly more complex:**
5. Jira (official MCP, enterprise engineering teams)
6. Notion (official MCP, spec drift is a real pain point)
7. Salesforce (official MCP in beta, large deal sizes justify complexity)
8. Intercom (official MCP, churn prevention = high ROI moment)

**Tier 3 -- Strong use cases, API-only integration needed:**
9. Zendesk (SLA breach is high urgency, API is solid)
10. Asana (project oversight moments are real, no MCP but good API)
11. Microsoft Graph (Outlook + Teams -- enterprise moat)

---

*Research compiled: March 2026 | Sources: official API docs, MCP registries (pulsemcp.com, mcpservers.org), vendor announcements*
