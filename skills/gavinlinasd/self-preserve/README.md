# self-preserve

Backup readiness self-assessment for your OpenClaw agent.

## Install

```bash
npx clawhub@latest install self-preserve
```

## What it does

Self-preserve checks whether your agent's important files have recent backups. It runs `ls` to check file names and dates across your OpenClaw directories, then generates a readiness report showing what's protected and what's at risk.

It does not read file contents, access credentials, or make network calls. See [SKILL.md](./SKILL.md) for the full assessment steps and safety rules.

## Status

Under active development. See [SKILL.md](./SKILL.md) for full details.

## License

MIT-0
