/**
 * cost_guard.js — AI API Cost Monitoring and Optimization
 * 
 * Tracks costs, estimates spend, suggests optimizations.
 * Supports OpenAI, Anthropic, Google, and custom pricing.
 * 
 * Usage: node cost_guard.js <command> [args...]
 * Commands:
 *   init [budget]        Initialize cost tracking with budget
 *   track <tokens> <model>  Track token usage
 *   status               Show current cost status
 *   compare <tokens>     Compare costs across providers
 *   suggest              Get cost optimization suggestions
 *   alert <threshold>    Set budget alert threshold
 *   report [period]      Generate cost report
 */

const fs = require('fs');
const path = require('path');

// ── Pricing (per 1M tokens, USD) ─────────────────────────────────────────────
const PRICING = {
  'gpt-4o': { input: 2.50, output: 10.00 },
  'gpt-4o-mini': { input: 0.15, output: 0.60 },
  'gpt-4-turbo': { input: 10.00, output: 30.00 },
  'gpt-3.5-turbo': { input: 0.50, output: 1.50 },
  'claude-3.5-sonnet': { input: 3.00, output: 15.00 },
  'claude-3-opus': { input: 15.00, output: 75.00 },
  'claude-3-haiku': { input: 0.25, output: 1.25 },
  'gemini-1.5-pro': { input: 1.25, output: 5.00 },
  'gemini-1.5-flash': { input: 0.075, output: 0.30 },
  'gemini-pro': { input: 0.50, output: 1.50 },
};

const COST_FILE = '.cost-guard.json';
const DEFAULT_BUDGET = 100; // $100 default monthly budget

// ── Cost Storage ────────────────────────────────────────────────────────────
function loadCosts() {
  if (!fs.existsSync(COST_FILE)) {
    return { budget: DEFAULT_BUDGET, spent: 0, tokenLog: [], alertThreshold: 0.80 };
  }
  try { return JSON.parse(fs.readFileSync(COST_FILE, 'utf8')); }
  catch { return { budget: DEFAULT_BUDGET, spent: 0, tokenLog: [], alertThreshold: 0.80 }; }
}

function saveCosts(costs) {
  fs.writeFileSync(COST_FILE, JSON.stringify(costs, null, 2));
}

// ── Cost Calculation ────────────────────────────────────────────────────────
function calculateCost(tokens, model, type = 'input') {
  const p = PRICING[model] || PRICING['gpt-4o-mini'];
  const rate = type === 'output' ? p.output : p.input;
  return (tokens / 1000000) * rate;
}

function formatCost(usd) {
  if (usd < 0.01) return `$${(usd * 100).toFixed(2)}¢`;
  if (usd < 1) return `$${usd.toFixed(4)}`;
  return `$${usd.toFixed(2)}`;
}

function formatTokens(n) {
  if (n < 1000) return `${n}`;
  if (n < 1000000) return `${(n / 1000).toFixed(1)}K`;
  return `${(n / 1000000).toFixed(2)}M`;
}

// ── Commands ───────────────────────────────────────────────────────────────
function cmdInit(budget) {
  const costs = loadCosts();
  costs.budget = parseFloat(budget) || DEFAULT_BUDGET;
  costs.spent = 0;
  costs.tokenLog = [];
  const now = new Date().toISOString();
  costs.periodStart = now;
  saveCosts(costs);
  console.log(`\n✅ Cost guard initialized`);
  console.log(`   Budget: $${costs.budget}/month`);
  console.log(`   Period: ${now.slice(0, 10)}\n`);
}

function cmdTrack(tokens, model) {
  const costs = loadCosts();
  const t = parseInt(tokens) || 0;
  const m = model || 'gpt-4o-mini';
  
  // Assume 70% input, 30% output ratio for simplicity
  const inputCost = calculateCost(t * 0.7, m, 'input');
  const outputCost = calculateCost(t * 0.3, m, 'output');
  const totalCost = inputCost + outputCost;
  
  costs.spent += totalCost;
  costs.tokenLog.push({
    timestamp: new Date().toISOString(),
    tokens: t,
    model: m,
    cost: totalCost,
  });
  
  saveCosts(costs);
  
  const percent = (costs.spent / costs.budget * 100).toFixed(1);
  console.log(`\n📊 Tracked: ${formatTokens(t)} tokens @ ${m}`);
  console.log(`   Cost: ${formatCost(totalCost)}`);
  console.log(`   Total spent: ${formatCost(costs.spent)} (${percent}% of budget)`);
  
  if (costs.spent >= costs.budget * costs.alertThreshold) {
    console.log(`   ⚠️  ALERT: Budget threshold reached!`);
  }
  console.log();
}

