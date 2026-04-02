#!/usr/bin/env node

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const os = require('os');

// ═══ Новые модули диагностики ══════════════════════════════════════════════
const { PipelineTrace } = require('./pipeline-trace.js');
const { MetricsCollector } = require('./metrics-collector.js');
const { requireAuth } = require('./auth-check.js');

// ═══ Константы ══════════════════════════════════════════════════════════════
// ═══ CDP Interceptor (module-level state) ══════════════════════════════════════
var cdpInterceptor = null;
// Определяем базовую директорию навыка (где лежит этот скрипт)
const SCRIPT_DIR = path.dirname(process.argv[1]);
const BASE_DIR = path.resolve(SCRIPT_DIR);

const argv = process.argv.slice(2);
const isVisible = argv.includes('--visible');
const waitForAuth = argv.includes('--wait');
const shouldClose = argv.includes('--close');
const endSession = argv.includes('--end-session');
const newChat = argv.includes('--new-chat');
const useDaemon = argv.includes('--daemon');
const VERBOSE = argv.includes('--verbose');

// ═══ Авто-детект пути к Chromium/Chrome ═══
let executablePath;

// Пробуем bundled Chromium от puppeteer (предпочтительно)
try {
  const bundledPath = require('puppeteer').executablePath();
  if (bundledPath && fs.existsSync(bundledPath)) {
    executablePath = bundledPath;
    log(`✅ Используем bundled Chromium: ${executablePath}`);
  }
} catch (e) {}

// Если bundled не найден, ищем system chromium
if (!executablePath) {
  log('⚠️ Bundled Chromium не найден, ищем system chromium...');
  try {
    const which = require('child_process').execSync('which chromium 2>/dev/null || which chromium-browser 2>/dev/null || which google-chrome 2>/dev/null || echo ""', { encoding: 'utf8' }).trim();
    if (which && fs.existsSync(which)) {
      executablePath = which;
      log(`✅ Найден system chromium: ${executablePath}`);
    }
  } catch (e) {}
}

// ═══ Вспомогательные функции для исправления locked profile ═══

/**
 * Убивает все процессы Chrome, использующие указанный profileDir
 */
async function killChromeProcessesForProfile(profilePath) {
  try {
    const { execSync } = require('child_process');
    const grepCmd = `ps aux | grep -i chrome | grep "${profilePath}" | grep -v grep | awk '{print $2}'`;
    const pids = execSync(grepCmd, { encoding: 'utf8' })
      .split('\n')
      .filter(pid => pid.trim())
      .map(pid => pid.trim());

    if (pids.length > 0) {
      debugLog(`🔪 Убиваем процессы Chrome: ${pids.join(', ')}`);
      for (const pid of pids) {
        try { process.kill(pid, 'SIGKILL'); } catch (e) {}
      }
      // Даем время на завершение
      await new Promise(resolve => setTimeout(resolve, 1000));
      // Очистка /dev/shm и /tmp
      try {
        execSync(`rm -rf /dev/shm/.com.google.Chrome.* 2>/dev/null || true`);
        execSync(`rm -rf /tmp/.com.google.Chrome.* 2>/dev/null || true`);
      } catch (e) {}
    }
  } catch (err) {
    // grep может вернуть ошибку если нет процессов — игнорируем
  }
}

/**
 * Запуск браузера с таймаутом и очисткой lock-файлов
 */
async function launchWithTimeout(options, timeoutMs = 30000) {
  const profileDir = options.userDataDir;
  // Очищаем lock-файлы перед запуском
  if (profileDir && fs.existsSync(profileDir)) {
    const locksToRemove = ['SingletonLock', 'SingletonSocket', 'SingletonCookie'];
    for (const lock of locksToRemove) {
      const lockPath = path.join(profileDir, lock);
      if (fs.existsSync(lockPath)) {
        try {
          fs.unlinkSync(lockPath);
          debugLog(`🧹 Удалён lock-файл: ${lock}`);
        } catch (err) {
          // Может быть permission denied, игнорируем
        }
      }
    }
  }

  log(`🚀 Запуск браузера (timeout: ${timeoutMs}ms)...`);
  const launchPromise = puppeteer.launch(options);
  const timeoutPromise = new Promise((_, reject) => 
    setTimeout(() => {
      debugLog(`⏰ Таймаут launch через ${timeoutMs}ms`);
      reject(new Error(`Launch timeout after ${timeoutMs}ms`));
    }, timeoutMs)
  );

  try {
    const browser = await Promise.race([launchPromise, timeoutPromise]);
    log('✅ Браузер запущен');
    return browser;
  } catch (err) {
    log('❌ Ошибка launch:', err.message);
    throw err;
  }
}

// Извлекаем имя сессии: --session work
const sessionIdx = argv.indexOf('--session');
const sessionName = sessionIdx !== -1 ? (argv[sessionIdx + 1] || 'default') : null;

// Вопрос — всё что не флаг
const question = argv.filter(a =>
 !a.startsWith('--') &&
 (sessionIdx === -1 || argv.indexOf(a) !== sessionIdx + 1)
).join(' ');

if (!question && !endSession) {
 console.error(`Usage:
 node ask-puppeteer.js "вопрос" — одиночный (закроет браузер)
 node ask-puppeteer.js "вопрос" --session work — сессия "work" (держит контекст)
 node ask-puppeteer.js "ещё вопрос" --session work — продолжение в той же сессии
 node ask-puppeteer.js --session work --new-chat "вопрос" — новый чат в сессии
 node ask-puppeteer.js --session work --end-session — завершить сессию
 node ask-puppeteer.js "вопрос" --visible --wait — с видимым браузером
 node ask-puppeteer.js "вопрос" --daemon — использовать демон (если запущен)
`);
 process.exit(1);
}

let browser = null;
let dsPage = null;
let browserLaunchedByUs = false;
let browserConnectionMode = 'local';

// ─── Graceful Shutdown: перехват сигналов для корректного закрытия браузера ──
['SIGINT', 'SIGTERM', 'SIGHUP'].forEach(signal => {
  process.on(signal, async () => {
    log(`\n(System) Получен сигнал ${signal}, закрываем ресурсы...`);
    if (browser && browserLaunchedByUs && shouldClose) {
      try {
        await browser.close();
        log('✅ Браузер закрыт');
      } catch (e) {
        // Игнорируем ошибки закрытия
      }
    } else if (browser) {
      // Сессия демона — просто отключаемся
      try {
        browser.disconnect();
      } catch (e) {}
    }
    process.exit(0);
  });
});

// Используем BASE_DIR
const PROFILE_DIR = path.join(BASE_DIR, '.profile');
const SESSIONS_DIR = path.join(BASE_DIR, '.sessions');
const DAEMON_ENDPOINT_FILE = path.join(BASE_DIR, '.daemon-ws-endpoint');

const DS_URL = 'https://chat.deepseek.com/';
const COMPOSER = [
  // DeepSeek Chat selectors (latest)
  'textarea[data-deepseek="chat-input"]',
  'textarea[placeholder*="Введите"]', 'textarea[placeholder*="Message"]', 'textarea[placeholder*="Type"]', 'textarea[placeholder]', 'textarea',
  'div[contenteditable="true"]', 'div[role="textbox"]', 'div[contenteditable]',
  'div[class*="input" i]', 'div[class*="composer" i]', 'div[class*="editor" i]',
  'div[class*="text-area" i]', 'div[class*="textbox" i]',
  '[contenteditable="true"]', 'p[contenteditable]', '[data-editor]', '[data-composer]', 'div.editor',
  // Web-standard
  'div[aria-label*="message" i]', 'div[aria-label*="input" i]'
];
const RESPONSE_SELECTORS = [
 '.ds-markdown', '.ds-markdown--block', 'div[class*="ds-markdown"]',
 'div[class*="markdown"]', '[class*="message-content"]',
 '[class*="assistant"] [class*="content"]', '[class*="answer-content"]',
 '[data-message-author-role="assistant"]', '.prose',
 '[class*="message"][class*="assistant"]', '[class*="message"][class*="ai"]',
 '[class*="message"]', 'main article',
 'div[class*="chat"] div[class*="content"]',
 // Новые/универсальные
 '.markdown-body',
 '[class*="response"]',
 '[class*="assistant-message"]',
 '[class*="chat-response"]',
 'article',
 'section[class*="content"]',
 'main',
 '[role="main"]',
 // Ещё более общие (всё внутри main)
 'main *',
 'main',
];
const API_PATTERNS = ['/chat/completions', '/completion', '/chat/completion'];

