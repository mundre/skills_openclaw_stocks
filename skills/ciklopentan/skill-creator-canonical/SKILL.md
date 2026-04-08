---
name: skill-creator
description: Create, edit, improve, or audit AgentSkills. Use when creating a new skill from scratch or when asked to improve, review, audit, tidy up, clean up, or restructure an existing skill or SKILL.md file. Also use when a skill should become easier for weaker AI models or agent runtimes to follow, with less ambiguity and clearer execution paths. Triggers on phrases like "create a skill", "author a skill", "tidy up a skill", "improve this skill", "review the skill", "clean up the skill", "audit the skill", or requests to make a skill easier for weak models.
---

# Skill Creator

This skill provides guidance for creating effective skills.

## About Skills

Skills are modular, self-contained packages that extend Codex's capabilities by providing
specialized knowledge, workflows, and tools. Think of them as "onboarding guides" for specific
domains or tasks—they transform Codex from a general-purpose agent into a specialized agent
equipped with procedural knowledge that no model can fully possess.

### What Skills Provide

1. Specialized workflows - Multi-step procedures for specific domains
2. Tool integrations - Instructions for working with specific file formats or APIs
3. Domain expertise - Company-specific knowledge, schemas, business logic
4. Bundled resources - Scripts, references, and assets for complex and repetitive tasks

## Core Principles

### Concise is Key

The context window is a public good. Skills share the context window with everything else Codex needs: system prompt, conversation history, other Skills' metadata, and the actual user request.

**Default assumption: Codex is already very smart.** Only add context Codex doesn't already have. Challenge each piece of information: "Does Codex really need this explanation?" and "Does this paragraph justify its token cost?"

Prefer concise examples over verbose explanations.

### Set Appropriate Degrees of Freedom

Match the level of specificity to the task's fragility and variability:

**High freedom (text-based instructions)**: Use when multiple approaches are valid, decisions depend on context, or heuristics guide the approach.

**Medium freedom (pseudocode or scripts with parameters)**: Use when a preferred pattern exists, some variation is acceptable, or configuration affects behavior.

**Low freedom (specific scripts, few parameters)**: Use when operations are fragile and error-prone, consistency is critical, or a specific sequence must be followed.

Think of Codex as exploring a path: a narrow bridge with cliffs needs specific guardrails (low freedom), while an open field allows many routes (high freedom).

For weak-model targeting, prefer low or medium freedom unless you can write explicit decision criteria for high freedom.

### Writing for Reliability (Weak Models)

When a skill should work reliably for weaker AI models or agent runtimes, make ambiguity expensive and navigation cheap.

1. **Write one action per sentence.** Split compound instructions into short imperative lines.
2. **Spell out branches.** Use `if -> then -> else` patterns instead of implied decisions.
3. **Add an explicit stop condition** for each logical sequence. If nothing matches, say what to do and stop.
4. **Specify the output of every action step.** Name the file, patch, message, variable, or artifact the step must produce.
5. **Avoid bare pronouns.** Repeat the noun when needed; weak models lose reference chains.
6. **Use concrete paths.** Say whether a path is absolute or relative to the skill root.
7. **Use checklists when order matters.** Do not hide required ordering inside prose.
8. **Add navigation cues for references.** Use this format when possible: `Read [filename] when [condition]. Purpose: [one verb + noun].`
9. **Provide decision rules for high-freedom tasks.** Do not grant freedom without criteria.
10. **Include a concrete example** when a step is brittle, non-obvious, or easy to misread.

These rules are not a license to bloat the skill. Keep the text short, but make every step executable without guessing.

### When a Step Is Ambiguous (Runtime Fallback)

If a skill step violates the rules above, weak models must not guess. Follow this fallback cascade:

1. **Missing output specification** -> write to `skill_output.txt` in the current working directory. Append the step number and timestamp. Do not overwrite existing content unless the skill says to overwrite.
2. **Bare pronoun** (`it`, `they`, `this`, `that`) -> look back exactly one sentence for the nearest explicit noun. If no explicit noun exists, write `Ambiguous pronoun at step X` and stop.
3. **Missing stop condition** -> treat completion of the step's single action as the stop condition. If the step contains multiple actions, do only the first action, then write `Multiple actions without stop condition — stopped after first action`.
4. **Missing navigation cue** -> do not read any reference file unless the skill explicitly says `read` and names the file.
5. **Missing decision criteria for a high-freedom step** -> choose the smallest safe action that makes progress. Write `Used safe default: <action>`.

