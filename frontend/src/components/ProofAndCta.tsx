"use client";

import { GlowingEffect } from "@/components/ui/glowing-effect";
import { LiquidButton } from "@/components/ui/liquid-glass-button";

const stats = [
  { value: "70", unit: "min", label: "avg. weekly planning time" },
  { value: "4",  unit: "×",   label: "more consistent posting" },
  { value: "100",unit: "%",   label: "founder voice preserved" },
];

const mosaicTiles = [
  { title: "Hero",     sub: "Positioning clarity",  color: "from-sky-500/10"    },
  { title: "Features", sub: "Capability proof",      color: "from-teal-500/10"   },
  { title: "Schedule", sub: "Workflow structure",    color: "from-amber-500/10"  },
  { title: "Proof",    sub: "Trust + conversion",    color: "from-purple-500/10" },
];

export function ProofAndCta() {
  return (
    <>
      {/* ── Social proof ── */}
      <section className="py-20 px-4" id="proof">
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-12 items-start">

          {/* Stats */}
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-teal-400 mb-3">Built for consistency</p>
            <h2 className="text-3xl md:text-4xl font-bold text-[#EEF1F1] tracking-tight mb-4">
              Not content panic
            </h2>
            <p className="text-[#7E9496] text-sm leading-relaxed mb-8">
              Teams using Ravah replace last-minute posting with structured weekly cycles — plan, generate, adapt, publish.
            </p>
            <a href="/agent" className="text-amber-400 text-sm hover:text-amber-300 transition-colors">
              Open content studio →
            </a>
            <div className="mt-8 flex items-center gap-6">
              {stats.map((s, i) => (
                <div key={s.label}>
                  {i > 0 && <div className="hidden" />}
                  <strong className="block text-3xl font-black text-[#EEF1F1]">
                    {s.value}<span className="text-lg text-teal-400">{s.unit}</span>
                  </strong>
                  <span className="text-xs text-[#7E9496]">{s.label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Glowing quote card */}
          <div className="relative rounded-[1.25rem] border border-white/[0.08] p-2">
            <GlowingEffect
              spread={40}
              glow={true}
              disabled={false}
              proximity={64}
              inactiveZone={0.01}
              borderWidth={2}
            />
            <div className="relative rounded-xl border border-white/[0.06] bg-[#131618] p-8 shadow-[0px_0px_27px_0px_rgba(0,0,0,0.4)]">
              <div className="text-5xl text-teal-400/30 font-serif leading-none mb-4">&ldquo;</div>
              <p className="text-[#EEF1F1] text-base leading-relaxed mb-6">
                Ravah cut our content planning from 6 hours to 70 minutes and gave us a repeatable founder voice every single week.
              </p>
              <div className="flex items-center gap-3">
                <div className="h-9 w-9 rounded-full bg-teal-500/20 flex items-center justify-center text-xs font-bold text-teal-400">EP</div>
                <div>
                  <strong className="block text-sm text-[#EEF1F1]">Early Design Partner</strong>
                  <span className="text-xs text-[#7E9496]">SaaS Founder, Series A</span>
                </div>
              </div>
              <div className="mt-4 text-amber-400 text-sm" aria-label="5 stars">★★★★★</div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Final CTA ── */}
      <section className="py-20 px-4" id="cta">
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-12 items-center">

          {/* Copy */}
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-teal-400 mb-3">One narrative engine</p>
            <h2 className="text-3xl md:text-4xl font-bold text-[#EEF1F1] tracking-tight mb-4">
              From founder idea to<br />
              <em className="not-italic text-teal-400">platform-ready content</em> — in minutes
            </h2>
            <p className="text-[#7E9496] text-sm leading-relaxed mb-8">
              Join founders building consistent, high-quality content systems.
            </p>
            <div className="flex flex-wrap items-center gap-3">
              <LiquidButton
                className="text-white border border-white/20 rounded-full"
                size="xl"
                onClick={() => { window.location.href = "/waitlist" }}
              >
                Request early access
              </LiquidButton>
              <a href="/login" className="text-sm text-white/50 hover:text-white/80 transition-colors">
                Already invited? Sign in
              </a>
            </div>
          </div>

          {/* Glowing mosaic */}
          <ul className="grid grid-cols-2 gap-3">
            {mosaicTiles.map((tile) => (
              <li key={tile.title} className="list-none">
                <div className="relative rounded-[1.25rem] border border-white/[0.08] p-2 h-full">
                  <GlowingEffect
                    spread={30}
                    glow={true}
                    disabled={false}
                    proximity={48}
                    inactiveZone={0.01}
                    borderWidth={2}
                  />
                  <div className={`relative rounded-xl border border-white/[0.06] bg-gradient-to-br ${tile.color} to-transparent bg-[#131618] p-5 h-full shadow-[0px_0px_20px_0px_rgba(0,0,0,0.4)]`}>
                    <strong className="block text-sm font-semibold text-[#EEF1F1] mb-1">{tile.title}</strong>
                    <span className="text-xs text-[#7E9496]">{tile.sub}</span>
                  </div>
                </div>
              </li>
            ))}
          </ul>

        </div>
      </section>
    </>
  );
}
