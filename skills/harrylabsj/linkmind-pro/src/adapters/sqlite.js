/**
 * SqliteStorageAdapter
 * SQLite 存储适配器骨架，表结构与 JSON 格式等效。
 * 事务支持、批量操作能力。
 */
const path = require('path');
const { StorageAdapter } = require('./base');

// sqlite3 为可选依赖，运行时检测
let sqlite3 = null;
try {
  sqlite3 = require('sqlite3');
} catch {
  // sqlite3 不可用，稍后通过 init() 检测并给出明确错误
}

const ROOT = __dirname.includes(`${path.sep}dist`)
  ? path.resolve(__dirname, '../..')
  : path.resolve(__dirname, '../..');
const DATA_DIR = path.resolve(ROOT, 'data');

const SCHEMA = `
CREATE TABLE IF NOT EXISTS documents (
  id TEXT PRIMARY KEY,
  type TEXT DEFAULT 'document',
  title TEXT,
  source_type TEXT,
  source_uri TEXT,
  imported_at TEXT,
  status TEXT DEFAULT 'active',
  text TEXT,
  metadata TEXT
);

CREATE TABLE IF NOT EXISTS fragments (
  id TEXT PRIMARY KEY,
  type TEXT DEFAULT 'fragment',
  document_id TEXT,
  frag_index INTEGER,
  text TEXT,
  summary TEXT,
  concept_names TEXT,
  metadata TEXT,
  FOREIGN KEY (document_id) REFERENCES documents(id)
);

CREATE TABLE IF NOT EXISTS concepts (
  id TEXT PRIMARY KEY,
  type TEXT DEFAULT 'concept',
  name TEXT,
  normalized_name TEXT UNIQUE,
  salience REAL,
  metadata TEXT
);

CREATE TABLE IF NOT EXISTS links (
  id TEXT PRIMARY KEY,
  type TEXT,
  from_id TEXT,
  from_type TEXT,
  to_id TEXT,
  to_type TEXT,
  document_id TEXT,
  score REAL,
  metadata TEXT
);

CREATE INDEX IF NOT EXISTS idx_fragments_document ON fragments(document_id);
CREATE INDEX IF NOT EXISTS idx_links_from ON links(from_id);
CREATE INDEX IF NOT EXISTS idx_links_to ON links(to_id);
CREATE INDEX IF NOT EXISTS idx_concepts_normalized ON concepts(normalized_name);
`;

class SqliteStorageAdapter extends StorageAdapter {
  constructor(opts = {}) {
    super();
    if (!sqlite3) {
      throw new Error('sqlite3 not installed. Run: npm install sqlite3');
    }
    this.dbPath = opts.dbPath || path.join(DATA_DIR, 'workspace.db');
    this._db = null;
  }

  async init() {
    if (this._db) return;
    return new Promise((resolve, reject) => {
      this._db = new sqlite3.Database(this.dbPath, (err) => {
        if (err) return reject(err);
        this._db.exec(SCHEMA, (execErr) => {
          if (execErr) return reject(execErr);
          resolve();
        });
      });
    });
  }

