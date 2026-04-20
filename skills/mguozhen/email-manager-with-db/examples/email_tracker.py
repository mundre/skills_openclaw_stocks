#!/usr/bin/env python3
"""
Solvea Email Tracking Server — open rate & click rate
Serves:
  GET  /sent?id=EMAIL_ID&to=ADDR&subject=S  → logs send event
  GET  /open?id=EMAIL_ID                    → 1x1 pixel, logs open event (with bot filter)
  GET  /click?id=EMAIL_ID&url=URL           → redirect + logs click event (with bot filter)
  GET  /stats                               → JSON stats (raw + bot-filtered)
  GET  /hot-leads                           → JSON list of leads that opened/clicked (real opens only)
  GET  /health                              → JSON health check

Reads real client IP from CF-Connecting-IP / X-Forwarded-For / X-Real-IP headers
(cloudflared tunnel terminates locally, so RemoteAddr is always 127.0.0.1).
"""

import sqlite3
import base64
import hashlib
import hmac
import os
import urllib.parse
import json
import re
import sys
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import date

DB_PATH = Path("/Users/guozhen/MailOutbound/tracking.db")
PORT = 7788

UNSUB_SECRET = os.environ.get("UNSUB_SECRET", "solvea-default-secret-change-me")


def _unsub_token(email: str) -> str:
    """Generate HMAC-SHA256 token for recipient email. 16 hex chars = 64-bit security."""
    return hmac.new(
        UNSUB_SECRET.encode(),
        email.lower().strip().encode(),
        hashlib.sha256,
    ).hexdigest()[:16]


def _verify_unsub_token(email: str, token: str) -> bool:
    return hmac.compare_digest(_unsub_token(email), token or "")

PIXEL = base64.b64decode(
    "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
)

TRUSTED_LOCAL_IPS = {"127.0.0.1", "::1", "localhost"}

