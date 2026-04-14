#!/usr/bin/env node
/**
 * markdown-clip - CLI tool to clip any webpage to Markdown
 * 用法: node markdown-clip.js <url> [output_path]
 */

const { chromium } = require('playwright');
const TurndownService = require('turndown');
const fs = require('fs');
const path = require('path');
const url = require('url');

// 配置
const DESKTOP = path.join(process.env.USERPROFILE || '', 'Desktop');
const DEFAULT_OUTPUT = DESKTOP;

async function extractTitle(page) {
  const selectors = [
    'meta[property="og:title"]',
    'meta[property="twitter:title"]',
    'meta[name="title"]',
    'meta[name="twitter:title"]',
    'h1', 'h2', 'article h1',
    '.article-title', '.post-title', '.entry-title',
    '#title', '[class*="title"]',
  ];
  for (const sel of selectors) {
    try {
      const el = await page.$(sel);
      if (el) {
        const text = await el.innerText();
        if (text && text.trim().length > 0) {
          return text.trim();
        }
      }
    } catch {}
  }
  return null;
}

async function extractContent(page) {
  const selectors = [
    'article',
    '[role="main"]',
    'main',
    '.post-content', '.article-content', '.entry-content', '.content', '#content',
    '#js_content',
    '.post', '.article', '.story',
    '.main-content', '.page-content',
    '.container', '.article-container',
    '.article-detail', '.article-cont', '.detail-content',
    '.detail', '.article-body',
  ];

  for (const sel of selectors) {
    try {
      const el = await page.$(sel);
      if (el) {
        const html = await page.evaluate(el => {
          const clone = el.cloneNode(true);
          const junkSelectors = [
            'script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'noscript',
            '.login-banner', '.login-tip', '.login-bar',
            '[class*="login"]', '[class*="register"]',
            '[class*="sidebar"]', '[class*="related"]', '[class*="recommend"]',
            '[class*="advertisement"]', '[class*="ads"]', '[class*="track"]',
            '[class*="mathjax"]', '[class*="MathJax"]', '[class*="loading"]',
            '[id*="login"]', '[id*="sidebar"]',
            'form[action]', '.comments', '.comment',
            '.footer', '.header', '.nav',
            '.follow-bar', '.share-bar', '.action-bar',
            '.tags', '.tag-list',
          ];
          junkSelectors.forEach(sel => {
            try { clone.querySelectorAll(sel).forEach(n => n.remove()); } catch {}
          });
          clone.querySelectorAll('a[href=""], a[href="#"]').forEach(a => {
            const text = a.textContent.trim();
            a.replaceWith(document.createTextNode(text));
          });
          return clone.innerHTML;
        }, el);
        if (html && html.replace(/<[^>]+>/g, '').length > 200) {
          return html;
        }
      }
    } catch {}
  }

  return await page.evaluate(() => {
    const body = document.body.cloneNode(true);
    ['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'noscript',
     '.login-banner', '.login-tip', '.login-bar', '[class*="login"]', '[class*="sidebar"]',
     '[class*="related"]', '[class*="recommend"]', '[class*="advertisement"]',
     '[class*="mathjax"]', '[class*="MathJax"]', '[class*="loading"]',
     'form[action]', '.comments', '.comment', '.footer', '.header', '.nav',
     '.follow-bar', '.share-bar', '.action-bar'
    ].forEach(sel => {
      try { body.querySelectorAll(sel).forEach(n => n.remove()); } catch {}
    });
    return body.innerHTML;
  });
}

async function extractMetadata(page) {
  const getMeta = async (selectors) => {
    for (const sel of selectors) {
      try {
        const el = await page.$(sel);
        if (el) {
          const content = await el.getAttribute('content');
          if (content) return content;
        }
      } catch {}
    }
    return null;
  };

  const [title, description, author, cover] = await Promise.all([
    getMeta(['meta[property="og:title"]', 'meta[name="twitter:title"]', 'meta[name="author"]']),
    getMeta(['meta[property="og:description"]', 'meta[name="description"]', 'meta[property="twitter:description"]']),
    getMeta(['meta[name="author"]', 'meta[property="article:author"]']),
    getMeta(['meta[property="og:image"]', 'meta[name="twitter:image"]']),
  ]);

  return { title, description, author, cover };
}

