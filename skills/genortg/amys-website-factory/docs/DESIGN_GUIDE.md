# Design & theming guide

This skill standardizes theming so every generated site uses the same variable names and a simple switchable theme system.

Color variable names (always present):
- --color-bg (page background)
- --color-fg (primary text)
- --color-muted (muted text/borders)
- --color-accent-1 (primary accent / buttons)
- --color-accent-2 (secondary accent / links)

Tailwind integration (recommended pattern):

1) Define CSS variables in :root (and a .theme--<name> modifier for alternate palettes):

```css
:root {
  --color-bg: 255 255 255; /* stored as R G B */
  --color-fg: 17 24 39;
  --color-muted: 107 114 128;
  --color-accent-1: 59 130 246;
  --color-accent-2: 16 185 129;
}
.theme--midnight { --color-bg: 6 7 9; --color-fg: 243 244 246; }
```

2) Tell Tailwind to use CSS vars (tailwind.config.js snippet):

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        bg: 'rgb(var(--color-bg) / <alpha-value>)',
        fg: 'rgb(var(--color-fg) / <alpha-value>)',
        muted: 'rgb(var(--color-muted) / <alpha-value>)',
        accent1: 'rgb(var(--color-accent-1) / <alpha-value>)',
        accent2: 'rgb(var(--color-accent-2) / <alpha-value>)',
      }
    }
  }
}
```

3) Use in components:

`className="bg-bg text-fg"` and `bg-[color:rgb(var(--color-accent-1)/1)]` when needed.

Theme switching is achieved by toggling a root class (e.g., `document.documentElement.classList.add('theme--midnight')`).

Accessibility notes:
- Ensure 4.5:1 contrast for normal text; 3:1 for large text. Generate alternate palettes and run contrast checks in verify step.

