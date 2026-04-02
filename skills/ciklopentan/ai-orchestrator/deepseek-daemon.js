const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const PROFILE_DIR = path.join(__dirname, '.profile');
const SESSIONS_DIR = path.join(__dirname, '.sessions');
const SESSION_FILE = path.join(SESSIONS_DIR, 'daemon.json');
const DAEMON_ENDPOINT_FILE = path.join(__dirname, '.daemon-ws-endpoint');
const DS_URL = 'https://chat.deepseek.com/';

(async () => {
  console.log('🚀 Запуск DeepSeek Daemon...');
  
  // Создаём директории
  fs.mkdirSync(PROFILE_DIR, { recursive: true });
  fs.mkdirSync(SESSIONS_DIR, { recursive: true });

  // Запускаем браузер
  const browser = await puppeteer.launch({
    headless: 'new',
    userDataDir: PROFILE_DIR,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-blink-features=AutomationControlled',
      '--no-first-run',
      '--no-default-browser-check',
      '--disable-gpu',
      '--window-size=1280,800',
    ],
  });

  const page = (await browser.pages())[0];

  // Сохраняем endpoint сразу, чтобы клиенты могли подключиться пока грузится DeepSeek
  const endpoint = browser.wsEndpoint();
  fs.writeFileSync(DAEMON_ENDPOINT_FILE, endpoint);
  fs.writeFileSync(SESSION_FILE, JSON.stringify({ 
    browserWSEndpoint: endpoint, 
    created: new Date().toISOString() 
  }));
  console.log(`✅ Endpoint готов: ${endpoint}`);
  console.log(`📁 Endpoint file: ${DAEMON_ENDPOINT_FILE}`);
  
  // Переходим на DeepSeek
  await page.goto(DS_URL, { timeout: 60000, waitUntil: 'domcontentloaded' });
  console.log('✅ DeepSeek page loaded');

  // Перезапуск страницы при краше
  page.on('error', async (err) => {
    console.error('⚠️ Страница упала, перезагружаем...', err.message);
    try {
      await page.reload({ waitUntil: 'domcontentloaded', timeout: 30000 });
      console.log('✅ Страница перезагружена');
    } catch (e) {
      console.error('❌ Не удалось перезагрузить страницу:', e.message);
    }
  });

  // Graceful shutdown
  const shutdown = async (signal) => {
    console.log(`\n(System) Получен ${signal}, останавливаю демон...`);
    try {
      await browser.close();
      fs.unlinkSync(DAEMON_ENDPOINT_FILE);
      fs.unlinkSync(SESSION_FILE);
      console.log('✅ Демон остановлен');
    } catch (e) {}
    process.exit(0);
  };

  process.on('SIGTERM', () => shutdown('SIGTERM'));
  process.on('SIGINT', () => shutdown('SIGINT'));
  process.on('SIGHUP', () => shutdown('SIGHUP'));

  // Логируем PID
  console.log(`🆔 PID: ${process.pid}`);
  console.log('💡 Для остановки: kill ' + process.pid);
  console.log('💡 Или: node ' + __filename + ' --stop');
})();
