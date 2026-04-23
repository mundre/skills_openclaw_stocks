"use client";

import { useState } from "react";

export default function ContactPage() {
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    setTimeout(() => setSubmitted(false), 3000);
  };

  return (
    <section id="contact" className="py-20 bg-fancy">
      <div className="container mx-auto px-4 max-w-2xl">
        <h1 className="text-4xl md:text-5xl font-bold text-center gradient-text mb-2">
          Contact
        </h1>
        <p className="text-center text-muted/80 mb-10">
          Have a question or collaboration idea? Reach out — I respond quickly.
        </p>
        <div className="card max-w-md mx-auto">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium mb-2">Name</label>
              <input id="name" name="name" type="text" required className="w-full px-3 py-2 border border-white/10 rounded bg-black/20 text-white placeholder-muted focus:outline-none focus:ring-2 focus:ring-accent" placeholder="Your name" />
            </div>
            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-2">Email</label>
              <input id="email" name="email" type="email" required className="w-full px-3 py-2 border border-white/10 rounded bg-black/20 text-white placeholder-muted focus:outline-none focus:ring-2 focus:ring-accent" placeholder="you@example.com" />
            </div>
            <div>
              <label htmlFor="message" className="block text-sm font-medium mb-2">Message</label>
              <textarea id="message" name="message" rows={4} required className="w-full px-3 py-2 border border-white/10 rounded bg-black/20 text-white placeholder-muted focus:outline-none focus:ring-2 focus:ring-accent" placeholder="Your message…" />
            </div>
            <button type="submit" className="bg-primary hover:bg-primary/80 text-white px-6 py-2 rounded font-semibold w-full transition transform hover:scale-105">
              {submitted ? "Sending…" : "Send Message"}
            </button>
            {submitted && <p className="text-accent text-sm text-center">Message sent! I’ll reply soon.</p>}
          </form>
        </div>
      </div>
    </section>
  );
}