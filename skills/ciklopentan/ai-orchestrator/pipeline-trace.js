#!/usr/bin/env node
/**
 * Structured Pipeline Trace System
 * Единая система трассировки для всех этапов ask-puppeteer.js
 * 
 * Каждый этап логируется с:
 *   - timestamp (ISO)
 *   - phase (enum)
 *   - duration_ms (если завершён)
 *   - status: started|running|succeeded|failed|skipped
 *   - metadata (произвольные данные)
 * 
 * Output: stdout (цветной) + JSONL файл (для анализа)
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// ═══ Phase definitions ═══════════════════════════════════════════════════
const PHASES = {
  INIT:             { id: 'init',             label: 'Инициализация',        color: '\x1b[36m' },
  BROWSER_LAUNCH:   { id: 'browser_launch',   label: 'Запуск браузера',      color: '\x1b[35m' },
  DAEMON_CONNECT:   { id: 'daemon_connect',   label: 'Подключение к демону', color: '\x1b[34m' },
  SESSION_RESTORE:  { id: 'session_restore',  label: 'Восстановление сессии',color: '\x1b[33m' },
  PAGE_NAVIGATE:    { id: 'page_navigate',     label: 'Навигация',           color: '\x1b[35m' },
  AUTH_CHECK:       { id: 'auth_check',        label: 'Проверка авторизации', color: '\x1b[31m' },
  NEW_CHAT:         { id: 'new_chat',           label: 'Новый чат',           color: '\x1b[33m' },
  COMPOSER_WAIT:    { id: 'composer_wait',     label: 'Ожидание composer',  color: '\x1b[34m' },
  PROMPT_SEND:      { id: 'prompt_send',        label: 'Отправка промпта',   color: '\x1b[32m' },
  API_STREAM:       { id: 'api_stream',         label: 'API стрим',          color: '\x1b[32m' },
  ANSWER_WAIT:      { id: 'answer_wait',        label: 'Ожидание ответа',    color: '\x1b[36m' },
  ANSWER_EXTRACT:   { id: 'answer_extract',     label: 'Извлечение ответа',  color: '\x1b[32m' },
  CONTINUE:         { id: 'continue',            label: 'Продолжение',       color: '\x1b[33m' },
  FINAL:            { id: 'final',               label: 'Завершение',         color: '\x1b[37m' },
};

// ═══ Trace state ═══════════════════════════════════════════════════════════
class PipelineTrace {
  constructor(opts = {}) {
    this.traceId = opts.traceId || generateId('tr');
    this.sessionName = opts.sessionName || null;
    this.promptPreview = opts.promptPreview || '';
    this.phases = {};         // phaseId → { start, end, status, metadata }
    this.events = [];          // raw events for JSONL
    this.logLines = [];       // collected stdout lines for summary
    this.error = null;
    this.startTime = Date.now();
    
    // JSONL log file
    this.logDir = opts.logDir || null;
    this.jsonlFile = null;
    if (this.logDir) {
      try {
        fs.mkdirSync(this.logDir, { recursive: true });
        this.jsonlFile = path.join(this.logDir, `trace-${this.traceId}.jsonl`);
      } catch (e) {}
    }
    
    this.RESET = '\x1b[0m';
    this._setupConsole();
  }

  _setupConsole() {
    // Перехватываем console.log для сбора в logLines
    this._origLog = console.log;
    const self = this;
    console.log = (...args) => {
      const line = args.map(a => String(a)).join(' ');
      self.logLines.push(line);
      self._origLog.apply(console, args);
    };
  }

  _restoreConsole() {
    console.log = this._origLog;
  }

  // ═══ Phase management ════════════════════════════════════════════════════
  
  /**
   * Начать этап
   * @param {string} phaseId - ключ из PHASES
   * @param {Object} metadata - дополнительные данные
   */
  start(phaseId, metadata = {}) {
    const phase = PHASES[phaseId];
    if (!phase) {
      this._log('WARN', `Unknown phase: ${phaseId}`);
      return;
    }
    
    this.phases[phaseId] = {
      phaseId,
      label: phase.label,
      status: 'running',
      start: Date.now(),
      end: null,
      duration_ms: null,
      metadata,
    };
    
    this._emit(phaseId, 'started', metadata);
    this._logPhase(phase, '⏳', `Начат: ${phase.label}`);
  }

  /**
   * Завершить этап успешно
   * @param {string} phaseId
   * @param {Object} metadata - результаты этапа
   */
  succeed(phaseId, metadata = {}) {
    const record = this.phases[phaseId];
    if (!record) {
      this._log('WARN', `succeed() for unknown phase: ${phaseId}`);
      return;
    }
    
    record.status = 'succeeded';
    record.end = Date.now();
    record.duration_ms = record.end - record.start;
    Object.assign(record.metadata, metadata);
    
    this._emit(phaseId, 'succeeded', metadata);
    const phase = PHASES[phaseId];
    const dur = this._formatDuration(record.duration_ms);
    this._logPhase(phase, '✅', `Завершён: ${phase.label} (${dur})`, metadata);
  }

  /**
   * Завершить этап с ошибкой
   * @param {string} phaseId
   * @param {Error|string} err
   * @param {Object} metadata
   */
  fail(phaseId, err, metadata = {}) {
    const record = this.phases[phaseId];
    const phase = PHASES[phaseId];
    
    const errMsg = err instanceof Error ? err.message : String(err);
    if (record) {
      record.status = 'failed';
      record.end = Date.now();
      record.duration_ms = record.end - record.start;
      record.error = errMsg;
      Object.assign(record.metadata, metadata);
    }
    
    this._emit(phaseId, 'failed', { error: errMsg, ...metadata });
    this._logPhase(phase, '❌', `ОШИБКА [${phase.label}]: ${errMsg}`, metadata);
    
    // Сохраняем первую ошибку
    if (!this.error) {
      this.error = { phaseId, phaseLabel: phase?.label, message: errMsg };
    }
  }

  /**
   * Пропустить этап
   * @param {string} phaseId
   * @param {string} reason
   */
  skip(phaseId, reason = '') {
    const record = this.phases[phaseId];
    const phase = PHASES[phaseId];
    if (record) {
      record.status = 'skipped';
      record.end = Date.now();
      record.duration_ms = record.end - record.start;
    }
    
    this._emit(phaseId, 'skipped', { reason });
    this._logPhase(phase, '⏭', `Пропущен: ${phase.label}${reason ? ` (${reason})` : ''}`);
  }

  /**
   * Обновить metadata этапа (для long-running этапов)
   * @param {string} phaseId
   * @param {Object} metadata
   */
  update(phaseId, metadata) {
    const record = this.phases[phaseId];
    if (record) {
      Object.assign(record.metadata, metadata);
      this._emit(phaseId, 'running', metadata);
    }
  }

  // ═══ Event emission ═══════════════════════════════════════════════════════
  
  _emit(phaseId, status, metadata = {}) {
    const event = {
      traceId: this.traceId,
      timestamp: new Date().toISOString(),
      phaseId,
      status,
      duration_ms: this.phases[phaseId] ? (Date.now() - this.phases[phaseId].start) : null,
      sessionName: this.sessionName,
      promptPreview: this.promptPreview,
      metadata,
    };
    this.events.push(event);
    
    // Write to JSONL immediately (append)
    if (this.jsonlFile) {
      try {
        fs.appendFileSync(this.jsonlFile, JSON.stringify(event) + '\n', 'utf8');
      } catch (e) {}
    }
  }

  // ═══ Logging ═════════════════════════════════════════════════════════════
  
  _log(level, ...args) {
    const prefix = {
      INFO: '\x1b[34m[INFO]\x1b[0m',
      WARN: '\x1b[33m[WARN]\x1b[0m',
      ERROR: '\x1b[31m[ERROR]\x1b[0m',
    }[level] || '';
    this._origLog(`${prefix} ${args.join(' ')}`);
  }

  _logPhase(phase, icon, message, metadata = {}) {
    const color = phase?.color || '\x1b[37m';
    const meta = Object.keys(metadata).length > 0
      ? ` ${JSON.stringify(metadata)}`
      : '';
    this._origLog(`${color}${icon} [${phase?.label || '???'}]${this.RESET} ${message}${meta}`);
  }

  _formatDuration(ms) {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${Math.floor(ms / 60000)}m ${((ms % 60000) / 1000).toFixed(0)}s`;
  }

  // ═══ Summary report ═══════════════════════════════════════════════════════
  
  /**
   * Печатает итоговый отчёт и возвращает статистику
   */
  summary() {
    const totalMs = Date.now() - this.startTime;
    const phases = Object.values(this.phases);
    
    this._restoreConsole();
    
    console.log('\n' + '═'.repeat(70));
    console.log(`📊 TRACER REPORT [${this.traceId}]`);
    console.log('═'.repeat(70));
    console.log(`⏱  Общее время:     ${this._formatDuration(totalMs)}`);
    console.log(`🔤 Промпт:          ${this.promptPreview.substring(0, 60)}${this.promptPreview.length > 60 ? '...' : ''}`);
    if (this.sessionName) console.log(`🔄 Сессия:          ${this.sessionName}`);
    console.log('');
    console.log('📍 Этапы:');
    
    for (const [id, phase] of Object.entries(PHASES)) {
      const record = this.phases[id];
      if (!record && id === 'INIT') {
        // init всегда есть
      }
      if (!record) continue;
      
      const icon = record.status === 'succeeded' ? '✅'
        : record.status === 'failed' ? '❌'
        : record.status === 'running' ? '⏳'
        : '⏭';
      const color = record.status === 'succeeded' ? '\x1b[32m'
        : record.status === 'failed' ? '\x1b[31m'
        : '\x1b[33m';
      const dur = record.duration_ms ? this._formatDuration(record.duration_ms) : '—';
      const meta = Object.keys(record.metadata || {}).length > 0
        ? ` ${JSON.stringify(record.metadata)}`
        : '';
      
      console.log(`  ${icon} ${phase.label.padEnd(22)} ${color}${dur.padEnd(10)}${this.RESET} ${record.status}${meta}`);
    }
    
    console.log('');
    if (this.error) {
      console.log(`❌ Ошибка: [${this.error.phaseLabel}] ${this.error.message}`);
    } else {
      console.log('✅ Все этапы пройдены без ошибок');
    }
    
    // Размер ответа
    const extractPhase = this.phases['answer_extract'];
    if (extractPhase?.metadata?.answerLength) {
      console.log(`📦 Ответ:           ${extractPhase.metadata.answerLength} символов`);
    }
    
    console.log('═'.repeat(70));
    
    // Пишем в файл summary
    if (this.logDir) {
      try {
        const summaryFile = path.join(this.logDir, `summary-${this.traceId}.json`);
        const summary = {
          traceId: this.traceId,
          totalMs,
          promptPreview: this.promptPreview,
          sessionName: this.sessionName,
          error: this.error,
          phases: this.phases,
          logLines: this.logLines,
        };
        fs.writeFileSync(summaryFile, JSON.stringify(summary, null, 2), 'utf8');
      } catch (e) {}
    }
    
    return {
      traceId: this.traceId,
      totalMs,
      error: this.error,
      phases: this.phases,
    };
  }

  /**
   * Принудительно восстановить console после завершения
   */
  finish() {
    this._restoreConsole();
  }
}

// ═══ Utilities ═══════════════════════════════════════════════════════════════
function generateId(prefix = 'id') {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
}

module.exports = { PipelineTrace, PHASES, generateId };
