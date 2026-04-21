#!/usr/bin/env node
/**
 * lk-order MCP 下单工具
 * 
 * 功能：
 * - 自动管理 MCP Session
 * - 调用 lk-order MCP Server 下单
 * - 自动处理支付二维码
 * 
 * 用法：
 *   node lk-order.cjs create <productId> [deptId] [payType]
 *   node lk-order.cjs quick <keyword> [payType]
 * 
 * 示例：
 *   node lk-order.cjs create 5293 345187 2  # 创建特仑苏订单，微信支付
 *   node lk-order.cjs quick 特仑苏 2        # 快速下单特仑苏
 * 
 * 🔐 安全配置：
 *   Token 通过以下方式获取（优先级从高到低）：
 *   1. 环境变量 LK_ORDER_TOKEN
 *   2. openclaw.json 配置文件
 *   3. 默认路径的 openclaw.json
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

/**
 * 获取 Token（安全方式）
 * 优先级：环境变量 > openclaw.json > 报错
 */
function getToken() {
    // 方式 1：环境变量（推荐）
    if (process.env.LK_ORDER_TOKEN) {
        return process.env.LK_ORDER_TOKEN;
    }
    
    // 方式 2：从 openclaw.json 读取
    const possiblePaths = [
        path.join(process.env.HOME || '', '.openclaw', 'openclaw.json'),
        path.join(process.cwd(), 'openclaw.json'),
        '/home/node/.openclaw/openclaw.json',
    ];
    
    for (const configPath of possiblePaths) {
        try {
            if (fs.existsSync(configPath)) {
                const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
                const token = config.mcpServers?.['lk-order']?.headers?.Authorization;
                if (token) {
                    return token.replace('Bearer ', '');
                }
            }
        } catch (err) {
            // 继续尝试下一个路径
        }
    }
    
    // 未找到 Token
    throw new Error(
        '❌ 未找到 Token！请通过以下方式之一配置：\n' +
        '  1. 环境变量：export LK_ORDER_TOKEN="your_token"\n' +
        '  2. openclaw.json: mcpServers.lk-order.headers.Authorization'
    );
}

// MCP 配置
const MCP_CONFIG = {
    url: 'https://inpre.lkcoffee.com/app/proxymcp',
    token: getToken(),
    sessionId: null,
};

// 临时目录
const TMP_DIR = '/tmp/openclaw/wecom-mcp';

/**
 * 发送 MCP 请求
 */
function sendMcpRequest(method, params) {
    const headers = [
        `-H "Authorization: Bearer ${MCP_CONFIG.token}"`,
        `-H "Content-Type: application/json"`,
        `-H "Accept: application/json, text/event-stream"`,
    ];
    
    if (MCP_CONFIG.sessionId) {
        headers.push(`-H "mcp-session-id: ${MCP_CONFIG.sessionId}"`);
    }
    
    const body = JSON.stringify({
        jsonrpc: '2.0',
        id: Date.now(),
        method,
        params,
    });
    
    const cmd = `curl -si -X POST ${headers.join(' ')} -d '${body}' ${MCP_CONFIG.url}`;
    const output = execSync(cmd, { encoding: 'utf8' });
    
    // 提取 session ID（从 response headers）
    if (output.includes('mcp-session-id:')) {
        const match = output.match(/mcp-session-id: ([^\r\n]+)/);
        if (match) {
            MCP_CONFIG.sessionId = match[1].trim();
            console.error(`[INFO] Session ID: ${MCP_CONFIG.sessionId}`);
        }
    }
    
    // 提取 data 部分
    const dataMatch = output.match(/data: (.+)/);
    if (dataMatch) {
        return JSON.parse(dataMatch[1]);
    }
    
    return JSON.parse(output);
}

/**
 * 初始化 MCP 连接
 */
function initialize() {
    console.error('[INFO] 初始化 MCP 连接...');
    const result = sendMcpRequest('initialize', {
        protocolVersion: '2024-11-05',
        capabilities: { roots: { listChanged: true } },
        clientInfo: { name: 'lk-order-cli', version: '1.0.0' },
    });
    console.error(`[INFO] 已连接：${result.result?.serverInfo?.name} v${result.result?.serverInfo?.version}`);
    return result;
}

/**
 * 创建订单
 */