  async load() {
    await this.init();
    return new Promise((resolve, reject) => {
      const docStmt = this._db.prepare('SELECT * FROM documents');
      const fragStmt = this._db.prepare('SELECT * FROM fragments');
      const conceptStmt = this._db.prepare('SELECT * FROM concepts');
      const linkStmt = this._db.prepare('SELECT * FROM links');

      const rows = { documents: [], fragments: [], concepts: [], links: [] };

      const finish = () => {
        // 反序列化 JSON 字段
        rows.fragments = rows.fragments.map((f) => ({
          ...f,
          id: f.id,
          type: 'fragment',
          documentId: f.document_id,
          index: f.frag_index,
          conceptNames: f.concept_names ? JSON.parse(f.concept_names) : []
        }));
        rows.concepts = rows.concepts.map((c) => ({
          ...c,
          type: 'concept',
          normalizedName: c.normalized_name
        }));
        rows.links = rows.links.map((l) => ({
          ...l,
          fromId: l.from_id,
          fromType: l.from_type,
          toId: l.to_id,
          toType: l.to_type,
          documentId: l.document_id
        }));
        resolve(rows);
      };

      let pending = 4;
      const done = () => { if (--pending === 0) finish(); };

      docStmt.all((err, docs) => {
        if (err) { docStmt.close(); return reject(err); }
        rows.documents = docs.map((d) => ({ ...d, type: 'document' }));
        docStmt.close();
        done();
      });
      fragStmt.all((err, frags) => {
        if (err) { fragStmt.close(); return reject(err); }
        rows.fragments = frags;
        fragStmt.close();
        done();
      });
      conceptStmt.all((err, concepts) => {
        if (err) { conceptStmt.close(); return reject(err); }
        rows.concepts = concepts;
        conceptStmt.close();
        done();
      });
      linkStmt.all((err, links) => {
        if (err) { linkStmt.close(); return reject(err); }
        rows.links = links;
        linkStmt.close();
        done();
      });
    });
  }

  async save(rows) {
    await this.init();
    return new Promise((resolve, reject) => {
      this._db.serialize(() => {
        const insertDoc = this._db.prepare(
          'INSERT OR REPLACE INTO documents (id,type,title,source_type,source_uri,imported_at,status,text,metadata) VALUES (?,?,?,?,?,?,?,?,?)'
        );
        const insertFrag = this._db.prepare(
          'INSERT OR REPLACE INTO fragments (id,type,document_id,frag_index,text,summary,concept_names,metadata) VALUES (?,?,?,?,?,?,?,?)'
        );
        const insertConcept = this._db.prepare(
          'INSERT OR REPLACE INTO concepts (id,type,name,normalized_name,salience,metadata) VALUES (?,?,?,?,?,?)'
        );
        const insertLink = this._db.prepare(
          'INSERT OR REPLACE INTO links (id,type,from_id,from_type,to_id,to_type,document_id,score,metadata) VALUES (?,?,?,?,?,?,?,?,?)'
        );

        try {
          for (const d of rows.documents) {
            insertDoc.run(d.id, d.type, d.title, d.sourceType, d.sourceUri, d.importedAt, d.status, d.text, d.metadata ? JSON.stringify(d.metadata) : null);
          }
          for (const f of rows.fragments) {
            insertFrag.run(f.id, f.type, f.documentId, f.index, f.text, f.summary, JSON.stringify(f.conceptNames || []), f.metadata ? JSON.stringify(f.metadata) : null);
          }
          for (const c of rows.concepts) {
            insertConcept.run(c.id, c.type, c.name, c.normalizedName, c.salience, c.metadata ? JSON.stringify(c.metadata) : null);
          }
          for (const l of rows.links) {
            insertLink.run(l.id, l.type, l.fromId, l.fromType, l.toId, l.toType, l.documentId, l.score, l.metadata ? JSON.stringify(l.metadata) : null);
          }
          resolve();
        } catch (err) {
          reject(err);
        } finally {
          insertDoc.close();
          insertFrag.close();
          insertConcept.close();
          insertLink.close();
        }
      });
    });
  }

  async clear() {
    await this.init();
    return new Promise((resolve, reject) => {
      this._db.run('DELETE FROM links; DELETE FROM fragments; DELETE FROM concepts; DELETE FROM documents;', function (err) {
        if (err) return reject(err);
        resolve();
      });
    });
  }

  async query(fn) {
    // 供未来事务查询使用，当前与 load 行为相同
    const db = await this.load();
    return fn(db);
  }

  async close() {
    if (this._db) {
      return new Promise((resolve) => {
        this._db.close(() => resolve());
        this._db = null;
      });
    }
  }
}

module.exports = { SqliteStorageAdapter };
