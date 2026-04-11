import process from "node:process";

const DEFAULT_MODEL = "qwen-image-2.0-pro";
const DEFAULT_AR = "16:9";

const SIZE_MAP: Record<string, string> = {
  "1:1": "1024*1024",
  "16:9": "1280*720",
  "9:16": "720*1280",
  "4:3": "1280*960",
  "3:4": "960*1280",
  "2:3": "768*1152",
  "3:2": "1152*768",
  "4:5": "800*1000",
  "9:19.5": "720*1560",
  "21:9": "1344*576",
};

function getApiKey(): string | null {
  return process.env.DASHSCOPE_API_KEY || null;
}

function getBaseUrl(): string {
  const base = process.env.DASHSCOPE_BASE_URL || "https://dashscope.aliyuncs.com";
  return base.replace(/\/+$/g, "");
}

export async function generateImage(
  prompt: string,
  options?: {
    aspectRatio?: string | null;
    model?: string;
  }
): Promise<Uint8Array> {
  const apiKey = getApiKey();
  if (!apiKey) {
    throw new Error(
      "DASHSCOPE_API_KEY environment variable is required.\n" +
        "Set it in your shell or add to .baoyu-skills/.env file."
    );
  }

  const model = options?.model || DEFAULT_MODEL;
  const ar = options?.aspectRatio || DEFAULT_AR;
  const size = SIZE_MAP[ar] || SIZE_MAP["16:9"];

  const stylePrompt = `${prompt}

【风格】手绘
【氛围】简约
【画面要求】整洁、留白、构图平衡、色调统一、风格统一，不要文字`;

  const url = `${getBaseUrl()}/api/v1/services/aigc/multimodal-generation/generation`;

  const body = {
    model,
    input: {
      messages: [
        {
          role: "user",
          content: [{ text: stylePrompt }],
        },
      ],
    },
    parameters: {
      prompt_extend: false,
      size,
      watermark: false,
      negative_prompt: "文字，水印，签名，低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节，过度光滑，画面具有 AI 感，构图混乱，扭曲，照片写实，真实感，3D 渲染，矢量图，复杂背景，拥挤，杂乱，色彩过饱和，暗色调，阴沉",
    },
  };

  console.log(`Generating with DashScope (${model}) - Size: ${size}`);

  // Retry logic with exponential backoff for rate limits
  const maxRetries = 3;
  let lastError: Error | null = null;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const errText = await res.text();

        if (res.status === 429) {
          const retryAfter = res.headers.get("Retry-After");
          const defaultWaits = [10000, 30000, 60000]; // 10s, 30s, 60s
          const waitTime = retryAfter
            ? parseInt(retryAfter, 10) * 1000
            : (defaultWaits[attempt - 1] ?? 60000);

          if (attempt < maxRetries) {
            console.log(`  Rate limit hit, waiting ${waitTime / 1000}s before retry ${attempt}/${maxRetries}...`);
            await sleep(waitTime);
            continue;
          }
        }

        throw new Error(`DashScope API error (${res.status}): ${errText}`);
      }

      const result = await res.json();
      let imageData: string | null = null;

      if (result.output?.result_image) {
        imageData = result.output.result_image;
      } else if (result.output?.choices?.[0]?.message?.content) {
        const content = result.output.choices[0].message.content;
        if (Array.isArray(content)) {
          for (const item of content) {
            if (item.image) {
              imageData = item.image;
              break;
            }
          }
        }
      }

      if (!imageData) {
        console.error("Response:", JSON.stringify(result, null, 2));
        throw new Error("No image in response");
      }

      if (imageData.startsWith("http://") || imageData.startsWith("https://")) {
        const imgRes = await fetch(imageData);
        if (!imgRes.ok) throw new Error("Failed to download image");
        const buf = await imgRes.arrayBuffer();
        return new Uint8Array(buf);
      }

      return Uint8Array.from(Buffer.from(imageData, "base64"));
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      if (attempt < maxRetries && lastError.message.includes("429")) {
        continue;
      }
      throw lastError;
    }
  }

  throw lastError || new Error("Failed to generate image");
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
