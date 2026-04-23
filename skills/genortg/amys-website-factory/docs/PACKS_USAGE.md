# Component & animation usage examples (practical snippets)

This file gives short, copy-pasteable examples so agents can teach components to other agents and inject working code into scaffolds.

1) anime.js — basic tween

Install: `npm install animejs`

Example (fade + translate):
```js
import anime from 'animejs/lib/anime.es.js';
anime({
  targets: '.hero .title',
  translateY: [-20, 0],
  opacity: [0,1],
  duration: 700,
  easing: 'easeOutQuad'
});
```

2) framer-motion — React motion (preferred for React/Next)

Install: `npm install framer-motion`

Example:
```jsx
import { motion } from 'framer-motion';
export default function Hero(){
  return (
    <motion.h1 initial={{y:20, opacity:0}} animate={{y:0, opacity:1}} transition={{duration:0.6}}>
      Hello
    </motion.h1>
  )
}
```

3) three.js — minimal scene

Install: `npm install three`

Example (create scene + cube):
```js
import * as THREE from 'three';
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, innerWidth/innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
document.body.appendChild(renderer.domElement);
const geometry = new THREE.BoxGeometry();
const material = new THREE.MeshStandardMaterial({ color: 0x0077ff });
const cube = new THREE.Mesh(geometry, material);
scene.add(cube);
camera.position.z = 5;
function animate(){ requestAnimationFrame(animate); cube.rotation.x += 0.01; cube.rotation.y += 0.01; renderer.render(scene,camera);} animate();
```

4) lottie-web — play exported animations

Install: `npm install lottie-web`

Example:
```js
import lottie from 'lottie-web';
const anim = lottie.loadAnimation({ container: document.querySelector('#anim'), renderer: 'svg', loop: true, autoplay: true, path: '/animations/hero.json' });
```

5) Radix + shadcn (pattern)

Install primitives: `npm install @radix-ui/react-alert-dialog @radix-ui/react-tooltip` (install the primitives you need).  
shadcn provides copyable, ready components built on Radix — preferred workflow: copy component source into /components, then adapt Tailwind classes to CSS variables.

Radix example (dialog skeleton):
```jsx
import * as Dialog from '@radix-ui/react-dialog';
export default function MyDialog(){
 return (
  <Dialog.Root>
    <Dialog.Trigger>Open</Dialog.Trigger>
    <Dialog.Overlay className="fixed inset-0 bg-black/40" />
    <Dialog.Content className="bg-bg text-fg p-6 rounded">Dialog content</Dialog.Content>
  </Dialog.Root>
 )
}
```

6) Headless UI (Tailwind) example (Menu):
```jsx
import { Menu } from '@headlessui/react'
<Menu>
 <Menu.Button>Options</Menu.Button>
 <Menu.Items className="bg-white"> <Menu.Item>Item</Menu.Item> </Menu.Items>
</Menu>
```

7) PixiJS / p5.js notes
- Use for canvas-heavy 2D experiences; include an example only when the brief requests creative canvas/particle art.

Agent guidelines
- Prefer copyable source (shadcn) or headless primitives (Radix/Headless) so agents can edit components.  
- Always wire colors to the CSS variables pattern (DESIGN_GUIDE.md).  
- Add a small usage example into the component's README inside the site repo so future agents can learn locally.

