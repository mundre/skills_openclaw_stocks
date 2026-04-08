---
name: ntriq-content-factory-mcp
description: "Multi-format content generation: Q&A, reports, quizzes, flashcards, mind maps, slide decks. 9 output formats from single input."
version: 1.0.0
metadata:
  openclaw:
    primaryTag: data-intelligence
    tags: [content,generation,writing]
    author: ntriq
    homepage: https://x402.ntriq.co.kr
---

# Content Factory MCP

Multi-format content generation from a single input text. Produces Q&A pairs, structured reports, quizzes, flashcards, mind maps, slide deck outlines, and more. 9 output formats, fully local AI — no external API calls.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `text` | string | ✅ | Source content (article, transcript, notes) |
| `formats` | array | ✅ | Output types: `qa`, `report`, `quiz`, `flashcards`, `mindmap`, `slides`, `podcast`, `table`, `summary` |
| `audience` | string | ❌ | Target audience: `executive`, `technical`, `student` |
| `language` | string | ❌ | Output language (default: `en`) |

## Example Response

```json
{
  "qa": [
    {"q": "What is the primary risk factor identified?", "a": "Supply chain concentration in Southeast Asia."}
  ],
  "flashcards": [
    {"front": "COGS", "back": "Cost of Goods Sold — direct costs attributable to product production"}
  ],
  "slides": [
    {"slide": 1, "title": "Executive Summary", "bullets": ["Revenue up 18% YoY", "3 new markets entered"]}
  ]
}
```

## Use Cases

- Training material generation from employee handbooks
- Sales enablement content from product docs
- E-learning course creation from expert interviews

## Access

```bash
# Service catalog
curl https://x402.ntriq.co.kr/services
```

Available on [Apify Store](https://apify.com/ntriqpro/content-factory-mcp) · [x402 micropayments](https://x402.ntriq.co.kr)
