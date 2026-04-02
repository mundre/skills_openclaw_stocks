/**
 * Metrics Collector
 * Собирает метрики во время выполнения запроса.
 * Используется для отслеживания производительности и выявления проблем.
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

class MetricsCollector {
  constructor(opts = {}) {
    this.traceId = opts.traceId || `metrics-${Date.now()}`;
    this.sessionName = opts.sessionName || null;
    this.promptLength = opts.promptLength || 0;
    
    // Timing
    this.startTime = Date.now();
    this.phases = {};         // phase timings
    this.memorySnapshots = []; // memory at key moments
    
    // Counts
    this.retryCount = 0;
    this.extractionAttempts = 0;
    this.continueRounds = 0;
    this.charactersExtracted = 0;
    this.apiRequests = 0;
    this.cdpEvents = 0;
    
    // Status
    this.answerComplete = false;
    this.incompleteReason = null; // 'rate_limit' | 'timeout' | 'auth' | null
    this.error = null;
    
    // Chrome memory (if available)
    this.chromeMemoryMB = null;
    
    // File output
    this.outputDir = opts.outputDir || null;
    this.metricsFile = null;
    if (this.outputDir) {
      try {
        fs.mkdirSync(this.outputDir, { recursive: true });
      } catch {}
    }
  }

  // ═══ Timing helpers ═══════════════════════════════════════════════════════

  phaseStart(name) {
    this.phases[name] = { start: Date.now(), end: null, duration_ms: null };
  }

  phaseEnd(name, metadata = {}) {
    if (!this.phases[name]) {
      this.phases[name] = { start: Date.now(), end: Date.now(), duration_ms: 0 };
    }
    this.phases[name].end = Date.now();
    this.phases[name].duration_ms = this.phases[name].end - this.phases[name].start;
    Object.assign(this.phases[name], metadata);
  }

  getDuration(name) {
    const p = this.phases[name];
    if (!p) return null;
    if (p.duration_ms !== null) return p.duration_ms;
    if (!p.end) return Date.now() - p.start;
    return p.end - p.start;
  }

  // ═══ Memory tracking ═══════════════════════════════════════════════════════
  
  /**
   * Записывает текущее потребление памяти Node.js
   */
  snapMemory(label = 'manual') {
    const mem = process.memoryUsage();
    const snapshot = {
      label,
      timestamp: Date.now(),
      rss_mb: Math.round(mem.rss / 1024 / 1024),
      heapUsed_mb: Math.round(mem.heapUsed / 1024 / 1024),
      heapTotal_mb: Math.round(mem.heapTotal / 1024 / 1024),
      external_mb: Math.round(mem.external / 1024 / 1024),
    };
    this.memorySnapshots.push(snapshot);
    return snapshot;
  }

  /**
   * Пытается получить память Chrome через heapUsed из performance metrics
   * (Требует CDP session)
   * @param {import('puppeteer').CDPSession} client
   */
  async snapChromeMemory(client) {
    try {
      const metrics = await client.send('Performance.getMetrics');
      const jsHeapUsed = metricValue(metrics, 'JSHeapUsedSize');
      const jsHeapTotal = metricValue(metrics, 'JSHeapTotalSize');
      if (jsHeapUsed) {
        this.chromeMemoryMB = Math.round(jsHeapUsed / 1024 / 1024);
      }
    } catch (e) {}
  }

  // ═══ Counters ═══════════════════════════════════════════════════════════════
  
  increment(key, by = 1) {
    if (!(key in this)) this[key] = 0;
    this[key] += by;
  }

  // ═══ Finalize ═══════════════════════════════════════════════════════════════
  
  /**
   * Возвращает итоговую статистику
   */
  finalize(answerLength = 0) {
    const totalMs = Date.now() - this.startTime;
    const peakMemoryMB = this.memorySnapshots.length > 0
      ? Math.max(...this.memorySnapshots.map(s => s.rss_mb))
      : null;

    return {
      traceId: this.traceId,
      sessionName: this.sessionName,
      promptLength: this.promptLength,
      answerLength,
      totalMs,
      totalSec: Math.round(totalMs / 1000),
      phases: this.phases,
      memory: {
        peakMB: peakMemoryMB,
        snapshots: this.memorySnapshots,
        chromeMB: this.chromeMemoryMB,
      },
      counts: {
        retries: this.retryCount,
        extractionAttempts: this.extractionAttempts,
        continueRounds: this.continueRounds,
        apiRequests: this.apiRequests,
        cdpEvents: this.cdpEvents,
      },
      answerComplete: this.answerComplete,
      incompleteReason: this.incompleteReason,
      error: this.error,
      nodeVersion: process.version,
      platform: os.platform(),
      arch: os.arch(),
      cpuCount: os.cpus().length,
      totalMemoryMB: Math.round(os.totalmem() / 1024 / 1024),
      freeMemoryMB: Math.round(os.freemem() / 1024 / 1024),
    };
  }

  /**
   * Сохраняет метрики в файл
   */
  save() {
    if (!this.outputDir) return;
    try {
      const data = this.finalize(this.charactersExtracted);
      const file = path.join(this.outputDir, `metrics-${this.traceId}.json`);
      fs.writeFileSync(file, JSON.stringify(data, null, 2), 'utf8');
      return file;
    } catch (e) {
      return null;
    }
  }

  /**
   * Печатает компактную сводку
   */
  printSummary(answerLength = 0) {
    const data = this.finalize(answerLength);
    const { counts, memory, totalSec } = data;
    
    console.log('');
    console.log('📊 Метрики:');
    console.log(`   ⏱  Общее время:    ${totalSec}s`);
    if (memory.peakMB) console.log(`   💾 Пик памяти:    ${memory.peakMB}MB (Node)`);
    if (memory.chromeMB) console.log(`   🌐 Chrome heap:   ${memory.chromeMB}MB`);
    console.log(`   📝 Промпт:        ${this.promptLength} символов`);
    console.log(`   📦 Ответ:         ${answerLength} символов`);
    console.log(`   🔄 Продолжений:   ${counts.continueRounds}`);
    console.log(`   🔁 Ретраев:       ${counts.retries}`);
    console.log(`   📥 Попыток экстракта: ${counts.extractionAttempts}`);
    
    // Фазы
    const phaseKeys = Object.keys(this.phases);
    if (phaseKeys.length > 0) {
      console.log('   📍 Этапы:');
      for (const [name, p] of Object.entries(this.phases)) {
        if (p.duration_ms !== null) {
          const ms = p.duration_ms;
          const str = ms < 1000 ? `${ms}ms` : ms < 60000 ? `${(ms/1000).toFixed(1)}s` : `${Math.floor(ms/60000)}m${((ms%60000)/1000).toFixed(0)}s`;
          console.log(`      ${name.padEnd(18)} ${str}`);
        }
      }
    }
    
    if (data.answerComplete) {
      console.log('   ✅ Статус ответа: полный');
    } else if (data.incompleteReason) {
      console.log(`   ⚠️  Статус ответа: неполный (${data.incompleteReason})`);
    }
    
    if (data.error) {
      console.log(`   ❌ Ошибка: ${data.error}`);
    }
  }
}

function metricValue(metrics, name) {
  const m = metrics.metrics?.find(s => s.name === name);
  return m ? Number(m.value) : null;
}

module.exports = { MetricsCollector };
