# Deployment

Requires login (`~/.iga/auth.json` or env vars). **Must run from the project root** (the directory containing the project source files). If you just scaffolded a new project, `cd` into it first.

## Basic Usage

```bash
iga pages deploy                              # auto-detect Git or upload
iga pages deploy --name my-app               # explicit project name (when the first deploy cannot prompt)
iga pages deploy --name my-app --scope domestic   # deploy to domestic region
```

## Deployment Modes

The CLI automatically selects the deploy mode:

- **GitHub remote detected** → Git deploy (triggers build from GitHub)
- **Non-GitHub remote** (GitLab, Gitee, etc.) → falls back to upload deploy automatically
- **No Git remote** → upload deploy (packages and uploads)

If the project was previously linked with `provider: upload_v2`, subsequent deploys continue using upload regardless of Git remote.

## GitHub Deploy

Only GitHub is supported for Git integration:

- Your GitHub account must be authorized in IGA Pages Console
- **TTY**: opens browser for OAuth if not authorized
- **Non-TTY**: exits with error and prints the Console URL to authorize

**GitLab, Gitee, and other Git platforms** are not supported for Git deploy — the CLI falls back to upload deploy silently.

## Deployment Output

On success:

```
✔ Project deployed!
  Project ID  : proj_xxxx
  Console     : https://console.volcengine.com/dcdn/pages/detail/proj_xxxx
  Preview URL : https://xxx.iga-pages.com?iga_token=<token>&iga_time=<timestamp>
```
