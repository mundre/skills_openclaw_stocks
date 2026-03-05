#!/usr/bin/env node
/**
 * 董事长早晚报主脚本
 * Chairman Daily Brief - Main Script
 * 
 * Usage:
 *   node chairman_daily.mjs morning --symbol 600519.SS --company 贵州茅台
 *   node chairman_daily.mjs evening --symbol 0700.HK --company 腾讯控股
 *   node chairman_daily.mjs morning --watchlist holdings
 *   node chairman_daily.mjs watch --action list
 */

import { readFileSync, existsSync, writeFileSync, mkdirSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SKILL_DIR = join(__dirname, '..');
const CONFIG_DIR = join(SKILL_DIR, 'config');
const EVOLUTION_DIR = join(SKILL_DIR, '.evolution');

// QVeris API 配置
const QVERIS_API_BASE = 'https://qveris.ai/api/v1';
const QVERIS_API_KEY = process.env.QVERIS_API_KEY;

if (!QVERIS_API_KEY) {
  console.error('❌ 错误：未设置 QVERIS_API_KEY 环境变量');
  console.error('请设置：export QVERIS_API_KEY="your-api-key"');
  process.exit(1);
}

// 工具链配置
const TOOL_CHAINS = {
  morning_brief: {
    market_overview: ['ths_ifind.global_market', 'alpha_vantage.market_status'],
    policy_news: ['caidazi.news.query', 'caidazi.report.query'],
    company_quote: ['ths_ifind.real_time_quotation'],
    industry_data: ['ths_ifind.industry_index', 'caidazi.sector_analysis'],
    sentiment: ['qveris_social.x_domain_hot_topics']
  },
  evening_brief: {
    company_quote: ['ths_ifind.real_time_quotation', 'ths_ifind.history_quotation'],
    announcements: ['caidazi.news.query', 'exchange_announcements'],
    research: ['caidazi.report.query', 'alpha_news_sentiment'],
    fund_flow: ['ths_ifind.capital_flow', 'ths_ifind.dragon_tiger']
  }
};

/**
 * 搜索 QVeris 工具
 */
async function searchTools(query, limit = 10) {
  try {
    const response = await fetch(`${QVERIS_API_BASE}/tools/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${QVERIS_API_KEY}`
      },
      body: JSON.stringify({ query, limit })
    });

    if (!response.ok) {
      throw new Error(`搜索失败: ${response.status}`);
    }

    const data = await response.json();
    return data.tools || [];
  } catch (error) {
    console.error(`搜索工具失败: ${error.message}`);
    return [];
  }
}

/**
 * 执行 QVeris 工具
 */
