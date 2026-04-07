/**
 * StorageAdapter Interface
 * 所有 storage adapter 必须实现此接口契约。
 */
class StorageAdapter {
  /**
   * @returns {Promise<void>}
   */
  async init() {
    throw new Error('Not implemented');
  }

  // --- Document ---
  async saveDocument(doc) {
    throw new Error('Not implemented');
  }
  async getDocument(id) {
    throw new Error('Not implemented');
  }
  async listDocuments() {
    throw new Error('Not implemented');
  }
  async deleteDocument(id) {
    throw new Error('Not implemented');
  }

  // --- Fragment ---
  async saveFragment(frag) {
    throw new Error('Not implemented');
  }
  async getFragment(id) {
    throw new Error('Not implemented');
  }
  async listFragments(documentId) {
    throw new Error('Not implemented');
  }
  async deleteFragmentsByDocument(documentId) {
    throw new Error('Not implemented');
  }

  // --- Concept ---
  async saveConcept(concept) {
    throw new Error('Not implemented');
  }
  async getConcept(id) {
    throw new Error('Not implemented');
  }
  async listConcepts() {
    throw new Error('Not implemented');
  }
  async upsertConcept(concept) {
    throw new Error('Not implemented');
  }

  // --- Link ---
  async saveLink(link) {
    throw new Error('Not implemented');
  }
  async getLinks(fromId, toId) {
    throw new Error('Not implemented');
  }
  async deleteLinksByDocument(documentId) {
    throw new Error('Not implemented');
  }

  // --- Bulk ---
  async saveFragments(fragments) {
    throw new Error('Not implemented');
  }
  async saveConcepts(concepts) {
    throw new Error('Not implemented');
  }
  async saveLinks(links) {
    throw new Error('Not implemented');
  }

  // --- Workspace ---
  async clear() {
    throw new Error('Not implemented');
  }
}

module.exports = { StorageAdapter };
