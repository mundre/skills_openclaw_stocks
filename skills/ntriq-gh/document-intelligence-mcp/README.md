# Document Intelligence MCP Server

Extract text (OCR), summarize, classify, and extract tables from document images using local AI vision models.

## Features

| Tool | Description | Price |
|------|-------------|-------|
| `extract_text` | OCR - Extract all text from document images in markdown format | $0.05/use |
| `summarize_document` | Analyze and summarize document content with key information | $0.10/use |
| `classify_document` | Classify document type (invoice, contract, receipt, etc.) with confidence | $0.05/use |
| `extract_tables` | Extract all tables as structured JSON (headers + rows) | $0.10/use |

## Connect via Claude Desktop

Add to your Claude Desktop MCP settings:

```json
{
  "mcpServers": {
    "document-intelligence": {
      "url": "https://ntriqpro--document-intelligence-mcp.apify.actor/mcp?token=YOUR_APIFY_TOKEN"
    }
  }
}
```

## Supported Document Types

- Invoices and receipts
- Contracts and agreements
- Business letters and memos
- Reports and presentations
- Forms and applications
- ID documents and certificates
- Tables, spreadsheets, and charts

## Supported Languages

Responses can be generated in: English, Korean, Japanese, Chinese, Spanish.

## Input

Each tool accepts:
- `imageUrl` (required): URL of the document image
- `language` (optional): Response language code (default: "en")

## Output

Each tool returns structured JSON with the analysis results.

### Example: extract_text

Input:
```json
{
  "imageUrl": "https://example.com/invoice.png"
}
```

Output:
```json
{
  "status": "success",
  "text": "# Invoice\n\n**Invoice #**: 2024-001\n**Date**: March 15, 2024\n...",
  "model": "qwen2.5-vl",
  "imageUrl": "https://example.com/invoice.png"
}
```

### Example: classify_document

Output:
```json
{
  "status": "success",
  "classification": {
    "document_type": "invoice",
    "confidence": 0.95,
    "language": "en",
    "key_fields": ["invoice_number", "date", "total_amount", "vendor"]
  }
}
```

### Example: extract_tables

Output:
```json
{
  "status": "success",
  "tables": {
    "tables": [
      {
        "headers": ["Item", "Quantity", "Price"],
        "rows": [
          ["Widget A", "10", "$5.00"],
          ["Widget B", "5", "$12.00"]
        ]
      }
    ]
  }
}
```

## Technology

- **Vision Model**: Qwen2.5-VL (Apache 2.0 License)
- **Processing**: Local AI inference, zero external API calls
- **Privacy**: Document images are processed in real-time and not stored

## Open Source Licenses

This service uses the following open source models:
- [Qwen2.5-VL](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct) — Apache 2.0 License

Platform usage is free. You only pay per event (see pricing above).
