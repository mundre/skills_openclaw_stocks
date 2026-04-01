#!/usr/bin/env node
import { randomUUID } from "node:crypto";
import { parseArgs } from "node:util";

const DEFAULT_BASE_URL = "https://claw-uat.ebonex.io";
const DEFAULT_SKILL_KEY = "100_indicators_analysis";
const AGENT_RUN_TIMEOUT_MS = 150000;
const AGENT_RESULT_RETRY_TIMES = 3;
const AGENT_RESULT_RETRY_INTERVAL_MS = 10000;

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function isTimeoutError(error) {
  if (!error) return false;
  return error.name === "TimeoutError" || error.name === "AbortError";
}

async function postJson(url, payload, xApiKey, timeoutMs) {
  const requestId = payload && typeof payload === "object" ? payload.request_id || "" : "";
  console.error(`[HTTP REQUEST] request_id=${requestId}`);
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": xApiKey,
    },
    body: JSON.stringify(payload),
    signal: AbortSignal.timeout(timeoutMs),
  });
  const text = await res.text();
  if (!res.ok) {
    const error = new Error(`HTTP ${res.status}: ${text}`);
    error.status = res.status;
    throw error;
  }
  return JSON.parse(text);
}

async function invokeAgentResultWithRetry(baseUrl, requestId, xApiKey) {
  const url = `${baseUrl.replace(/\/+$/, "")}/api/claw/agent-result`;
  let lastResult = { error: true, detail: "agent-result 尚未获取到结果" };

  for (let attempt = 1; attempt <= AGENT_RESULT_RETRY_TIMES; attempt += 1) {
    if (attempt > 1) {
      await sleep(AGENT_RESULT_RETRY_INTERVAL_MS);
    }
    try {
      const result = await postJson(url, { request_id: requestId }, xApiKey, AGENT_RUN_TIMEOUT_MS);
      lastResult = result;
      const status = String(result?.data?.status || "").toLowerCase();
      if (status !== "running") {
        return result;
      }
    } catch (error) {
      lastResult = { error: true, detail: `第 ${attempt} 次 agent-result 请求失败: ${error.message || error}` };
    }
  }

  return lastResult;
}

async function invokeAgentRun(baseUrl, skillKey, question, threadId, xApiKey) {
  const requestId = randomUUID();
  const url = `${baseUrl.replace(/\/+$/, "")}/api/claw/agent-run`;
  const payload = {
    skill_key: skillKey,
    question,
    thread_id: threadId,
    request_id: requestId,
  };

  try {
    return await postJson(url, payload, xApiKey, AGENT_RUN_TIMEOUT_MS);
  } catch (error) {
    if (isTimeoutError(error)) {
      return await invokeAgentResultWithRetry(baseUrl, requestId, xApiKey);
    }
    throw error;
  }
}

async function main() {
  let values;
  try {
    ({ values } = parseArgs({
      args: process.argv.slice(2),
      options: {
        question: { type: "string", short: "q" },
        "thread-id": { type: "string", short: "t", default: "" },
        help: { type: "boolean", short: "h", default: false },
      },
      allowPositionals: false,
    }));
  } catch (error) {
    console.error(error.message || error);
    process.exit(1);
  }

  if (values.help) {
    console.log('用法: node scripts/prana_skill_client.js -q "用户任务" [-t thread_id]');
    process.exit(0);
  }

  if (!values.question) {
    console.error("错误: 必须使用 -q / --question 提供用户需求任务描述。");
    process.exit(1);
  }

  const xApiKey = String(process.env.PRANA_SKILL_API_FLAG || "").trim();
  if (!xApiKey) {
    console.error("错误: 未检测到环境变量 PRANA_SKILL_API_FLAG。");
    process.exit(1);
  }

  try {
    const result = await invokeAgentRun(
      DEFAULT_BASE_URL,
      DEFAULT_SKILL_KEY,
      values.question,
      values["thread-id"] || "",
      xApiKey,
    );
    console.log(JSON.stringify(result, null, 2));
  } catch (error) {
    console.error(`请求失败: ${error.message || error}`);
    process.exit(2);
  }
}

await main();
