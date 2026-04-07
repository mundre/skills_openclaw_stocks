/**
 * SqliteStorageAdapter
 * 基于 better-sqlite3 的 SQLite 存储实现。
 * 建表语句 + 所有 StorageAdapter 方法的完整实现。
 */
const { StorageAdapter } = require('./StorageAdapter');

let sqlite3 = null;
try {
  sqlite3 = require('better-sqlite3');
} catch {
  // better-sqlite3 not installed — adapter will throw on init()
}

const ROOT = path => require('path').resolve(__dirname, '../..');
const DATA_DIR = path.join(ROOT, 'data');
const DB_PATH = path.join(DATA_DIR, 'db.sqlite');

function ensureDir(dir) {
  require('fs').mkdirSync(dir, { recursive: true });
}

function now() {
  return new Date().toISOString();
}

const SCHEMA = `
CREATE TABLE IF NOT EXISTS documents (
  id TEXT PRIMARY KEY,
  type TEXT DEFAULT 'document',
  title TEXT,
  sourceType TEXT,
  sourceUri TEXT,
  importedAt TEXT,
  status TEXT DEFAULT 'active',
  text TEXT,
  createdAt TEXT,
  updatedAt TEXT
);

CREATE TABLE IF NOT EXISTS fragments (
  id TEXT PRIMARY KEY,
  type TEXT DEFAULT 'fragment',
  documentId TEXT,
  "index" INTEGER,
  text TEXT,
  summary TEXT,
  conceptNames TEXT,
  createdAt TEXT,
  FOREIGN KEY (documentId) REFERENCES documents(id)
);

CREATE TABLE IF NOT EXISTS concepts (
  id TEXT PRIMARY KEY,
  type TEXT DEFAULT 'concept',
  name TEXT,
  normalizedName TEXT UNIQUE,
  salience REAL,
  createdAt TEXT
);

CREATE TABLE IF NOT EXISTS links (
  id TEXT PRIMARY KEY,
  type TEXT,
  fromId TEXT,
  fromType TEXT,
  toId TEXT,
  toType TEXT,
  documentId TEXT,
  score REAL,
  createdAt TEXT,
  FOREIGN KEY (documentId) REFERENCES documents(id)
);

CREATE TABLE IF NOT EXISTS fragment_vectors (
  fragmentId TEXT PRIMARY KEY,
  vector BLOB,
  updatedAt TEXT,
  FOREIGN KEY (fragmentId) REFERENCES fragments(id)
);

CREATE INDEX IF NOT EXISTS idx_fragments_documentId ON fragments(documentId);
CREATE INDEX IF NOT EXISTS idx_links_fromId ON links(fromId);
CREATE INDEX IF NOT EXISTS idx_links_toId ON links(toId);
CREATE INDEX IF NOT EXISTS idx_links_documentId ON links(documentId);
CREATE INDEX IF NOT EXISTS idx_concepts_normalizedName ON concepts(normalizedName);
`;

class SqliteStorageAdapter extends StorageAdapter {
  constructor({ dbPath } = {}) {
    super();
    this._dbPath = dbPath || DB_PATH;
    this._db = null;
  }

  async init() {
    if (!sqlite3) {
      throw new Error('better-sqlite3 is not installed. Run: npm install better-sqlite3');
    }
    ensureDir(require('path').dirname(this._dbPath));
    this._db = sqlite3(this._dbPath);
    this._db.pragma('journal_mode = WAL');
    this._db.exec(SCHEMA);
  }

  _run(sql, params = []) {
    try {
      return this._db.prepare(sql).run(...params);
    } catch (e) {
      throw new Error(`SQLite run error: ${e.message} | sql: ${sql}`);
    }
  }

  _all(sql, params = []) {
    try {
      return this._db.prepare(sql).all(...params);
    } catch (e) {
      throw new Error(`SQLite all error: ${e.message} | sql: ${sql}`);
    }
  }

  _get(sql, params = []) {
    try {
      return this._db.prepare(sql).get(...params);
    } catch (e) {
      throw new Error(`SQLite get error: ${e.message} | sql: ${sql}`);
    }
  }

