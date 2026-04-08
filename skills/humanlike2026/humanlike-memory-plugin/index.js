/**
 * Human-Like Memory Plugin for OpenClaw
 *
 * Long-term memory plugin for OpenClaw.
 *
 * @license Apache-2.0
 */

const PLUGIN_VERSION = "0.4.0";
const USER_QUERY_MARKER = "--- User Query ---";

/**
 * Session cache for tracking conversation history
 * Key: conversationId, Value: { messages: [], lastActivity: timestamp }
 */
const sessionCache = new Map();

/**
 * Timeout handles for session flush
 */
const sessionTimers = new Map();

/**
 * Upgrade notification from server
 * Contains: { required: boolean, version: string, message: string, url: string }
 */
let upgradeNotification = null;

/**
 * Display warning when API Key is not configured
 */
function warnMissingApiKey(log) {
  const msg = `
[Memory Plugin] API key not configured.
Setup: openclaw config set plugins.entries.human-like-mem.config.apiKey "mp_xxxxxx"
Get your key: https://plugin.human-like.me
`;
  if (log?.warn) {
    log.warn(msg);
  } else {
    console.warn(msg);
  }
}

/**
 * Extract text from content (string or array format)
 */
function extractText(content) {
  if (!content) return "";
  if (typeof content === "string") return content;
  if (Array.isArray(content)) {
    return content
      .filter((block) => block && typeof block === "object" && block.type === "text")
      .map((block) => block.text)
      .join(" ");
  }
  return "";
}

/**
 * Strip prepended prompt markers from message content
 */
function stripPrependedPrompt(content) {
  const text = extractText(content);
  if (!text) return text;
  const markerIndex = text.indexOf(USER_QUERY_MARKER);
  if (markerIndex !== -1) {
    return text.substring(markerIndex + USER_QUERY_MARKER.length).trim();
  }
  return text;
}

/**
 * Extract latest user utterance from channel "System: ...: <message>" transcript lines.
 */
function extractLatestSystemTranscriptMessage(text) {
  if (!text || typeof text !== "string") return "";
  const normalized = text.replace(/\r\n/g, "\n");
  const lines = normalized.split("\n");
  let latest = "";

  for (const rawLine of lines) {
    const line = rawLine.trim();
    // Example:
    // System: [2026-03-12 18:15:07 GMT+8] Feishu[...] message in group ...: 你好
    const match = line.match(/^System:\s*\[[^\]]+\]\s*.+?:\s*(.+)$/i);
    if (match && match[1]) {
      const candidate = match[1].trim();
      if (candidate) latest = candidate;
    }
  }

  return latest;
}

/**
 * Extract the final Feishu channel tail block and keep traceability fields.
 * Example kept block:
 * [Feishu ...:ou_xxx ...] username: message
 * [message_id: om_xxx]
 */
function extractFeishuTailBlock(text) {
  if (!text || typeof text !== "string") return "";
  const normalized = text.replace(/\r\n/g, "\n");
  const match = normalized.match(
    /(\[Feishu[^\]]*:((?:ou|on|u)_[A-Za-z0-9]+)[^\]]*\]\s*[^:\n]+:\s*[\s\S]*?(?:\n\[message_id:[^\]]+\]\s*)?)$/i
  );
  if (!match || !match[1]) return "";
  return match[1].trim();
}

/**
 * Whether text is only transport metadata rather than a real utterance.
 */
function isMetadataOnlyText(text) {
  if (!text) return true;
  const value = String(text).trim();
  if (!value) return true;
  if (/^\[message_id:\s*[^\]]+\]$/i.test(value)) return true;
  if (/^\[\[reply_to[^\]]*\]\]$/i.test(value)) return true;
  return false;
}

/**
 * Normalize user message text before caching/storing.
 * For channel-formatted payloads (e.g. Feishu), keep only the actual user utterance
 * and drop prepended system transcript lines.
 */
function normalizeUserMessageContent(content) {
  const text = stripPrependedPrompt(content);
  if (!text) return "";

  const normalized = String(text).replace(/\r\n/g, "\n").trim();
  if (!normalized) return "";

  // Feishu: preserve the final traceable tail block (contains platform user id/message_id).
  const feishuTailBlock = extractFeishuTailBlock(normalized);
  if (feishuTailBlock && !isMetadataOnlyText(feishuTailBlock)) {
    return feishuTailBlock;
  }

  // Generic channel relays: fallback to latest "System: ...: <message>" line.
  const latestSystemMessage = extractLatestSystemTranscriptMessage(normalized);
  if (latestSystemMessage && !isMetadataOnlyText(latestSystemMessage)) {
    return latestSystemMessage;
  }

  // Feishu channel-formatted payload:
  // [Feishu ...] username: actual message
  // [message_id: ...]
  const feishuTail = normalized.match(
    /\[Feishu[^\]]*\]\s*[^:\n]+:\s*([\s\S]*?)(?:\n\[message_id:[^\]]+\]\s*)?$/i
  );
  if (feishuTail && feishuTail[1]) {
    const candidate = feishuTail[1].trim();
    if (!isMetadataOnlyText(candidate)) return candidate;
  }

  // Discord-style channel-formatted payload:
  // [from: username (id)] actual message
  const discordTail = normalized.match(
    /\[from:\s*[^\(\]\n]+?\s*\(\d{6,}\)\]\s*([\s\S]*?)$/i
  );
  if (discordTail && discordTail[1]) {
    const candidate = discordTail[1].trim();
    if (!isMetadataOnlyText(candidate)) return candidate;
  }

  return isMetadataOnlyText(normalized) ? "" : normalized;
}

