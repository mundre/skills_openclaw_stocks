const { ImapFlow } = require('imapflow');
const { simpleParser } = require('mailparser');
const { getDb } = require('./db');
const { shouldFilter } = require('./filters');
const { htmlToMarkdown } = require('./html-to-text');
const { testSmtp } = require('./smtp');

/**
 * Create an IMAP client for the given account config
 */
function createClient(account) {
  return new ImapFlow({
    host: account.imap_host,
    port: account.imap_port,
    secure: true,
    auth: {
      user: account.username,
      pass: account.app_password
    },
    socketTimeout: 30000, // 30-second timeout for the socket
    logger: false
  });
}

/**
 * Fetch new emails since last synced UID
 */
async function syncInbox(accountId, folder = 'INBOX', limit = 50, refilterAll = false) {
  const db = getDb();
  const account = db.prepare('SELECT * FROM accounts WHERE id = ?').get(accountId);
  if (!account) throw new Error(`Account ${accountId} not found`);

  const syncState = db.prepare(
    'SELECT * FROM sync_state WHERE account_id = ? AND folder = ?'
  ).get(accountId, folder);

  const lastUid = syncState ? syncState.last_uid : 0;

  const client = createClient(account);
  const results = { fetched: 0, filtered: 0, errors: [] };

  try {
    await client.connect();
    const lock = await client.getMailboxLock(folder);

    try {
      // Fetch messages newer than last known UID
      const range = lastUid > 0 ? `${lastUid + 1}:*` : `1:*`;
      let count = 0;
      let maxUid = lastUid;

      const insertEmail = db.prepare(`
        INSERT OR IGNORE INTO emails
          (account_id, message_id, uid, folder, from_addr, from_name, to_addr, cc,
           subject, date, body_text, body_html, snippet, is_read, is_filtered, filter_reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `);

      for await (const message of client.fetch(range, {
        uid: true,
        envelope: true,
        source: true,
        flags: true
      })) {
        if (count >= limit) break;

        try {
          const parsed = await simpleParser(message.source);
          const fromAddr = parsed.from?.value?.[0]?.address || '';
          const fromName = parsed.from?.value?.[0]?.name || '';
          const toAddr = parsed.to?.value?.map(v => v.address).join(', ') || '';
          const ccAddr = parsed.cc?.value?.map(v => v.address).join(', ') || '';
          const bodyHtml = parsed.html || '';
          const bodyText = bodyHtml
            ? htmlToMarkdown(bodyHtml, parsed.attachments)
            : (parsed.text || '');
          const snippet = bodyText.substring(0, 200).replace(/\n/g, ' ').trim();
          const isRead = message.flags?.has('\\Seen') ? 1 : 0;

          const emailData = {
            from_addr: fromAddr,
            from_name: fromName,
            to_addr: toAddr,
            cc: ccAddr,
            subject: parsed.subject || '(no subject)',
            body_text: bodyText,
            body_html: bodyHtml
          };

          const filterResult = shouldFilter(accountId, emailData);

          insertEmail.run(
            accountId,
            parsed.messageId || null,
            message.uid,
            folder,
            fromAddr,
            fromName,
            toAddr,
            ccAddr,
            parsed.subject || '(no subject)',
            parsed.date ? parsed.date.toISOString() : null,
            bodyText,
            bodyHtml,
            snippet,
            isRead,
            filterResult.filtered ? 1 : 0,
            filterResult.reason
          );

          if (message.uid > maxUid) maxUid = message.uid;
          count++;
          results.fetched++;
          if (filterResult.filtered) results.filtered++;
        } catch (parseErr) {
          results.errors.push(`UID ${message.uid}: ${parseErr.message}`);
        }
      }

      // Update sync state
      if (maxUid > lastUid) {
        db.prepare(`
          INSERT INTO sync_state (account_id, folder, last_uid, last_sync)
          VALUES (?, ?, ?, datetime('now'))
          ON CONFLICT(account_id, folder)
          DO UPDATE SET last_uid = ?, last_sync = datetime('now')
        `).run(accountId, folder, maxUid, maxUid);
      }
    } finally {
      lock.release();
    }
  } finally {
    await client.logout().catch(() => {});
  }
  
  // -- SMTP VERIFICATION --
  const smtpResult = await testSmtp(account);
  db.prepare(`
    UPDATE accounts SET smtp_ok = ?, smtp_checked_at = datetime('now') WHERE id = ?
  `).run(smtpResult.ok ? 1 : 0, accountId);
  results.smtp = smtpResult;

  // -- RE-FILTERING STEP --
  if (refilterAll) {
    const allUnfiltered = db.prepare('SELECT * FROM emails WHERE account_id = ? AND is_filtered = 0').all(accountId);
    const updateStmt = db.prepare('UPDATE emails SET is_filtered = 1, filter_reason = ? WHERE id = ?');
    let refilteredCount = 0;
    
    for (const email of allUnfiltered) {
        const filterResult = shouldFilter(accountId, email);
        if (filterResult.filtered) {
            updateStmt.run(filterResult.reason, email.id);
            refilteredCount++;
        }
    }
    if (refilteredCount > 0) {
        results.refiltered = refilteredCount;
    }
  }


  return results;
}

/**
 * List mailbox folders
 */
async function listFolders(accountId) {
  const db = getDb();
  const account = db.prepare('SELECT * FROM accounts WHERE id = ?').get(accountId);
  if (!account) throw new Error(`Account ${accountId} not found`);

  const client = createClient(account);
  try {
    await client.connect();
    const folders = await client.list();
    return folders.map(f => ({ name: f.name, path: f.path, flags: [...(f.flags || [])] }));
  } finally {
    await client.logout().catch(() => {});
  }
}

/**
 * Test IMAP connection
 */
async function testConnection(account) {
  const client = createClient(account);
  try {
    await client.connect();
    const status = await client.status('INBOX', { messages: true, unseen: true });
    await client.logout();
    return { ok: true, messages: status.messages, unseen: status.unseen };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

async function moveMessage(accountId, uid, fromFolder, toFolder) {
  const db = getDb();
  const account = db.prepare('SELECT * FROM accounts WHERE id = ?').get(accountId);
  if (!account) throw new Error(`Account ${accountId} not found`);

  const client = createClient(account);
  try {
    await client.connect();
    const lock = await client.getMailboxLock(fromFolder);
    try {
      await client.messageMove(uid.toString(), toFolder, { uid: true });
      return { ok: true, moved: uid };
    } finally {
      lock.release();
    }
  } catch (err) {
    return { ok: false, error: err.message };
  } finally {
    await client.logout().catch(() => {});
  }
}

module.exports = { syncInbox, listFolders, testConnection, moveMessage };
