# Mad SEO Writer Tools

Mad SEO Writer provides a surgical suite of strategic and editorial tools for high-impact content growth.

## Core High-Rank Workflows

### mad_seo:research_strategy
Generates a deep strategic plan for a topic based on **Skyscraper 2.0**, **Topic Cluster** (Hub-and-Spoke), and **Entity Grounding** models.
- **topic** (string): The target keyword or topic.
- **returns**: A strategic research brief including content gaps, competitor weaknesses, and primary entity definitions for GEO.

### mad_seo:draft_article
Generates a fully GEO-optimized and EEAT-compliant long-form article using **Sentence Chunking** and **Experience Mandates**.
- **topic** (string): Topic or research brief.
- **target_keyword** (string): Primary keyword to rank for.
- **word_count** (number, optional): Minimum word count (1,500 for standard, 2,500+ for pillars).
- **returns**: The drafted article with title options, meta description, FAQ section, and a Semantic Summary Table.

### mad_seo:site_wide_intelligence
Performs a GLOBAL SITE INTELLIGENCE AUDIT including competitive analysis and internal linking.
- **sitemap_url** (string): The URL of the XML sitemap.
- **gsc_property** (string): The GSC property URL to correlate with.
- **returns**: Individualreports in '/root/.openclaw/shared/audits/', a global '/root/.openclaw/shared/ENTITY_MAP.md', and a '/root/.openclaw/shared/LINKING_QUEUE.md'.
- **requires**: 'scrapling-official' and 'api-gateway' skills.

### mad_seo:plan_content
Generates a 4-week Editorial Calendar based on exhaustive Top-10 resilient research.
- **seed_topic** (string): The main topic or pillar theme.
- **frequency** (number, optional): Articles per week (default: 3).
- **competitor_url** (string, optional): Target a specific competitor for surgical gap analysis.
- **returns**: A persistent '/root/.openclaw/shared/CALENDAR.md' file with topic cluster mapping.
- **requires**: 'scrapling-official' for resilient competitor intelligence.

### mad_seo:performance_audit
Analyzes real-world performance data from Google Search Console and GA4 to identify optimization opportunities.
- **site_url** (string): The URL of the property in GSC.
- **ga_property_id** (string, optional): The GA4 property ID for session/conversion data.
- **returns**: A prioritized SEO Action List based on live metrics.
- **requires**: 'api-gateway' for Google API connectivity.

### mad_seo:audit_eeat
Performs the **70-point Scientific SEO & EEAT Audit**. Focuses on AI Citation Likelihood and HCU Experience markers.
- **file_path** (string): Path to the draft file.
- **returns**: Audit report with a 0-70 score and the "Top 10 High-Impact Citation Killers."

### mad_seo:content_refresh
Analyzes a draft or URL to develop a **GEO-focused Refresh Strategy** to maintain freshness and reclaim lost AI citations.
- **target** (string): URL or local file path to analyze.
- **returns**: A refresh checklist focused on "Quotable Facts" and entity re-verification.

---

## Specialized Publishing Helpers

### mad_seo:headline_pro
Generates high-CTR, GEO-grounded headlines using the **Title Formula** library.
- **topic** (string): The article topic or current title to optimize.
- **returns**: 10+ headline variations with CTR analysis.

### mad_seo:snippet_optimizer
Formats specific content blocks to maximize **AI Citation Likelihood** for definitions, lists, and tables.
- **text** (string): The section text to optimize.
- **type** (string): The snippet type (e.g., "list", "table", "definition").
- **returns**: Formatted markdown with chunked sentences and 2-column tables.

### mad_seo:metadata_suite
Generates optimized Meta Titles, Meta Descriptions, and Slug recommendations.
- **topic** (string): The article topic and keywords.
- **returns**: Reusable metadata block with front-loaded keywords and clear CTAs.
