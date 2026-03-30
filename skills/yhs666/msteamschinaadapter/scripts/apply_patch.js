/**
 * OpenClaw MS Teams China Adapter Patch Script v7
 *
 * 自动修补 OpenClaw msteams 扩展，支持 Microsoft Teams 中国区 (世纪互联/21Vianet)
 *
 * 特性:
 * - 按内容 marker 定位文件（哈希文件名完全兼容，自动适配 src-CfmuZgBM.js 等）
 * - 幂等：已打补丁自动跳过
 * - 双向：同时处理原始代码和已被部分补丁的代码
 * - 每次补丁从磁盘重读，确保跨补丁一致性
 */

const fs = require('fs');
const path = require('path');

// ===== 兼容: 支持 OPENCLAW_DIST 环境变量覆盖 =====
const OPENCLAW_DIST = process.env.OPENCLAW_DIST
  || '/home/yang/.nvm/versions/node/v24.14.1/lib/node_modules/openclaw/dist';

// ===== 构建文件索引（仅用于 locateFile，marker 搜索）=====
console.log('Indexing dist files...');
const fileIndex = {};
for (const file of fs.readdirSync(OPENCLAW_DIST).filter(f => f.endsWith('.js') && !f.endsWith('.map'))) {
  fileIndex[file] = fs.readFileSync(path.join(OPENCLAW_DIST, file), 'utf8');
}
const fileList = Object.entries(fileIndex);
console.log(`  ${fileList.length} files indexed\n`);

// ===== 通过 marker 定位文件（哈希文件名完全兼容）=====
function locateFile(markers) {
  for (const [file, content] of fileList) {
    if (markers.every(m => content.includes(m))) {
      return { file, content };
    }
  }
  return null;
}

// ===== 补丁引擎 =====
// locateFile 用索引（只读一次每个文件）
// applyPatch 每次从磁盘重读，保证看到之前补丁的结果
function applyPatch(patch) {
  const located = locateFile(patch.findFile.markers);
  if (!located) return 'not_found';

  const { file } = located;
  // 从磁盘重读 — 确保看到之前补丁对此文件的修改
  const fileContent = fs.readFileSync(path.join(OPENCLAW_DIST, file), 'utf8');

  if (fileContent.includes(patch.newText)) return 'already';

  if (fileContent.includes(patch.oldText)) {
    const newContent = fileContent.replace(patch.oldText, patch.newText);
    fs.writeFileSync(path.join(OPENCLAW_DIST, file), newContent);
    return 'patched';
  }

  if (patch.altText) {
    for (const alt of patch.altText) {
      if (alt.old !== alt.new && fileContent.includes(alt.old)) {
        const newContent = fileContent.replace(alt.old, alt.new);
        fs.writeFileSync(path.join(OPENCLAW_DIST, file), newContent);
        return 'patched_alt';
      }
    }
  }

  return 'missing';
}

// ===== 补丁定义 =====
// 所有 oldText 均已在当前 dist 文件中验证存在
// marker 只使用内容特征（函数名、字符串字面量等），不依赖哈希文件名

