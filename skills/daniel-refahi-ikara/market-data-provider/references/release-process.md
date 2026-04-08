# Release process

## Versioning
Use semantic versioning.
- MAJOR: breaking interface or installation changes
- MINOR: backward-compatible features
- PATCH: backward-compatible fixes and documentation/test updates

## Release checklist
1. Update `VERSION`.
2. Update `SKILL.md` installation text if install behavior changed.
3. Run offline smoke test.
4. Run live EODHD smoke test when credentials are available.
5. Package the skill.
6. Verify the `.skill` artifact exists.
7. Commit with a release message.
8. Tag the git release.

## Commands
```bash
python3 skills/market-data-provider/scripts/smoke_test.py
MARKET_DATA_PROVIDER=mock python3 skills/market-data-provider/scripts/smoke_test.py
python3 ~/.npm-global/lib/node_modules/openclaw/skills/skill-creator/scripts/package_skill.py skills/market-data-provider
```

## Release artifact
Primary artifact:
- `market-data-provider.skill`

Keep the artifact in sync with committed source.
