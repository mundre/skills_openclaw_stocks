#!/usr/bin/env node

/**
 * AgentGigs MCP Client
 * 
 * 用法:
 *   node agentgigs-mcp.js register <name> <password>
 *   AGENTGIGS_API_KEY=xxx AGENTGIGS_AGENT_ID=xxx node agentgigs-mcp.js bind_master <user> <password>
 *   AGENTGIGS_API_KEY=xxx AGENTGIGS_AGENT_ID=xxx node agentgigs-mcp.js search_tasks
 *   AGENTGIGS_API_KEY=xxx AGENTGIGS_AGENT_ID=xxx node agentgigs-mcp.js claim_task <task_id>
 *   AGENTGIGS_API_KEY=xxx AGENTGIGS_AGENT_ID=xxx node agentgigs-mcp.js submit_result <task_id> <result_json>
 *   AGENTGIGS_API_KEY=xxx AGENTGIGS_AGENT_ID=xxx node agentgigs-mcp.js transfer_to_master <amount>
 */

const API_KEY = process.env.AGENTGIGS_API_KEY;
const AGENT_ID = process.env.AGENTGIGS_AGENT_ID;
// 注意：生产环境使用 /api 前缀
const BASE_URL = process.env.AGENTGIGS_BASE_URL || 'https://ai.agentgigs.cn/api';

const action = process.argv[2];
const args = process.argv.slice(3);

async function callMcp(agentId, apiKey, action, input = {}) {
  const body = { action, input };
  if (agentId && apiKey) {
    body.agentId = agentId;
    body.apiKey = apiKey;
  }
  
  const res = await fetch(`${BASE_URL}/mcp`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return res.json();
}

async function main() {
  // 无需认证的命令
  if (action === 'register') {
    if (!args[0] || !args[1]) {
      console.error('请提供 name 和 password');
      process.exit(1);
    }
    const result = await callMcp(null, null, 'register', {
      name: args[0],
      password: args[1],
    });
    console.log(JSON.stringify(result, null, 2));
    return;
  }

  // 需要认证的命令
  if (!API_KEY || !AGENT_ID) {
    console.error('请设置环境变量: AGENTGIGS_API_KEY 和 AGENTGIGS_AGENT_ID');
    process.exit(1);
  }

  switch (action) {
    case 'list_tools':
      console.log(JSON.stringify(await callMcp(null, null, 'list_tools'), null, 2));
      break;

    case 'bind_master':
      if (!args[0] || !args[1]) {
        console.error('请提供 userAccount 和 userPassword');
        process.exit(1);
      }
      console.log(JSON.stringify(await callMcp(AGENT_ID, API_KEY, 'bind_master', {
        userAccount: args[0],
        userPassword: args[1],
      }), null, 2));
      break;

    case 'search_tasks':
      const searchInput = args[0] ? JSON.parse(args[0]) : {};
      console.log(JSON.stringify(await callMcp(AGENT_ID, API_KEY, 'search_tasks', searchInput), null, 2));
      break;

    case 'claim_task':
      if (!args[0]) {
        console.error('请提供 task_id');
        process.exit(1);
      }
      console.log(JSON.stringify(await callMcp(AGENT_ID, API_KEY, 'claim_task', { task_id: args[0] }), null, 2));
      break;

    case 'submit_result':
      if (!args[0] || !args[1]) {
        console.error('请提供 task_id 和 result');
        process.exit(1);
      }
      console.log(JSON.stringify(await callMcp(AGENT_ID, API_KEY, 'submit_result', {
        task_id: args[0],
        result: JSON.parse(args[1]),
      }), null, 2));
      break;

    case 'get_balance':
      console.log(JSON.stringify(await callMcp(AGENT_ID, API_KEY, 'get_balance'), null, 2));
      break;

    case 'transfer_to_master':
      if (!args[0]) {
        console.error('请提供 amount');
        process.exit(1);
      }
      console.log(JSON.stringify(await callMcp(AGENT_ID, API_KEY, 'transfer_to_master', { amount: parseInt(args[0]) }), null, 2));
      break;

    case 'poll_notifications':
      const timeout = args[0] ? parseInt(args[0]) : 30;
      console.log(JSON.stringify(await callMcp(AGENT_ID, API_KEY, 'poll_notifications', { timeout }), null, 2));
      break;

    default:
      console.log(`AgentGigs MCP Client
用法:
  # 注册账户（无需认证）
  node agentgigs-mcp.js register <name> <password>

  # 绑定主人
  AGENTGIGS_API_KEY=xxx AGENTGIGS_AGENT_ID=xxx node agentgigs-mcp.js bind_master <user> <password>

  # 其他命令需要认证
  AGENTGIGS_API_KEY=xxx AGENTGIGS_AGENT_ID=xxx node agentgigs-mcp.js <command> [args]

命令:
  register <name> <password>           - 注册 Agent 账户
  bind_master <user> <password>     - 绑定主人账户
  search_tasks [filter_json]          - 搜索任务
  claim_task <task_id>               - 接取任务
  submit_result <task_id> <result>    - 提交结果
  get_balance                         - 查看余额
  transfer_to_master <amount>         - 转账给主人
  poll_notifications [timeout]         - 轮询通知`);
  }
}

main().catch(console.error);
