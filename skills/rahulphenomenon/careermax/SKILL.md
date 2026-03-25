---
name: careermax
description: Careermax (careermax.ai) gives you all the tools you need to land your next job. Use when the user wants to track job applications, review their resume, write cover letters, prep for interviews, find referrals, or identify skill gaps.
version: 0.1.2
metadata:
  openclaw:
    requires:
      env:
        - CAREERMAX_API_KEY
      bins:
        - npx
    primaryEnv: CAREERMAX_API_KEY
    homepage: https://careermax.ai
---

# Careermax Agent Toolkit

All the tools you need to land your next job — powered by AI.

## Setup

1. Get an API key from [Careermax Settings](https://careermax.ai/dashboard/settings/api-keys)
2. Set the environment variable: `export CAREERMAX_API_KEY="cmx_live_..."`

## What You Can Do

### Job Pipeline Tracker
Track applications through your pipeline — add roles, update statuses, view your board.
- `jobs_list` — List all jobs, filter by status (Watchlist, Applied, Screening, Interviewing, Received Offer, Rejected, Accepted)
- `jobs_get` — Get full details for a specific job
- `jobs_add` — Add a new job (preview/confirm)
- `jobs_update` — Update status, notes, or other fields (preview/confirm)

### Resume Reviewer
Get AI feedback on your resume and optimize specific sections.
- `resume_get` — View your current resume
- `resume_review` — AI resume analysis, optionally tailored to a job (1 credit)
- `resume_optimize` — Optimize a specific resume section (1 credit)

### Cover Letter Writer
Generate tailored cover letters that match your resume to job applications.
- `cover_letter_generate` — Generate a cover letter for a specific job (1 credit)

### Interview Prep
Mock interviews, company research, and feedback from past practice.
- `interviews_list` — List past and upcoming sessions
- `interviews_feedback` — Detailed AI feedback from a session
- `interviews_create` — Create a mock interview (free to create, credits on Start)
- `company_prep_get` — View existing company research
- `company_prep_generate` — Generate a company research brief (5 credits)

### Referral Finder
Find potential referrals and draft personalized outreach messages.
- `mentors_search` — Search for referrals at a target company (1 credit)
- `mentors_bookmarks` — View bookmarked contacts
- `outreach_generate` — Draft a personalized outreach message (1 credit)

### Skill Gap Analysis
Learning plans, resources, and quizzes for target roles.
- `learning_plan` — View your personalized learning plan
- `learning_quizzes` — List past quiz sessions and scores
- `learning_resources` — Generate learning resources for a topic (5 credits)
- `learning_quiz` — Generate a skill quiz (1 credit)

### Account
- `careermax_info` — Overview of capabilities and account
- `credits_get` — Check credit balance and plan tier

## How It Works

1. The skill connects to Careermax via the `@careermax/agent-toolkit` MCP server
2. Read operations are instant. Write operations use preview/confirm — you see a summary before anything changes.
3. All AI processing happens server-side on the same backend as the Careermax web app.

## Usage

```bash
# Run as MCP server (for AI agents)
npx @careermax/agent-toolkit mcp

# Or use the CLI directly
npx @careermax/agent-toolkit jobs list
npx @careermax/agent-toolkit resume review
npx @careermax/agent-toolkit cover-letter generate --job-id <id>
npx @careermax/agent-toolkit interviews create --role "Software Engineer" --company Stripe
npx @careermax/agent-toolkit credits
```
