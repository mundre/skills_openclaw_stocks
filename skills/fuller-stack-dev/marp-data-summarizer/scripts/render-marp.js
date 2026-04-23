#!/usr/bin/env node

import { spawnSync } from "node:child_process"
import fs from "node:fs"
import path from "node:path"

function usage() {
  console.error(
    [
      "Usage:",
      "  node scripts/render-marp.js <input.slides.md> [output] [--format html|pdf|pptx|notes|png|jpeg|pngs|jpegs]",
      "",
      "Examples:",
      "  node scripts/render-marp.js deck.slides.md",
      "  node scripts/render-marp.js deck.slides.md deck.slides.pdf --format pdf",
      "  node scripts/render-marp.js deck.slides.md ./slides-out --format pngs",
    ].join("\n"),
  )
}

function parseArgs(argv) {
  if (argv.length < 1) {
    usage()
    process.exit(1)
  }

  const inputPath = path.resolve(argv[0])
  let outputPath = null
  let format = null

  let i = 1
  if (i < argv.length && !argv[i].startsWith("--")) {
    outputPath = path.resolve(argv[i])
    i += 1
  }

  while (i < argv.length) {
    if (argv[i] === "--format") {
      format = argv[i + 1]
      i += 2
      continue
    }
    console.error(`Unknown option: ${argv[i]}`)
    usage()
    process.exit(1)
  }

  if (!fs.existsSync(inputPath)) {
    throw new Error(`Input file not found: ${inputPath}`)
  }

  const inferred = inferFormat(outputPath)
  const finalFormat = (format || inferred || "html").toLowerCase()
  if (!supportedFormats().includes(finalFormat)) {
    throw new Error(`Unsupported format: ${finalFormat}`)
  }

  const finalOutputPath = outputPath || defaultOutputPath(inputPath, finalFormat)
  return { inputPath, outputPath: finalOutputPath, format: finalFormat }
}

function supportedFormats() {
  return ["html", "pdf", "pptx", "notes", "png", "jpeg", "pngs", "jpegs"]
}

function inferFormat(outputPath) {
  if (!outputPath) return null
  const statExists = fs.existsSync(outputPath)
  if (!statExists) {
    const ext = path.extname(outputPath).toLowerCase()
    if (ext === ".html") return "html"
    if (ext === ".pdf") return "pdf"
    if (ext === ".pptx") return "pptx"
    if (ext === ".txt") return "notes"
    if (ext === ".png") return "png"
    if (ext === ".jpeg" || ext === ".jpg") return "jpeg"
    return null
  }
  if (fs.statSync(outputPath).isDirectory()) {
    return null
  }
  return inferFormat(`${outputPath}`)
}

function defaultStem(inputPath) {
  if (inputPath.endsWith(".slides.md")) {
    return inputPath.slice(0, -3)
  }
  if (inputPath.endsWith(".md")) {
    return inputPath.slice(0, -3)
  }
  return inputPath
}

function defaultOutputPath(inputPath, format) {
  const stem = defaultStem(inputPath)
  if (format === "html") return `${stem}.html`
  if (format === "pdf") return `${stem}.pdf`
  if (format === "pptx") return `${stem}.pptx`
  if (format === "notes") return `${stem}.notes.txt`
  if (format === "png") return `${stem}.png`
  if (format === "jpeg") return `${stem}.jpeg`
  if (format === "pngs" || format === "jpegs") return path.dirname(inputPath)
  return `${stem}.html`
}

function binaryExists(bin, args = ["--version"]) {
  const result = spawnSync(bin, args, { stdio: "ignore" })
  return !result.error
}

function resolveRunner() {
  if (binaryExists("marp")) return { bin: "marp", prefix: [] }
  if (binaryExists("npx")) return { bin: "npx", prefix: ["--yes", "@marp-team/marp-cli"] }
  if (binaryExists("pnpm")) return { bin: "pnpm", prefix: ["dlx", "@marp-team/marp-cli"] }
  if (binaryExists("bunx")) return { bin: "bunx", prefix: ["@marp-team/marp-cli"] }
  if (binaryExists("yarn")) return { bin: "yarn", prefix: ["dlx", "@marp-team/marp-cli"] }
  throw new Error("No Marp runner found. Install marp, npx, pnpm, bunx, or yarn.")
}

function marpArgs(inputPath, outputPath, format) {
  if (format === "html") return [inputPath, "-o", outputPath]
  if (format === "pdf") return [inputPath, "--pdf", "-o", outputPath]
  if (format === "pptx") return [inputPath, "--pptx", "-o", outputPath]
  if (format === "notes") return [inputPath, "--notes", "-o", outputPath]
  if (format === "png") return [inputPath, "--image", "png", "-o", outputPath]
  if (format === "jpeg") return [inputPath, "--image", "jpeg", "-o", outputPath]
  if (format === "pngs") return [inputPath, "--images", "png", "-o", outputPath]
  if (format === "jpegs") return [inputPath, "--images", "jpeg", "-o", outputPath]
  throw new Error(`Unsupported format: ${format}`)
}

function ensureParent(outputPath, format) {
  if (format === "pngs" || format === "jpegs") {
    fs.mkdirSync(outputPath, { recursive: true })
    return
  }
  fs.mkdirSync(path.dirname(outputPath), { recursive: true })
}

function verifyOutput(outputPath, format) {
  if (format === "pngs" || format === "jpegs") {
    const entries = fs.readdirSync(outputPath)
    if (!entries.length) {
      throw new Error(`No images were rendered into ${outputPath}`)
    }
    return
  }

  if (!fs.existsSync(outputPath)) {
    throw new Error(`Expected output was not created: ${outputPath}`)
  }

  const stat = fs.statSync(outputPath)
  if (!stat.isFile() || stat.size === 0) {
    throw new Error(`Rendered artifact is empty: ${outputPath}`)
  }
}

function main() {
  const { inputPath, outputPath, format } = parseArgs(process.argv.slice(2))
  ensureParent(outputPath, format)

  const runner = resolveRunner()
  const args = [...runner.prefix, ...marpArgs(inputPath, outputPath, format)]
  const result = spawnSync(runner.bin, args, { stdio: "inherit" })
  if (result.error) throw result.error
  if (result.status !== 0) {
    process.exit(result.status ?? 1)
  }

  verifyOutput(outputPath, format)
  console.log(outputPath)
}

try {
  main()
} catch (error) {
  console.error(error instanceof Error ? error.message : String(error))
  process.exit(1)
}
