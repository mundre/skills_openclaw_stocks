## Component packs & UI primitives — open-source options

This skill uses only free/open-source libraries and recommends non-paid component packs. Recommended stacks and tradeoffs:

- shadcn/ui: open-source, accessible components built with Radix + Tailwind. Components are copyable source — excellent for editable, production-ready UIs.
- Radix UI: low-level, accessibility-first primitives (headless). Pair with Tailwind or CSS variables for styling.
- Headless UI: unstyled primitives from Tailwind Labs — simple and lightweight.
- Flowbite / DaisyUI / HyperUI: free Tailwind component kits for quick prototyping (fast, but review accessibility).  

Animation & graphics (open-source):
- anime.js — lightweight JS animation engine for UI motion (https://animejs.com).  
- three.js — 3D graphics for the web (https://threejs.org).  
- framer-motion — React animation library (open-source) for interactive UIs.  
- motion one — performant small animation library for modern browsers.  
- lottie-web (Bodymovin) — play exported After Effects animations (open-source players).  
- p5.js / PixiJS — creative 2D graphics and canvas rendering.
- A-Frame — WebXR scene building (if 3D/VR desired).

How the skill will integrate these (agent-friendly):
1. Default UI stack: shadcn + Radix + Tailwind (all OSS).  
2. For motion: prefer framer-motion or anime.js; use lottie-web for complex vector animations.  
3. For creative graphics/3D: three.js or PixiJS; A-Frame for WebXR.  
4. Wire all styles to the CSS variables from DESIGN_GUIDE.md so themes are switchable and consistent.  
5. Run accessibility and performance checks during verify (axe, Lighthouse, Playwright).  

Quick install examples (agents will run these when creating a site):
```
npm install @radix-ui/react-*/ @shadcn/ui tailwindcss postcss autoprefixer
npm install framer-motion animejs lottie-web three
```

Notes:
- No paid or proprietary component packs are included or required.  
- Agents should prefer copying component source (shadcn) or using Radix primitives so generated sites remain editable and dependency-light.