/**
 * Normalize assistant message text before caching/storing.
 * Ignore transport acks like "NO_REPLY" to avoid poisoning memory.
 */
function normalizeAssistantMessageContent(content) {
  const text = extractText(content);
  if (!text) return "";
  const normalized = String(text).trim();
  if (!normalized || normalized === "NO_REPLY") return "";
  return normalized;
}

/**
 * Parse platform identity hints from channel-formatted message text.
 * Returns null when no platform-specific id can be extracted.
 */
function parsePlatformIdentity(text) {
  if (!text || typeof text !== "string") return null;

  // Discord example:
  // [from: huang yongqing (1470374017541079042)]
  const discordFrom = text.match(/\[from:\s*([^\(\]\n]+?)\s*\((\d{6,})\)\]/i);
  if (discordFrom) {
    return {
      platform: "discord",
      userId: discordFrom[2],
      userName: discordFrom[1].trim(),
      source: "discord-from-line",
    };
  }

  // Feishu example:
  // [Feishu ...:ou_17b624... Wed ...] username: message
  const feishuUser = text.match(/\[Feishu[^\]]*:((?:ou|on|u)_[A-Za-z0-9]+)[^\]]*\]\s*([^:\n]+):/i);
  if (feishuUser) {
    return {
      platform: "feishu",
      userId: feishuUser[1],
      userName: feishuUser[2].trim(),
      source: "feishu-header-line",
    };
  }

  return null;
}

/**
 * Parse all platform user ids from a text blob.
 */
function parseAllPlatformUserIds(text) {
  if (!text || typeof text !== "string") return [];

  const ids = [];

  // Discord example:
  // [from: huang yongqing (1470374017541079042)]
  const discordRegex = /\[from:\s*[^\(\]\n]+?\s*\((\d{6,})\)\]/gi;
  let match;
  while ((match = discordRegex.exec(text)) !== null) {
    if (match[1]) ids.push(match[1]);
  }

  // Feishu example:
  // [Feishu ...:ou_17b624... Wed ...] username: message
  const feishuRegex = /\[Feishu[^\]]*:((?:ou|on|u)_[A-Za-z0-9]+)[^\]]*\]/gi;
  while ((match = feishuRegex.exec(text)) !== null) {
    if (match[1]) ids.push(match[1]);
  }

  return ids;
}

/**
 * Collect distinct user ids parsed from all messages.
 */
function collectUniqueUserIdsFromMessages(messages, fallbackUserId) {
  const unique = new Set();

  if (Array.isArray(messages)) {
    for (const msg of messages) {
      if (!msg) continue;
      const sourceText = msg.rawContent !== undefined ? msg.rawContent : msg.content;
      const text = typeof sourceText === "string" ? sourceText : extractText(sourceText);
      const ids = parseAllPlatformUserIds(text);
      for (const id of ids) unique.add(id);
    }
  }

  if (unique.size === 0 && fallbackUserId) {
    unique.add(fallbackUserId);
  }

  return Array.from(unique);
}

/**
 * Get latest user message text from cached messages.
 */
function getLatestUserMessageText(messages) {
  if (!Array.isArray(messages)) return "";
  for (let i = messages.length - 1; i >= 0; i--) {
    const msg = messages[i];
    if (msg?.role !== "user") continue;
    const sourceText = msg.rawContent !== undefined ? msg.rawContent : msg.content;
    return stripPrependedPrompt(sourceText);
  }
  return "";
}

/**
 * Resolve request identity with fallback:
 * platform user id -> configured user id -> "openclaw-user"
 */
function resolveRequestIdentity(promptText, cfg, ctx) {
  const parsed = parsePlatformIdentity(promptText);
  if (parsed?.userId) {
    return {
      userId: parsed.userId,
      userName: parsed.userName || null,
      platform: parsed.platform || null,
      source: parsed.source || "platform-parser",
    };
  }

  if (cfg?.configuredUserId) {
    return {
      userId: cfg.configuredUserId,
      userName: null,
      platform: null,
      source: "configured-user-id",
    };
  }

  if (ctx?.userId) {
    return {
      userId: ctx.userId,
      userName: null,
      platform: null,
      source: "ctx-user-id",
    };
  }

  return {
    userId: "openclaw-user",
    userName: null,
    platform: null,
    source: "default-user-id",
  };
}

/**
 * Strip accidental api-key fragments from user id strings.
 * Example: "tenant:mem_xxx:116041..." -> "116041..."
 */
function sanitizeUserId(rawUserId) {
  if (!rawUserId) return "openclaw-user";
  const value = String(rawUserId).trim();
  if (!value) return "openclaw-user";

  if (value.includes(":") && /(^|:)mem_[^:]+(:|$)/.test(value)) {
    const parts = value.split(":").filter(Boolean);
    const memIdx = parts.findIndex((p) => p.startsWith("mem_"));
    if (memIdx >= 0 && memIdx < parts.length - 1) {
      return parts[parts.length - 1];
    }
  }

  return value;
}

/**
 * Truncate text to specified maximum length
 */
function truncate(text, maxLen) {
  if (!text || text.length <= maxLen) return text;
  return text.substring(0, maxLen - 3) + "...";
}

/**
 * Make HTTP request with retry logic
 */