// ─── Утилиты ────────────────────────────────────────────────
function log(...a) { console.log(...a); }
function debugLog(...a) { if (VERBOSE) console.log(...a); }
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
function ensureDirSync(d) { try { fs.mkdirSync(d, { recursive: true }); } catch {} }

// Отключает CSS-анимации и transition для стабилизации DOM
async function disableAnimations(page) {
  await page.evaluate(() => {
    const style = document.createElement('style');
    style.textContent = `
      *, *::before, *::after {
        animation-duration: 0s !important;
        animation-delay: 0s !important;
        transition-duration: 0s !important;
        transition-delay: 0s !important;
      }
    `;
    document.head.appendChild(style);
    // Удаляем классы анимаций/typewriter
    document.querySelectorAll('[class*="typewriter"], [class*="typing"], [class*="cursor"], [class*="animation"]').forEach(el => {
      el.classList.remove('typewriter', 'typing', 'cursor', 'animation');
      el.style.animation = 'none';
    });
  });
}

// Проверяет, жив ли браузер по wsEndpoint (health check)
async function isBrowserAlive(wsEndpoint) {
  try {
    const browser = await puppeteer.connect({
      browserWSEndpoint: wsEndpoint,
      timeout: 5000 // короткий таймаут для быстрой проверки
    });
    const pages = await browser.pages();
    await browser.disconnect();
    return pages.length > 0;
  } catch (err) {
    debugLog('Health check failed:', err.message);
    return false;
  }
}

// Retry logic for transient failures
async function withRetry(fn, options = {}) {
  const { maxRetries = 3, baseDelay = 1000, retryOn = [404, 429, 500, 502, 503] } = options;
  for (let i = 0; i <= maxRetries; i++) {
    try {
      return await fn();
    } catch (err) {
      if (i === maxRetries) throw err;
      const shouldRetry = retryOn.includes(err.statusCode) ||
                          err.message.includes('timeout') ||
                          err.message.includes('ECONNRESET') ||
                          err.message.includes('network') ||
                          err.message.includes('EAI_AGAIN');
      if (!shouldRetry) throw err;
      const delay = baseDelay * Math.pow(2, i);
      debugLog(`⚠️ Retry ${i+1}/${maxRetries} after ${delay}ms: ${err.message}`);
      await sleep(delay);
    }
  }
}

// ─── Демон и оптимизации ────────────────────────────────────────
async function connectToDaemon() {
  if (!fs.existsSync(DAEMON_ENDPOINT_FILE)) {
    throw new Error('Демон не запущен. Запусти: node deepseek-daemon.js');
  }
  const wsEndpoint = fs.readFileSync(DAEMON_ENDPOINT_FILE, 'utf8').trim();
  log('🔗 Подключаюсь к демону:', wsEndpoint);
  try {
    const browser = await puppeteer.connect({
      browserWSEndpoint: wsEndpoint,
      defaultViewport: null,
    });
    browserConnectionMode = 'daemon';
    return browser;
  } catch (e) {
    // Демон не отвечает — удаляем stale endpoint file
    try { fs.unlinkSync(DAEMON_ENDPOINT_FILE); } catch {}
    throw new Error(`Демон недоступен: ${e.message}`);
  }
}

async function blockUnnecessaryResources(page) {
  await page.setRequestInterception(true);
  page.on('request', (req) => {
    const type = req.resourceType();
    const url = req.url().toLowerCase();
    if (['image', 'font', 'media', 'stylesheet'].includes(type)) {
      req.abort();
      return;
    }
    if (url.includes('analytics') || url.includes('tracker') ||
        url.includes('datadoghq') || url.includes('singular') ||
        url.includes('google-analytics') || url.includes('googletagmanager')) {
      req.abort();
      return;
    }
    req.continue();
  });
}

// ─── Управление сессиями ────────────────────────────────────

function getSessionFile(name) {
 ensureDirSync(SESSIONS_DIR);
 return path.join(SESSIONS_DIR, `${name}.json`);
}

function loadSession(name) {
 try {
 const f = getSessionFile(name);
 if (fs.existsSync(f)) return JSON.parse(fs.readFileSync(f, 'utf8'));
 } catch {}
 return { name, messageCount: 0, created: null, lastUsed: null, chatUrl: null, browserPid: null };
}

function saveSession(name, data) {
 try {
 ensureDirSync(SESSIONS_DIR);
 fs.writeFileSync(getSessionFile(name), JSON.stringify(data, null, 2));
 } catch {}
}

function deleteSession(name) {
 try { fs.unlinkSync(getSessionFile(name)); } catch {}
}

function listSessions() {
 try {
 ensureDirSync(SESSIONS_DIR);
 return fs.readdirSync(SESSIONS_DIR)
 .filter(f => f.endsWith('.json'))
 .map(f => {
 try { return JSON.parse(fs.readFileSync(path.join(SESSIONS_DIR, f), 'utf8')); }
 catch { return null; }
 })
 .filter(Boolean);
 } catch { return []; }
}

// ─── Кэш селекторов ────────────────────────────────────────
const CACHE_FILE = path.join(BASE_DIR, 'working-selectors.json');

// Очистка кэша при каждом запуске (защита от старого мусора)
if (fs.existsSync(CACHE_FILE)) {
  try {
    fs.unlinkSync(CACHE_FILE);
    debugLog('[Cache] working-selectors.json удалён (чистый старт)');
  } catch (e) {}
}

function loadCachedSelectors() {
 try {
 if (fs.existsSync(CACHE_FILE)) return JSON.parse(fs.readFileSync(CACHE_FILE, 'utf8')).deepseek || [];
 } catch {}
 return [];
}

function saveCachedSelector(sel) {
 try {
 // Валидация: только чистые CSS-селекторы
 if (!sel || typeof sel !== 'string') return;
 const trimmed = sel.trim();
 if (!trimmed) return;

 // Игнорируем auto-last:, auto-first:, treewalker, body-fallback
 const invalidPrefixes = ['auto-last:', 'auto-first:', 'treewalker', 'body-fallback', '__'];
 if (invalidPrefixes.some(p => trimmed.startsWith(p))) {
   return;
 }

 // Сохраняем только селекторы, которые выглядят как CSS (содержат [a-zA-Z] или начинаются с . # [ *)
 if (!/[a-zA-Z#.[\[]/.test(trimmed)) {
   return;
 }

 const cache = { deepseek: loadCachedSelectors() };
 if (!cache.deepseek.includes(trimmed)) {
   cache.deepseek.unshift(trimmed);
   cache.deepseek = cache.deepseek.slice(0, 20);
   ensureDirSync(path.dirname(CACHE_FILE));
   fs.writeFileSync(CACHE_FILE, JSON.stringify(cache, null, 2));
 }
 } catch {}
}

// ─── Диагностика ────────────────────────────────────────────
async function dumpArtifacts(page, reason) {
 ensureDirSync(BASE_DIR);
 const ts = Date.now();
 const safe = String(reason).replace(/[^a-z0-9]/gi, '_').substring(0, 40);
 try { await page.screenshot({ path: path.join(BASE_DIR, `ds-${safe}-${ts}.png`), fullPage: true }); } catch {}
 try { await fs.promises.writeFile(path.join(BASE_DIR, `ds-${safe}-${ts}.html`), await page.content().catch(() => ''), 'utf8'); } catch {}
}

async function discoverDOM(page) {
 const found = await page.evaluate(() => {
 const r = [];
 for (const el of document.querySelectorAll('div, article, section, p, span')) {
 const t = el.innerText?.trim();
 if (!t || t.length < 30) continue;
 let s = el.tagName.toLowerCase();
 if (el.className && typeof el.className === 'string')
 s += '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.');
 const kids = el.querySelectorAll('div, article, section').length;
 r.push({ s, len: t.length, preview: t.slice(0, 60), density: t.length / (kids + 1) });
 }
 r.sort((a, b) => b.density - a.density);
 return r.slice(0, 4);
 }).catch(() => []);
 if (found.length) {
 log('🔍 DOM:');
 for (const d of found) log(` ${d.s} (${d.len}ch) "${d.preview}"`);
 }
}

