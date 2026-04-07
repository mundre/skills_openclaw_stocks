#!/usr/bin/env node
/**
 * LinkMind CLI - 知识连接引擎
 * 支持 adapter 切换（json/sqlite）和 embedding 切换（keyword/openai）
 */
const fs = require('fs');
const path = require('path');

const THIS_DIR = __dirname.includes(`${path.sep}dist`) ? __dirname : __dirname;
const IS_DIST = THIS_DIR.includes(`${path.sep}dist`);
const ROOT = IS_DIST ? path.resolve(THIS_DIR, '..') : path.resolve(THIS_DIR, '..');
const DATA_DIR = path.join(ROOT, 'data');

function createEmptyDb() {
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

function stableId(prefix, input) {
  let hash = 0;
  for (let i = 0; i < input.length; i += 1) {
    hash = ((hash << 5) - hash + input.charCodeAt(i)) | 0;
  }
  return `${prefix}_${Math.abs(hash).toString(36)}`;
}

function normalizeConcept(text) {
  return text
    .toLowerCase()
    .replace(/[\u2018\u2019'"""''()（）【】\[\],.:;!?/\\]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

const STOPWORDS = new Set([
  'the','and','for','that','this','with','from','into','your','have','will','not','are','was','were',
  'can','could','should','about','what','when','where','which','while','than','then','them','they',
  'their','there','here','also','more','most','some','such','using','used','use','make','made',
  'over','under','very','just','only','each','been','being','does','did','done','how','why',
  'our','you','its','his','her','she','him','who','has','had','but','too','via','per',
  'one','two','three',
  '我们','你们','他们','这个','那个','一个','一种','可以','需要','如果','因为','所以','以及',
  '进行','通过','没有','不是','就是','如何','什么','为什么','时候','今天','已经','还有',
  '对于','一些','这种','那些','并且','或者','主要','用户','系统','功能','能力','作为'
]);

function extractConcepts(text) {
  const zhMatches = text.match(/[\u4e00-\u9fa5]{2,8}/g) || [];
  const enMatches = text.match(/[A-Za-z][A-Za-z0-9_-]{2,}/g) || [];
  const tokens = [...zhMatches, ...enMatches]
    .map((item) => item.trim())
    .map((item) => ({ raw: item, normalized: normalizeConcept(item) }))
    .filter((item) => item.normalized && !STOPWORDS.has(item.normalized));

  const counts = new Map();
  for (const token of tokens) {
    counts.set(token.normalized, (counts.get(token.normalized) || 0) + 1);
  }

  return [...counts.entries()]
    .map(([normalizedName, count]) => ({
      normalizedName,
      name: tokens.find((item) => item.normalized === normalizedName)?.raw || normalizedName,
      count
    }))
    .sort((a, b) => b.count - a.count || a.normalizedName.localeCompare(b.normalizedName))
    .slice(0, 12);
}

function splitParagraphs(text) {
  return text
    .split(/\n\s*\n+/)
    .map((part) => part.trim())
    .filter(Boolean);
}

function upsertDocument(db, doc) {
  const existingIndex = db.documents.findIndex((item) => item.id === doc.id);
  if (existingIndex >= 0) db.documents[existingIndex] = doc;
  else db.documents.push(doc);
}

function buildForDocument(db, document) {
  const fragmentIds = db.fragments.filter((f) => f.documentId === document.id).map((f) => f.id);
  db.fragments = db.fragments.filter((f) => f.documentId !== document.id);
  db.links = db.links.filter((l) => !fragmentIds.includes(l.fromId) && !fragmentIds.includes(l.toId) && l.documentId !== document.id);

  const usedConceptIds = new Set();
  for (const link of db.links) {
    if (link.toType === 'concept') usedConceptIds.add(link.toId);
    if (link.fromType === 'concept') usedConceptIds.add(link.fromId);
  }
  db.concepts = db.concepts.filter((c) => usedConceptIds.has(c.id));

  const fragments = splitParagraphs(document.text).map((text, index) => ({
    id: stableId('frag', `${document.id}:${index}:${text.slice(0, 80)}`),
    type: 'fragment',
    documentId: document.id,
    index,
    text,
    summary: text.slice(0, 100),
    conceptNames: []
  }));

  const conceptMap = new Map(db.concepts.map((c) => [c.normalizedName, c]));
  const links = [];

  for (const fragment of fragments) {
    const fragmentConcepts = extractConcepts(fragment.text).slice(0, 6);
    fragment.conceptNames = fragmentConcepts.map((item) => item.normalizedName);

    for (const concept of fragmentConcepts) {
      if (!conceptMap.has(concept.normalizedName)) {
        conceptMap.set(concept.normalizedName, {
          id: stableId('concept', concept.normalizedName),
          type: 'concept',
          name: concept.name,
          normalizedName: concept.normalizedName,
          salience: Math.min(1, concept.count / 3)
        });
      }
      const conceptNode = conceptMap.get(concept.normalizedName);
      links.push({
        id: stableId('link', `${fragment.id}->${conceptNode.id}`),
        type: 'mentions',
        fromId: fragment.id,
        fromType: 'fragment',
        toId: conceptNode.id,
        toType: 'concept',
        documentId: document.id,
        score: concept.count
      });
    }
  }

  for (let i = 0; i < fragments.length - 1; i += 1) {
    links.push({
      id: stableId('link', `${fragments[i].id}->${fragments[i + 1].id}`),
      type: 'adjacent',
      fromId: fragments[i].id,
      fromType: 'fragment',
      toId: fragments[i + 1].id,
      toType: 'fragment',
      documentId: document.id,
      score: 0.4
    });
  }

  db.fragments.push(...fragments);
  db.links.push(...links);
  db.concepts = [...conceptMap.values()].sort((a, b) => a.normalizedName.localeCompare(b.normalizedName));

  return { fragmentsCreated: fragments.length, linksCreated: links.length, conceptsTotal: db.concepts.length };
}

async function queryWithEmbedding(adapter, embeddingProvider, q, options = {}) {
  const db = await adapter.load();
  const query = normalizeConcept(q || '');
  if (!query) throw new Error('Query is required');

  const terms = query.split(' ').filter(Boolean);

  let scored = db.fragments.map((fragment) => {
    const textNorm = normalizeConcept(fragment.text);
    let score = 0;
    for (const term of terms) {
      if (textNorm.includes(term)) score += 3;
      if (fragment.conceptNames.includes(term)) score += 5;
    }
    return { fragment, score };
  }).filter((item) => item.score > 0)
    .sort((a, b) => b.score - a.score || a.fragment.index - b.fragment.index)
    .slice(0, Number(options.limit || 3));

  // Vector re-rank if real embedding provider (not KeywordEmbeddingProvider)
  if (embeddingProvider && embeddingProvider.constructor.name !== 'KeywordEmbeddingProvider') {
    try {
      const queryVec = await embeddingProvider.embed(q);
      const fragTexts = scored.length > 0 ? scored.map((s) => s.fragment.text) : db.fragments.slice(0, 20).map((f) => f.text);
      const fragVecs = await embeddingProvider.embedBatch(fragTexts);

      if (fragVecs.length > 0) {
        const scoredWithVec = scored.length > 0
          ? scored.map((s, i) => ({ ...s, vecScore: embeddingProvider.similarity(queryVec, fragVecs[i]) }))
          : db.fragments.slice(0, 20).map((f, i) => ({ fragment: f, score: 0, vecScore: embeddingProvider.similarity(queryVec, fragVecs[i]) }));

        scoredWithVec.forEach((item) => {
          item.blendedScore = item.score * 0.6 + item.vecScore * 10 * 0.4;
        });

        scored = scoredWithVec.sort((a, b) => b.blendedScore - a.blendedScore).slice(0, Number(options.limit || 3));
      }
    } catch {
      // No API key or vector search failed, keep keyword results
    }
  }

  const evidence = scored.map((item) => {
    const doc = db.documents.find((d) => d.id === item.fragment.documentId);
    return {
      fragmentId: item.fragment.id,
      documentId: item.fragment.documentId,
      documentTitle: doc?.title || 'unknown',
      score: item.score || item.vecScore,
      text: item.fragment.text
    };
  });

  const relatedConcepts = [...new Set(scored.flatMap((item) => item.fragment.conceptNames))]
    .map((name) => db.concepts.find((c) => c.normalizedName === name))
    .filter(Boolean)
    .slice(0, 8)
    .map((concept) => ({ id: concept.id, name: concept.name, normalizedName: concept.normalizedName }));

  const answer = evidence.length
    ? `Found ${evidence.length} relevant fragments for "${q}". Top evidence comes from ${[...new Set(evidence.map((item) => item.documentTitle))].join(', ')}.`
    : `No strong match found for "${q}". Try a broader concept or ingest more documents.`;

  return {
    query: q,
    answer,
    evidence,
    relatedConcepts,
    stats: { documents: db.documents.length, fragments: db.fragments.length, concepts: db.concepts.length, links: db.links.length }
  };
}

function parseArgs(argv) {
  const result = { _: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith('--')) {
      result._.push(token);
      continue;
    }
    const [key, inline] = token.slice(2).split('=');
    if (inline !== undefined) {
      result[key] = inline;
      continue;
    }
    const next = argv[i + 1];
    if (!next || next.startsWith('--')) {
      result[key] = true;
    } else {
      result[key] = next;
      i += 1;
    }
  }
  return result;
}

function printHelp() {
  console.log(`LinkMind MVP CLI v0.2.0

Commands:
  ingest --file <path> [--title <title>] [--sourceType <type>] [--storage json|sqlite]
  query --q <text> [--limit <n>] [--embedding keyword|openai]
  status [--storage json|sqlite]
  reset [--storage json|sqlite]
  help

Options:
  --storage <adapter>    Storage: json (default) or sqlite
  --embedding <provider> Embedding: keyword (default) or openai
  --db-path <path>      Custom db path

Examples:
  node dist/index.js ingest --file examples/sample-note.md --title "Sample"
  node dist/index.js query --q "knowledge connector"
  node dist/index.js status --storage sqlite
  node dist/index.js reset --storage sqlite`);
}

async function main() {
  const [, , command, ...rest] = process.argv;
  const args = parseArgs(rest);
  const storageType = args.storage || 'json';
  const embeddingType = args.embedding || 'keyword';
  const dbPathArg = args['db-path'] || undefined;
  let adapter = null;

  try {
    if (!command || command === 'help' || args.help) {
      printHelp();
      return;
    }
    try {
      const adaptersDir = IS_DIST ? 'storage-adapters' : 'src/storage-adapters';
      if (storageType === 'sqlite') {
        const { SqliteStorageAdapter } = require(path.join(THIS_DIR, adaptersDir, 'SqliteStorageAdapter.js'));
        adapter = new SqliteStorageAdapter(dbPathArg ? { dbPath: dbPathArg } : {});
      } else {
        const { JsonStorageAdapter } = require(path.join(THIS_DIR, adaptersDir, 'JsonStorageAdapter.js'));
        adapter = new JsonStorageAdapter(dbPathArg ? { dbPath: dbPathArg } : {});
      }
    } catch (e) {
      if (e.message.includes('sqlite3 not installed')) {
        console.error('[LinkMind] sqlite3 not installed. Run: npm install sqlite3');
      } else {
        console.error(`[LinkMind] Adapter load error: ${e.message}`);
      }
      process.exitCode = 1;
      return;
    }

    let embeddingProvider = null;
    try {
      const providersDir = IS_DIST ? 'embedding-providers' : 'src/embedding-providers';
      const { MockProvider, OpenAICompatibleProvider } = require(path.join(THIS_DIR, providersDir, 'index.js'));
      embeddingProvider = embeddingType === 'openai'
        ? new OpenAICompatibleProvider({ baseURL: process.env.OPENAI_BASE_URL || 'https://api.openai.com/v1', apiKey: process.env.OPENAI_API_KEY || '', model: process.env.OPENAI_MODEL || 'text-embedding-3-small' })
        : new MockProvider();
    } catch {
      embeddingProvider = null;
    }

    const now = () => new Date().toISOString();

    if (command === 'ingest') {
      if (!args.file) throw new Error('--file is required for ingest');
      const full = path.resolve(process.cwd(), args.file);
      if (!fs.existsSync(full)) throw new Error(`File not found: ${full}`);
      const text = fs.readFileSync(full, 'utf8');
      const db = await adapter.load();
      const doc = {
        id: stableId('doc', `${full}:${args.title || path.basename(full)}`),
        type: 'document',
        title: args.title || path.basename(full),
        sourceType: args.sourceType || 'file',
        sourceUri: full,
        importedAt: now(),
        status: 'active',
        text
      };
      upsertDocument(db, doc);
      const stats = buildForDocument(db, doc);
      await adapter.save(db);
      console.log(JSON.stringify({ documentId: doc.id, title: doc.title, ...stats }, null, 2));
      return;
    }

    if (command === 'query') {
      if (!args.q && !args.query) throw new Error('--q is required for query');
      const result = await queryWithEmbedding(adapter, embeddingProvider, args.q || args.query, { limit: args.limit });
      console.log(JSON.stringify(result, null, 2));
      return;
    }

    if (command === 'status') {
      const db = await adapter.load();
      console.log(JSON.stringify({
        documents: db.documents.length,
        fragments: db.fragments.length,
        concepts: db.concepts.length,
        links: db.links.length,
        updatedAt: db.updatedAt,
        adapter: storageType,
        embedding: embeddingType
      }, null, 2));
      return;
    }

    if (command === 'reset') {
      await adapter.clear();
      console.log(JSON.stringify({ ok: true, adapter: storageType }, null, 2));
      return;
    }

    throw new Error(`Unknown command: ${command}`);
  } catch (error) {
    console.error(`[LinkMind] ${error.message}`);
    process.exitCode = 1;
  } finally {
    if (adapter) await adapter.close();
  }
}

if (require.main === module) {
  main();
}

module.exports = {
  buildForDocument,
  extractConcepts,
  splitParagraphs,
  normalizeConcept,
  stableId,
  queryWithEmbedding,
  createEmptyDb
};