These fallbacks do not replace good skill writing. They reduce stalls and guessing when a real-world skill is imperfect.

### Anatomy of a Skill

Every skill consists of a required SKILL.md file and optional bundled resources:

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown instructions (required)
└── Bundled Resources (optional)
    ├── scripts/          - Executable code (Python/Bash/etc.)
    ├── references/       - Documentation intended to be loaded into context as needed
    └── assets/           - Files used in output (templates, icons, fonts, etc.)
```

#### SKILL.md (required)

Every SKILL.md consists of:

- **Frontmatter** (YAML): Contains `name` and `description` fields. These are the only fields that Codex reads to determine when the skill gets used, thus it is very important to be clear and comprehensive in describing what the skill is, and when it should be used.
- **Body** (Markdown): Instructions and guidance for using the skill. Only loaded AFTER the skill triggers (if at all).

#### Bundled Resources (optional)

##### Scripts (`scripts/`)

Executable code (Python/Bash/etc.) for tasks that require deterministic reliability or are repeatedly rewritten.

- **When to include**: When the same code is being rewritten repeatedly or deterministic reliability is needed
- **Example**: `scripts/rotate_pdf.py` for PDF rotation tasks
- **Benefits**: Token efficient, deterministic, may be executed without loading into context
- **Note**: Scripts may still need to be read by Codex for patching or environment-specific adjustments

##### References (`references/`)

Documentation and reference material intended to be loaded as needed into context to inform Codex's process and thinking.

- **When to include**: For documentation that Codex should reference while working
- **Examples**: `references/finance.md` for financial schemas, `references/mnda.md` for company NDA template, `references/policies.md` for company policies, `references/api_docs.md` for API specifications
- **Use cases**: Database schemas, API documentation, domain knowledge, company policies, detailed workflow guides
- **Benefits**: Keeps SKILL.md lean, loaded only when Codex determines it's needed
- **Best practice**: If files are large (>10k words), include grep search patterns in SKILL.md
- **Avoid duplication**: Information should live in either SKILL.md or references files, not both. Prefer references files for detailed information unless it's truly core to the skill—this keeps SKILL.md lean while making information discoverable without hogging the context window. Keep only essential procedural instructions and workflow guidance in SKILL.md; move detailed reference material, schemas, and examples to references files.

##### Assets (`assets/`)

Files not intended to be loaded into context, but rather used within the output Codex produces.

- **When to include**: When the skill needs files that will be used in the final output
- **Examples**: `assets/logo.png` for brand assets, `assets/slides.pptx` for PowerPoint templates, `assets/frontend-template/` for HTML/React boilerplate, `assets/font.ttf` for typography
- **Use cases**: Templates, images, icons, boilerplate code, fonts, sample documents that get copied or modified
- **Benefits**: Separates output resources from documentation, enables Codex to use files without loading them into context

#### What to Not Include in a Skill

A skill should only contain essential files that directly support its functionality. Do NOT create extraneous documentation or auxiliary files, including:

- README.md
- INSTALLATION_GUIDE.md
- QUICK_REFERENCE.md
- CHANGELOG.md
- etc.

The skill should only contain the information needed for an AI agent to do the job at hand. It should not contain auxiliary context about the process that went into creating it, setup and testing procedures, user-facing documentation, etc. Creating additional documentation files just adds clutter and confusion.

### Progressive Disclosure Design Principle

Skills use a three-level loading system to manage context efficiently:

1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by Codex (Unlimited because scripts can be executed without reading into context window)

#### Progressive Disclosure Patterns

Keep SKILL.md body to the essentials and under 500 lines to minimize context bloat. Split content into separate files when approaching this limit. When splitting out content into other files, it is very important to reference them from SKILL.md and describe clearly when to read them, to ensure the reader of the skill knows they exist and when to use them.

**Key principle:** When a skill supports multiple variations, frameworks, or options, keep only the core workflow and selection guidance in SKILL.md. Move variant-specific details (patterns, examples, configuration) into separate reference files.

**Pattern 1: High-level guide with references**

```markdown
# PDF Processing

## Quick start

Extract text with pdfplumber:
[code example]

## Advanced features

- **Form filling**: See [FORMS.md](FORMS.md) for complete guide
- **API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
- **Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
```

Codex loads FORMS.md, REFERENCE.md, or EXAMPLES.md only when needed.

**Pattern 2: Domain-specific organization**

For Skills with multiple domains, organize content by domain to avoid loading irrelevant context:

```
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