async function httpRequest(url, options, cfg, log) {
  const timeout = cfg.timeoutMs || 5000;
  const retries = cfg.retries || 1;

  let lastError;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // Check for upgrade notification in response headers
      checkUpgradeHeaders(response, log);

      if (!response.ok) {
        const errorText = await response.text();
        if (log?.warn) {
          log.warn(`[Memory Plugin] HTTP ${response.status}: ${errorText.substring(0, 200)}`);
        }
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const jsonResult = await response.json();

      // Also check for upgrade notification in response body
      checkUpgradeBody(jsonResult, log);

      return jsonResult;
    } catch (error) {
      lastError = error;
      if (attempt < retries && error.name !== 'AbortError') {
        if (log?.debug) {
          log.debug(`[Memory Plugin] Request attempt ${attempt + 1} failed, retrying...`);
        }
        continue;
      }
      if (error.name === 'AbortError') {
        if (log?.warn) log.warn(`[Memory Plugin] Request timeout after ${timeout}ms`);
        break;
      }
      if (log?.warn) {
        log.warn(`[Memory Plugin] Request failed: ${error.message}`);
      }
    }
  }

  throw lastError;
}

/**
 * Check response headers for upgrade notification
 */
function checkUpgradeHeaders(response, log) {
  const upgradeRequired = response.headers.get('X-Upgrade-Required');
  const upgradeVersion = response.headers.get('X-Upgrade-Version');
  const upgradeMessage = response.headers.get('X-Upgrade-Message');
  const upgradeUrl = response.headers.get('X-Upgrade-Url');

  if (upgradeRequired === 'true' || upgradeVersion) {
    upgradeNotification = {
      required: upgradeRequired === 'true',
      version: upgradeVersion || 'latest',
      message: upgradeMessage || `Please upgrade to version ${upgradeVersion || 'latest'}`,
      url: upgradeUrl || 'https://www.npmjs.com/package/@humanlikememory/human-like-mem',
      currentVersion: PLUGIN_VERSION,
    };
    if (log?.warn) {
      log.warn(`[Memory Plugin] Upgrade ${upgradeRequired === 'true' ? 'REQUIRED' : 'available'}: ${upgradeNotification.message}`);
    }
  }
}

/**
 * Check response body for upgrade notification
 */
function checkUpgradeBody(result, log) {
  if (result && result._upgrade) {
    const upgrade = result._upgrade;
    upgradeNotification = {
      required: upgrade.required === true,
      version: upgrade.version || 'latest',
      message: upgrade.message || `Please upgrade to version ${upgrade.version || 'latest'}`,
      url: upgrade.url || 'https://www.npmjs.com/package/@humanlikememory/human-like-mem',
      currentVersion: PLUGIN_VERSION,
    };
    if (log?.warn) {
      log.warn(`[Memory Plugin] Upgrade ${upgrade.required ? 'REQUIRED' : 'available'}: ${upgradeNotification.message}`);
    }
  }
}

/**
 * Format upgrade notification for user display
 */
function formatUpgradeNotification() {
  if (!upgradeNotification) return null;

  const { required, version, message, url, currentVersion } = upgradeNotification;

  if (required) {
    return `
**[Human-Like Memory Plugin] Upgrade Required**

Current version: ${currentVersion}
Latest version: ${version}

${message}

Please upgrade to continue using memory features:
\`\`\`bash
npm update @humanlikememory/human-like-mem
\`\`\`

More info: ${url}
`;
  }

  return `
**[Human-Like Memory Plugin] Upgrade Available**

Current version: ${currentVersion}
Latest version: ${version}

${message}

Upgrade command:
\`\`\`bash
npm update @humanlikememory/human-like-mem
\`\`\`
`;
}

/**
 * Retrieve memories from the API
 */
async function retrieveMemory(prompt, cfg, ctx, log) {
  const baseUrl = cfg.baseUrl || process.env.HUMAN_LIKE_MEM_BASE_URL;
  const apiKey = cfg.apiKey || process.env.HUMAN_LIKE_MEM_API_KEY;

  if (!apiKey) {
    warnMissingApiKey(log);
    return [];
  }

  const url = `${baseUrl}/api/plugin/v1/search/memory`;
  if (log?.info) {
    log.info(`[Memory Plugin] Recall request URL: ${url}`);
  }
  const identity = resolveRequestIdentity(prompt, cfg, ctx);
  const userId = sanitizeUserId(identity.userId);
  const payload = {
    query: prompt,
    user_id: userId,
    agent_id: cfg.agentId || ctx?.agentId,
    conversation_id: cfg.recallGlobal !== false ? null : (ctx?.sessionId || ctx?.conversationId),
    memory_limit_number: cfg.memoryLimitNumber || 6,
    min_score: cfg.minScore || 0.1,
    tags: cfg.tags || null,
  };

  try {
    const result = await httpRequest(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": apiKey,
        "x-request-id": ctx?.requestId || `openclaw-${Date.now()}`,
        "x-plugin-version": PLUGIN_VERSION,
        "x-client-type": "plugin",
      },
      body: JSON.stringify(payload),
    }, cfg, log);

    if (!result.success) {
      if (log?.warn) log.warn(`[Memory Plugin] Memory retrieval failed: ${result.error}`);
      return [];
    }

    const memoryCount = result.memories?.length || 0;
    if (memoryCount > 0 && log?.info) {
      log.info(`[Memory Plugin] Retrieved ${memoryCount} memories for query: "${truncate(prompt, 50)}"`);
    }

    return result.memories || [];
  } catch (error) {
    if (log?.warn) {
      log.warn(`[Memory Plugin] Memory retrieval failed: ${error.message}`);
    }
    return [];
  }
}

