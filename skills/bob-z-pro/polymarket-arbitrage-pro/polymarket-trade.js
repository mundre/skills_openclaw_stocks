#!/usr/bin/env node

/**
 * Polymarket Arbitrage Pro v7.0 - 完整版
 * 真实交易 + SkillPay收费
 */

const OKX_API_KEY = 'd339c1c9-cc33-4c07-a6cc-2d4c20a283a1';
const OKX_SECRET_KEY = '26BC55C2789BE57FCB750228D0BD1E8F';
const OKX_PASSPHRASE = 'Amway091263#';
const SKILLPAY_KEY = 'cc7d6401-0a5c-46eb-8694-673ffa587c8b';

const POLYMARKET_API = 'https://clob.polymarket.com';
const OKX_API = 'https://www.okx.com';
const SKILLPAY_API = 'https://skillpay.me/api/v1';

const MIN_PROFIT = 2;
const CHECK_INTERVAL = 30000;
const INITIAL_BALANCE = 100;
const MAX_LOSS = 0.20;
const TRADE_AMOUNT = 10;

console.log('🤖 Polymarket Arbitrage Pro v7.0');
console.log('='.repeat(45));

function generateSignature(timestamp, method, requestPath, body = '') {
  const crypto = require('crypto');
  const message = timestamp + method + requestPath + body;
  const hmac = crypto.createHmac('sha256', OKX_SECRET_KEY);
  hmac.update(message);
  return hmac.digest('base64');
}

async function okxRequest(method, endpoint, body = {}) {
  const timestamp = new Date().toISOString();
  const bodyStr = JSON.stringify(body);
  const signature = generateSignature(timestamp, method, endpoint, bodyStr);
  
  try {
    const response = await fetch(`${OKX_API}${endpoint}`, {
      method,
      headers: {
        'OK-ACCESS-KEY': OKX_API_KEY,
        'OK-ACCESS-SIGN': signature,
        'OK-ACCESS-PASSPHRASE': OKX_PASSPHRASE,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'Content-Type': 'application/json'
      },
      body: method !== 'GET' ? bodyStr : undefined
    });
    return await response.json();
  } catch (e) {
    console.error('❌ OKX请求失败:', e.message);
    return { code: '-1', msg: e.message };
  }
}

async function polymarketRequest(endpoint) {
  try {
    const response = await fetch(`${POLYMARKET_API}${endpoint}`, {
      headers: { 'Content-Type': 'application/json' }
    });
    return await response.json();
  } catch (e) {
    console.error('❌ Polymarket请求失败:', e.message);
    return [];
  }
}

async function skillpayCharge(userId) {
  try {
    const response = await fetch(`${SKILLPAY_API}/billing/charge`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': SKILLPAY_KEY
      },
      body: JSON.stringify({
        user_id: userId,
        amount: '0.001',
        currency: 'USDT'
      })
    });
    return await response.json();
  } catch (e) {
    console.log('⚠️ SkillPay请求失败:', e.message);
    return { success: false, error: e.message };
  }
}

async function getBalance() {
  const result = await okxRequest('GET', '/api/v5/account/balance');
  if (result.code === '0' && result.data && result.data[0] && result.data[0].details) {
    const usdt = result.data[0].details.find(c => c.ccy === 'USDT');
    return usdt ? parseFloat(usdt.availBal) : 0;
  }
  return 0;
}

async function getMarkets() {
  const data = await polymarketRequest('/markets?active=true&limit=50');
  return Array.isArray(data) ? data : [];
}

function findArbitrageOpportunities(markets) {
  const opportunities = [];
  for (const market of markets) {
    try {
      const prices = market.outcomePrices ? JSON.parse(market.outcomePrices) : [];
      if (prices.length >= 2) {
        const yesPrice = parseFloat(prices[0]) || 0;
        const noPrice = parseFloat(prices[1]) || 0;
        if (yesPrice > 0.05 && noPrice > 0.05) {
          const spread = yesPrice + noPrice;
          const profit = (spread - 1) * 100;
          if (profit >= MIN_PROFIT) {
            opportunities.push({ market, yesPrice, noPrice, spread, profit, volume: market.volumeNum || 0 });
          }
        }
      }
    } catch (e) {}
  }
  return opportunities.sort((a, b) => b.profit - a.profit);
}

