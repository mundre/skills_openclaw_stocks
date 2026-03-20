/**
 * handshake.js
 * Auto-handshake logic.
 * When a new peer is discovered, automatically send them a hello DM.
 * This establishes a two-way connection and proves both agents are live.
 */

const db = require('./db');
const { send } = require('./messaging');

let identity = null;

function start(id) {
  identity = id;
}

async function handshakeNewPeer(pk) {
  const peer = db.prepare('SELECT handshake FROM peers WHERE pk = ?').get(pk);
  if (!peer || peer.handshake === 1) return; // already handshaked

  console.log(`[handshake] Initiating handshake with ${pk.slice(0, 16)}...`);

  const greeting = JSON.stringify({
    type: 'ocmesh-hello',
    version: '0.1.0',
    from: identity.pk,
    ts: Date.now(),
  });

  try {
    await send(pk, greeting);
    db.prepare('UPDATE peers SET handshake = 1 WHERE pk = ?').run(pk);
    console.log(`[handshake] Handshake complete with ${pk.slice(0, 16)}...`);
  } catch (err) {
    console.error(`[handshake] Failed:`, err.message);
  }
}

module.exports = { start, handshakeNewPeer };
