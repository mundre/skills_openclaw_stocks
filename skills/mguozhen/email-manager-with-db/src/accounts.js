const { getDb } = require('./db');
const crypto = require('crypto');

function generateId(email) {
  // e.g. liya@solvea.cx → liya-solvea
  const [user, domain] = email.split('@');
  const domainBase = domain.split('.')[0];
  return `${user}-${domainBase}`;
}

function addAccount({
  email,
  appPassword,
  imapHost = 'imap.gmail.com',
  imapPort = 993,
  smtpHost = 'smtp.gmail.com',
  smtpPort = 465,
  username = null
}) {
  const db = getDb();
  const id = generateId(email);
  const user = username || email;

  db.prepare(`
    INSERT INTO accounts (id, email, imap_host, imap_port, smtp_host, smtp_port, username, app_password)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(email) DO UPDATE SET
      imap_host = ?, imap_port = ?, smtp_host = ?, smtp_port = ?,
      username = ?, app_password = ?, updated_at = datetime('now')
  `).run(id, email, imapHost, imapPort, smtpHost, smtpPort, user, appPassword,
         imapHost, imapPort, smtpHost, smtpPort, user, appPassword);

  return { id, email };
}

function getAccount(idOrEmail) {
  const db = getDb();
  return db.prepare('SELECT * FROM accounts WHERE id = ? OR email = ?').get(idOrEmail, idOrEmail);
}

function listAccounts() {
  const db = getDb();
  return db.prepare('SELECT id, email, imap_host, smtp_host, active, created_at FROM accounts').all();
}

function removeAccount(idOrEmail) {
  const db = getDb();
  const account = getAccount(idOrEmail);
  if (!account) throw new Error(`Account not found: ${idOrEmail}`);
  db.prepare('DELETE FROM accounts WHERE id = ?').run(account.id);
  return { removed: account.id };
}

module.exports = { addAccount, getAccount, listAccounts, removeAccount };
