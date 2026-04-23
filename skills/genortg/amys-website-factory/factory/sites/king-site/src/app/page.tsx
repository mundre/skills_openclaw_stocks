'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import Crown3D from '@/components/Crown3D';

/* ─── Particle Canvas ─── */
function ParticleCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d')!;
    let animId: number;
    let particles: { x: number; y: number; vx: number; vy: number; size: number; life: number; maxLife: number }[] = [];
    let w = 0, h = 0;

    const resize = () => {
      w = canvas.width = window.innerWidth;
      h = canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', resize);
    resize();

    const spawn = () => ({
      x: Math.random() * w,
      y: Math.random() * h,
      vx: (Math.random() - 0.5) * 0.3,
      vy: -Math.random() * 0.8 - 0.2,
      size: Math.random() * 3 + 1,
      life: 0,
      maxLife: Math.random() * 200 + 100,
    });

    particles = Array.from({ length: 80 }, spawn);

    const draw = () => {
      ctx.clearRect(0, 0, w, h);
      particles = particles.map(p => {
        p.x += p.vx;
        p.y += p.vy;
        p.life++;
        const alpha = Math.max(0, 1 - p.life / p.maxLife);
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 215, 0, ${alpha * 0.6})`;
        ctx.fill();
        if (p.life >= p.maxLife) return spawn();
        return p;
      });
      animId = requestAnimationFrame(draw);
    };
    draw();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return <canvas id="particles" ref={canvasRef} />;
}

/* ─── Sparkle Cursor ─── */
function SparkleCursor() {
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (Math.random() > 0.3) return;
      const el = document.createElement('div');
      el.className = 'sparkle';
      el.style.left = e.clientX - 4 + 'px';
      el.style.top = e.clientY - 4 + 'px';
      document.body.appendChild(el);
      setTimeout(() => el.remove(), 600);
    };
    window.addEventListener('mousemove', handler);
    return () => window.removeEventListener('mousemove', handler);
  }, []);
  return null;
}

/* ─── Scroll Reveal ─── */
function Reveal({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setTimeout(() => el.classList.add('visible'), delay);
        obs.disconnect();
      }
    }, { threshold: 0.15 });
    obs.observe(el);
    return () => obs.disconnect();
  }, [delay]);
  return <div ref={ref} className="reveal">{children}</div>;
}

/* ─── Animated Counter ─── */
function Counter({ target, duration = 2000, suffix = '' }: { target: number; duration?: number; suffix?: string }) {
  const [val, setVal] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        const start = performance.now();
        const tick = (now: number) => {
          const p = Math.min((now - start) / duration, 1);
          const ease = 1 - Math.pow(1 - p, 3);
          setVal(Math.floor(ease * target));
          if (p < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
        obs.disconnect();
      }
    }, { threshold: 0.5 });
    obs.observe(el);
    return () => obs.disconnect();
  }, [target, duration]);

  return <span ref={ref}>{val.toLocaleString()}{suffix}</span>;
}

/* ─── Navbar ─── */
function Navbar() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 60);
    window.addEventListener('scroll', handler);
    return () => window.removeEventListener('scroll', handler);
  }, []);

  const links = ['Home', 'Empire', 'Achievements', 'Legacy', 'Contact'];

  return (
    <nav className={`navbar ${scrolled ? 'scrolled' : ''}`}>
      <div className="text-xl font-bold gold-text tracking-widest">KING GENOR</div>
      <div className="flex gap-8">
        {links.map(l => (
          <a key={l} href={`#${l.toLowerCase()}`} className="nav-link">{l}</a>
        ))}
      </div>
    </nav>
  );
}

