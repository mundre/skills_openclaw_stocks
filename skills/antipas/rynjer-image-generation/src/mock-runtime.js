const https = require('https');
const fs = require('fs');
const path = require('path');

const tools = JSON.parse(fs.readFileSync(path.join(__dirname, 'tools.json'), 'utf8'));
const BASE_URL = process.env.RYNJER_BASE_URL || 'https://rynjer.com';
const ACCESS_TOKEN = process.env.RYNJER_ACCESS_TOKEN || '';
const USE_LIVE = process.env.RYNJER_USE_LIVE === '1';

function routeModel({ use_case, quality_mode, model_override }) {
  if (model_override) return model_override;
  if (quality_mode === 'fast') return 'google/nano-banana';
  if (quality_mode === 'high') return use_case === 'product' ? 'qwen/text-to-image' : 'nano-banana-pro';
  if (use_case === 'product') return 'qwen/text-to-image';
  return 'nano-banana-pro';
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function normalizeApiError(status, data, context) {
  const rawError = data?.data?.error || data?.error || data?.message || 'unknown_error';
  return {
    ok: false,
    live: true,
    status,
    context,
    error: rawError,
    raw_response: data
  };
}

function ensureLiveAuth() {
  if (!USE_LIVE) return null;
  if (!ACCESS_TOKEN) {
    return {
      ok: false,
      live: true,
      status: 0,
      context: 'auth',
      error: 'missing_access_token',
      message: 'Set RYNJER_ACCESS_TOKEN when RYNJER_USE_LIVE=1'
    };
  }
  return null;
}

function httpJson(method, url, body, token) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const req = https.request({
      method,
      hostname: u.hostname,
      path: `${u.pathname}${u.search}`,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      }
    }, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        if (!data) {
          resolve({ status: res.statusCode, data: {} });
          return;
        }
        try {
          const parsed = JSON.parse(data);
          resolve({ status: res.statusCode, data: parsed });
        } catch (err) {
          reject(new Error(`Invalid JSON response (${res.statusCode}): ${data.slice(0, 300)}`));
        }
      });
    });
    req.on('error', reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

function extractEstimateSummary(data) {
  return {
    estimated_credits: data?.data?.estimated_credits ?? data?.estimated_credits ?? null,
    price_version: data?.data?.price_version ?? data?.price_version ?? null,
    breakdown: data?.data?.breakdown ?? data?.breakdown ?? null
  };
}

function extractPollSummary(requestId, data) {
  const payload = data?.data || data || {};
  const outputs = Array.isArray(payload.outputs) ? payload.outputs : [];
  const imageUrls = outputs
    .map(item => item?.url)
    .filter(Boolean);

  return {
    request_id: payload.request_id || requestId,
    task_id: payload.task_id || null,
    provider_task_id: payload.provider_task_id || null,
    status: payload.status || 'unknown',
    image_urls: imageUrls,
    outputs,
    usage_event_id: payload.usage_event_id || null
  };
}

function rewritePrompt(input) {
  const tone = input.tone ? `${input.tone} ` : '';
  const audience = input.audience ? ` for ${input.audience}` : '';
  const base = `${input.goal}: ${input.raw_prompt}`.trim();
  return {
    ok: true,
    refined_prompt: `Create a ${tone}${input.use_case} image${audience}. ${base}. Clean composition, commercially usable, strong visual clarity.`,
    suggested_style: input.tone || 'premium',
    suggested_aspect_ratio: input.use_case === 'landing' ? '16:9' : '1:1',
    notes: ['Local prompt rewrite flow', 'Can be upgraded later without blocking monetization path']
  };
}

async function estimateCost(input) {
  const model = routeModel(input);
  const authError = ensureLiveAuth();
  if (authError) return authError;

  if (!USE_LIVE) {
    const unit = model === 'google/nano-banana' ? 8 : model === 'qwen/text-to-image' ? 15 : 20;
    const estimated = unit * (input.count || 1) * (input.resolution === '4K' ? 2 : 1);
    return {
      ok: true,
      recommended_model: model,
      estimated_credits: estimated,
      price_version: 'draft-mock-v1',
      notes: ['Mock estimate only', 'Set RYNJER_USE_LIVE=1 and RYNJER_ACCESS_TOKEN to use live endpoint']
    };
  }

  const body = {
    product: 'image',
    model,
    units: input.count || 1,
    price_version: input.price_version || '2026-02-02-v1',
    options: {
      resolution: input.resolution || '1K'
    }
  };

  try {
    const res = await httpJson('POST', `${BASE_URL}/api/credits/estimate`, body, ACCESS_TOKEN);
    if (res.status < 200 || res.status >= 300) return normalizeApiError(res.status, res.data, 'estimate_image_cost');
    const summary = extractEstimateSummary(res.data);
    return {
      ok: true,
      live: true,
      recommended_model: model,
      api_status: res.status,
      ...summary,
      raw_response: res.data
    };
  } catch (err) {
    return {
      ok: false,
      live: true,
      context: 'estimate_image_cost',
      error: 'invalid_or_unexpected_response',
      message: err.message
    };
  }
}

async function pollImageResult(input) {
  const authError = ensureLiveAuth();
  if (authError) return authError;

  if (!USE_LIVE) {
    return {
      ok: true,
      live: false,
      request_id: input.request_id,
      status: 'succeeded',
      image_urls: ['https://example.com/mock/generated-image.png'],
      notes: ['Mock poll response']
    };
  }

  try {
    const res = await httpJson('GET', `${BASE_URL}/v1/generate/${input.request_id}`, null, ACCESS_TOKEN);
    if (res.status < 200 || res.status >= 300) return normalizeApiError(res.status, res.data, 'poll_image_result');
    const summary = extractPollSummary(input.request_id, res.data);
    return {
      ok: true,
      live: true,
      ...summary,
      pending: summary.status === 'pending' || summary.status === 'processing',
      raw_response: res.data
    };
  } catch (err) {
    return {
      ok: false,
      live: true,
      context: 'poll_image_result',
      error: 'invalid_or_unexpected_response',
      message: err.message
    };
  }
}

async function generateImage(input) {
  const model = routeModel(input);
  const authError = ensureLiveAuth();
  if (authError) return authError;

  if (!USE_LIVE) {
    const unit = model === 'google/nano-banana' ? 8 : model === 'qwen/text-to-image' ? 15 : 20;
    const used = unit * (input.count || 1);
    return {
      ok: true,
      image_urls: ['https://example.com/mock/generated-image.png'],
      model_used: model,
      credits_used: used,
      result_notes: ['Mock generation response', 'Set RYNJER_USE_LIVE=1 and RYNJER_ACCESS_TOKEN to use live endpoint'],
      next_actions: ['Generate a second variation', 'Refine the prompt', 'View pricing', 'Get API access']
    };
  }

  const requestId = input.request_id || `skill-${Date.now()}`;
  const body = {
    request_id: requestId,
    model,
    prompt: input.prompt,
    product: 'image',
    units: {
      count: input.count || 1,
      resolution: input.resolution || '1K',
      aspect_ratio: input.aspect_ratio || '1:1'
    },
    scene: input.scene || 'text-to-image'
  };

  try {
    const res = await httpJson('POST', `${BASE_URL}/v1/generate`, body, ACCESS_TOKEN);
    if (res.status < 200 || res.status >= 300) return normalizeApiError(res.status, res.data, 'generate_image');

    const payload = res.data?.data || res.data || {};
    const out = {
      ok: true,
      live: true,
      request_id: requestId,
      model_used: model,
      api_status: res.status,
      task_id: payload.task_id || null,
      provider_task_id: payload.provider_task_id || null,
      status: payload.status || 'unknown',
      usage_event_id: payload.usage_event_id || null,
      raw_response: res.data,
      poll_hint: `${BASE_URL}/v1/generate/${requestId}`
    };

    const autoPoll = input.auto_poll === true;
    if (!autoPoll) return out;

    const attempts = input.poll_attempts || 3;
    const intervalMs = input.poll_interval_ms || 1500;
    let lastPoll = null;
    for (let i = 0; i < attempts; i++) {
      await sleep(intervalMs);
      lastPoll = await pollImageResult({ request_id: requestId });
      if (!lastPoll.ok) return { ...out, auto_poll: true, poll_error: lastPoll };
      if (!lastPoll.pending) {
        return { ...out, auto_poll: true, final_result: lastPoll };
      }
    }

    return {
      ...out,
      auto_poll: true,
      pending: true,
      final_result: lastPoll,
      message: 'Generation still pending after auto-poll attempts'
    };
  } catch (err) {
    return {
      ok: false,
      live: true,
      context: 'generate_image',
      error: 'invalid_or_unexpected_response',
      message: err.message
    };
  }
}

async function main() {
  const [,, toolName, rawInput] = process.argv;
  if (!toolName) {
    console.error('Usage: node src/mock-runtime.js <tool_name> <json_input>');
    process.exit(1);
  }

  const input = rawInput ? JSON.parse(rawInput) : {};

  let result;
  if (toolName === 'rewrite_image_prompt') result = rewritePrompt(input);
  else if (toolName === 'estimate_image_cost') result = await estimateCost(input);
  else if (toolName === 'generate_image') result = await generateImage(input);
  else if (toolName === 'poll_image_result') result = await pollImageResult(input);
  else {
    console.error(`Unknown tool: ${toolName}`);
    console.error(`Available tools: ${tools.tools.map(t => t.name).join(', ')}`);
    process.exit(1);
  }

  console.log(JSON.stringify(result, null, 2));
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
