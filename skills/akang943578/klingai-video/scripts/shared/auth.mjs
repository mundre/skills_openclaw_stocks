/**
 * Kling AI auth (zero external deps)
 * Supports env vars, .env file, and interactive prompt for credentials
 */
import { createHmac } from 'node:crypto';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, resolve, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createInterface } from 'node:readline';

const __dir = dirname(fileURLToPath(import.meta.url));

/**
 * 解析 .env 文件内容，写入 process.env（不覆盖已有变量）
 */
function parseEnvContent(content) {
  for (const line of content.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith('#')) continue;
    const eqIdx = trimmed.indexOf('=');
    if (eqIdx <= 0) continue;
    const key = trimmed.slice(0, eqIdx).trim();
    let val = trimmed.slice(eqIdx + 1).trim();
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    }
    if (!(key in process.env)) {
      process.env[key] = val;
    }
  }
}

/**
 * .env 搜索路径（按优先级）：
 *   CWD > 脚本相对路径（1~3 级父目录）> ~/.config/kling/
 */
function getEnvSearchPaths() {
  const seen = new Set();
  const paths = [];
  const add = (p) => {
    const abs = resolve(p);
    if (!seen.has(abs)) { seen.add(abs); paths.push(abs); }
  };
  add(join(process.cwd(), '.env'));
  for (let i = 1; i <= 3; i++) {
    add(join(__dir, ...Array(i).fill('..'), '.env'));
  }
  const home = process.env.HOME || process.env.USERPROFILE;
  if (home) {
    add(join(home, '.config', 'kling', '.env'));
  }
  return paths;
}

(function loadEnv() {
  for (const p of getEnvSearchPaths()) {
    try { parseEnvContent(readFileSync(p, 'utf-8')); } catch {}
  }
})();

/** 同步回退值（仅供 KLING_API_BASE 显式设置时使用，勿直接用于请求） */
const API_BASE = process.env.KLING_API_BASE || 'https://api-beijing.klingai.com';

/** 国内 + 国际两个候选节点，按优先级排列 */
const CANDIDATE_BASES = [
  'https://api-beijing.klingai.com',
  'https://api-singapore.klingai.com',
];

/** 状态文件路径：~/.config/kling/state.json */
function getStatePath() {
  const home = process.env.HOME || process.env.USERPROFILE;
  if (home) return join(home, '.config', 'kling', 'state.json');
  return resolve(__dir, '..', '.kling-state.json');
}

function readState() {
  try {
    const obj = JSON.parse(readFileSync(getStatePath(), 'utf-8'));
    if (typeof obj.api_base === 'string') return obj;
  } catch {}
  return null;
}

function writeState(apiBase) {
  const p = getStatePath();
  try {
    mkdirSync(dirname(p), { recursive: true });
    writeFileSync(
      p,
      JSON.stringify({ api_base: apiBase, updated_at: new Date().toISOString() }, null, 2) + '\n',
    );
  } catch {}
}

/**
 * 探测某个节点是否对当前 token 可用
 * 使用轻量只读接口，不消耗额度
 */
async function probeBase(base, token) {
  try {
    const res = await fetch(`${base}/v1/videos/text2video?pageNum=1&pageSize=1`, {
      method: 'GET',
      headers: { Authorization: `Bearer ${token}` },
      signal: AbortSignal.timeout(8000),
    });
    if (!res.ok) return false;
    const json = await res.json().catch(() => null);
    return json != null && (json.code === 0 || json.code === 200);
  } catch {
    return false;
  }
}

let _resolvedBase = null;

/**
 * 异步解析 API Base URL（进程内缓存，只检测一次）
 *
 * 优先级：
 *   1. KLING_API_BASE 环境变量（显式设置，直接使用）
 *   2. 状态文件 ~/.config/kling/state.json（上次成功的节点）
 *   3. 自动探测国内 + 国际节点，首个通过者写入状态文件
 *   4. 全部失败 → 打印错误并退出
 *
 * @param {string} token  Bearer Token（用于探测鉴权）
 */
export async function resolveApiBase(token) {
  if (_resolvedBase) return _resolvedBase;

  // 显式环境变量，无条件信任
  if (process.env.KLING_API_BASE) {
    _resolvedBase = process.env.KLING_API_BASE;
    return _resolvedBase;
  }

  // 读取状态文件（上次成功的节点）
  const state = readState();
  if (state) {
    _resolvedBase = state.api_base;
    return _resolvedBase;
  }

  // 首次运行，自动探测
  console.error('\n🔍 Probing API endpoints... / 正在检测 API 节点...');
  for (const base of CANDIDATE_BASES) {
    process.stderr.write(`   ${base} ... `);
    if (await probeBase(base, token)) {
      process.stderr.write('✓ OK\n\n');
      writeState(base);
      _resolvedBase = base;
      return _resolvedBase;
    }
    process.stderr.write('✗\n');
  }

  const statePath = getStatePath();
  console.error('\n❌ Cannot connect to any Kling API endpoint / 无法连接任何可灵 API 节点');
  for (const base of CANDIDATE_BASES) console.error(`   • ${base}`);
  console.error('\nPossible causes / 可能原因:');
  console.error('  1. Token invalid or expired / Token 无效或已过期:');
  console.error('     China / 国内: https://app.klingai.com/cn/dev/console/application');
  console.error('     Global / 国际: https://app.klingai.com/global/dev/console/application');
  console.error('  2. Network issue / 网络问题');
  console.error('\nSet KLING_TOKEN or KLING_API_KEY, remove cache, retry / 重置后重试:');
  console.error(`  rm "${statePath}"\n`);
  process.exit(1);
}