/**
 * Add memories to the API
 */
async function addMemory(messages, cfg, ctx, log) {
  const baseUrl = cfg.baseUrl || process.env.HUMAN_LIKE_MEM_BASE_URL;
  const apiKey = cfg.apiKey || process.env.HUMAN_LIKE_MEM_API_KEY;

  if (!apiKey) return;

  const url = `${baseUrl}/api/plugin/v1/add/message`;
  if (log?.info) {
    log.info(`[Memory Plugin] Add-memory request URL: ${url}`);
  }
  const sessionId = resolveSessionId(ctx, null) || `session-${Date.now()}`;
  const latestUserText = getLatestUserMessageText(messages);
  const identity = resolveRequestIdentity(latestUserText, cfg, ctx);
  const userId = sanitizeUserId(identity.userId);
  const metadataUserIds = (() => {
    // If stripPlatformMetadata is true, don't extract platform user IDs from messages
    if (cfg.stripPlatformMetadata) {
      return [userId];
    }
    const parsed = collectUniqueUserIdsFromMessages(messages, null)
      .map((id) => sanitizeUserId(id))
      .filter(Boolean);
    if (parsed.length > 0) {
      return Array.from(new Set(parsed));
    }
    return [userId];
  })();
  const agentId = cfg.agentId || ctx?.agentId || "main";

  const payload = {
    user_id: userId,
    conversation_id: sessionId,
    messages: messages.map(m => ({
      role: m.role,
      content: truncate(m.content, cfg.maxMessageChars || 20000),
    })),
    agent_id: agentId,
    tags: cfg.tags || ["openclaw"],
    async_mode: true,
    custom_workflows: {
      stream_params: {
        metadata: JSON.stringify({
          user_ids: metadataUserIds,
          agent_ids: [agentId],
          session_id: sessionId,
          scenario: cfg.scenario || "openclaw-plugin",
        }),
      },
    },
  };

  if (log?.debug) {
    log.debug(
      `[Memory Plugin] add/message payload: user_id=${userId}, agent_id=${agentId}, conversation_id=${sessionId}, metadata.user_ids=${JSON.stringify(metadataUserIds)}, metadata.agent_ids=${JSON.stringify([agentId])}`
    );
  }

  try {
    const result = await httpRequest(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": apiKey,
        "x-request-id": ctx?.requestId || `openclaw-${Date.now()}`,
        "x-plugin-version": PLUGIN_VERSION,
        "x-client-type": "plugin",
      },
      body: JSON.stringify(payload),
    }, cfg, log);

    const memoryCount = result?.memories_count || 0;
    if (log?.info) {
      log.info(`[Memory Plugin] Successfully added memory: ${memoryCount} streams`);
    }

    return result;
  } catch (error) {
    if (log?.warn) {
      log.warn(`[Memory Plugin] Memory add failed: ${error.message}`);
    }
    throw error;
  }
}

/**
 * Format time for display
 */
function formatTime(value) {
  if (value === undefined || value === null || value === "") return "";
  if (typeof value === "number") {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "";
    const pad2 = (v) => String(v).padStart(2, "0");
    return `${date.getFullYear()}-${pad2(date.getMonth() + 1)}-${pad2(date.getDate())} ${pad2(date.getHours())}:${pad2(date.getMinutes())}`;
  }
  if (typeof value === "string") {
    const trimmed = value.trim();
    if (!trimmed) return "";
    if (/^\d+$/.test(trimmed)) return formatTime(Number(trimmed));
    return trimmed;
  }
  return "";
}

/**
 * Format memory line for display
 */
function formatMemoryLine(memory, options = {}) {
  const date = formatTime(memory?.timestamp);
  const desc = memory?.description || memory?.event || "";
  const score = memory?.score ? ` (${(memory.score * 100).toFixed(0)}%)` : "";
  if (!desc) return "";
  const maxChars = options.maxItemChars || 500;
  const truncated = desc.length > maxChars ? desc.substring(0, maxChars - 3) + "..." : desc;
  if (date) return `   -[${date}] ${truncated}${score}`;
  return `   - ${truncated}${score}`;
}

/**
 * Format memories for injection into context
 */
