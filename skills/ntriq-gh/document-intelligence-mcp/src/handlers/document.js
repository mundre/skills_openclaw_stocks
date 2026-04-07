/**
 * Document analysis handlers
 * Calls ntriq AI server to analyze document images
 * Model: Qwen2.5-VL (Apache 2.0 License)
 */

const SERVER = process.env.NTRIQ_AI_URL || "https://ai.ntriq.co.kr";

async function callDocumentServer(body, timeout = 120) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), (timeout + 15) * 1000);

  try {
    const resp = await fetch(`${SERVER}/analyze/document`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });

    clearTimeout(timer);

    if (!resp.ok) {
      const error = await resp.text();
      throw new Error(`Document server error: ${resp.status} ${error}`);
    }

    return await resp.json();
  } catch (e) {
    clearTimeout(timer);
    throw e;
  }
}

export async function extractText(imageUrl, language = "en") {
  const result = await callDocumentServer({
    image_url: imageUrl,
    analysis_type: "extract",
    language: language,
    max_tokens: 3000,
  });

  return {
    status: "success",
    text: result.analysis || result.text || result,
    model: result.model || "qwen2.5-vl",
    imageUrl: imageUrl,
  };
}

export async function summarizeDocument(imageUrl, language = "en") {
  const result = await callDocumentServer({
    image_url: imageUrl,
    analysis_type: "summarize",
    language: language,
    max_tokens: 2048,
  });

  return {
    status: "success",
    summary: result.analysis || result.text || result,
    model: result.model || "qwen2.5-vl",
    imageUrl: imageUrl,
  };
}

export async function classifyDocument(imageUrl, language = "en") {
  const result = await callDocumentServer({
    image_url: imageUrl,
    analysis_type: "classify",
    language: language,
    max_tokens: 512,
  });

  return {
    status: "success",
    classification: result.analysis || result.text || result,
    model: result.model || "qwen2.5-vl",
    imageUrl: imageUrl,
  };
}

export async function extractTables(imageUrl, language = "en") {
  const result = await callDocumentServer({
    image_url: imageUrl,
    analysis_type: "table",
    language: language,
    max_tokens: 3000,
  });

  return {
    status: "success",
    tables: result.analysis || result.text || result,
    model: result.model || "qwen2.5-vl",
    imageUrl: imageUrl,
  };
}
