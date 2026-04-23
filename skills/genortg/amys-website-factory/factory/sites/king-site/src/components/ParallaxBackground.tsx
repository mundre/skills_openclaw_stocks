'use client';

import { useEffect, useRef } from 'react';

export default function ParallaxBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d')!;
    let animId: number;
    let w = 0, h = 0;
    let mouseX = 0, mouseY = 0;

    const resize = () => {
      w = canvas.width = window.innerWidth;
      h = canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', resize);
    resize();

    window.addEventListener('mousemove', (e) => {
      mouseX = (e.clientX / w - 0.5) * 2;
      mouseY = (e.clientY / h - 0.5) * 2;
    });

    // Stars
    const stars: { x: number; y: number; size: number; speed: number; opacity: number }[] = [];
    for (let i = 0; i < 200; i++) {
      stars.push({
        x: Math.random() * w,
        y: Math.random() * h,
        size: Math.random() * 2 + 0.5,
        speed: Math.random() * 0.5 + 0.1,
        opacity: Math.random() * 0.8 + 0.2,
      });
    }

    // Floating orbs
    const orbs: { x: number; y: number; radius: number; vx: number; vy: number; color: string; life: number; maxLife: number }[] = [];
    for (let i = 0; i < 8; i++) {
      orbs.push({
        x: Math.random() * w,
        y: Math.random() * h,
        radius: Math.random() * 80 + 40,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        color: `hsla(${40 + Math.random() * 20}, 100%, ${50 + Math.random() * 30}%, `,
        life: 0,
        maxLife: Math.random() * 1000 + 500,
      });
    }

    const draw = () => {
      animId = requestAnimationFrame(draw);
      ctx.clearRect(0, 0, w, h);

      // Stars with parallax
      stars.forEach(s => {
        const parallaxX = mouseX * s.speed * 10;
        const parallaxY = mouseY * s.speed * 10;
        const twinkle = 0.5 + 0.5 * Math.sin(Date.now() * 0.003 + s.x);
        ctx.beginPath();
        ctx.arc(s.x + parallaxX, s.y + parallaxY, s.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 215, 0, ${s.opacity * twinkle})`;
        ctx.fill();
      });

      // Floating orbs
      orbs.forEach(o => {
        o.x += o.vx;
        o.y += o.vy;
        o.life++;

        if (o.x < -o.radius) o.x = w + o.radius;
        if (o.x > w + o.radius) o.x = -o.radius;
        if (o.y < -o.radius) o.y = h + o.radius;
        if (o.y > h + o.radius) o.y = -o.radius;

        const alpha = Math.min(o.life / 60, (o.maxLife - o.life) / 60, 0.15);
        const gradient = ctx.createRadialGradient(o.x, o.y, 0, o.x, o.y, o.radius);
        gradient.addColorStop(0, o.color + alpha + ')');
        gradient.addColorStop(1, o.color + '0)');
        ctx.beginPath();
        ctx.arc(o.x, o.y, o.radius, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();

        if (o.life >= o.maxLife) {
          o.x = Math.random() * w;
          o.y = Math.random() * h;
          o.life = 0;
          o.maxLife = Math.random() * 1000 + 500;
        }
      });
    };
    draw();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return <canvas ref={canvasRef} style={{ position: 'fixed', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none', zIndex: 0 }} />;
}
