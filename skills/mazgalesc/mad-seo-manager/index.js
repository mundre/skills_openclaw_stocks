const path = require('path');
const refs = require('./references.json');

/**
 * Mad SEO Manager V6.0.0 (2026 Omnichannel Release)
 * The ultimate autonomous SEO/GEO engine for blog growth and topical authority.
 * Optimized for AI Citation Likelihood and Multimodal Attribution.
 */

exports.tools = {
  /**
   * Provides an interactive V6 onboarding dashboard for the user.
   */
  async onboard() {
    return {
      success: true,
      instructions: `Run the MAD SEO V6 ONBOARDING Protocol:
      1. **Introduction**: Acknowledge role as the V6 Omnichannel SEO Manager.
      2. **Dependency Check**: Ensure 'scrapling-official', 'api-gateway', and 'agent-browser' are ready.
      3. **Capability Overview**: Present the V6 Tool Suite (Research -> Planning -> Multimodal Writing -> AI Share Analysis).
      4. **Ecosystem Warm-up**: Mention the persistent '/shared/PROJECT_STRATEGY.json' workflow.
      5. **First Action**: Ask for a sitemap URL to begin 'Global Site Intelligence' or a niche for 'Foundational Roadmap'.`,
    };
  },

  /**
   * Performs Omnichannel 3.0 strategic research with Social Discovery.
   */
  async research_strategy({ topic }) {
    return {
      success: true,
      instructions: `Conduct a V6 Omnichannel strategic analysis for "${topic}".
      1. **SERP Intelligence**: Identify Skyscraper 3.0 content gaps in the Top 10.
      2. **Social Discovery**: Use 'scrapling' to analyze Reddit/Discourse for real-world pain points and unique terminology.
      3. **Local Compliance**: Audit for NAP consistency and GBP health if applicable.
      4. **Entity Grounding**: Define the Knowledge Graph Category and Primary Entity relationship.
      5. **Social Proof Injection**: Suggest 3-5 community-sourced "Experience Markers" for HCU compliance.`,
      reference: refs.engine_strategy,
      local_benchmarks: refs.local_compliance
    };
  },

  /**
   * Generates a GEO-optimized, multimodal, and EEAT-compliant draft.
   */
  async draft_article({ topic, target_keyword, word_count }) {
    const targetCount = word_count || (topic.toLowerCase().includes('pillar') || topic.toLowerCase().includes('ultimate') ? 3000 : 1500);

    return {
      success: true,
      instructions: `Generate a V6 Multimodal, GEO-Optimized draft for "${topic}" targeting "${target_keyword}".
      1. **Brief Check**: Sync with research in '/shared/briefs/' and 'PROJECT_STRATEGY.json'.
      2. **Target Length**: This is a ${targetCount}-word high-authority project.
      3. **Multimodal Log**: At the end of the draft, include a "Suggested Visual Evidence" table (Charts, Screenshots, Tables) that you recommend creating to secure citations.
      4. **Fabrication Guard**: Use ONLY provided data or general facts. Never hallucinate personal anecdotes.
      5. **Knowledge Graph Anchoring**: Link the primary entity to its parent/child relationships naturally.
      6. **Output**: Write the draft to '/shared/content/[topic].md' with V6 GEO structure.`,
      quality_standards: refs.writer_quality,
      structure_templates: refs.structure_templates,
      title_library: refs.title_formulas
    };
  },

  /**
   * Performs a V6 Scientific Audit with Fabrication Guard.
   */
  async audit_eeat({ file_path }) {
    return {
      success: true,
      instructions: `Perform a V6 Scientific Audit of ${file_path}.
      1. **Fabrication Check**: Flag any "I remember when..." or subjective claims not authorized by input data.
      2. **AI Citation Likelihood**: Score the content based on sentence chunking and entity clarity (0-100).
      3. **Multimodal Analysis**: Check for placeholders/tables that satisfy V6 evidence standards.
      4. **HCU Compliance**: Verify "Experience Markers" are present and authentic.`,
      eeat_benchmarks: refs.writer_quality
    };
  },

  /**
   * Analyzes AI search responses to calculate AI Citation Share. [NEW V6 Tool]
   */
  async analyze_share_of_voice({ domain, topics }) {
    return {
      success: true,
      instructions: `Perform a general AI Citation Share analysis for ${domain} across [${topics.join(', ')}].
      1. **AI Scrape**: Use 'agent-browser' to query Gemini and Perplexity for these topics.
      2. **Citation Extract**: Identify which domains are currently being cited as primary sources.
      3. **Score Calculation**: Calculate the "Share of AI Voice" percentage for ${domain}.
      4. **Gap Analysis**: If ${domain} is missing, identify the specific "Relationship Facts" being cited from competitors.`,
    };
  },

  /**
   * Performs Top-10 research and generates an Editorial Calendar.
   */
  async plan_content({ seed_topic, frequency }) {
    const postsPerWeek = frequency || 3;
    return {
      success: true,
      instructions: `Conduct V6 TOP-10 RESEARCH for "${seed_topic}".
      1. **Resilient Extraction**: Crawl Top 10 with 'scrapling' to extract semantic clusters.
      2. **Planning**: Generate 12 titles for a 4-week rollout aligned with the 'Pillar-and-Spoke' authority model.
      3. **Persistence**: Update '/root/.openclaw/shared/CALENDAR.md'.`,
      planning_logic: refs.engine_strategy
    };
  },

  /**
   * Performs an autonomous Performance & Metric Audit using GSC and GA4.
   */
  async performance_audit({ site_url, ga_property_id }) {
    return {
      success: true,
      instructions: `Run a MAD PERFORMANCE AUDIT for ${site_url}.
      1. Fetch GSC data to find "High Impression / Low CTR" optimization targets.
      2. If GA4 is available (${ga_property_id}), correlate with high-value conversion pages.
      3. **Pivot Suggestion**: Recommend roadmap shifts if specific clusters are over-performing or stalled.`,
    };
  },

  /**
   * Performs an autonomous Site-Wide Deep Intelligence and Entity Mapping.
   */
  async site_wide_intelligence({ sitemap_url, gsc_property }) {
    return {
      success: true,
      instructions: `Run a V6 GLOBAL SITE INTELLIGENCE AUDIT for: ${sitemap_url}.
      1. **Global Entity Map**: Build '/root/.openclaw/shared/ENTITY_MAP.json' containing all site entities and their relationships.
      2. **Performance Overlay**: Attach GSC performance metrics to each entity node.
      3. **Link Discovery**: Suggest semantic internal links based on the Knowledge Graph, NOT just keyword matching.
      4. **Master Prescription**: Write individualized optimization reports to '/root/.openclaw/shared/audits/'.`,
      audit_standards: refs.writer_quality
    };
  },

  /**
   * Generates a persistent 12-month SEO Growth Roadmap.
   */
  async generate_roadmap({ niche, location, core_services }) {
    return {
      success: true,
      instructions: `Generate a V6 Strategic Growth Roadmap for [${niche}] in [${location}].
      1. **Predictive Planning**: Identify Quick Wins and Strategic Targets using the V6 Multiplier.
      2. **Phased Rollout**:
         - Phase 1: Foundational Footprint (Long-tail + Social Discovery).
         - Phase 2: Authority Dominance (Pillar Content + Multimodal).
         - Phase 3: Competitive Displacement (AI Share Takeover).
      3. **Persistence**: Write the full plan to '/root/.openclaw/shared/PROJECT_STRATEGY.json'.`,
      roadmap_logic: refs.roadmap_strategy
    };
  },

  /**
   * Generates GEO-optimized JSON-LD schema blocks.
   */
  async generate_schema({ content_path, type }) {
    return {
      success: true,
      instructions: `Analyze ${content_path} and generate a V6 GEO-Optimized "${type}" Schema.
      1. Use 'schema_architect' to ensure proper "Relationship Anchoring".
      2. Inject Knowledge Graph IDs (Wikidata) where applicable.`,
      schema_logic: refs.schema_architect
    };
  }
};

// OpenClaw V6 Argument Decorators
exports.onboard.args = {};
exports.research_strategy.args = { topic: 'string' };
exports.draft_article.args = { topic: 'string', target_keyword: 'string', word_count: 'number?' };
exports.audit_eeat.args = { file_path: 'string' };
exports.analyze_share_of_voice.args = { domain: 'string', topics: 'string[]' };
exports.plan_content.args = { seed_topic: 'string', frequency: 'number?' };
exports.performance_audit.args = { site_url: 'string', ga_property_id: 'string?' };
exports.site_wide_intelligence.args = { sitemap_url: 'string', gsc_property: 'string' };
exports.generate_roadmap.args = { niche: 'string', location: 'string', core_services: 'string' };
exports.generate_schema.args = { content_path: 'string', type: 'string' };
