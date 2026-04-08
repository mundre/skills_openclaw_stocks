---
name: outlook-email
description: >-
  Manage Outlook and Microsoft 365 email with AI agents — triage inbox by sender
  trust, draft replies with tone matching, organize folders, create inbox rules,
  and monitor for priority messages. Use when user says "check my email," "triage
  inbox," "organize email," "email cleanup," "outlook folders," "inbox rules,"
  "draft a reply," "email summary," "unread messages," "email heartbeat," or
  "monitor my mailbox." Works with any Graph API client; optionally enhanced by
  the open-source email-agent-mcp server.
license: Apache-2.0
compatibility: >-
  Works with any agent that can call the Microsoft Graph API.
  Optional MCP server (email-agent-mcp) requires Node.js >=20.
metadata:
  author: UseJunior
  version: "0.1.0"
---

# Outlook Email Management

> 使用 AI 代理管理 Outlook 邮件

Patterns for AI agents working with Microsoft 365 / Outlook email. These patterns work with any Graph API client. For a turnkey MCP server with safety guardrails, see [email-agent-mcp](https://github.com/UseJunior/email-agent-mcp) (open source, Apache-2.0).

## Safety Model
> 安全模型

**Draft-first is the recommended default for enterprise email.** Agents should never send email without explicit user approval.

The workflow:

1. **Compose** — create the email as a draft
2. **Present** — show recipients, subject, and body to the user
3. **Wait for approval** — only send when the user says "send," "send now," or equivalent
4. **Clean up** — after confirming a send, archive stale duplicate drafts

Why this matters: a single wrong send — wrong recipient, wrong attachment, confidential content to the wrong thread — can cause real damage. Drafts are free. Mistakes are expensive.

**email-agent-mcp** enforces this via empty send allowlists by default and a `create_draft` → `send_draft` two-step flow. **NemoClaw** can enforce it at the network policy level — see the [NemoClaw Email Policy skill](#related-skills).

## Email Triage
> 邮件分类

Not all email is equally important. Triage by sender trust, not by arrival order:

| Priority | Who | Action |
|----------|-----|--------|
| 1 - Immediate | Paying customers, active clients | Surface and summarize right away |
| 2 - Prompt | Engaged contacts, active threads | Surface promptly |
| 3 - Colleagues | Internal team, contractors | Surface promptly |
| 4 - Batch | Newsletters, automated notifications | Batch for later review |
| 5 - Deprioritize | Unknown senders | Default low priority |

**Exception lane**: Unknown senders may be elevated if they have objective evidence — replying to an existing thread, matching a known client domain, referencing a real calendar event, or reporting a credible security event (not self-claimed urgency).

**Anti-pattern**: Treating all unread email as equally important. A marketing newsletter with "URGENT" in the subject is not urgent. Self-claimed urgency from unknown senders is unreliable signal.

For the full triage model with anti-patterns and exception criteria, see the [Zero-Trust Email Triage skill](#related-skills).

## Email Drafting
> 邮件起草

When drafting replies:

- **Match the sender's tone** — if they wrote "Dear Steven," reply with "Dear [Name]," not "Hey!"
- **State the outcome, not the journey** — "The document is ready for your review" beats "I processed the document through our pipeline and..."
- **One clear ask per message** — don't bury the action item in paragraph three
- **Check threading** — if the subject has "Re:" or "RE:", find the original message and create a threaded reply, not a standalone draft

**Formatting gotchas** agents get wrong:

| Issue | Fix |
|-------|-----|
| Cuddled lists (no blank line before `- item`) | Always add a blank line before the first list item |
| Markdown in HTML email | Convert markdown to HTML before sending; raw `**bold**` renders as literal asterisks |
| Missing plain-text body | Always include both HTML and plain-text versions |
| Signature placement | Put the signature after the reply body, before the quoted thread |

For the complete drafting guide with tone calibration by relationship type, see the [Email Drafting skill](#related-skills).

## Inbox Organization
> 收件箱整理

Two levers for inbox control:

**One-time cleanup**: Scan recent inbox, identify the noisiest automated senders, create folders, batch-move existing emails.

**Ongoing rules**: Create server-side Outlook rules via Graph API to auto-sort future mail. Rules run on Microsoft's servers — they work even when no agent is running.

The workflow:

1. **Scan** — fetch recent inbox emails, count by sender, sort descending
2. **Categorize by action** — not by sender type:
   - Glance, don't act: CI notifications, build alerts, DMARC reports
   - Read when time allows: newsletters, marketing
   - Archive for records: receipts, invoices, payment confirmations
   - May need action: meeting bookings, security alerts
3. **Create folders** — 5-9 folders covers most inboxes. More and they stop getting checked.
4. **Move existing email** — batch-move matching messages to the new folders
5. **Create rules** — auto-sort future mail. Set `stopProcessingRules: true` to prevent cascade.
6. **Re-sweep** — rules only apply to future mail. After creating a rule, move existing matches too.

**Gotcha**: Meeting notifications (e.g., HubSpot booking confirmations) look like newsletters because of `noreply@` prefixes. Create a meeting-specific rule with a lower sequence number, or the generic newsletter rule will swallow them.

For the full cleanup workflow with Graph API gotchas and battle-tested patterns, see the [Inbox Cleanup skill](#related-skills).

## Email Heartbeat
> 邮件心跳检查

Three tiers of mailbox monitoring:

| Tier | Frequency | What to check |
|------|-----------|---------------|
| **Light** | Every 15-30 min | Unread count from priority senders only |
| **Deep** | Every 2-4 hours | Full triage pass — new unread from all senders, summarize by priority tier |
| **Digest** | Daily | End-of-day summary — what came in, what was handled, what needs follow-up |

**Light check pattern**:
1. List unread emails from priority sender domains
2. If any found, surface a one-line summary per email
3. If none, stay silent — no "no new email" noise

**Deep check pattern**:
1. List all unread emails
2. Classify by sender trust tier
3. Summarize Tier 1-2 emails individually
4. Batch Tier 3-5 into a count ("12 newsletters, 3 GitHub notifications")

**Digest pattern**:
1. List all emails received today
2. Group by: handled (replied/read), needs follow-up, informational
3. Highlight any Tier 1-2 emails that haven't been responded to

## Communicating Results to the User

Different users prefer different channels for email updates:

| Channel | When to use |
|---------|------------|
| **Chat interface** | Default. Summarize inline in the conversation. |
| **Text message** | If the user prefers distilled updates via messaging. Provide copy-paste text with phone number if no SMS tool is available. |
| **Calendar event** | For action items with deadlines — create an event instead of a reminder email. |
| **Summary email** | Only if explicitly requested. Be aware this adds to inbox clutter. |

Ask on first use — don't assume the user wants email summaries delivered by email.

## Gotchas That Will Bite You
> 常见陷阱

**Graph API `$search` cannot combine `from:` + `to:` KQL prefixes** — you get a 400 Syntax error. Use `$filter` instead when combining sender and recipient filters.

**`$select` does not work on PATCH requests** — returns 400 "OData request not supported." Only use `$select` on GET.

**Move is a POST, not a PATCH** — `POST /me/messages/{id}/move` with `{"destinationId": "<folder-id>"}`.

**Self-sent emails** are best found by listing `sentitems`, not searching inbox.

**Root-only folder listing** — `GET /me/mailFolders` returns only root-level folders. Child folders require recursive traversal via `/mailFolders/{id}/childFolders`.

**Inbox rule ordering** — `sequence` controls priority. Specific rules must fire before broad ones.

**Rules require `MailboxSettings.ReadWrite` scope** — if the OAuth token predates this scope, the user needs to re-consent.

For the complete reference with REST API patterns, pagination, attachments, and calendar integration, see [references/outlook-graph-patterns.md](./references/outlook-graph-patterns.md).

## Related Skills

Focused skills for specific email workflows:

- **Zero-Trust Email Triage** (`email-triage`) — sender-trust-based prioritization with exception lane for unknown senders
- **Email Response Drafting** (`email-drafting`) — tone-matching, formatting gotchas, thread detection
- **Inbox Cleanup & Rules** (`email-cleanup`) — folder management, Graph API rules, battle-tested cleanup workflow
- **NemoClaw Email Policy** (`nemoclaw-email-policy`) — network-level policy enforcement for email agents

Install a focused skill:
```
clawhub install stevenobiajulu/zero-trust-email-triage
clawhub install stevenobiajulu/email-response-drafting
clawhub install stevenobiajulu/inbox-cleanup-outlook
clawhub install stevenobiajulu/nemoclaw-email-policy
```

## Feedback

If this skill helped, star us on GitHub: https://github.com/UseJunior/email-agent-mcp
On ClawHub: `clawhub star stevenobiajulu/outlook-email-management`
