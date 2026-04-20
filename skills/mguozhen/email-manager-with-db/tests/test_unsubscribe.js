#!/usr/bin/env node
/**
 * End-to-end regression test for List-Unsubscribe flow.
 * Tests: token generation, header building, HMAC verification, suppression check.
 */

const path = require('path');
const assert = require('assert');
const crypto = require('crypto');
const http = require('http');

// Use test-isolated DB + secret
const TEST_DB = '/tmp/test_tracking_unsub.db';
process.env.TRACKING_DB_PATH = TEST_DB;
process.env.UNSUB_SECRET = 'test-secret-xyz';
process.env.UNSUB_BASE_URL = 'http://localhost:7788';
process.env.UNSUB_MAILTO_DOMAIN = 'test.example.com';

try { require('fs').unlinkSync(TEST_DB); } catch {}

const unsub = require(path.resolve(__dirname, '../src/unsubscribe.js'));

let passed = 0, failed = 0;
function test(name, fn) {
  try { fn(); console.log(`  ✓ ${name}`); passed++; }
  catch (e) { console.log(`  ✗ ${name}\n    ${e.message}`); failed++; }
}

console.log('\n=== Token generation & verification ===');
test('makeToken returns deterministic 16-char hex', () => {
  const t = unsub.makeToken('alice@example.com');
  assert.strictEqual(t.length, 16);
  assert.match(t, /^[0-9a-f]+$/);
  assert.strictEqual(unsub.makeToken('alice@example.com'), t);
});

test('makeToken is case-insensitive + trims', () => {
  assert.strictEqual(
    unsub.makeToken('ALICE@example.com'),
    unsub.makeToken('  alice@example.com  ')
  );
});

test('different emails produce different tokens', () => {
  assert.notStrictEqual(
    unsub.makeToken('alice@example.com'),
    unsub.makeToken('bob@example.com')
  );
});

test('verifyToken accepts valid token', () => {
  const t = unsub.makeToken('charlie@example.com');
  assert.strictEqual(unsub.verifyToken('charlie@example.com', t), true);
});

test('verifyToken rejects invalid token', () => {
  assert.strictEqual(unsub.verifyToken('charlie@example.com', 'deadbeefdeadbeef'), false);
});

test('verifyToken rejects cross-email token', () => {
  const t = unsub.makeToken('alice@example.com');
  assert.strictEqual(unsub.verifyToken('bob@example.com', t), false);
});

console.log('\n=== Header building ===');
test('buildHeaders includes HTTPS + mailto + One-Click', () => {
  const h = unsub.buildHeaders('user@test.com');
  assert.ok(h, 'headers should be non-null');
  assert.match(h['List-Unsubscribe'], /^<http/);
  assert.match(h['List-Unsubscribe'], /<mailto:/);
  assert.strictEqual(h['List-Unsubscribe-Post'], 'List-Unsubscribe=One-Click');
  assert.strictEqual(h['Precedence'], 'bulk');
});

test('HTTPS link contains URL-encoded email', () => {
  const h = unsub.buildHeaders('user+tag@test.com');
  assert.ok(h['List-Unsubscribe'].includes('user%2Btag%40test.com'));
});

test('mailto link includes HMAC token', () => {
  const h = unsub.buildHeaders('user@test.com');
  const token = unsub.makeToken('user@test.com');
  assert.ok(h['List-Unsubscribe'].includes(`unsubscribe+${token}@test.example.com`));
});

console.log('\n=== Suppression list ===');
test('isSuppressed returns null for unknown email', () => {
  assert.strictEqual(unsub.isSuppressed('never-suppressed@test.com'), null);
});

test('suppress + isSuppressed round-trip', () => {
  unsub.suppress('blocked@test.com', 'unsubscribe', 'test');
  assert.strictEqual(unsub.isSuppressed('blocked@test.com'), 'unsubscribe');
});

test('suppress is case-insensitive', () => {
  unsub.suppress('UpperCase@Test.Com');
  assert.strictEqual(unsub.isSuppressed('uppercase@test.com'), 'unsubscribe');
});

