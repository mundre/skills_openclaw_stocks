/**
 * 东南亚市场政策查询Skill测试
 */

const SoutheastAsiaPolicyQuery = require('./index.js');

async function runTests() {
  console.log('=== 东南亚市场政策查询Skill测试 ===\n');

  // 创建实例
  const skill = new SoutheastAsiaPolicyQuery({
    countries: ['SG', 'MY', 'TH'],
    updateInterval: 60 // 1分钟更新一次（测试用）
  });

  try {
    // 测试1: 查询支持的国家
    console.log('1. 测试支持的国家列表:');
    const countries = skill.getSupportedCountries();
    console.log(countries);
    console.log('✅ 测试1通过\n');

    // 测试2: 查询新加坡政策
    console.log('2. 测试查询新加坡政策:');
    const sgPolicies = await skill.queryPolicies('Singapore', { category: 'technology' });
    console.log(JSON.stringify(sgPolicies, null, 2));
    console.log('✅ 测试2通过\n');

    // 测试3: 查询马来西亚政策（使用中文）
    console.log('3. 测试查询马来西亚政策:');
    const myPolicies = await skill.queryPolicies('马来西亚', { category: 'investment' });
    console.log(JSON.stringify(myPolicies, null, 2));
    console.log('✅ 测试3通过\n');

    // 测试4: 市场分析
    console.log('4. 测试泰国科技市场分析:');
    const thAnalysis = await skill.analyzeMarket('Thailand', 'technology');
    console.log(JSON.stringify(thAnalysis, null, 2));
    console.log('✅ 测试4通过\n');

    // 测试5: 错误处理
    console.log('5. 测试错误处理（不支持的国家）:');
    try {
      await skill.queryPolicies('UnknownCountry');
      console.log('❌ 测试5失败：应该抛出错误');
    } catch (error) {
      console.log(`✅ 测试5通过：正确抛出错误 - ${error.message}`);
    }

    console.log('\n=== 所有测试完成 ===');
    console.log('✅ Skill功能正常，可以发布到ClawHub');

  } catch (error) {
    console.error('❌ 测试失败:', error);
    process.exit(1);
  }
}

// 运行测试
runTests();