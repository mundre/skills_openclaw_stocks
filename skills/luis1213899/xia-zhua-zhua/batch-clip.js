#!/usr/bin/env node
/**
 * batch-clip - 并发批量网页转 Markdown
 * 用法: node batch-clip.js <url文件> [并发数] [输出目录]
 */
const fs = require('fs');
const path = require('path');

const { chromium } = require('playwright');
const TurndownService = require('turndown');

const DESKTOP = path.join(process.env.USERPROFILE || '', 'Desktop');
const DEFAULT_CONCURRENCY = 3;
const DEFAULT_OUTPUT = DESKTOP;
const MIN_DELAY = 1000;
const MAX_DELAY = 3000;

// 随机 UA 池
const USER_AGENTS = [
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36',
];

function randomUA() {
  return USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)];
}

function buildFilename(pageUrl, title, ext) {
  try {
    const u = new URL(pageUrl);
    const domain = u.hostname.replace('www.', '');
    const date = new Date().toISOString().slice(0, 10);
    let name = title
      ? title.replace(/[\\/:*?"<>|]/g, '-').replace(/\s+/g, '-').substring(0, 50)
      : u.pathname.replace(/\//g, '-').replace(/^-/, '');
    return `${date}-${domain}-${name}${ext}`;
  } catch {
    return `clip-${Date.now()}${ext}`;
  }
}

function buildFrontmatter(metadata, pageUrl) {
  const lines = ['---'];
  if (metadata.title) lines.push(`title: "${metadata.title.replace(/"/g, '\\"')}"`);
  if (metadata.author) lines.push(`author: "${metadata.author.replace(/"/g, '\\"')}"`);
  if (metadata.description) lines.push(`description: "${metadata.description.replace(/"/g, '\\"')}"`);
  if (metadata.cover) lines.push(`cover: "${metadata.cover}"`);
  lines.push(`source: ${pageUrl}`);
  lines.push(`clipped: ${new Date().toISOString()}`);
  lines.push('---\n');
  return lines.join('\n') + '\n';
}

async function clipOneUrl(pageUrl, outputDir) {
  const timeout = 60000;
  const ua = randomUA();

  const browser = await chromium.launch({
    headless: true,
    args: [
      '--no-sandbox', '--disable-setuid-sandbox',
      '--disable-blink-features=AutomationControlled',
      '--no-first-run', '--no-zygote', '--disable-gpu',
    ],
  });

  const context = await browser.newContext({
    userAgent: ua,
    viewport: { width: 1920, height: 1080 },
    locale: 'zh-CN',
    timezoneId: 'Asia/Shanghai',
  });

  await context.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
    Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en'] });
    // @ts-ignore
    window.chrome = { runtime: {} };
  });

  const page = await context.newPage();

  try {
    await page.goto(pageUrl, { waitUntil: 'domcontentloaded', timeout });
    await page.waitForTimeout(3000);
  } catch {
    try {
      await page.goto(pageUrl, { waitUntil: 'commit', timeout: 30000 });
      await page.waitForTimeout(5000);
    } catch {
      throw new Error('页面加载超时');
    }
  }

  // 提取标题
  async function extractTitle() {
    const selectors = [
      'meta[property="og:title"]', 'meta[property="twitter:title"]',
      'meta[name="title"]', 'h1', 'article h1',
      '.article-title', '.post-title', '.entry-title',
    ];
    for (const sel of selectors) {
      try {
        const el = await page.$(sel);
        if (el) {
          const t = await el.innerText();
          if (t && t.trim()) return t.trim().substring(0, 200);
        }
      } catch {}
    }
    return '';
  }

  // 提取作者
  async function extractAuthor() {
    const selectors = ['meta[name="author"]', 'meta[property="article:author"]', '.author', '.byline'];
    for (const sel of selectors) {
      try {
        const el = await page.$(sel);
        if (el) {
          const t = await el.innerText();
          if (t && t.trim()) return t.trim().substring(0, 100);
        }
      } catch {}
    }
    return '';
  }

  // 提取描述
  async function extractDescription() {
    const selectors = ['meta[property="og:description"]', 'meta[name="description"]'];
    for (const sel of selectors) {
      try {
        const el = await page.$(sel);
        if (el) {
          const t = await el.getAttribute('content');
          if (t && t.trim()) return t.trim().substring(0, 500);
        }
      } catch {}
    }
    return '';
  }

  // 提取封面图
  async function extractCover() {
    const selectors = ['meta[property="og:image"]', 'meta[property="twitter:image"]'];
    for (const sel of selectors) {
      try {
        const el = await page.$(sel);
        if (el) {
          const src = await el.getAttribute('content');
          if (src && (src.startsWith('http') || src.startsWith('//'))) {
            return src.startsWith('//') ? 'https:' + src : src;
          }
        }
      } catch {}
    }
    return '';
  }

  // 提取正文
  async function extractContent() {
    const selectors = [
      'article', '[role="main"]', 'main',
      '.article-content', '.article-body', '.post-content',
      '.entry-content', '.content', '#content', '.post-body',
    ];
    for (const sel of selectors) {
      try {
        const el = await page.$(sel);
        if (el) {
          const html = await el.innerHTML();
          if (html && html.length > 200) {
            return html
              .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
              .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
              .replace(/<!--[\s\S]*?-->/g, '')
              .replace(/<footer[^>]*>[\s\S]*?<\/footer>/gi, '')
              .replace(/<nav[^>]*>[\s\S]*?<\/nav>/gi, '')
              .replace(/<header[^>]*>[\s\S]*?<\/header>/gi, '');
          }
        }
      } catch {}
    }
    try {
      const body = await page.$('body');
      return body ? await body.innerHTML() : '';
    } catch { return ''; }
  }

  const [title, author, description, cover, htmlContent] = await Promise.all([
    extractTitle(), extractAuthor(), extractDescription(), extractCover(), extractContent(),
  ]);

  const metadata = { title, author, description, cover };

  const td = new TurndownService({
    headingStyle: 'atx', codeBlockStyle: 'fenced',
    bulletListMarker: '-', linkStyle: 'inlined',
  });

  td.addRule('images', {
    filter: 'img',
    replacement: (content, node) => {
      const alt = node.alt || '';
      const src = node.src || node.getAttribute('data-src') || '';
      if (!src) return '';
      return `![${alt}](${src})`;
    },
  });

  td.addRule('pre', {
    filter: 'pre',
    replacement: (content, node) => {
      const code = node.querySelector('code');
      const lang = code ? code.className.replace('language-', '') : '';
      return `\n\`\`\`${lang}\n${code ? code.innerText : node.innerText}\n\`\`\`\n`;
    },
  });

  let markdown = td.turndown(htmlContent);
  markdown = markdown
    .replace(/\n{3,}/g, '\n\n')
    .replace(/^\s*\|.*\|\s*$/gm, '')
    .trim();

  const frontmatter = buildFrontmatter(metadata, pageUrl);
  markdown = frontmatter + markdown;

  const filename = buildFilename(pageUrl, metadata.title, '.md');
  const outputPath = path.join(outputDir, filename);
  fs.writeFileSync(outputPath, markdown, 'utf8');

  await browser.close();
  return { success: true, path: outputPath, title: metadata.title, url: pageUrl };
}

// ========== 并发队列核心 ==========

function randomDelay() {
  return Math.floor(Math.random() * (MAX_DELAY - MIN_DELAY)) + MIN_DELAY;
}

async function worker(id, urlQueue, results, outputDir, progress, lock) {
  while (true) {
    let item;
    // 线程安全的 queue shift
    while (true) {
      if (urlQueue.length === 0) { item = undefined; break; }
      item = urlQueue.shift();
      break;
    }
    if (item === undefined) break;

    const { url, index, total } = item;
    process.stdout.write(`\r  [${id}] ${index}/${total}: ${url.substring(0, 55)}...`);

    try {
      const result = await clipOneUrl(url, outputDir);
      results.push({ ...result, status: 'success' });
    } catch (err) {
      results.push({ url, status: 'failed', error: err.message });
    }

    progress.done++;
    if (urlQueue.length > 0) {
      await new Promise(r => setTimeout(r, randomDelay()));
    }
  }
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    console.log(`
📦 batch-clip - 并发批量网页转 Markdown

用法:
  node batch-clip.js <url文件> [并发数] [输出目录]

参数:
  url文件      包含URL的文件，每行一个URL，支持 # 注释
  并发数       同时处理的浏览器实例数（默认 3，最大 10）
  输出目录     保存目录（默认桌面）

示例:
  node batch-clip.js urls.txt
  node batch-clip.js urls.txt 5
  node batch-clip.js urls.txt 3 ~/Desktop
`);
    process.exit(0);
  }

  const urlFile = args[0];
  const concurrency = Math.min(Math.max(parseInt(args[1]) || DEFAULT_CONCURRENCY, 1), 10);
  const outputDir = args[2] || DEFAULT_OUTPUT;

  if (!fs.existsSync(urlFile)) {
    console.error(`\u274c URL文件不存在: ${urlFile}`);
    process.exit(1);
  }

  const raw = fs.readFileSync(urlFile, 'utf-8');
  const urls = raw.split('\n').map(l => l.trim()).filter(l => l && !l.startsWith('#'));

  if (urls.length === 0) {
    console.error('\u274c URL文件中没有有效的URL');
    process.exit(1);
  }

  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  console.log(`\n\uD83D\uDCE6 batch-clip 并发批量抓取`);
  console.log(`  URL数量: ${urls.length}  |  并发数: ${concurrency}  |  输出: ${outputDir}`);
  console.log('');

  const urlQueue = urls.map((url, i) => ({ url, index: i + 1, total: urls.length }));
  const results = [];
  const progress = { done: 0 };
  const lock = { busy: false };

  const workers = [];
  for (let i = 1; i <= concurrency; i++) {
    workers.push(worker(i, urlQueue, results, outputDir, progress, lock));
  }

  await Promise.all(workers);

  console.log('\n\n' + '\u2500'.repeat(50));
  const success = results.filter(r => r.status === 'success');
  const failed = results.filter(r => r.status === 'failed');

  console.log(`\uD83D\uDCCA 处理完成: ${results.length}/${urls.length}`);
  console.log(`\u2705 成功: ${success.length}  |  \u274C 失败: ${failed.length}`);

  if (failed.length > 0) {
    console.log('\n失败列表:');
    failed.forEach(r => console.log(`  - ${r.url}`));
    console.log('');
  }

  if (success.length > 0) {
    console.log('已保存文件:');
    success.forEach(r => console.log(`  \u2705 ${path.basename(r.path)}`));
  }
}

main().catch(err => {
  console.error('\u274c 错误:', err.message);
  process.exit(1);
});