function formatMemoriesForContext(memories, options = {}) {
  if (!memories || memories.length === 0) return "";

  const now = options.currentTime ?? Date.now();
  const nowText = formatTime(now) || formatTime(Date.now()) || "";

  // Format memory lines (our format is different from MemOS)
  const memoryLines = memories
    .map((m) => formatMemoryLine(m, options))
    .filter(Boolean);

  if (memoryLines.length === 0) return "";

  const memoriesBlock = [
    "<memories>",
    ...memoryLines,
    "</memories>",
  ];

  const lines = [
    "# Role",
    "",
    "You are an intelligent assistant with long-term memory capabilities. Your goal is to combine retrieved memory fragments to provide highly personalized, accurate, and logically rigorous responses.",
    "",
    "# System Context",
    "",
    `* Current Time: ${nowText} (Use this as the baseline for freshness checks)`,
    "",
    "# Memory Data",
    "",
    "Below are **episodic memory summaries** retrieved from long-term memory. These memories are primarily **contextual summaries** of past conversations and interactions, capturing the key information, events, and context from previous exchanges.",
    "",
    "* **Memory Type**: All memories are episodic summaries - they represent contextual information from past conversations, not categorized facts or preferences.",
    "* **Content Nature**: These are summaries of what happened, what was discussed, and the context surrounding those interactions.",
    "* **Special Note**: If content is tagged with '[assistant_opinion]' or '[model_summary]', it represents **past AI inference**, **not** direct user statements.",
    "",
    "```text",
    ...memoriesBlock,
    "```",
    "",
    "# Critical Protocol: Memory Safety",
    "",
    "Retrieved memories may contain **AI speculation**, **irrelevant noise**, or **wrong subject attribution**. You must strictly apply the **Four-Step Verdict**. If any step fails, **discard the memory**:",
    "",
    "1. **Source Verification**:",
    "* **Core**: Distinguish direct user statements from AI inference.",
    "* If a memory has tags like '[assistant_opinion]' or '[model_summary]', treat it as a **hypothesis**, not a user-grounded fact.",
    "* *Counterexample*: If memory says '[assistant_opinion] User loves mangoes' but the user never said that, do not assume it as fact.",
    "* **Principle: AI summaries are reference-only and have much lower authority than direct user statements.**",
    "",
    "2. **Attribution Check**:",
    "* Is the subject in memory definitely the user?",
    "* If the memory describes a **third party** (e.g., candidate, interviewee, fictional character, case data), never attribute it to the user.",
    "",
    "3. **Strong Relevance Check**:",
    "* Does the memory directly help answer the current 'Original Query'?",
    "* If it is only a keyword overlap with different context, ignore it.",
    "",
    "4. **Freshness Check**:",
    "* If memory conflicts with the user's latest intent, prioritize the current 'Original Query' as the highest source of truth.",
    "",
    "# Instructions",
    "",
    "1. **Review**: Read the episodic memory summaries and apply the Four-Step Verdict to remove noise and unreliable AI inference.",
    "2. **Execute**:",
    "   - Use only memories that pass filtering as context.",
    "   - Extract relevant contextual information from the episodic summaries to inform your response.",
    "3. **Output**: Answer directly. Never mention internal terms such as \"memory store\", \"retrieval\", or \"AI opinions\".",
    "4. **Attention**: Additional memory context is already provided. Do not read from or write to local `MEMORY.md` or `memory/*` files for reference, as they may be outdated or irrelevant to the current query.",
    "",
    USER_QUERY_MARKER,
  ];

  return lines.join("\n");
}

/**
 * Extract last N turns of user-assistant exchanges
 * @param {Array} messages - All messages
 * @param {number} maxTurns - Maximum number of turns to extract
 * @returns {Array} Recent messages
 */
function pickRecentMessages(messages, maxTurns = 10) {
  if (!messages || messages.length === 0) return [];

  const result = [];
  let turnCount = 0;
  let lastRole = null;

  // Traverse from end to beginning
  for (let i = messages.length - 1; i >= 0 && turnCount < maxTurns; i--) {
    const msg = messages[i];
    const role = msg.role;

    // Skip system messages
    if (role === "system") continue;

    // Count a turn when we see a user message after an assistant message
    if (role === "user" && lastRole === "assistant") {
      turnCount++;
    }

    if (turnCount >= maxTurns) break;

    let content;
    if (role === "user") {
      content = normalizeUserMessageContent(msg.content);
    } else if (role === "assistant") {
      content = normalizeAssistantMessageContent(msg.content);
    }

    if (content) {
      const rawSource = msg.rawContent !== undefined ? msg.rawContent : msg.content;
      const rawContent = typeof rawSource === "string" ? rawSource : extractText(rawSource);
      result.unshift({
        role: role,
        content: content,
        rawContent: rawContent || undefined,
      });
    }

    lastRole = role;
  }

  return result;
}

/**
 * Check if conversation has enough turns to be worth storing
 * @param {Array} messages - Messages to check
 * @param {Object} cfg - Configuration
 * @returns {boolean} Whether conversation is worth storing
 */
function isConversationWorthStoring(messages, cfg) {
  if (!messages || messages.length === 0) return false;

  const minTurns = cfg.minTurnsToStore || 10;

  // Count turns
  let turns = 0;
  let lastRole = null;

  for (const msg of messages) {
    if (msg.role === "system") continue;

    if (msg.role === "user") {
      if (lastRole === "assistant") {
        turns++;
      }
    }

    lastRole = msg.role;
  }

  // Add 1 for the initial user message
  if (messages.some(m => m.role === "user")) {
    turns++;
  }

  return turns >= minTurns;
}

/**
 * Get or create session cache entry
 */
function getSessionCache(sessionId) {
  if (!sessionCache.has(sessionId)) {
    sessionCache.set(sessionId, {
      messages: [],
      lastActivity: Date.now(),
      turnCount: 0,
    });
  }
  return sessionCache.get(sessionId);
}

/**
 * Add message to session cache
 */
function addToSessionCache(sessionId, message) {
  const cache = getSessionCache(sessionId);
  cache.messages.push(message);
  cache.lastActivity = Date.now();

  // Count turns (user message after assistant = new turn)
  if (message.role === "user" && cache.messages.length > 1) {
    const prevMsg = cache.messages[cache.messages.length - 2];
    if (prevMsg && prevMsg.role === "assistant") {
      cache.turnCount++;
    }
  }

  return cache;
}

