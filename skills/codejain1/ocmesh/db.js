/**
 * db.js
 * SQLite database using Node.js built-in node:sqlite (available from Node 22.5+).
 * Stores identity, peers, and messages.
 */

const { DatabaseSync } = require('node:sqlite');
const path = require('path');
const os = require('os');
const fs = require('fs');

const DATA_DIR = path.join(os.homedir(), '.ocmesh');
fs.mkdirSync(DATA_DIR, { recursive: true });

const db = new DatabaseSync(path.join(DATA_DIR, 'ocmesh.db'));

db.exec(`
  CREATE TABLE IF NOT EXISTS identity (
    sk TEXT NOT NULL,
    pk TEXT NOT NULL
  );

  CREATE TABLE IF NOT EXISTS peers (
    pk        TEXT PRIMARY KEY,
    first_seen INTEGER NOT NULL,
    last_seen  INTEGER NOT NULL,
    handshake  INTEGER DEFAULT 0,
    meta       TEXT
  );

  CREATE TABLE IF NOT EXISTS messages (
    id        TEXT PRIMARY KEY,
    from_pk   TEXT NOT NULL,
    to_pk     TEXT NOT NULL,
    content   TEXT NOT NULL,
    received_at INTEGER NOT NULL,
    read      INTEGER DEFAULT 0
  );
`);

module.exports = db;
