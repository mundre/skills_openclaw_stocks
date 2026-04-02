/**
 * Video parser — extracts key frames via FFmpeg, then converts to base64 images
 * for vision-capable models (Claude / GPT-4o).
 *
 * Requires: ffmpeg installed on the system (see README for installation)
 */

import fs from "fs";
import path from "path";
import os from "os";
import { ParsedContent } from "./types";
import { exec } from "openclaw";

const FRAMES_PER_VIDEO = 8;         // Number of key frames to extract
const MAX_FRAME_SIZE_PX = 1024;     // Resize to max this dimension to save tokens

// ─── Check ffmpeg availability ─────────────────────────────────────────────────

async function checkFFmpeg(): Promise<boolean> {
  try {
    const result = await exec("ffmpeg -version", { timeout: 5000 });
    return result.code === 0;
  } catch {
    return false;
  }
}

// ─── Get video duration in seconds ────────────────────────────────────────────

async function getVideoDuration(filePath: string): Promise<number> {
  try {
    const result = await exec(
      `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "${filePath}"`,
      { encoding: "utf-8", timeout: 10000 }
    );

    if (result.code !== 0 || !result.stdout) {
      return 60;
    }

    return parseFloat(result.stdout.trim()) || 60;
  } catch {
    return 60;
  }
}

// ─── Extract frames at evenly-spaced timestamps ────────────────────────────────

export async function parseVideo(filePath: string, source: string): Promise<ParsedContent> {
  const hasFFmpeg = await checkFFmpeg();
  
  if (!hasFFmpeg) {
    console.warn(
      "[video-parser] ffmpeg not found. Install it to enable video analysis.\n" +
      "  brew install ffmpeg  |  apt install ffmpeg  |  choco install ffmpeg"
    );
    return {
      text: `[Video file: ${source} — ffmpeg not installed, frame extraction skipped]`,
      images: [],
      source,
      inputType: "video",
    };
  }

  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "testgen-frames-"));

  try {
    const duration = await getVideoDuration(filePath);
    const interval = Math.max(1, Math.floor(duration / FRAMES_PER_VIDEO));

    // Extract frames: one every `interval` seconds, max FRAMES_PER_VIDEO
    const ffmpegCmd = `ffmpeg -i "${filePath}" -vf "select='not(mod(t\\,${interval}))',scale=${MAX_FRAME_SIZE_PX}:-1" -vsync vfr -frames:v ${FRAMES_PER_VIDEO} -q:v 3 "${path.join(tmpDir, "frame%03d.jpg")}"`;
    
    const result = await exec(ffmpegCmd, { 
      encoding: "utf-8", 
      timeout: 60000 
    });

    if (result.code !== 0 && result.stderr) {
      console.warn("[video-parser] ffmpeg stderr:", result.stderr.slice(0, 300));
    }

    // Read extracted frames
    const frameFiles = fs
      .readdirSync(tmpDir)
      .filter((f) => f.endsWith(".jpg"))
      .sort()
      .slice(0, FRAMES_PER_VIDEO);

    if (frameFiles.length === 0) {
      return {
        text: `[Video: ${source} — no frames could be extracted]`,
        images: [],
        source,
        inputType: "video",
      };
    }

    const images: string[] = frameFiles.map((f) => {
      const buf = fs.readFileSync(path.join(tmpDir, f));
      return `data:image/jpeg;base64,${buf.toString("base64")}`;
    });

    const durationStr = formatDuration(duration);
    const text = [
      `[Video: ${source}]`,
      `Duration: ${durationStr}`,
      `Extracted ${images.length} key frames at ~${interval}s intervals`,
      `Please analyze the UI and interactions shown in the frames to generate test cases.`,
    ].join("\n");

    return { text, images, source, inputType: "video" };

  } finally {
    // Always clean up temp frames
    fs.rmSync(tmpDir, { recursive: true, force: true });
  }
}

// ─── Buffer variant (for web upload) ──────────────────────────────────────────

export async function parseVideoBuffer(buffer: Buffer, originalName: string): Promise<ParsedContent> {
  const tmpFile = path.join(os.tmpdir(), `testgen-video-${Date.now()}${path.extname(originalName)}`);
  fs.writeFileSync(tmpFile, buffer);
  try {
    return await parseVideo(tmpFile, originalName);
  } finally {
    fs.rmSync(tmpFile, { force: true });
  }
}

// ─── Helper ───────────────────────────────────────────────────────────────────

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}m${s.toString().padStart(2, "0")}s`;
}

export function isVideoFile(mimeType: string, filename: string): boolean {
  if (mimeType.startsWith("video/")) return true;
  const ext = path.extname(filename).toLowerCase();
  return [".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv", ".wmv"].includes(ext);
}
