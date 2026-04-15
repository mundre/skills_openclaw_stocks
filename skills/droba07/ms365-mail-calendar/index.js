#!/usr/bin/env node
// ms365/index.js — Microsoft 365 Email & Calendar CLI
const { setAccount, getEmails, getUnreadEmails, readEmail, sendEmail, searchEmails, getEvents, createEvent, deleteEvent, getMe } = require('./src/api');
const { startDeviceFlow } = require('./src/auth');
const { normalizeAccount } = require('./src/config');

const args = process.argv.slice(2);
const flags = {};
const positional = [];

for (let i = 0; i < args.length; i++) {
  if (args[i].startsWith('--')) {
    const key = args[i].slice(2);
    flags[key] = args[i + 1] && !args[i + 1].startsWith('--') ? args[++i] : true;
  } else {
    positional.push(args[i]);
  }
}

const account = flags.account || process.env.MS365_ACCOUNT || 'default';
setAccount(account);

const cmd = positional[0] || 'help';

async function run() {
  switch (cmd) {
    case 'login':
      await startDeviceFlow(account);
      break;

    case 'whoami':
      const me = await getMe();
      console.log(`${me.displayName} <${me.mail || me.userPrincipalName}>`);
      break;

    case 'mail':
      const subcmd = positional[1] || 'inbox';
      if (subcmd === 'inbox') {
        const emails = await getEmails(parseInt(flags.top || '10'));
        for (const e of emails) {
          const read = e.isRead ? ' ' : '●';
          console.log(`${read} ${e.receivedDateTime?.slice(0, 16)}  ${e.from?.emailAddress?.name || e.from?.emailAddress?.address}  ${e.subject}`);
        }
      } else if (subcmd === 'unread') {
        const emails = await getUnreadEmails(parseInt(flags.top || '10'));
        for (const e of emails) {
          console.log(`● ${e.receivedDateTime?.slice(0, 16)}  ${e.from?.emailAddress?.name || e.from?.emailAddress?.address}  ${e.subject}`);
        }
      } else if (subcmd === 'read') {
        const email = await readEmail(positional[2]);
        console.log(`From: ${email.from?.emailAddress?.address}`);
        console.log(`To: ${email.toRecipients?.map(r => r.emailAddress?.address).join(', ')}`);
        console.log(`Subject: ${email.subject}`);
        console.log(`Date: ${email.receivedDateTime}`);
        console.log(`\n${email.body?.content}`);
      } else if (subcmd === 'send') {
        if (!flags.to || !flags.subject || !flags.body) {
          console.error('Usage: ms365 mail send --to addr --subject "..." --body "..."');
          process.exit(1);
        }
        await sendEmail(flags.to, flags.subject, flags.body, flags.cc);
        console.log('Email sent.');
      } else if (subcmd === 'search') {
        const results = await searchEmails(positional[2] || flags.query, parseInt(flags.top || '10'));
        for (const e of results) {
          console.log(`${e.receivedDateTime?.slice(0, 16)}  ${e.from?.emailAddress?.address}  ${e.subject}`);
        }
      }
      break;

    case 'calendar':
      const events = await getEvents(flags.from, flags.to);
      if (!events.length) { console.log('No events.'); break; }
      for (const e of events) {
        const start = e.start?.dateTime?.slice(0, 16);
        const end = e.end?.dateTime?.slice(0, 16);
        const loc = e.location?.displayName ? ` @ ${e.location.displayName}` : '';
        console.log(`${start} - ${end}  ${e.subject}${loc}`);
      }
      break;

    case 'calendar-create':
      if (!flags.subject || !flags.start || !flags.end) {
        console.error('Usage: ms365 calendar-create --subject "..." --start 2026-01-15T10:00 --end 2026-01-15T11:00 [--attendees a@b.com,c@d.com]');
        process.exit(1);
      }
      const attendees = flags.attendees ? flags.attendees.split(',') : [];
      const created = await createEvent(flags.subject, flags.start, flags.end, attendees, flags.body || '');
      console.log(`Event created: ${created.id}`);
      break;

    default:
      console.log(`ms365 — Microsoft 365 Email & Calendar CLI

Usage: node index.js [--account name] <command>

Commands:
  login                              Authenticate (device code flow)
  whoami                             Show current user
  mail inbox [--top N]               List recent emails
  mail unread [--top N]              List unread emails
  mail read <id>                     Read email by ID
  mail send --to --subject --body    Send email
  mail search <query> [--top N]      Search emails
  calendar [--from --to]             List events
  calendar-create --subject --start --end  Create event

Accounts:
  --account personal                 Use 'personal' account
  --account work                     Use 'work' account
  Each account has separate tokens.`);
  }
}

run().catch(e => { console.error(e.message); process.exit(1); });
