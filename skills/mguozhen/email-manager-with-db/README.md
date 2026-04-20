<p align="center">
  <img src="https://cdn-icons-png.flaticon.com/512/732/732200.png" width="80" alt="Email Manager">
</p>

<h1 align="center">Email Manager with DB</h1>

<p align="center">
  <strong>Multi-account IMAP/SMTP email manager with local SQLite, RFC 8058 one-click unsubscribe, and suppression list — built for cold email outreach that doesn't get blacklisted.</strong>
</p>

<p align="center">
  <a href="#quick-start"><img src="https://img.shields.io/badge/setup-2min-brightgreen?style=flat-square" alt="2min Setup"></a>
  <a href="https://agentskills.io"><img src="https://img.shields.io/badge/Agent%20Skills-compatible-blue?style=flat-square" alt="Agent Skills"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="MIT License"></a>
  <a href="https://datatracker.ietf.org/doc/html/rfc8058"><img src="https://img.shields.io/badge/RFC%208058-compliant-purple?style=flat-square" alt="RFC 8058"></a>
  <img src="https://img.shields.io/badge/node-18+-339933?style=flat-square&logo=node.js&logoColor=white" alt="Node 18+">
</p>

<p align="center">
  <a href="#what-makes-this-different">Why</a> &bull;
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#commands">Commands</a> &bull;
  <a href="#unsubscribe-compliance">Unsubscribe</a> &bull;
  <a href="#architecture">Architecture</a>
</p>

---

## What makes this different

Most email libraries just wrap nodemailer. This one adds the stuff that keeps you out of spam folder:

- **Multi-account rotation** — switch between Gmail/Outlook/custom SMTP accounts to spread load
- **RFC 8058 One-Click Unsubscribe** — Hotmail and Gmail both require this for bulk mail; without it, your delivery tanks
- **HMAC-signed unsubscribe tokens** — recipients can't forge unsub requests for other emails
- **Automatic suppression list** — unsubscribed addresses are blocked from future sends (shared SQLite)
- **Local inbox sync** — IMAP pull into SQLite for fast search, filter, read
- **Filter rules** — gmail-style filters that auto-label/archive incoming mail
- **Daily send reports** — per-account stats for volume tracking and warmup monitoring

## Quick Start

```bash
# Clone into your Claude Code skills directory
git clone https://github.com/mguozhen/email-manager-with-db.git \
  ~/.claude/skills/email-manager-with-db

cd ~/.claude/skills/email-manager-with-db
npm install

# Add your first account (Gmail with App Password)
node cli.js account add \
  --email you@gmail.com \
  --password "xxxx xxxx xxxx xxxx" \
  --imap-host imap.gmail.com \
  --smtp-host smtp.gmail.com
```

That's it. Now you can send, receive, search, filter.

## Commands

### Accounts

```bash
node cli.js account add --email <email> --password <app-password>
node cli.js account list
node cli.js account remove <id>
node cli.js test <account-id>              # verify IMAP+SMTP work
```

### Sending

```bash
node cli.js send <account-id> \
  --to recipient@example.com \
  --subject "Hello" \
  --body "Plain text body"

# HTML body with automatic List-Unsubscribe headers
node cli.js send <account-id> \
  --to recipient@example.com \
  --subject "Campaign" \
  --html-file campaign.html
```

### Inbox

```bash
node cli.js sync <account-id>              # IMAP sync to local DB
node cli.js inbox <account-id> --unread    # list unread
node cli.js read <email-id>                # read email content
node cli.js search <query>                 # full-text search
```

### Suppression list (unsubscribe)

```bash
node cli.js unsub list                     # view all suppressed addresses
node cli.js unsub add <email>              # manually suppress
node cli.js unsub remove <email>           # remove from list
```

### Reports

```bash
node cli.js report <account-id>            # today's send stats
```

## Unsubscribe Compliance

This is the part most libraries skip.

### What it does

Every outbound email automatically gets these headers:

```
List-Unsubscribe: <https://track.yourdomain.com/unsubscribe?e=...&t=HMAC>, <mailto:unsubscribe+HMAC@yourdomain.com>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
Precedence: bulk
```

### Why dual HTTPS + mailto matters

- **Gmail / Yahoo** prefer the HTTPS link (one-click button in UI)
- **Hotmail / Outlook** require `mailto:` fallback — **without it, one-click button won't render and you go to spam**
- **RFC 8058** says mail clients should POST to the HTTPS URL; our server handles both GET (browser) and POST (one-click)

### HMAC tokens

```javascript
token = hmac_sha256(secret, email.toLowerCase()).slice(0, 16)
```

Recipients can't forge unsub requests for other emails. If someone tries `?e=competitor@corp.com&t=stolen_token`, the verification fails and returns 400.

### Suppression list enforcement

Once a recipient clicks unsubscribe:
1. Their email is added to `suppressions` table
2. Next time you call `sendEmail(to: unsubscribed@x.com)`, it throws `SUPPRESSED` error **before** hitting SMTP
3. No accidental re-sends, no compliance violations

### Bypass flags (for transactional mail)

```javascript
await sendEmail(accountId, {
  to: recipient,
  subject: 'Password reset',
  text: '...',
  skipUnsubHeader: true,        // Don't add List-Unsubscribe (1:1 transactional)
  skipSuppressionCheck: true,   // Send even if suppressed (account-critical)
});
```

