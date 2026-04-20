const { getDb } = require('./db');

/**
 * Check if an email should be filtered out.
 * Returns { filtered: boolean, reason: string|null }
 */
function shouldFilter(accountId, email) {
  const db = getDb();
  const rules = db.prepare(`
    SELECT * FROM filter_rules
    WHERE is_global = 1 OR account_id = ?
  `).all(accountId);

  const fromAddr = (email.from_addr || '').toLowerCase();
  const fromName = (email.from_name || '').toLowerCase();
  const subject = (email.subject || '').toLowerCase();

  for (const rule of rules) {
    const pattern = rule.pattern.toLowerCase();
    let target = '';

    switch (rule.field) {
      case 'from':
        target = fromAddr + ' ' + fromName;
        break;
      case 'subject':
        target = subject;
        break;
      case 'to':
        target = (email.to_addr || '').toLowerCase();
        break;
      case 'body':
        target = (email.body_text || '').toLowerCase() + ' ' + (email.body_html || '').toLowerCase();
        break;
      case 'body_regex':
        target = (email.body_text || '') + ' ' + (email.body_html || '');
        break;
      default:
        target = fromAddr;
    }

    if (rule.field === 'body_regex') {
      try {
        const re = new RegExp(rule.pattern);
        if (re.test(target)) {
          return {
            filtered: true,
            reason: `Rule: body matches regex /${rule.pattern}/`
          };
        }
      } catch (e) {
        // invalid regex, skip
      }
    } else if (target.includes(pattern)) {
      return {
        filtered: true,
        reason: `Rule: ${rule.field} contains "${rule.pattern}"`
      };
    }
  }

  return { filtered: false, reason: null };
}

function addRule(accountId, field, pattern, action = 'filter') {
  const db = getDb();
  db.prepare(`
    INSERT INTO filter_rules (account_id, field, pattern, action, is_global)
    VALUES (?, ?, ?, ?, ?)
  `).run(accountId, field, pattern, action, accountId ? 0 : 1);
}

function listRules(accountId) {
  const db = getDb();
  return db.prepare(`
    SELECT * FROM filter_rules
    WHERE is_global = 1 OR account_id = ?
  `).all(accountId || '');
}

function removeRule(ruleId) {
  const db = getDb();
  db.prepare('DELETE FROM filter_rules WHERE id = ?').run(ruleId);
}

module.exports = { shouldFilter, addRule, listRules, removeRule };
