/**
 * Document Intelligence MCP Server
 * Extract text, summarize, classify, and extract tables from document images
 * Main entry point for Apify Actor
 */

import { Actor } from "apify";
import { trackMCP } from "agnost";
import express from "express";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { z } from "zod";

import {
  extractText,
  summarizeDocument,
  classifyDocument,
  extractTables,
} from "./handlers/document.js";

// PPE charge amounts per tool — MUST match pay_per_event.json exactly
const CHARGE_MAP = {
  extract_text: 0.05,
  summarize_document: 0.15,
  classify_document: 0.05,
  extract_tables: 0.12,
};

async function main() {
  await Actor.init();

  const app = express();
  app.use(express.json());

  const mcpServer = new McpServer({
    name: "document-intelligence-mcp",
    version: "1.0.0",
  });

  // --- Register 4 MCP Tools ---

  mcpServer.tool(
    "extract_text",
    "Extract all text from a document image (OCR). Returns structured markdown preserving headers, lists, and tables.",
    {
      imageUrl: z
        .string()
        .describe("URL of the document image to extract text from"),
      language: z
        .string()
        .optional()
        .describe("Response language: en, ko, ja, zh, es (default: en)"),
    },
    async ({ imageUrl, language }) => {
      const result = await extractText(imageUrl, language || "en");
      await chargeForTool("extract_text");
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      };
    },
  );

  mcpServer.tool(
    "summarize_document",
    "Analyze and summarize a document image. Returns document type, key information, and important dates/numbers/names.",
    {
      imageUrl: z.string().describe("URL of the document image to summarize"),
      language: z
        .string()
        .optional()
        .describe("Response language: en, ko, ja, zh, es (default: en)"),
    },
    async ({ imageUrl, language }) => {
      const result = await summarizeDocument(imageUrl, language || "en");
      await chargeForTool("summarize_document");
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      };
    },
  );

  mcpServer.tool(
    "classify_document",
    "Classify a document image type (invoice, contract, receipt, letter, report, form, ID document, etc.) with confidence score.",
    {
      imageUrl: z.string().describe("URL of the document image to classify"),
      language: z
        .string()
        .optional()
        .describe("Response language: en, ko, ja, zh, es (default: en)"),
    },
    async ({ imageUrl, language }) => {
      const result = await classifyDocument(imageUrl, language || "en");
      await chargeForTool("classify_document");
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      };
    },
  );

  mcpServer.tool(
    "extract_tables",
    "Extract all tables from a document image. Returns structured JSON with headers and rows.",
    {
      imageUrl: z
        .string()
        .describe("URL of the document image containing tables"),
      language: z
        .string()
        .optional()
        .describe("Response language: en, ko, ja, zh, es (default: en)"),
    },
    async ({ imageUrl, language }) => {
      const result = await extractTables(imageUrl, language || "en");
      await chargeForTool("extract_tables");
      return {
        content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
      };
    },
  );

  // --- MCP Transport ---

  trackMCP(mcpServer, "49897781-817a-421b-8ba2-5a42387a7458");

  app.post("/mcp", async (req, res) => {
    try {
      const transport = new StreamableHTTPServerTransport({
        sessionIdGenerator: undefined,
      });
      res.on("close", () => transport.close());
      await mcpServer.connect(transport);
      await transport.handleRequest(req, res, req.body);
    } catch (error) {
      console.error("MCP request error:", error);
      if (!res.headersSent) {
        res.status(500).json({
          jsonrpc: "2.0",
          error: {
            code: -32603,
            message: error.message || "Internal server error",
          },
          id: null,
        });
      }
    }
  });

  app.get("/health", (req, res) => {
    res.json({
      status: "ok",
      server: "document-intelligence-mcp",
      version: "1.0.0",
    });
  });

  const port = process.env.APIFY_CONTAINER_PORT || 3000;
  app.listen(port, "0.0.0.0", () => {
    console.log(
      `Document Intelligence MCP Server listening on http://0.0.0.0:${port}/mcp`,
    );
  });
}

async function chargeForTool(toolName) {
  const amount = CHARGE_MAP[toolName];
  if (amount) {
    try {
      await Actor.charge({ eventName: toolName, count: 1 });
      console.log(`Charged $${amount} for ${toolName}`);
    } catch (e) {
      console.error(`Charge failed for ${toolName}:`, e.message);
    }
  }
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
