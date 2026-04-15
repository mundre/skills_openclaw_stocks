/**
 * mirror.ts — Shadow trading script for Degen Claw Arena agent
 * Polls main Son of Adam (Shekel) agent for new trades/orders and mirrors them
 * on the Arena agent via trade.ts.
 *
 * Usage: npx tsx scripts/mirror.ts
 * Cron:  * /5 * * * * cd ~/dgclaw-skill && npx tsx scripts/mirror.ts >> ~/mirror.log 2>&1
 */

import { execSync } from "child_process";
import * as fs from "fs";
import * as path from "path";
import * as https from "https";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ─── Config ───────────────────────────────────────────────────────────────────

const SHEKEL_API = "https://shekel-skill-backend.onrender.com";
const SHEKEL_KEY = process.env.SHEKEL_API_KEY;
if (!SHEKEL_KEY) {
  console.error("ERROR: SHEKEL_API_KEY not set in .env");
  process.exit(1);
}

// Arena account balance vs main account balance ratio for position sizing
// Arena ~$17-117 / Main ~$1107 → auto-calculated each run
const STATE_FILE = path.join(__dirname, "../.mirror-state.json");

// ─── Types ────────────────────────────────────────────────────────────────────

interface MirrorState {
  lastTradeId: string | null;
  lastOrderIds: string[];
  mirroredPositions: Record<string, { side: string; size: number; leverage: number }>;
}

interface ShekelTrade {
  id: string;
  action: string;
  coin: string;
  side: string;
  size: string;
  price: string;
  closedPnl: string | null;
  error: string | null;
  createdAt: string;
}

interface ShekelOrder {
  coin: string;
  side: string;
  limitPx: string;
  sz: string;
  oid: number;
  reduceOnly: boolean;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function log(msg: string) {
  console.log(`[${new Date().toISOString()}] ${msg}`);
}

function loadState(): MirrorState {
  if (fs.existsSync(STATE_FILE)) {
    return JSON.parse(fs.readFileSync(STATE_FILE, "utf8"));
  }
  return { lastTradeId: null, lastOrderIds: [], mirroredPositions: {} };
}

function saveState(state: MirrorState) {
  fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

function shekelGet(path: string): Promise<any> {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: "shekel-skill-backend.onrender.com",
      path,
      method: "GET",
      headers: { Authorization: `Bearer ${SHEKEL_KEY}` },
    };
    const req = https.request(options, (res) => {
      let data = "";
      res.on("data", (chunk) => (data += chunk));
      res.on("end", () => {
        try { resolve(JSON.parse(data)); }
        catch (e) { reject(new Error(`Parse error: ${data}`)); }
      });
    });
    req.on("error", reject);
    req.end();
  });
}

function runTrade(args: string): string {
  const cmd = `npx tsx ${__dirname}/trade.ts ${args}`;
  log(`Executing: ${cmd}`);
  try {
    const out = execSync(cmd, { cwd: path.join(__dirname, ".."), encoding: "utf8" });
    log(`Result: ${out.trim()}`);
    return out;
  } catch (e: any) {
    log(`Error: ${e.message}`);
    return "";
  }
}

// Normalize coin name: "BTC" → "BTC"
// Returns null for unsupported HIP-3 pairs (xyz:*)
function normalizePair(coin: string): string | null {
  if (coin.includes(":")) {
    log(`Skipping HIP-3 pair ${coin} — not supported by trade.ts`);
    return null;
  }
  return coin.toUpperCase();
}

// Scale arena size proportionally to main account
function scaleSize(mainSize: number, mainBalance: number, arenaBalance: number): number {
  if (mainBalance <= 0) return 10; // fallback minimum
  const ratio = arenaBalance / mainBalance;
  const scaled = mainSize * ratio;
  return Math.max(10, Math.round(scaled * 100) / 100); // min $10
}

