/**
 * storage-adapters/index.js
 * Factory: 根据配置返回对应的 storage adapter 实例。
 */
const { JsonStorageAdapter } = require('./JsonStorageAdapter');
const { SqliteStorageAdapter } = require('./SqliteStorageAdapter');

function createStorageAdapter(type = 'json', options = {}) {
  switch (type) {
    case 'json':
      return new JsonStorageAdapter(options);
    case 'sqlite':
      return new SqliteStorageAdapter(options);
    default:
      throw new Error(`Unknown storage adapter type: ${type}. Use 'json' or 'sqlite'.`);
  }
}

module.exports = { createStorageAdapter, JsonStorageAdapter, SqliteStorageAdapter };
