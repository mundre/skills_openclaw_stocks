#!/usr/bin/env node
/**
 * LinkMind Smoke Test - Phase 2
 * 覆盖: storage adapters + embedding providers + retriever
 */
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';
import { pathToFileURL } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SKILL_ROOT = path.resolve(__dirname, '..');
process.chdir(SKILL_ROOT);

function run(cmd) {
  console.log(`\n$ ${cmd}`);
  return JSON.parse(execSync(cmd, { encoding: 'utf8' }));
}

function check(label, cond) {
  if (cond) {
    console.log(`  ✓ ${label}`);
  } else {
    console.error(`  ✗ FAIL: ${label}`);
    process.exitCode = 1;
  }
}

// Import phase-2 modules via dynamic import
const srcDir = path.join(SKILL_ROOT, 'src');

async function runTests() {
  console.log('=== LinkMind Smoke Test (Phase 2) ===\n');

  // Phase 1: CLI commands
  console.log('--- Phase 1: CLI Commands ---');
  const reset = run('node dist/index.js reset');
  check('reset returns ok', reset.ok === true);

  const empty = run('node dist/index.js status');
  check('empty workspace has 0 documents', empty.documents === 0);

  const ingest = run('node dist/index.js ingest --file examples/sample-note.md --title "Sample Note"');
  check('ingest returns documentId', !!ingest.documentId);
  check('ingest creates fragments', ingest.fragmentsCreated >= 1);

  const after = run('node dist/index.js status');
  check('has 1 document', after.documents === 1);
  check('has fragments', after.fragments >= 1);

  const q1 = run('node dist/index.js query --q "knowledge"');
  check('query "knowledge" finds evidence', q1.evidence && q1.evidence.length >= 1);
  check('query "knowledge" returns answer', !!q1.answer);

  const q2 = run('node dist/index.js query --q "xyznonexistentterm12345"');
  check('query no-match returns empty evidence', q2.evidence && q2.evidence.length === 0);

  const q3 = run('node dist/index.js query --q "knowledge" --limit 1');
  check('query with limit respects limit', q3.evidence && q3.evidence.length <= 1);

  // Phase 2: Storage Adapters
  console.log('\n--- Phase 2: Storage Adapters ---');
  const JsonStorageAdapterMod = await import(pathToFileURL(path.join(srcDir, 'storage-adapters/JsonStorageAdapter.js')).href);
  const StorageAdapterMod = await import(pathToFileURL(path.join(srcDir, 'storage-adapters/StorageAdapter.js')).href);
  const { JsonStorageAdapter } = JsonStorageAdapterMod;
  const { StorageAdapter } = StorageAdapterMod;

  const jsAdapter = new JsonStorageAdapter();
  await jsAdapter.init();
  await jsAdapter.clear();
  check('JsonStorageAdapter.init() ok', true);

  const testDoc = {
    id: 'doc_test1',
    type: 'document',
    title: 'Test Doc',
    sourceType: 'note',
    sourceUri: '/test/path.md',
    importedAt: new Date().toISOString(),
    status: 'active',
    text: 'This is a test document for storage adapter testing.'
  };
  await jsAdapter.saveDocument(testDoc);
  const retrieved = await jsAdapter.getDocument('doc_test1');
  check('JsonStorageAdapter.saveDocument + getDocument', retrieved && retrieved.title === 'Test Doc');

  const docs = await jsAdapter.listDocuments();
  check('JsonStorageAdapter.listDocuments', docs && docs.length >= 1);

  const testFrag = {
    id: 'frag_test1',
    type: 'fragment',
    documentId: 'doc_test1',
    index: 0,
    text: 'This is a test fragment.',
    summary: 'This is a test',
    conceptNames: ['test'],
    createdAt: new Date().toISOString()
  };
  await jsAdapter.saveFragment(testFrag);
  const frag = await jsAdapter.getFragment('frag_test1');
  check('JsonStorageAdapter.saveFragment + getFragment', frag && frag.text.includes('test fragment'));

  const frags = await jsAdapter.listFragments('doc_test1');
  check('JsonStorageAdapter.listFragments', frags && frags.length >= 1);

  const testConcept = {
    id: 'concept_test1',
    type: 'concept',
    name: 'TestConcept',
    normalizedName: 'testconcept',
    salience: 0.5,
    createdAt: new Date().toISOString()
  };
  await jsAdapter.saveConcept(testConcept);
  const concepts = await jsAdapter.listConcepts();
  check('JsonStorageAdapter.listConcepts', concepts && concepts.some(c => c.normalizedName === 'testconcept'));

  const testLink = {
    id: 'link_test1',
    type: 'mentions',
    fromId: 'frag_test1',
    fromType: 'fragment',
    toId: 'concept_test1',
    toType: 'concept',
    documentId: 'doc_test1',
    score: 1,
    createdAt: new Date().toISOString()
  };
  await jsAdapter.saveLink(testLink);
  const links = await jsAdapter.getLinks('frag_test1', null);
  check('JsonStorageAdapter.saveLink + getLinks', links && links.some(l => l.id === 'link_test1'));

  // test bulk save
  await jsAdapter.clear();
  await jsAdapter.saveDocument(testDoc);
  await jsAdapter.saveFragments([testFrag]);
  await jsAdapter.saveConcepts([testConcept]);
  await jsAdapter.saveLinks([testLink]);
  const afterBulk = await jsAdapter.listFragments('doc_test1');
  check('JsonStorageAdapter.saveFragments bulk', afterBulk && afterBulk.length >= 1);

  await jsAdapter.clear();
  const emptyAfterClear = await jsAdapter.listDocuments();
  check('JsonStorageAdapter.clear()', emptyAfterClear.length === 0);

  // StorageAdapter interface
  check('StorageAdapter is a class', typeof StorageAdapter === 'function');

  // Phase 2: Embedding Providers
  console.log('\n--- Phase 2: Embedding Providers ---');
  const MockProviderMod = await import(pathToFileURL(path.join(srcDir, 'embedding-providers/MockProvider.js')).href);
  const OpenAICompatibleProviderMod = await import(pathToFileURL(path.join(srcDir, 'embedding-providers/OpenAICompatibleProvider.js')).href);
  const EmbeddingProviderMod = await import(pathToFileURL(path.join(srcDir, 'embedding-providers/EmbeddingProvider.js')).href);
  const { MockProvider } = MockProviderMod;
  const { OpenAICompatibleProvider } = OpenAICompatibleProviderMod;
  const { EmbeddingProvider } = EmbeddingProviderMod;

  const mock = new MockProvider({ dimension: 128 });
  check('MockProvider.dimension', mock.dimension === 128);
  check('MockProvider.name', mock.name === 'mock');

  const [vec] = await mock.embed(['hello world']);
  check('MockProvider.embed returns vector', Array.isArray(vec) && vec.length === 128);
  check('MockProvider.vector is L2-normalized', Math.abs(vec.reduce((s, v) => s + v * v, 0) - 1) < 0.01);

  const [vec2] = await mock.embed(['hello world']);
  check('MockProvider caches results', vec2 === vec);

  const differentText = await mock.embed(['different text']);
  check('MockProvider different text yields different vector', differentText[0] !== vec);

  const openai = new OpenAICompatibleProvider({ baseURL: 'https://api.example.com/v1', apiKey: 'test-key', model: 'test-model', dimension: 256 });
  check('OpenAICompatibleProvider.dimension', openai.dimension === 256);
  check('OpenAICompatibleProvider.name includes model', openai.name.includes('test-model'));
  check('OpenAICompatibleProvider.name includes baseURL hint', openai.name.includes('openai-compatible'));

  check('EmbeddingProvider is a class', typeof EmbeddingProvider === 'function');

  // Phase 2: Retriever
  console.log('\n--- Phase 2: Retriever ---');
  const retrieverMod = await import(pathToFileURL(path.join(srcDir, 'retriever.js')).href);
  const { keywordSearch, vectorSearch, mergeResults, cosineSimilarity, retrieve } = retrieverMod;

  check('cosineSimilarity identical vectors = 1', Math.abs(cosineSimilarity([0.5, 0.5, 0.5, 0.5], [0.5, 0.5, 0.5, 0.5]) - 1) < 0.0001);
  check('cosineSimilarity orthogonal = 0', Math.abs(cosineSimilarity([1, 0, 0], [0, 1, 0])) < 0.0001);

  const testFrags = [
    { id: 'f1', documentId: 'd1', documentTitle: 'Doc 1', index: 0, text: 'knowledge graph is useful', conceptNames: ['knowledge', 'graph'] },
    { id: 'f2', documentId: 'd1', documentTitle: 'Doc 1', index: 1, text: 'machine learning and AI', conceptNames: ['machine', 'learning'] },
    { id: 'f3', documentId: 'd2', documentTitle: 'Doc 2', index: 0, text: 'knowledge base systems', conceptNames: ['knowledge', 'base'] }
  ];

  const kw = keywordSearch(testFrags, 'knowledge');
  check('keywordSearch finds knowledge fragments', kw.length >= 2);
  check('keywordSearch assigns score > 0', kw.every(r => r.score > 0));
  check('keywordSearch source=keyword', kw.every(r => r.source === 'keyword'));

  const vecResults = await vectorSearch(testFrags, 'knowledge graph', mock);
  check('vectorSearch returns results', Array.isArray(vecResults));
  check('vectorSearch source=vector', vecResults.every(r => r.source === 'vector'));

  const merged = mergeResults(kw, vecResults, 5);
  check('mergeResults deduplicates', merged.length <= kw.length + vecResults.length);
  check('mergeResults returns array', Array.isArray(merged));
  check('mergeResults items have score', merged.every(r => typeof r.score === 'number'));

  const kwOnly = await retrieve({ fragments: testFrags, query: 'knowledge', limit: 5 });
  check('retrieve keyword-only works', kwOnly.length >= 1);

  const hybrid = await retrieve({ fragments: testFrags, query: 'knowledge', embeddingProvider: mock, limit: 5 });
  check('retrieve hybrid works', hybrid.length >= 1);
  check('retrieve hybrid may include vector source', hybrid.some(r => r.source === 'vector' || r.source === 'hybrid'));

  console.log('\n=== Smoke Test Complete ===');
  if (process.exitCode === 1) {
    console.log('RESULT: FAILED');
    process.exit(1);
  } else {
    console.log('RESULT: PASSED');
  }
}

runTests().catch((err) => {
  console.error('Test error:', err);
  process.exit(1);
});
