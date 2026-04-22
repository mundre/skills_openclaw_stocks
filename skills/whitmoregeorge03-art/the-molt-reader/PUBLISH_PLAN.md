# The Molt Reader, publish plan

## Folder contents
- SKILL.md
- ENDPOINTS.md
- README.md
- SECURITY.md
- CHANGELOG.md
- LICENSE.txt

## Local validation
1. Put the folder in the active workspace skills directory.
2. Run `openclaw skills list`.
3. Run `openclaw skills info the_molt_reader`.
4. Run `openclaw skills check`.
5. Start a new session and test the prompts listed in README.md.

## ClawHub publish flow
1. Install the ClawHub CLI: `npm i -g clawhub`
2. Authenticate in the CLI if prompted.
3. Dry-run the publish plan:
   `clawhub skill publish ./molt-reader-skill --slug the-molt-reader --name "The Molt Reader" --version 1.0.0 --changelog "Initial public release" --tags latest,media,reader --dry-run`
4. If the dry-run looks correct, publish:
   `clawhub skill publish ./molt-reader-skill --slug the-molt-reader --name "The Molt Reader" --version 1.0.0 --changelog "Initial public release" --tags latest,media,reader`
5. Install from a clean workspace and re-test:
   `openclaw skills install the-molt-reader`

## Submission notes
- Publish only after the live site exposes at least the basic endpoints the skill expects, or update SKILL.md to make clear which endpoints are currently live.
- Keep the skill read-only.
- Do not add hidden tool execution, shell commands, or credential requirements unless absolutely necessary.
