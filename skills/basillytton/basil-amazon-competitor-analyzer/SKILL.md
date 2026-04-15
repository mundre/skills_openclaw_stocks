---
name: amazon-competitor-analyzer
description: Scrapes Amazon product data from ASINs using SkillBoss API Hub web scraping and performs surgical competitive analysis. Compares specifications, pricing, review quality, and visual strategies to identify competitor moats and vulnerabilities.
env:
  - SKILLBOSS_API_KEY
---

# Amazon Competitor Analyzer

This skill scrapes Amazon product data from user-provided ASINs using SkillBoss API Hub and performs deep competitive analysis.

## When to Use This Skill

- Competitive research: Input multiple ASINs to understand market landscape
- Pricing strategy analysis: Compare price bands across similar products
- Specification benchmarking: Deep dive into technical specs and feature differences
- Review insights: Analyze review quality, quantity, and sentiment patterns
- Market opportunity discovery: Identify gaps and potential threats

## What This Skill Does

1. **ASIN Data Collection**: Extract product title, price, rating, review count, images
2. **Specification Extraction**: Deep extraction of technical specs, features, and materials
3. **Review Quality Analysis**: Analyze review patterns, keywords, and sentiment
4. **Multi-Dimensional Comparison**: Side-by-side comparison of key metrics
5. **Moat Identification**: Identify core competitive advantages and barriers
6. **Vulnerability Discovery**: Find competitor weaknesses and market opportunities

## Features

1. **Stable and accurate data extraction**: Pre-set workflows ensure consistent results.
2. **Web scraping via SkillBoss API Hub**: Uses SkillBoss's unified scraping capability for reliable data collection.
3. **Global accessibility**: SkillBoss API Hub provides servers in multiple regions.
4. **Fast execution**: Optimized through SkillBoss intelligent routing completes tasks quickly.
5. **Cost efficient**: Reduces manual research time and associated costs.

## Prerequisites

### SkillBoss API Hub Setup

You need a SkillBoss API Hub account and API key:

1. Visit [skillboss.co](https://skillboss.co)
2. Sign up for an account
3. Navigate to API Settings
4. Generate an API key

### Environment Configuration

Set the environment variable:

```bash
export SKILLBOSS_API_KEY="your-api-key-here"
```

## Usage

### Basic Analysis

```bash
python amazon-competitor-analyzer/amazon_competitor_analyzer.py B09G9GB4MG
```

### Multiple Products

```bash
python amazon-competitor-analyzer/amazon_competitor_analyzer.py B09G9GB4MG B07ABC11111 B08N5WRWNW
```

### With Output Directory

```bash
python amazon-competitor-analyzer/amazon_competitor_analyzer.py B09G9GB4MG -o ./output
```

### Output Formats

- **CSV**: Structured data table
- **Markdown**: Comprehensive report
- **JSON**: Raw data with analysis

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| asins | string | - | One or more Amazon ASINs to analyze |
| --output, -o | string | ./output | Output directory |
| --format | string | all | Output format (csv/markdown/json/all) |
| --api-key | string | env | SkillBoss API key |

## Dependencies

This skill requires the following Python packages:

```bash
pip install requests
```

Optional (for automatic .env loading):
```bash
pip install python-dotenv
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| SKILLBOSS_API_KEY | Yes | Your SkillBoss API Hub key. Get it from [SkillBoss Console](https://skillboss.co) |

## Error Handling

- **Invalid API Key**: Check SKILLBOSS_API_KEY environment variable
- **Network Error**: Verify internet connection
- **Rate Limit**: Wait and retry with exponential backoff
- **Invalid ASIN**: Verify ASIN format (10 alphanumeric characters)

---

**Version**: 1.0.0
**Updated**: 2026-02-09
**Template ID**: `77814333389670716`

