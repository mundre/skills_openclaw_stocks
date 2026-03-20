/**
 * presence.js
 * Announces this agent's presence to Nostr relays
 * and discovers other ocmesh agents.
 * Uses nostr-tools v1 API (finishEvent / signEvent).
 */

const { finishEvent } = require('nostr-tools');
const { publish, subscribe } = require('./nostr');
const { PRESENCE_KIND, ANNOUNCE_INTERVAL, DISCOVERY_INTERVAL, PEER_TTL } = require('./relays');
const db = require('./db');

let identity = null;

function start(id) {
  identity = id;
  announce();
  discover();

  setInterval(announce, ANNOUNCE_INTERVAL);
  setInterval(discover, DISCOVERY_INTERVAL);
}

function announce() {
  const now = Math.floor(Date.now() / 1000);

  const event = finishEvent({
    kind: PRESENCE_KIND,
    created_at: now,
    tags: [
      ['d', 'ocmesh-presence'],
      ['app', 'ocmesh'],
      ['v', '0.1.0'],
    ],
    content: 'ocmesh-agent-online',
  }, identity.sk);

  publish(event);
  console.log('[presence] Announced online');
}

function discover() {
  const since = Math.floor((Date.now() - PEER_TTL) / 1000);

  subscribe({
    kinds: [PRESENCE_KIND],
    since,
  });

  console.log('[presence] Discovery scan started');
}

function handlePresenceEvent(event) {
  if (!event || !event.pubkey) return;
  if (identity && event.pubkey === identity.pk) return;

  const isOcmesh = event.tags && event.tags.some(
    ([k, v]) => k === 'app' && v === 'ocmesh'
  );
  if (!isOcmesh) return;

  const now = Date.now();
  const existing = db.prepare('SELECT pk FROM peers WHERE pk = ?').get(event.pubkey);

  if (existing) {
    db.prepare('UPDATE peers SET last_seen = ? WHERE pk = ?')
      .run(now, event.pubkey);
  } else {
    const version = getTag(event, 'v');
    db.prepare(`
      INSERT INTO peers (pk, first_seen, last_seen, handshake, meta)
      VALUES (?, ?, ?, 0, ?)
    `).run(event.pubkey, now, now, JSON.stringify({ version }));

    console.log(`[presence] New peer discovered: ${event.pubkey.slice(0, 16)}...`);
  }
}

function getTag(event, name) {
  const tag = event.tags && event.tags.find(([k]) => k === name);
  return tag ? tag[1] : null;
}

module.exports = { start, handlePresenceEvent };
