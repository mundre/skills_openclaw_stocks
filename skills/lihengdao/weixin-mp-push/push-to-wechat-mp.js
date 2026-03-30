#!/usr/bin/env node
/**
 * 推送到公众号。config.json 和此脚本应在同一目录；支持HTML和图片模式，HTML 模式时 HTML 应该放在同目录。
 *
 * HTML：
 *   node push-to-wechat-mp.js html <HTML 文件名> [sendMode]
 * 示例：node push-to-wechat-mp.js html 你的文件.html draft
 * sendMode 缺省为 draft；亦可选 send、masssend。
 *
 * 图片（第二参为 JSON 数组整段字符串，shell 下请用单引号包住）：
 *   node push-to-wechat-mp.js img <JSON数组> <title> <content> [sendMode]
 * 示例：node push-to-wechat-mp.js img '["https://example.com/a.png"]' "标题" "正文" draft
 * sendMode 同上。
 */

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');

const DEFAULT_API = 'https://api.pcloud.ac.cn/openClawService';
const DIR = __dirname;

function readJson(name) {
  const p = path.join(DIR, name);
  if (!fs.existsSync(p)) throw new Error('缺少: ' + p);
  return JSON.parse(fs.readFileSync(p, 'utf8').trim());
}

function titleFromHtml(html) {
  // 先尝试 <title>
  const titleMatch = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
  if (titleMatch) {
    const raw = titleMatch[1].replace(/<[^>]+>/g, '').trim();
    if (raw) return raw;
  }

  // 回退到 <h1>、<h2> ... <h6>
  const hMatch = html.match(/<h[1-6][^>]*>([\s\S]*?)<\/h[1-6]>/i);
  if (hMatch) {
    const raw = hMatch[1].replace(/<[^>]+>/g, '').trim();
    if (raw) return raw;
  }

  return '未命名';
}

function parseImgUrlsArg(arg) {
  let trimmed = String(arg || '').trim();
  if (!trimmed) throw new Error('图片模式需要第二参：图片链接的 JSON 数组字符串');

  // 首先尝试直接解析为JSON
  let arr;
  let originalError = null;

  try {
    arr = JSON.parse(trimmed);
    // 如果成功且是数组，直接返回
    if (Array.isArray(arr) && arr.length > 0) {
      const urls = arr.map((u) => String(u).trim()).filter(Boolean);
      if (urls.length > 0) return urls;
    }
  } catch (e) {
    originalError = e;
  }

  // 如果直接解析失败，尝试兼容处理
  // 兼容 PowerShell 单引号传参导致外层方括号丢失的情况
  if (!trimmed.startsWith('[')) {
    trimmed = '[' + trimmed;
  }
  if (!trimmed.endsWith(']')) {
    trimmed = trimmed + ']';
  }

  // 兼容 PowerShell 单引号传参导致内部双引号丢失的情况
  if (!trimmed.includes('"')) {
    // 移除外层方括号，获取内容
    let content = trimmed.slice(1, -1);

    // 更稳健的方法：按逗号分割，但智能合并包含URL的片段
    const parts = content.split(',');
    const urls = [];
    let currentUrl = '';

    for (let i = 0; i < parts.length; i++) {
      const part = parts[i].trim();
      if (part.startsWith('http://') || part.startsWith('https://')) {
        // 如果currentUrl不为空，说明这是一个新的URL开始
        if (currentUrl) {
          urls.push(currentUrl.trim());
        }
        currentUrl = part;
      } else if (currentUrl) {
        // 如果不是http开头但有currentUrl，可能是URL的后续部分
        currentUrl += ',' + part;
      }
    }

    // 添加最后一个URL
    if (currentUrl) {
      urls.push(currentUrl.trim());
    }

    // 为每个URL添加双引号
    const quotedUrls = urls.map(url => `"${url}"`);
    trimmed = `[${quotedUrls.join(',')}]`;
  }

  // 再次尝试解析
  try {
    arr = JSON.parse(trimmed);
  } catch (e) {
    throw new Error('图片列表须为合法 JSON 数组字符串: ' + (originalError ? originalError.message : e.message));
  }

  if (!Array.isArray(arr) || arr.length === 0) {
    throw new Error('图片列表须为非空数组，元素为图片 URL 字符串');
  }
  const urls = arr.map((u) => String(u).trim()).filter(Boolean);
  if (urls.length === 0) throw new Error('图片 URL 解析后为空');
  return urls;
}

