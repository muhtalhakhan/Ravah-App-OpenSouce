"use client";

import { Layers, FileText, CheckCircle } from "lucide-react";
import { GlowingEffect } from "@/components/ui/glowing-effect";
import { cn } from "@/lib/utils";

const features = [
  {
    num: "01",
    icon: <Layers className="h-[18px] w-[18px]" />,
    iconColor: "text-sky-400",
    iconBg: "bg-sky-400/10",
    title: "Context Capture",
    body: "Define audience, tone, and product angle once. Every post stems from a shared strategic foundation — never generic, always on-brand.",
    link: "/onboarding",
    linkLabel: "Set up context",
    area: "md:[grid-area:1/1/2/5]",
  },
  {
    num: "02",
    icon: <FileText className="h-[18px] w-[18px]" />,
    iconColor: "text-teal-400",
    iconBg: "bg-teal-400/10",
    title: "Content Blocks",
    body: "Hooks, body copy, and CTA stacks aligned with your founder voice. Structured weekly content — not a blank page every Monday morning.",
    link: "/agent",
    linkLabel: "Open studio",
    area: "md:[grid-area:1/5/2/9]",
    hero: true,
  },
  {
    num: "03",
    icon: <CheckCircle className="h-[18px] w-[18px]" />,
    iconColor: "text-amber-400",
    iconBg: "bg-amber-400/10",
    title: "Approval Flow",
    body: "Review and ship from one dashboard. No more version history scattered across Notion docs and platform apps. One source of truth.",
    link: "/waitlist",
    linkLabel: "Join waitlist",
    area: "md:[grid-area:1/9/2/13]",
  },
];

export function FeaturesGrid() {
  return (
    <section className="py-20 px-4" id="features">
      <header className="text-center mb-12">
        <p className="text-xs uppercase tracking-[0.2em] text-teal-400 mb-3">Core capabilities</p>
        <h2 className="text-3xl md:text-4xl font-bold text-[#EEF1F1] tracking-tight">
          Everything founders need to stay consistent
        </h2>
      </header>

      <ul className="grid grid-cols-1 gap-4 md:grid-cols-12 max-w-6xl mx-auto">
        {features.map((f) => (
          <li key={f.num} className={cn("min-h-[14rem] list-none", f.area)}>
            <div className="relative h-full rounded-[1.25rem] border border-white/[0.08] p-2">
              <GlowingEffect
                spread={40}
                glow={true}
                disabled={false}
                proximity={64}
                inactiveZone={0.01}
                borderWidth={2}
              />
              <div className={cn(
                "relative flex h-full flex-col justify-between gap-6 overflow-hidden rounded-xl border border-white/[0.06] p-6",
                f.hero
                  ? "bg-[rgba(0,194,179,0.06)]"
                  : "bg-[#131618]",
                "shadow-[0px_0px_27px_0px_rgba(0,0,0,0.4)]"
              )}>
                <div className="flex flex-col gap-4">
                  <div className="flex items-center justify-between">
                    <div className={cn("w-fit rounded-lg border border-white/[0.08] p-2", f.iconBg, f.iconColor)}>
                      {f.icon}
                    </div>
                    <span className="text-[10px] font-mono text-white/20">{f.num}</span>
                  </div>
                  <div className="space-y-2">
                    <h3 className="text-xl font-semibold tracking-tight text-[#EEF1F1]">
                      {f.title}
                    </h3>
                    <p className="text-sm leading-relaxed text-[#7E9496]">
                      {f.body}
                    </p>
                  </div>
                </div>
                <a
                  href={f.link}
                  className="text-xs text-teal-400 hover:text-teal-300 transition-colors flex items-center gap-1"
                >
                  {f.linkLabel} <span aria-hidden="true">→</span>
                </a>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
