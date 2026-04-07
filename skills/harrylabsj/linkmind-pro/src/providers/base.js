/**
 * EmbeddingProvider 接口契约
 * 所有 provider 必须实现以下方法：
 *   embed(text)        -> Promise<number[]>        单文本向量
 *   embedBatch(texts)  -> Promise<number[][]>     批量向量
 *   similarity(a, b)   -> number                  余弦相似度
 *   dimensions()       -> number                   向量维度
 */
class EmbeddingProvider {
  async embed(text) {
    throw new Error('Not implemented: embed(text)');
  }
  async embedBatch(texts) {
    throw new Error('Not implemented: embedBatch(texts)');
  }
  similarity(a, b) {
    if (a.length !== b.length) throw new Error('Vector dimensions mismatch');
    let dot = 0, normA = 0, normB = 0;
    for (let i = 0; i < a.length; i++) {
      dot += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }
    return dot / (Math.sqrt(normA) * Math.sqrt(normB) + 1e-10);
  }
  dimensions() {
    throw new Error('Not implemented: dimensions()');
  }
}

module.exports = { EmbeddingProvider };
