/**
 * Kling AI HTTP client (zero external deps)
 * Uses Node.js 18+ built-in fetch
 */
import { getBearerToken, API_BASE, resolveApiBase } from './auth.mjs';

/**
 * 构建请求头（自动带鉴权）
 */
function makeHeaders(token) {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  };
}

/**
 * 解析可灵 API 响应，code 为 0 或 200 为成功
 */
function parseResponse(json) {
  if (json.code !== 0 && json.code !== 200) {
    throw new Error(`API error / API 错误 (code=${json.code}): ${json.message || 'Unknown error'}`);
  }
  return json.data;
}

/**
 * POST 请求可灵 API
 * @param {string} path  API 路径，如 /v1/videos/image2video
 * @param {object} body  请求体
 * @param {string} [token]  可选 token，不传则自动获取
 * @returns {Promise<object>} data 字段
 */
export async function klingPost(path, body, token) {
  if (!token) token = getBearerToken();
  const base = await resolveApiBase(token);
  const res = await fetch(`${base}${path}`, {
    method: 'POST',
    headers: makeHeaders(token),
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  return parseResponse(await res.json());
}

/**
 * GET 请求可灵 API
 * @param {string} path  API 路径，如 /v1/videos/image2video/{task_id}
 * @param {string} [token]  可选 token，不传则自动获取
 * @returns {Promise<object>} data 字段
 */
export async function klingGet(path, token) {
  if (!token) token = getBearerToken();
  const base = await resolveApiBase(token);
  const res = await fetch(`${base}${path}`, {
    method: 'GET',
    headers: { 'Authorization': `Bearer ${token}` },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  return parseResponse(await res.json());
}

export { getBearerToken, API_BASE, resolveApiBase };