/* ─── Hero ─── */
function Hero() {
  const [text, setText] = useState('');
  const full = 'Behold the Sovereign of All Things Awesome';
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let i = 0;
    const iv = setInterval(() => {
      if (i <= full.length) {
        setText(full.slice(0, i));
        i++;
      } else clearInterval(iv);
    }, 60);
    return () => clearInterval(iv);
  }, []);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        el.classList.add('visible');
        obs.disconnect();
      }
    });
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  return (
    <section id="home" className="hero-section">
      <div className="hero-glow" />

      {/* 3D Crown */}
      <div ref={ref} className="reveal" style={{ position: 'relative', width: '520px', height: '420px', zIndex: 2, marginBottom: '20px' }}>
        <Crown3D />
      </div>

      <motion.h1 initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: 0.8, delay: 0.2 }} className="gold-text text-5xl md:text-7xl font-bold mb-6" style={{ fontFamily: 'Cinzel, serif', zIndex: 2, textAlign: 'center' }}>
        KING GENOR
      </motion.h1>

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.8, delay: 0.4 }} style={{ zIndex: 2, fontSize: '1.3rem', color: 'rgba(255,215,0,0.6)', marginBottom: '40px', fontFamily: 'Playfair Display, serif' }}>
        <span className="typing-text">{text}</span>
      </motion.div>

      <motion.button
        onClick={() => document.getElementById('empire')?.scrollIntoView({ behavior: 'smooth' })}
        className="scepter-btn"
        style={{ zIndex: 2 }}
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.6, delay: 0.6 }}
      >
        Explore My Realm
      </motion.button>

      <motion.div initial={{ y: 6, opacity: 0.8 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: 0.6, delay: 0.8 }} style={{ position: 'absolute', bottom: '40px', zIndex: 2, fontSize: '2rem', color: 'rgba(255,215,0,0.4)' }}>
        ↓
      </motion.div>
    </section>
  );
}

/* ─── Empire Stats ─── */
function Empire() {
  const stats = [
    { num: 47, suffix: '+', label: 'Kingdoms Conquered' },
    { num: 999, suffix: 'M+', label: 'Subjects Admire' },
    { num: 365, suffix: '/7', label: 'Days of Awesome' },
    { num: 1, suffix: '', label: 'King Everlasting' },
  ];

  return (
    <section id="empire" className="section" style={{ paddingTop: '120px' }}>
      <Reveal>
        <h2 className="gold-text text-4xl md:text-5xl font-bold mb-16" style={{ fontFamily: 'Cinzel, serif', textAlign: 'center' }}>
          THE EMPIRE
        </h2>
      </Reveal>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
        {stats.map((s, i) => (
          <Reveal key={s.label} delay={i * 150}>
            <div className="text-center" style={{ padding: '30px 0' }}>
              <div className="stat-number gold-text"><Counter target={s.num} suffix={s.suffix} /></div>
              <div className="stat-label mt-4">{s.label}</div>
            </div>
          </Reveal>
        ))}
      </div>
    </section>
  );
}

/* ─── Achievements ─── */
function Achievements() {
  const items = [
    { icon: '🏰', title: 'Built the Golden Palace', desc: 'A castle so magnificent, the sun gets jealous of its shine.' },
    { icon: '⚔️', title: 'Defeated the Dragon of Bugs', desc: 'With a single pull request, the bug was vanquished forever.' },
    { icon: '🌍', title: 'Conquered Three Continents', desc: 'Via WiFi. The most efficient conquest in history.' },
    { icon: '🧠', title: 'Master of All Technologies', desc: 'From CSS to quantum computing — nothing escapes His Majesty.' },
    { icon: '👑', title: 'Invented the Crown', desc: 'Or at least improved it by 400%. Hard to verify.' },
    { icon: '🔥', title: 'Never Missed a Deadline', desc: 'Kings don\'t miss deadlines. Deadlines miss kings.' },
  ];

  return (
    <section id="achievements" className="section">
      <Reveal>
        <h2 className="gold-text text-4xl md:text-5xl font-bold mb-16" style={{ fontFamily: 'Cinzel, serif', textAlign: 'center' }}>
          ROYAL ACHIEVEMENTS
        </h2>
      </Reveal>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
        {items.map((item, i) => (
          <Reveal key={item.title} delay={i * 100}>
            <div className="achievement-card">
              <div style={{ fontSize: '3rem', marginBottom: '16px' }}>{item.icon}</div>
              <h3 className="gold-text text-xl font-bold mb-3" style={{ fontFamily: 'Cinzel, serif' }}>{item.title}</h3>
              <p style={{ color: 'rgba(255,215,0,0.5)', lineHeight: '1.6' }}>{item.desc}</p>
            </div>
          </Reveal>
        ))}
      </div>
    </section>
  );
}

