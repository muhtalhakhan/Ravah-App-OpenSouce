"use client";

import { GlowingEffect } from "@/components/ui/glowing-effect";

const weekRows = [
  { day: "Mon", dayColor: "text-sky-400",   task: "Positioning thread",   tag: "Thread", tagColor: "bg-sky-400/10 text-sky-400",   badge: "Done",   badgeColor: "bg-teal-400/10 text-teal-400" },
  { day: "Wed", dayColor: "text-teal-400",  task: "Founder lesson post",  tag: "Post",   tagColor: "bg-teal-400/10 text-teal-400", badge: "Review", badgeColor: "bg-amber-400/10 text-amber-400" },
  { day: "Fri", dayColor: "text-amber-400", task: "Product update launch", tag: "Launch", tagColor: "bg-amber-400/10 text-amber-400",badge: "Draft",  badgeColor: "bg-white/5 text-white/40" },
  { day: "Sun", dayColor: "text-purple-400",task: "Community recap",       tag: "Recap",  tagColor: "bg-purple-400/10 text-purple-400", badge: "Draft", badgeColor: "bg-white/5 text-white/40" },
];

export function ScheduleSection() {
  return (
    <section className="py-20 px-4" id="schedule">
      <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-12 items-center">

        {/* Left copy */}
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-teal-400 mb-3">Weekly system</p>
          <h2 className="text-3xl md:text-4xl font-bold text-[#EEF1F1] tracking-tight mb-4">
            Execution track with<br />measurable momentum
          </h2>
          <p className="text-[#7E9496] text-sm leading-relaxed mb-8">
            Stop reacting to blank calendars. Ravah maps your narrative arcs to a weekly cadence so you never miss a publish window again.
          </p>
          <a
            href="/agent"
            className="inline-flex items-center gap-1 rounded-full bg-teal-500 px-5 py-2.5 text-sm font-semibold text-white hover:bg-teal-400 transition-colors"
          >
            View full schedule
          </a>
        </div>

        {/* Right — glowing week card */}
        <div className="relative rounded-[1.25rem] border border-white/[0.08] p-2">
          <GlowingEffect
            spread={50}
            glow={true}
            disabled={false}
            proximity={80}
            inactiveZone={0.01}
            borderWidth={2}
          />
          <div className="relative rounded-xl border border-white/[0.06] bg-[#131618] p-6 shadow-[0px_0px_27px_0px_rgba(0,0,0,0.4)]">
            <p className="text-xs font-semibold uppercase tracking-widest text-white/30 mb-5">Week cycle</p>
            <div className="flex flex-col gap-3">
              {weekRows.map((row) => (
                <div key={row.day} className="flex items-center gap-3">
                  <span className={`w-8 text-xs font-semibold ${row.dayColor}`}>{row.day}</span>
                  <div className="flex flex-1 items-center gap-2 min-w-0">
                    <span className="truncate text-sm text-[#EEF1F1]">{row.task}</span>
                    <span className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-medium ${row.tagColor}`}>{row.tag}</span>
                  </div>
                  <span className={`shrink-0 rounded-full px-2.5 py-0.5 text-[10px] font-semibold ${row.badgeColor}`}>{row.badge}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>
    </section>
  );
}