// ─── Состояние страницы ─────────────────────────────────────
async function waitUntilReady(page, timeout = 45000) {
 const start = Date.now();
 let i = 0;
 while (Date.now() - start < timeout) {
   i++;

   // Проверяем URL — не на странице логина?
   try {
     const url = page.url();
     if (/login|auth|signup/i.test(url)) {
       throw new Error('Требуется авторизация — запусти с --visible --wait');
     }
   } catch (e) {
     if (e.message && e.message.includes('Требуется авторизация')) throw e;
     // Страница может быть в процессе навигации
   }

   // Ищем composer
   for (const sel of COMPOSER) {
     try {
       const el = await page.$(sel);
       if (el) {
         log(`✅ Composer: ${sel} (${i} checks, ${((Date.now()-start)/1000).toFixed(1)}s)`);
         return sel;
       }
     } catch {}
   }

   // Первые 3 итерации — быстрая проверка (500мс)
   // Потом — стандартная (1с)
   if (i <= 3) {
     log(`⏳ waiting (${i})...`);
     await sleep(500);
   } else {
     await sleep(1000);
   }
 }

 throw new Error(`Not usable after ${timeout}ms`);
}

// ─── Подсчёт сообщений в чате ───────────────────────────────
async function countMessages(page) {
 return page.evaluate(() => {
 // Считаем пары (user + assistant)
 const msgs = document.querySelectorAll(
 '[class*="message"], [data-message-author-role], .ds-markdown'
 );
 return msgs.length;
 }).catch(() => 0);
}

// ─── Браузер ────────────────────────────────────────────────
async function cleanup() {
 try {
   if (browser && browserLaunchedByUs) {
     await browser.close().catch(() => {});
     // Дополнительная очистка процессов для одноразовых запросов
     if (!sessionName && shouldClose) {
       await killChromeProcessesForProfile(PROFILE_DIR);
     }
   }
 } finally {
   browser = null;
   dsPage = null;
 }
}

async function connectToExistingBrowser(session) {
 // Пробуем подключиться к уже запущенному браузеру
 if (session.wsEndpoint) {
 try {
 browser = await puppeteer.connect({ browserWSEndpoint: session.wsEndpoint });
 browserConnectionMode = 'session';
 const pages = await browser.pages();
 dsPage = pages.find(p => p.url().includes('deepseek')) || pages[0];
 if (dsPage) {
 log('🔗 Подключились к существующему браузеру');
 return true;
 }
 } catch {
 log('⚠️ Не удалось подключиться, запускаю новый');
 }
 }
 return false;
}

/**
 * Создает CDP-перехватчик для получения полного ответа от API DeepSeek.
 */
async function setupDeepSeekInterceptor(page) {
  const client = await page.target().createCDPSession();
  await client.send('Network.enable');

  let targetRequestId = null;
  let completionPromiseResolve;
  let completionPromise = new Promise(r => completionPromiseResolve = r);

  client.on('Network.requestWillBeSent', (event) => {
    const url = event.request.url;
    if ((url.includes('/chat/completion') || url.includes('/completion')) && event.request.method === 'POST') {
      targetRequestId = event.requestId;
      debugLog(`[CDP] Пойман запрос к API: ${event.requestId}`);
    }
  });

  client.on('Network.loadingFinished', async (event) => {
    if (event.requestId === targetRequestId) {
      try {
        debugLog(`[CDP] Поток завершен, извлекаем тело...`);
        const response = await client.send('Network.getResponseBody', { requestId: event.requestId });
        let body = response.body;
        if (response.base64Encoded) {
          body = Buffer.from(body, 'base64').toString('utf8');
        }
        completionPromiseResolve(body);
      } catch (err) {
        debugLog(`[CDP] Ошибка извлечения тела: ${err.message}`);
        completionPromiseResolve(null);
      }
    }
  });

  client.on('Network.loadingFailed', (event) => {
    if (event.requestId === targetRequestId) {
      debugLog(`[CDP] Запрос оборвался!`);
      completionPromiseResolve(null);
    }
  });

  return {
    reset: () => {
      targetRequestId = null;
      completionPromise = new Promise(r => completionPromiseResolve = r);
    },
    waitForCompletion: () => completionPromise
  };
}