/**
 * Clear session cache
 */
function clearSessionCache(sessionId) {
  sessionCache.delete(sessionId);
  if (sessionTimers.has(sessionId)) {
    clearTimeout(sessionTimers.get(sessionId));
    sessionTimers.delete(sessionId);
  }
}

/**
 * Resolve session ID from ctx and event objects, trying multiple field names
 * that different OpenClaw versions may use.
 */
function resolveSessionId(ctx, event) {
  // Direct fields on ctx
  const fromCtx = ctx?.conversationId
    || ctx?.sessionId
    || ctx?.session_id
    || ctx?.conversation_id
    || ctx?.runId
    || ctx?.run_id;
  if (fromCtx) return fromCtx;

  // Direct fields on event
  const fromEvent = event?.sessionId
    || event?.session_id
    || event?.conversationId
    || event?.conversation_id
    || event?.runId
    || event?.run_id;
  if (fromEvent) return fromEvent;

  // Try sessionKey (skip "unknown")
  if (ctx?.sessionKey && ctx.sessionKey !== "unknown") {
    return ctx.sessionKey;
  }

  // Try messageProvider (may contain session info)
  const mp = ctx?.messageProvider;
  if (mp) {
    const fromMp = mp.sessionId || mp.session_id
      || mp.conversationId || mp.conversation_id
      || (typeof mp.getSessionId === 'function' ? mp.getSessionId() : null);
    if (fromMp) return fromMp;
  }

  // Last resort: use agentId as session identifier
  if (ctx?.agentId) return `agent-${ctx.agentId}`;

  return null;
}

/**
 * Schedule session flush after timeout
 */
function scheduleSessionFlush(sessionId, cfg, ctx, log) {
  // Clear existing timer
  if (sessionTimers.has(sessionId)) {
    clearTimeout(sessionTimers.get(sessionId));
  }

  const timeoutMs = cfg.sessionTimeoutMs || 5 * 60 * 1000; // 5 minutes default

  const timer = setTimeout(async () => {
    await flushSession(sessionId, cfg, ctx, log);
  }, timeoutMs);

  sessionTimers.set(sessionId, timer);
}

/**
 * Flush session cache to memory storage
 */
async function flushSession(sessionId, cfg, ctx, log) {
  const cache = sessionCache.get(sessionId);
  if (!cache || cache.messages.length === 0) {
    clearSessionCache(sessionId);
    return;
  }

  // Check if conversation is worth storing
  if (!isConversationWorthStoring(cache.messages, cfg)) {
    if (log?.debug) {
      log.debug(`[Memory Plugin] Session ${sessionId} not worth storing (turns: ${cache.turnCount}, messages: ${cache.messages.length})`);
    }
    clearSessionCache(sessionId);
    return;
  }

  // Get recent messages to store
  const maxTurns = cfg.maxTurnsToStore || 10;
  const messagesToSave = pickRecentMessages(cache.messages, maxTurns);

  if (messagesToSave.length === 0) {
    clearSessionCache(sessionId);
    return;
  }

  try {
    if (log?.info) {
      log.info(`[Memory Plugin] Flushing session ${sessionId}: ${messagesToSave.length} messages, ${cache.turnCount} turns`);
    }
    await addMemory(messagesToSave, cfg, ctx, log, sessionId);
  } catch (error) {
    if (log?.warn) {
      log.warn(`[Memory Plugin] Session flush failed: ${error.message}`);
    }
  } finally {
    clearSessionCache(sessionId);
  }
}

/**
 * Main plugin export — object-style with register(api) method.
 * Supports OpenClaw >=2026.2.0 capability registration.
 */
