# Publishing

## Pre-publish checklist

- confirm the slug: `google-stitch-workflow`
- confirm the release version: `1.0.0`
- confirm `SKILL.md` is self-contained enough for public readers
- confirm supporting files are intentional and minimal
- confirm you are comfortable publishing under the included MIT License

## Publish

From the parent directory:

```bash
cd /Users/luis/SKILLS/publish
clawhub login
clawhub publish ./google-stitch-workflow --slug google-stitch-workflow --name "Google Stitch Workflow" --version 1.0.0 --tags latest --changelog "Initial public release."
```

## Verify

After publishing:

```bash
clawhub search "google stitch"
```

Then check the ClawHub page and verify:

- the title and description render correctly
- the `SKILL.md` sections are readable
- the supporting reference file is included
- the changelog and version appear as expected
