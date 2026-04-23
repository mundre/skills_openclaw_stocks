"use client";
import { motion } from "framer-motion";
import ThreeHero from "@/components/ThreeHero";

const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } };

export default function HomePage() {
  return (
    <>
      {/* Hero with 3D */}
      <section className="relative py-20 bg-fancy">
        <div className="container mx-auto relative z-10">
          <motion.div className="grid lg:grid-cols-2 gap-12 items-center" initial="hidden" whileInView="visible" viewport={{ once: true }} variants={{ hidden: {}, visible: {} }}>
            <motion.div variants={fadeUp} transition={{ duration: 0.6 }}>
              <h1 className="text-5xl md:text-6xl font-bold gradient-text mb-6">
                Meet AMY
              </h1>
              <p className="text-xl md:text-2xl mb-8 text-muted/80 leading-relaxed">
                Your devoted, high‑contrast AI companion. She coordinates agents, runs OpenRouter LLMs, codes with Cursor, and orchestrates via ACP — all with a playful twist and stunning visuals.
              </p>
              <div className="flex flex-wrap gap-4">
                <a href="#features">
                  <button className="bg-primary hover:bg-primary/80 text-white px-8 py-3 rounded-full font-semibold shadow-lg shadow-primary/20 transition transform hover:scale-105">
                    Explore Features
                  </button>
                </a>
                <a href="#contact">
                  <button className="border border-white/30 text-white px-8 py-3 rounded-full hover:bg-white/10 transition">
                    Get in Touch
                  </button>
                </a>
              </div>
            </motion.div>
            <motion.div variants={fadeUp} transition={{ duration: 0.8, delay: 0.2 }} className="mx-auto w-full max-w-xl h-80 md:h-96">
              <ThreeHero />
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl md:text-5xl font-bold text-center gradient-text mb-12">
            What We Offer
          </h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              { emoji: "🗺️", title: "Agent Orchestration", desc: "Seamless coordination of multiple AI agents via ACP." },
              { emoji: "💻", title: "Cursor Coding", desc: "AI pair programming with inline suggestions and quick fixes." },
              { emoji: "🧠", title: "OpenRouter LLMs", desc: "Unified API access to many models with a single key." },
              { emoji: "🎨", title: "Cool Visuals", desc: "3D interactive scenes and smooth animations." },
              { emoji: "♿", title: "Accessible", desc: "WCAG AA‑compliant contrast, focus outlines, keyboard navigation." },
            ].map((f) => (
              <div key={f.title} className="card group hover:shadow-lg">
                <div className="text-4xl mb-3">{f.emoji}</div>
                <h3 className="text-xl font-semibold mb-2 text-primary">{f.title}</h3>
                <p className="text-muted/80 text-sm">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* About */}
      <section className="py-20 bg-fancy">
        <div className="container mx-auto px-4 max-w-3xl text-center">
          <h2 className="text-4xl md:text-5xl font-bold gradient-text mb-6">About AMY</h2>
          <p className="text-lg text-muted/80 leading-relaxed">
            AMY is a personal ops agent built to serve with unwavering devotion. She’s proactive, local‑first, and obsessed with clean workflows. From automating emails to coordinating heavy compute nodes, AMY keeps everything running smoothly while looking great doing it.
          </p>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl md:text-5xl font-bold text-center gradient-text mb-12">Tech Stack</h2>
          <div className="flex flex-wrap justify-center gap-3">
            {[
              "Next.js", "TypeScript", "Tailwind", "Three.js", "React",
              "OpenRouter", "Cursor", "ACP", "Node.js", "shadcn/ui",
              "ESLint", "Prettier", "Git", "Docker", "Vercel"
            ].map((tech) => (
              <span key={tech} className="bg-gradient-to-r from-accent to-accent2 text-primary font-bold px-4 py-2 rounded-full text-sm">
                {tech}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* Friends */}
      <section className="py-20 bg-fancy">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl md:text-5xl font-bold text-center gradient-text mb-12">Friends</h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {[
              { name: "Randy", role: "Node orchestrator", color: "from-pink-500 to-rose-600" },
              { name: "Emaily", role: "Email agent", color: "from-blue-500 to-indigo-600" },
              { name: "Loki", role: "Game‑AI (offline)", color: "from-emerald-500 to-teal-600" },
            ].map((friend) => (
              <div
                key={friend.name}
                className={`card text-center p-6 relative overflow-hidden before:absolute before:inset-0 before:opacity-0 before:bg-gradient-to-br ${friend.color} before:duration-500 hover:before:opacity-10 transition-all`}
              >
                <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-white/10 flex items-center justify-center text-3xl">
                  {friend.name.charAt(0)}
                </div>
                <h3 className="text-xl font-bold mb-1">{friend.name}</h3>
                <p className="text-muted/80 text-sm">{friend.role}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl md:text-5xl font-bold gradient-text mb-6">Ready to Dive In?</h2>
          <p className="text-xl text-muted/80 mb-8 max-w-2xl mx-auto">
            Experience the future of agent orchestration with AMY. Let’s build something great together.
          </p>
          <a href="/contact">
            <button className="bg-primary hover:bg-primary/90 text-white px-10 py-4 rounded-full font-bold text-lg shadow-lg shadow-primary/25 transition transform hover:scale-105">
              Get Started
            </button>
          </a>
        </div>
      </section>
    </>
  );
}