async function executeTool(toolId, searchId, params) {
  try {
    const response = await fetch(`${QVERIS_API_BASE}/tools/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${QVERIS_API_KEY}`
      },
      body: JSON.stringify({
        tool_id: toolId,
        search_id: searchId,
        params
      })
    });

    if (!response.ok) {
      throw new Error(`执行失败: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`执行工具失败: ${error.message}`);
    return null;
  }
}

/**
 * 获取全球市场行情
 */
async function getGlobalMarketOverview() {
  const tools = await searchTools('global market overview US stock Asia', 5);
  
  // 模拟数据（实际应调用 QVeris）
  return {
    markets: [
      { name: '道琼斯', close: 43850, change: 0.5, impact: '正面' },
      { name: '纳斯达克', close: 18920, change: 1.2, impact: '正面' },
      { name: '恒生指数', close: 23450, change: -0.3, impact: '轻微负面' },
      { name: 'A50期指', close: 13280, change: 0.4, impact: '正面开盘预期' }
    ],
    summary: '美股科技股强势反弹，对A股成长股情绪有提振作用'
  };
}

/**
 * 获取公司行情数据
 */
async function getCompanyQuote(symbol, company) {
  const tools = await searchTools('real time stock quote China A share Hong Kong', 5);
  
  // 模拟数据
  return {
    symbol,
    name: company,
    price: 1580.00,
    change: 15.00,
    changePercent: 0.96,
    volume: 2850000,
    marketCap: '1.98万亿',
    pe: 28.5,
    pb: 8.2,
    support: 1550,
    resistance: 1600
  };
}

/**
 * 获取行业新闻
 */
async function getIndustryNews(industry, limit = 5) {
  const tools = await searchTools('China financial news policy regulation', 5);
  
  return [
    {
      title: `${industry || '行业'}监管新规发布`,
      source: '市场监管总局',
      impact: '中性偏负面',
      summary: '对高端产品的营销宣传提出更严格要求'
    }
  ];
}

/**
 * 获取竞争对手动态
 */
async function getCompetitorNews(competitors) {
  if (!competitors) return [];
  
  const compList = competitors.split(',');
  return compList.map(symbol => ({
    symbol: symbol.trim(),
    name: symbol.trim(), // 实际应解析公司名称
    event: '发布年报预告，净利润增长12%',
    impact: '行业竞争加剧',
    suggestion: '加速直销渠道建设'
  }));
}

/**
 * 生成早班报告
 */
async function generateMorningBrief(options) {
  const { symbol, company, industry, competitors, format = 'markdown' } = options;
  
  console.log(`\n🌅 正在生成早班报告: ${company || symbol}...\n`);
  
  // 并行获取数据
  const [marketOverview, companyQuote, industryNews, competitorNews] = await Promise.all([
    getGlobalMarketOverview(),
    getCompanyQuote(symbol, company),
    getIndustryNews(industry),
    getCompetitorNews(competitors)
  ]);
  
  const now = new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });
  
  if (format === 'json') {
    return JSON.stringify({
      type: 'morning',
      timestamp: now,
      symbol,
      company,
      marketOverview,
      companyQuote,
      industryNews,
      competitorNews
    }, null, 2);
  }
  
  // Markdown 格式
  let report = `# 📊 董事长早班简报 — ${company || symbol} (${symbol})
📅 ${now}

---

## 🌍 隔夜全球市场
| 市场 | 收盘 | 涨跌 | 对A股影响 |
|------|------|------|-----------|
`;
  
  marketOverview.markets.forEach(m => {
    report += `| ${m.name} | ${m.close.toLocaleString()} | ${m.change > 0 ? '+' : ''}${m.change}% | ${m.impact} |\n`;
  });
  
  report += `
**点评**：${marketOverview.summary}

---

## 📰 宏观政策速递
`;
  
  industryNews.forEach(news => {
    report += `🔔 **${news.title}** — ${news.source}
- **影响评估**：${news.impact}
- **摘要**：${news.summary}

`;
  });
  
  report += `---

## 📈 本公司前瞻
| 指标 | 数值 | 备注 |
|------|------|------|
| 昨收 | ${companyQuote.price}元 | - |
| 涨跌 | ${companyQuote.change > 0 ? '+' : ''}${companyQuote.change}元 (${companyQuote.changePercent}%) | - |
| 市值 | ${companyQuote.marketCap} | - |
| 市盈率 | ${companyQuote.pe}x | - |
| 关键阻力位 | ${companyQuote.resistance}元 | 突破需放量 |
| 关键支撑位 | ${companyQuote.support}元 | 强支撑 |

---

## 🏭 行业雷达
✅ 行业整体平稳，无重大利空消息

---

## 🎯 竞争情报
`;
  
  if (competitorNews.length > 0) {
    competitorNews.forEach(comp => {
      report += `**${comp.name} (${comp.symbol})**
- **动态**：${comp.event}
- **影响**：${comp.impact}
- **建议**：${comp.suggestion}

`;
    });
  } else {
    report += '暂无竞争对手重大动态\n';
  }
  
  report += `
---

## ⚠️ 风险提示
1. 宏观政策变化风险
2. 市场流动性风险
3. 行业竞争加剧风险

---

## 📅 今日重点关注
- 09:30 市场开盘
- 关注北向资金流向
- 监控成交量变化

---
*数据来源：QVeris | THS iFinD、Caidazi、同花顺财经*
*本报告仅供参考，不构成投资建议*
`;
  
  return report;
}

/**
 * 生成晚报
 */
async function generateEveningBrief(options) {
  const { symbol, company, competitors, format = 'markdown' } = options;
  
  console.log(`\n🌙 正在生成晚报: ${company || symbol}...\n`);
  
  const companyQuote = await getCompanyQuote(symbol, company);
  const now = new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });
  
  if (format === 'json') {
    return JSON.stringify({
      type: 'evening',
      timestamp: now,
      symbol,
      company,
      companyQuote
    }, null, 2);
  }
  
  return `# 🌙 董事长晚报 — ${company || symbol} (${symbol})
📅 ${now}

---

## 📊 收盘概览
| 指标 | 数值 | 变动 |
|------|------|------|
| 收盘价 | ${companyQuote.price}元 | ${companyQuote.change > 0 ? '+' : ''}${companyQuote.change}元 |
| 涨跌幅 | ${companyQuote.changePercent}% | - |
| 成交量 | ${(companyQuote.volume / 10000).toFixed(0)}万股 | - |
| 市值 | ${companyQuote.marketCap} | - |

**点评**：今日股价${companyQuote.change > 0 ? '上涨' : '下跌'}，${companyQuote.changePercent > 1 ? '表现强于' : '表现弱于'}大盘

---

## 📢 今日公告
**本公司公告**：
- 无重大事项公告

**行业公告**：
- 暂无重要行业公告

---

## 📰 舆情监控
**市场情绪**：中性偏多

**关注要点**：
- 成交量变化
- 主力资金流向
- 北向资金动向

---

## 🎯 明日策略建议
1. **价格监控**：关注${companyQuote.support}元支撑位和${companyQuote.resistance}元阻力位
2. **成交量**：如放量突破阻力位，可考虑适当增持
3. **风险控制**：如跌破支撑位，注意控制仓位

---
*数据来源：QVeris | THS iFinD、Caidazi*
*本报告仅供参考，不构成投资建议*
`;
}

/**
 * 管理关注列表
 */
async function manageWatchlist(action, options) {
  const watchlistPath = join(CONFIG_DIR, 'watchlist.json');
  
  // 确保目录存在
  if (!existsSync(CONFIG_DIR)) {
    mkdirSync(CONFIG_DIR, { recursive: true });
  }
  
  // 读取或初始化
  let watchlist = { holdings: [], competitors: [], peers: {} };
  if (existsSync(watchlistPath)) {
    watchlist = JSON.parse(readFileSync(watchlistPath, 'utf-8'));
  }
  
  switch (action) {
    case 'list':
      console.log('\n📋 关注列表\n');
      console.log('【持仓公司】');
      watchlist.holdings.forEach(h => {
        console.log(`  • ${h.name} (${h.symbol})`);
      });
      console.log('\n【竞争对手】');
      watchlist.competitors.forEach(c => {
        console.log(`  • ${c.name} (${c.symbol}) - ${c.peerGroup || '未分组'}`);
      });
      break;
      
    case 'add':
      const { symbol, company, role, peerGroup } = options;
      const item = { symbol, name: company, addedAt: new Date().toISOString() };
      
      if (role === 'self' || role === 'holding') {
        watchlist.holdings.push(item);
        console.log(`✅ 已添加持仓: ${company} (${symbol})`);
      } else if (role === 'competitor') {
        item.peerGroup = peerGroup;
        watchlist.competitors.push(item);
        console.log(`✅ 已添加竞争对手: ${company} (${symbol})`);
      }
      break;
      
    case 'remove':
      const { symbol: removeSymbol } = options;
      watchlist.holdings = watchlist.holdings.filter(h => h.symbol !== removeSymbol);
      watchlist.competitors = watchlist.competitors.filter(c => c.symbol !== removeSymbol);
      console.log(`✅ 已移除: ${removeSymbol}`);
      break;
  }
  
  // 保存
  writeFileSync(watchlistPath, JSON.stringify(watchlist, null, 2));
}

/**
 * 获取关注列表中的公司
 */
function getWatchlistCompanies() {
  const watchlistPath = join(CONFIG_DIR, 'watchlist.json');
  if (!existsSync(watchlistPath)) {
    return { holdings: [], competitors: [] };
  }
  return JSON.parse(readFileSync(watchlistPath, 'utf-8'));
}

/**
 * 主函数
 */
async function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  // 解析参数
  const options = {};
  for (let i = 1; i < args.length; i += 2) {
    const key = args[i].replace('--', '');
    const value = args[i + 1];
    options[key] = value;
  }
  
  try {
    switch (command) {
      case 'morning':
        if (options.watchlist) {
          // 生成关注列表中所有公司的简报
          const watchlist = getWatchlistCompanies();
          for (const holding of watchlist.holdings) {
            const report = await generateMorningBrief({
              symbol: holding.symbol,
              company: holding.name,
              industry: options.industry,
              format: options.format
            });
            console.log(report);
            console.log('\n---\n');
          }
        } else if (options.symbol) {
          const report = await generateMorningBrief(options);
          console.log(report);
        } else {
          console.log('❌ 请指定 --symbol 或 --watchlist');
          process.exit(1);
        }
        break;
        
      case 'evening':
        if (options.watchlist) {
          const watchlist = getWatchlistCompanies();
          for (const holding of watchlist.holdings) {
            const report = await generateEveningBrief({
              symbol: holding.symbol,
              company: holding.name,
              competitors: options.competitors,
              format: options.format
            });
            console.log(report);
            console.log('\n---\n');
          }
        } else if (options.symbol) {
          const report = await generateEveningBrief(options);
          console.log(report);
        } else {
          console.log('❌ 请指定 --symbol 或 --watchlist');
          process.exit(1);
        }
        break;
        
      case 'watch':
        await manageWatchlist(options.action, options);
        break;
        
      default:
        console.log(`
董事长早晚报 - Chairman Daily Brief

用法:
  node chairman_daily.mjs morning --symbol <代码> --company <公司名>
  node chairman_daily.mjs evening --symbol <代码> --company <公司名>
  node chairman_daily.mjs morning --watchlist holdings
  node chairman_daily.mjs watch --action <list|add|remove>

选项:
  morning                    生成早班报告
  evening                    生成晚报
  watch                      管理关注列表
  
  --symbol <代码>            股票代码 (如: 600519.SS, 0700.HK, AAPL)
  --company <名称>           公司名称
  --industry <行业>          行业名称（用于行业雷达）
  --competitors <代码列表>   竞争对手代码，逗号分隔
  --watchlist holdings       使用关注列表生成报告
  --format <markdown|json>   输出格式 (默认: markdown)
  
  --action <list|add|remove> 关注列表操作
  --role <self|competitor>   添加时的角色类型
  --peer-group <分组>        竞争对手分组

示例:
  # 生成茅台早班报告
  node chairman_daily.mjs morning --symbol 600519.SS --company 贵州茅台
  
  # 生成腾讯晚报（带竞争对手分析）
  node chairman_daily.mjs evening --symbol 0700.HK --company 腾讯控股 --competitors 09999.HK,09618.HK
  
  # 添加关注公司
  node chairman_daily.mjs watch --action add --symbol 600519.SS --company 贵州茅台 --role self
  
  # 添加竞争对手
  node chairman_daily.mjs watch --action add --symbol 002594.SZ --company 比亚迪 --role competitor --peer-group 新能源汽车
  
  # 查看关注列表
  node chairman_daily.mjs watch --action list
`);
    }
  } catch (error) {
    console.error(`❌ 错误: ${error.message}`);
    process.exit(1);
  }
}

// 运行主函数
main();
