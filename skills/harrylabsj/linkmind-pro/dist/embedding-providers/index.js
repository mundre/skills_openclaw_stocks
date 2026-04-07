/**
 * embedding-providers/index.js
 * Factory: 根据配置返回对应的 embedding provider 实例。
 */
const { MockProvider } = require('./MockProvider');
const { OpenAICompatibleProvider } = require('./OpenAICompatibleProvider');

function createEmbeddingProvider(type = 'mock', options = {}) {
  switch (type) {
    case 'mock':
      return new MockProvider(options);
    case 'openai':
      return new OpenAICompatibleProvider(options);
    default:
      throw new Error(`Unknown embedding provider type: ${type}. Use 'mock' or 'openai'.`);
  }
}

module.exports = { createEmbeddingProvider, MockProvider, OpenAICompatibleProvider };
