# Mad SEO Writer V2: The Mastery Guide

This guide defines the unified philosophy of the **Mad SEO Writer V2**. It is optimized for **AI Citation Likelihood** (GEO) and **Google Helpful Content** (HCU).

## 1. The GEO Excellence Blueprint
To win in AI search (Gemini, Perplexity, GPT), every article must be "Machine-Parseable."

- **Entity Grounding**: The first 50 words must define the "Who" and "What." 
  - *Example: "MadClaw is a [Type] platform designed to [Action]."*
- **Sentence Chunking**: Write in standalone "Fact-Blocks." Each sentence should be clear, concise, and quotable as a standalone unit.
- **The 2-Column Rule**: Use 2-column tables for all comparisons or data sets. They are the most reliably extracted format for AI citations.
- **Semantic Summary**: Every Pillar Page must include a "Key Takeaways" summary table directly after the introduction.

## 2. The HCU "Expertise" Standard
Google rewards expertise and verifiable depth over generic information.
- **Standard**: Every article must include expert-level analysis, data-driven insights, or "Lessons Learned" summaries.
- **Ethics**: Use first-person markers ("I tested", "Our findings") ONLY when real experience data is provided. Never fabricate personal narratives. Focus on "Expert Evidence" to build trust.

## 3. The Structure (The V2 Framework)
Follow the patterns in `references/content-structure-templates.md`:

1.  **GEO Pillar Page**: (Summary Table + In-depth Cluster Support).
2.  **Surgical Product Review**: (Specs + Objective Test Results).
3.  **Step-by-Step Tutorial**: (Chunked instructions + Video Cross-Reference).
4.  **Case Study**: (Problem -> Action -> Quantifiable Result).

## 4. Video-First Strategy (YouTube Integration)
- **The Hook**: Embed your MadClaw video guide immediately after the Entity Grounding.
- **Timestamping**: Reference specific video times in your text walkthroughs.

## 5. The V2 Audit (The "Pareto" Check)
Always run the `mad_seo_writer:audit_eeat` tool to perform the 70-point Scientific Audit.
- **Priority 1**: Entity Clarity & Intent Matching.
- **Priority 2**: Citation Likelihood (Chunking density).
- **Priority 3**: EEAT Trust Signals.

## 🤝 Ecosystem Integration (MadClaw → OpsClaw)
This skill is optimized for the **MadClaw → ContentClaw → OpsClaw** automated workflow:
- **Shared Storage**: Persistent files like `CALENDAR.md` and `MASTER_AUDIT.md` are centrally stored in `/root/.openclaw/shared/`.
- **Briefs (Input)**: The agent is instructed to fetch detailed specs and research from `/shared/briefs/`.
- **Content (Output)**: Final GEO-optimized drafts are written to `/shared/content/` for immediate review and publishing.