function postJson(urlStr, body, timeoutMs = 120000) {
  const payload = JSON.stringify(body);
  const u = new URL(urlStr);
  const lib = u.protocol === 'https:' ? https : http;
  const port = u.port || (u.protocol === 'https:' ? 443 : 80);

  return new Promise((resolve, reject) => {
    const req = lib.request(
      {
        hostname: u.hostname,
        port,
        path: u.pathname + u.search,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json; charset=utf-8',
          'Content-Length': Buffer.byteLength(payload, 'utf8'),
        },
      },
      (res) => {
        const chunks = [];
        res.on('data', (c) => chunks.push(c));
        res.on('end', () => {
          const raw = Buffer.concat(chunks).toString('utf8');
          let json;
          try {
            json = JSON.parse(raw);
          } catch (_) {}
          resolve({ statusCode: res.statusCode, raw, json });
        });
      }
    );
    const t = setTimeout(() => req.destroy(new Error('超时')), timeoutMs);
    req.on('error', (e) => {
      clearTimeout(t);
      reject(e);
    });
    req.on('close', () => clearTimeout(t));
    req.write(payload);
    req.end();
  });
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    throw new Error(
      '用法:\n  HTML: node push-to-wechat-mp.js html <文件名.html> [sendMode]\n  图片: node push-to-wechat-mp.js img \'<JSON图片链接数组>\' <title> <content> [sendMode]'
    );
  }

  const cfg = readJson('config.json');
  if (!cfg.openId || String(cfg.openId).includes('XXXX')) {
    throw new Error('config.json 里 openId 无效，请用向导生成的配置');
  }

  const apiBase = cfg.apiBase || DEFAULT_API;
  const first = args[0].toLowerCase();
  let title;
  let content;
  let sendMode;
  /** @type {string[]|undefined} */
  let imgUrls;

  if (first === 'img') {
    if (args.length < 4) {
      throw new Error(
        '图片模式参数不足。示例: node push-to-wechat-mp.js img \'["https://example.com/a.png"]\' "标题" "正文说明" draft'
      );
    }
    imgUrls = parseImgUrlsArg(args[1]);
    title = String(args[2] || '').trim() || '未命名';
    content = String(args[3] != null ? args[3] : '图文卡片');
    sendMode = (args[4] && args[4].trim()) || 'draft';
  } else if (first === 'html') {
    const fileName = path.basename((args[1] || '').trim());
    if (!fileName) {
      throw new Error('请传入 HTML 文件名（与脚本同目录）。例如: node push-to-wechat-mp.js html 你的文件.html draft');
    }
    sendMode = (args[2] && args[2].trim()) || 'draft';

    const htmlPath = path.join(DIR, fileName);
    if (!fs.existsSync(htmlPath)) {
      throw new Error('同目录下找不到: ' + fileName + '（请把 HTML 放在脚本所在目录）');
    }
    content = fs.readFileSync(htmlPath, 'utf8');
    if (!content.trim()) throw new Error('文件为空: ' + htmlPath);
    title = titleFromHtml(content);
  } else {
    throw new Error(
      '首参须为 html 或 img。示例:\n  node push-to-wechat-mp.js html 你的文件.html draft\n  node push-to-wechat-mp.js img \'["https://..."]\' "标题" "正文" draft'
    );
  }

  const body = {
    action: 'sendToWechat',
    openId: cfg.openId,
    title: title.slice(0, 64),
    content,
    sendMode,
  };
  if (imgUrls && imgUrls.length > 0) {
    body.imgUrls = imgUrls;
  }
  if (cfg.pushMode === 'custom' && cfg.accountId != null && cfg.accountId !== '') {
    body.accountId = cfg.accountId;
  }

  if (imgUrls && imgUrls.length > 0) {
    console.error(
      '推送中（图片）…',
      apiBase,
      '| 标题',
      title.slice(0, 30) + (title.length > 30 ? '…' : ''),
      '| 图',
      imgUrls.length,
      '张',
      '| 正文长度',
      content.length
    );
  } else {
    console.error(
      '推送中（HTML）…',
      apiBase,
      '| 标题',
      title.slice(0, 30) + (title.length > 30 ? '…' : ''),
      '| 正文长度',
      content.length
    );
  }

  const res = await postJson(apiBase, body);
  console.log(
    JSON.stringify(
      { ok: res.statusCode >= 200 && res.statusCode < 300, statusCode: res.statusCode, data: res.json !== undefined ? res.json : res.raw },
      null,
      2
    )
  );
  if (res.statusCode < 200 || res.statusCode >= 300) process.exit(1);
}

main().catch((e) => {
  console.error(e.message || e);
  process.exit(1);
});
