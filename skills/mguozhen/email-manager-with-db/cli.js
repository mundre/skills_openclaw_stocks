const { addAccount, listAccounts, removeAccount, getAccount } = require('./src/accounts');
const { syncInbox, listFolders, testConnection, moveMessage } = require('./src/imap');
const { sendEmail, testSmtp } = require('./src/smtp');
const { shouldFilter, addRule, listRules, removeRule } = require('./src/filters');
const { getDb } = require('./src/db');

const args = process.argv.slice(2);
const cmd = args[0];
const subcmd = args[1];

function getFlag(name, defaultVal = null) {
  const idx = args.indexOf(`--${name}`);
  if (idx === -1) return defaultVal;
  return args[idx + 1] || defaultVal;
}

function hasFlag(name) {
  return args.includes(`--${name}`);
}

function json(obj) {
  console.log(JSON.stringify(obj, null, 2));
}

async function main() {
  try {
    switch (cmd) {
      case 'account': {
        switch (subcmd) {
          case 'add': {
            const email = getFlag('email');
            const password = getFlag('password');
            const imapHost = getFlag('imap-host', 'imap.gmail.com');
            const imapPort = parseInt(getFlag('imap-port', '993'));
            const smtpHost = getFlag('smtp-host', 'smtp.gmail.com');
            const smtpPort = parseInt(getFlag('smtp-port', '465'));
            if (!email || !password) {
              console.error('Required: --email and --password');
              process.exit(1);
            }
            const result = addAccount({ email, appPassword: password, imapHost, imapPort, smtpHost, smtpPort });
            json({ ok: true, ...result });
            break;
          }
          case 'list': {
            json(listAccounts());
            break;
          }
          case 'remove': {
            const id = args[2];
            json(removeAccount(id));
            break;
          }
          default:
            console.error('account subcommands: add, list, remove');
        }
        break;
      }

      case 'test': {
        const accountId = args[1];
        const account = getAccount(accountId);
        console.log(account)
        if (!account) { console.error('Account not found'); process.exit(1); }

        console.log('Testing IMAP...');
        const imapResult = await testConnection(account);
        console.log('IMAP:', JSON.stringify(imapResult));

        console.log('Testing SMTP...');
        const smtpResult = await testSmtp(account);
        console.log('SMTP:', JSON.stringify(smtpResult));

        json({ imap: imapResult, smtp: smtpResult });
        break;
      }

      case 'sync': {
        const accountId = args[1];
        const folder = getFlag('folder', 'INBOX');
        const limit = parseInt(getFlag('limit', '50'));
        const refilterAll = hasFlag('refilter-all');
        const result = await syncInbox(accountId, folder, limit, refilterAll);
        json(result);
        break;
      }

      case 'inbox': {
        const accountId = args[1];
        const limit = parseInt(getFlag('limit', '20'));
        const unreadOnly = hasFlag('unread');
        const showFiltered = !hasFlag('no-filtered');
        const showTrash = !hasFlag('no-trash');
        const db = getDb();

        let query = 'SELECT id, uid, from_addr, from_name, subject, date, snippet, is_read, is_filtered, filter_reason FROM emails WHERE account_id = ?';
        const params = [accountId];

        if (unreadOnly) {
          query += ' AND is_read = 0';
        }
        if (!showFiltered) {
          query += ' AND is_filtered = 0';
        }
        if (!showTrash) {
          query += ` AND folder NOT LIKE '%Trash%' AND folder NOT LIKE '%Bin%'`;
        }

        query += ' ORDER BY date DESC LIMIT ?';
        params.push(limit);

        const emails = db.prepare(query).all(...params);
        json({ count: emails.length, emails });
        break;
      }
      
      case 'move': {
        const emailId = args[1];
        const destination = args[2];
        if (!emailId || !destination) {
          console.error('Usage: move <email-id> <destination-folder>');
          process.exit(1);
        }
        const db = getDb();
        const email = db.prepare('SELECT account_id, uid, folder FROM emails WHERE id = ?').get(emailId);
        if (!email) {
          console.error('Email not found');
          process.exit(1);
        }
        const result = await moveMessage(email.account_id, email.uid, email.folder, destination);
        if (result.ok) {
          // Also update the local db
          db.prepare('UPDATE emails SET folder = ? WHERE id = ?').run(destination, emailId);
          console.log(`Email ${emailId} moved to ${destination}`);
        }
        json(result);
        break;
      }
      
      case 'read': {
        const emailId = args[1];
        const db = getDb();
        const email = db.prepare('SELECT * FROM emails WHERE id = ?').get(emailId);
        if (!email) { console.error('Email not found'); process.exit(1); }
        // Don't dump huge HTML, prefer text
        if (email.body_html && email.body_html.length > 5000) {
          email.body_html = email.body_html.substring(0, 5000) + '... [truncated]';
        }
        json(email);
        break;
      }

      case 'send': {
        const accountId = args[1];
        const to = getFlag('to');
        const cc = getFlag('cc');
        const bcc = getFlag('bcc');
        const subject = getFlag('subject');
        const body = getFlag('body');
        const inReplyTo = getFlag('reply-to');
        if (!to || !subject) {
          console.error('Required: --to and --subject');
          process.exit(1);
        }
        const result = await sendEmail(accountId, { to, cc, bcc, subject, text: body, inReplyTo });
        json({ ok: true, ...result });
        break;
      }

      case 'search': {
        const accountId = args[1];
        const query = getFlag('query', '');
        const limit = parseInt(getFlag('limit', '20'));
        const db = getDb();

        const emails = db.prepare(`
          SELECT id, uid, from_addr, from_name, subject, date, snippet, is_read, is_filtered
          FROM emails
          WHERE account_id = ?
            AND (subject LIKE ? OR from_addr LIKE ? OR from_name LIKE ? OR body_text LIKE ?)
          ORDER BY date DESC
          LIMIT ?
        `).all(accountId, `%${query}%`, `%${query}%`, `%${query}%`, `%${query}%`, limit);

        json({ count: emails.length, emails });
        break;
      }

      case 'folders': {
        const accountId = args[1];
        const folders = await listFolders(accountId);
        json(folders);
        break;
      }

      case 'filter': {
        switch (subcmd) {
          case 'list': {
            const accountId = args[2] || null;
            json(listRules(accountId));
            break;
          }
          case 'add': {
            const field = getFlag('field', 'from');
            const pattern = getFlag('pattern');
            const accountId = getFlag('account-id');
            if (!pattern) { console.error('Required: --pattern'); process.exit(1); }
            addRule(accountId, field, pattern);
            json({ ok: true, field, pattern });
            break;
          }
          case 'remove': {
            removeRule(parseInt(args[2]));
            json({ ok: true });
            break;
          }
          default:
            console.error('filter subcommands: list, add, remove');
        }
        break;
      }

      case 'report': {
        // Daily send report: defaults to today, supports --date YYYY-MM-DD and --days N
        const db = getDb();
        const accountId = args[1] && !args[1].startsWith('--') ? args[1] : null;
        const dateFlag = getFlag('date');
        const daysBack = parseInt(getFlag('days', '1'));

        // Build date range
        let startDate, endDate;
        if (dateFlag) {
          startDate = dateFlag;
          endDate = dateFlag;
        } else if (daysBack > 1) {
          // Last N days
          const end = new Date();
          const start = new Date();
          start.setDate(start.getDate() - (daysBack - 1));
          startDate = start.toISOString().slice(0, 10);
          endDate = end.toISOString().slice(0, 10);
        } else {
          // Today
          startDate = new Date().toISOString().slice(0, 10);
          endDate = startDate;
        }

        const accountFilter = accountId ? 'AND account_id = ?' : '';
        const baseParams = accountId
          ? [startDate, endDate, accountId]
          : [startDate, endDate];

        const sent = db.prepare(`
          SELECT COUNT(*) as cnt FROM sent_emails
          WHERE date(sent_at) BETWEEN date(?) AND date(?)
            AND status = 'sent' ${accountFilter}
        `).get(...baseParams).cnt;

        const failed = db.prepare(`
          SELECT COUNT(*) as cnt FROM sent_emails
          WHERE date(sent_at) BETWEEN date(?) AND date(?)
            AND status = 'failed' ${accountFilter}
        `).get(...baseParams).cnt;

        const total = sent + failed;

        // Break down by day if range > 1
        let byDay = null;
        if (startDate !== endDate) {
          byDay = db.prepare(`
            SELECT date(sent_at) as day,
                   SUM(CASE WHEN status = 'sent' THEN 1 ELSE 0 END) as sent,
                   SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                   COUNT(*) as total
            FROM sent_emails
            WHERE date(sent_at) BETWEEN date(?) AND date(?)
              ${accountFilter}
            GROUP BY day ORDER BY day DESC
          `).all(...baseParams);
        }

        // Recent failures
        const failureParams = accountId
          ? [startDate, endDate, accountId, 5]
          : [startDate, endDate, 5];
        const recentFailures = db.prepare(`
          SELECT sent_at, to_addr, subject, error, account_id
          FROM sent_emails
          WHERE date(sent_at) BETWEEN date(?) AND date(?)
            AND status = 'failed' ${accountFilter}
          ORDER BY sent_at DESC LIMIT ?
        `).all(...failureParams);

        const report = {
          period: startDate === endDate ? startDate : `${startDate} ~ ${endDate}`,
          summary: { total, sent, failed, success_rate: total > 0 ? `${((sent / total) * 100).toFixed(1)}%` : 'N/A' },
          ...(byDay ? { by_day: byDay } : {}),
          ...(recentFailures.length > 0 ? { recent_failures: recentFailures } : {})
        };

        json(report);
        break;
      }

      case 'stats': {
        const accountId = args[1];
        const db = getDb();
        let where = '';
        const params = [];
        if (accountId) {
          where = 'WHERE account_id = ?';
          params.push(accountId);
        }
        const total = db.prepare(`SELECT COUNT(*) as cnt FROM emails ${where}`).get(...params).cnt;
        const unread = db.prepare(`SELECT COUNT(*) as cnt FROM emails ${where ? where + ' AND' : 'WHERE'} is_read = 0`).get(...params).cnt;
        const filtered = db.prepare(`SELECT COUNT(*) as cnt FROM emails ${where ? where + ' AND' : 'WHERE'} is_filtered = 1`).get(...params).cnt;
        const sent = db.prepare(`SELECT COUNT(*) as cnt FROM sent_emails ${where ? where.replace('account_id', 'account_id') : ''}`).get(...params).cnt;

        json({ total, unread, filtered, sent, accounts: listAccounts() });
        break;
      }

      default:
        console.log(`
Email Manager CLI

Commands:
  account add --email <email> --password <app-password>
  account list
  account remove <id>
  test <account-id>              Test IMAP + SMTP connection
  sync <account-id>              Fetch new emails from server
  inbox <account-id>             List emails (--limit, --unread, --no-filtered)
  read <email-id>                Read full email
  move <email-id> <folder>       Move email to folder
  send <account-id>              Send email (--to, --subject, --body)
  search <account-id>            Search emails (--query)
  folders <account-id>           List mailbox folders
  filter list [account-id]       Show filter rules
  filter add                     Add rule (--field, --pattern)
  filter remove <rule-id>        Remove a filter rule
  stats [account-id]             Show statistics
  report [account-id]            Daily send report (--date YYYY-MM-DD, --days N)
        `);
    }
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

main();
