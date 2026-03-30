"use client"

import { WebGLShader } from "@/components/ui/web-gl-shader"
import { LiquidButton } from "@/components/ui/liquid-glass-button"

export function RavahHero() {
  return (
    <section className="relative min-h-screen w-full overflow-hidden" id="hero-section">
      {/* WebGL full-screen background */}
      <WebGLShader />

      {/* Navbar overlay */}
      <header className="relative z-20 flex items-center justify-between px-6 py-5 md:px-10">
        <a href="/" className="flex items-center gap-2 text-white font-semibold text-lg tracking-tight">
          <span className="flex gap-[3px]" aria-hidden="true">
            <i className="block h-2 w-2 rounded-full bg-sky-400" />
            <i className="block h-2 w-2 rounded-full bg-white/60" />
            <i className="block h-2 w-2 rounded-full bg-white/60" />
            <i className="block h-2 w-2 rounded-full bg-white/60" />
          </span>
          RavahFlow
        </a>
        <nav className="hidden md:flex items-center gap-6 text-sm text-white/70">
          <a href="/onboarding" className="hover:text-white transition-colors">Features</a>
          <a href="/agent" className="hover:text-white transition-colors">Solutions</a>
          <a href="/waitlist" className="hover:text-white transition-colors">Resources</a>
          <a href="/signup" className="hover:text-white transition-colors">Pricing</a>
        </nav>
        <div className="flex items-center gap-3">
          <a href="/login" className="text-sm text-white/70 hover:text-white transition-colors">Sign in</a>
          <a
            href="/waitlist"
            className="rounded-full border border-white/30 bg-white/10 px-4 py-1.5 text-sm text-white backdrop-blur-sm hover:bg-white/20 transition-colors"
          >
            Get demo
          </a>
        </div>
      </header>

      {/* Hero content */}
      <div className="relative z-10 flex min-h-[calc(100vh-80px)] flex-col items-center justify-center px-4 text-center">
        <div className="relative border border-[#27272a] p-2 w-full mx-auto max-w-3xl">
          <div className="relative border border-[#27272a] py-14 px-6 overflow-hidden">

            <p className="mb-4 text-xs uppercase tracking-[0.2em] text-white/50">
              Founder Narrative Engine
            </p>

            <h1 className="mb-4 text-white text-5xl font-extrabold tracking-tighter md:text-[clamp(2.5rem,7vw,6rem)] leading-none">
              Craft, plan,<br />
              <span className="text-white/40">and scale</span>
            </h1>

            <p className="text-white/60 px-6 mx-auto max-w-lg text-sm md:text-base">
              Turn founder strategy into platform-ready posts with one
              AI-powered narrative engine built for weekly consistency.
            </p>

            {/* Available indicator */}
            <div className="my-8 flex items-center justify-center gap-1.5">
              <span className="relative flex h-3 w-3 items-center justify-center">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-500 opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-green-500" />
              </span>
              <p className="text-xs text-green-500">Open for early access</p>
            </div>

            {/* CTAs */}
            <div className="flex items-center justify-center gap-3 flex-wrap">
              <LiquidButton
                className="text-white border border-white/20 rounded-full"
                size="xl"
                onClick={() => { window.location.href = "/waitlist" }}
              >
                Get free demo
              </LiquidButton>
              <a
                href="/agent"
                className="flex items-center gap-1 rounded-full px-6 py-3 text-sm text-white/60 hover:text-white transition-colors"
              >
                Open studio <span aria-hidden="true">→</span>
              </a>
            </div>

          </div>
        </div>
      </div>
    </section>
  )
}