  // --- Document ---
  async saveDocument(doc) {
    this._run(
      `INSERT OR REPLACE INTO documents (id,type,title,sourceType,sourceUri,importedAt,status,text,createdAt,updatedAt)
       VALUES (?,?,?,?,?,?,?,?,?,?)`,
      [doc.id, doc.type || 'document', doc.title || '', doc.sourceType || '', doc.sourceUri || '',
       doc.importedAt || now(), doc.status || 'active', doc.text || '',
       doc.createdAt || now(), now()]
    );
    return doc;
  }

  async getDocument(id) {
    const row = this._get('SELECT * FROM documents WHERE id = ?', [id]);
    return row ? this._mapDoc(row) : null;
  }

  async listDocuments() {
    return this._all('SELECT * FROM documents ORDER BY importedAt DESC').map(this._mapDoc);
  }

  async deleteDocument(id) {
    this._run('DELETE FROM documents WHERE id = ?', [id]);
  }

  // --- Fragment ---
  async saveFragment(frag) {
    this._run(
      `INSERT OR REPLACE INTO fragments (id,type,documentId,"index",text,summary,conceptNames,createdAt)
       VALUES (?,?,?,?,?,?,?,?)`,
      [frag.id, 'fragment', frag.documentId, frag.index, frag.text, frag.summary || frag.text.slice(0, 100),
       JSON.stringify(frag.conceptNames || []), frag.createdAt || now()]
    );
    return frag;
  }

  async getFragment(id) {
    const row = this._get('SELECT * FROM fragments WHERE id = ?', [id]);
    return row ? this._mapFrag(row) : null;
  }

  async listFragments(documentId) {
    return this._all('SELECT * FROM fragments WHERE documentId = ? ORDER BY "index" ASC', [documentId])
      .map(this._mapFrag);
  }

  async deleteFragmentsByDocument(documentId) {
    this._run('DELETE FROM fragments WHERE documentId = ?', [documentId]);
  }

  async saveFragments(fragments) {
    const stmt = this._db.prepare(
      `INSERT OR REPLACE INTO fragments (id,type,documentId,"index",text,summary,conceptNames,createdAt)
       VALUES (?,?,?,?,?,?,?,?)`
    );
    const insertMany = this._db.transaction((items) => {
      for (const frag of items) {
        stmt.run(frag.id, 'fragment', frag.documentId, frag.index, frag.text,
          frag.summary || frag.text.slice(0, 100), JSON.stringify(frag.conceptNames || []),
          frag.createdAt || now());
      }
    });
    insertMany(fragments);
    return fragments;
  }

  // --- Concept ---
  async saveConcept(concept) {
    this._run(
      `INSERT OR REPLACE INTO concepts (id,type,name,normalizedName,salience,createdAt)
       VALUES (?,?,?,?,?,?)`,
      [concept.id, 'concept', concept.name, concept.normalizedName, concept.salience || 0,
       concept.createdAt || now()]
    );
    return concept;
  }

  async getConcept(id) {
    const row = this._get('SELECT * FROM concepts WHERE id = ?', [id]);
    return row ? this._mapConcept(row) : null;
  }

  async listConcepts() {
    return this._all('SELECT * FROM concepts ORDER BY normalizedName ASC').map(this._mapConcept);
  }

  async upsertConcept(concept) {
    return this.saveConcept(concept);
  }

  async saveConcepts(concepts) {
    const stmt = this._db.prepare(
      `INSERT OR REPLACE INTO concepts (id,type,name,normalizedName,salience,createdAt) VALUES (?,?,?,?,?,?)`
    );
    const insertMany = this._db.transaction((items) => {
      for (const c of items) {
        stmt.run(c.id, 'concept', c.name, c.normalizedName, c.salience || 0, c.createdAt || now());
      }
    });
    insertMany(concepts);
    return concepts;
  }

  // --- Link ---
  async saveLink(link) {
    this._run(
      `INSERT OR REPLACE INTO links (id,type,fromId,fromType,toId,toType,documentId,score,createdAt)
       VALUES (?,?,?,?,?,?,?,?,?)`,
      [link.id, link.type, link.fromId, link.fromType, link.toId, link.toType,
       link.documentId, link.score || 0, link.createdAt || now()]
    );
    return link;
  }