function sanitizeFilename(name) {
  if (!name) return 'untitled';
  return name
    .replace(/[<>:"/\\|?*\x00-\x1f]/g, '')
    .replace(/\s+/g, '-')
    .substring(0, 100)
    .trim('-');
}

function buildFilename(pageUrl, title, ext) {
  const parsed = new url.URL(pageUrl);
  const domain = parsed.hostname.replace('www.', '').replace(/\./g, '-');
  const date = new Date().toISOString().slice(0, 10);

  if (title) {
    const safeTitle = sanitizeFilename(title);
    return `${date}-${domain}-${safeTitle}${ext}`;
  }
  return `${date}-${domain}${ext}`;
}

function buildFrontmatter(metadata, pageUrl) {
  const lines = ['---'];
  if (metadata.title) lines.push(`title: "${metadata.title.replace(/"/g, '\\"')}"`);
  if (metadata.author) lines.push(`author: "${metadata.author.replace(/"/g, '\\"')}"`);
  if (metadata.description) lines.push(`description: "${metadata.description.replace(/"/g, '\\"')}"`);
  if (metadata.cover) lines.push(`cover: "${metadata.cover}"`);
  lines.push(`source: ${pageUrl}`);
  lines.push(`clipped: ${new Date().toISOString()}`);
  lines.push('---', '');
  return lines.join('\n');
}

async function clipUrl(pageUrl, options = {}) {
  const {
    outputDir = DEFAULT_OUTPUT,
    timeout = 60000,
  } = options;

  console.log(`🔗 正在抓取: ${pageUrl}`);

  // 随机 UA，防止被识别为爬虫
  const userAgents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
  ];
  const ua = userAgents[Math.floor(Math.random() * userAgents.length)];

  const browser = await chromium.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-blink-features=AutomationControlled',
      '--no-first-run',
      '--no-zygote',
      '--disable-gpu',
    ],
  });

  const context = await browser.newContext({
    userAgent: ua,
    viewport: { width: 1920, height: 1080 },
    locale: 'zh-CN',
    timezoneId: 'Asia/Shanghai',
    permissions: [],
  });

  // 反检测：隐藏 webdriver 等自动化标志
  await context.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
    Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en'] });
    // @ts-ignore
    window.chrome = { runtime: {} };
    if (window.callPhantom || window._phantom) {
      Object.defineProperty(window, 'callPhantom', { get: () => undefined });
      Object.defineProperty(window, '_phantom', { get: () => undefined });
    }
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
      parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
    );
  });

  const page = await context.newPage();

  // 随机等待 1~3s，模拟人类访问节奏
  await new Promise(r => setTimeout(r, Math.floor(Math.random() * 2000) + 1000));

  try {
    // 优先用 domcontentloaded，对付加载慢的网站
    await page.goto(pageUrl, { waitUntil: 'domcontentloaded', timeout });
    await page.waitForTimeout(3000);
  } catch (err) {
    console.log('  加载超时，尝试降级加载...');
    await page.goto(pageUrl, { waitUntil: 'commit', timeout: 30000 });
    await page.waitForTimeout(5000);
  }

  try {
    const [metadata, htmlContent] = await Promise.all([
      extractMetadata(page),
      extractContent(page),
    ]);

    const td = new TurndownService({
      headingStyle: 'atx',
      codeBlockStyle: 'fenced',
      bulletListMarker: '-',
      linkStyle: 'inlined',
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

    td.addRule('links', {
      filter: 'a',
      replacement: (content, node) => {
        const href = node.href || '';
        const text = node.innerText || content;
        if (!href || href === '#' || href === pageUrl) return text;
        return `[${text}](${href})`;
      },
    });

    let markdown = td.turndown(htmlContent);

    // 清理
    markdown = markdown
      .replace(/\n{3,}/g, '\n\n')
      .replace(/^\s+$/gm, '')
      .replace(/Loading .MathJax.*/gi, '')
      .replace(/Loading.*MathJax.*/gi, '')
      .replace(/\[MathJax\].*/gi, '')
      .replace(/\[\]\([^)]*\?ad_trace=[^)]*\)/g, '')
      .replace(/\[[^\]]*\]\([^)]*utm_[^)]*\)/g, '')
      .replace(/\[[^\]]*\]\([^)]*fromSource=[^)]*\)/g, '')
      .replace(/^\[\]\(.*\)\s*$/gm, '')
      .replace(/^\[Login\/Register\].*/gm, '')
      .replace(/^\[首页\]\[\/.\].*/gm, '')
      .replace(/^\[建议反馈\].*/gm, '')
      .replace(/^\[文档\].*/gm, '')
      .replace(/^\[控制台\].*/gm, '')
      .replace(/^\[登录\/注册\].*/gm, '')
      .replace(/^\*\*作者相关精选\*\*/gm, '')
      .replace(/^\[关注作者\].*/gm, '')
      .replace(/^\[\[.*\]\(.*\)\]\(.*\)/gm, '')
      .replace(/^[*\-\s]*\[?\[*[^"']*\]?\([^)]*codebuddy[^)]*\)?/gim, '')
      .replace(/[*\-\s]*\[[^\]]+\]\([^)]*tencentcloud[^)]*\)/gim, '')
      .replace(/\[[^\]]*\]\(\/developer\/user\/\d+\)/g, '')
      .replace(/^\s*\|.*\|\s*$/gm, '')
      .trim();

    const frontmatter = buildFrontmatter(metadata, pageUrl);
    markdown = frontmatter + markdown;

    const filename = buildFilename(pageUrl, metadata.title, '.md');
    const outputPath = path.join(outputDir, filename);

    fs.writeFileSync(outputPath, markdown, 'utf8');

    console.log(`✅ 已保存: ${outputPath}`);
    console.log(`📄 标题: ${metadata.title || '无标题'}`);
    console.log(`📝 字数: ${markdown.length} 字符`);

    await browser.close();
    return { success: true, path: outputPath, markdown, metadata };
  } catch (err) {
    await browser.close();
    throw err;
  }
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
    console.log(`
🛍️  markdown-clip - 网页转 Markdown CLI 工具

用法:
  node markdown-clip.js <url> [输出目录]

示例:
  node markdown-clip.js https://mp.weixin.qq.com/s/xxxxx
  node markdown-clip.js https://example.com ~/Desktop

  # Batch: node batch-clip.js <urlfile> [concurrency] [outputdir]
`);
    process.exit(0);
  }

  const pageUrl = args[0];
  const outputDir = args[1] || DEFAULT_OUTPUT;

  try {
    new url.URL(pageUrl);
  } catch {
    console.error('❌ 无效的URL');
    process.exit(1);
  }

  try {
    await clipUrl(pageUrl, { outputDir });
  } catch (err) {
    console.error(`❌ 抓取失败: ${err.message}`);
    process.exit(1);
  }
}

main();