async function ensureBrowser(session, tracer = null) {
 debugLog(`[DEBUG] ensureBrowser() start, session:`, session);
 debugLog(`[DEBUG] browser=${!!browser}, dsPage=${!!dsPage}`);
 // Уже подключены — проверяем жива ли страница
 if (browser && dsPage) {
   try {
     const url = await dsPage.url();
     debugLog(`[DEBUG] Existing page alive, url=${url.substring(0, 50)}`);
     return dsPage;
   } catch (e) {
     debugLog(`[DEBUG] Existing page dead: ${e.message}`);
     browser = null;
     dsPage = null;
   }
 } else {
   debugLog(`[DEBUG] No existing browser/page, will launch new`);
 }

 // ═══ Попытка 1: подключиться к демону (если --daemon ИЛИ если демон уже запущен) ═══
 debugLog(`[DEBUG] Checking daemon: useDaemon=${useDaemon}, DAEMON_ENDPOINT_FILE exists=${fs.existsSync(DAEMON_ENDPOINT_FILE)}`);
 if (tracer) tracer.start('DAEMON_CONNECT');
 if (useDaemon || fs.existsSync(DAEMON_ENDPOINT_FILE)) {
   try {
     debugLog('[DEBUG] Connecting to daemon...');
     browser = await connectToDaemon();
     const pages = await browser.pages();
     dsPage = pages.find(p => {
       try { return p.url().includes('deepseek'); } catch { return false; }
     }) || pages[0] || await browser.newPage();

     // Если страница не на DeepSeek — переходим
     const currentUrl = dsPage.url();
     if (!currentUrl.includes('deepseek')) {
       log('📍 Навигация на DeepSeek...');
       await dsPage.goto(DS_URL, { waitUntil: 'domcontentloaded', timeout: 20000 });
     }

     log(`🔗 Подключился к демону (URL: ${dsPage.url().substring(0, 50)})`);
     if (tracer) tracer.succeed('DAEMON_CONNECT', { url: dsPage.url() });
     return dsPage;
   } catch (e) {
     debugLog(`[DEBUG] Daemon connection failed: ${e.message}`);
     if (tracer) tracer.fail('DAEMON_CONNECT', e.message);
     if (useDaemon) {
       // При --daemon НЕ падаем в fallback
       throw new Error('Демон недоступен. Запусти: cd ~/.openclaw/workspace/skills/ai-orchestrator && node deepseek-daemon.js');
     } else {
       // Демон найден, но не отвечает — логируем и продолжаем
       log(`⚠️ Демон найден, но недоступен: ${e.message}`);
     }
   }
 } else {
   if (tracer) tracer.skip('DAEMON_CONNECT', 'daemon mode not used');
 }

 // ═══ Попытка 2: подключиться к существующему браузеру через сессию ═══
 if (tracer) tracer.start('SESSION_RESTORE');
 if (session) {
   const wsEndpoint = session.wsEndpoint;
   if (wsEndpoint) {
     if (await isBrowserAlive(wsEndpoint)) {
       if (await connectToExistingBrowser(session)) {
       if (tracer) tracer.succeed('SESSION_RESTORE', { url: dsPage.url() });
         return dsPage;
       }
     } else {
       debugLog('⚠️ Сессия неактивна, удаляем файл сессии');
       const sessionPath = path.join(BASE_DIR, '.sessions', sessionName + '.json');
       try { fs.unlinkSync(sessionPath); } catch (e) { debugLog('Ошибка удаления сессии:', e.message); }
     }
   }
   if (tracer) tracer.skip('SESSION_RESTORE', 'no session or session dead');
 }

 // ═══ Попытка 3: запустить новый браузер ═══
 if (tracer) tracer.start('BROWSER_LAUNCH');  // NOTE: nested within parent's BROWSER_LAUNCH phase
 await cleanup();
 ensureDirSync(PROFILE_DIR);

 // Для одноразовых запросов (не сессий) убиваем процессы и очищаем locks
 if (!session && shouldClose) {
   await killChromeProcessesForProfile(PROFILE_DIR);
   await new Promise(resolve => setTimeout(resolve, 1000)); // даем время на завершение
 }

 const launchOptions = {
   headless: isVisible ? false : 'new',
   userDataDir: PROFILE_DIR,
   args: [
     '--no-sandbox', '--disable-setuid-sandbox',
     '--disable-blink-features=AutomationControlled',
     '--no-first-run', '--no-default-browser-check',
     '--disable-gpu', '--window-size=1280,800',
   ],
 };
 if (executablePath) {
   launchOptions.executablePath = executablePath;
 }

 log('🚀 Запуск нового браузера...');
 browser = await launchWithTimeout(launchOptions, 30000);
 browserLaunchedByUs = true;
 browserConnectionMode = 'local';

 const pages = await browser.pages();
 dsPage = pages[0] || await browser.newPage();

 await dsPage.setUserAgent(
   'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
 );
 await dsPage.setViewport({ width: 1280, height: 800 });
 await dsPage.evaluateOnNewDocument(() => {
   Object.defineProperty(navigator, 'webdriver', { get: () => false });
 });

 // Блокируем лишние ресурсы (если не видимый и мы запустили браузер)
 // FIXME: блокировка может мешать работе DeepSeek, временно отключено
 // if (browserLaunchedByUs && !isVisible) {
 //   try {
 //     await blockUnnecessaryResources(dsPage);
 //   } catch (e) {
 //     log('⚠️ Не удалось настроить блокировку ресурсов:', e.message);
 //   }
 // }

 // Логируем только API
 dsPage.on('response', resp => {
   const url = resp.url();
   if (API_PATTERNS.some(p => url.includes(p)))
     debugLog(`🌐 API ${resp.status()}: ${url.split('?')[0].split('/').pop()}`);
 });

 // Открываем DeepSeek (или сохранённый чат)
 if (tracer) tracer.start('PAGE_NAVIGATE');
 if (session?.chatUrl && !newChat) {
   log(`📂 Открываю чат: ${session.chatUrl.substring(0, 50)}`);
   await dsPage.goto(session.chatUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
 } else {
   log('📍 Открываем DeepSeek...');
   await dsPage.goto(DS_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
 }
 if (tracer) tracer.succeed('PAGE_NAVIGATE', { url: dsPage.url() });

 // Отключаем анимации для стабилизации DOM
 await disableAnimations(dsPage);
 await sleep(150); // достаточно для стабилизации DOM

 // Авторизация если нужно
 if (isVisible && waitForAuth) {
   log('\n⚠️ Авторизуйтесь и нажмите Enter...');
   if (process.stdin.isTTY) {
     await new Promise(r => { process.stdin.resume(); process.stdin.once('data', () => r()); });
   } else {
     await sleep(60000);
   }
 }

 // Сохраняем wsEndpoint для будущих подключений (сессии)
 if (session) {
   session.wsEndpoint = browser.wsEndpoint();
   saveSession(session.name, session);
 }

 return dsPage;
}

// ─── Новый чат ──────────────────────────────────────────────
async function startNewChat(page) {
 log('🆕 Начинаю новый чат...');

 // Проверяем, находимся ли мы уже в чате
 // Если --new-chat НЕ запрошен — пропускаем. Если запрошен — создаём принудительно.
 try {
   const url = page.url();
   if (url.includes('/a/chat/s/') && !newChat) {
     log('🆕 Уже в чате — пропускаем создание нового');
     return;
   }
 } catch (e) {
   // ignore, продолжим
 }

 const clicked = await page.evaluate(() => {
 // Ищем кнопку "New chat"
 const candidates = document.querySelectorAll('button, [role="button"], a');
 for (const el of candidates) {
 const text = (el.textContent || el.innerText || '').trim().toLowerCase();
 const aria = (el.getAttribute('aria-label') || '').toLowerCase();
 if ((text.includes('new chat') || text.includes('новый чат') || aria.includes('new chat'))
 && el.offsetWidth > 0) {
 el.click();
 return text || aria;
 }
 }
 return null;
 }).catch(() => null);

 if (clicked) {
 log(`🆕 New chat: "${clicked}"`);
 await sleep(1500);
 } else {
 // Fallback: goto main page
 await page.goto(DS_URL, { waitUntil: 'domcontentloaded', timeout: 15000 });
 await sleep(1500);
 }
}

// ─── Включение Search ───────────────────────────────────────
async function enableSearch(page) {
 log('🔍 Активирую Search...');

 const result = await page.evaluate(() => {
 const all = [...document.querySelectorAll('button, [role="button"], div[class*="btn"], span')];
 for (const el of all) {
 const text = (el.textContent || '').trim();
 const aria = (el.getAttribute('aria-label') || '');
 if ((/^search$/i.test(text) || /search/i.test(aria)) && el.offsetWidth > 0 && !el.disabled) {
 el.click();
 return `"${text}" aria="${aria}"`;
 }
 }
 // По data-атрибутам
 const dataSearch = document.querySelector('[data-testid*="search"], [data-action*="search"]');
 if (dataSearch) { dataSearch.click(); return 'data-attr'; }
 return null;
 }).catch(() => null);

 if (result) { log(`🔍 Search: ${result}`); await sleep(500); }
 else log('⚠️ Кнопка Search не найдена');
}

// ─── Отправка ───────────────────────────────────────────────
async function sendPrompt(page, composerSelector, prompt) {
 log(`📝 "${prompt.substring(0, 60)}..."`);

 const needsSearch = /\[РЕЖИМ: ПОИСК/i.test(prompt);
 if (needsSearch) await enableSearch(page);

 const element = await page.waitForSelector(composerSelector, { visible: true, timeout: 10000 });
 const textBefore = prompt;

 const result = await element.evaluate((el, text) => {
 el.focus();
 // Проверяем тип элемента для корректного ввода текста
 if (el.isContentEditable || el.getAttribute('contenteditable') === 'true') {
   el.textContent = text;
   el.dispatchEvent(new Event('input', { bubbles: true }));
   el.dispatchEvent(new Event('change', { bubbles: true }));
 } else if (el instanceof HTMLTextAreaElement || el instanceof HTMLInputElement) {
   const proto = el instanceof HTMLTextAreaElement ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
   const setter = Object.getOwnPropertyDescriptor(proto, 'value')?.set;
   if (setter) {
     setter.call(el, text);
   } else {
     el.value = text;
   }
   el.dispatchEvent(new Event('input', { bubbles: true }));
   el.dispatchEvent(new Event('change', { bubbles: true }));
 } else {
   el.textContent = text;
   el.dispatchEvent(new Event('input', { bubbles: true }));
 }

 const enter = { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true, cancelable: true };
 el.dispatchEvent(new KeyboardEvent('keydown', enter));
 el.dispatchEvent(new KeyboardEvent('keypress', enter));
 el.dispatchEvent(new KeyboardEvent('keyup', enter));

 let btn = null;
 for (const sel of ['button[type="submit"]', '[data-testid="send"]', 'button[aria-label*="send" i]']) {
 const b = (el.closest('form') || document).querySelector(sel);
 if (b && b.offsetWidth > 0 && !b.disabled) { b.click(); btn = sel; break; }
 }
 if (!btn) {
 const nearby = el.parentElement?.querySelector('button, [role="button"]');
 if (nearby && nearby.offsetWidth > 0 && !nearby.disabled) { nearby.click(); btn = 'nearby'; }
 }
 const len = (el.value || el.textContent || '').length;
 return { len, btn };
 }, prompt);

 await sleep(20);
 return { textBefore };
}

// ─── Чтение ответа ──────────────────────────────────────────
async function getTexts(page, selectors, prompt, opts = {}) {
 const minLen = opts.minLen || 50; // порог символов
 const results = [];
 
 // 1. Прямые селекторы: используем $$eval (один вызов, безопасно)
 for (const sel of selectors) {
   try {
     const texts = await page.$$eval(sel, (elements, prompt, minLen) => {
       return elements
         .filter(el => {
           if (el.closest('.sidebar, nav, aside, .history, .conversation-list, [class*="sidebar"], [class*="nav"], [class*="history"], [class*="list"][class*="conversation"]')) return false;
           if (el.closest('textarea, [contenteditable], [role="textbox"], [data-editor], div[class*="input"], div[class*="composer"]')) return false;
           const txt = el.innerText?.trim();
           return txt && txt.length >= minLen;
         })
         .map(el => el.innerText.trim())
         .filter(txt => txt.length >= minLen)
         .slice(0, 1); // только первый/наилучший
     }, prompt, minLen);
     
     if (texts.length > 0) {
       results.push({ selector: sel, text: texts[0] });
     }
   } catch (e) {
     // Detached frames ожидаемы при DOM churn
   }
 }
 
 // 2. Если не нашли — auto-last с ретраями (защита от detached frame)
 if (results.length === 0) {
   try {
     const best = await extractWithRetry(page, prompt, { minLen });
     if (best) results.push(best);
   } catch (e) {
     // Detached frames ожидаемы
   }
 }
 
 return results;
}

function isValid(t, minLen = 50) {
 if (!t || t.trim().length < minLen) return false;
 if (/captcha|verify you are human|rate limit/i.test(t)) return false;
 return true;
}

// ─── Извлечение с ретраями (защита от detached Frame) ─────────────────────
async function extractWithRetry(page, prompt, opts = {}) {
 const minLen = opts.minLen || 3;
 const maxRetries = opts.maxRetries || 3;
 for (let i = 0; i < maxRetries; i++) {
   try {
     return await page.evaluate((prompt, minLen) => {
       let candidates = [];
       const byRole = document.querySelectorAll('[data-message-author-role="assistant"]');
       if (byRole.length) candidates = Array.from(byRole);
       
       if (candidates.length === 0) {
         const classSelectors = '[class*="assistant"], [class*="ai"], [class*="bot"], [class*="message"]';
         candidates = Array.from(document.querySelectorAll(classSelectors));
       }
       
       const filtered = candidates.filter(el => {
         if (el.closest('.sidebar, nav, aside, .history, .conversation-list, [class*="sidebar"], [class*="nav"], [class*="history"], [class*="list"][class*="conversation"]')) return false;
         if (el.closest('textarea, [contenteditable], [role="textbox"], [data-editor], div[class*="input"], div[class*="composer"]')) return false;
         const txt = el.innerText?.trim();
         if (!txt || txt.length < minLen) return false;
         if (txt.length < 100) return true; // короткие — без density check
         const kids = el.querySelectorAll('div, article, section').length;
         const density = txt.length / (kids + 1);
         return density > 30;
       });
       
       if (filtered.length === 0) return null;
       
       const last = filtered[filtered.length - 1];
       const text = last.innerText.trim().slice(0, 5000);
       
       if (prompt && text.length > 0 && Math.abs(text.length - prompt.length) < 10) {
         if (text.startsWith(prompt.substring(0, 20))) return null;
       }
       
       return {
         selector: `auto-last:${last.tagName.toLowerCase()}${last.className ? '.'+last.className.split(/\s+/)[0] : ''}`,
         text: text
       };
     }, prompt, minLen);
   } catch (err) {
     if (err.message.includes('detached Frame') || err.message.includes('Execution context was destroyed')) {
       // Detached frames ожидаемы при DOM churn — не логируем как проблему
       await new Promise(r => setTimeout(r, 500)); // было 2000ms — оптимизировано
     } else {
       throw err;
     }
   }
 }
 return null;
}

// ─── Извлечение ответа из DOM (чистый текст) ───────────────────────────────
async function extractAnswerFromDOM(page, textBefore, opts = {}) {
 const minLen = opts.minLen || 50;
 try {
   // Ищем блоки ответов ассистента
   const answerText = await page.evaluate((minLen) => {
     // Приоритет 1: сообщения с атрибутом data-message-author-role="assistant"
     let blocks = Array.from(document.querySelectorAll('[data-message-author-role="assistant"]'));
     
     // Приоритет 2: классы, связанные с ответами ассистента
     if (blocks.length === 0) {
       const classSelectors = [
         '.ds-markdown',
         '.markdown-body',
         'div[class*="assistant"]:not([class*="user"])',
         'div[class*="ai"]:not([class*="user"])',
         'div[class*="bot"]:not([class*="user"])',
         'div[class*="response"]',
         'article'
       ];
       for (const sel of classSelectors) {
         const els = document.querySelectorAll(sel);
         if (els.length) blocks.push(...Array.from(els));
       }
     }
     
     // Убираем интерфейсные элементы и пользовательские сообщения
     const filtered = blocks.filter(el => {
       // Исключаем risen через родителя
       if (el.closest('textarea, [contenteditable], [role="textbox"], [data-editor], div[class*="input"], div[class*="composer"], nav, aside, .sidebar, .header, .footer, [class*="toolbar"]')) {
         return false;
       }
       // Исключаем пользовательские сообщения (role=user)
       if (el.closest('[data-message-author-role="user"]')) {
         return false;
       }
       const txt = el.innerText?.trim();
       return txt && txt.length >= minLen;
     });
     
     if (filtered.length === 0) return null;
     
     // Берем самый последний блок (текущий ответ)
     const lastMessage = filtered[filtered.length - 1];
     return lastMessage.innerText.trim();
   }, minLen);
   
   if (!answerText || answerText.length < minLen) return null;
   
   // Убираем промпт если есть
   let cleaned = answerText;
   if (textBefore && answerText.includes(textBefore)) {
     cleaned = answerText.replace(textBefore, '').trim();
   }
   if (cleaned.length < minLen && answerText.length > 100) {
     const ratio = textBefore ? (textBefore.length / answerText.length) : 0;
     if (ratio < 0.3) {
       cleaned = answerText.slice(Math.floor(answerText.length * 0.3)).trim();
     }
   }
   return cleaned.length >= minLen ? cleaned : null;
 } catch (e) {
   return null;
 }
}

// ─── Обработка кнопки "Продолжить" ─────────────────────────────────────────
/**
 * Проверяет и кликает кнопку "Continue generating" / "Продолжить" если она есть.
 * Возвращает дополнительный контент (пустую строку если кнопки нет или таймаут).
 * @param {import('puppeteer').Page} page
 * @param {string} existingText — уже извлечённый текст (чтобы отличить новое)
 * @returns {Promise<string>}追加 текст или пустая строка
 */
async function handleContinueButton(page, existingText) {
  const CONTINUE_SELECTORS = [
    // DeepSeek buttons (CSS only; Puppeteer doesn't support :has-text)
    'button[class*="continue" i]',
    'button[class*="regenerate" i]',
    '[class*="continue" i] button',
    '[class*="regenerate" i] button',
    'button[class*="outline" i]',
    'button[class*="secondary" i]',
    'button',
    '[role="button"]',
    'a',
  ];

  let continueBtn = null;
  for (const sel of CONTINUE_SELECTORS) {
    try {
      const btns = await page.$$(sel);
      for (const btn of btns) {
        const text = await btn.evaluate(el => el.textContent.trim());
        const disabled = await btn.evaluate(el => el.disabled || el.getAttribute('aria-disabled') === 'true');
        if ((text.includes('Continue') || text.includes('Продолжить') || text.includes('Generate')) && !disabled) {
          continueBtn = btn;
          log(`🔄 Найдена кнопка продолжения: "${text}" (${sel})`);
          break;
        }
      }
      if (continueBtn) break;
    } catch (e) { /* selector might not match, try next */ }
  }

  if (!continueBtn) {
    // === FALLBACK: кнопка не найдена ===
    // Если ответ длинный или явно обрезан, пробуем отправить "Продолжи" через composer
    const shouldFallback = existingText.length > 8000 ||
      (existingText.length >= 2000 && existingText.length <= 6000);
    if (shouldFallback) {
      log('⚠️ Кнопка "Продолжить" не найдена, пробуем fallback (отправка "Продолжи")');
      try {
        const composerSelectors = [
          'textarea[placeholder*="Message"]',
          'textarea[placeholder*="message"]',
          'div[contenteditable="true"]',
          'textarea',
        ];
        let composer = null;
        for (const sel of composerSelectors) {
          try {
            const el = await page.$(sel);
            if (el) { composer = el; break; }
          } catch {}
        }
        if (!composer) {
          log('❌ Composer не найден для fallback');
          return '';
        }

        await composer.click({ clickCount: 3 });
        await page.keyboard.press('Backspace');
        await sleep(200);
        await composer.type('Продолжи');
        await sleep(300);
        // Отправляем через Enter (не через кнопку)
        await page.keyboard.press('Enter');
        log('✅ Отправили "Продолжи" через Enter');

        await sleep(2000);
        const newCandidates = await page.evaluate(() => {
          const els = document.querySelectorAll('[class*="message"], [class*="content"], [class*="answer"], article, main');
          let best = { text: '', len: 0 };
          for (const el of els) {
            const t = (el.textContent || '').trim();
            if (t.length > best.len) best = { text: t, len: t.length };
          }
          return best;
        });

        if (newCandidates.len > existingText.length + 100) {
          // Защита: новый текст должен быть хотя бы на 100 символов больше
          // (защита от "pseudo-update" где добавляется 1-2 символа)
          log(`📈 Fallback вернул +${newCandidates.len - existingText.length} символов`);
          return newCandidates.text.substring(existingText.length);
        } else {
          log(`⚠️ Fallback: текст не изменился существенно (${newCandidates.len - existingText.length} символов delta)`);
          return '';
        }
      } catch (e) {
        log(`❌ Fallback ошибка: ${e.message}`);
        return '';
      }
    }
    return '';
  }

  // Кликаем и ждём нового контента
  try {
    await continueBtn.click();
    log('✅ Кликнули "Продолжить", ждём новый контент...');
    await sleep(1000); // было 3000ms — оптимизировано для скорости

    // Ждём появления НОВОГО текста (больше чем existingText)
    const maxWaitMs = 300000; // 5 минут на каждое продолжение
    const startTime = Date.now();
    let newText = existingText;
    let lastLen = 0;

    while (Date.now() - startTime < maxWaitMs) {
      await sleep(250); // быстрее polling без заметной потери надежности
      const candidates = await page.evaluate(() => {
        const els = document.querySelectorAll('[class*="message"], [class*="content"], [class*="answer"], article, main');
        let best = { text: '', len: 0 };
        for (const el of els) {
          const t = (el.textContent || '').trim();
          if (t.length > best.len) best = { text: t, len: t.length };
        }
        return best;
      });

      if (candidates.len > newText.length) {
        newText = candidates.text;
        if (candidates.len !== lastLen) {
          log(`📈 Продолжение: +${candidates.len - existingText.length} символов (всего ${candidates.len})`);
          lastLen = candidates.len;
        }
      }

      // Проверяем: может текст стабилизировался
      if (newText.length === lastLen && lastLen > 0) {
        await sleep(2000); // было 5000ms — оптимизировано для скорости
        const final = await page.evaluate(() => {
          const els = document.querySelectorAll('[class*="message"], [class*="content"], [class*="answer"], article, main');
          let best = { text: '', len: 0 };
          for (const el of els) {
            const t = (el.textContent || '').trim();
            if (t.length > best.len) best = { text: t, len: t.length };
          }
          return best;
        });
        if (final.len === lastLen) {
          log(`✅ Продолжение завершено (${final.len - existingText.length} новых символов)`);
          return final.text.slice(existingText.length); // возвращаем ТОЛЬКО追加 часть
        }
      }
    }

    // Таймаут — возвращаем что успели набрать
    log(`⚠️ Таймаут продолжения, возвращаем ${newText.length - existingText.length} новых символов`);
    return newText.slice(existingText.length);
  } catch (e) {
    log(`⚠️ Не удалось кликнуть Continue: ${e.message}`);
    return '';
  }
}

async function waitForAnswer(page, prompt, textBefore, timeoutMs = 600000, tracer = null, metrics = null) {
  log('⏳ Жду ответ...');

  // === Детектор завершения потока ==========================================
  // Сначала ждём сигнала от CDP, затем используем DOM как источник ответа.
  let apiFinished = false;
  if (cdpInterceptor) {
    cdpInterceptor.waitForCompletion().then(() => {
      apiFinished = true;
      log('✅ CDP: API стрим завершён');
    }).catch(() => {});
  }
  const idleTimeoutMs = 15000; // 15 секунд без изменений текста (было 30)
  const heartbeatIntervalMs = 15000; // выводить прогресс каждые 15 секунд
  const domErrorIdleMs = 25000; // если 25 секунд только ошибки извлечения — прерываем (было 40)
  let lastText = '';
  let lastChangeTime = Date.now();
  let lastHeartbeatTime = Date.now();
  let lastSuccessfulExtraction = Date.now();
  let foundSelector = null;
  let consecutiveExtractionErrors = 0;

  const cached = loadCachedSelectors();
  const allSels = [...new Set([...cached, ...RESPONSE_SELECTORS])];
  const startTime = Date.now();

  // Основной цикл: проверяем DOM каждые 2 секунды
  while (true) {
    // Global timeout
    if (Date.now() - startTime > timeoutMs) {
      break;
    }

    // Если CDP сообщил о завершении стрима — запускаем финальное извлечение
    if (apiFinished && lastText && lastText.length >= 50) {
      log('✅ API завершился, извлекаем финальный текст из DOM...');
      const finalText = await extractAnswerFromDOM(page, textBefore);
      if (finalText && finalText.length > lastText.length) {
        lastText = finalText;
        foundSelector = 'answer-dom';
      }
      break;
    }

    let currentText = null;

    // 1. Сначала пробуем DOM-экстракт: это самый дешёвый и обычно самый точный путь.
    let answerText = await extractAnswerFromDOM(page, textBefore, { minLen: 50 });
    if (!answerText || answerText.length < 50) {
      answerText = await extractAnswerFromDOM(page, textBefore, { minLen: 2 });
    }
    if (answerText && answerText.length >= 2 && answerText.toLowerCase() !== prompt.toLowerCase()) {
      currentText = answerText;
      foundSelector = 'answer-dom';
    }

    // 2. Если DOM не дал результата — пробуем селекторы (сначала normal, потом tiny)
    if (!currentText) {
      let texts = await getTexts(page, allSels, prompt, { minLen: 50 });
      let valid = texts.filter(x => isValid(x.text, 50));
      if (!valid.length) {
        texts = await getTexts(page, allSels, prompt, { minLen: 3 });
        valid = texts.filter(x => isValid(x.text, 2));
      }
      if (valid.length) {
        valid.sort((a, b) => b.text.length - a.text.length);
        const best = valid[0];
        if (prompt && best.text.length > 0 && Math.abs(best.text.length - prompt.length) < 10) {
          if (!best.text.startsWith(prompt.substring(0, 20))) {
            currentText = best.text;
            foundSelector = best.selector;
          }
        } else {
          currentText = best.text;
          foundSelector = best.selector;
        }
      }
    }

    // Обработка результата извлечения
    if (currentText && currentText.length >= 2) {
      consecutiveExtractionErrors = 0;

      if (currentText !== lastText) {
        lastText = currentText;
        lastChangeTime = Date.now();
        lastSuccessfulExtraction = Date.now();
        log(`📈 Текст обновился: ${currentText.length} символов`);
      }

      // Heartbeat
      const now = Date.now();
      if (now - lastHeartbeatTime > heartbeatIntervalMs) {
        log(`[Progress] Сгенерировано ${currentText.length} символов...`);
        lastHeartbeatTime = now;
      }

      // Idle timeout (только для длинных ответов)
      if (currentText.length >= 50 && now - lastChangeTime > idleTimeoutMs) {
        log(`✅ Стабильный текст (${lastText.length} символов) после ${Math.round((now-lastChangeTime)/1000)} сек без изменений`);
        break;
      }
      
      // Короткие ответы (< 50 chars) — принимаем только после короткой стабилизации
      if (currentText.length < 50) {
        const shortStableMs = 300;
        if (apiFinished && now - lastChangeTime >= shortStableMs) {
          await sleep(50);
          log(`✅ Короткий ответ: "${currentText}" (${currentText.length} символов)`);
          break;
        }
      }
    } else {
      consecutiveExtractionErrors++;
    }

    // Проверка длительных ошибок извлечения
    const now = Date.now();
    if (consecutiveExtractionErrors > 0 && (now - lastSuccessfulExtraction > domErrorIdleMs)) {
      log(`⚠️ Длительный период ошибок извлечения (${Math.round((now - lastSuccessfulExtraction)/1000)} сек). Возвращаем partial (${lastText.length} символов)`);
      if (lastText && lastText.length >= 50) {
        break;
      } else {
        throw new Error('Нет успешных извлечений (длительный DOM churn)');
      }
    }

    await sleep(100); // faster polling without losing reliability
  }

  // ─── Цикл "Продолжить" ─────────────────────────────────────────────
  // Кликаем кнопку "Продолжить" пока она есть и появляется новый контент
  let finalText = lastText || '';
  let continueRound = 0;
  const MAX_CONTINUE_ROUNDS = 30; // защита от бесконечного цикла

  while (continueRound < MAX_CONTINUE_ROUNDS) {
    if (finalText.length < 50) break;

    continueRound++;
    if (tracer) tracer.start('CONTINUE');
    if (metrics) metrics.increment('continueRounds');
    log(`🔍 Раунд ${continueRound}: ищу кнопку продолжения (уже ${finalText.length} символов)...`);

    const addedText = await handleContinueButton(page, finalText);

    if (!addedText || addedText.length < 50) {
      if (continueRound === 1) {
        // Кнопка не найдена вообще — просто возвращаем что есть
        log(`✅ Финальный текст: ${finalText.length} символов (кнопки продолжения нет)`);
      } else {
        log(`✅ Продолжения завершены: ${finalText.length} символов`);
      }
      if (tracer) tracer.succeed('CONTINUE', { rounds: continueRound, finalLength: finalText.length, found: false });
      break;
    }

    finalText += addedText;
    log(`📦 +${addedText.length} символов → итого ${finalText.length}`);
    if (tracer) tracer.succeed('CONTINUE', { rounds: continueRound, addedChars: addedText.length, totalLength: finalText.length });
  }

  // Возвращаем текст (принимаем даже 2 символа — "hi", "ok" и т.д.)
  if (finalText && finalText.length >= 2) {
    return { selector: foundSelector || 'final', text: finalText };
  }

  throw new Error('Ответ не найден (таймаут)');
}

// ─── Главная ────────────────────────────────────────────────
async function ask(q) {
 // ═══ Инициализация диагностики ════════════════════════════════════════════
 const LOG_DIR = path.join(BASE_DIR, '.diagnostics');
 const tracer = new PipelineTrace({
   traceId: `tr-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
   sessionName,
   promptPreview: q.substring(0, 80),
   logDir: LOG_DIR,
 });
 const metrics = new MetricsCollector({
   traceId: tracer.traceId,
   sessionName,
   promptLength: q.length,
   outputDir: LOG_DIR,
 });

 tracer.start('INIT');
 metrics.phaseStart('init');
 metrics.snapMemory('start');

 // ═══ Rate limit ═══════════════════════════════════════════════════════════
 const RL = path.join(BASE_DIR, 'rate-limit.json');
 try {
 const now = Date.now();
 let lim = { t: 0 };
 if (fs.existsSync(RL)) lim = JSON.parse(fs.readFileSync(RL, 'utf8'));
 if (now - (lim.t || 0) < 5000) throw new Error('Rate limit: 5s');
 lim.t = now;
 ensureDirSync(BASE_DIR);
 fs.writeFileSync(RL, JSON.stringify(lim));
 } catch (e) { if (e.message.includes('Rate limit')) throw e; }
 tracer.succeed('INIT', { rateLimit: 'passed' });
 metrics.phaseEnd('init');

 // ═══ Определяем режим ═══
 const isSession = !!sessionName;
 const session = isSession ? loadSession(sessionName) : null;

 debugLog(`[DEBUG] ask() started, q=${q.substring(0, 50)}`);
 debugLog(`[DEBUG] sessionName=${sessionName}, isSession=${isSession}`);
 debugLog(`[DEBUG] loaded session:`, session ? {chatUrl: session.chatUrl, messageCount: session.messageCount} : null);

 if (isSession) {
 log(`\n🔄 Сессия: "${sessionName}" (сообщений: ${session.messageCount})`);
 } else {
 log(`\n🤖 Одиночный запрос`);
 }
 log(`📝 "${q}"`);
 log(`🔖 Trace: ${tracer.traceId}`);

 // ═══ Запуск / подключение браузера ════════════════════════════════════════
 tracer.start('BROWSER_LAUNCH');
 metrics.phaseStart('browser_launch');
 try {
   var page = await ensureBrowser(session, tracer);
   tracer.succeed('BROWSER_LAUNCH', { url: page.url().substring(0, 80) });
   metrics.phaseEnd('browser_launch');
   metrics.snapMemory('after_browser');
 } catch (err) {
   tracer.fail('BROWSER_LAUNCH', err);
   throw err;
 }

 // ═══ Auth check (критично — до отправки промпта) ══════════════════════════
 tracer.start('AUTH_CHECK');
 metrics.phaseStart('auth_check');
 const authOk = await requireAuth(page, tracer, log.bind(null, '\x1b[36m[AUTH]\x1b[0m'));
 metrics.phaseEnd('auth_check');
 metrics.snapMemory('after_auth');
 if (!authOk) {
   tracer.fail('AUTH_CHECK', 'Not authenticated');
   await cleanup();
   throw new Error('AUTH_REQUIRED: Требуется авторизация в DeepSeek. Запусти демон вручную и авторизуйся. Инструкция в auth-check.js');
 }
 tracer.succeed('AUTH_CHECK', { url: page.url() });

 // CDP Interceptor setup (once per page)
 cdpInterceptor = await setupDeepSeekInterceptor(page);
 debugLog("[CDP] Interceptor configured");


 // Если сессия без chatUrl, но страница уже в чате (демон), используем текущий
 // ВАЖНО: не переиспользуем старые чаты от предыдущих сессий — всегда начинаем новый чат
 // чтобы избежать перемешивания контекста между разными запросами
 if (sessionName && !session.chatUrl) {
   try {
     const currentUrl = page.url();
     if (currentUrl.includes('/a/chat/s/')) {
       log(`⚠️ Демон на старом чате (${currentUrl.substring(0, 40)}...), создаём новый`);
       // НЕ устанавливаем session.chatUrl — чтобы needNewChat сработал
     }
   } catch (e) {}
 }

 // Новый чат если запрошено
 // Определяем, нужен ли новый чат
 const needNewChat = !sessionName || newChat || (session && !session.chatUrl);
 if (needNewChat) {
 await startNewChat(page);
 // Ждём завершения навигации, если она произошла
 try { await page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 12000 }).catch(() => {}); } catch {}
 await sleep(150); // чуть быстрее, без потери стабильности
 if (session) {
   session.messageCount = 0;
   session.chatUrl = null;
 }
 }

 tracer.start('COMPOSER_WAIT');
 metrics.phaseStart('composer_wait');
 const composerSel = await waitUntilReady(page);
 tracer.succeed('COMPOSER_WAIT', { selector: composerSel });
 metrics.phaseEnd('composer_wait');
 metrics.snapMemory('after_composer');

 // ═══ Отправка промпта ══════════════════════════════════════════════════════
 tracer.start('PROMPT_SEND');
 metrics.phaseStart('prompt_send');
 const { textBefore } = await sendPrompt(page, composerSel, q);
 tracer.succeed('PROMPT_SEND', { promptLength: q.length });
 metrics.phaseEnd('prompt_send');
 metrics.increment('apiRequests', 1);
 metrics.snapMemory('after_prompt');

 // ═══ Ожидание и извлечение ответа ═══════════════════════════════════════════
 tracer.start('ANSWER_WAIT');
 metrics.phaseStart('answer_wait');
 let result = await waitForAnswer(page, q, textBefore, 600000, tracer, metrics);
 tracer.succeed('ANSWER_WAIT', { selector: result.selector, textLength: result.text.length });
 metrics.phaseEnd('answer_wait');
 metrics.charactersExtracted = result.text.length;
 metrics.answerComplete = !result.incomplete;
 if (result.incomplete) metrics.incompleteReason = result.incompleteReason;
 metrics.snapMemory('after_answer');

 tracer.start('ANSWER_EXTRACT');
 saveCachedSelector(result.selector);
 if (tracer) tracer.succeed('ANSWER_EXTRACT', { selector: result.selector, textLength: result.text.length });
 if (isSession) {
 session.messageCount++;
 session.lastUsed = new Date().toISOString();
 if (!session.created) session.created = session.lastUsed;
 // Сохраняем URL чата для будущего подключения
 session.chatUrl = page.url();
 session.wsEndpoint = browser.wsEndpoint();
 session.browserMode = browserConnectionMode;
 saveSession(sessionName, session);
 log(`📊 Сессия "${sessionName}": ${session.messageCount} сообщений, URL: ${session.chatUrl}`);
 }

 // ═══ Вывод ═══
 log('\n════════════════════════════════════════════');
 if (isSession) {
 log(`ОТВЕТ DeepSeek [сессия: ${sessionName}, #${session.messageCount}]:`);
 } else {
 log('ОТВЕТ DeepSeek:');
 }
 log('════════════════════════════════════════════');
 log(result.text);
 log('════════════════════════════════════════════\n');

 // Статус лимита — пробуем reload + продолжить если сессия
 if (result.text && result.text.length > 8000) {
   log('\n⚠️  СТАТУС: INCOMPLETE_LIMIT_REACHED — пробуем reload + продолжить...');
   if (isSession && session && session.chatUrl) {
     try {
       log('🔄 Перезагружаем страницу для появления кнопки "Продолжить"...');
       await dsPage.reload({ waitUntil: 'networkidle2', timeout: 30000 });
       await sleep(3000);

       // Ищем кнопку продолжения на перезагруженной странице
       const moreText = await handleContinueButton(dsPage, result.text);
       if (moreText && moreText.length > 100) {
         log(`📦 После reload: +${moreText.length - result.text.length} символов → итого ${moreText.length}`);
         result = { selector: 'after-reload', text: moreText };
         // Показываем обновлённый результат
         log('\n════════════════════════════════════════════');
         log(`ОТВЕТ DeepSeek [после продолжения]:`);
         log('════════════════════════════════════════════');
         log(moreText);
         log('════════════════════════════════════════════\n');
       } else {
         log('⚠️  Кнопка "Продолжить" не появилась и после reload');
       }
     } catch (e) {
       log(`⚠️  Reload не помог: ${e.message}`);
     }
   } else {
     log('💡 Для продолжения используйте --session (контекст сохраняется)');
   }
 }

 // ═══ Закрытие ═══
 if (isSession) {
 // Сессионный: НЕ закрываем — держим контекст
 log(`🟢 Сессия "${sessionName}" активна. Браузер открыт.`);
 } else if (shouldClose || !isVisible) {
 // Одиночный: закрываем
 log('🔒 Закрываю...');
 await cleanup();
 } else {
 log('🟢 Браузер открыт.');
 }

 // ═══ Итоговый отчёт ═════════════════════════════════════════════════════════
 tracer.finish();
 metrics.snapMemory('final');
 const summaryData = tracer.summary();
 metrics.printSummary(result.text.length);
 const metricsFile = metrics.save();
 if (metricsFile) log(`📁 Метрики: ${metricsFile}`);
 log(`🔖 Trace ID: ${tracer.traceId}`);
 log('');

 return result;
}

async function handleEndSession() {
 if (!sessionName) { console.error('Укажите --session <имя>'); process.exit(1); }

 const session = loadSession(sessionName);
 log(`\n🛑 Завершаю сессию "${sessionName}" (${session.messageCount} сообщений)`);

 // Попытка подключиться и закрыть
 if (session.wsEndpoint) {
 try {
 browser = await puppeteer.connect({ browserWSEndpoint: session.wsEndpoint });
 const daemonEndpoint = fs.existsSync(DAEMON_ENDPOINT_FILE) ? fs.readFileSync(DAEMON_ENDPOINT_FILE, 'utf8').trim() : '';
 const isDaemonSession = session.browserMode === 'daemon' || (daemonEndpoint && session.wsEndpoint === daemonEndpoint);
 if (isDaemonSession) {
 browser.disconnect();
 log('🔌 Сессия была в daemon-режиме, только отключаемся');
 } else {
 await browser.close();
 log('🔒 Браузер закрыт');
 }
 } catch {
 log('⚠️ Браузер уже закрыт');
 }
 }

 deleteSession(sessionName);
 log(`✅ Сессия "${sessionName}" удалена`);
}

// ─── Сигналы ────────────────────────────────────────────────
process.on('SIGINT', async () => {
 // В сессионном режиме НЕ закрываем браузер при Ctrl+C
 if (sessionName) {
 log('\n⚠️ Ctrl+C. Браузер остаётся (сессия активна). Для закрытия: --end-session');
 } else {
 await cleanup().catch(() => {});
 }
 process.exit(130);
});
process.on('SIGTERM', async () => { await cleanup().catch(() => {}); process.exit(143); });
process.on('unhandledRejection', e => console.error('❌', e));


// ─── Запуск ─────────────────────────────────────────────────
(async () => {
  // Graceful shutdown при непойманных ошибках
  process.on('uncaughtException', async (e) => {
    console.error(`\x1b[31m❌ UNCAUGHT EXCEPTION: ${e.message}\x1b[0m`);
    console.error(e.stack);
    if (dsPage && browser) {
      try {
        const dumpFile = path.join(BASE_DIR, `.diagnostics`, `crash-${Date.now()}.png`);
        require('fs').mkdirSync(path.join(BASE_DIR, '.diagnostics'), { recursive: true });
        await dsPage.screenshot({ path: dumpFile, fullPage: true }).catch(() => {});
        console.error(`📸 Screenshot saved: ${dumpFile}`);
      } catch {}
    }
    await cleanup().catch(() => {});
    process.exit(1);
  });

  try {
    if (endSession) await handleEndSession();
    else await ask(question);
  } catch (e) {
    // Пробуем записать артефакты при ошибке
    if (dsPage) {
      try {
        const diagnosticsDir = path.join(BASE_DIR, '.diagnostics');
        require('fs').mkdirSync(diagnosticsDir, { recursive: true });
        const ts = Date.now();
        await dsPage.screenshot({ path: path.join(diagnosticsDir, `error-${ts}.png`), fullPage: true }).catch(() => {});
        await require('fs').promises.writeFile(
          path.join(diagnosticsDir, `error-${ts}.html`),
          await dsPage.content().catch(() => ''),
          'utf8'
        ).catch(() => {});
        console.error(`\x1b[33m📸 Артефакты ошибки сохранены в .diagnostics/\x1b[0m`);
      } catch {}
    }
    console.error(`\x1b[31m❌ ${e.message}\x1b[0m`);
    if (!sessionName || shouldClose) await cleanup().catch(() => {});
    process.exit(1);
  }
})();