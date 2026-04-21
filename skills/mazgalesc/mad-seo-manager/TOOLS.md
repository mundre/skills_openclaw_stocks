# Mad SEO Manager V6 Tools

Mad SEO Manager provides a surgical suite of strategic and editorial tools for 2026-level content growth and AI visibility.

## 📊 Strategic Planning & AI Visibility

### `mad_seo:generate_roadmap` [UPGRADED]
Generates a persistent **12-Month Strategic Growth Roadmap**.
- **niche** (string): The industry/specialty.
- **location** (string): Target geography (City/Region/Global).
- **core_services** (string): List of primary offerings.
- **returns**: Creates a persistent `/root/.openclaw/shared/PROJECT_STRATEGY.json`.

### `mad_seo:analyze_share_of_voice` [NEW]
Calculates the brand's citation percentage across AI search engines (Gemini, Perplexity, etc.).
- **domain** (string): The brand's domain.
- **topics** (string[]): Key topics to check.
- **returns**: "AI Citation Score" and top competitor citations.

### `mad_seo:research_strategy` [UPGRADED]
Conducts **Omnichannel 3.0** research including SERP analysis and **Social Discovery** (Reddit/Forums).
- **topic** (string): The target keyword or topic.
- **returns**: Strategic brief with "Social Proof" points and entity grounding.

---

## ✍️ High-Authority Content Workflows

### `mad_seo:draft_article` [UPGRADED]
Generates GEO-optimized and EEAT-compliant content with **Multimodal Asset** instructions.
- **topic** (string): Topic or research brief.
- **target_keyword** (string): Primary keyword.
- **word_count** (number, optional).
- **returns**: Draft with "Multimodal Log" for required charts, tables, and evidence.

### `mad_seo:audit_eeat` [UPGRADED]
Performs a Scientific Audit with **Fabrication Guard** and **Citation Clarity** scoring.
- **file_path** (string): Path to the draft file.
- **returns**: 0-70 score and "Fabrication Alert" if fake stories are detected.

### `mad_seo:site_wide_intelligence`
Performs a Global Site Audit overlaying sitemaps with GSC metrics.
- **sitemap_url** (string): XML sitemap URL.
- **gsc_property** (string): GSC property URL.
- **returns**: Persistent entity maps and linking queues.

---

## 🛠️ Specialized Helpers

### `mad_seo:performance_audit`
Analyzes GSC/GA4 data to find "High Impression / Low CTR" optimization opportunities for the Roadmap.
- **site_url** (string): GSC property URL.
- **ga_property_id** (string, optional).

### `mad_seo:generate_schema`
Generates GEO-optimized JSON-LD schema (Article, FAQ, HowTo).
- **content_path** (string): Path to the draft.
- **type** (string): Schema type.

### `mad_seo:audit_author`
EEAT Entity Audit for authors to build niche authority signals.
- **name** (string): Author name.
- **bio** (string): Author bio.

---
*Created with surgical precision at Mad Labs.*
