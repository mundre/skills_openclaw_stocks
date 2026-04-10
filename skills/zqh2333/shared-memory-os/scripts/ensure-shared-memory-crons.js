#!/usr/bin/env node
const { execSync } = require('child_process');

const ROOT = '/home/zqh2333/.openclaw/workspace';
const TZ = 'Asia/Shanghai';

const jobs = [
  {
    name: 'shared-memory-os daily maintenance',
    description: 'Daily shared-memory health check, learnings index rebuild, and light maintenance.',
    cron: '15 3 * * *',
    message: [
      `In ${ROOT}, run the Shared Memory OS daily light maintenance. Execute these commands with exec and stop on real errors:`,
      '1) node skills/shared-memory-os/scripts/init-shared-memory-os.js',
      '2) node skills/shared-memory-os/scripts/check-memory-health.js > reports/shared-memory/latest-health.json',
      '3) node skills/shared-memory-os/scripts/rebuild-learnings-index.js',
      '4) node skills/shared-memory-os/scripts/record-health-snapshot.js',
      'Then read and briefly summarize latest-health.json and whether INDEX.md was refreshed. Keep the reply concise.'
    ].join('\n'),
    timeoutSeconds: '300'
  },
  {
    name: 'shared-memory-os weekly review',
    description: 'Weekly shared-memory review for duplicates, promotions, dashboard, and audit artifacts.',
    cron: '30 3 * * 1',
    message: [
      `In ${ROOT}, run the Shared Memory OS weekly maintenance. Execute this command with exec:`,
      'node skills/shared-memory-os/scripts/run-shared-memory-maintenance.js',
      'After it completes, read reports/shared-memory/dashboard.md and reports/shared-memory/shared-memory-audit-report.md and provide a concise summary of health score, failed checks, duplicate groups, promotion candidates, and notable next actions.'
    ].join('\n'),
    timeoutSeconds: '600'
  },
  {
    name: 'shared-memory-os monthly deep maintenance',
    description: 'Monthly deep shared-memory cleanup and review of stale entries, merge suggestions, and upgrade candidates.',
    cron: '45 3 1 * *',
    message: [
      `In ${ROOT}, run the Shared Memory OS monthly deep maintenance by executing:`,
      'node skills/shared-memory-os/scripts/run-shared-memory-maintenance.js',
      'Then read these files if present and summarize the important findings only: reports/shared-memory/shared-memory-stale-durable-memory.json, reports/shared-memory/shared-memory-merge-suggestions.json, reports/shared-memory/shared-memory-skill-upgrade-candidates.json, reports/shared-memory/dashboard.md. Keep the report concise and action-oriented.'
    ].join('\n'),
    timeoutSeconds: '600'
  }
];

function sh(command) {
  return execSync(command, { cwd: ROOT, encoding: 'utf8', shell: '/bin/bash' }).trim();
}

function q(value) {
  return `'${String(value).replace(/'/g, `'"'"'`)}'`;
}

const listRaw = sh('openclaw cron list --json --timeout 10000');
const current = JSON.parse(listRaw).jobs || [];
const results = [];

for (const job of jobs) {
  const existing = current.find(x => x.name === job.name);
  const common = [
    '--name', q(job.name),
    '--description', q(job.description),
    '--cron', q(job.cron),
    '--tz', q(TZ),
    '--session', 'isolated',
    '--message', q(job.message),
    '--thinking', 'low',
    '--timeout-seconds', job.timeoutSeconds,
    '--tools', 'exec,read',
    '--no-deliver',
    '--failure-alert',
    '--failure-alert-after', '1',
    '--failure-alert-cooldown', '6h'
  ].join(' ');

  if (existing) {
    sh(`openclaw cron edit ${q(existing.id)} ${common} --enable --timeout 10000`);
    results.push({ action: 'updated', id: existing.id, name: job.name });
  } else {
    const added = JSON.parse(sh(`openclaw cron add --json ${common} --timeout 10000`));
    results.push({ action: 'created', id: added.id, name: job.name });
  }
}

console.log(JSON.stringify({ ok: true, timezone: TZ, results }, null, 2));