BOT_UA_PATTERNS = re.compile(
    r"(googleimageproxy|ggpht|gmailimageproxy|"
    r"yahoomailproxy|bingpreview|"
    r"mimecast|proofpoint|barracuda|"
    r"microsoft|outlook|exchange|symantec|messagelabs|"
    r"forcepoint|trendmicro|sophos|"
    r"cloudmark|agari|abuse\.ch|urlscan|virustotal|"
    r"headlesschrome|phantomjs|puppeteer|playwright|"
    r"python-requests|curl|wget|go-http-client|java/|okhttp)",
    re.IGNORECASE,
)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sent (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_id TEXT NOT NULL,
            to_addr TEXT,
            subject TEXT,
            ts TEXT NOT NULL DEFAULT (datetime('now')),
            delivered_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS opens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_id TEXT NOT NULL,
            ts TEXT NOT NULL DEFAULT (datetime('now')),
            ip TEXT,
            user_agent TEXT,
            is_bot INTEGER NOT NULL DEFAULT 0,
            bot_reason TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_id TEXT NOT NULL,
            url TEXT,
            ts TEXT NOT NULL DEFAULT (datetime('now')),
            ip TEXT,
            user_agent TEXT,
            is_bot INTEGER NOT NULL DEFAULT 0,
            bot_reason TEXT
        )
    """)

    for ddl in [
        "ALTER TABLE sent ADD COLUMN delivered_at TEXT",
        "ALTER TABLE opens ADD COLUMN user_agent TEXT",
        "ALTER TABLE opens ADD COLUMN is_bot INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE opens ADD COLUMN bot_reason TEXT",
        "ALTER TABLE clicks ADD COLUMN user_agent TEXT",
        "ALTER TABLE clicks ADD COLUMN is_bot INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE clicks ADD COLUMN bot_reason TEXT",
    ]:
        try:
            conn.execute(ddl)
        except sqlite3.OperationalError:
            pass

    conn.execute("""
        CREATE TABLE IF NOT EXISTS suppressions (
            email TEXT PRIMARY KEY,
            reason TEXT NOT NULL DEFAULT 'unsubscribe',
            source TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_suppressions_email ON suppressions(email)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_opens_email ON opens(email_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_opens_bot ON opens(email_id, is_bot)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_clicks_email ON clicks(email_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_clicks_bot ON clicks(email_id, is_bot)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sent_ts ON sent(ts)")
    conn.commit()
    return conn


class TrackingHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        sys.stdout.write(
            f"[{datetime.utcnow().isoformat()}Z] "
            f"{self._real_ip()} "
            f"{self.command} {self.path} "
            f"ua=\"{(self.headers.get('User-Agent') or '-')[:80]}\"\n"
        )
        sys.stdout.flush()

    def _real_ip(self):
        remote = self.client_address[0] if self.client_address else "unknown"
        if remote not in TRUSTED_LOCAL_IPS:
            return remote
        cf = (self.headers.get("CF-Connecting-IP") or "").strip()
        if cf:
            return cf
        xff = (self.headers.get("X-Forwarded-For") or "").strip()
        if xff:
            return xff.split(",")[0].strip()
        xr = (self.headers.get("X-Real-IP") or "").strip()
        if xr:
            return xr
        return remote

    def _classify_bot(self, email_id, ua, conn, event_type="open"):
        if ua and BOT_UA_PATTERNS.search(ua):
            return "ua_blacklist"
        if not ua or not ua.strip():
            return "empty_ua"

        row = conn.execute(
            "SELECT COALESCE(delivered_at, ts) AS t FROM sent WHERE email_id = ? ORDER BY id DESC LIMIT 1",
            (email_id,),
        ).fetchone()
        if row and row[0]:
            try:
                sent_ts = datetime.fromisoformat(row[0].replace("Z", ""))
                if (datetime.utcnow() - sent_ts).total_seconds() < 60:
                    return "too_fast"
            except ValueError:
                pass

        recent = conn.execute(
            f"SELECT COUNT(*) FROM {'opens' if event_type=='open' else 'clicks'} "
            f"WHERE email_id = ? AND ts > datetime('now', '-2 seconds')",
            (email_id,),
        ).fetchone()[0]
        if recent > 0:
            return "rapid_replay"
        return None

    def do_HEAD(self):
        self.do_GET()

    def do_POST(self):
        """RFC 8058 One-Click Unsubscribe: Mail clients POST to List-Unsubscribe URL."""
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/unsubscribe":
            self.send_response(404)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"not found")
            return

        # Parse query string + body (one-click sends both)
        params = dict(urllib.parse.parse_qsl(parsed.query))
        try:
            length = int(self.headers.get("Content-Length") or 0)
            if length > 0:
                body = self.rfile.read(length).decode("utf-8", errors="ignore")
                params.update(dict(urllib.parse.parse_qsl(body)))
        except Exception:
            pass

        email = (params.get("e") or "").strip().lower()
        token = (params.get("t") or "").strip()

        if not email or not token or not _verify_unsub_token(email, token):
            self.send_response(400)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"invalid token")
            return

        with get_db() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO suppressions (email, reason, source, created_at) "
                "VALUES (?, 'unsubscribe', 'one-click', datetime('now'))",
                (email,),
            )
        print(f"[Unsub] One-click: {email}", flush=True)

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"unsubscribed")

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = dict(urllib.parse.parse_qsl(parsed.query))
        ip = self._real_ip()
        ua = self.headers.get("User-Agent", "") or ""

        if parsed.path == "/sent":
            email_id = params.get("id", "unknown")
            to_addr = params.get("to", "")
            subject = params.get("subject", "")
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO sent (email_id, to_addr, subject) VALUES (?, ?, ?)",
                    (email_id, to_addr, subject),
                )
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Cache-Control", "no-store, private, max-age=0")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(b"ok")

        elif parsed.path == "/delivered":
            email_id = params.get("id", "unknown")
            with get_db() as conn:
                conn.execute(
                    "UPDATE sent SET delivered_at = datetime('now') "
                    "WHERE email_id = ? AND delivered_at IS NULL",
                    (email_id,),
                )
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(b"ok")

        elif parsed.path == "/open":
            email_id = params.get("id", "unknown")
            with get_db() as conn:
                reason = self._classify_bot(email_id, ua, conn, event_type="open")
                conn.execute(
                    "INSERT INTO opens (email_id, ip, user_agent, is_bot, bot_reason) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (email_id, ip, ua, 1 if reason else 0, reason),
                )
            self.send_response(200)
            self.send_header("Content-Type", "image/gif")
            self.send_header("Cache-Control", "no-store, private, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(PIXEL)

        elif parsed.path == "/click":
            email_id = params.get("id", "unknown")
            url = params.get("url", "https://solvea.cx")
            with get_db() as conn:
                reason = self._classify_bot(email_id, ua, conn, event_type="click")
                conn.execute(
                    "INSERT INTO clicks (email_id, url, ip, user_agent, is_bot, bot_reason) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (email_id, url, ip, ua, 1 if reason else 0, reason),
                )
            self.send_response(302)
            self.send_header("Location", url)
            self.send_header("Cache-Control", "no-store, private, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.end_headers()

        elif parsed.path == "/hot-leads":
            with get_db() as conn:
                rows = conn.execute("""
                    SELECT s.to_addr, s.subject, s.email_id, s.ts AS sent_ts,
                           (SELECT COUNT(*) FROM opens o
                              WHERE o.email_id = s.email_id AND o.is_bot = 0) AS open_count,
                           (SELECT COUNT(*) FROM clicks c
                              WHERE c.email_id = s.email_id AND c.is_bot = 0) AS click_count
                    FROM sent s
                    WHERE s.to_addr IS NOT NULL AND s.to_addr != ''
                      AND (EXISTS (SELECT 1 FROM opens o
                                    WHERE o.email_id = s.email_id AND o.is_bot = 0)
                        OR EXISTS (SELECT 1 FROM clicks c
                                    WHERE c.email_id = s.email_id AND c.is_bot = 0))
                    ORDER BY click_count DESC, open_count DESC
                """).fetchall()
            leads = [
                {"to": r[0], "subject": r[1], "tracking_id": r[2], "sent_at": r[3],
                 "opens": r[4], "clicks": r[5]}
                for r in rows
            ]
            body = json.dumps(leads).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        elif parsed.path == "/stats":
            today_iso = date.today().isoformat()
            with get_db() as conn:
                total_sent = conn.execute(
                    "SELECT COUNT(DISTINCT email_id) FROM sent"
                ).fetchone()[0]
                today_sent = conn.execute(
                    "SELECT COUNT(DISTINCT email_id) FROM sent WHERE ts LIKE ?",
                    (f"{today_iso}%",),
                ).fetchone()[0]

                total_opens_raw = conn.execute(
                    "SELECT COUNT(DISTINCT email_id) FROM opens"
                ).fetchone()[0]
                total_opens_real = conn.execute(
                    "SELECT COUNT(DISTINCT email_id) FROM opens WHERE is_bot = 0"
                ).fetchone()[0]
                today_opens_real = conn.execute(
                    "SELECT COUNT(DISTINCT email_id) FROM opens "
                    "WHERE is_bot = 0 AND ts LIKE ?",
                    (f"{today_iso}%",),
                ).fetchone()[0]

                total_clicks_raw = conn.execute(
                    "SELECT COUNT(DISTINCT email_id) FROM clicks"
                ).fetchone()[0]
                total_clicks_real = conn.execute(
                    "SELECT COUNT(DISTINCT email_id) FROM clicks WHERE is_bot = 0"
                ).fetchone()[0]
                today_clicks_real = conn.execute(
                    "SELECT COUNT(DISTINCT email_id) FROM clicks "
                    "WHERE is_bot = 0 AND ts LIKE ?",
                    (f"{today_iso}%",),
                ).fetchone()[0]

                bot_reasons = {
                    r[0]: r[1]
                    for r in conn.execute(
                        "SELECT bot_reason, COUNT(*) FROM opens "
                        "WHERE is_bot = 1 GROUP BY bot_reason"
                    ).fetchall()
                }

            stats = {
                "today": today_iso,
                "sent": {"today": today_sent, "total": total_sent},
                "opens": {
                    "today_real": today_opens_real,
                    "total_real": total_opens_real,
                    "total_raw": total_opens_raw,
                    "bot_filtered": total_opens_raw - total_opens_real,
                },
                "clicks": {
                    "today_real": today_clicks_real,
                    "total_real": total_clicks_real,
                    "total_raw": total_clicks_raw,
                    "bot_filtered": total_clicks_raw - total_clicks_real,
                },
                "bot_reasons": bot_reasons,
                "rates": {
                    "open_rate_raw": f"{total_opens_raw/total_sent*100:.1f}%" if total_sent else "N/A",
                    "open_rate_real": f"{total_opens_real/total_sent*100:.1f}%" if total_sent else "N/A",
                    "click_rate_real": f"{total_clicks_real/total_sent*100:.1f}%" if total_sent else "N/A",
                },
            }
            body = json.dumps(stats, indent=2).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        elif parsed.path == "/unsubscribe":
            email = (params.get("e") or "").strip().lower()
            token = (params.get("t") or "").strip()
            if not email or not token or not _verify_unsub_token(email, token):
                self.send_response(400)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                if self.command != "HEAD":
                    self.wfile.write(b"<h1>Invalid unsubscribe link</h1><p>This link is invalid or has been tampered with.</p>")
                return

            with get_db() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO suppressions (email, reason, source, created_at) "
                    "VALUES (?, 'unsubscribe', 'browser', datetime('now'))",
                    (email,),
                )
            print(f"[Unsub] Browser: {email}", flush=True)

            html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Unsubscribed</title>
<style>body{{font-family:-apple-system,sans-serif;max-width:500px;margin:80px auto;padding:0 20px;color:#333}}
h1{{color:#0a7d3b}}.email{{background:#f5f5f5;padding:8px 12px;border-radius:4px;display:inline-block;font-family:monospace}}</style>
</head><body>
<h1>You have been unsubscribed</h1>
<p>The email address <span class="email">{email}</span> has been removed from our mailing list.</p>
<p>You will no longer receive marketing emails from us. We are sorry to see you go.</p>
<p style="color:#888;font-size:13px;margin-top:40px">If this was a mistake, contact us at support@solvea.cx to resubscribe.</p>
</body></html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(html.encode())

        elif parsed.path == "/health":
            body = json.dumps({"ok": True, "ts": datetime.utcnow().isoformat()}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(b"not found")


def run():
    server = HTTPServer(("0.0.0.0", PORT), TrackingHandler)
    print(f"Tracking server on :{PORT}")
    print(f"DB: {DB_PATH}")
    server.serve_forever()


if __name__ == "__main__":
    run()