## Configuration

### Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `UNSUB_SECRET` | Recommended | HMAC secret for unsub tokens. Generate: `openssl rand -hex 32` |
| `UNSUB_BASE_URL` | Yes (for headers) | Public URL of your tracking/unsub server |
| `UNSUB_MAILTO_DOMAIN` | Optional | Domain for `mailto:` fallback (default: `solvea.cx`) |
| `TRACKING_DB_PATH` | Optional | Path to shared suppression SQLite |
| `EMAIL_DB_PATH` | Optional | Path to main email DB (default: `emails.db` in cwd) |

### Unsubscribe server (Python)

You need to run an HTTP server that handles `GET/POST /unsubscribe`. A reference implementation that shares the same SQLite + HMAC secret:

```python
# Core logic (see examples/email_tracker.py for full server)
def _unsub_token(email):
    return hmac.new(
        UNSUB_SECRET.encode(),
        email.lower().strip().encode(),
        hashlib.sha256,
    ).hexdigest()[:16]

def _verify_unsub_token(email, token):
    return hmac.compare_digest(_unsub_token(email), token or "")

# GET /unsubscribe?e=<email>&t=<token>   → HTML confirmation page
# POST /unsubscribe  (RFC 8058 one-click) → 200 "unsubscribed"
```

## Architecture

```
email-manager-with-db/
├── SKILL.md                     # Claude Code / Agent Skills definition
├── cli.js                       # CLI entry point
├── src/
│   ├── accounts.js              # Account CRUD
│   ├── db.js                    # SQLite schema + init
│   ├── smtp.js                  # Send email (with auto unsub headers)
│   ├── imap.js                  # IMAP sync
│   ├── filters.js               # Gmail-style filter rules
│   ├── html-to-text.js          # Plain-text fallback from HTML
│   └── unsubscribe.js           # HMAC tokens, suppression list, header building
├── examples/
│   └── email_tracker.py         # Reference Python server for /unsubscribe
└── tests/
    └── test_unsubscribe.js      # 24 regression tests
```

### Data model

```sql
-- Main email DB
CREATE TABLE accounts (id, email, username, app_password, smtp_host, ...);
CREATE TABLE sent_emails (id, account_id, to_addr, subject, body, status, error, sent_at);
CREATE TABLE inbox_emails (id, account_id, from_addr, subject, body, unread, ...);
CREATE TABLE filters (id, account_id, rule, action, enabled);

-- Shared suppression DB (usually tracking.db)
CREATE TABLE suppressions (email PRIMARY KEY, reason, source, created_at);
```

## Running tests

```bash
node tests/test_unsubscribe.js
```

```
=== Token generation & verification ===
  ✓ makeToken returns deterministic 16-char hex
  ✓ makeToken is case-insensitive + trims
  ✓ different emails produce different tokens
  ✓ verifyToken accepts valid token
  ✓ verifyToken rejects invalid token
  ✓ verifyToken rejects cross-email token
=== Header building ===
  ✓ buildHeaders includes HTTPS + mailto + One-Click
  ✓ HTTPS link contains URL-encoded email
  ✓ mailto link includes HMAC token
=== Suppression list ===
  ✓ isSuppressed returns null for unknown email
  ✓ suppress + isSuppressed round-trip
  ✓ suppress is case-insensitive
  ✓ unsuppress removes entry
  ✓ listSuppressions returns array
=== sendEmail integration ===
  ✓ List-Unsubscribe header injected
  ✓ List-Unsubscribe-Post header present
  ✓ mailto: fallback in header (Hotmail compat)
  ✓ skipUnsubHeader bypasses injection
  ✓ Suppression blocks send with SUPPRESSED error code
  ✓ skipSuppressionCheck bypasses block

20 passed, 0 failed
```

## FAQ

<details>
<summary><strong>Why SQLite instead of Postgres?</strong></summary>

Listmonk's architecture inspired this — single binary, single file DB, no daemon to manage. For under 1M emails, SQLite with WAL mode is faster and operationally simpler than Postgres.
</details>

<details>
<summary><strong>Does this work with Gmail App Passwords?</strong></summary>

Yes. Enable 2FA on your Google account, generate an App Password at myaccount.google.com/apppasswords, and use that as the `password`. Standard Gmail SMTP: `smtp.gmail.com:587` or `smtp.gmail.com:465`.
</details>

<details>
<summary><strong>Can I use this without a public unsub server?</strong></summary>

The `List-Unsubscribe` header will be omitted if `UNSUB_BASE_URL` is not configured. You can still use the library, but your emails will look more like bulk/spam to ISPs. A Cloudflare tunnel (free) to localhost works fine for low volume.
</details>

<details>
<summary><strong>Is this replacement for Mailgun/SendGrid?</strong></summary>

For outbound, yes — if you have your own SMTP reputation (warmed Gmail accounts, custom domain with SPF/DKIM/DMARC). For transactional at scale, no — use a proper ESP. This tool is for cold outreach and small-batch campaigns.
</details>

## Contributing

PRs welcome. All changes must pass `node tests/test_unsubscribe.js`.

## License

[MIT](LICENSE)

---

<p align="center">
  Built for <a href="https://code.claude.com">Claude Code</a> &bull; Inspired by <a href="https://listmonk.app">listmonk</a> and <a href="https://www.rfc-editor.org/rfc/rfc8058.html">RFC 8058</a>
</p>
