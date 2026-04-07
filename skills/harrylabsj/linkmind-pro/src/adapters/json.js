/**
 * JsonStorageAdapter
 * 保持现有 JSON 文件行为，完全兼容旧数据格式。
 */
const fs = require('fs');
const path = require('path');
const { StorageAdapter } = require('./base');

const ROOT = __dirname.includes(`${path.sep}dist`)
  ? path.resolve(__dirname, '../..')
  : path.resolve(__dirname, '../..');
const DATA_DIR = path.join(ROOT, 'data');
const DB_PATH = path.join(DATA_DIR, 'workspace.json');

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

class JsonStorageAdapter extends StorageAdapter {
  constructor(opts = {}) {
    super();
    this.dbPath = opts.dbPath || DB_PATH;
    this.dataDir = opts.dataDir || DATA_DIR;
  }

  _createEmpty() {
    return {
      version: 1,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      documents: [],
      fragments: [],
      concepts: [],
      links: []
    };
  }

  async load() {
    ensureDir(this.dataDir);
    if (!fs.existsSync(this.dbPath)) {
      const empty = this._createEmpty();
      await this.save(empty);
      return empty;
    }
    return JSON.parse(fs.readFileSync(this.dbPath, 'utf8'));
  }

  async save(db) {
    db.updatedAt = new Date().toISOString();
    ensureDir(this.dataDir);
    fs.writeFileSync(this.dbPath, JSON.stringify(db, null, 2), 'utf8');
  }

  async clear() {
    await this.save(this._createEmpty());
  }

  async query(fn) {
    // JSON adapter 不需要事务，直接执行
    const db = await this.load();
    return fn(db);
  }

  async close() {
    // 无需关闭
  }

  dbPath() {
    return this.dbPath;
  }
}

module.exports = { JsonStorageAdapter };
