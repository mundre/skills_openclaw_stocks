/**
 * Node.js Messenger CLI — FLO Blockchain Transactions
 *
 * Usage:
 *   node flo_node.js --action balance [--address <FLO_ID>]
 *   node flo_node.js --action send --to <FLO_ID> --amount <FLO> [--memo <TEXT>]
 *   node flo_node.js --action history [--address <FLO_ID>] [--limit <N>]
 *
 * Security: Requires FLO_PRIVATE_KEY environment variable.
 *
 * Note: 'balance' and 'history' work for any address (no private key needed for reads,
 *       but FLO_PRIVATE_KEY is still required to derive your own address if --address is omitted).
 *       'send' signs and broadcasts a real on-chain transaction — funds move immediately.
 */

'use strict';

const { getPrivateKey } = require('./node_shared');

// Load FLO libraries without full cloud init (we use floBlockchainAPI directly)
(function bootstrap() {
    const fs = require('fs');
    const vm = require('vm');
    const path = require('path');
    const { WebSocket } = require('ws');
    global.WebSocket = WebSocket;
    global.floGlobals = { blockchain: "FLO", application: "messenger", adminID: "FMRsefPydWznGWneLqi4ABeQAJeFvtS3aQ" };
    Object.defineProperty(global, 'navigator', { value: { userAgent: "node", plugins: [], mimeTypes: [], cookieEnabled: false, language: "en" }, writable: true, configurable: true });
    Object.defineProperty(global, 'screen', { value: { height: 1080, width: 1920 }, writable: true, configurable: true });
    global.window = global;
    global.require = require;
    if (typeof global.btoa === 'undefined') {
        global.btoa = s => Buffer.from(s, 'binary').toString('base64');
        global.atob = s => Buffer.from(s, 'base64').toString('binary');
    }
    function loadScript(fp) { vm.runInThisContext(fs.readFileSync(path.join(__dirname, fp), 'utf8'), { filename: fp }); }
    loadScript('scripts/lib.js');
    loadScript('scripts/floCrypto.js');
    loadScript('scripts/floBlockchainAPI.js');
})();

// ── Parse CLI arguments ──

function parseArgs() {
    const args = process.argv.slice(2);
    const parsed = { limit: 20, memo: '' };
    for (let i = 0; i < args.length; i++) {
        switch (args[i]) {
            case '--action': parsed.action = args[++i]; break;
            case '--to': parsed.to = args[++i]; break;
            case '--address': parsed.address = args[++i]; break;
            case '--amount': parsed.amount = parseFloat(args[++i]); break;
            case '--memo': parsed.memo = args[++i]; break;
            case '--limit': parsed.limit = parseInt(args[++i], 10); break;
        }
    }
    return parsed;
}

// ── Actions ──

/**
 * Show FLO balance for an address.
 */
async function showBalance(address) {
    console.log(`\n[flo] Fetching balance for: ${address}`);
    const balance = await floBlockchainAPI.getBalance(address);
    console.log(`\n  Address : ${address}`);
    console.log(`  Balance : ${parseFloat(balance).toFixed(8)} FLO\n`);
}

/**
 * Send FLO tokens from your address to a receiver.
 * The memo is embedded in the transaction as floData (on-chain, public).
 */
async function sendFLO(senderAddr, privateKey, receiverAddr, amount, memo) {
    // ── Validate inputs before any network call ──
    if (!receiverAddr) throw new Error('--to (receiver address) is required.');
    if (!amount || isNaN(amount) || amount <= 0) throw new Error('--amount must be a positive number (in FLO).');

    // Validate address format
    if (!floCrypto.validateAddr(receiverAddr)) {
        throw new Error(`Invalid receiver address: ${receiverAddr}`);
    }

    console.log(`\n[flo] Preparing transaction...`);
    console.log(`  From   : ${senderAddr}`);
    console.log(`  To     : ${receiverAddr}`);
    console.log(`  Amount : ${amount} FLO`);
    if (memo) console.log(`  Memo   : ${memo}`);

    // Check balance first
    const balance = parseFloat(await floBlockchainAPI.getBalance(senderAddr));
    console.log(`\n[flo] Current balance: ${balance.toFixed(8)} FLO`);

    if (balance < amount) {
        throw new Error(`Insufficient balance. Have ${balance} FLO, need ${amount} FLO.`);
    }

    console.log('[flo] Broadcasting transaction...');

    // sendTx: creates, signs, and broadcasts in one step
    const txid = await floBlockchainAPI.sendTx(
        senderAddr,
        receiverAddr,
        amount,
        privateKey,
        memo   // embedded as floData (on-chain optional text field, max ~1040 chars)
    );

    console.log(`\n[flo] Transaction broadcast!`);
    console.log(`  TXID     : ${txid}`);
    console.log(`  Explorer : https://flosight.dpow.network/tx/${txid}\n`);
}

