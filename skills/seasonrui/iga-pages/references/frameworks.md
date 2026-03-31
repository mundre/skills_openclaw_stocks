# Frameworks

IGA Pages **only** supports the frameworks listed below. The CLI auto-detects the framework — no configuration is required for supported frameworks.

**If the user's framework is not in this list, inform them that it is not currently supported by IGA Pages before proceeding.**

## Supported Frameworks

| Framework            | Output Dir              |
| -------------------- | ----------------------- |
| **Next.js**          | `.next`                 |
| **Vite**             | `dist`                  |
| **Vue CLI**          | `dist`                  |
| **Create React App** | `build`                 |
| **Angular**          | `dist` (see note)       |
| **Hexo**             | `public`                |
| **Docusaurus**       | `build`                 |
| **VitePress**        | `docs/.vitepress/dist`  |
| **VuePress**         | `src/.vuepress/dist`    |
| **Hugo**             | `public` (configurable) |

Frameworks **not** in this list (e.g. Nuxt, Remix, Astro, Gatsby, SvelteKit) are unsupported. Inform the user and do not attempt deployment with unsupported frameworks.
