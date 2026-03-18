/**
 * Kling AI CLI helpers (zero external deps)
 * Argument parsing, auth, media file reading
 */
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { getBearerToken, promptAndSaveCredentials } from './auth.mjs';

/**
 * 解析命令行参数
 * @param {string[]} argv  process.argv
 * @param {string[]} [booleanFlags]  额外的布尔标志名（不需要跟值的 --flag）
 * @returns {object} 参数键值对
 */
export function parseArgs(argv, booleanFlags = []) {
  const boolSet = new Set(['no-wait', 'download', 'wait', 'help', ...booleanFlags]);
  const args = {};
  for (let i = 2; i < argv.length; i++) {
    const key = argv[i];
    if (!key.startsWith('--')) continue;
    const name = key.slice(2);
    if (name === 'no-wait') { args.wait = false; continue; }
    if (boolSet.has(name)) { args[name] = true; continue; }
    const val = argv[i + 1];
    if (val !== undefined && !val.startsWith('--')) {
      args[name] = val; i++;
    } else {
      args[name] = true;
    }
  }
  return args;
}

/**
 * 获取 Bearer Token：环境变量/.env → 交互式输入 → 失败退出
 * @returns {Promise<string>} token
 */
export async function getTokenOrExit() {
  try {
    return getBearerToken();
  } catch {
    try {
      return await promptAndSaveCredentials();
    } catch (e) {
      console.error(`Auth error / 鉴权错误: ${e.message}`);
      console.error('Set / 设置: export KLING_TOKEN="your-token"');
      console.error('Or / 或: export KLING_API_KEY="accessKey|secretKey"');
      console.error('Get keys / 获取密钥: https://app.klingai.com/cn/dev/console/application');
      process.exit(1);
    }
  }
}

/**
 * 读取媒体文件：URL 直接返回，本地文件读为 base64
 * @param {string} pathOrUrl  文件路径或 URL
 * @returns {Promise<string>} URL 或 base64 字符串
 */
export async function readMediaAsValue(pathOrUrl) {
  if (!pathOrUrl) return undefined;
  const s = pathOrUrl.trim();
  if (s.startsWith('http://') || s.startsWith('https://')) return s;
  const buf = await readFile(resolve(s));
  return buf.toString('base64');
}