When a user asks about sales metrics, Codex only reads sales.md.

Similarly, for skills supporting multiple frameworks or variants, organize by variant:

```
cloud-deploy/
├── SKILL.md (workflow + provider selection)
└── references/
    ├── aws.md (AWS deployment patterns)
    ├── gcp.md (GCP deployment patterns)
    └── azure.md (Azure deployment patterns)
```

When the user chooses AWS, Codex only reads aws.md.

**Pattern 3: Conditional details**

Show basic content, link to advanced content:

```markdown
# DOCX Processing

## Creating documents

Use docx-js for new documents. See [DOCX-JS.md](DOCX-JS.md).

## Editing documents

For simple edits, modify the XML directly.

**For tracked changes**: See [REDLINING.md](REDLINING.md)
**For OOXML details**: See [OOXML.md](OOXML.md)
```

Codex reads REDLINING.md or OOXML.md only when the user needs those features.

**Important guidelines:**

- **Avoid deeply nested references** - Keep references one level deep from SKILL.md. All reference files should link directly from SKILL.md.
- **Structure longer reference files** - For files longer than 100 lines, include a table of contents at the top so Codex can see the full scope when previewing.

## Canonical Skill Authoring Workflow

Use this workflow as the default path for skill creation and serious skill improvement.

### Workflow Overview

1. Understand the real task and gather concrete trigger examples.
2. Design the skill structure and reusable resources.
3. Initialize or normalize the skill folder.
4. Author or revise `SKILL.md`, `scripts/`, `references/`, and `assets/`.
5. Run the weak-model authoring pass.
6. Decide whether the change requires a full dual-thinking review.
7. Apply the review changes.
8. Validate.
9. Package.
10. Publish if needed.
11. Iterate from real usage.

Default rule:
- for **new skills**, **major rewrites**, and **serious audits**, run the full flow including dual-thinking
- for **small local edits** (for example, tiny wording fixes or very small single-file changes), you may skip the deep review and go straight to validation

Decision rule:
- if you cannot state the before/after behavior in one sentence -> do the dual-thinking review
- if the change touches more than one file -> do the dual-thinking review
- otherwise -> skip with self-check

### Skill Naming

- Use lowercase letters, digits, and hyphens only; normalize user-provided titles to hyphen-case (e.g., "Plan Mode" -> `plan-mode`).
- Generate a name under 64 characters.
- Prefer short, verb-led phrases that describe the action.
- Namespace by tool when it improves clarity or triggering (e.g., `gh-address-comments`, `linear-address-issue`).
- Name the skill folder exactly after the skill name.

### Step 1 — Understand the Real Task

Start from concrete examples, not abstract intent.

Collect:
- what the skill must do
- what a user would actually say to trigger it
- what failure modes matter
- whether the skill is mostly workflow, reference, tooling, or mixed

Ask only the minimum questions needed to remove ambiguity.

Conclude this step only when you can name:
- the trigger patterns
- the main success path
- the likely edge cases

### Step 2 — Design the Skill Structure

For each concrete example, decide what should live in:
- `SKILL.md` — core workflow and navigation
- `scripts/` — deterministic or repeated operations
- `references/` — detailed docs loaded on demand
- `assets/` — templates, boilerplate, or files used in outputs

Use this rule:
- if the same code would be rewritten repeatedly -> move it to `scripts/`
- if the same reference material would be re-explained repeatedly -> move it to `references/`
- if the same template or starter files would be recreated repeatedly -> move it to `assets/`

### Step 3 — Initialize or Normalize the Skill Folder

For a new skill, run:

```bash
scripts/init_skill.py <skill-name> --path <output-directory> [--resources scripts,references,assets] [--examples]
```

Examples:

```bash
scripts/init_skill.py my-skill --path skills/public
scripts/init_skill.py my-skill --path skills/public --resources scripts,references
scripts/init_skill.py my-skill --path skills/public --resources scripts --examples
```

For an existing skill:
- normalize naming and directory structure
- remove placeholder files that are no longer needed
- remove stray docs that do not belong in a skill package

Do not keep unused directories or decorative files.

### Step 4 — Author the Skill

Write for another agent, not for a human reader browsing casually.

#### Frontmatter

Write YAML with only:
- `name`
- `description`

The description must say both:
- what the skill does
- when to use it

Do not move trigger logic into the body; the body loads only after triggering.

#### Body

Write the body in imperative form.

