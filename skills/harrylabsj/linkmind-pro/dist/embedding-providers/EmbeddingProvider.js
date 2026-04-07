/**
 * EmbeddingProvider Interface
 * 所有 embedding provider 必须实现此接口契约。
 */
class EmbeddingProvider {
  /**
   * 将文本列表转为向量
   * @param {string[]} texts
   * @returns {Promise<number[][]>}
   */
  async embed(texts) {
    throw new Error('Not implemented');
  }

  /**
   * 返回 provider 名称
   */
  get name() {
    return 'unknown';
  }

  /**
   * 返回向量维度
   */
  get dimension() {
    throw new Error('Not implemented');
  }
}

module.exports = { EmbeddingProvider };