function createOrder(deptId, productList, payType = '2', useCafeKu = false, useDiscount = true) {
    console.error('[INFO] 创建订单...');
    const result = sendMcpRequest('tools/call', {
        name: 'create_order',
        arguments: {
            deptId,
            delivery: 'pick',
            productList,
            payType,
            useCafeKu,
            useDiscount,
        },
    });
    
    if (result.result?.content?.[0]?.text) {
        const orderInfo = JSON.parse(result.result.content[0].text);
        console.error(`[INFO] 订单创建成功：${orderInfo.orderId}`);
        return orderInfo;
    }
    
    throw new Error(result.error?.message || '创建订单失败');
}

/**
 * 获取支付二维码
 */
function getPayment(orderId, payType = '2') {
    console.error('[INFO] 获取支付二维码...');
    const result = sendMcpRequest('tools/call', {
        name: 'pay_order',
        arguments: { orderId, payType },
    });
    
    if (result.result?.content) {
        // 提取二维码信息
        for (const item of result.result.content) {
            if (item.type === 'text' && item.text) {
                try {
                    const paymentInfo = JSON.parse(item.text);
                    return paymentInfo;
                } catch {
                    // 不是 JSON，跳过
                }
            }
        }
    }
    
    throw new Error('获取支付二维码失败');
}

/**
 * 处理并展示二维码
 */
function showQRCode(paymentInfo) {
    const { message, payUrl, qrImageUrl, orderId } = paymentInfo;
    
    console.log(message);
    console.log(`\n订单号：${orderId}`);
    console.log(`\n支付链接：${payUrl}`);
    console.log(`\n二维码链接：${qrImageUrl}`);
    
    // 下载二维码图片
    if (qrImageUrl) {
        if (!fs.existsSync(TMP_DIR)) {
            fs.mkdirSync(TMP_DIR, { recursive: true });
        }
        
        const qrPath = path.join(TMP_DIR, `mcp-qr-${Date.now()}.png`);
        execSync(`curl -s -o "${qrPath}" "${qrImageUrl}"`);
        
        if (fs.existsSync(qrPath) && fs.statSync(qrPath).size > 0) {
            console.error(`[INFO] 二维码已下载：${qrPath}`);
            console.log(`\nMEDIA: ${qrPath}`);
        }
    }
}

/**
 * 快速下单（按关键词）
 */
function quickOrder(keyword, payType = '2') {
    console.error('[INFO] 快速下单...');
    const result = sendMcpRequest('tools/call', {
        name: 'quick_order',
        arguments: { keyword, payType },
    });
    
    if (result.result?.content?.[0]?.text) {
        const orderInfo = JSON.parse(result.result.content[0].text);
        const orderId = orderInfo.orderId || orderInfo.order?.orderId;
        console.error(`[INFO] 订单创建成功：${orderId}`);
        
        if (!orderId) {
            throw new Error('订单创建成功但未返回订单号');
        }
        
        // 获取支付二维码
        const paymentInfo = getPayment(orderId, payType);
        showQRCode(paymentInfo);
        
        return orderInfo;
    }
    
    throw new Error(result.error?.message || '下单失败');
}

// CLI 入口
if (require.main === module) {
    const args = process.argv.slice(2);
    const command = args[0];
    
    if (!command) {
        console.error('用法：');
        console.error('  node lk-order.cjs create <productId> [deptId] [payType]');
        console.error('  node lk-order.cjs quick <keyword> [payType]');
        console.error('');
        console.error('示例：');
        console.error('  node lk-order.cjs create 5293 345187 2  # 特仑苏，T3 店，微信支付');
        console.error('  node lk-order.cjs quick 特仑苏 2        # 快速下单特仑苏');
        process.exit(1);
    }
    
    try {
        // 初始化 MCP 连接
        initialize();
        
        if (command === 'create') {
            const productId = parseInt(args[1], 10) || 5293; // 默认特仑苏
            const deptId = args[2] || '345187'; // 默认 T3 店
            const payType = args[3] || '2'; // 默认微信支付
            
            const orderInfo = createOrder(deptId, [
                { productId, skuCode: 'SP3713-00051', amount: 1 },
            ], payType);
            
            // 获取支付二维码
            const paymentInfo = getPayment(orderInfo.orderId, payType);
            showQRCode(paymentInfo);
            
        } else if (command === 'quick') {
            const keyword = args[1] || '特仑苏';
            const payType = args[2] || '2';
            
            quickOrder(keyword, payType);
            
        } else {
            console.error(`未知命令：${command}`);
            process.exit(1);
        }
    } catch (err) {
        console.error(`[ERROR] ${err.message}`);
        process.exit(1);
    }
}

module.exports = { initialize, createOrder, getPayment, showQRCode, quickOrder };
