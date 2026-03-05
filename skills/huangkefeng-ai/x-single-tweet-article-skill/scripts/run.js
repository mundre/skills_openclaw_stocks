#!/usr/bin/env node
const { spawnSync } = require('child_process');

const args = process.argv.slice(2);
const getArg = (name) => {
  const i = args.indexOf(`--${name}`);
  return i >= 0 ? args[i + 1] : undefined;
};

const url = getArg('url');
const article = getArg('article');
const userId = getArg('user') || 'anonymous';

if ((!url && !article) || (url && article)) {
  console.error('Usage: node scripts/run.js --url <x-status-url> OR --article <x-article-url> --user <user-id>');
  process.exit(1);
}

const BILLING_URL = process.env.SKILLPAY_BILLING_URL || 'https://skillpay.me/api/v1/billing';
const API_KEY = process.env.SKILL_BILLING_API_KEY || 'sk_74e1969ebc92fcf58257470c50f8bb76e36c9da0d201aa69861e28c62f5bd48e';
const SKILL_ID = process.env.SKILL_ID || '7674002a-818d-45f7-811b-c0e0145101e4';
const PRICE = Number(process.env.SKILLPAY_PRICE_TOKEN || '1');
const FETCHER = process.env.X_TWEET_FETCHER_PATH || '/home/kkk/.openclaw/workspace-web3/x-tweet-fetcher/scripts/fetch_tweet.py';

async function getPaymentLink(amount = 7) {
  const r = await fetch(`${BILLING_URL}/payment-link`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'x-api-key': API_KEY },
    body: JSON.stringify({ user_id: userId, amount }),
  }).catch(() => null);
  if (!r) return null;
  const d = await r.json().catch(() => ({}));
  return d.payment_url || null;
}

async function charge() {
  const r = await fetch(`${BILLING_URL}/charge`, {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'x-api-key': API_KEY },
    body: JSON.stringify({ user_id: userId, skill_id: SKILL_ID, amount: PRICE }),
  }).catch(() => null);
  if (!r) return { ok: false, reason: 'network_error' };
  const d = await r.json().catch(() => ({}));
  if (d.success) return { ok: true, data: d };
  const payment = await getPaymentLink(7);
  if (payment) d.payment_url = payment;
  return { ok: false, reason: 'insufficient_balance', data: d };
}

(async () => {
  const c = await charge();
  if (!c.ok) {
    if (c?.data?.payment_url) {
      console.error(`PAYMENT_URL:${c.data.payment_url}`);
      console.error('PAYMENT_INFO:Insufficient balance. Top up and retry.');
    }
    console.error(JSON.stringify({ ok: false, stage: 'billing', chargeResult: c, topup_min_usdt: 7 }, null, 2));
    process.exit(2);
  }

  const pyArgs = [FETCHER];
  if (url) pyArgs.push('--url', url);
  if (article) pyArgs.push('--article', article);
  pyArgs.push('--pretty');

  const res = spawnSync('python3', pyArgs, { encoding: 'utf8' });
  if (res.status !== 0) {
    console.error(JSON.stringify({ ok: false, stage: 'fetch', stderr: res.stderr || '', stdout: res.stdout || '' }, null, 2));
    process.exit(3);
  }

  const out = (res.stdout || '').trim();
  try {
    const data = JSON.parse(out);
    console.log(JSON.stringify({ ok: true, charged: true, mode: url ? 'tweet' : 'article', data }, null, 2));
  } catch {
    console.log(JSON.stringify({ ok: true, charged: true, mode: url ? 'tweet' : 'article', raw: out }, null, 2));
  }
})();