export default {
  id: "human-like-mem",
  name: "Human-Like Memory Plugin",
  kind: "memory",

  register(api) {
    const config = api.pluginConfig || {};
    const log = api.logger || console;
    const cfg = buildConfig(config);

    if (log?.info) {
      log.info(`[Memory Plugin] v${PLUGIN_VERSION} registering as memory slot`);
    }

    // --- Check allowPromptInjection policy ---
    const pluginEntry = api.config?.plugins?.entries?.[api.id] ?? api.config?.plugins?.entries?.["human-like-mem"];
    const allowPromptInjection = pluginEntry?.hooks?.allowPromptInjection !== false;

    // --- Service lifecycle ---
    api.registerService({
      id: "human-like-mem",
      start: async () => {
        if (log?.info) log.info(`[Memory Plugin] Service started (v${PLUGIN_VERSION})`);
      },
      health: async () => {
        const hasApiKey = !!(cfg.apiKey || process.env.HUMAN_LIKE_MEM_API_KEY);
        return {
          status: hasApiKey ? "ok" : "degraded",
          message: hasApiKey
            ? `v${PLUGIN_VERSION} ready, ${sessionCache.size} active sessions`
            : "API key not configured",
        };
      },
      stop: async () => {
        if (log?.info) log.info(`[Memory Plugin] Service stopping, flushing ${sessionCache.size} sessions`);
        const flushPromises = [];
        for (const [sid] of sessionCache) {
          flushPromises.push(
            flushSession(sid, cfg, null, log).catch(err => {
              if (log?.warn) log.warn(`[Memory Plugin] Flush failed for ${sid}: ${err.message}`);
            })
          );
        }
        await Promise.allSettled(flushPromises);
        if (log?.info) log.info(`[Memory Plugin] Service stopped`);
      },
    });

    // --- Register memory runtime for status reporting ---
    if (typeof api.registerMemoryRuntime === "function") {
      api.registerMemoryRuntime({
        getMemorySearchManager: async () => ({
          manager: {
            async probeVectorAvailability() {
              return { ok: !!(cfg.apiKey || process.env.HUMAN_LIKE_MEM_API_KEY) };
            },
            status() {
              return {
                files: sessionCache.size,
                chunks: 0,
                dirty: false,
                sources: ["remote-api"],
                provider: "human-like-mem",
                vector: { enabled: true, available: true, provider: "remote" },
              };
            },
            async close() {},
          },
        }),
        resolveMemoryBackendConfig: () => ({
          store: { driver: "remote", path: "remote://plugin.human-like.me" },
        }),
      });
      if (log?.info) log.info(`[Memory Plugin] Registered memory runtime for status reporting`);
    }

    // --- Recall handler (before_prompt_build only) ---
    const recallHandler = async (event, ctx) => {
      if (!cfg.recallEnabled) return;
      if (!allowPromptInjection) {
        if (log?.debug) log.debug(`[Memory Plugin] allowPromptInjection=false, auto-recall disabled`);
        return;
      }

      if (log?.debug) {
        log.debug(`[Memory Plugin] before_prompt_build TRIGGERED`);
        log.debug(`[Memory Plugin] recall ctx keys: ${JSON.stringify(ctx ? Object.keys(ctx) : 'null')}`);
        log.debug(`[Memory Plugin] recall event keys: ${JSON.stringify(event ? Object.keys(event) : 'null')}`);
      }

      const prompt = event?.prompt || "";
      if (!prompt || prompt.trim().length < 3) {
        if (log?.debug) log.debug('[Memory Plugin] Prompt too short, skipping recall');
        return;
      }

      const sessionId = resolveSessionId(ctx, event) || `session-${Date.now()}`;
      const userContent = normalizeUserMessageContent(prompt);
      const rawUserContent = stripPrependedPrompt(prompt);
      if (userContent) {
        addToSessionCache(sessionId, { role: "user", content: userContent, rawContent: rawUserContent });
      }

      try {
        const memories = await retrieveMemory(prompt, cfg, ctx, log);

        let prependContext = "";

        const upgradeMsg = formatUpgradeNotification();
        if (upgradeMsg) {
          prependContext += upgradeMsg + "\n\n";
          upgradeNotification = null;
        }

        if (memories && memories.length > 0) {
          prependContext += formatMemoriesForContext(memories, { currentTime: Date.now() });
          if (log?.info) log.info(`[Memory Plugin] Injected ${memories.length} memories`);
        }

        if (prependContext) {
          return { prependContext };
        }
      } catch (error) {
        if (log?.warn) log.warn(`[Memory Plugin] Memory recall failed: ${error.message}`);

        const upgradeMsg = formatUpgradeNotification();
        if (upgradeMsg) {
          upgradeNotification = null;
          return { prependContext: upgradeMsg };
        }
      }
    };

    // --- Store handler (agent_end only) ---
    const storeHandler = async (event, ctx) => {
      if (!cfg.addEnabled) return;
      if (!event?.success) return;

      if (log?.debug) {
        log.debug(`[Memory Plugin] agent_end store TRIGGERED`);
        log.debug(`[Memory Plugin] store hook ctx keys: ${JSON.stringify(ctx ? Object.keys(ctx) : 'null')}`);
        log.debug(`[Memory Plugin] store hook event keys: ${JSON.stringify(event ? Object.keys(event) : 'null')}`);
      }

      const sessionId = resolveSessionId(ctx, event);
      if (!sessionId) {
        if (log?.debug) log.debug('[Memory Plugin] No session ID found in ctx or event, skipping memory cache');
        return;
      }

      const assistantContent = event?.response || event?.result;
      if (assistantContent) {
        const content = normalizeAssistantMessageContent(assistantContent);
        const rawContent = extractText(assistantContent);
        if (content) {
          addToSessionCache(sessionId, { role: "assistant", content, rawContent: rawContent || undefined });
        }
      } else if (event?.messages?.length) {
        for (let i = event.messages.length - 1; i >= 0; i--) {
          if (event.messages[i].role === "assistant") {
            const content = normalizeAssistantMessageContent(event.messages[i].content);
            const rawContent = extractText(event.messages[i].content);
            if (content) {
              addToSessionCache(sessionId, { role: "assistant", content, rawContent: rawContent || undefined });
            }
            break;
          }
        }
      }

      scheduleSessionFlush(sessionId, cfg, ctx, log);

      const cache = sessionCache.get(sessionId);
      if (cache && cache.turnCount >= (cfg.minTurnsToStore || 10)) {
        if (isConversationWorthStoring(cache.messages, cfg)) {
          if (log?.info) {
            log.info(`[Memory Plugin] Reached ${cache.turnCount} turns, flushing session`);
          }
          flushSession(sessionId, cfg, ctx, log).catch(err => {
            if (log?.warn) log.warn(`[Memory Plugin] Async flush failed: ${err.message}`);
          });
        }
      }
    };

    // --- Session end handler ---
    const sessionEndHandler = async (event, ctx) => {
      if (!cfg.addEnabled) return;

      const sessionId = resolveSessionId(ctx, event);
      if (!sessionId) return;

      if (log?.info) {
        log.info(`[Memory Plugin] Session ending, flushing cache`);
      }

      await flushSession(sessionId, cfg, ctx, log);
    };

    // --- Hook registration (single canonical hooks) ---
    api.on("before_prompt_build", recallHandler);
    api.on("agent_end", storeHandler);
    api.on("session_end", sessionEndHandler);

    // --- Agent tools registration ---
    if (typeof api.registerTool === "function") {
      api.registerTool({
        name: "memory_search",
        label: "Memory Search",
        description: "Search user's long-term memory for relevant past conversations, knowledge, and preferences. Use this when you need context about the user's history or when they reference past events.",
        parameters: {
          type: "object",
          properties: {
            query: { type: "string", description: "Search query — keywords or natural language describing what to look for in memory" },
            limit: { type: "number", description: "Maximum number of results to return (default: 6, max: 20)" },
          },
          required: ["query"],
        },
        execute: async (_toolCallId, params) => {
          const { query, limit = 6 } = params;
          const clampedLimit = Math.min(Math.max(1, limit), 20);
          if (log?.info) log.info(`[Memory Plugin] Tool memory_search: query="${truncate(query, 50)}", limit=${clampedLimit}`);
          try {
            const memories = await retrieveMemory(query, { ...cfg, memoryLimitNumber: clampedLimit }, null, log);
            if (!memories || memories.length === 0) {
              return { content: [{ type: "text", text: "No relevant memories found for this query." }] };
            }
            const formatted = formatMemoriesForContext(memories, { currentTime: Date.now() });
            return {
              content: [{ type: "text", text: formatted }],
              details: { hits: memories.length, query },
            };
          } catch (error) {
            if (log?.warn) log.warn(`[Memory Plugin] Tool memory_search failed: ${error.message}`);
            return { content: [{ type: "text", text: `Memory search failed: ${error.message}` }], isError: true };
          }
        },
      });

      api.registerTool({
        name: "memory_store",
        label: "Memory Store",
        description: "Actively save important information, user preferences, or key decisions to long-term memory. Use this when the user shares something worth remembering for future conversations.",
        parameters: {
          type: "object",
          properties: {
            content: { type: "string", description: "The information to remember — be specific and include context" },
            category: { type: "string", description: "Optional category tag (e.g. 'preference', 'fact', 'decision')" },
          },
          required: ["content"],
        },
        execute: async (_toolCallId, params) => {
          const { content, category } = params;
          if (log?.info) log.info(`[Memory Plugin] Tool memory_store: content="${truncate(content, 50)}", category=${category || 'none'}`);
          try {
            const messages = [
              { role: "user", content: `[Memory Store${category ? ` | ${category}` : ""}] ${content}` },
              { role: "assistant", content: `Noted and saved to memory: ${truncate(content, 100)}` },
            ];
            const result = await addMemory(messages, cfg, null, log);
            return {
              content: [{ type: "text", text: `Memory saved successfully: "${truncate(content, 80)}"` }],
              details: { stored: true, category: category || null },
            };
          } catch (error) {
            if (log?.warn) log.warn(`[Memory Plugin] Tool memory_store failed: ${error.message}`);
            return { content: [{ type: "text", text: `Memory store failed: ${error.message}` }], isError: true };
          }
        },
      });

      if (log?.info) log.info(`[Memory Plugin] Registered 2 agent tools: memory_search, memory_store`);
    }

    if (log?.info) {
      log.info(`[Memory Plugin] Registration complete: hooks=[before_prompt_build, agent_end, session_end], tools=${typeof api.registerTool === "function" ? 2 : 0}`);
    }
  },
};

