/**
 * KeywordEmbeddingProvider
 * MVP 版本：基于词项匹配的伪嵌入，用于无外部 API 依赖场景。
 * 后续可替换为真正的 OpenAI/text-embedding-3* provider。
 */
const { EmbeddingProvider } = require('./base');

class KeywordEmbeddingProvider extends EmbeddingProvider {
  constructor(opts = {}) {
    super();
    this._dims = opts.dimensions || 384; // 与 text-embedding-3-small 常用维度兼容
  }

  dimensions() {
    return this._dims;
  }

  /**
   * 简单词袋伪嵌入：基于 term frequency 构建稀疏向量
   * 兼容性接口，实际向量召回走 retriever 的关键词逻辑
   */
  async embed(text) {
    const terms = (text || '')
      .toLowerCase()
      .replace(/[^\w\s\u4e00-\u9fa5]/g, ' ')
      .split(/\s+/)
      .filter(Boolean);

    // 生成确定性伪向量（基于 term hash）
    const vec = new Array(this._dims).fill(0);
    for (const term of terms) {
      const hash = this._hash(term);
      for (let i = 0; i < terms.length; i++) {
        const idx = (hash + i * 31) % this._dims;
        vec[idx] += 1;
      }
    }
    // L2 normalize
    const norm = Math.sqrt(vec.reduce((s, v) => s + v * v, 0));
    return norm > 0 ? vec.map((v) => v / norm) : vec;
  }

  async embedBatch(texts) {
    return Promise.all(texts.map((t) => this.embed(t)));
  }

  _hash(s) {
    let h = 0;
    for (let i = 0; i < s.length; i++) {
      h = ((h << 5) - h + s.charCodeAt(i)) | 0;
    }
    return Math.abs(h);
  }
}

/**
 * OpenAiEmbeddingProvider
 * OpenAI-compatible API 调用桩，后续填入真实 API key 和 endpoint 即可启用。
 */
class OpenAiEmbeddingProvider extends EmbeddingProvider {
  constructor(opts = {}) {
    super();
    this.apiKey = opts.apiKey || process.env.OPENAI_API_KEY;
    this.endpoint = opts.endpoint || 'https://api.openai.com/v1/embeddings';
    this.model = opts.model || 'text-embedding-3-small';
    this.dims = opts.dimensions || 1536;
  }

  dimensions() {
    return this.dims;
  }

  async embed(text) {
    if (!this.apiKey) {
      throw new Error('OPENAI_API_KEY not set. Use --embedding=keyword or set OPENAI_API_KEY.');
    }
    const res = await fetch(this.endpoint, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: this.model,
        input: text,
        dimensions: this.dims
      })
    });
    if (!res.ok) {
      const err = await res.text();
      throw new Error(`OpenAI embedding error ${res.status}: ${err}`);
    }
    const json = await res.json();
    return json.data[0].embedding;
  }

  async embedBatch(texts) {
    if (!this.apiKey) {
      throw new Error('OPENAI_API_KEY not set. Use --embedding=keyword or set OPENAI_API_KEY.');
    }
    const res = await fetch(this.endpoint, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: this.model,
        input: texts,
        dimensions: this.dims
      })
    });
    if (!res.ok) {
      const err = await res.text();
      throw new Error(`OpenAI embedding error ${res.status}: ${err}`);
    }
    const json = await res.json();
    return json.data.map((item) => item.embedding);
  }
}

module.exports = { KeywordEmbeddingProvider, OpenAiEmbeddingProvider };
