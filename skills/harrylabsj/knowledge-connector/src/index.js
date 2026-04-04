const fs = require('fs');
const path = require('path');
const os = require('os');

class KnowledgeConnector {
  constructor(options = {}) {
    this.dataDir = options.dataDir || path.join(os.homedir(), '.local', 'share', 'knowledge-connector');
    this.conceptsFile = path.join(this.dataDir, 'concepts.json');
    this.relationsFile = path.join(this.dataDir, 'relations.json');
    this.sourcesFile = path.join(this.dataDir, 'sources.json');
    this.init();
  }

  init() {
    if (!fs.existsSync(this.dataDir)) {
      fs.mkdirSync(this.dataDir, { recursive: true });
    }
    for (const file of [this.conceptsFile, this.relationsFile, this.sourcesFile]) {
      if (!fs.existsSync(file)) {
        fs.writeFileSync(file, JSON.stringify([]));
      }
    }
  }

  loadJson(file) {
    try {
      return JSON.parse(fs.readFileSync(file, 'utf-8'));
    } catch {
      return [];
    }
  }

  saveJson(file, data) {
    fs.writeFileSync(file, JSON.stringify(data, null, 2));
  }

  loadConcepts() {
    return this.loadJson(this.conceptsFile);
  }

  saveConceptsData(concepts) {
    this.saveJson(this.conceptsFile, concepts);
  }

  loadRelations() {
    return this.loadJson(this.relationsFile);
  }

  saveRelationsData(relations) {
    this.saveJson(this.relationsFile, relations);
  }

  loadSources() {
    return this.loadJson(this.sourcesFile);
  }

  saveSourcesData(sources) {
    this.saveJson(this.sourcesFile, sources);
  }

  generateId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  normalizeName(name) {
    return String(name || '').trim().toLowerCase();
  }

  getSourceExcerpt(text) {
    return String(text || '').replace(/\s+/g, ' ').trim().slice(0, 160);
  }

  getTextFiles(targetPath, recursive = true) {
    const allowed = new Set(['.txt', '.md', '.markdown', '.text', '.json', '.csv']);
    const results = [];
    const stat = fs.statSync(targetPath);

    if (stat.isFile()) {
      return allowed.has(path.extname(targetPath).toLowerCase()) ? [targetPath] : [];
    }

    const walk = (dir) => {
      for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
        const fullPath = path.join(dir, entry.name);
        if (entry.isDirectory()) {
          if (recursive) {
            walk(fullPath);
          }
          continue;
        }
        if (allowed.has(path.extname(fullPath).toLowerCase())) {
          results.push(fullPath);
        }
      }
    };