function cmdStatus() {
  const costs = loadCosts();
  const percent = costs.budget > 0 ? (costs.spent / costs.budget * 100) : 0;
  const remaining = costs.budget - costs.spent;
  
  console.log(`\n## Cost Guard Status\n`);
  console.log(`Budget: $${costs.budget}/month`);
  console.log(`Spent: ${formatCost(costs.spent)} (${percent.toFixed(1)}%)`);
  console.log(`Remaining: ${formatCost(Math.max(0, remaining))}`);
  
  if (costs.tokenLog.length > 0) {
    const totalTokens = costs.tokenLog.reduce((a, e) => a + e.tokens, 0);
    console.log(`\nToken Usage:`);
    console.log(`  Total: ${formatTokens(totalTokens)} tokens`);
    console.log(`  Calls: ${costs.tokenLog.length}`);
    console.log(`  Avg per call: ${formatTokens(totalTokens / costs.tokenLog.length)}`);
  }
  
  // Alert status
  if (costs.spent >= costs.budget) {
    console.log(`\n🔴 BUDGET EXCEEDED!`);
  } else if (costs.spent >= costs.budget * costs.alertThreshold) {
    console.log(`\n🟡 Warning: ${(costs.alertThreshold * 100).toFixed(0)}% budget threshold reached`);
  } else {
    console.log(`\n🟢 Budget OK`);
  }
  console.log();
}

function cmdCompare(tokens) {
  const t = parseInt(tokens) || 1000;
  console.log(`\n## Cost Comparison: ${formatTokens(t)} tokens\n`);
  console.log(`Model                  Input      Output     Total      Monthly*`);
  console.log(`─────────────────────────────────────────────────────────────`);
  
  const models = Object.keys(PRICING).sort((a, b) => {
    const pa = PRICING[a], pb = PRICING[b];
    return (pa.input + pa.output) - (pb.input + pb.output);
  });
  
  for (const m of models) {
    const p = PRICING[m];
    const inputCost = calculateCost(t * 0.7, m, 'input');
    const outputCost = calculateCost(t * 0.3, m, 'output');
    const total = inputCost + outputCost;
    const monthly = total * 30 * 100; // Assume 100 calls/day
    
    console.log(`${m.padEnd(22)} $${p.input.toFixed(2).padStart(6)}/M  $${p.output.toFixed(2).padStart(6)}/M  ${formatCost(total).padStart(8)}  ${formatCost(monthly).padStart(10)}`);
  }
  console.log(`─────────────────────────────────────────────────────────────`);
  console.log(`* Estimated: 100 calls/day × 30 days\n`);
  
  // Recommendation
  const cheapest = models[0];
  const bestValue = models.find(m => m.includes('gpt-4o-mini') || m.includes('haiku')) || models[0];
  console.log(`💡 Cheapest: ${cheapest}`);
  console.log(`💡 Best value: ${bestValue}`);
  console.log();
}

function cmdSuggest() {
  const costs = loadCosts();
  const suggestions = [];
  
  if (costs.tokenLog.length > 0) {
    const avgTokens = costs.tokenLog.reduce((a, e) => a + e.tokens, 0) / costs.tokenLog.length;
    const avgCost = costs.spent / costs.tokenLog.length;
    
    // High token usage
    if (avgTokens > 5000) {
      const savedPerCall = calculateCost(avgTokens * 0.3, 'gpt-4o-mini') - calculateCost(avgTokens * 0.3, 'claude-3-haiku');
      suggestions.push({
        priority: 'high',
        action: 'Switch to cheaper model for simple tasks',
        saving: `Save ${formatCost(savedPerCall * costs.tokenLog.length)}/period`,
      });
    }
    
    // High cost relative to budget
    if (costs.spent > costs.budget * 0.5) {
      suggestions.push({
        priority: 'high', 
        action: 'Implement token caching for repeated queries',
        saving: 'Save 30-50% on input tokens',
      });
    }
    
    // Frequent small calls
    if (costs.tokenLog.length > 100 && avgTokens < 500) {
      suggestions.push({
        priority: 'medium',
        action: 'Batch small requests into larger API calls',
        saving: 'Reduce per-call overhead by 20-40%',
      });
    }
    
    // No caching detected
    suggestions.push({
      priority: 'medium',
      action: 'Use prompt caching (Claude) or context caching (Gemini)',
      saving: 'Save 50-90% on repeated context',
    });
    
    // Streaming
    suggestions.push({
      priority: 'low',
      action: 'Use streaming to process responses incrementally',
      saving: 'Improve perceived latency',
    });
  } else {
    suggestions.push({
      priority: 'info',
      action: 'Track some token usage first to get personalized suggestions',
      saving: 'Run: cost_guard.js track <tokens> <model>',
    });
  }
  
  console.log(`\n## Cost Optimization Suggestions\n`);
  for (const s of suggestions) {
    const badge = s.priority === 'high' ? '🔴' : s.priority === 'medium' ? '🟡' : '🟢';
    console.log(`${badge} [${s.priority.toUpperCase()}] ${s.action}`);
    console.log(`   ${s.saving}\n`);
  }
}

