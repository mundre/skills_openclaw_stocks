---
name: email-manager-with-db
description: "Email account manager with IMAP/SMTP support and local database. Manage multiple email accounts, sync inbox, send emails, search, set filters, and generate daily send reports. Triggers: email manager, manage email, send email, check inbox, email account, imap smtp, email report, email filter"
allowed-tools: Bash
---

# Email Manager Skill

This skill manages email accounts and interacts with them via IMAP and SMTP.

## Commands

### `account`

Manage email accounts.

- **`add`**: Add a new email account.
  - `node cli.js account add --email <email> --password <app-password> [--imap-host <host>] [--imap-port <port>] [--smtp-host <host>] [--smtp-port <port>]`
- **`list`**: List all configured email accounts.
  - `node cli.js account list`
- **`remove`**: Remove an email account.
  - `node cli.js account remove <account-id>`

### `test`

Test the IMAP and SMTP connection for an account.
`node cli.js test <account-id>`

### `sync`

Sync emails from the server.
`node cli.js sync <account-id> [--folder <folder-name>] [--limit <number>]`

### `inbox`

List emails in the inbox.
`node cli.js inbox <account-id> [--limit <number>] [--unread] [--no-filtered]`

### `read`

Read the content of a specific email.
`node cli.js read <email-id>`

### `send`

Send an email.
`node cli.js send <account-id> --to <recipient> --subject "<subject>" --body "<body>"`

### `search`

Search for emails.
`node cli.js search <account-id> --query "<query>"`

### `folders`

List all folders for an account.
`node cli.js folders <account-id>`

### `filter`

Manage email filters.

- **`list`**: List all filter rules.
  - `node cli.js filter list [account-id]`
- **`add`**: Add a new filter rule.
  - `node cli.js filter add --field <from|to|subject> --pattern "<pattern>" [--account-id <id>]`
- **`remove`**: Remove a filter rule.
  - `node cli.js filter remove <rule-id>`

### `stats`

Show statistics about emails.
`node cli.js stats [account-id]`

### `report`

Daily send report: how many emails were sent and how many failed.
Defaults to today. Use `--date` to specify a date, or `--days` for a multi-day range.

`node cli.js report [account-id] [--date YYYY-MM-DD] [--days <number>]`

- No flags: today's report
- `--date 2026-03-31`: report for a specific date
- `--days 7`: report for the last 7 days (broken down by day)

Output includes: total / sent / failed counts, success rate, and recent failure details (recipient, subject, error message).
