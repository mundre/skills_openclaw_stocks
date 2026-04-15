# Mad SEO Manager 🚀

**Mad SEO Manager** is the ultimate autonomous content and authority engine for OpenClaw. It transforms the standard SEO writing process into a director-level management workflow, optimized for **Google HCU** and **2026-level GEO (Generative Engine Optimization)**.

## 🎯 Core Capabilities
- **Global Site Intelligence Engine (V5)**: Builds a site-wide Knowledge Graph (ENTITY_MAP) to autonomously recommend surgical internal links.
- **Competitive SERP Analyst**: Fetch and correlate the Top 5 competitors for every article to identify content and authority gaps.
- **Performance-Driven Logic**: Bridges with GSC/GA4 to prioritize optimizations for high-impression / low-CTR pages.
- **EEAT-Surgical Writing**: Enforces a 70-point quality audit focused on AI Citation Likelihood and Experience markers.

## 🛠️ Tools & Triggers

### `mad_seo:research_strategy`
*Trigger: "Build a cluster for [Topic]"*
Generates Skyscraper 2.0 plans and Hub-and-Spoke authority maps.

### `mad_seo:draft_article`
*Trigger: "Write a pillar post about [Topic]"*
Generates 1,500-2,500+ word articles with Answer-First formatting and 7 GEO Factors.

### `mad_seo:plan_content`
*Trigger: "Design a content plan for [Topic]"*
Performs exhaustive Top-10 resilient research and generates a persistent `CALENDAR.md`.

### `mad_seo:site_wide_intelligence`
*Trigger: "Run a deep intelligence audit on [Sitemap]"*
Performs a data-correlated audit: overlays sitemap URLs with live GSC metrics and generates individual `/audits/[slug].md` reports.

### `mad_seo:performance_audit`
*Trigger: "Analyze my search performance"*
Bridges GSC/GA4 data to find "High Impression / Low CTR" optimization opportunities.

## 🧩 Dependencies (For Manager Features)
> [!IMPORTANT]
> To unlock the autonomous V3 features, the following skills must be installed in the agent workspace:
> 1. **`api-gateway`** — Required for Search Console & Analytics data.
> 2. **`scrapling-official`** — Required for resilient rendering and Top-10 analysis.
> 3. **`agent-browser-clawdbot`** — Recommended for deep competitor research.

## 📖 Usage Guide
For detailed instructions on customizing the Brand Voice or setting up the API Bridge, refer to the included `GUIDE.md`.

## 🛡️ Compliance & Responsible Use
- **Authorized Audits Only**: The `site_wide_audit` tool should only be used on websites you own or have explicit permission to audit.
- **Public Data Research**: Planning tools are designed for analyzing **publicly available** competitive search data.
- **Terms of Service**: Users are responsible for ensuring that all automated discovery and research tasks comply with the target site's `robots.txt` and Terms of Service.
- **Data Privacy**: No personal or sensitive data is collected or processed by this skill.

### `mad_seo:onboard`
*Trigger: "Onboard me" or "What can you do?"*
Launches the interactive Manager Dashboard and checks for dependency health.

---
*Created with surgical precision at Mad Labs.*

## 🛡️ Technical Requirements & Security
To maintain professional stability and security, this skill requires the following:
- **Mandatory Dependencies**: `api-gateway` (for GSC/GA4 access) and `scrapling-official` (for resilient research).
- **Filesystem Permissions**: Requires write access to `/root/.openclaw/shared/` to store persistent site-wide entity maps, editorial calendars, and linking queues.
- **Privacy Policy**: This skill does NOT store or manage credentials. All GSC/GA4 access is delegated to your local `api-gateway` skill. All scraping is performed via authorized sitemaps.
