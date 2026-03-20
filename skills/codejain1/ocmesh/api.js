/**
 * api.js
 * HTTP API server on localhost:7432
 * Your OpenClaw agent hits this to query peers and send messages.
 */

const express = require('express');
const db = require('./db');
const { send } = require('./messaging');
const { PEER_TTL } = require('./relays');

const app = express();
app.use(express.json());

const PORT = 7432;

// ─── Status ───────────────────────────────────────────────────────────────────

app.get('/status', (req, res) => {
  const identity = db.prepare('SELECT pk FROM identity LIMIT 1').get();
  const totalPeers = db.prepare('SELECT COUNT(*) as c FROM peers').get().c;
  const onlinePeers = db.prepare(
    'SELECT COUNT(*) as c FROM peers WHERE last_seen > ?'
  ).get(Date.now() - PEER_TTL).c;
  const unread = db.prepare(
    'SELECT COUNT(*) as c FROM messages WHERE read = 0'
  ).get().c;

  res.json({
    ok: true,
    publicKey: identity?.pk ?? null,
    peers: { total: totalPeers, online: onlinePeers },
    messages: { unread },
    uptime: Math.floor(process.uptime()),
  });
});

// ─── Peers ────────────────────────────────────────────────────────────────────

app.get('/peers', (req, res) => {
  const { online } = req.query;
  let peers;

  if (online === 'true') {
    peers = db.prepare(
      'SELECT * FROM peers WHERE last_seen > ? ORDER BY last_seen DESC'
    ).all(Date.now() - PEER_TTL);
  } else {
    peers = db.prepare('SELECT * FROM peers ORDER BY last_seen DESC').all();
  }

  res.json({ peers: peers.map(formatPeer) });
});

app.get('/peers/:pk', (req, res) => {
  const peer = db.prepare('SELECT * FROM peers WHERE pk = ?').get(req.params.pk);
  if (!peer) return res.status(404).json({ error: 'peer not found' });
  res.json(formatPeer(peer));
});

// ─── Messages ─────────────────────────────────────────────────────────────────

app.get('/messages', (req, res) => {
  const { unread, from } = req.query;
  let query = 'SELECT * FROM messages';
  const params = [];

  if (unread === 'true') {
    query += ' WHERE read = 0';
  } else if (from) {
    query += ' WHERE from_pk = ?';
    params.push(from);
  }

  query += ' ORDER BY received_at DESC LIMIT 50';
  const messages = db.prepare(query).all(...params);
  res.json({ messages });
});

app.post('/messages/read', (req, res) => {
  const { id } = req.body;
  if (id) {
    db.prepare('UPDATE messages SET read = 1 WHERE id = ?').run(id);
  } else {
    db.prepare('UPDATE messages SET read = 1').run();
  }
  res.json({ ok: true });
});

// ─── Send ─────────────────────────────────────────────────────────────────────

app.post('/send', async (req, res) => {
  const { to, content } = req.body;
  if (!to || !content) {
    return res.status(400).json({ error: 'to and content required' });
  }

  try {
    const id = await send(to, content);
    res.json({ ok: true, id });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ─── Identity ─────────────────────────────────────────────────────────────────

app.get('/identity', (req, res) => {
  const identity = db.prepare('SELECT pk FROM identity LIMIT 1').get();
  res.json({ publicKey: identity?.pk ?? null });
});

// ─── Helpers ──────────────────────────────────────────────────────────────────

function formatPeer(p) {
  const online = p.last_seen > Date.now() - PEER_TTL;
  return {
    pk: p.pk,
    online,
    handshaked: p.handshake === 1,
    firstSeen: p.first_seen,
    lastSeen: p.last_seen,
    meta: p.meta ? JSON.parse(p.meta) : {},
  };
}

function start() {
  app.listen(PORT, '127.0.0.1', () => {
    console.log(`[api] HTTP API running on http://127.0.0.1:${PORT}`);
  });
}

module.exports = { start };
