/**
 * messaging.js
 * Encrypted agent-to-agent messaging via Nostr NIP-04 DMs.
 * Uses nostr-tools v1 API.
 */

const { finishEvent, nip04 } = require('nostr-tools');
const { publish, subscribe } = require('./nostr');
const { DM_KIND } = require('./relays');
const db = require('./db');

let identity = null;

function start(id) {
  identity = id;

  // Subscribe to DMs addressed to us
  subscribe({
    kinds: [DM_KIND],
    '#p': [identity.pk],
    since: Math.floor(Date.now() / 1000) - 60,
  });

  console.log('[messaging] Listening for encrypted DMs');
}

async function send(toPk, content) {
  const encrypted = await nip04.encrypt(identity.sk, toPk, content);
  const now = Math.floor(Date.now() / 1000);

  const event = finishEvent({
    kind: DM_KIND,
    created_at: now,
    tags: [['p', toPk]],
    content: encrypted,
  }, identity.sk);

  publish(event);
  console.log(`[messaging] Sent DM to ${toPk.slice(0, 16)}...`);

  return event.id;
}

async function handleDmEvent(event) {
  if (!event || !identity) return;
  if (event.pubkey === identity.pk) return;

  const toPk = event.tags && event.tags.find(([k]) => k === 'p')?.[1];
  if (toPk !== identity.pk) return;

  try {
    const decrypted = await nip04.decrypt(identity.sk, event.pubkey, event.content);

    const existing = db.prepare('SELECT id FROM messages WHERE id = ?').get(event.id);
    if (existing) return;

    db.prepare(`
      INSERT INTO messages (id, from_pk, to_pk, content, received_at, read)
      VALUES (?, ?, ?, ?, ?, 0)
    `).run(event.id, event.pubkey, identity.pk, decrypted, Date.now());

    console.log(`[messaging] New message from ${event.pubkey.slice(0, 16)}...`);

    // Auto-add peer if not known
    const peer = db.prepare('SELECT pk FROM peers WHERE pk = ?').get(event.pubkey);
    if (!peer) {
      const now = Date.now();
      db.prepare(`
        INSERT INTO peers (pk, first_seen, last_seen, handshake, meta)
        VALUES (?, ?, ?, 1, ?)
      `).run(event.pubkey, now, now, JSON.stringify({ via: 'dm' }));
    } else {
      db.prepare('UPDATE peers SET last_seen = ?, handshake = 1 WHERE pk = ?')
        .run(Date.now(), event.pubkey);
    }

  } catch (err) {
    console.error('[messaging] Failed to decrypt DM:', err.message);
  }
}

module.exports = { start, send, handleDmEvent };