For weak-model-friendly skills, prefer this shape unless there is a strong reason not to:
1. **Quick start / first action**
2. **Ordered workflow**
3. **Branch rules** (`if -> then -> else`)
4. **Reference navigation** (`Read X when Y. Purpose: Z.`)
5. **Outputs / completion condition**

Do not add headings for ceremony. Add headings only when they reduce ambiguity or help the next action become obvious.

#### Reusable Contents

Start with the reusable contents first:
- implement scripts that must be deterministic
- add references that contain variant-specific or detailed material
- add assets only when the skill needs real output files or templates

Test scripts by actually running them. If there are many similar scripts, test a representative sample.

#### Proven Patterns

When you need stronger guidance, consult:
- **Multi-step processes**: `references/workflows.md`
- **Output formats / quality standards**: `references/output-patterns.md`

### Step 5 — Run the Weak-Model Authoring Pass

Before calling the draft done, review it against these rules:

- Write one action per sentence.
- Give each logical block a clear stop condition.
- Make each step produce a concrete output when appropriate.
- Replace ambiguous pronouns with explicit nouns when the reference chain could break.
- Use explicit decision rules instead of "use judgment" when possible.
- For reference loading, prefer `Read [filename] when [condition]. Purpose: [one verb + noun].`

If the skill includes execution-style sections, make them explicit with headings like:
- `## Execution`
- `## Instructions`
- `## Runtime Fallback`
- `## Steps to Run`

### Step 6 — Deep Review Trigger

Decide whether the current change requires a full `dual-thinking` review.

Run the full review when any of these are true:
- the skill is new
- the change is a major rewrite
- the audit is substantial
- the skill has multiple interacting parts (`SKILL.md` + scripts + references + assets)
- the change alters agent behavior in non-obvious ways
- the weak-model pass exposed ambiguity that is not trivial to fix
- the user explicitly wants deep review
- you are unsure whether the skill is good enough

For a trivial edit, you may skip the deep review only when all are true:
- the change is small
- the change is local
- the change does not alter the workflow shape
- the change does not introduce new ambiguity

If a full review is triggered, use these rules:
- use the real SKILL.md text, not a summary
- include the actual pain points and desired behavior changes
- continue round by round until **both you and DeepSeek explicitly agree** that further improvement is not worth the added time, complexity, or churn
- if DeepSeek surfaces a real flaw, revise the skill and continue

If the review is skipped, write a brief self-check instead:
- what changed
- what could break
- why a full review is unnecessary for this edit

### Step 7 — Apply Review Changes

After dual-thinking:
- merge the accepted changes
- reject what is over-engineered or context-blind
- keep a simpler safer version when evidence is mixed
- update the skill text and resources before validation

If the review exposed a structural flaw, go back to Step 2 or Step 4 instead of papering over it.

### Step 8 — Validate

Run the validation stack in this order:

```bash
scripts/quick_validate.py <skill-dir>
scripts/validate_weak_models.py <skill-dir>
```

Use `validate_weak_models.py` to lint explicit execution-style sections for:
- reference cues that should use `Read ... when ... Purpose: ...`
- ordered steps that do not clearly specify an output or stop condition

If `validate_weak_models.py` warns that no execution section exists, decide whether that is expected for the skill. Reference-heavy skills may not need one.

### Step 9 — Package

Package only after the authoring pass, dual-thinking pass, and validation pass are complete.

```bash
scripts/package_skill.py <path/to/skill-folder>
```

Optional output directory:

```bash
scripts/package_skill.py <path/to/skill-folder> ./dist
```

Packaging validates the skill, rejects dangerous path escapes, and creates a distributable `.skill` archive.

### Step 10 — Publish if Needed

If the user wants distribution, publish only after packaging succeeds.

Use the normal publishing path for the environment (for example, ClawHub when appropriate). Do not publish a skill that has not completed the full workflow above.

### Step 11 — Iterate From Real Usage

After the skill is used on real tasks:
1. notice where the agent struggled
2. identify whether the fix belongs in `SKILL.md`, `scripts/`, `references/`, or `assets/`
3. update the skill
4. rerun weak-model pass, dual-thinking review, validation, and packaging as needed

## Completion Standard

A skill is ready only when all are true:
- the trigger description is clear
- the structure matches the real task shape
- reusable code and references are in the right places
- the weak-model authoring pass is complete
- the mandatory full dual-thinking review is complete
- validation passes
- packaging succeeds

If any item above is still open, the skill is still in draft.
