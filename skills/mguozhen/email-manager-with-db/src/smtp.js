const nodemailer = require('nodemailer');
const { getDb } = require('./db');
const unsubscribe = require('./unsubscribe');

/**
 * Create SMTP transporter for account
 */
function createTransporter(account) {
  return nodemailer.createTransport({
    host: account.smtp_host,
    port: account.smtp_port,
    secure: account.smtp_port === 465,
    auth: {
      user: account.username,
      pass: account.app_password
    }
  });
}

/**
 * Send an email.
 *
 * Automatically:
 *   - Checks suppression list (blocks resend to unsubscribed recipients)
 *   - Injects RFC 2369 + RFC 8058 List-Unsubscribe headers
 *
 * Options:
 *   skipSuppressionCheck  Set true to bypass suppression check (e.g. transactional replies)
 *   skipUnsubHeader       Set true to omit List-Unsubscribe (e.g. 1:1 human conversations)
 *   extraHeaders          Additional headers to merge
 */
async function sendEmail(accountId, {
  to, cc, bcc, subject, text, html, inReplyTo, references,
  skipSuppressionCheck = false,
  skipUnsubHeader = false,
  extraHeaders = {},
}) {
  const db = getDb();
  const account = db.prepare('SELECT * FROM accounts WHERE id = ?').get(accountId);
  if (!account) throw new Error(`Account ${accountId} not found`);

  // Suppression check
  if (!skipSuppressionCheck && to) {
    const suppressReason = unsubscribe.isSuppressed(to);
    if (suppressReason) {
      db.prepare(`
        INSERT INTO sent_emails (account_id, to_addr, cc, bcc, subject, body_text, body_html, in_reply_to, status, error)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'suppressed', ?)
      `).run(accountId, to, cc || null, bcc || null, subject, text || null, html || null, inReplyTo || null, `suppressed: ${suppressReason}`);
      const err = new Error(`Recipient ${to} is on suppression list (${suppressReason})`);
      err.code = 'SUPPRESSED';
      err.suppressReason = suppressReason;
      throw err;
    }
  }

  // Build headers
  const headers = { ...extraHeaders };
  if (!skipUnsubHeader && to) {
    const unsubHeaders = unsubscribe.buildHeaders(to);
    if (unsubHeaders) Object.assign(headers, unsubHeaders);
  }

  const transporter = createTransporter(account);

  const mailOptions = {
    from: `${account.email}`,
    to,
    cc: cc || undefined,
    bcc: bcc || undefined,
    subject,
    text: text || undefined,
    html: html || undefined,
    inReplyTo: inReplyTo || undefined,
    references: references || undefined,
    headers: Object.keys(headers).length ? headers : undefined,
  };

  let info;
  try {
    info = await transporter.sendMail(mailOptions);
  } catch (err) {
    db.prepare(`
      INSERT INTO sent_emails (account_id, to_addr, cc, bcc, subject, body_text, body_html, in_reply_to, status, error)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'failed', ?)
    `).run(accountId, to, cc || null, bcc || null, subject, text || null, html || null, inReplyTo || null, err.message);
    throw err;
  }

  // Log to DB
  db.prepare(`
    INSERT INTO sent_emails (account_id, to_addr, cc, bcc, subject, body_text, body_html, in_reply_to, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'sent')
  `).run(accountId, to, cc || null, bcc || null, subject, text || null, html || null, inReplyTo || null);

  return { messageId: info.messageId, accepted: info.accepted };
}

/**
 * Test SMTP connection
 */
async function testSmtp(account) {
  const transporter = createTransporter(account);
  try {
    await transporter.verify();
    return { ok: true };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

module.exports = { sendEmail, testSmtp, unsubscribe };
