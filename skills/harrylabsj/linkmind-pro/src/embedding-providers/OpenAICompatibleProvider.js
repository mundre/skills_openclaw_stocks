/**
 * OpenAICompatibleProvider
 * 调用 OpenAI-compatible API endpoint（如 vLLM、Ollama、Azure OpenAI 等）。
 */
const { EmbeddingProvider } = require('./EmbeddingProvider');

const DEFAULT_DIM = 1536;

class OpenAICompatibleProvider extends EmbeddingProvider {
  constructor({ baseURL = 'https://api.openai.com/v1', apiKey = '', model = 'text-embedding-3-small', dimension = DEFAULT_DIM, batchSize = 100 } = {}) {
    super();
    this._baseURL = baseURL.replace(/\/$/, '');
    this._apiKey = apiKey;
    this._model = model;
    this._dim = dimension;
    this._batchSize = batchSize;
  }

  get name() {
    return `openai-compatible:${this._model}`;
  }

  get dimension() {
    return this._dim;
  }

  async embed(texts) {
    if (!texts || texts.length === 0) return [];
    const results = [];
    for (let i = 0; i < texts.length; i += this._batchSize) {
      const batch = texts.slice(i, i + this._batchSize);
      const vectors = await this._fetchBatch(batch);
      results.push(...vectors);
    }
    return results;
  }

  async _fetchBatch(batch) {
    const url = `${this._baseURL}/embeddings`;
    const body = {
      model: this._model,
      input: batch
    };
    const headers = {
      'Content-Type': 'application/json'
    };
    if (this._apiKey) {
      headers['Authorization'] = `Bearer ${this._apiKey}`;
    }
    const resp = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(body)
    });
    if (!resp.ok) {
      const text = await resp.text().catch(() => '');
      throw new Error(`Embedding API error ${resp.status}: ${text}`);
    }
    const json = await resp.json();
    if (!json.data || !Array.isArray(json.data)) {
      throw new Error(`Unexpected embedding response format`);
    }
    // sort by index to maintain order
    const sorted = json.data.slice().sort((a, b) => a.index - b.index);
    return sorted.map((item) => {
      if (!item.embedding || !Array.isArray(item.embedding)) {
        throw new Error(`Invalid embedding vector in response`);
      }
      return item.embedding;
    });
  }
}

module.exports = { OpenAICompatibleProvider };