const patches = [

  // === graph-users: buildMSTeamsAuthConfig ===
  {
    name: 'buildMSTeamsAuthConfig - MSAL 中国区认证',
    findFile: { markers: ['buildMSTeamsAuthConfig', 'getAuthConfigWithDefaults'] },
    oldText: `return sdk.getAuthConfigWithDefaults({
		clientId: creds.appId,
		clientSecret: creds.appPassword,
		tenantId: creds.tenantId
	});`,
    newText: `return sdk.getAuthConfigWithDefaults({
		clientId: creds.appId,
		clientSecret: creds.appPassword,
		tenantId: creds.tenantId,
		authority: "https://login.chinacloudapi.cn",
		issuers: ["https://api.botframework.azure.cn", "https://sts.chinacloudapi.cn/"],
		scope: "https://api.botframework.azure.cn"
	});`
  },

  // === graph-users: GRAPH_ROOT ===
  {
    name: 'GRAPH_ROOT - Graph API 中国区',
    findFile: { markers: ['GRAPH_ROOT', 'microsoftgraph'] },
    oldText: `const GRAPH_ROOT = "https://graph.microsoft.com/v1.0";`,
    newText: `const GRAPH_ROOT = "https://microsoftgraph.chinacloudapi.cn/v1.0";`,
    altText: [
      { old: `const GRAPH_ROOT = "https://microsoftgraph.chinacloudapi.cn/v1.0";`, new: `const GRAPH_ROOT = "https://microsoftgraph.chinacloudapi.cn/v1.0";` }
    ]
  },

  // === graph-users: getAccessToken Graph (MsalTokenProvider) ===
  {
    name: 'getAccessToken Graph scope - 中国区',
    findFile: { markers: ['MsalTokenProvider', 'getAccessToken', 'GRAPH_ROOT'] },
    oldText: `getAccessToken("https://graph.microsoft.com")`,
    newText: `getAccessToken("https://microsoftgraph.chinacloudapi.cn")`
  },

  // === graph-users: DEFAULT_MEDIA_HOST_ALLOWLIST ===
  {
    name: 'DEFAULT_MEDIA_HOST_ALLOWLIST - 中国区 Graph CDN',
    findFile: { markers: ['DEFAULT_MEDIA_HOST_ALLOWLIST', 'microsoftgraph'] },
    oldText: `"graph.microsoft.com"`,
    newText: `"microsoftgraph.chinacloudapi.cn"`,
    altText: [
      { old: `"microsoftgraph.chinacloudapi.cn"`, new: `"microsoftgraph.chinacloudapi.cn"` }
    ]
  },

  // === graph-users: DEFAULT_MEDIA_AUTH_HOST_ALLOWLIST ===
  {
    name: 'DEFAULT_MEDIA_AUTH_HOST_ALLOWLIST - 中国区',
    findFile: { markers: ['DEFAULT_MEDIA_AUTH_HOST_ALLOWLIST', 'microsoftgraph'] },
    oldText: `"graph.microsoft.com"`,
    newText: `"microsoftgraph.chinacloudapi.cn"`,
    altText: [
      { old: `"microsoftgraph.chinacloudapi.cn"`, new: `"microsoftgraph.chinacloudapi.cn"` }
    ]
  },

  // === src: getDefaultIssuers - 添加中国区 issuer ===
  {
    name: 'getDefaultIssuers - 添加中国区 issuer',
    findFile: { markers: ['getDefaultIssuers', 'api.botframework.com'] },
    oldText: `return [
			"https://api.botframework.com",
			\`https://sts.windows.net/\${tenantId}/\`,
			\`\${authority}/\${tenantId}/v2.0\`
		];`,
    newText: `return [
			"https://api.botframework.azure.cn",
			"https://api.botframework.com",
			\`https://sts.chinacloudapi.cn/\${tenantId}/\`,
			\`\${authority}/\${tenantId}/v2.0\`
		];`
  },

  // === src: MsalConnectionManager.applyConnectionDefaults issuers ===
  {
    name: 'MsalConnectionManager.applyConnectionDefaults - issuers 中国区',
    findFile: { markers: ['MsalConnectionManager', 'applyConnectionDefaults'] },
    oldText: `(_d.issuers = [
					"https://api.botframework.com",
					\`https://sts.windows.net/\${conn.connectionSettings.tenantId}/\`,`,
    newText: `(_d.issuers = [
					"https://api.botframework.azure.cn",
					"https://api.botframework.com",
					\`https://sts.chinacloudapi.cn/\${conn.connectionSettings.tenantId}/\`,`
  },

  // === src: jwksUri iss check - 添加中国区判断 ===
  {
    name: 'jwksUri - 中国区 JWKS 端点',
    findFile: { markers: ['payload.iss', 'login.botframework.com'] },
    oldText: `const jwksUri = payload.iss === "https://api.botframework.com" ? "https://login.botframework.com/v1/.well-known/keys" : \`\${authConfig.authority}/\${authConfig.tenantId}/discovery/v2.0/keys\`;`,
    newText: `const jwksUri = payload.iss === "https://api.botframework.com" ? "https://login.botframework.com/v1/.well-known/keys" : payload.iss === "https://api.botframework.azure.cn" ? "https://login.botframework.azure.cn/v1/.well-known/keys" : \`\${authConfig.authority}/\${authConfig.tenantId}/discovery/v2.0/keys\`;`
  },

  // === src: verifyOptions audience - 添加中国区 ===
  {
    name: 'verifyOptions audience - 添加中国区',
    findFile: { markers: ['verifyOptions', 'api.botframework.com'] },
    oldText: `audience: [authConfig.clientId, "https://api.botframework.com"],
			ignoreExpiration: false,
			algorithms: ["RS256"],
			clockTolerance: 300`,
    newText: `audience: [authConfig.clientId, "https://api.botframework.com", "https://api.botframework.azure.cn"],
			ignoreExpiration: false,
			algorithms: ["RS256"],
			clockTolerance: 300`
  },

  // === src: getTokenServiceEndpoint 默认中国区 ===
  {
    name: 'getTokenServiceEndpoint - 默认中国区',
    findFile: { markers: ['getTokenServiceEndpoint', 'TOKEN_SERVICE_ENDPOINT'] },
    oldText: `return (_a = process.env.TOKEN_SERVICE_ENDPOINT) !== null && _a !== void 0 ? _a : "https://api.botframework.com";`,
    newText: `return (_a = process.env.TOKEN_SERVICE_ENDPOINT) !== null && _a !== void 0 ? _a : "https://api.botframework.azure.cn";`
  },

  // === src: createConnectorClientWithIdentity default scope ===
  {
    name: 'createConnectorClientWithIdentity - scope 默认中国区',
    findFile: { markers: ['createConnectorClientWithIdentity'] },
    oldText: `_j : identity.appid) !== null && _k !== void 0 ? _k : "https://api.botframework.com";`,
    newText: `_j : identity.appid) !== null && _k !== void 0 ? _k : "https://api.botframework.azure.cn";`
  },

  // === src: createUserTokenClient 默认 scope/audience ===
  {
    name: 'createUserTokenClient - scope/audience 默认中国区',
    findFile: { markers: ['createUserTokenClient'] },
    oldText: `scope = "https://api.botframework.com", audience = "https://api.botframework.com"`,
    newText: `scope = "https://api.botframework.azure.cn", audience = "https://api.botframework.azure.cn"`
  },

  // === src: getAccessToken botframework scope ===
  {
    name: 'getAccessToken botframework scope - 中国区',
    findFile: { markers: ['MsalTokenProvider', 'loadAuthConfigFromEnv'] },
    oldText: `getAccessToken((0, auth_1.loadAuthConfigFromEnv)(), "https://api.botframework.com")`,
    newText: `getAccessToken((0, auth_1.loadAuthConfigFromEnv)(), "https://api.botframework.azure.cn")`
  },

  // === graph-users: probe GRAPH_ROOT/SCOPE ===
  {
    name: 'probe GRAPH_ROOT/SCOPE - 中国区',
    findFile: { markers: ['GRAPH_ROOT', 'microsoftgraph.chinacloudapi.cn'] },
    oldText: `"https://graph.microsoft.com"`,
    newText: `"https://microsoftgraph.chinacloudapi.cn"`
  },

  // === src: scopeCandidatesForUrl - 添加中国区 Graph 域名 ===
  {
    name: 'scopeCandidatesForUrl - 添加中国区 Graph 域名',
    findFile: { markers: ['scopeCandidatesForUrl', 'graph.microsoft.com'] },
    oldText: `host.endsWith("graph.microsoft.com") || host.endsWith("sharepoint.com")`,
    newText: `host.endsWith("graph.microsoft.com") || host.endsWith("microsoftgraph.chinacloudapi.cn") || host.endsWith("sharepoint.com")`
  },

  // === src: getAccessToken Graph (scopeCandidatesForUrl context) ===
  {
    name: 'scopeCandidatesForUrl getAccessToken Graph - 中国区',
    findFile: { markers: ['scopeCandidatesForUrl', 'getAccessToken', 'microsoftgraph'] },
    oldText: `getAccessToken("https://graph.microsoft.com")`,
    newText: `getAccessToken("https://microsoftgraph.chinacloudapi.cn")`
  },
];

// ===== 主流程 =====

console.log('OpenClaw MS Teams China patches v7\n');
console.log(`Dist: ${OPENCLAW_DIST}\n`);

const stats = { patched: 0, already: 0, missing: 0, not_found: 0 };

for (const patch of patches) {
  const result = applyPatch(patch);
  if (result === 'patched' || result === 'patched_alt') {
    console.log(`[OK]   ${patch.name}`);
    stats.patched++;
  } else if (result === 'already') {
    stats.already++;
  } else if (result === 'missing') {
    console.log(`[SKIP] ${patch.name} - pattern not found`);
    stats.missing++;
  } else {
    console.log(`[WARN] ${patch.name} - file not found (markers: ${patch.findFile.markers.join(', ')})`);
    stats.not_found++;
  }
}

console.log(`\n=== Result: ${stats.patched} applied, ${stats.already} already, ${stats.missing} missing, ${stats.not_found} not found ===`);
if (stats.patched > 0) {
  console.log('\nRestart gateway: systemctl --user restart openclaw-gateway');
}
