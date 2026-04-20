const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');

const DATA_DIR = path.join(__dirname, '..', 'data');
fs.mkdirSync(DATA_DIR, { recursive: true });

let _db = null;

function getDb() {
  if (_db) return _db;
  _db = new Database(path.join(DATA_DIR, 'emails.db'));
  _db.pragma('journal_mode = WAL');
  _db.pragma('foreign_keys = ON');
  initSchema(_db);
  return _db;
}

function initSchema(db) {
  db.exec(`
    CREATE TABLE IF NOT EXISTS accounts (
      id TEXT PRIMARY KEY,
      email TEXT NOT NULL UNIQUE,
      imap_host TEXT NOT NULL DEFAULT 'imap.gmail.com',
      imap_port INTEGER NOT NULL DEFAULT 993,
      smtp_host TEXT NOT NULL DEFAULT 'smtp.gmail.com',
      smtp_port INTEGER NOT NULL DEFAULT 465,
      username TEXT NOT NULL,
      app_password TEXT NOT NULL,
      active INTEGER NOT NULL DEFAULT 1,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS emails (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      account_id TEXT NOT NULL REFERENCES accounts(id),
      message_id TEXT,
      uid INTEGER,
      folder TEXT NOT NULL DEFAULT 'INBOX',
      from_addr TEXT,
      from_name TEXT,
      to_addr TEXT,
      subject TEXT,
      date TEXT,
      body_text TEXT,
      body_html TEXT,
      snippet TEXT,
      is_read INTEGER NOT NULL DEFAULT 0,
      is_starred INTEGER NOT NULL DEFAULT 0,
      is_filtered INTEGER NOT NULL DEFAULT 0,
      filter_reason TEXT,
      raw_headers TEXT,
      created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE UNIQUE INDEX IF NOT EXISTS idx_emails_account_uid_folder
      ON emails(account_id, uid, folder);
    CREATE INDEX IF NOT EXISTS idx_emails_account_date
      ON emails(account_id, date DESC);
    CREATE INDEX IF NOT EXISTS idx_emails_from
      ON emails(from_addr);
    CREATE INDEX IF NOT EXISTS idx_emails_filtered
      ON emails(is_filtered);

    CREATE TABLE IF NOT EXISTS filter_rules (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      account_id TEXT REFERENCES accounts(id),
      field TEXT NOT NULL DEFAULT 'from',
      pattern TEXT NOT NULL,
      action TEXT NOT NULL DEFAULT 'filter',
      is_global INTEGER NOT NULL DEFAULT 0,
      created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS sent_emails (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      account_id TEXT NOT NULL REFERENCES accounts(id),
      to_addr TEXT NOT NULL,
      cc TEXT,
      bcc TEXT,
      subject TEXT,
      body_text TEXT,
      body_html TEXT,
      in_reply_to TEXT,
      sent_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS sync_state (
      account_id TEXT NOT NULL,
      folder TEXT NOT NULL DEFAULT 'INBOX',
      last_uid INTEGER NOT NULL DEFAULT 0,
      last_sync TEXT,
      PRIMARY KEY (account_id, folder)
    );
  `);

  // Migrations: add columns introduced after initial schema
  const migrations = [
    'ALTER TABLE accounts ADD COLUMN smtp_ok INTEGER DEFAULT NULL',
    'ALTER TABLE accounts ADD COLUMN smtp_checked_at TEXT DEFAULT NULL',
    'ALTER TABLE emails ADD COLUMN cc TEXT DEFAULT NULL',
    "ALTER TABLE sent_emails ADD COLUMN status TEXT NOT NULL DEFAULT 'sent'",
    'ALTER TABLE sent_emails ADD COLUMN error TEXT DEFAULT NULL',
  ];
  for (const sql of migrations) {
    try { db.exec(sql); } catch (_) { /* column already exists */ }
  }

  // Seed default global filter rules
  const existing = db.prepare('SELECT COUNT(*) as cnt FROM filter_rules WHERE is_global = 1').get();
  if (existing.cnt === 0) {
    const insert = db.prepare('INSERT INTO filter_rules (field, pattern, action, is_global) VALUES (?, ?, ?, 1)');
    insert.run('from', 'noreply', 'filter');
    insert.run('from', 'no-reply', 'filter');
  }
}

module.exports = { getDb };
