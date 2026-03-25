/**
 * Agent Messaging Example
 * 独立 Agent 消息发送示例（方案 C）
 */

const { message } = require('@openclaw/tools');
const { getAgentAddress, getAgentInfo } = require('../agent-addresses');
const { Config } = require('../config');

const config = new Config();

/**
 * 向指定 Agent 发送消息
 * @param {string} agentName - Agent 名称
 * @param {string} task - 任务描述
 * @param {object} params - 任务参数
 */
async function sendToAgent(agentName, task, params = {}) {
  try {
    const agentInfo = getAgentInfo(agentName);
    const target = getAgentAddress(agentName);
    
    const messageContent = `🤖 ${agentInfo.role.toUpperCase()} Agent 任务指令

目标 Agent: ${agentName}
任务：${task}
参数：${JSON.stringify(params, null, 2)}
优先级：high
时间：${new Date().toISOString()}

---
${agentInfo.description} 已就绪，等待任务分配！`;

    const result = await message({
      action: 'send',
      channel: 'qqbot',
      target: target,
      message: messageContent
    });

    console.log(`✅ 消息已发送到 ${agentName}:`, result);
    return result;
  } catch (error) {
    console.error(`❌ 发送消息到 ${agentName} 失败:`, error.message);
    throw error;
  }
}

/**
 * 向所有 Agent 发送消息
 * @param {string} task - 任务描述
 * @param {object} params - 任务参数
 */
async function sendToAllAgents(task, params = {}) {
  const agentNames = Object.keys(require('../agent-addresses').AGENT_ADDRESSES);
  
  console.log(`🚀 向 ${agentNames.length} 个 Agent 发送消息...`);
  
  const results = [];
  for (const agentName of agentNames) {
    try {
      const result = await sendToAgent(agentName, task, params);
      results.push({ agent: agentName, success: true, result });
    } catch (error) {
      results.push({ agent: agentName, success: false, error: error.message });
    }
  }
  
  return results;
}

/**
 * 测试消息发送
 */
async function testMessaging() {
  console.log('=== 测试 Agent 消息发送（方案 C） ===\n');
  
  // 测试单个 Agent
  console.log('1. 测试向 Coder Agent 发送消息...');
  await sendToAgent('coder-agent', '测试代码开发功能', { test: true });
  
  console.log('\n2. 测试向 Main Agent 发送消息...');
  await sendToAgent('main-agent', '测试任务管理功能', { test: true });
  
  console.log('\n3. 测试向所有 Agent 发送消息...');
  const results = await sendToAllAgents('测试完整协作流程', { 
    test: true, 
    timestamp: new Date().toISOString() 
  });
  
  console.log('\n=== 测试结果 ===');
  results.forEach(r => {
    console.log(`${r.agent}: ${r.success ? '✅ 成功' : '❌ 失败'}`);
    if (!r.success) {
      console.log(`   错误：${r.error}`);
    }
  });
}

// 导出函数供其他模块使用
module.exports = {
  sendToAgent,
  sendToAllAgents,
  testMessaging
};

// 如果直接运行此文件
if (require.main === module) {
  testMessaging().catch(console.error);
}