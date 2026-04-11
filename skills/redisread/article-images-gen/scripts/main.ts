#!/usr/bin/env bun
/**
 * Simple single-image generation entry point
 */

import process from "node:process";
import { readFile, writeFile } from "node:fs/promises";
import { generateImage } from "./image-generator";

type CliArgs = {
  prompt: string | null;
  promptFiles: string | null;
  image: string | null;
  help: boolean;
};

function printUsage(): void {
  console.log(`Usage:
  bun scripts/main.ts --prompt "your prompt here"
  bun scripts/main.ts --promptfiles prompt.md
  bun scripts/main.ts --help

Options:
  --prompt <text>        Direct prompt for image generation
  --promptfiles <files>  Comma-separated list of prompt files to read
  --image <path>         Output image path (used with --promptfiles)
  -h, --help             Show help
`);
}

function parseArgs(argv: string[]): CliArgs {
  const args: CliArgs = {
    prompt: null,
    promptFiles: null,
    image: null,
    help: false,
  };

  for (let i = 0; i < argv.length; i++) {
    const current = argv[i]!;
    if (current === "--prompt") {
      args.prompt = argv[++i] ?? null;
    } else if (current === "--promptfiles") {
      args.promptFiles = argv[++i] ?? null;
    } else if (current === "--image") {
      args.image = argv[++i] ?? null;
    } else if (current === "--help" || current === "-h") {
      args.help = true;
    }
  }

  return args;
}

async function main(): Promise<void> {
  const args = parseArgs(process.argv.slice(2));

  if (args.help) {
    printUsage();
    return;
  }

  if (args.prompt) {
    // Direct prompt mode
    console.log("Generating image with DashScope (qwen-image-2.0-pro)... Size: 1280*720");

    const imageBuffer = await generateImage(args.prompt);

    const outputPath = args.image || `output-${Date.now()}.png`;
    await writeFile(outputPath, imageBuffer);
    console.log(`Image saved to: ${outputPath}`);
    return;
  }

  if (args.promptFiles) {
    // Batch prompt files mode
    const files = args.promptFiles.split(",");
    for (const file of files) {
      const promptContent = await readFile(file.trim(), "utf8");
      const promptText = promptContent.replace(/^---\n[\s\S]*?\n---\n/, "").trim();

      console.log(`Generating image with DashScope (qwen-image-2.0-pro)... Size: 1280*720`);

      const imageBuffer = await generateImage(promptText);

      const outputFile = args.image || file.trim().replace(".md", ".png");
      await writeFile(outputFile, imageBuffer);
      console.log(`Image saved to: ${outputFile}`);
    }
    return;
  }

  printUsage();
}

main().catch((error) => {
  console.error("Fatal error:", error instanceof Error ? error.message : String(error));
  process.exit(1);
});
