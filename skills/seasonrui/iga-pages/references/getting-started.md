# Getting Started

## Install

```bash
npm i -g @iga-pages/cli
```

Verify installation:

```bash
iga --version
```

## First-Time Setup

1. **Get Volcengine credentials** — Obtain an Access Key (AK) and Secret Key (SK) from the [Volcengine IAM console](https://console.volcengine.com/iam/keymanage).
2. **Authenticate** — `iga login` (interactive prompt, or pass flags directly).
3. **Go to your project directory** — `cd my-project`. If you just scaffolded a new project (e.g. `npx create-next-app@latest my-app`), you **must `cd my-app`** first.
4. **Link or deploy** — Run `iga pages link` to link to an existing project, or `iga pages deploy` to create and deploy in one step.
5. **Develop locally** — `iga pages dev` starts a local server on port 3000.

### New Project Workflow

When creating a project from scratch, scaffold first, then enter the directory, then run IGA commands:

```bash
npx create-next-app@latest my-app --yes
cd my-app
iga pages deploy --name my-app
```

All `iga` commands must run from the project root directory.

## Key Files

| File                          | Purpose                                         |
| ----------------------------- | ----------------------------------------------- |
| `~/.iga/auth.json`            | Global AK/SK credentials                        |
| `<project>/.iga/project.json` | Project link (projectId, projectName, provider) |

Credential resolution order and advanced auth details: see `references/authentication.md`.
