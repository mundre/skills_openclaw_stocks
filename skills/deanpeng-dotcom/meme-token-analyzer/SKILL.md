---
name: meme-token-analyzer
version: 1.0.2
description: "Meme Token Analyzer workflow with web search, image generation, data cleaning, and multimodal analysis to output wealth gene detection reports. Use this skill when analyzing meme token sentiment, generating prediction images, and producing professional investment analysis reports. Supports multi-dimensional analysis, intelligent detection, and humorous professional reporting."
author: AntalphaAI
license: MIT
requires: [python-3.12]
keywords: [meme, token, sentiment-analysis, image-generation, multimodal, ai, langgraph, wealth-gene, meme-coin-analysis]
metadata: {"repository":"https://github.com/AntalphaAI/Meme-Token-Analyzer","install":{"type":"python","command":"pip install -r requirements.txt"},"env":[{"name":"COZE_WORKSPACE_PATH","description":"Workspace path for configuration files","required":true,"sensitive":false}],"disclaimer":"This skill only uses COZE_WORKSPACE_PATH. It does NOT use COZE_BUCKET_ENDPOINT_URL, PGDATABASE_URL, or any storage/database credentials."}
---

# Meme Token Analyzer Skill

This skill guides the implementation of an automated, multimodal Meme token analysis tool using LangGraph and coze-coding-dev-sdk, combining real-time sentiment search, AI-generated prediction images, and comprehensive wealth gene detection analysis.

## Overview

Meme Token Analyzer enables you to build applications that automatically analyze Meme tokens by:
- 🔍 **Searching** latest news, social media sentiment, and market trends with time range filtering
- 🎨 **Generating** "Moonshot" prediction images for tokens
- 🧹 **Cleaning** search results into LLM-friendly summaries
- 🤖 **Analyzing** sentiment data and visual elements with multimodal AI
- 💎 **Rating** tokens with a four-tier wealth gene system (Diamond Hand, Moonshot, Paper Hand, Shitcoin)

## Supported Languages

This skill supports Python SDK.

**Mandatory (required): When you use this skill, you MUST immediately open and read the SDK guide for the language you are implementing in for installation, client initialization, and usage examples, and then follow it exactly. Do not guess APIs, do not proceed before reading the corresponding SDK guide.**

- **Python SDK**: Read first: [python/README.md](python/README.md)

## Key Features

### 🔍 Web Search
- Searches latest news, social media sentiment, and market trends
- Time range filter (1 month) for fresh data
- AI-generated summary of search results

### 🎨 Image Generation
- Creates "Moonshot" prediction images for tokens
- High-quality 2K resolution images
- Dynamic, cinematic visual style

### 🧹 Data Cleaning
- Condenses search results into LLM-friendly summaries
- Date freshness validation
- Removes irrelevant information

### 🤖 AI Analysis
- Multimodal analysis combining sentiment data and visual elements
- Four-dimensional analysis framework:
  1. 🎯 **Narrative Magic Analysis** - Name and concept memorability
  2. 📢 **Community Hype Ability Prediction** - Community activity and shilling intensity
  3. 🎨 **Visual Gene Detection** - Meme image's viral potential
  4. 🏆 **Wealth Gene Rating** - Final verdict

### 💎 Wealth Gene Rating System
- 🌟 **Diamond Hand** - 10000x potential
- 🌙 **Moonshot** - 100x expected
- 🗑️ **Paper Hand** - Likely a rug
- 💩 **Shitcoin** - Stay away

### 🧠 Smart Detection
- Automatically detects major coins (BTC/ETH/SOL) with cross-border scan perspective
- Handles missing data gracefully without fabrication
- Identifies irrelevant search results with appropriate warnings

## Workflow Architecture

### DAG Flow Diagram

```
                              ┌─────────────────────────────────────┐
                              │           START                      │
                              │         (token_name)                 │
                              └──────────────┬──────────────────────┘
                                             │
                      ┌──────────────────────┴──────────────────────┐
                      │                                             │
                      ▼                                             ▼
        ┌─────────────────────────┐                 ┌─────────────────────────┐
        │      search_node        │                 │     image_gen_node      │
        │   (Web Search Node)     │                 │  (Image Generation)     │
        │                         │                 │                         │
        │  • Search web news      │                 │  • Generate prediction  │
        │  • Fetch sentiment      │                 │    image for token      │
        │  • AI summary           │                 │  • 2K resolution        │
        └───────────┬─────────────┘                 └───────────┬─────────────┘
                    │                                           │
                    ▼                                           │
        ┌─────────────────────────┐                             │
        │   clean_data_node       │                             │
        │   (Data Cleaning)       │                             │
        │                         │                             │
        │  • Condense results     │                             │
        │  • Validate dates       │                             │
        │  • Remove noise         │                             │
        └───────────┬─────────────┘                             │
                    │                                           │
                    └─────────────────┬─────────────────────────┘
                                      │
                                      ▼
                      ┌─────────────────────────────────────┐
                      │       analysis_node                  │
                      │   (Wealth Gene Detection)           │
                      │                                      │
                      │  • Multimodal analysis              │
                      │  • Narrative Magic Check            │
                      │  • Community Hype Prediction        │
                      │  • Visual Gene Detection            │
                      │  • Wealth Gene Rating               │
                      └──────────────┬──────────────────────┘
                                     │
                                     ▼
                      ┌─────────────────────────────────────┐
                      │              END                     │
                      │   (analysis_report, image_url)      │
                      └─────────────────────────────────────┘
```

