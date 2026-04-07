/**
 * JsonStorageAdapter
 * 基于本地 JSON 文件的存储实现，保持向后兼容。
 */
const fs = require('fs');
const path = require('path');

const { StorageAdapter } = require('./StorageAdapter');

const ROOT = path.resolve(__dirname, '../..');
const DATA_DIR = path.join(ROOT, 'data');
const DB_PATH = path.join(DATA_DIR, 'workspace.json');

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function now() {
  return new Date().toISOString();
}

class JsonStorageAdapter extends StorageAdapter {
  constructor() {
    super();
    this._db = null;
  }

  _loadDb() {
    ensureDir(DATA_DIR);
    if (!fs.existsSync(DB_PATH)) {
      const empty = this._emptyDb();
      this._saveDb(empty);
      return empty;
    }
    return JSON.parse(fs.readFileSync(DB_PATH, 'utf8'));
  }

  _saveDb(db) {
    db.updatedAt = now();
    ensureDir(DATA_DIR);
    fs.writeFileSync(DB_PATH, JSON.stringify(db, null, 2), 'utf8');
  }

  _emptyDb() {
    return { version: 1, createdAt: now(), updatedAt: now(), documents: [], fragments: [], concepts: [], links: [] };
  }

  async init() {
    this._db = this._loadDb();
  }

  // --- Document ---
  async saveDocument(doc) {
    const db = this._loadDb();
    const idx = db.documents.findIndex((d) => d.id === doc.id);
    if (idx >= 0) db.documents[idx] = doc;
    else db.documents.push(doc);
    this._saveDb(db);
    return doc;
  }

  async getDocument(id) {
    const db = this._loadDb();
    return db.documents.find((d) => d.id === id) || null;
  }

  async listDocuments() {
    const db = this._loadDb();
    return db.documents;
  }

  async deleteDocument(id) {
    const db = this._loadDb();
    db.documents = db.documents.filter((d) => d.id !== id);
    this._saveDb(db);
  }

  // --- Fragment ---
  async saveFragment(frag) {
    const db = this._loadDb();
    const idx = db.fragments.findIndex((f) => f.id === frag.id);
    if (idx >= 0) db.fragments[idx] = frag;
    else db.fragments.push(frag);
    this._saveDb(db);
    return frag;
  }

  async getFragment(id) {
    const db = this._loadDb();
    return db.fragments.find((f) => f.id === id) || null;
  }

  async listFragments(documentId) {
    const db = this._loadDb();
    return db.fragments.filter((f) => f.documentId === documentId);
  }

  async deleteFragmentsByDocument(documentId) {
    const db = this._loadDb();
    db.fragments = db.fragments.filter((f) => f.documentId !== documentId);
    this._saveDb(db);
  }

  async saveFragments(fragments) {
    const db = this._loadDb();
    for (const frag of fragments) {
      const idx = db.fragments.findIndex((f) => f.id === frag.id);
      if (idx >= 0) db.fragments[idx] = frag;
      else db.fragments.push(frag);
    }
    this._saveDb(db);
  }

  // --- Concept ---
  async saveConcept(concept) {
    const db = this._loadDb();
    const idx = db.concepts.findIndex((c) => c.id === concept.id);
    if (idx >= 0) db.concepts[idx] = concept;
    else db.concepts.push(concept);
    this._saveDb(db);
    return concept;
  }

  async getConcept(id) {
    const db = this._loadDb();
    return db.concepts.find((c) => c.id === id) || null;
  }

  async listConcepts() {
    const db = this._loadDb();
    return db.concepts;
  }

  async upsertConcept(concept) {
    const db = this._loadDb();
    const idx = db.concepts.findIndex((c) => c.id === concept.id);
    if (idx >= 0) db.concepts[idx] = concept;
    else db.concepts.push(concept);
    this._saveDb(db);
    return concept;
  }

  async saveConcepts(concepts) {
    const db = this._loadDb();
    for (const c of concepts) {
      const idx = db.concepts.findIndex((x) => x.id === c.id);
      if (idx >= 0) db.concepts[idx] = c;
      else db.concepts.push(c);
    }
    this._saveDb(db);
  }

  // --- Link ---
  async saveLink(link) {
    const db = this._loadDb();
    const idx = db.links.findIndex((l) => l.id === link.id);
    if (idx >= 0) db.links[idx] = link;
    else db.links.push(link);
    this._saveDb(db);
    return link;
  }

  async getLinks(fromId, toId) {
    const db = this._loadDb();
    return db.links.filter(
      (l) => (fromId ? l.fromId === fromId : true) && (toId ? l.toId === toId : true)
    );
  }

  async deleteLinksByDocument(documentId) {
    const db = this._loadDb();
    db.links = db.links.filter((l) => l.documentId !== documentId);
    this._saveDb(db);
  }

  async saveLinks(links) {
    const db = this._loadDb();
    for (const l of links) {
      const idx = db.links.findIndex((x) => x.id === l.id);
      if (idx >= 0) db.links[idx] = l;
      else db.links.push(l);
    }
    this._saveDb(db);
  }

  // --- Full DB operations (for CLI compat) ---
  async load() {
    return this._loadDb();
  }

  async save(db) {
    this._saveDb(db);
  }

  async close() {
    // no-op for JSON
  }

  // --- Workspace ---
  async clear() {
    this._saveDb(this._emptyDb());
  }

  // --- Stats ---
  getStats() {
    const db = this._loadDb();
    return {
      documents: db.documents.length,
      fragments: db.fragments.length,
      concepts: db.concepts.length,
      links: db.links.length,
      updatedAt: db.updatedAt,
      dbPath: DB_PATH
    };
  }
}

module.exports = { JsonStorageAdapter };
