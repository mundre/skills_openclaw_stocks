/**
 * StorageAdapter 接口契约
 * 所有 adapter 必须实现以下方法：
 *   load()           -> Promise<WorkspaceDb>
 *   save(db)         -> Promise<void>
 *   clear()          -> Promise<void>
 *   query(fn)        -> Promise<any>  (事务查询)
 *   close()          -> Promise<void>
 */
class StorageAdapter {
  async load() {
    throw new Error('Not implemented: load()');
  }
  async save(db) {
    throw new Error('Not implemented: save(db)');
  }
  async clear() {
    throw new Error('Not implemented: clear()');
  }
  async query(fn) {
    throw new Error('Not implemented: query(fn)');
  }
  async close() {
    throw new Error('Not implemented: close()');
  }
}

module.exports = { StorageAdapter };
