---
name: iga-pages
description: Develop and deploy projects on IGA Pages — CLI workflow (login, link, dev, build, deploy), serverless functions (api/ routes), and build config. Use when the user mentions IGA Pages, runs iga CLI commands, writes API routes in api/, or requests deployment ("deploy my app", "publish this site", "push this live", "deploy and give me the link", "create a preview deployment", "deploy to IGA Pages", "ship to production").
---

# IGA Pages Skill

Two areas: **CLI** (`iga` tool for auth, link, dev, build, deploy) and **Project development** (serverless functions, API routes).

Run `iga <command> -h` for full flag details.

## Critical: Project Linking

State is stored in:

- **`.iga/project.json`** — project link (projectId, projectName, provider). Created by `iga pages link` or first `iga pages deploy`.
- **`~/.iga/auth.json`** — AK/SK credentials. Created by `iga login`. Obtain AK/SK from the [Volcengine IAM console](https://console.volcengine.com/iam/keymanage).

**When to use `deploy` vs `link`**:

- **New project** → prefer `iga pages deploy` directly. It creates the project and writes `.iga/project.json` in one step, no need to `link` first.
- **Connect to an existing project without deploying** → use `iga pages link`.

## Critical: Framework Compatibility

Before deploying or scaffolding a project, verify the framework is supported. IGA Pages **only** supports: Next.js, Vite, Vue CLI, Create React App, Angular, Hexo, Docusaurus, VitePress, VuePress, Hugo. If the user's framework is not in this list, **proactively inform them it is not supported** before proceeding. See `references/frameworks.md` for output directory details.

## Critical: Working Directory

All `iga` commands (link, dev, build, deploy) must run **inside the project root** — the directory that was scaffolded or contains the project source files.

When scaffolding a new project, the tool (e.g. `create-next-app`, `npm create vite`, `hugo new site`) creates a **subdirectory**. You **must `cd` into it** before running any `iga` command. Use `working_directory` parameter or chain with `&&`:

```bash
npx create-next-app@latest my-app --yes
cd my-app && iga pages deploy --name my-app
```

Never run `iga pages deploy` or `iga pages dev` from the parent directory — it will deploy the wrong content or fail to detect the framework.

## Quick Start

```bash
npm i -g @iga-pages/cli
iga login                      # authenticate with AK/SK
cd my-project                  # enter project directory first!
iga pages deploy               # deploy (auto-creates project on first run)
iga pages link                 # link to existing project (or create new)
```

For local development:

```bash
iga pages dev                  # local development server (no linking needed)
```

## Command Structure

```
iga login      [--accessKey <ak>] [--secretKey <sk>] [--check]
iga logout
iga pages dev  [-p <port>]
iga pages build [-o <output>]
iga pages deploy [--name <name>] [--scope domestic|overseas]
iga pages link [-y]
```

## Decision Tree

Route to the correct reference:

| Topic                             | Reference                         |
| --------------------------------- | --------------------------------- |
| First-time setup / install        | `references/getting-started.md`   |
| Authentication (login/logout)     | `references/authentication.md`    |
| Deploy a project                  | `references/deployment.md`        |
| Local development server          | `references/local-development.md` |
| Build for production              | `references/build.md`             |
| Link directory to a project       | `references/link.md`              |
| Supported frameworks              | `references/frameworks.md`        |
| Serverless functions / API routes | `references/functions.md`         |

## Anti-Patterns

**CLI**

- Running `iga` commands outside the project directory → after scaffolding (`create-next-app`, `npm create vite`, etc.), always `cd` into the new directory before running any `iga` command
- Deploy without login → always `iga login` first
- GitHub not authorized before Git deploy → authorize in IGA Pages Console first; GitLab/Gitee/others silently fall back to upload
- Committing `.iga/` → it's auto-gitignored, don't remove the entry
- `provider: "upload_v2"` with GitHub remote → delete `.iga/project.json` and redeploy to switch to Git deploy

**Serverless Functions**

- Calling `app.listen()` in Express/Koa → export the app instance only, do not start a server
- Express/Koa file not named `[[default]].js` → sub-paths won't be forwarded to the framework router
- Relying on module-level state → runtime may spawn fresh process per invocation
- Using native addons → `http`, `fs`, `path`, `os`, `stream` OK; native addons unavailable in FaaS