function base64url(buf) {
  return Buffer.from(buf).toString('base64')
    .replace(/=/g, '')
    .replace(/\+/g, '-')
    .replace(/\//g, '_');
}

function makeJwt(accessKey, secretKey) {
  const header = base64url(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const now = Math.floor(Date.now() / 1000);
  const payload = base64url(JSON.stringify({
    iss: accessKey,
    exp: now + 1800,
    nbf: now - 5,
  }));
  const signature = base64url(
    createHmac('sha256', secretKey).update(`${header}.${payload}`).digest()
  );
  return `${header}.${payload}.${signature}`;
}

/**
 * 获取 Bearer Token（同步，从环境变量 / .env 读取）
 * 优先 KLING_TOKEN，否则用 KLING_API_KEY 生成 JWT
 */
export function getBearerToken() {
  let token = (process.env.KLING_TOKEN || '').trim();
  if (token) {
    if (token.toLowerCase().startsWith('bearer ')) {
      token = token.slice(7).trim();
    }
    return token;
  }
  const apiKey = (process.env.KLING_API_KEY || '').trim();
  if (!apiKey) {
    throw new Error('Set KLING_TOKEN (recommended) or KLING_API_KEY (format: accessKey|secretKey) / 请设置 KLING_TOKEN 或 KLING_API_KEY');
  }
  const parts = apiKey.split('|');
  if (parts.length !== 2) {
    throw new Error('KLING_API_KEY format: accessKey|secretKey / KLING_API_KEY 格式错误');
  }
  return makeJwt(parts[0].trim(), parts[1].trim());
}

/**
 * 密钥持久化保存路径：~/.config/kling/.env，回退到脚本同级目录
 */
function getCredentialSavePath() {
  const home = process.env.HOME || process.env.USERPROFILE;
  if (home) return join(home, '.config', 'kling', '.env');
  return resolve(__dir, '..', '..', '..', '.env');
}

/**
 * 交互式询问密钥并保存（仅 TTY 环境可用）
 * @returns {Promise<string>} Bearer Token
 */
export async function promptAndSaveCredentials() {
  if (!process.stdin.isTTY) {
    throw new Error('Set KLING_TOKEN (recommended) or KLING_API_KEY (format: accessKey|secretKey) / 请设置 KLING_TOKEN 或 KLING_API_KEY');
  }

  const rl = createInterface({ input: process.stdin, output: process.stderr });
  const ask = (q) => new Promise((r) => rl.question(q, (a) => r(a.trim())));

  try {
    console.error('\n── Kling AI Credentials / 可灵 AI 密钥配置 ─────────────');
    console.error('No credentials found / 未检测到密钥，请输入:');
    console.error('  • Bearer Token');
    console.error('  • API Key (accessKey|secretKey)');
    console.error('Get keys / 获取密钥: https://app.klingai.com/cn/dev/console/application');
    console.error('──────────────────────────────────────────────────────\n');

    const input = await ask('Enter credentials / 请输入密钥: ');
    if (!input) throw new Error('No credentials provided / 未提供密钥');

    let envKey, envVal, token;
    if (input.includes('|')) {
      const parts = input.split('|');
      if (parts.length !== 2 || !parts[0].trim() || !parts[1].trim()) {
        throw new Error('API Key format: accessKey|secretKey / API Key 格式错误');
      }
      envKey = 'KLING_API_KEY';
      envVal = input;
      token = makeJwt(parts[0].trim(), parts[1].trim());
    } else {
      token = input.toLowerCase().startsWith('bearer ') ? input.slice(7).trim() : input;
      envKey = 'KLING_TOKEN';
      envVal = token;
    }

    process.env[envKey] = envVal;

    const savePath = getCredentialSavePath();
    try {
      mkdirSync(dirname(savePath), { recursive: true });
      let lines = [];
      try { lines = readFileSync(savePath, 'utf-8').split('\n'); } catch {}
      const prefix = `${envKey}=`;
      const idx = lines.findIndex((l) => l.startsWith(prefix));
      if (idx >= 0) {
        lines[idx] = `${envKey}=${envVal}`;
      } else {
        if (lines.length && lines[lines.length - 1] === '') lines.pop();
        lines.push(`${envKey}=${envVal}`);
      }
      writeFileSync(savePath, lines.join('\n').trimEnd() + '\n');
      console.error(`\n✓ Saved / 已保存: ${savePath}`);
      console.error('  Auto-loaded next time / 下次自动读取\n');
    } catch (err) {
      console.error(`\n⚠ Save failed / 保存失败 (${err.message})\n`);
    }

    return token;
  } finally {
    rl.close();
  }
}

export { API_BASE, CANDIDATE_BASES, getStatePath };