// ─── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  log("=== Mirror run started ===");
  const state = loadState();

  // 1. Fetch main agent balances for size scaling
  let mainBalance = 1107;
  let arenaBalance = 100;
  try {
    const mainBalData = await shekelGet("/account/balances");
    mainBalance = parseFloat(mainBalData.marginSummary?.accountValue || "1107");

    // Arena balance via trade.ts balance
    const arenaBalRaw = execSync("npx tsx scripts/trade.ts balance", {
      cwd: path.join(__dirname, ".."), encoding: "utf8"
    });
    const arenaBal = JSON.parse(arenaBalRaw);
    const usdcBal = arenaBal.spot?.balances?.find((b: any) => b.coin === "USDC");
    arenaBalance = parseFloat(usdcBal?.total || "100");
    log(`Balances — Main: $${mainBalance.toFixed(2)}, Arena: $${arenaBalance.toFixed(2)}`);
  } catch (e: any) {
    log(`Balance fetch error: ${e.message}`);
  }

  // 2. Fetch main agent open positions
  let mainPositions: any[] = [];
  try {
    const portfolio = await shekelGet("/account/portfolio");
    mainPositions = portfolio.clearinghouse?.assetPositions || [];
    log(`Main open positions: ${mainPositions.length}`);
  } catch (e: any) {
    log(`Portfolio fetch error: ${e.message}`);
  }

  // 3. Fetch main agent recent trades
  let mainTrades: ShekelTrade[] = [];
  try {
    const tradesData = await shekelGet("/account/trades?limit=20");
    mainTrades = tradesData.trades || [];
    log(`Recent trades fetched: ${mainTrades.length}`);
  } catch (e: any) {
    log(`Trades fetch error: ${e.message}`);
  }

  // 4. Fetch main agent open orders (SL/TP/limits)
  let mainOrders: ShekelOrder[] = [];
  try {
    const ordersData = await shekelGet("/account/orders");
    mainOrders = ordersData.orders || [];
    log(`Open orders fetched: ${mainOrders.length}`);
  } catch (e: any) {
    log(`Orders fetch error: ${e.message}`);
  }

  // 5. Check for new trades since last run
  // Find index of last known trade – everything BEFORE it is new
  const lastIdx = state.lastTradeId 
    ? mainTrades.findIndex(t => t.id === state.lastTradeId)
    : -1;

  const newTrades = lastIdx === -1
    ? [] // first run or lastTradeId not in recent 20 – skip to avoid mass mirror
    : mainTrades.slice(0, lastIdx).filter(t => !t.error && t.id);

  // 6. Process new trades
  for (const trade of newTrades) {
    const pair = normalizePair(trade.coin);
    if (!pair) continue; // skip HIP-3 pairs
    const side = trade.side === "buy" ? "long" : "short";
    const mainSizeUsd = parseFloat(trade.size) * parseFloat(trade.price || "1");
    const arenaSize = scaleSize(mainSizeUsd, mainBalance, arenaBalance);

    log(`New trade detected: ${trade.action} ${pair} ${side} $${mainSizeUsd.toFixed(2)} → Arena: $${arenaSize}`);

    // Map action types
    if (["agent_long", "agent_short", "agent_set_limit", "market_order", "limit_order"].includes(trade.action)) {
      // Open/entry trade
      const leverage = Math.min(5, Math.max(1, Math.round(mainSizeUsd / (mainBalance * 0.15))));
      runTrade(`open --pair ${pair} --side ${side} --size ${arenaSize} --leverage ${leverage}`);
      state.mirroredPositions[pair] = { side, size: arenaSize, leverage };

    } else if (["agent_close", "agent_stop_loss", "agent_take_profit"].includes(trade.action)) {
      // Close trade
      if (state.mirroredPositions[pair]) {
        runTrade(`close --pair ${pair}`);
        delete state.mirroredPositions[pair];
      }
    }
  }

  // 7. Sync SL/TP orders for mirrored positions
  for (const order of mainOrders) {
    const pair = normalizePair(order.coin);
    if (!pair || !state.mirroredPositions[pair]) continue;

    const orderIdStr = order.oid.toString();
    if (state.lastOrderIds.includes(orderIdStr)) continue; // already synced

    log(`Syncing order for ${pair}: side=${order.side} price=${order.limitPx} reduceOnly=${order.reduceOnly}`);

    if (order.reduceOnly) {
      // This is a SL or TP order – apply to arena position
      const isStop = order.side !== (state.mirroredPositions[pair].side === "long" ? "sell" : "buy");
      if (isStop) {
        runTrade(`modify --pair ${pair} --sl ${order.limitPx}`);
      } else {
        runTrade(`modify --pair ${pair} --tp ${order.limitPx}`);
      }
      state.lastOrderIds.push(orderIdStr);
    }
  }

  // 8. Handle position closures – if main has no position but arena does
  const mainPairs = new Set(
    mainPositions
      .filter((p: any) => p.position?.coin)
      .map((p: any) => normalizePair(p.position.coin))
  );
  for (const pair of Object.keys(state.mirroredPositions)) {
    if (!mainPairs.has(pair)) {
      log(`Main closed ${pair} – closing arena position`);
      runTrade(`close --pair ${pair}`);
      delete state.mirroredPositions[pair];
    }
  }

  // 9. Update state
  if (mainTrades.length > 0) {
    state.lastTradeId = mainTrades[0].id;
  }
  // Trim order ID list to last 100
  state.lastOrderIds = state.lastOrderIds.slice(-100);
  saveState(state);

  log("=== Mirror run complete ===\n");
}

main().catch((e) => log(`Fatal error: ${e.message}`));
