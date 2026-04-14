# Ministry Weekly

An OpenClaw skill that turns a simple Sunday briefing into a complete weekly content package for church staff -- in one shot, no back-and-forth required.

## What It Does

Give it a sermon title, scripture, and any announcements. It returns three ready-to-use pieces:

**1. Bulletin Draft**
A clean, formatted Sunday bulletin with welcome language, sermon details, scripture reference, a brief sermon summary, and any announcements.

**2. Social Media Posts**
Three posts formatted for Facebook or Instagram -- a mid-week hype post, a day-of reminder, and a post-service reflection. Each written to feel natural, not corporate.

**3. Weekly Email Announcement**
A 150-200 word email with a subject line, ready for the church admin to send to the congregation. Covers the sermon, service times, and announcements.

## How to Trigger It

The skill detects intent from context -- you do not need to specify what you want. Examples:

- "Need content for this Sunday. Pastor is preaching on John 11, theme is resurrection hope. Two services at 9 and 11."
- "Sermon this week is Proverbs 3:5-6. Normal Sunday, 10am, potluck after. Church is Grace Fellowship."
- "We're doing a baptism service Sunday. Romans 6. Also need to announce VBS registration opens Monday."

It also responds to casual phrasing like "help me with Sunday's stuff" or "I need content for this week" in a church context.

## How to Install

1. In your OpenClaw workspace, navigate to `.openclaw/workspace/skills/`
2. Create a folder named `ministry-weekly`
3. Copy `SKILL.md` into that folder
4. Restart OpenClaw or reload skills

## Evals

The `evals/evals.json` file contains three test prompts covering different Sunday scenarios (Easter, regular Sunday, baptism service). Use these to verify the skill is working correctly after installation.

## Notes

- Works with minimal input. If something critical is truly missing (like a service time), it will ask one short question. Otherwise it makes reasonable assumptions and flags them at the end.
- Tone defaults to warm and accessible -- appropriate for most Protestant and non-denominational churches. It will adjust if your input signals a specific style (liturgical, contemporary, charismatic).
- All three outputs are clearly labeled so staff can copy each section directly without reformatting.

## Skill Metadata

| Field | Value |
|---|---|
| Name | ministry-weekly |
| Version | 1.0.0 |
| Author | Chris (zocase) |
| Compatible with | OpenClaw |
| Category | Content Production |
| Audience | Church staff, ministry communicators |