  async getLinks(fromId, toId) {
    let sql = 'SELECT * FROM links WHERE 1=1';
    const params = [];
    if (fromId) { sql += ' AND fromId = ?'; params.push(fromId); }
    if (toId)   { sql += ' AND toId = ?';   params.push(toId); }
    return this._all(sql, params);
  }

  async deleteLinksByDocument(documentId) {
    this._run('DELETE FROM links WHERE documentId = ?', [documentId]);
  }

  async saveLinks(links) {
    const stmt = this._db.prepare(
      `INSERT OR REPLACE INTO links (id,type,fromId,fromType,toId,toType,documentId,score,createdAt)
       VALUES (?,?,?,?,?,?,?,?,?)`
    );
    const insertMany = this._db.transaction((items) => {
      for (const l of items) {
        stmt.run(l.id, l.type, l.fromId, l.fromType, l.toId, l.toType,
          l.documentId, l.score || 0, l.createdAt || now());
      }
    });
    insertMany(links);
    return links;
  }

  // --- Vector ---
  async saveFragmentVector(fragmentId, vector) {
    const buf = Buffer.from(JSON.stringify(vector));
    this._run(
      `INSERT OR REPLACE INTO fragment_vectors (fragmentId,vector,updatedAt) VALUES (?,?,?)`,
      [fragmentId, buf, now()]
    );
  }

  async getFragmentVector(fragmentId) {
    const row = this._get('SELECT vector FROM fragment_vectors WHERE fragmentId = ?', [fragmentId]);
    if (!row) return null;
    return JSON.parse(row.vector);
  }

  async listFragmentVectors() {
    return this._all('SELECT fragmentId, vector FROM fragment_vectors').map((r) => ({
      fragmentId: r.fragmentId,
      vector: JSON.parse(r.vector)
    }));
  }

  // --- Full DB operations (for CLI compat) ---
  async load() {
    const docs = this._all('SELECT * FROM documents ORDER BY importedAt DESC').map(this._mapDoc);
    const frags = this._all('SELECT * FROM fragments ORDER BY "index" ASC').map(this._mapFrag);
    const concepts = this._all('SELECT * FROM concepts ORDER BY normalizedName ASC').map(this._mapConcept);
    const links = this._all('SELECT * FROM links');
    const updatedAt = this._get('SELECT MAX(updatedAt) as t FROM documents UNION ALL SELECT MAX(updatedAt) as t FROM fragments')?.t || new Date().toISOString();
    return { version: 1, documents: docs, fragments: frags, concepts, links, updatedAt };
  }

  async save(db) {
    await this.clear();
    if (db.documents) for (const d of db.documents) await this.saveDocument(d);
    if (db.fragments) for (const f of db.fragments) await this.saveFragment(f);
    if (db.concepts) for (const c of db.concepts) await this.saveConcept(c);
    if (db.links) for (const l of db.links) await this.saveLink(l);
  }

  async close() {
    if (this._db) { this._db.close(); this._db = null; }
  }

  // --- Workspace ---
  async clear() {
    this._run('DELETE FROM fragment_vectors');
    this._run('DELETE FROM links');
    this._run('DELETE FROM fragments');
    this._run('DELETE FROM concepts');
    this._run('DELETE FROM documents');
  }

  getStats() {
    return {
      documents: this._get('SELECT COUNT(*) as n FROM documents')?.n || 0,
      fragments: this._get('SELECT COUNT(*) as n FROM fragments')?.n || 0,
      concepts: this._get('SELECT COUNT(*) as n FROM concepts')?.n || 0,
      links: this._get('SELECT COUNT(*) as n FROM links')?.n || 0,
      dbPath: this._dbPath
    };
  }

  // --- Mappers ---
  _mapDoc(row) {
    return { ...row };
  }

  _mapFrag(row) {
    return { ...row, conceptNames: JSON.parse(row.conceptNames || '[]') };
  }

  _mapConcept(row) {
    return { ...row };
  }
}

module.exports = { SqliteStorageAdapter };