/**
 * Show transaction history for an address using readTxs (returns full tx objects).
 * readData returns floData strings only — readTxs gives sender/receiver/amount.
 */
async function showHistory(address, limit) {
    console.log(`\n[flo] Fetching transaction history for: ${address}`);

    // readTxs returns { txs: [], totalPages, page, ... } with full tx objects
    const response = await floBlockchainAPI.readTxs(address, {
        confirmed: true,
        pageSize: limit
    });

    const txs = response.txs || [];

    if (txs.length === 0) {
        console.log('[flo] No transactions found.\n');
        return;
    }

    console.log(`\n${'='.repeat(65)}`);
    console.log(`  TRANSACTIONS  (${txs.length} shown, address: ${address})`);
    console.log('='.repeat(65));

    for (const tx of txs) {
        const date = tx.blockTime ? new Date(tx.blockTime * 1000).toLocaleString() : 'pending';

        // Determine if sent or received relative to the queried address
        const isSender = tx.vin && tx.vin.some(v => v.addresses && v.addresses[0] === address);

        // Sum amounts going to/from the address
        let netAmt = 0;
        if (tx.vout) {
            tx.vout.forEach(out => {
                if (out.scriptPubKey && out.scriptPubKey.addresses && out.scriptPubKey.addresses[0] === address)
                    netAmt += parseFloat(out.value || 0);
            });
        }

        const direction = isSender ? 'SENT' : 'RECV';
        const floData = tx.floData ? `  Memo   : ${tx.floData}` : '';

        console.log(`\n  ${direction}  ${date}`);
        console.log(`  TXID   : ${tx.txid}`);
        if (isSender && tx.vout) {
            // Show who received
            tx.vout.filter(o => o.scriptPubKey && o.scriptPubKey.addresses && o.scriptPubKey.addresses[0] !== address)
                .forEach(o => console.log(`  To     : ${o.scriptPubKey.addresses[0]}  (${parseFloat(o.value).toFixed(8)} FLO)`));
        } else {
            // Show who sent
            if (tx.vin && tx.vin[0] && tx.vin[0].addresses)
                console.log(`  From   : ${tx.vin[0].addresses[0]}`);
            console.log(`  Amount : ${netAmt.toFixed(8)} FLO`);
        }
        if (floData) console.log(floData);
    }

    console.log(`\n${'='.repeat(65)}`);
    console.log(`  Full history: https://flosight.dpow.network/address/${address}\n`);
}


// ── Main ──

async function main() {
    try {
        const args = parseArgs();

        switch (args.action) {
            case 'balance': {
                // Can look up any address; if none given, derive from private key
                let address = args.address;
                if (!address) {
                    const privateKey = getPrivateKey();
                    address = floCrypto.getFloID(privateKey);
                }
                await showBalance(address);
                break;
            }

            case 'send': {
                const privateKey = getPrivateKey();
                const senderAddr = floCrypto.getFloID(privateKey);
                await sendFLO(senderAddr, privateKey, args.to, args.amount, args.memo);
                break;
            }

            case 'history': {
                let address = args.address;
                if (!address) {
                    const privateKey = getPrivateKey();
                    address = floCrypto.getFloID(privateKey);
                }
                await showHistory(address, args.limit);
                break;
            }

            default:
                console.log(`
Messenger FLO Transactions (Node.js)

Usage: node flo_node.js --action <action> [options]

Actions:
  balance  [--address <FLO_ID>]           Show FLO balance (defaults to your address)
  send      --to <FLO_ID>                 Send FLO to an address
            --amount <FLO>                Amount in FLO (e.g. 1.5)
           [--memo <TEXT>]                Optional on-chain memo (public, stored on blockchain)
  history  [--address <FLO_ID>]           Show transaction history (defaults to your address)
           [--limit <N>]                  Number of entries (default: 20)

Examples:
  node flo_node.js --action balance
  node flo_node.js --action send --to FQxfoLm4j... --amount 2.5 --memo "payment"
  node flo_node.js --action history --limit 10

Prerequisites:
  FLO_PRIVATE_KEY environment variable must be set (not needed for balance/history with --address).

Warning:
  'send' broadcasts a real on-chain transaction. Funds move immediately and cannot be reversed.
  The --memo text is stored publicly on the FLO blockchain.
`);
        }

    } catch (error) {
        console.error('[error]', error.message || error);
        process.exitCode = 1;
    }

    setTimeout(() => process.exit(process.exitCode || 0), 300);
}

main();
