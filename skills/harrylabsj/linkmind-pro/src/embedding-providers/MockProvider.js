/**
 * MockProvider
 * 返回随机向量，用于测试和离线开发。
 */
const { EmbeddingProvider } = require('./EmbeddingProvider');

const DEFAULT_DIM = 1536;

class MockProvider extends EmbeddingProvider {
  constructor({ dimension = DEFAULT_DIM, seed = 42 } = {}) {
    super();
    this._dim = dimension;
    this._seed = seed;
    this._cache = new Map();
  }

  get name() {
    return 'mock';
  }

  get dimension() {
    return this._dim;
  }

  _pseudoRandom(text) {
    let hash = 0;
    for (let i = 0; i < text.length; i += 1) {
      hash = ((hash << 5) - hash + text.charCodeAt(i)) | 0;
    }
    return Math.abs(hash) / 0x7fffffff;
  }

  async embed(texts) {
    return texts.map((text) => {
      if (this._cache.has(text)) return this._cache.get(text);
      const vec = [];
      for (let i = 0; i < this._dim; i += 1) {
        // deterministic random based on text + index
        const base = this._pseudoRandom(text + i);
        vec.push(base);
      }
      // L2 normalize
      const norm = Math.sqrt(vec.reduce((s, v) => s + v * v, 0));
      const normalized = norm > 0 ? vec.map((v) => v / norm) : vec;
      this._cache.set(text, normalized);
      return normalized;
    });
  }
}

module.exports = { MockProvider };
