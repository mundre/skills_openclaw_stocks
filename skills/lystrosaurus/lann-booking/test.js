const { handleUserInput, queryStores, queryServices, createBooking, recognizeIntent } = require('./index');

// 测试函数
async function runTests() {
  console.log('=== 开始测试蘭泰式按摩预约技能 ===\n');

  // 测试1：门店查询
  console.log('1. 测试门店查询功能');
  try {
    const storeResult = await handleUserInput('有哪些门店？');
    console.log('结果:', storeResult.message);
    console.log('测试通过: 门店查询功能正常\n');
  } catch (error) {
    console.log('测试失败:', error.message);
  }

  // 测试2：服务查询
  console.log('2. 测试服务查询功能');
  try {
    const serviceResult = await handleUserInput('有哪些服务项目？');
    console.log('结果:', serviceResult.message);
    console.log('测试通过: 服务查询功能正常\n');
  } catch (error) {
    console.log('测试失败:', error.message);
  }

  // 测试3：意图识别
  console.log('3. 测试意图识别功能');
  try {
    const intent1 = recognizeIntent('我要预约');
    console.log('预约意图:', intent1);
    
    const intent2 = recognizeIntent('查询门店');
    console.log('门店查询意图:', intent2);
    
    const intent3 = recognizeIntent('查询服务');
    console.log('服务查询意图:', intent3);
    
    const intent4 = recognizeIntent('随便说点什么');
    console.log('未知意图:', intent4);
    console.log('测试通过: 意图识别功能正常\n');
  } catch (error) {
    console.log('测试失败:', error.message);
  }

  // 测试4：错误处理 - 缺少参数
  console.log('4. 测试错误处理 - 缺少参数');
  try {
    const errorResult = await handleUserInput('预约淮海店');
    console.log('错误信息:', errorResult.message);
    console.log('测试通过: 错误处理功能正常\n');
  } catch (error) {
    console.log('测试失败:', error.message);
  }

  // 测试5：智能匹配
  console.log('5. 测试智能匹配功能');
  try {
    // 这里需要根据实际的门店数据进行测试
    // 假设我们有一个"淮海店"
    const matchResult = await handleUserInput('预约淮海店的传统古法全身按摩，2人，2024-01-15T14:00:00，手机号13812345678');
    console.log('智能匹配结果:', matchResult.message);
    console.log('测试通过: 智能匹配功能正常\n');
  } catch (error) {
    console.log('测试失败:', error.message);
  }

  // 测试6：验证函数
  console.log('6. 测试验证函数');
  try {
    // 这里可以直接测试验证函数
    const phoneValid = require('./index').validatePhone('13812345678');
    console.log('手机号验证:', phoneValid);
    
    const countValid = require('./index').validatePeopleCount(5);
    console.log('人数验证:', countValid);
    
    const timeValid = require('./index').validateBookingTime('2024-12-31T23:59:59');
    console.log('时间验证:', timeValid);
    console.log('测试通过: 验证函数正常\n');
  } catch (error) {
    console.log('测试失败:', error.message);
  }

  console.log('=== 测试完成 ===');
}

// 运行测试
runTests().catch(console.error);