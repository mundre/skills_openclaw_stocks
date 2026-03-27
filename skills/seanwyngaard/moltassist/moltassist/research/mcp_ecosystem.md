# MCP Ecosystem Research -- Pulse Integration Strategy

> **Research date:** March 2026  
> **Purpose:** Evaluate the MCP landscape for Pulse -- a proactive AI assistant that watches a user's world and surfaces the right context at the right moment.  
> **Guiding principle:** Start with the moment. What does "how did it know?" feel like? Work backwards to the protocol.

---

## Table of Contents

1. [What is MCP?](#1-what-is-mcp)
2. [Why MCP Matters for Pulse](#2-why-mcp-matters-for-pulse)
3. [High-Value MCP Servers by Category](#3-high-value-mcp-servers-by-category)
   - [Productivity](#productivity)
   - [Communication](#communication)
   - [Developer Tools](#developer-tools)
   - [Data & Analytics / Finance](#data--analytics--finance)
   - [Web & Search](#web--search)
   - [Files & Local](#files--local)
   - [Infrastructure & Cloud](#infrastructure--cloud)
   - [Home & IoT](#home--iot)
4. [MCP vs Direct API -- Decision Framework](#4-mcp-vs-direct-api--decision-framework)
5. [MCP Hosting Strategy for Pulse](#5-mcp-hosting-strategy-for-pulse)
6. [Pulse Priority Tiers -- Recommended Rollout](#6-pulse-priority-tiers--recommended-rollout)
7. [Key Registries & Discovery Resources](#7-key-registries--discovery-resources)

---

## 1. What is MCP?

**Model Context Protocol (MCP)** is an open standard that defines how AI agents connect to external tools and data sources. Created by Anthropic in late 2024, it was donated to the **Agentic AI Foundation (AAIF)** under the Linux Foundation in December 2025 -- co-governed by Anthropic, Anthropic, Block, and OpenAI. As of March 2025, OpenAI adopted MCP and deprecated their proprietary Assistants API integration model.

### How it works

MCP is built on **JSON-RPC 2.0** over persistent connections (inspired by the Language Server Protocol). The core primitives are:

| Primitive | What it is | Example |
|---|---|---|
| **Tools** | Actions the AI can invoke | `send_message`, `create_issue`, `query_database` |
| **Resources** | Read-only data the AI can fetch | File contents, database records, calendar events |
| **Prompts** | Reusable instruction templates | Pre-built query patterns, context injectors |

### Transport options

- **stdio** -- Local subprocess communication (zero auth overhead, fastest for local tools)
- **SSE (Server-Sent Events)** -- Remote HTTP-based (used by Slack, Stripe, Sentry official servers)
- **Streamable HTTP** -- Next-gen transport in MCP spec roadmap (bidirectional, replaces SSE)

### Standard configuration pattern

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_..."
      }
    },
    "slack": {
      "url": "https://mcp.slack.com/mcp",
      "transport": "sse"
    }
  }
}
```

---

## 2. Why MCP Matters for Pulse

The classic problem with building Pulse via raw APIs: **N agents  M tools = NM custom integrations**. Add Slack? Write auth, error handling, schema parsing, and retry logic for every tool. Add Linear? Do it all again. This doesn't scale.

**MCP collapses NM to N+M.** Each tool writes one server. Pulse writes one client. As we add data sources, integration cost is additive, not multiplicative.

But more fundamentally: **MCP was designed for agents, not developers.** REST APIs are built for deterministic code. MCP is built for AI that reasons across tools dynamically. Pulse's entire value proposition -- proactive, contextual, timely -- requires exactly this: an agent that can say "let me check your calendar, cross-reference your inbox, and see what just broke in the CI pipeline" without a human writing the plumbing.

### The "how did it know?" architecture

For Pulse to create those magical moments, it needs access to:

1. **Signals** -- What's changing in the user's world right now?
2. **Context** -- What else is true that makes this signal meaningful?
3. **Timing** -- When is the user in a state to care?

MCP gives Pulse a standard way to pull signals from any connected system. The richer and more real-time the signal sources, the more moments Pulse can surface. This is the core argument for investing heavily in MCP coverage.

---

## 3. High-Value MCP Servers by Category

---

### Productivity

---

####  Notion MCP Server

- **Maintainer:** Official -- Notion ([`makenotion/notion-mcp-server`](https://github.com/makenotion/notion-mcp-server))
- **Hosted:** Remote (OAuth) at `https://mcp.notion.com` OR self-hosted with API token
- **Transport:** Remote SSE (OAuth) or local stdio (API key)
- **Stars:** Official Notion org repo, actively maintained (v2.0 released 2025, uses 2025-09-03 API)

**Tools exposed:**
- `create_page` -- Create new pages with structured content
- `search_content` -- Full-text search across entire workspace
- `retrieve_page` -- Get page as Markdown (token-efficient)
- `query_database` -- Filter/sort database entries
- `update_database_item` -- Modify database records
- `append_blocks` -- Add content to existing pages

**Pulse trigger scenarios:**
-  A database record's status changes to "Stuck" -> Pulse nudges the owner
-  A page hasn't been edited in 14 days (project likely stale) -> Pulse checks in
-  New row added to a CRM database -> Pulse summarises and surfaces to user
-  Notion search for keywords matching current context -> smart briefing

**Integration complexity:** Medium. OAuth for remote (one-click); API token for self-hosted.  
**Limitation:** Integration must be explicitly connected to each page/database in Notion settings.

---

####  Google Calendar MCP Server

- **Maintainer:** Community -- multiple implementations. Best: [`@cocal/google-calendar-mcp`](https://www.npmjs.com/package/@cocal/google-calendar-mcp)
- **Also:** Google announced fully-managed remote MCP across Google services (Dec 2025) -- Calendar included
- **Transport:** Local stdio with OAuth credentials

**Tools exposed:**
- `list_events` -- Upcoming events with date filtering
- `create_event` -- Schedule with attendees, location, description
- `update_event` / `delete_event` -- Modify/remove
- `get_freebusy` -- Check availability across calendars
- `search_events` -- Find by title or description

**Pulse trigger scenarios:**
-  Meeting starting in 30min -> auto-pull relevant emails, docs, last conversation with attendee
-  Back-to-back meetings with no buffer -> Pulse flags to reschedule
-  Recurring meeting has no agenda -> Pulse prompts to add one
-  Day starts with 6+ hours of meetings -> Pulse adjusts daily summary tone

**Integration complexity:** Medium. Google OAuth flow, requires Google Cloud credentials and Calendar API enabled.

---

####  Google Drive MCP Server

- **Maintainer:** Community -- [`google-drive-mcp`](https://www.npmjs.com/package/google-drive-mcp); also covered under Google's managed MCP announcement (Dec 2025)
- **Transport:** Local stdio with OAuth

**Tools exposed:**
- `search_files` -- Find by name, type, content
- `read_document` -- Get file content (Docs -> Markdown)
- `upload_file` -- Create new files
- `list_folder` -- Browse directory structure
- `get_permissions` -- Who has access?

**Pulse trigger scenarios:**
-  Document shared with user -> Pulse summarises it
-  Collaborative doc has been idle for N days -> Pulse notifies
-  Before a meeting, pull related Drive docs -> contextual briefing

**Integration complexity:** Medium. Same Google Cloud OAuth flow as Calendar.

---

####  Obsidian MCP Server

- **Maintainer:** Community -- [`MarkusPfundstein/mcp-obsidian`](https://github.com/MarkusPfundstein/mcp-obsidian) (via Obsidian REST API plugin) or [`jacksteamdev/obsidian-mcp-tools`](https://github.com/jacksteamdev/obsidian-mcp-tools) (semantic search + Templater)
- **Transport:** Local stdio (requires Obsidian Local REST API community plugin running)

**Tools exposed:**
- `read_note` -- Get note content by path
- `search_vault` -- Full-text or semantic search across vault
- `create_note` / `update_note` -- Write notes
- `list_notes` -- Browse vault structure
- `get_active_note` -- What the user is currently looking at (mcp-obsidian)

**Pulse trigger scenarios:**
-  User's working notes reference a topic that just appeared in the news -> Pulse surfaces it
-  A note flagged with `#followup` hasn't been touched in 7 days -> reminder
-  User mentions a project in chat -> Pulse searches vault for related notes
-  Semantic search finds relevant knowledge before a meeting

**Integration complexity:** Low-Medium. Requires Obsidian app running with REST API plugin. No cloud auth.

---

####  Microsoft 365 / Outlook / Teams

- **Maintainer:** No single official Microsoft MCP server yet (as of March 2026), but Microsoft is deeply invested in MCP via Copilot Studio and Playwright (official)
- **Community:** Multiple community implementations via Microsoft Graph API
- **Transport:** Local or remote, OAuth via Microsoft identity platform

**Tools exposed (via Graph API MCP wrappers):**
- Email: `list_messages`, `send_email`, `search_mail`, `get_thread`
- Calendar: `list_events`, `create_meeting`, `get_availability`
- Teams: `list_channels`, `post_message`, `search_messages`
- OneDrive: `list_files`, `read_document`

**Pulse trigger scenarios:**
- Same as Google Workspace equivalents
-  Teams message mentions user's name -> Pulse flags for urgent review
-  Meeting invite from senior stakeholder -> Pulse preps briefing

**Integration complexity:** High. Microsoft Graph OAuth is complex (tenant registration, scopes, consent flows). Enterprise grade.

---

### Communication

---

####  Slack MCP Server

- **Maintainer:** Official -- Slack ([`mcp.slack.com`](https://mcp.slack.com/mcp))
- **Transport:** Remote SSE with OAuth
- **Status:** Production. 47 tools. OAuth connects per-workspace.

**Tools exposed:**
- `slack_send_message` -- Post to channels by ID
- `slack_search_public` -- Search public channel messages
- `slack_search_public_and_private` -- Search all channels (with permissions)
- `slack_read_channel` -- Fetch message history
- `slack_read_thread` -- Get thread replies
- `slack_create_canvas` -- Create Slack-native documents
- `slack_list_channels` -- Enumerate accessible channels
- `slack_get_user_info` -- User profile data

**Community alternative:** [`korotovsky/slack-mcp-server`](https://github.com/korotovsky/slack-mcp-server) -- "stealth mode" (no bot install required, uses user token), OAuth mode, DMs, Group DMs.

**Pulse trigger scenarios:**
-  User mentioned or DM'd -> Pulse classifies urgency and surfaces if high
-  Channel silent for N days -> flag potential team blocker
-  Keyword/topic appears in a channel user cares about -> proactive summary
-  Thread on a PR/issue the user owns -> Pulse catches it before it's buried

**Integration complexity:** Low (remote OAuth, no local install). Bot must be invited to private channels.

---

####  Gmail MCP Server

- **Maintainer:** Community -- `mcp-google-workspace` (npm) covers Gmail + Calendar + Drive together; Google's managed MCP endpoint also covers Gmail
- **Transport:** Remote OAuth (claude.ai integration) or local stdio (self-hosted)

**Tools exposed:**
- `send_email` -- Compose and send
- `search_emails` -- Full Gmail query syntax (`from:`, `subject:`, `has:attachment`, etc.)
- `get_unread_emails` -- Inbox unread fetch
- `read_email` -- Full message content
- `trash_email` -- Move to trash
- `modify_email` -- Labels, read/unread, archive
- `list_labels` -- Available Gmail labels

**Pulse trigger scenarios:**
-  VIP sender email arrives -> Pulse summarises and alerts immediately
-  Urgent keywords detected (invoice overdue, server down, urgent) -> proactive flag
-  Thread you're CC'd on gets a new reply -> Pulse decides if you need to know
-  Morning brief: unread count, top 3 emails to act on

**Integration complexity:** Medium. Google OAuth 2.0, Gmail API enabled in Cloud Console.

---

####  Telegram MCP Server

- **Maintainer:** Community -- various implementations using Telegram Bot API and MTProto
- **Examples:** [`Anman61/telegram-mcp`](https://github.com/Anman61/telegram-mcp), Pyrogram/Telethon-based servers
- **Transport:** Local stdio (API token or user session)

**Tools exposed (varies by implementation):**
- `send_message` -- Send to channel/group/user
- `get_messages` -- Fetch chat history
- `list_chats` -- Enumerate conversations
- `search_messages` -- Search across chat history
- `get_channel_info` -- Channel/group metadata

**Pulse trigger scenarios:**
-  Message in a monitored channel matches keyword -> surface to user
-  Group chat goes quiet or spikes in activity -> Pulse flags the pattern
-  Unread DMs from specific contacts -> prioritised alert

**Integration complexity:** Low-Medium. Bot API is simple (token only). User-level access (MTProto) requires phone auth -- powerful but sensitive.

---

### Developer Tools

---

####  GitHub MCP Server

- **Maintainer:** Official -- GitHub ([`@modelcontextprotocol/server-github`](https://github.com/modelcontextprotocol/servers/tree/main/src/github))
- **Transport:** Local stdio
- **Status:** Gold standard. Most widely used MCP server in dev workflows.

**Tools exposed:**
- `create_pull_request` -- Open PRs with full diff context
- `get_issue` / `create_issue` / `search_issues` -- Issue management
- `list_files` / `get_file_contents` -- Repository navigation
- `search_code` -- Code search across repos
- `get_workflow_runs` -- CI/CD pipeline status
- `create_branch` -- Branch management
- `push_files` -- Commit changes
- `fork_repository` -- Fork repos

**Pulse trigger scenarios:**
-  PR review requested -> Pulse summarises diff and surfaces to developer
-  CI pipeline fails on main -> immediate alert with error context
-  Issue assigned to user -> Pulse cross-references with current sprint
-  PR has been open 5+ days with no activity -> nudge to merge or close
-  Repo dependency has a known CVE -> security alert

**Integration complexity:** Low. Personal access token. Scopes configurable.

---

####  GitLab MCP Server

- **Maintainer:** Official (archived in modelcontextprotocol/servers-archived); Community alternatives active
- **Community:** [`zereight/gitlab-mcp`](https://github.com/zereight/gitlab-mcp), others
- **Transport:** Local stdio

**Tools exposed:**
- Project management (issues, merge requests, pipelines)
- Repository operations (files, branches, commits)
- CI/CD status and job logs
- Group/namespace management

**Pulse trigger scenarios:**
- Same as GitHub equivalents
-  GitLab pipeline fails -> Pulse surfaces with job output
-  Merge request stuck in review -> escalation nudge

**Integration complexity:** Low. GitLab personal access token or OAuth.

---

####  Linear MCP Server

- **Maintainer:** Community -- [`@mcp-devtools/linear`](https://www.npmjs.com/package/@mcp-devtools/linear)
- **Transport:** Local stdio
- **Status:** Actively maintained, widely used by eng teams.

**Tools exposed:**
- `create_issue` / `update_issue` -- Issue lifecycle
- `list_issues` -- Filter by project, cycle, assignee, status
- `create_project` / `update_project` -- Project management
- `search_issues` -- Full-text search
- `list_cycles` -- Sprint/cycle management
- `transition_issue` -- Status changes (Todo -> In Progress -> Done)

**Pulse trigger scenarios:**
-  Issue assigned to user -> Pulse reads it and offers context from codebase
-  Sprint ends tomorrow with 40% completion -> Pulse flags to re-plan
-  P0 bug created -> immediate alert regardless of time
-  Issue blocked for 3+ days -> Pulse escalates or asks what's needed

**Integration complexity:** Low. API key from Linear Settings > API > Create Key.

---

####  Atlassian MCP Server (Jira + Confluence)

- **Maintainer:** Official -- Atlassian ([`mcp.atlassian.com/v1/sse`](https://mcp.atlassian.com/v1/sse))
- **Transport:** Remote SSE with OAuth. Built on Cloudflare Agents SDK.
- **Status:** Remote beta. Enterprise-grade OAuth.

**Tools exposed:**
- Jira: `create_issue`, `search_issues` (JQL), `update_issue`, `add_comment`, `transition_issue`
- Confluence: `search_pages`, `create_page`, `update_page`, `get_page`

**Community alternative (self-hosted):** `@mcp-devtools/jira` with API token

**Pulse trigger scenarios:**
-  Jira ticket status changes to Blocked -> Pulse alerts owner + manager
-  New bug linked to current sprint -> daily digest update
-  Confluence page edited in project space -> Pulse checks if decision changed
-  JQL query: "issues due today with no updates this week" -> proactive sprint check

**Integration complexity:** Low (remote OAuth). Self-hosted requires API token + URL.

---

####  Sentry MCP Server

- **Maintainer:** Official -- Sentry ([`mcp.sentry.dev/mcp`](https://mcp.sentry.dev/mcp))
- **Transport:** Remote SSE with OAuth
- **Status:** Production. Seer AI debugging integration included.

**Tools exposed:**
- Query errors and issues by project/org
- Get full error context (stack traces, breadcrumbs)
- Seer analysis -- AI-assisted root cause
- Performance telemetry and metrics
- Link errors to releases/commits

**Pulse trigger scenarios:**
-  New error spike in production -> Pulse summarises error + likely cause
-  Error rate crosses threshold -> immediate alert to on-call dev
-  New error is first-seen -> Pulse checks if similar issues exist
-  Deploy just happened -> Pulse monitors Sentry for regression

**Integration complexity:** Low. Remote OAuth, select tool groups during auth.

---

### Data & Analytics / Finance

---

####  Stripe MCP Server

- **Maintainer:** Official -- Stripe ([`mcp.stripe.com`](https://mcp.stripe.com))
- **Docs:** [docs.stripe.com/mcp](https://docs.stripe.com/mcp)
- **Transport:** Remote SSE with OAuth
- **Status:** Production. Covers full Stripe API + knowledge base (docs, support articles).

**Tools exposed:**
- Payments: `list_charges`, `retrieve_charge`, `create_payment_intent`
- Customers: `list_customers`, `retrieve_customer`, `create_customer`
- Subscriptions: `list_subscriptions`, `update_subscription`, `cancel_subscription`
- Invoices: `list_invoices`, `retrieve_invoice`
- Products & Prices: CRUD operations
- Disputes: `list_disputes`, `retrieve_dispute`
- Knowledge search: search Stripe docs and support articles

**Pulse trigger scenarios:**
-  Churn spike detected (multiple subscription cancellations in short window) -> alert
-  High-value customer's charge fails -> urgent notification
-  Dispute filed against payment -> immediate escalation
-  Revenue goal hit/missed by end of day -> proactive business digest
-  Unusual refund pattern -> fraud flag

**Integration complexity:** Low. Remote OAuth via Stripe dashboard.

---

####  Shopify MCP Server

- **Maintainer:** Community -- [`GeLi2001/shopify-mcp`](https://github.com/GeLi2001/shopify-mcp) (16 tools, GraphQL)
- **Transport:** Local stdio
- **Status:** Community, actively maintained. No official Shopify MCP yet.

**Tools exposed (16 tools via Shopify GraphQL Admin API):**
- Products: CRUD, inventory levels
- Customers: profile, order history
- Orders: list, retrieve, fulfillment status
- Collections: product groupings
- Webhooks: subscription management
- Metafields: custom data

**Pulse trigger scenarios:**
-  Out-of-stock on top-selling product -> proactive restocking alert
-  Order spike (flash sale working) -> surface metrics in real-time
-  High-value customer places first order -> personalised flag
-  Abandoned cart rate rises -> alert to check checkout flow

**Integration complexity:** Medium. Shopify Admin API token, store URL required.

---

####  PostgreSQL MCP Server

- **Maintainer:** Google (Toolbox) + Community ([`@crystaldba/postgres-mcp`](https://www.npmjs.com/package/@crystaldba/postgres-mcp))
- **Transport:** Local stdio
- **Status:** Multiple solid implementations. Google Toolbox is enterprise-grade.

**Tools exposed:**
- `execute_sql` -- Run queries with safety controls
- `list_schemas` / `list_tables` -- Database structure navigation
- `describe_table` -- Column info, types, constraints
- `explain_query` -- Query plan analysis
- `create_index` / `analyze_table` -- Performance tools (Postgres MCP Pro)

**Pulse trigger scenarios:**
-  Anomalous query pattern detected -> Pulse alerts (if connected to monitoring)
-  User asks "why is the dashboard slow?" -> Pulse queries DB, runs EXPLAIN
-  Business metric crosses threshold -> event-driven alert (requires polling layer)

**Integration complexity:** Low-Medium. Connection string. Use read-only credentials in production.  
 **Security:** Never expose write access to untrusted agents. Use read-only DB user.

---

####  SQLite MCP Server

- **Maintainer:** Official -- Anthropic ([`@modelcontextprotocol/server-sqlite`](https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite))
- **Transport:** Local stdio (file path arg)
- **Status:** Reference implementation. Stable.

**Use for Pulse:** Local user data store, preferences, history, trigger logs. Great for prototyping event pipelines.

---

### Web & Search

---

####  Brave Search MCP Server

- **Maintainer:** Official -- Brave ([`@anthropic/brave-search-mcp`](https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search))
- **Transport:** Local stdio
- **Status:** Official. Requires Brave Search API key (free tier available at api.search.brave.com).

**Tools exposed:**
- `web_search` -- Web search with privacy-respecting results
- `local_search` -- Location-based results (restaurants, services, etc.)

**Pulse trigger scenarios:**
-  User is about to meet with a company -> Pulse searches recent news about them
-  A project references a technology -> Pulse surfaces latest docs/releases
-  User asks about something Pulse doesn't have in memory -> real-time search

**Integration complexity:** Low. API key only.

---

####  Fetch MCP Server

- **Maintainer:** Official -- Anthropic ([`@modelcontextprotocol/server-fetch`](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch))
- **Transport:** Local stdio
- **Status:** Reference implementation. No auth required.

**Tools exposed:**
- `fetch` -- Fetch any URL and convert to Markdown/text for LLM consumption
- Configurable robots.txt respect, user-agent, content extraction

**Pulse trigger scenarios:**
-  Monitoring a URL for changes (pair with cron/polling) -> content diff alerts
-  Pull current price/status from a webpage before alerting user
-  Pre-meeting: fetch LinkedIn profile, company homepage

**Integration complexity:** None. Install and run.

---

####  Playwright MCP Server (Browser Automation)

- **Maintainer:** Official -- Microsoft ([`@playwright/mcp`](https://www.npmjs.com/package/@playwright/mcp))
- **Transport:** Local stdio
- **Status:** Production. Officially maintained by Microsoft.

**Tools exposed:**
- `browser_navigate` -- Go to URL
- `browser_click` / `browser_fill` -- Interact with elements
- `browser_screenshot` -- Capture page
- `browser_evaluate` -- Run JavaScript
- `browser_snapshot` -- Accessibility tree (lightweight vs screenshot)
- `browser_wait_for` -- Wait for element/condition

**Pulse trigger scenarios:**
-  Competitor changes pricing page -> visual/text diff alert
-  Status page shows degradation -> extract and surface the text
-  Web scraping sites that don't have APIs (e.g., public government data)

**Integration complexity:** Low. `npx @playwright/mcp` -- browser installs automatically.

---

### Files & Local

---

####  Filesystem MCP Server

- **Maintainer:** Official -- Anthropic ([`@modelcontextprotocol/server-filesystem`](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem))
- **Transport:** Local stdio (access restricted to specified paths)
- **Status:** Reference implementation. Stable.

**Tools exposed:**
- `read_file` -- Get file contents
- `write_file` -- Create/update files
- `list_directory` -- Browse directory structure
- `search_files` -- Pattern/regex matching across files
- `get_file_info` -- Size, modified date, permissions
- `move_file` -- Rename/move
- `create_directory` -- Folder creation

**Pulse trigger scenarios:**
-  Important file modified unexpectedly -> alert
-  Disk space approaching limit -> proactive warning
-  User is in a project -> Pulse reads local README, package.json for context
-  Log file contains ERROR lines in past hour -> surface to developer

**Integration complexity:** None. Path-based access control.

---

####  Memory MCP Server (Knowledge Graph)

- **Maintainer:** Official -- Anthropic ([`@modelcontextprotocol/server-memory`](https://github.com/modelcontextprotocol/servers/tree/main/src/memory))
- **Transport:** Local stdio
- **Status:** Reference implementation. Persistent JSON-based graph.

**Tools exposed:**
- `create_entities` -- Add nodes (people, projects, concepts)
- `create_relations` -- Connect nodes with typed relationships
- `search_nodes` -- Find by name or type
- `open_nodes` -- Get connected context graph
- `add_observations` -- Append facts to existing entities
- `delete_entities` / `delete_relations` -- Graph maintenance

**Pulse trigger scenarios:**
- This IS the Pulse brain. Store everything Pulse learns about the user.
- User mentions a contact -> Memory server stores name, context, relationship
- Project started -> node created, linked to tools, teammates, deadlines
-  Pulse connects new incoming event to existing entity -> richer context

**Integration complexity:** None. Local file-backed graph. Critical infrastructure for Pulse.

---

####  Git MCP Server

- **Maintainer:** Official -- Anthropic ([`mcp-server-git`](https://github.com/modelcontextprotocol/servers/tree/main/src/git))
- **Transport:** Local stdio
- **Status:** Reference implementation.

**Tools exposed:**
- `git_log` -- Commit history with diffs
- `git_status` -- Working tree changes
- `git_diff` -- File-level diffs
- `git_commit` -- Create commits
- `git_branch` -- Branch management
- `git_show` -- Specific commit details

**Pulse trigger scenarios:**
-  Nothing committed in 3 days on active project -> nudge
-  Large uncommitted change detected -> remind to commit
-  Branch diverged from main by 50+ commits -> flag merge conflict risk

**Integration complexity:** None. Operates on local git repos.

---

### Infrastructure & Cloud

---

####  Google Cloud MCP (Managed)

- **Maintainer:** Official -- Google ([announced Dec 2025](https://cloud.google.com/blog/products/ai-machine-learning/announcing-official-mcp-support-for-google-services))
- **Scope:** BigQuery, Maps, Compute Engine, GKE, Cloud SQL, Spanner, Firestore, Bigtable, AlloyDB
- **Transport:** Remote managed endpoints (IAM auth)

**Notable services for Pulse:**
- **BigQuery** -- Query enterprise data at scale; agents interpret schemas and run SQL
- **Maps** -- Geospatial context (distances, places, weather, routing)
- **Cloud SQL** -- Managed database access

**Pulse trigger scenarios:**
-  BigQuery anomaly in business metrics -> proactive alert
-  User traveling -> Maps MCP provides weather, traffic, place data

---

####  Docker MCP Gateway

- **Maintainer:** Docker Inc.
- **What it does:** Manages lifecycle of MCP servers -- launches on-demand, routes tool calls, handles auth centrally
- **Relevance for Pulse:** A gateway pattern Pulse could implement internally to manage per-user MCP instances

---

####  Qdrant MCP Server (Vector Memory)

- **Maintainer:** Official -- Qdrant ([`qdrant-mcp`](https://www.npmjs.com/package/qdrant-mcp))
- **Transport:** Local stdio
- **Status:** Production, actively maintained.

**Tools exposed:**
- Collection management (create, list, delete)
- `upsert_points` -- Store vectors + payload
- `search_points` -- Semantic similarity search
- `scroll_points` -- Paginated browsing

**Pulse trigger scenarios:**
- Semantic memory for Pulse -- store embeddings of user's past interactions
-  New event semantically similar to past experience -> Pulse recalls context
- RAG over user's documents, emails, notes

**Integration complexity:** Low-Medium. Requires Qdrant instance running (local Docker or Qdrant Cloud).

---

### Home & IoT

---

####  Home Assistant MCP Server

- **Maintainer:** Community -- [`allenporter/hass-mcp`](https://github.com/allenporter/hass-mcp)
- **Transport:** Local or remote (Home Assistant REST API)
- **Status:** Community, growing adoption

**Tools exposed:**
- Query entity states (lights, sensors, switches, thermostats)
- Call services (turn on/off, set temperature, run automations)
- Get device history

**Pulse trigger scenarios:**
-  Front door unlocked while user is away -> alert
-  Temperature sensor spikes -> Pulse flags unusual reading
-  User leaves home (presence detection) -> Pulse adjusts reminders context
-  Smart alarm goes off -> Pulse prepares morning briefing

**Integration complexity:** Medium. Requires Home Assistant with Long-Lived Access Token.

---

## 4. MCP vs Direct API -- Decision Framework

### When to use MCP

| Scenario | Use MCP | Reason |
|---|---|---|
| 3+ integrations |  | NM problem becomes N+M |
| Dynamic tool landscape |  | New tools auto-discovered at runtime |
| Multi-step agent workflows |  | Stateful sessions, multi-tool composition |
| Well-supported service (Slack, Stripe, GitHub) |  | Official servers are polished and maintained |
| User consent/OAuth flows |  | MCP centralises auth governance |
| Local tools (filesystem, git, DB) |  | stdio is zero-overhead and secure |

### When to use Direct API

| Scenario | Use Direct API | Reason |
|---|---|---|
| Single, simple integration |  | MCP overhead not worth it |
| Webhooks / push events |  | MCP is pull-based; webhooks are push |
| Custom logic not expressible as tools |  | Full code control |
| High-frequency polling (sub-second) |  | MCP sessions have overhead |
| Service with no MCP server |  | Build or wait |

### The key architectural insight for Pulse

> **MCP is for reading context. Webhooks/push APIs are for receiving signals.**

Pulse's architecture should be:
- **Webhooks/subscriptions -> Trigger layer** (Slack events, GitHub webhooks, Stripe event stream, calendar push notifications)
- **MCP -> Context enrichment layer** (when a trigger fires, Pulse uses MCP to gather rich context before acting)
- **Direct API -> Write actions** (send message, create issue, update record)

**Example flow:**
1. GitHub webhook: "PR review requested on `feature/payments`"
2. Pulse fires MCP tools: `get_issue`, `search_code` (codebase context), `slack_search_private` (any discussion about this), `list_events` (does user have time to review today?)
3. Pulse composes: "Hey -- PR review needed on the payments feature. You have a gap at 2pm. Here's a 3-line summary of the diff."
4. Pulse posts via direct Slack/Telegram API call.

---

### Tradeoffs Summary

| Dimension | MCP | Direct API |
|---|---|---|
| **Setup cost** | Higher (protocol overhead) | Lower (just call endpoint) |
| **Maintenance** | Lower (server maintained externally) | Higher (your code) |
| **Flexibility** | Lower (tool schema constraints) | Higher (anything goes) |
| **Agent-native** |  Yes |  No |
| **Auth governance** | Centralised | Scattered |
| **Discovery** | Dynamic (runtime) | Static (hardcoded) |
| **Stateful sessions** |  Yes |  Per-request only |
| **Real-time push** |  No (pull only) |  Yes (webhooks) |

---

## 5. MCP Hosting Strategy for Pulse

### The three patterns (per AWS Prescriptive Guidance)

#### Pattern A: Local (stdio)
- MCP server runs as subprocess on user's machine
- Best for: filesystem, git, local databases, Obsidian
- Pros: zero network latency, no auth overhead, uses user's existing credentials
- Cons: user must install; can't manage remotely; versioning is hard

#### Pattern B: Remote (SSE/HTTP)
- MCP server hosted in cloud, accessed over HTTPS
- Best for: Slack, Stripe, Sentry, Atlassian (they host their own)
- Pros: centralised updates, OAuth managed, no user install
- Cons: network latency; Pulse needs to handle auth token refresh; stateful sessions are hard to scale

#### Pattern C: MCP Gateway
- Single endpoint that routes to many backend MCP servers
- Best for: Pulse at scale (managing 10+ integrations per user)
- Pros: one connection per user; dynamic tool discovery; centralized auth/routing
- Cons: complex to build; stateful session scaling (Glama runs 2,000+ VMs for this reason)

### Recommended Pulse architecture

**Phase 1 (MVP -- local user install):**
- Give users a Pulse desktop client that runs local MCP servers (filesystem, git, memory, SQLite)
- Connect to remote official servers (Slack, Stripe, GitHub, Notion) via OAuth
- User manages their own credentials via simple Pulse config UI

**Phase 2 (SaaS product -- per-user cloud instances):**
- Pulse cloud runs an MCP Gateway per user
- Each gateway manages their connected integrations
- Stateless servers (Brave Search, Fetch) run as shared instances
- Stateful servers (Memory, vector DB) run as isolated per-user containers
- Auth tokens encrypted per-user in Pulse backend

**Phase 3 (Scale):**
- Implement Smithery Connect pattern: managed OAuth + credential storage
- Allow third-party MCP servers to register with Pulse
- Semantic tool discovery (user connects "my Shopify store" -> Pulse discovers and registers relevant tools)

### Critical insight from community (Reddit/Glama)

> "Hosting thousands of stateful MCP servers is really hard. Glama has over 2,000 VMs running. What's easy is hosting stateless/shared instances."

**Pulse should:**
- Start with stateless shared instances for commodity tools (search, fetch, public APIs)
- Use per-user isolated containers only for stateful, sensitive data (memory, filesystem, OAuth tokens)
- Leverage existing hosted servers (Slack at `mcp.slack.com`, Stripe at `mcp.stripe.com`) to offload infrastructure

---

## 6. Pulse Priority Tiers -- Recommended Rollout

### Tier 1 -- Core "How Did It Know?" Signals (Build first)

| Server | Why | Transport |
|---|---|---|
| **Memory (knowledge graph)** | Pulse's long-term brain -- connects all context | Local |
| **Gmail / Google Calendar** | Most users' primary work surface | OAuth local/remote |
| **Slack** | Where most work decisions happen | Remote OAuth |
| **GitHub** | Strongest dev signal density | Local |
| **Filesystem** | User's actual work, not just cloud | Local |
| **Brave Search / Fetch** | Real-world grounding, no blind spots | Local |

### Tier 2 -- Rich Context Amplifiers (Build next)

| Server | Why | Transport |
|---|---|---|
| **Notion** | Where knowledge and projects live | Remote OAuth |
| **Linear / Jira** | Sprint and work item context | Local/Remote |
| **Stripe** | Business health pulse | Remote OAuth |
| **Sentry** | Production health for dev users | Remote OAuth |
| **Qdrant** | Semantic memory, RAG over user's world | Local |
| **Playwright** | Web world access for any site | Local |

### Tier 3 -- Power User / Vertical Depth

| Server | Why | Transport |
|---|---|---|
| **Shopify** | E-commerce founders | Local |
| **Home Assistant** | Ambient context (presence, environment) | Local/Remote |
| **Obsidian** | Knowledge workers with local notes | Local |
| **Telegram** | Community managers, international users | Local |
| **BigQuery / Cloud SQL** | Data teams, analytics users | Remote |
| **MongoDB / Supabase** | Developers with cloud databases | Local |

---

## 7. Key Registries & Discovery Resources

| Resource | URL | Notes |
|---|---|---|
| **Official MCP Registry** | [registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io/) | Canonical source of truth |
| **Smithery** | [smithery.ai](https://smithery.ai/) | Largest marketplace, managed OAuth/hosting, install tooling |
| **Glama MCP Directory** | [glama.ai/mcp/servers](https://glama.ai/mcp/servers) | 2,000+ servers, synced with punkpeye awesome list |
| **PulseMCP** | [pulsemcp.com](https://www.pulsemcp.com/) | Directory with usage rankings |
| **mcpservers.org** | [mcpservers.org](https://mcpservers.org/) | Community curated |
| **Awesome MCP Servers** | [github.com/punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) | Most comprehensive list, 948 PRs open |
| **Wong2 Awesome MCP** | [github.com/wong2/awesome-mcp-servers](https://github.com/wong2/awesome-mcp-servers) | Curated alternative list |
| **Anthropic Reference Servers** | [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | Official reference implementations |
| **MCP Spec Docs** | [modelcontextprotocol.io](https://modelcontextprotocol.io/) | Protocol specification |
| **AWS MCP Strategy Guide** | [docs.aws.amazon.com/.../mcp-hosting-strategy](https://docs.aws.amazon.com/prescriptive-guidance/latest/mcp-strategies/mcp-hosting-strategy.html) | Hosting patterns |

---

## Appendix: Quick Reference -- Auth Patterns

| Pattern | Examples | Notes |
|---|---|---|
| **No auth** | Filesystem, SQLite, Git, Fetch | Local only. Implicit OS-level trust. |
| **API key** | GitHub, Linear, Brave Search, Shopify | Simple. Store in env vars. Easy to rotate. |
| **OAuth 2.0** | Slack, Notion, Gmail, Stripe, Sentry, Atlassian | Browser consent flow. Refresh token management needed. |
| **Complex OAuth** | Microsoft 365, Google Cloud | Tenant/project registration. Enterprise complexity. |

---

*Research compiled from: modelcontextprotocol.io, registry.modelcontextprotocol.io, smithery.ai, glama.ai, punkpeye/awesome-mcp-servers, blog.premai.io, AWS Prescriptive Guidance, Google Cloud Blog, atlan.com, individual server GitHub repos.*

*Last updated: March 2026*
