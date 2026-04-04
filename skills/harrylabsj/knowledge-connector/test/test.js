const KnowledgeConnector = require('../src/index.js');
const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');

async function runTests() {
  console.log('🧪 开始运行测试...\n');
  
  const testDir = fs.mkdtempSync(path.join(os.tmpdir(), 'knowledge-connector-test-'));
  const kc = new KnowledgeConnector({ dataDir: testDir });
  let passed = 0;
  let failed = 0;
  
  // 测试 1: 提取概念
  try {
    const concepts = await kc.extract('人工智能是机器学习的基础，深度学习是人工智能的重要分支');
    assert(concepts.length > 0, '应该提取到概念');
    console.log('✅ 测试 1: 概念提取 - 通过');
    passed++;
  } catch (e) {
    console.log('❌ 测试 1: 概念提取 - 失败:', e.message);
    failed++;
  }
  
  // 测试 2: 保存概念
  try {
    const concepts = await kc.extract('测试概念 A 和测试概念 B');
    await kc.saveConcepts(concepts);
    const saved = kc.loadConcepts();
    assert(saved.length > 0, '应该保存了概念');
    console.log('✅ 测试 2: 保存概念 - 通过');
    passed++;
  } catch (e) {
    console.log('❌ 测试 2: 保存概念 - 失败:', e.message);
    failed++;
  }
  
  // 测试 3: 建立关联
  try {
    const concepts = kc.loadConcepts();
    if (concepts.length >= 2) {
      await kc.connect({
        from: concepts[0].name,
        to: concepts[1].name,
        type: '相关'
      });
      console.log('✅ 测试 3: 建立关联 - 通过');
      passed++;
    } else {
      console.log('⚠️  测试 3: 建立关联 - 跳过 (概念不足)');
    }
  } catch (e) {
    console.log('❌ 测试 3: 建立关联 - 失败:', e.message);
    failed++;
  }
  
  // 测试 4: 搜索
  try {
    const results = await kc.search('测试');
    assert(Array.isArray(results.concepts), '应该返回概念列表');
    console.log('✅ 测试 4: 搜索功能 - 通过');
    passed++;
  } catch (e) {
    console.log('❌ 测试 4: 搜索功能 - 失败:', e.message);
    failed++;
  }
  
  // 测试 5: 统计信息
  try {
    const stats = await kc.getStats();
    assert(typeof stats.conceptCount === 'number', '应该有概念数量');
    console.log('✅ 测试 5: 统计信息 - 通过');
    passed++;
  } catch (e) {
    console.log('❌ 测试 5: 统计信息 - 失败:', e.message);
    failed++;
  }
  
  // 测试 6: 可视化
  try {
    const html = await kc.visualize({ format: 'html' });
    assert(html.includes('<html>'), '应该生成 HTML');
    console.log('✅ 测试 6: 可视化 - 通过');
    passed++;
  } catch (e) {
    console.log('❌ 测试 6: 可视化 - 失败:', e.message);
    failed++;
  }
  
  // 测试 7: 导出
  try {
    const data = await kc.export();
    assert(data.concepts, '应该有概念数据');
    assert(data.relations, '应该有关系数据');
    console.log('✅ 测试 7: 导出功能 - 通过');
    passed++;
  } catch (e) {
    console.log('❌ 测试 7: 导出功能 - 失败:', e.message);
    failed++;
  }
  
  // 测试 8: 推荐
  try {
    const concepts = kc.loadConcepts();
    if (concepts.length > 0) {
      const recommendations = await kc.recommend(concepts[0].name, 3);
      console.log('✅ 测试 8: 推荐功能 - 通过');
      passed++;
    } else {
      console.log('⚠️  测试 8: 推荐功能 - 跳过 (概念不足)');
    }
  } catch (e) {
    console.log('❌ 测试 8: 推荐功能 - 失败:', e.message);
    failed++;
  }

  // 测试 9: 批量导入文档
  try {
    const docsDir = path.join(testDir, 'docs');
    fs.mkdirSync(docsDir, { recursive: true });
    fs.writeFileSync(path.join(docsDir, 'a.md'), '人工智能 连接 机器学习');
    fs.writeFileSync(path.join(docsDir, 'b.md'), '机器学习 连接 深度学习');
    const summary = await kc.importDocuments([docsDir]);
    assert(summary.fileCount === 2, '应该导入 2 个文档');
    assert(summary.conceptCount > 0, '应该导入概念');
    console.log('✅ 测试 9: 批量导入文档 - 通过');
    passed++;
  } catch (e) {
    console.log('❌ 测试 9: 批量导入文档 - 失败:', e.message);
    failed++;
  }

  // 测试 10: 概念子图
  try {
    const map = await kc.map('机器学习', 1);
    assert(map && Array.isArray(map.nodes), '应该生成子图');
    console.log('✅ 测试 10: 概念子图 - 通过');
    passed++;
  } catch (e) {
    console.log('❌ 测试 10: 概念子图 - 失败:', e.message);
    failed++;
  }

  // 测试 11: 导入预览
  try {
    const docsDir = path.join(testDir, 'docs');
    const plan = kc.planImport([docsDir]);
    assert(plan.fileCount >= 2, '应该预览到导入文件');
    assert(Array.isArray(plan.supportedTypes), '应该返回支持类型');
    console.log('✅ 测试 11: 导入预览 - 通过');
    passed++;
  } catch (e) {
    console.log('❌ 测试 11: 导入预览 - 失败:', e.message);
    failed++;
  }

  // 测试 12: 答案页结果
  try {
    const answer = await kc.answer('机器学习');
    assert(answer.summary && answer.summary.includes('问题'), '应该生成答案摘要');
    const html = await kc.answer('机器学习', { format: 'html' });
    assert(typeof html === 'string' && html.includes('<html>'), '应该生成 HTML 答案页');
    console.log('✅ 测试 12: 答案页结果 - 通过');
    passed++;
  } catch (e) {
    console.log('❌ 测试 12: 答案页结果 - 失败:', e.message);
    failed++;
  }
  
  console.log('\n' + '='.repeat(40));
  console.log(`测试结果: ${passed} 通过, ${failed} 失败`);
  console.log('='.repeat(40));
  
  process.exit(failed > 0 ? 1 : 0);
}

runTests();