    walk(targetPath);
    return results;
  }

  planImport(inputs, options = {}) {
    const targets = Array.isArray(inputs) ? inputs : [inputs];
    const recursive = options.recursive !== false;
    const files = [];

    for (const target of targets) {
      for (const filePath of this.getTextFiles(target, recursive)) {
        files.push({
          path: filePath,
          title: path.basename(filePath),
          type: path.extname(filePath).replace('.', '') || 'text'
        });
      }
    }

    return {
      fileCount: files.length,
      files,
      supportedTypes: Array.from(new Set(files.map((file) => file.type))).sort()
    };
  }

  async extract(text, options = {}) {
    const source = options.source || 'direct-input';
    const sourceId = options.sourceId || null;
    const concepts = [];
    const addConcept = (name, type, description = '') => {
      const trimmed = String(name || '').trim();
      if (!trimmed || trimmed.length < 2 || trimmed.length > 60) {
        return;
      }
      if (concepts.find((c) => this.normalizeName(c.name) === this.normalizeName(trimmed))) {
        return;
      }
      concepts.push({
        id: this.generateId(),
        name: trimmed,
        type,
        description,
        source,
        sourceId,
        sourceExcerpt: this.getSourceExcerpt(text),
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      });
    };

    let match;
    const quotedPattern = /["""']([^"""']+)["""']/g;
    while ((match = quotedPattern.exec(text)) !== null) {
      addConcept(match[1], 'term');
    }

    const properNounPattern = /[A-Z][a-zA-Z0-9.+\-/\s]{1,30}(?=[\s,;.!?：，。！)]|$)/g;
    while ((match = properNounPattern.exec(text)) !== null) {
      addConcept(match[0], 'proper-noun');
    }

    const chinesePattern = /[\u4e00-\u9fa5]{2,10}/g;
    const stopWords = new Set(['这是', '那是', '一个', '一些', '可以', '进行', '需要', '通过', '根据', '关于']);
    while ((match = chinesePattern.exec(text)) !== null) {
      if (!stopWords.has(match[0])) {
        addConcept(match[0], 'concept');
      }
    }

    const techTerms = [
      '人工智能', '机器学习', '深度学习', '神经网络', '自然语言处理',
      '计算机视觉', '数据挖掘', '算法', '模型', '训练', '推理',
      'Python', 'JavaScript', 'Java', 'TypeScript', 'Node.js',
      'React', 'Vue', 'Angular', '数据库', 'API', '微服务',
      '云计算', '大数据', '区块链', '物联网', '5G', '边缘计算'
    ];
    for (const term of techTerms) {
      if (text.includes(term)) {
        addConcept(term, 'tech');
      }
    }

    return concepts;
  }

  async saveConcepts(newConcepts) {
    const existing = this.loadConcepts();

    for (const incoming of newConcepts) {
      const match = existing.find((item) => this.normalizeName(item.name) === this.normalizeName(incoming.name));
      if (!match) {
        existing.push({
          ...incoming,
          aliases: incoming.aliases || [],
          sources: incoming.source ? [incoming.source] : []
        });
        continue;
      }

      match.updatedAt = new Date().toISOString();
      match.description = match.description || incoming.description || '';
      match.type = match.type || incoming.type;
      match.aliases = Array.from(new Set([...(match.aliases || []), ...(incoming.aliases || [])]));
      match.sources = Array.from(new Set([...(match.sources || []), ...(incoming.source ? [incoming.source] : [])]));
      if (!match.sourceExcerpt && incoming.sourceExcerpt) {
        match.sourceExcerpt = incoming.sourceExcerpt;
      }
    }

    this.saveConceptsData(existing);
    return existing;
  }

  async connect(options) {
    const { from, to, type = '相关', weight = 0.5, source = 'manual' } = options;
    const concepts = this.loadConcepts();
    const fromConcept = concepts.find((c) => this.normalizeName(c.name) === this.normalizeName(from));
    const toConcept = concepts.find((c) => this.normalizeName(c.name) === this.normalizeName(to));

    if (!fromConcept) {
      throw new Error(`源概念不存在: ${from}`);
    }
    if (!toConcept) {
      throw new Error(`目标概念不存在: ${to}`);
    }

    const relations = this.loadRelations();
    const existing = relations.find((r) => r.from === fromConcept.id && r.to === toConcept.id && r.type === type);
    if (existing) {
      return existing;
    }

    const relation = {
      id: this.generateId(),
      from: fromConcept.id,
      to: toConcept.id,
      type,
      weight,
      source,
      createdAt: new Date().toISOString()
    };

    relations.push(relation);
    this.saveRelationsData(relations);
    return relation;
  }

  calculateSimilarity(s1, s2) {
    const set1 = new Set(String(s1 || ''));
    const set2 = new Set(String(s2 || ''));
    const intersection = new Set([...set1].filter((x) => set2.has(x)));
    const union = new Set([...set1, ...set2]);
    return union.size === 0 ? 0 : intersection.size / union.size;
  }

  async autoConnect() {
    const concepts = this.loadConcepts();
    const relations = this.loadRelations();
    const newRelations = [];

    for (let i = 0; i < concepts.length; i += 1) {
      for (let j = i + 1; j < concepts.length; j += 1) {
        const a = concepts[i];
        const b = concepts[j];
        const existing = relations.find((r) =>
          (r.from === a.id && r.to === b.id) || (r.from === b.id && r.to === a.id)
        );
        if (existing) {
          continue;
        }

        const sharedSource = (a.sources || []).some((source) => (b.sources || []).includes(source));
        const similarity = this.calculateSimilarity(a.name, b.name);
        const weight = sharedSource ? Math.max(0.45, similarity) : similarity;

        if (weight >= 0.3) {
          const relation = {
            id: this.generateId(),
            from: a.id,
            to: b.id,
            type: sharedSource ? '共现' : (weight > 0.7 ? '相似' : '相关'),
            weight,
            source: sharedSource ? 'shared-source' : 'name-similarity',
            createdAt: new Date().toISOString()
          };
          relations.push(relation);
          newRelations.push(relation);
        }
      }
    }

    this.saveRelationsData(relations);
    return newRelations;
  }

  async importRelations(data) {
    const relations = this.loadRelations();
    const concepts = this.loadConcepts();
    const newRelations = [];

    for (const item of data) {
      const fromConcept = concepts.find((c) => c.name === item.from || c.id === item.from);
      const toConcept = concepts.find((c) => c.name === item.to || c.id === item.to);
      if (!fromConcept || !toConcept) {
        continue;
      }
      const relation = {
        id: this.generateId(),
        from: fromConcept.id,
        to: toConcept.id,
        type: item.type || '相关',
        weight: item.weight || 0.5,
        source: item.source || 'import',
        createdAt: new Date().toISOString()
      };
      relations.push(relation);
      newRelations.push(relation);
    }

    this.saveRelationsData(relations);
    return newRelations;
  }

  async importDocuments(inputs, options = {}) {
    const targets = Array.isArray(inputs) ? inputs : [inputs];
    const recursive = options.recursive !== false;
    const sources = this.loadSources();
    const importedFiles = [];
    let conceptCount = 0;

    for (const target of targets) {
      for (const filePath of this.getTextFiles(target, recursive)) {
        const content = fs.readFileSync(filePath, 'utf-8');
        const sourceRecord = {
          id: this.generateId(),
          title: path.basename(filePath),
          path: filePath,
          type: path.extname(filePath).replace('.', '') || 'text',
          excerpt: this.getSourceExcerpt(content),
          importedAt: new Date().toISOString()
        };

        const concepts = await this.extract(content, { source: sourceRecord.title, sourceId: sourceRecord.id });
        await this.saveConcepts(concepts);
        sourceRecord.conceptCount = concepts.length;
        sources.push(sourceRecord);
        importedFiles.push(sourceRecord);
        conceptCount += concepts.length;
      }
    }

    this.saveSourcesData(sources);
    const relations = options.autoConnect === false ? [] : await this.autoConnect();

    return {
      fileCount: importedFiles.length,
      conceptCount,
      relationCount: relations.length,
      files: importedFiles
    };
  }

  async search(keyword, options = {}) {
    const query = String(keyword || '').trim().toLowerCase();
    const concepts = this.loadConcepts();
    const sources = this.loadSources();
    const relations = this.loadRelations();

    const conceptHits = concepts.filter((c) =>
      c.name.toLowerCase().includes(query) ||
      (c.description && c.description.toLowerCase().includes(query)) ||
      (c.aliases && c.aliases.some((a) => a.toLowerCase().includes(query)))
    );

    const sourceHits = sources.filter((s) =>
      s.title.toLowerCase().includes(query) ||
      (s.excerpt && s.excerpt.toLowerCase().includes(query)) ||
      (s.path && s.path.toLowerCase().includes(query))
    );

    const conceptIds = new Set(conceptHits.map((c) => c.id));
    const relationHits = relations.filter((r) => conceptIds.has(r.from) || conceptIds.has(r.to));

    if (options.mode === 'concepts') {
      return conceptHits;
    }

    return {
      concepts: conceptHits,
      sources: sourceHits,
      relations: relationHits,
      nextSteps: this.buildNextSteps({ concepts: conceptHits, sources: sourceHits, relations: relationHits })
    };
  }

  async getConcept(name) {
    const concepts = this.loadConcepts();
    return concepts.find((c) => this.normalizeName(c.name) === this.normalizeName(name));
  }

  async getRelated(conceptId) {
    const relations = this.loadRelations();
    const concepts = this.loadConcepts();
    return relations
      .filter((r) => r.from === conceptId || r.to === conceptId)
      .map((r) => {
        const otherId = r.from === conceptId ? r.to : r.from;
        const otherConcept = concepts.find((c) => c.id === otherId);
        return otherConcept ? {
          ...otherConcept,
          relationType: r.type,
          relationWeight: r.weight
        } : null;
      })
      .filter(Boolean);
  }

  buildNextSteps({ concepts, sources, relations }) {
    const nextSteps = [];
    if (sources.length === 0) {
      nextSteps.push('导入更多文档，让图谱结果不只来自单条输入。');
    }
    if (concepts.length > 0 && relations.length === 0) {
      nextSteps.push('运行自动关联，补出概念之间的关系边。');
    }
    if (concepts.length > 0) {
      nextSteps.push('围绕命中的核心概念生成 2 层子图，检查遗漏关系。');
    }
    if (sources.length > 1) {
      nextSteps.push('按命中的来源文档回看上下文，确认跨文档连接是否成立。');
    }
    return nextSteps;
  }

  async ask(question) {
    const keywords = question.match(/[\u4e00-\u9fa5]{2,}|[a-zA-Z]{3,}/g) || [];
    const aggregate = { concepts: [], sources: [], relations: [] };
    const seenConcepts = new Set();
    const seenSources = new Set();
    const seenRelations = new Set();

    for (const keyword of keywords) {
      const result = await this.search(keyword);
      for (const concept of result.concepts) {
        if (!seenConcepts.has(concept.id)) {
          seenConcepts.add(concept.id);
          aggregate.concepts.push(concept);
        }
      }
      for (const source of result.sources) {
        if (!seenSources.has(source.id)) {
          seenSources.add(source.id);
          aggregate.sources.push(source);
        }
      }
      for (const relation of result.relations) {
        if (!seenRelations.has(relation.id)) {
          seenRelations.add(relation.id);
          aggregate.relations.push(relation);
        }
      }
    }

    const answer = aggregate.concepts.length > 0
      ? `找到 ${aggregate.concepts.length} 个相关概念，覆盖 ${aggregate.sources.length} 个来源文档，并命中 ${aggregate.relations.length} 条关系。`
      : '未找到相关信息';

    return {
      answer,
      concepts: aggregate.concepts,
      sources: aggregate.sources,
      relations: aggregate.relations,
      nextSteps: this.buildNextSteps(aggregate)
    };
  }

  buildAnswerSummary(query, result) {
    const topConcepts = result.concepts.slice(0, 5).map((concept) => concept.name);
    const topSources = result.sources.slice(0, 5).map((source) => source.title);
    const lines = [`问题: ${query}`];
    if (topConcepts.length > 0) {
      lines.push(`命中概念: ${topConcepts.join('、')}`);
    }
    if (topSources.length > 0) {
      lines.push(`涉及文档: ${topSources.join('、')}`);
    }
    if (result.relations.length > 0) {
      lines.push(`相关关系数: ${result.relations.length}`);
    }
    return lines.join('\n');
  }

  async answer(query, options = {}) {
    const result = await this.search(query);
    const summary = this.buildAnswerSummary(query, result);

    if (options.format === 'html') {
      const conceptItems = result.concepts.slice(0, 12).map((concept) =>
        `<li><strong>${concept.name}</strong> <span style="color:#667">(${concept.type})</span></li>`
      ).join('');
      const sourceItems = result.sources.slice(0, 12).map((source) =>
        `<li><strong>${source.title}</strong><br><span style="color:#667">${source.path}</span></li>`
      ).join('');
      const nextStepItems = result.nextSteps.map((step) => `<li>${step}</li>`).join('');

      return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Knowledge Connector Answer</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 0; padding: 24px; color: #223; background: #f7f8fb; }
    .card { background: white; border: 1px solid #e3e6ee; border-radius: 16px; padding: 20px; margin-bottom: 16px; }
    h1, h2 { margin-top: 0; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    ul { padding-left: 18px; }
    code { background: #eef3ff; padding: 2px 6px; border-radius: 6px; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Knowledge Connector Answer</h1>
    <p><strong>Query:</strong> ${query}</p>
    <pre>${summary}</pre>
  </div>
  <div class="grid">
    <div class="card">
      <h2>Matched Concepts</h2>
      <ul>${conceptItems || '<li>没有命中概念</li>'}</ul>
    </div>
    <div class="card">
      <h2>Matched Sources</h2>
      <ul>${sourceItems || '<li>没有命中文档</li>'}</ul>
    </div>
  </div>
  <div class="card">
    <h2>Next Steps</h2>
    <ul>${nextStepItems || '<li>继续导入更多文档扩展图谱。</li>'}</ul>
    <p>Tips: <code>kc map --concept &lt;概念&gt;</code> / <code>kc visualize --concept &lt;概念&gt;</code></p>
  </div>
</body>
</html>`;
    }

    return {
      query,
      summary,
      ...result
    };
  }

  async map(conceptName, depth = 2) {
    const center = await this.getConcept(conceptName);
    if (!center) {
      return null;
    }

    const concepts = this.loadConcepts();
    const relations = this.loadRelations();
    const relatedIds = new Set([center.id]);

    for (let i = 0; i < depth; i += 1) {
      const snapshot = new Set(relatedIds);
      for (const relation of relations) {
        if (snapshot.has(relation.from) || snapshot.has(relation.to)) {
          relatedIds.add(relation.from);
          relatedIds.add(relation.to);
        }
      }
    }

    const nodes = concepts.filter((concept) => relatedIds.has(concept.id));
    const edges = relations.filter((relation) => relatedIds.has(relation.from) && relatedIds.has(relation.to));

    return {
      center,
      nodes,
      edges,
      nextSteps: this.buildNextSteps({ concepts: nodes, sources: this.loadSources().filter((s) => nodes.some((n) => (n.sources || []).includes(s.title))), relations: edges })
    };
  }

  async visualize(options = {}) {
    const { format = 'html', concept, depth = 2 } = options;
    const graph = concept ? await this.map(concept, depth) : {
      center: null,
      nodes: this.loadConcepts(),
      edges: this.loadRelations(),
      nextSteps: this.buildNextSteps({
        concepts: this.loadConcepts(),
        sources: this.loadSources(),
        relations: this.loadRelations()
      })
    };

    const filteredConcepts = graph ? graph.nodes : [];
    const filteredRelations = graph ? graph.edges : [];

    if (format === 'json') {
      return JSON.stringify({
        center: graph.center,
        concepts: filteredConcepts,
        relations: filteredRelations,
        nextSteps: graph.nextSteps
      }, null, 2);
    }

    if (format === 'dot') {
      let dot = 'digraph KnowledgeGraph {\n';
      dot += '  rankdir=LR;\n';
      dot += '  node [shape=box, style=rounded];\n\n';
      for (const conceptNode of filteredConcepts) {
        dot += `  "${conceptNode.id}" [label="${conceptNode.name}"];\n`;
      }
      dot += '\n';
      for (const relation of filteredRelations) {
        dot += `  "${relation.from}" -> "${relation.to}" [label="${relation.type}"];\n`;
      }
      dot += '}';
      return dot;
    }

    const summaryItems = graph.nextSteps.map((item) => `<li>${item}</li>`).join('');
    return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>知识图谱</title>
  <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
  <style>
    body { margin: 0; padding: 20px; font-family: Arial, sans-serif; color: #223; }
    .layout { display: grid; grid-template-columns: 1fr 320px; gap: 16px; }
    #graph { width: 100%; height: 640px; border: 1px solid #ddd; border-radius: 12px; }
    .panel { border: 1px solid #ddd; border-radius: 12px; padding: 16px; background: #fafafa; }
    .stats { margin: 10px 0 16px; color: #666; }
    h1, h2 { margin: 0 0 12px; }
    ul { padding-left: 18px; }
    code { background: #eef3ff; padding: 2px 6px; border-radius: 6px; }
  </style>
</head>
<body>
  <h1>知识图谱</h1>
  <div class="stats">概念: ${filteredConcepts.length} | 关系: ${filteredRelations.length}${graph.center ? ` | 中心概念: ${graph.center.name}` : ''}</div>
  <div class="layout">
    <div id="graph"></div>
    <div class="panel">
      <h2>下一步建议</h2>
      <ul>${summaryItems || '<li>继续导入文档，扩展图谱范围。</li>'}</ul>
      <h2>使用提示</h2>
      <ul>
        <li>用 <code>kc search &lt;关键词&gt;</code> 做跨文档搜索</li>
        <li>用 <code>kc map --concept &lt;概念&gt;</code> 看可操作子图</li>
        <li>用 <code>kc import-docs --dir &lt;目录&gt;</code> 批量导入</li>
      </ul>
    </div>
  </div>
  <script>
    const nodes = new vis.DataSet(${JSON.stringify(filteredConcepts.map((conceptNode) => ({
      id: conceptNode.id,
      label: conceptNode.name,
      title: conceptNode.description || conceptNode.sourceExcerpt || conceptNode.name,
      color: conceptNode.type === 'tech' ? '#d7ebff' : '#eef2f7'
    })))});
    const edges = new vis.DataSet(${JSON.stringify(filteredRelations.map((relation) => ({
      from: relation.from,
      to: relation.to,
      label: relation.type,
      arrows: 'to'
    })))});
    const network = new vis.Network(
      document.getElementById('graph'),
      { nodes, edges },
      {
        nodes: { shape: 'box', margin: 10, font: { size: 14 } },
        edges: { font: { size: 12 }, smooth: { type: 'continuous' } },
        physics: { stabilization: false }
      }
    );
  </script>
</body>
</html>`;
  }

  async getStats() {
    const concepts = this.loadConcepts();
    const relations = this.loadRelations();
    const sources = this.loadSources();
    return {
      conceptCount: concepts.length,
      relationCount: relations.length,
      sourceCount: sources.length,
      typeCount: new Set(concepts.map((c) => c.type).filter(Boolean)).size,
      dataSize: this.getDataSize()
    };
  }

  getDataSize() {
    try {
      const total = [this.conceptsFile, this.relationsFile, this.sourcesFile]
        .map((file) => fs.statSync(file).size)
        .reduce((sum, size) => sum + size, 0);
      if (total < 1024) return `${total} B`;
      if (total < 1024 * 1024) return `${(total / 1024).toFixed(2)} KB`;
      return `${(total / (1024 * 1024)).toFixed(2)} MB`;
    } catch {
      return '0 B';
    }
  }

  async export() {
    return {
      concepts: this.loadConcepts(),
      relations: this.loadRelations(),
      sources: this.loadSources(),
      exportedAt: new Date().toISOString()
    };
  }

  async import(data) {
    if (data.concepts) {
      this.saveConceptsData(data.concepts);
    }
    if (data.relations) {
      this.saveRelationsData(data.relations);
    }
    if (data.sources) {
      this.saveSourcesData(data.sources);
    }
  }

  async clear() {
    this.saveConceptsData([]);
    this.saveRelationsData([]);
    this.saveSourcesData([]);
  }

  async recommend(conceptName, limit = 5) {
    const concept = await this.getConcept(conceptName);
    if (!concept) {
      return [];
    }

    return (await this.getRelated(concept.id))
      .sort((a, b) => b.relationWeight - a.relationWeight)
      .slice(0, limit)
      .map((related) => ({
        id: related.id,
        name: related.name,
        type: related.type,
        score: related.relationWeight,
        reason: `与 ${conceptName} 存在“${related.relationType}”关系`
      }));
  }
}

module.exports = KnowledgeConnector;
