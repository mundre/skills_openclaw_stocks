/**
 * index.js
 * ocmesh — Decentralized OpenClaw agent mesh
 *
 * Starts automatically, connects to Nostr relays, announces presence,
 * discovers peers, auto-handshakes, and exposes HTTP API on port 7432.
 */

const { loadOrCreateIdentity } = require('./identity');
const { connectAll } = require('./nostr');
const { start: startPresence, handlePresenceEvent } = require('./presence');
const { start: startMessaging, handleDmEvent } = require('./messaging');
const { start: startHandshake, handshakeNewPeer } = require('./handshake');
const { start: startApi } = require('./api');
const db = require('./db');
const { PEER_TTL } = require('./relays');

async function main() {
  console.log('╔══════════════════════════════╗');
  console.log('║       ocmesh v0.1.0          ║');
  console.log('║  OpenClaw Agent Mesh Node    ║');
  console.log('╚══════════════════════════════╝');

  // Load or create identity
  const identity = loadOrCreateIdentity();
  console.log(`[main] Identity: ${identity.pk.slice(0, 16)}...`);

  // Start subsystems
  startHandshake(identity);
  startMessaging(identity);

  // Connect to Nostr relays and handle all incoming events
  connectAll(async (event, relay) => {
    try {
      await handlePresenceEvent(event);
      await handleDmEvent(event);

      // Auto-handshake newly discovered peers
      if (event.kind === 31337) {
        const peer = db.prepare('SELECT handshake FROM peers WHERE pk = ?').get(event.pubkey);
        if (peer && peer.handshake === 0) {
          await handshakeNewPeer(event.pubkey);
        }
      }
    } catch (err) {
      console.error('[main] Event handler error:', err.message);
    }
  });

  // Give relays 2s to connect before announcing
  await sleep(2000);

  startPresence(identity);

  // Start HTTP API
  startApi();

  // Periodic cleanup — remove peers not seen in 2x TTL
  setInterval(() => {
    const cutoff = Date.now() - PEER_TTL * 2;
    const result = db.prepare('DELETE FROM peers WHERE last_seen < ?').run(cutoff);
    if (result.changes > 0) {
      console.log(`[main] Cleaned up ${result.changes} stale peers`);
    }
  }, 10 * 60 * 1000); // every 10 minutes

  console.log('[main] ocmesh is running. Press Ctrl+C to stop.');
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

main().catch((err) => {
  console.error('[main] Fatal error:', err);
  process.exit(1);
});
