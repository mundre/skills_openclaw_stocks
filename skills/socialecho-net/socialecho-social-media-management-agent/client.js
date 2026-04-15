#!/usr/bin/env node

export function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith("--")) continue;
    const key = token.slice(2);
    const next = argv[i + 1];
    if (!next || next.startsWith("--")) {
      args[key] = true;
      continue;
    }
    args[key] = next;
    i += 1;
  }
  return args;
}

export function getOption(args, name, required = true, fallback = "") {
  const v = args[name] ?? fallback;
  if (required && !v) {
    throw new Error(`Missing option: --${name}`);
  }
  return v;
}

function buildQuery(params) {
  const usp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === null || v === "") continue;
    usp.set(k, String(v));
  }
  return usp.toString();
}

export function buildRequestOptions(args) {
  return {
    apiKey: getOption(args, "api-key"),
    baseUrl: getOption(args, "base-url", false, "https://api.socialecho.net"),
    teamId: getOption(args, "team-id", false, ""),
    lang: getOption(args, "lang", false, "zh_CN")
  };
}

export async function callApi(path, params = {}, options) {
  const { apiKey, baseUrl, teamId, lang } = options;

  const qs = buildQuery(params);
  const url = `${baseUrl}${path}${qs ? `?${qs}` : ""}`;

  const headers = {
    Authorization: `Bearer ${apiKey}`,
    "X-Lang": lang
  };
  if (teamId) headers["X-Team-Id"] = teamId;

  const resp = await fetch(url, { method: "GET", headers });
  const status = resp.status;
  let body;
  try {
    body = await resp.json();
  } catch {
    body = { parse_error: true };
  }

  const ok = status === 200 && body?.code === 200;
  return { ok, status, body, url };
}

export function parseCsvIds(raw) {
  if (!raw) return "";
  return String(raw)
    .split(",")
    .map((x) => x.trim())
    .filter(Boolean)
    .join(",");
}

export function printAndExit(result) {
  console.log(JSON.stringify(result, null, 2));
  if (!result.ok) process.exit(1);
}
