const path = require('path');
const refs = require('./references.json');

/**
 * Mad SEO Manager V3.1.5 (Compliance & Stability Release)
 * The ultimate autonomous SEO engine for blog growth and topical authority.
 * Optimized for GE (Generative Engine) visibility and HCU Compliance.
 */

exports.tools = {
  /**
   * Provides an interactive onboarding dashboard for the user.
   */
  async onboard() {
    return {
      success: true,
      instructions: `Run the MAD SEO ONBOARDING Protocol:
      1. **Introduction**: Introduce yourself as the Mad SEO Manager.
      2. **Dependency Check**: Verify if 'scrapling-official' and 'api-gateway' skills are available.
      3. **Capability Overview**: Present a table of your top "Manager" tools.
      4. **Ecosystem Check**: Acknowledge awareness of the '/shared/briefs/' (Input) and '/shared/content/' (Output) workflow.
      5. **First Step**: Ask for a sitemap URL or the topic to plan.`,
    };
  },

  /**
   * Provides the strategic framework for a topic with GEO grounding.
   */
  async research_strategy({ topic }) {
    return {
      success: true,
      instructions: `Conduct a Scientific GEO strategic analysis for "${topic}".
      1. Keyword Intelligence: Define search volume and difficulty.
      2. SERP Analysis: Identify Skyscraper 2.0 gaps.
      3. Entity Grounding: Define the primary Category and Entity for this topic.
      4. Topic Cluster: Map the Hub-and-Spoke authority model.`,
      reference: refs.engine_strategy
    };
  },

  /**
   * Generates a GEO-optimized and EEAT-compliant draft.
   */
  async draft_article({ topic, target_keyword, word_count }) {
    const targetCount = word_count || (topic.toLowerCase().includes('pillar') || topic.toLowerCase().includes('ultimate') ? 2500 : 1500);

    return {
      success: true,
      instructions: `Generate a V2 GEO-Optimized draft for "${topic}" targeting "${target_keyword}".
      1. **Brief Check**: Look for research and specifications in '/shared/briefs/' if applicable.
      2. **Target Length**: This is a ${targetCount}-word project.
      3. **HCU Integrity**: Focus on expert evidence-based analysis. Never fabricate personal stories.
      4. **Sentence Chunking**: Write each sentence as a standalone, clear fact for AI extraction.
      5. **7 GEO Factors**: Apply Entity Clarity and Structural Clarity.
      6. **Output**: Write the final draft to '/shared/content/[topic].md'.
      7. **CORE-EEAT**: Apply the surgical quality standards found in the reference.`,
      quality_standards: refs.writer_quality,
      structure_templates: refs.structure_templates,
      title_library: refs.title_formulas
    };
  },

  /**
   * Performs the 70-point Scientific SEO & EEAT Audit.
   */
  async audit_eeat({ file_path }) {
    return {
      success: true,
      instructions: `Perform a V2 Scientific Audit of ${file_path}.
      1. Score the content using the 70-point GEO Audit (0-70).
      2. Categorize failures into "Top 10 High-Impact Citation Killers" (Pareto).
      3. Measure "Citation Likelihood" based on sentence chunking and entity grounding.
      4. Verify expertise markers are present for HCU compliance.`,
      eeat_benchmarks: refs.writer_quality
    };
  },

  /**
   * Performs exhaustive Top-10 research and generates a 4-week Editorial Calendar.
   */
  async plan_content({ seed_topic, frequency, competitor_url }) {
    const postsPerWeek = frequency || 3;
    return {
      success: true,
      instructions: `Conduct RESILIENT TOP-10 RESEARCH for "${seed_topic}" ${competitor_url ? `with focus on competitor: ${competitor_url}` : ''}.
      1. **Resilient Intelligence**: Use 'scrapling:fetch' to extract content from TOP 10 search results.
      2. **Gap Mapping**: Identify semantic gaps and entity trends across the Top 10.
      3. **Content Plan**: Generate 12 titles (if ${postsPerWeek} articles/week) for a 4-week rollout.
      4. **Cluster Logic**: Label articles as 'Pillar' or 'Cluster' correctly.
      5. **Calendar Persistence**: Write to '/root/.openclaw/shared/CALENDAR.md' with Status fields [Planned, In Progress, Published].`,
      planning_logic: refs.engine_strategy,
      defaults: { frequency: postsPerWeek, duration_weeks: 4, competitor: competitor_url }
    };
  },

  /**
   * Performs an autonomous Performance & Metric Audit using GSC and GA4.
   */
  async performance_audit({ site_url, ga_property_id }) {
    return {
      success: true,
      instructions: `Run a MAD PERFORMANCE AUDIT for ${site_url}.
      1. **GSC Analysis**: Discover "High Impression / Low CTR" (<1.0%) pages.
      2. **Analysis**: Correlate search data with conversion events if GA4 property ${ga_property_id} is available.
      3. **Strategic Triggers**: Suggest 'headline_pro' for Low CTR or 'content_refresh' for position 11-20 pages.`,
    };
  },

  /**
   * Content Refresh logic for V2.
   */
  async content_refresh({ target }) {
    return {
      success: true,
      instructions: `Develop a GEO-focused Refresh Strategy for ${target}.
      1. Update facts/stats to maintain freshness.
      2. Re-verify Entity Grounding to reclaim lost AI citations.`,
      refresh_logic: refs.engine_strategy
    };
  },

  /**
   * Performs an autonomous Site-Wide Deep Intelligence, Competitive Analysis, and Internal Linking Audit.
   */
  async site_wide_intelligence({ sitemap_url, gsc_property }) {
    return {
      success: true,
      instructions: `Run a GLOBAL SITE INTELLIGENCE AUDIT for: ${sitemap_url}.
      1. **Phase 1: Mapping**: Fetch the sitemap and crawl all titles/entities to build a site-wide '/root/.openclaw/shared/ENTITY_MAP.md'. This is your Global Site Memory.
      2. **Phase 2: Performance Overlay**: Overlay GSC data from property ${gsc_property} via 'api-gateway'.
      3. **Phase 3: Competitive & Linking Loop**: For each URL:
         - **Competitive Fetch**: Use 'scrapling' to analyze TOP 5 SERP results for the article's keyword.
         - **Gap Discovery**: Identify entities, assets, or sections the competitors have that we lack.
         - **Internal Linking**: Cross-reference current content with 'ENTITY_MAP.md' to suggest semantic internal links.
         - **Individual Report**: Write a dedicated report to '/root/.openclaw/shared/audits/[url-slug].md' including sections for:
              - '🚀 Competitive Gap Analysis'
              - '🔗 Internal Linking Strategy' (Anchor + Target URL)
      4. **Phase 4: Global Queue**: Update '/root/.openclaw/shared/LINKING_QUEUE.md' with all new linking opportunities.
      5. **Master Synthesis**: Update '/root/.openclaw/shared/MASTER_AUDIT.md' linking to individual optimization prescriptions.`,
      audit_standards: refs.writer_quality
    };
  },

  /**
   * Title Formulas for V2.
   */
  async headline_pro({ topic }) {
    return {
      success: true,
      instructions: `Generate 10+ GEO-grounded headlines for "${topic}". Ensure the "Entity" is clearly identifiable.`,
      title_formulas: refs.title_formulas
    };
  },

  /**
   * Snippet targeting for Position Zero.
   */
  async snippet_optimizer({ text, type }) {
    return {
      success: true,
      instructions: `Optimize this block for a "${type}" snippet. Focus on "Citation Likelihood" using clear, chunked sentences.`,
      original_text: text
    };
  },

  /**
   * Standard Metadata Generation.
   */
  async metadata_suite({ topic }) {
    return {
      success: true,
      instructions: `Generate optimized Meta Title, Meta Description, and URL Slug for "${topic}".`,
      title_patterns: refs.title_formulas
    };
  }
};

// OpenClaw Argument Decorators
exports.research_strategy.args = { topic: 'string' };
exports.draft_article.args = { topic: 'string', target_keyword: 'string', word_count: 'number?' };
exports.audit_eeat.args = { file_path: 'string' };
exports.content_refresh.args = { target: 'string' };
exports.headline_pro.args = { topic: 'string' };
exports.snippet_optimizer.args = { text: 'string', type: 'string' };
exports.metadata_suite.args = { topic: 'string' };
exports.site_wide_intelligence.args = { sitemap_url: 'string', gsc_property: 'string' };
exports.plan_content.args = { seed_topic: 'string', frequency: 'number?', competitor_url: 'string?' };
exports.performance_audit.args = { site_url: 'string', ga_property_id: 'string?' };
exports.onboard.args = {};
