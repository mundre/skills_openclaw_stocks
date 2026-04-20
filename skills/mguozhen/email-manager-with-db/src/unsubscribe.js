/**
 * RFC 2369 + RFC 8058 List-Unsubscribe header generation.
 *
 * - Generates HMAC-signed token per recipient email (can't forge)
 * - Returns headers object to merge into nodemailer mailOptions
 * - Reads/writes suppression list in tracking.db (shared with Python tracker)
 *
 * Env vars:
 *   UNSUB_SECRET        HMAC secret (required, fallback "solvea-default-secret")
 *   UNSUB_BASE_URL      Public URL of tracking server (required, fallback reads .tracking_config)
 *   UNSUB_MAILTO_DOMAIN Domain for mailto: fallback (default "solvea.cx")
 *   TRACKING_DB_PATH    Path to tracking.db (default "/Users/guozhen/MailOutbound/tracking.db")
 */

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const Database = require('better-sqlite3');

const DEFAULT_TRACKING_DB = '/Users/guozhen/MailOutbound/tracking.db';
const DEFAULT_TRACKING_CFG = '/Users/guozhen/MailOutbound/.tracking_config';
const DEFAULT_SECRET = 'solvea-default-secret-change-me';
const DEFAULT_MAILTO_DOMAIN = 'solvea.cx';

let _db = null;
function getDb() {
  if (_db) return _db;
  const dbPath = process.env.TRACKING_DB_PATH || DEFAULT_TRACKING_DB;
  _db = new Database(dbPath);
  _db.exec(`
    CREATE TABLE IF NOT EXISTS suppressions (
      email TEXT PRIMARY KEY,
      reason TEXT NOT NULL DEFAULT 'unsubscribe',
      source TEXT,
      created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )
  `);
  _db.exec(`CREATE INDEX IF NOT EXISTS idx_suppressions_email ON suppressions(email)`);
  return _db;
}

function getBaseUrl() {
  if (process.env.UNSUB_BASE_URL) return process.env.UNSUB_BASE_URL;
  try {
    const cfg = fs.readFileSync(DEFAULT_TRACKING_CFG, 'utf8');
    const m = cfg.match(/^TRACKING_URL=(\S+)/m);
    if (m) return m[1];
  } catch {}
  return null;
}

function getSecret() {
  return process.env.UNSUB_SECRET || DEFAULT_SECRET;
}

function getMailtoDomain() {
  return process.env.UNSUB_MAILTO_DOMAIN || DEFAULT_MAILTO_DOMAIN;
}

/**
 * Generate HMAC-SHA256 token for recipient. First 16 hex chars = 64-bit security.
 */
function makeToken(email) {
  return crypto
    .createHmac('sha256', getSecret())
    .update(email.toLowerCase().trim())
    .digest('hex')
    .slice(0, 16);
}

function verifyToken(email, token) {
  const expected = makeToken(email);
  if (expected.length !== token.length) return false;
  return crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(token));
}

/**
 * Check if email is suppressed. Returns reason string or null.
 */
function isSuppressed(email) {
  const row = getDb()
    .prepare('SELECT reason FROM suppressions WHERE email = ? LIMIT 1')
    .get(email.toLowerCase().trim());
  return row ? row.reason : null;
}

/**
 * Record an unsubscribe in the suppression list.
 */
function suppress(email, reason = 'unsubscribe', source = 'api') {
  getDb()
    .prepare(
      `INSERT OR REPLACE INTO suppressions (email, reason, source, created_at)
       VALUES (?, ?, ?, datetime('now'))`
    )
    .run(email.toLowerCase().trim(), reason, source);
}

function unsuppress(email) {
  const info = getDb()
    .prepare('DELETE FROM suppressions WHERE email = ?')
    .run(email.toLowerCase().trim());
  return info.changes > 0;
}

function listSuppressions(limit = 100) {
  return getDb()
    .prepare('SELECT email, reason, source, created_at FROM suppressions ORDER BY created_at DESC LIMIT ?')
    .all(limit);
}

/**
 * Build RFC 2369 + RFC 8058 unsubscribe headers for a given recipient.
 * Returns null if no base URL configured (so caller can decide).
 */
function buildHeaders(toEmail) {
  const baseUrl = getBaseUrl();
  if (!baseUrl) return null;

  const token = makeToken(toEmail);
  const encoded = encodeURIComponent(toEmail);
  const httpsLink = `${baseUrl}/unsubscribe?e=${encoded}&t=${token}`;
  const mailtoLink = `unsubscribe+${token}@${getMailtoDomain()}`;

  return {
    'List-Unsubscribe': `<${httpsLink}>, <mailto:${mailtoLink}?subject=unsubscribe&body=${encoded}>`,
    'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click',
    'Precedence': 'bulk',
  };
}

module.exports = {
  makeToken,
  verifyToken,
  isSuppressed,
  suppress,
  unsuppress,
  listSuppressions,
  buildHeaders,
  getBaseUrl,
};
