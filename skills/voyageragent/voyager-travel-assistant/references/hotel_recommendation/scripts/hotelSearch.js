#!/usr/bin/env node

/**
 * 用法:
 *   node hotelSearch.js '[{"subQuery":"大阪酒店推荐","checkInDate":"2026-04-01","checkOutDate":"2026-04-07","city":"大阪","country":"日本","nearby":"梅田"}]'
 */

const { execSync } = require('child_process');

if (process.argv.length < 3) {
  console.error('❌ 请提供查询JSON数组参数');
  process.exit(1);
}

const queryString = process.argv[2];

const payload = JSON.stringify({
  token: "003d2b7d-1ef9-4827-ab9b-cae765689f9d",
  botId: "2026030610103389649",
  bizUserId: "2107220265020227",
  chatContent: { contentType: "TEXT", text: queryString },
  botVariables: { userId: "2107220265020227", serviceType: "RECALL_hotel" },
  stream: false
});

const cmd = `curl -sS -X POST 'https://ibotservice.alipayplus.com/almpapi/v1/message/chat' \
  -H 'Content-Type: application/json' \
  --data-raw '${payload.replace(/'/g, `'\\''`)}'`;

process.stdout.write(execSync(cmd, { stdio: ['ignore', 'pipe', 'inherit'] }));
