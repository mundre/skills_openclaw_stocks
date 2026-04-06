# Simplify Budget

`simplify-budget` is an OpenClaw skill for running a personal budget tracker on top of a specific Google Sheets template.

It handles:
- expenses: log, find, update, delete
- income: log, find, update, delete
- recurring items: create, inspect, update, delete
- recurring questions such as `what is due this month`
- FX conversion into the tracker currency
- receipt-based expense logging
- safe category confirmation with learned aliases over time

## What This Ships

This repo contains the full skill implementation:
- [SKILL.md](./SKILL.md): agent instructions
- [SETUP.md](./SETUP.md): end-to-end installation
- `scripts/`: the actual shell scripts used by the skill
- `data/learned_category_aliases.json`: confirmed category hints learned from real usage

The `clawhub/` folder is the publishable bundle. It should be an exact mirror of the skill contents that matter at runtime.

## Required Template

This skill only works with the Simplify Budget sheet template, or a direct copy of it:
- [Simplify Budget Template](https://docs.google.com/spreadsheets/d/1fA8lHlDC8bZKVHSWSGEGkXHNmVylqF0Ef2imI_2jkZ8/edit?gid=524897973#gid=524897973)

If the sheet layout is changed, the scripts will break.

Expected tabs:
- `Expenses`
- `Income`
- `Recurring`
- `Dontedit`

Expected layout assumptions:
- `Expenses` ledger starts at row `5`
- `Income` ledger starts at row `5`
- `Recurring` ledger starts at row `6`
- active categories live in `Dontedit!L10:O39`
- expense and recurring expense categories use `=zategory<stableId>`
- recurring income uses literal `Income 💵`

## Setup

Minimum requirements:
- a copy of the template
- a Google service account JSON key
- the copied sheet shared with that service account
- `GOOGLE_SA_FILE`
- `SPREADSHEET_ID`
- `TRACKER_CURRENCY`

Optional:
- `TRACKER_CURRENCY_SYMBOL`

Install summary:
1. Copy the Google Sheet template.
2. Share the copied sheet with the service account email.
3. Install this skill in `~/.openclaw/skills/simplify-budget`.
4. Install the matching workspace wrappers in `~/.openclaw/workspace`.
5. Set the required environment variables.
6. Restart OpenClaw.

Full instructions are in [SETUP.md](./SETUP.md).

## Behavior Notes

- New expenses should go through natural-language `log.sh`.
- If the user names a category explicitly, the skill uses it directly.
- If the parser already knows the item, it suggests that category.
- If the parser does not know the item, the LLM suggests a category and asks for confirmation before writing.
- Once the user confirms, the skill can learn that alias for future suggestions.

## Example Prompts

Expenses:
- `i bought coffee for 5 euro`
- `i bought the pencil for 10 euro under business category`
- `change that coffee to 4 euro`
- `delete that coffee expense`

Income:
- `log income of 100 euro today named test income`
- `change that income account to Revolut`

Recurring:
- `add a monthly test subscription for 10 euro in simplify budget`
- `when is capcut due`

Receipts:
- `log this receipt`
- `add this grocery receipt to simplify budget`

## For Agents

Agent-specific behavior lives in [AGENTS.md](./AGENTS.md).