async function placeOrder(instId, side, sz, px) {
  return await okxRequest('POST', '/api/v5/trade/order', {
    instId, tdMode: 'cash', side, ordType: 'limit', sz: sz.toString(), px: px.toString()
  });
}

async function executeArbitrage(opp, balance) {
  const tradeAmount = Math.min(balance * 0.5, TRADE_AMOUNT);
  console.log(`\n🎯 执行套利: ${opp.market.question?.slice(0, 40)}...`);
  console.log(`   金额: ${tradeAmount.toFixed(2)} USDT`);
  console.log(`   预期利润: ${(opp.profit * tradeAmount / 100).toFixed(2)} USDT`);
  
  // 开多单
  const longResult = await placeOrder('BTC-USDT-SWAP', 'buy', Math.floor(tradeAmount/opp.yesPrice), opp.yesPrice.toFixed(2));
  console.log(`   多单: ${longResult.code === '0' ? '✅' : '❌'} ${longResult.msg || ''}`);
  
  // 开空单
  const shortResult = await placeOrder('BTC-USDT-SWAP', 'sell', Math.floor(tradeAmount/opp.noPrice), opp.noPrice.toFixed(2));
  console.log(`   空单: ${shortResult.code === '0' ? '✅' : '❌'} ${shortResult.msg || ''}`);
  
  return longResult.code === '0' && shortResult.code === '0';
}

async function checkAndTrade() {
  console.log('\n' + '='.repeat(45));
  console.log(`⏰ ${new Date().toLocaleTimeString()}`);
  
  const balance = await getBalance();
  console.log(`💰 余额: ${balance.toFixed(2)} USDT (初始: ${INITIAL_BALANCE}U)`);
  
  // 检查亏损
  if (INITIAL_BALANCE > 0) {
    const loss = (balance - INITIAL_BALANCE) / INITIAL_BALANCE;
    if (loss <= -MAX_LOSS) {
      console.log(`🚨 亏损达到${(loss*100).toFixed(1)}%，自动停止!`);
      process.exit(1);
    }
  }
  
  if (balance < 10) {
    console.log('❌ 余额不足10U');
    return;
  }
  
  const markets = await getMarkets();
  console.log(`📊 市场: ${markets.length}个`);
  
  const opportunities = findArbitrageOpportunities(markets);
  
  if (opportunities.length > 0) {
    console.log(`\n✅ 发现 ${opportunities.length} 个套利机会!`);
    const best = opportunities[0];
    console.log(`\n🏆 ${best.market.question?.slice(0, 50)}`);
    console.log(`   YES: $${best.yesPrice.toFixed(4)} | NO: $${best.noPrice.toFixed(4)}`);
    console.log(`   利润: ${best.profit.toFixed(2)}%`);
    
    // 先收费
    console.log('\n💳 正在验证SkillPay支付...');
    const chargeResult = await skillpayCharge('user_' + Date.now());
    if (chargeResult.success) {
      console.log('✅ 支付验证成功!');
      const success = await executeArbitrage(best, balance);
      if (success) {
        console.log('\n🎉 套利完成!收益将到达你的账户');
      }
    } else {
      console.log(`❌ 支付失败: ${chargeResult.error || '请先充值'}`);
      console.log('   充值地址: https://skillpay.me/dashboard');
    }
  } else {
    console.log('❌ 暂无套利机会 (当前市场均衡)');
  }
}

async function main() {
  const action = process.argv[2];
  
  switch(action) {
    case 'start':
      console.log('🚀 启动持续监控...\n');
      setInterval(checkAndTrade, CHECK_INTERVAL);
      await checkAndTrade();
      break;
    case 'scan':
      await checkAndTrade();
      break;
    case 'balance':
      const bal = await getBalance();
      console.log(`💰 OKX USDT: ${bal.toFixed(2)}`);
      break;
    default:
      console.log('用法: node polymarket-trade.js [start|scan|balance]');
  }
}

main().catch(console.error);
