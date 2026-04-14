---
name: cv-skill
description: Create professional Harvard-style resumes and CVs from user-provided candidate descriptions, structured data, or existing resumes. Use when the user wants a polished one-page or role-targeted resume, needs multiple resume versions for different job directions, wants to convert raw candidate notes into structured bullets, or needs DOCX/PDF outputs in any language from structured input data.
version: 1.0.0
---

# CV Skill

Create role-targeted, black-and-white, Harvard-style resumes from candidate descriptions, structured input, or existing resumes.

## Use this skill when

- The user wants a professional resume or CV in `.docx`
- The user gives a rough candidate description and wants the agent to draft the resume from scratch
- The user wants one candidate rewritten into multiple job-targeted versions
- The user provides a PDF, notes, or rough bullets and wants a polished resume
- The user wants tighter, more professional bullets without fluff
- The user wants a Harvard-style layout with larger spacing and clean hierarchy
- The user needs output in a language other than Chinese or English

## Workflow

### 1. Gather candidate data

Use the structured schema in `references/input-schema.md`.

If you are starting from an existing resume, extract:

- contact info
- summary / positioning
- education
- work experience
- projects
- campus or extracurricular items
- tools, languages, certificates
- target job directions

### 2. Define track-specific positioning

For each job direction, rewrite:

- resume title
- 2-3 sentence summary
- bullet emphasis within experience
- skills ordering

Keep facts intact. Do not invent results or responsibilities.

### 3. Generate the resume

Run:

```bash
python3 scripts/generate_resume.py --input assets/example_profile.json --track all --output-dir /tmp/cv-output
```

Generate a specific track:

```bash
python3 scripts/generate_resume.py --input candidate.json --track operations --output-dir /tmp/cv-output
```

Try PDF export when LibreOffice is installed:

```bash
python3 scripts/generate_resume.py --input candidate.json --track all --output-dir /tmp/cv-output --pdf
```

### 4. Validate before delivery

Check that:

- no hardcoded personal info from unrelated candidates remains
- dates and headings are consistent
- bullets are role-targeted rather than generic
- low-signal items are removed or pushed down
- generated filenames are generic and safe

## Layout rules

- Single column
- Black and white only
- Section headers with strong hierarchy
- Larger spacing than default Word exports
- Short, factual bullets
- Avoid self-evaluation phrases such as “责任心强” or “结果导向”
- Prefer evidence and scope over adjectives

## Safety rules

- Do not hardcode real candidate data into scripts
- Do not store secrets, API keys, tokens, or `.env` files in the skill folder
- Keep outputs outside the skill folder unless the user explicitly wants examples saved there
- Use `assets/example_profile.json` only as a redacted example

## Files

- `scripts/generate_resume.py`: generic generator
- `references/input-schema.md`: input contract
- `references/rewriting-guide.md`: track-specific rewriting guidance
- `assets/example_profile.json`: safe sample input
- `agents/openai.yaml`: UI metadata