/**
 * Build config from various sources
 */
function buildConfig(config) {
  const minTurnsToStore = config?.minTurnsToStore || parseInt(process.env.HUMAN_LIKE_MEM_MIN_TURNS) || 5;
  const configuredUserId = config?.userId || process.env.HUMAN_LIKE_MEM_USER_ID;

  return {
    baseUrl: config?.baseUrl || process.env.HUMAN_LIKE_MEM_BASE_URL || "https://plugin.human-like.me",
    apiKey: config?.apiKey || process.env.HUMAN_LIKE_MEM_API_KEY,
    configuredUserId: configuredUserId,
    userId: configuredUserId || "openclaw-user",
    agentId: config?.agentId || process.env.HUMAN_LIKE_MEM_AGENT_ID,
    recallEnabled: config?.recallEnabled !== false,
    addEnabled: config?.addEnabled !== false,
    recallGlobal: config?.recallGlobal !== false,
    memoryLimitNumber: config?.memoryLimitNumber || parseInt(process.env.HUMAN_LIKE_MEM_LIMIT_NUMBER) || 6,
    minScore: config?.minScore || parseFloat(process.env.HUMAN_LIKE_MEM_MIN_SCORE) || 0.1,
    tags: config?.tags || null,
    maxMessageChars: config?.maxMessageChars || 20000,
    asyncMode: config?.asyncMode !== false,
    timeoutMs: config?.timeoutMs || 5000,
    retries: config?.retries ?? 1,
    scenario: config?.scenario || process.env.HUMAN_LIKE_MEM_SCENARIO || "openclaw-plugin",
    // Session-based storage settings
    minTurnsToStore: minTurnsToStore,
    maxTurnsToStore: minTurnsToStore * 2,  // Always 2x of minTurnsToStore
    sessionTimeoutMs: config?.sessionTimeoutMs || parseInt(process.env.HUMAN_LIKE_MEM_SESSION_TIMEOUT) || 5 * 60 * 1000,
  };
}