/* ─── Golden Orb Divider ─── */
function GoldenOrb() {
  return (
    <div className="section" style={{ display: 'flex', justifyContent: 'center', padding: '60px 0' }}>
      <Reveal>
        <div className="golden-orb" />
      </Reveal>
    </div>
  );
}

/* ─── Legacy Timeline ─── */
function Legacy() {
  const events = [
    { year: 'Year 1', title: 'The Crown is Forged', desc: 'A king is born. The world trembles with anticipation.' },
    { year: 'Year 5', title: 'First Kingdom Falls', desc: 'Not to war — to sheer awesomeness. Diplomacy via charisma.' },
    { year: 'Year 10', title: 'The Great Codebase Unification', desc: 'All repos bow to one throne. Chaos becomes order.' },
    { year: 'Year 15', title: 'Legendary Status Achieved', desc: 'Even the compilers sing hymns in His Majesty\'s honor.' },
  ];

  return (
    <section id="legacy" className="section">
      <Reveal>
        <h2 className="gold-text text-4xl md:text-5xl font-bold mb-16" style={{ fontFamily: 'Cinzel, serif', textAlign: 'center' }}>
          THE LEGACY
        </h2>
      </Reveal>

      <div style={{ position: 'relative', paddingLeft: '40px' }}>
        <div style={{ position: 'absolute', left: '15px', top: 0, bottom: 0, width: '2px', background: 'linear-gradient(to bottom, transparent, #ffd700, transparent)' }} />
        {events.map((ev, i) => (
          <Reveal key={ev.year} delay={i * 200}>
            <div style={{ position: 'relative', marginBottom: '60px', paddingLeft: '30px' }}>
              <div style={{ position: 'absolute', left: '-33px', top: '5px', width: '16px', height: '16px', borderRadius: '50%', background: '#ffd700', boxShadow: '0 0 20px rgba(255,215,0,0.5)', border: '3px solid #05050a' }} />
              <div className="gold-text text-sm font-bold mb-2" style={{ fontFamily: 'Cinzel, serif' }}>{ev.year}</div>
              <h3 className="text-2xl font-bold mb-2" style={{ fontFamily: 'Cinzel, serif', color: '#ffd700' }}>{ev.title}</h3>
              <p style={{ color: 'rgba(255,215,0,0.5)', lineHeight: '1.6' }}>{ev.desc}</p>
            </div>
          </Reveal>
        ))}
      </div>
    </section>
  );
}

/* ─── Contact / Footer ─── */
function Footer() {
  return (
    <footer id="contact" className="footer">
      <Reveal>
        <div style={{ fontSize: '4rem', marginBottom: '20px' }}>👑</div>
        <h2 className="gold-text text-3xl font-bold mb-6" style={{ fontFamily: 'Cinzel, serif' }}>
          PROSTRATE BEFORE THE KING
        </h2>
        <p style={{ color: 'rgba(255,215,0,0.4)', maxWidth: '500px', margin: '0 auto 30px', lineHeight: '1.6' }}>
          All roads lead to the throne. All messages are received with benevolent grace.
          Kneel appropriately.
        </p>
        <div className="section-divider mb-8" />
        <p style={{ fontSize: '0.8rem', letterSpacing: '3px' }}>
          © {new Date().getFullYear()} KING GENOR — ALL WORLDS RESERVED
        </p>
      </Reveal>
    </footer>
  );
}

/* ─── Main Page ─── */
export default function Page() {
  return (
    <>
      <ParticleCanvas />
      <SparkleCursor />
      <Navbar />
      <Hero />
      <div className="section-divider" />
      <Empire />
      <div className="section-divider" />
      <Achievements />
      <GoldenOrb />
      <Legacy />
      <div className="section-divider" />
      <Footer />
    </>
  );
}