function cmdAlert(threshold) {
  const costs = loadCosts();
  costs.alertThreshold = parseFloat(threshold) || 0.80;
  saveCosts(costs);
  console.log(`\n✅ Alert threshold set to ${(costs.alertThreshold * 100).toFixed(0)}%`);
  console.log(`   You will be alerted when spending reaches ${formatCost(costs.budget * costs.alertThreshold)}\n`);
}

function cmdReport(period) {
  const costs = loadCosts();
  const days = period === 'week' ? 7 : period === 'month' ? 30 : 30;
  
  // Filter by period
  const cutoff = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();
  const entries = costs.tokenLog.filter(e => e.timestamp >= cutoff);
  
  const totalCost = entries.reduce((a, e) => a + e.cost, 0);
  const totalTokens = entries.reduce((a, e) => a + e.tokens, 0);
  const calls = entries.length;
  
  console.log(`\n## Cost Report (${period || 'month'})\n`);
  console.log(`Period: ${days} days`);
  console.log(`Calls: ${calls}`);
  console.log(`Tokens: ${formatTokens(totalTokens)}`);
  console.log(`Cost: ${formatCost(totalCost)}`);
  console.log(`Avg per call: ${formatCost(totalCost / Math.max(1, calls))}`);
  
  // By model breakdown
  const byModel = {};
  for (const e of entries) {
    if (!byModel[e.model]) byModel[e.model] = { calls: 0, tokens: 0, cost: 0 };
    byModel[e.model].calls++;
    byModel[e.model].tokens += e.tokens;
    byModel[e.model].cost += e.cost;
  }
  
  if (Object.keys(byModel).length > 0) {
    console.log(`\nBy Model:`);
    for (const [m, stats] of Object.entries(byModel)) {
      console.log(`  ${m}: ${stats.calls} calls, ${formatTokens(stats.tokens)}, ${formatCost(stats.cost)}`);
    }
  }
  console.log();
}

// ── Main ─────────────────────────────────────────────────────────────────────
const [,, cmd, ...args] = process.argv;

const COMMANDS = {
  init: cmdInit,
  track: cmdTrack,
  status: cmdStatus,
  compare: cmdCompare,
  suggest: cmdSuggest,
  alert: cmdAlert,
  report: cmdReport,
};

if (!cmd || !COMMANDS[cmd] || cmd === 'help') {
  console.log(`cost_guard.js — AI API Cost Monitoring and Optimization

Usage: node cost_guard.js <command> [args...]

Commands:
  init [budget]        Initialize cost tracking (default: $100/month)
  track <tokens> <model> Track token usage
  status               Show current cost status
  compare <tokens>     Compare costs across providers
  suggest              Get cost optimization suggestions
  alert <threshold>    Set budget alert threshold (default: 0.80)
  report [week|month]  Generate cost report

Supported Models:
  OpenAI: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo
  Anthropic: claude-3.5-sonnet, claude-3-opus, claude-3-haiku
  Google: gemini-1.5-pro, gemini-1.5-flash, gemini-pro

Examples:
  node cost_guard.js init 50
  node cost_guard.js track 2500 gpt-4o-mini
  node cost_guard.js status
  node cost_guard.js compare 5000
`);
  process.exit(0);
}

COMMANDS[cmd](...args);
