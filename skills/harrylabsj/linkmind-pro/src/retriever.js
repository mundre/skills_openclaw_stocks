/**
 * retriever.js
 * 关键词召回 + 向量相似度召回双层检索。
 * ranker：余弦相似度
 * 最终结果 = 关键词召回 ∪ 向量召回 → 去重排序
 */
const { normalizeConcept, STOPWORDS } = require('./utils/nlp');

/**
 * @typedef {Object} RetrievalResult
 * @property {string} fragmentId
 * @property {string} documentId
 * @property {string} documentTitle
 * @property {number} score
 * @property {string} text
 * @property {'keyword'|'vector'|'hybrid'} source
 */

/**
 * 计算余弦相似度
 * @param {number[]} a
 * @param {number[]} b
 */
function cosineSimilarity(a, b) {
  if (a.length !== b.length) return 0;
  let dot = 0, na = 0, nb = 0;
  for (let i = 0; i < a.length; i += 1) {
    dot += a[i] * b[i];
    na += a[i] * a[i];
    nb += b[i] * b[i];
  }
  const denom = Math.sqrt(na) * Math.sqrt(nb);
  return denom === 0 ? 0 : dot / denom;
}

/**
 * 关键词召回（从 fragment 列表）
 */
function keywordSearch(fragments, query, limit = 20) {
  const terms = normalizeConcept(query)
    .split(' ')
    .filter(Boolean)
    .filter((t) => !STOPWORDS.has(t));

  if (terms.length === 0) return [];

  return fragments
    .map((frag) => {
      const textNorm = normalizeConcept(frag.text);
      let score = 0;
      for (const term of terms) {
        if (textNorm.includes(term)) score += 3;
        if ((frag.conceptNames || []).includes(term)) score += 5;
      }
      return { frag, score };
    })
    .filter((item) => item.score > 0)
    .sort((a, b) => b.score - a.score || a.frag.index - b.frag.index)
    .slice(0, limit)
    .map((item) => ({
      fragmentId: item.frag.id,
      documentId: item.frag.documentId,
      documentTitle: item.frag.documentTitle || 'unknown',
      score: item.score,
      text: item.frag.text,
      source: 'keyword'
    }));
}

/**
 * 向量相似度召回
 * @param {object[]} fragments - 带 documentTitle
 * @param {string} query
 * @param {import('./embedding-providers/EmbeddingProvider')} embeddingProvider
 * @param {number} limit
 */
async function vectorSearch(fragments, query, embeddingProvider, limit = 20) {
  if (!embeddingProvider || fragments.length === 0) return [];

  const texts = fragments.map((f) => f.text);
  const [queryVec, fragVecs] = await Promise.all([
    embeddingProvider.embed([query]),
    embeddingProvider.embed(texts)
  ]);

  const qv = queryVec[0];
  return fragments
    .map((frag, i) => ({
      frag,
      sim: cosineSimilarity(qv, fragVecs[i] || [])
    }))
    .filter((item) => item.sim > 0)
    .sort((a, b) => b.sim - a.sim)
    .slice(0, limit)
    .map((item) => ({
      fragmentId: item.frag.id,
      documentId: item.frag.documentId,
      documentTitle: item.frag.documentTitle || 'unknown',
      score: item.sim,
      text: item.frag.text,
      source: 'vector'
    }));
}

/**
 * 合并关键词召回 + 向量召回，去重并排序
 * @param {RetrievalResult[]} keywordResults
 * @param {RetrievalResult[]} vectorResults
 * @param {number} limit
 */
function mergeResults(keywordResults, vectorResults, limit = 10) {
  const seen = new Map();
  for (const r of [...keywordResults, ...vectorResults]) {
    if (!seen.has(r.fragmentId)) {
      seen.set(r.fragmentId, { ...r });
    } else {
      // 取最高分
      const existing = seen.get(r.fragmentId);
      existing.score = Math.max(existing.score, r.score);
      existing.source = existing.source === r.source ? existing.source : 'hybrid';
    }
  }
  return [...seen.values()]
    .sort((a, b) => b.score - a.score)
    .slice(0, limit);
}

/**
 * 主检索入口
 * @param {object} options
 * @param {object[]} options.fragments - fragment 列表，需含 documentTitle
 * @param {string} options.query
 * @param {import('./embedding-providers/EmbeddingProvider')} [options.embeddingProvider]
 * @param {number} [options.limit]
 */
async function retrieve({ fragments, query, embeddingProvider = null, limit = 10 }) {
  const kw = keywordSearch(fragments, query, limit * 2);
  const vec = embeddingProvider
    ? await vectorSearch(fragments, query, embeddingProvider, limit * 2)
    : [];
  return mergeResults(kw, vec, limit);
}

module.exports = {
  keywordSearch,
  vectorSearch,
  mergeResults,
  cosineSimilarity,
  retrieve
};