### Execution Flow

```
START
  ├── search (Web Search) ──> clean_data (Data Cleaning) ──┐
  └── image_gen (Image Generation) ────────────────────────┤
                                                            ├─> analysis (Wealth Gene Detection) ──> END
```

### Node Details

| Node | Type | Input | Output | Description |
|------|------|-------|--------|-------------|
| `search_node` | Task | `token_name` | `search_results`, `search_summary` | Web search with AI summary |
| `image_gen_node` | Task | `token_name` | `generated_image_url` | AI prediction image generation |
| `clean_data_node` | Task | `search_results`, `search_summary` | `sentiment_data` | Data cleaning and condensation |
| `analysis_node` | Agent | `sentiment_data`, `generated_image_url` | `analysis_report` | Multimodal wealth gene analysis |

**Parallel Execution**: Search and image generation run in parallel for efficiency.

**Convergence**: Analysis waits for both data cleaning and image generation to complete.

## Input/Output

**Input**:
- `token_name` (String): Token name, e.g., "PEPE", "SHIB", "Dogecoin"

**Output**:
- `analysis_report` (String): Humorous and professional wealth gene detection report
- `generated_image_url` (String): Generated prediction image URL

## Prerequisites

The following packages are already installed:
- `coze-coding-dev-sdk`: For LLM, search, and image generation clients
- `langgraph`: For workflow orchestration
- `langchain-core`: For message types
- `pydantic`: For data models

## Quick Start

```python
from langgraph.graph import StateGraph, END, START
from coze_coding_dev_sdk import LLMClient, SearchClient, ImageGenerationClient

# Define your nodes
def search_node(state, config, runtime):
    client = SearchClient(ctx=runtime.context)
    response = client.search(query=f"{state.token_name} token news", need_summary=True)
    return {"search_results": response.web_items, "search_summary": response.summary}

# Build your workflow
builder = StateGraph(GlobalState, input_schema=GraphInput, output_schema=GraphOutput)
builder.add_node("search", search_node)
builder.add_edge(START, "search")
# ... add more nodes and edges
main_graph = builder.compile()
```

For complete implementation details, see [python/README.md](python/README.md).

## Use Cases

### Analyze a Single Token
```python
result = main_graph.invoke({"token_name": "PEPE"})
print(result["analysis_report"])
```

### Batch Analysis
```python
tokens = ["PEPE", "SHIB", "DOGE"]
for token in tokens:
    result = main_graph.invoke({"token_name": token})
    print(f"{token}: {result['analysis_report'][:100]}...")
```

### Integration with Trading Bots
```python
def analyze_before_trade(token_name):
    result = main_graph.invoke({"token_name": token_name})
    report = result["analysis_report"]
    
    if "Diamond Hand" in report:
        return "BUY", result["generated_image_url"]
    elif "Shitcoin" in report:
        return "AVOID", None
    else:
        return "RESEARCH", result["generated_image_url"]
```

## Security Notes

- **Disclaimer**: This skill is an **analysis and entertainment tool only**. It does NOT execute trades, access wallets, connect to blockchain networks, or handle any financial transactions. All crypto/meme token references are for sentiment analysis purposes only.
- **External Requests**: This skill makes requests to external APIs:
  - Web search APIs (via coze-coding-dev-sdk)
  - Image generation APIs (via coze-coding-dev-sdk)
  - LLM APIs (doubao-seed-1-6-vision-250815)
- **Data Handling**: Token names and search results are sent to external APIs for analysis. No wallet keys, private keys, or financial credentials are ever requested or stored.
- **File Persistence**: No local file persistence, all operations are stateless
- **Sensitive Data**: No API keys stored locally, all handled via SDK
- **Input Validation**: Token names are validated and sanitized before use
- **No Storage Dependencies**: This skill does NOT use S3, database, or any persistent storage. All `src/storage/` code and related dependencies (boto3, sqlalchemy, etc.) have been removed from the skill package.

## Best Practices

1. **Use Time Range Filtering**: Always filter search results by time range for fresh data
2. **Handle Missing Data**: Gracefully handle cases where no search results are found
3. **Multimodal Analysis**: Combine text and image analysis for comprehensive insights
4. **Error Handling**: Implement robust error handling for API calls
5. **Rate Limiting**: Respect API rate limits when analyzing multiple tokens

## Limitations

- Search results depend on public web data availability
- Image generation quality varies based on token name clarity
- Analysis is for educational purposes only, not financial advice
- API rate limits may apply for high-volume usage

## Troubleshooting

**Issue**: Search returns no results
- **Solution**: Check if token name is correct and publicly known
- **Solution**: Verify network connectivity and API status

**Issue**: Image generation fails
- **Solution**: Check if prompt is appropriate and follows content guidelines
- **Solution**: Verify ImageGenerationClient initialization and API status

**Issue**: Analysis returns empty report
- **Solution**: Check if sentiment_data and image_url are properly passed
- **Solution**: Verify LLM model availability and configuration

## Support

For detailed implementation guide:
- Python SDK: [python/README.md](python/README.md)

For skill-related issues:
- Check the troubleshooting section
- Review the complete code examples in python/README.md
- Ensure all prerequisites are met

---

**Maintainer**: AntalphaAI  
**License**: MIT