test('unsuppress removes entry', () => {
  unsub.suppress('temp@test.com');
  assert.ok(unsub.unsuppress('temp@test.com'));
  assert.strictEqual(unsub.isSuppressed('temp@test.com'), null);
});

test('listSuppressions returns array', () => {
  const list = unsub.listSuppressions(10);
  assert.ok(Array.isArray(list));
  assert.ok(list.length > 0);
});

// Skip live HTTP tests in CI/default runs — requires the Python tracker running.
// Run with SKIP_LIVE=1 to skip; SKIP_LIVE=0 or unset to attempt.
if (process.env.SKIP_LIVE === '1') {
  console.log(`\n${passed} passed, ${failed} failed (live HTTP tests skipped)`);
  process.exit(failed === 0 ? 0 : 1);
}

console.log('\n=== Live HTTP endpoints (tracker must be running on :7788) ===');

function httpGet(url) {
  return new Promise((resolve, reject) => {
    http.get(url, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => resolve({ status: res.statusCode, body: data }));
    }).on('error', reject);
  });
}

function httpPost(url, body) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const req = http.request({
      hostname: u.hostname, port: u.port, path: u.pathname + u.search, method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': Buffer.byteLength(body) },
    }, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => resolve({ status: res.statusCode, body: data }));
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

(async () => {
  // The tracker uses its own UNSUB_SECRET env - need to check what it has
  // For live test, we generate token using tracker's secret (default)
  const email = 'livetest@example.com';
  // Re-derive token using tracker's default secret
  const trackerSecret = 'solvea-default-secret-change-me';
  const token = crypto.createHmac('sha256', trackerSecret).update(email.toLowerCase()).digest('hex').slice(0, 16);

  test('GET /unsubscribe with invalid token → 400', async () => {
    const r = await httpGet('http://localhost:7788/unsubscribe?e=bad@test.com&t=deadbeefdeadbeef');
    assert.strictEqual(r.status, 400);
  });

  try {
    const r1 = await httpGet(`http://localhost:7788/unsubscribe?e=${encodeURIComponent(email)}&t=${token}`);
    if (r1.status === 200 && r1.body.includes('unsubscribed')) {
      console.log('  ✓ GET /unsubscribe with valid token → 200 + HTML');
      passed++;
    } else {
      console.log(`  ✗ GET /unsubscribe with valid token → status ${r1.status}`);
      failed++;
    }
  } catch (e) { console.log(`  ✗ GET /unsubscribe: ${e.message}`); failed++; }

  try {
    const email2 = 'oneclick@example.com';
    const token2 = crypto.createHmac('sha256', trackerSecret).update(email2.toLowerCase()).digest('hex').slice(0, 16);
    const r2 = await httpPost(
      'http://localhost:7788/unsubscribe',
      `e=${encodeURIComponent(email2)}&t=${token2}&List-Unsubscribe=One-Click`
    );
    if (r2.status === 200 && r2.body.trim() === 'unsubscribed') {
      console.log('  ✓ POST /unsubscribe (RFC 8058 one-click) → 200 unsubscribed');
      passed++;
    } else {
      console.log(`  ✗ POST /unsubscribe: ${r2.status} ${r2.body}`);
      failed++;
    }
  } catch (e) { console.log(`  ✗ POST /unsubscribe: ${e.message}`); failed++; }

  try {
    const r3 = await httpPost(
      'http://localhost:7788/unsubscribe',
      'e=bad@test.com&t=wrongtoken1234'
    );
    if (r3.status === 400) {
      console.log('  ✓ POST /unsubscribe with bad token → 400');
      passed++;
    } else {
      console.log(`  ✗ POST /unsubscribe bad token: ${r3.status}`);
      failed++;
    }
  } catch (e) { console.log(`  ✗ POST /unsubscribe bad: ${e.message}`); failed++; }

  console.log(`\n${passed} passed, ${failed} failed`);
  process.exit(failed === 0 ? 0 : 1);
})();
