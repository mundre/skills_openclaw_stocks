# FlowyTeam MCP

> Connect Claude Code (or any MCP-compatible AI agent) to your FlowyTeam workspace and manage your entire business via natural language.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP Protocol](https://img.shields.io/badge/MCP-2024--11--05-blue.svg)](https://modelcontextprotocol.io)
[![Tools](https://img.shields.io/badge/Tools-31-orange.svg)](SKILL.md)
[![Platform](https://img.shields.io/badge/Platform-FlowyTeam-teal.svg)](https://flowyteam.com)

---

## What is FlowyTeam?

[FlowyTeam](https://flowyteam.com) is an all-in-one SaaS platform for team productivity and performance management — OKRs, KPIs, projects, HR, CRM, finance, and more. Trusted by 7,000+ organizations across 140+ countries.

---

## What does this MCP do?

This skill connects Claude Code (or any MCP client) to your FlowyTeam workspace via a remote HTTP MCP server. Once connected, you can manage your entire workspace through natural language — no need to open the app.

**31 tools. Full CRUD. No extra software required.**

---

## Quick Start

### 1. Get your API Token

Log in to FlowyTeam → **Settings → API Token** → Copy your token.

### 2. Connect with Claude Code

```bash
claude mcp add flowyteam \
  --transport http \
  --url https://flowyteam.com/api/v2/mcp/rpc \
  --header "Authorization: Bearer YOUR_API_TOKEN"
```

### 3. Or use Claude Desktop / Cursor

Add this to your `mcp.json`:

```json
{
  "mcpServers": {
    "flowyteam": {
      "transport": "http",
      "url": "https://flowyteam.com/api/v2/mcp/rpc",
      "headers": {
        "Authorization": "Bearer YOUR_API_TOKEN"
      }
    }
  }
}
```

### 4. Start talking to your workspace

```
"Create a task 'Review Q2 Report' in Marketing project, assign to Sarah, due April 30"
"Show me all open high-priority tickets"
"Who is on leave this week?"
"What are our company OKRs for Q2 2026?"
"Log 8 hours on the Mobile App project for today"
"Create an invoice for Acme Corp, total $5,000, due May 31"
```

---

## Tools (31)

| # | Tool | Description | Methods |
|---|---|---|---|
| 1 | `tasks` | Manage tasks and assignments | GET POST PUT DELETE |
| 2 | `projects` | Manage projects and workflow | GET POST PUT DELETE |
| 3 | `employees` | Manage employees and team members | GET POST PUT DELETE |
| 4 | `objectives` | Manage OKR objectives | GET POST PUT DELETE |
| 5 | `key-result` | Manage OKR key results | GET POST PUT DELETE |
| 6 | `indicators` | Manage KPIs and performance indicators | GET POST PUT DELETE |
| 7 | `indicator-record` | Log KPI actual values per period | GET POST DELETE |
| 8 | `leads` | Manage sales leads and prospects | GET POST PUT DELETE |
| 9 | `clients` | Manage clients and relationships | GET POST PUT DELETE |
| 10 | `tickets` | Manage support tickets | GET POST PUT DELETE |
| 11 | `attendance` | Clock in / clock out / attendance history | GET POST PUT |
| 12 | `leave` | Manage leave requests and approvals | GET POST PUT DELETE |
| 13 | `department` | Manage departments and teams | GET POST PUT DELETE |
| 14 | `designation` | Manage job designations | GET POST PUT DELETE |
| 15 | `performance-cycle` | Manage performance / OKR cycles | GET POST PUT DELETE |
| 16 | `holiday` | Manage company public holidays | GET POST PUT DELETE |
| 17 | `project-category` | Manage project categories | GET POST PUT DELETE |
| 18 | `task-category` | Manage task categories | GET POST PUT DELETE |
| 19 | `ticket-type` | Manage ticket types | GET POST PUT DELETE |
| 20 | `ticket-channel` | Manage ticket channels | GET POST PUT DELETE |
| 21 | `ticket-agent` | List ticket agents and groups | GET |
| 22 | `indicator-category` | Manage KPI categories | GET POST PUT DELETE |
| 23 | `leave-type` | Manage leave types (Annual, Sick, etc.) | GET POST PUT DELETE |
| 24 | `invoices` | Manage client invoices | GET POST PUT DELETE |
| 25 | `estimates` | Manage client estimates and quotes | GET POST PUT DELETE |
| 26 | `contracts` | Manage client contracts | GET POST PUT DELETE |
| 27 | `events` | Manage company calendar events | GET POST PUT DELETE |
| 28 | `expenses` | Manage expenses and claims | GET POST PUT DELETE |
| 29 | `expense-category` | Manage expense categories | GET POST PUT DELETE |
| 30 | `notices` | Manage company notice board | GET POST PUT DELETE |
| 31 | `timelogs` | Start/stop timers, log project hours | GET POST PUT DELETE |

---

## How It Works

This MCP uses **Streamable HTTP transport (JSON-RPC 2.0)**. Every tool accepts a `method` parameter to select the operation:

| `method` | Operation |
|---|---|
| `GET` | Read / list records |
| `POST` | Create a new record |
| `PUT` | Update an existing record |
| `DELETE` | Delete a record |

**Protocol:** `POST https://flowyteam.com/api/v2/mcp/rpc`
**Auth:** `Authorization: Bearer <api_token>`
**MCP Protocol Version:** `2024-11-05`

---

## Smart Features

Several tools support **name-based resolution** — you don't need to look up IDs manually:

- `department` — lookup by `name` string (auto-finds the ID for PUT/DELETE)
- `invoices` — lookup by `invoice_number` (e.g. `INV#0001`)
- `estimates` — lookup by `estimate_number` (e.g. `EST#0003`)
- `contracts` — lookup by `subject` (partial match)
- `events` — lookup by `event_name` (partial match)
- `expenses` — lookup by `item_name` (partial match)
- `timelogs` — resolve `project_name` → ID, `task_name` → ID, `employee_name` → ID
- `timelogs` PUT — without `id`, finds the currently running timer automatically

---

## Permissions

| Role | Capabilities |
|---|---|
| **Admin** | Full read/write access to all tools |
| **Employee** | Read + self-service (own tasks, attendance, leave, expenses, time logs) |

Some modules (`invoices`, `estimates`, `contracts`, `events`, `expenses`, `notices`, `timelogs`) require the corresponding module to be enabled in your FlowyTeam plan.

---

## Full Documentation

- **MCP Server page:** [flowyteam.com/get/mcp-server](https://flowyteam.com/get/mcp-server)
- **API Reference:** [flowyteam.com/get/mcp-docs](https://flowyteam.com/get/mcp-docs)
- **Tool parameters:** See [SKILL.md](SKILL.md)

---

## Sign Up

Don't have a FlowyTeam account yet? [Sign up free](https://app.flowyteam.com/register)

---

## License

MIT — free to use, modify, and distribute.
