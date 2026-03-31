'use client'

import { useState, useEffect, useCallback } from 'react'
import type { GeneratedPost, Platform, ContentType, Style } from '@/lib/types'
import { renderMarkdown } from '@/lib/prompts'

// ── Palette ───────────────────────────────────────────────────────────────────

const P = {
  petalFrost: '#ffd6ff',
  mauve:      '#e7c6ff',
  mauve2:     '#c8b6ff',
  peri:       '#b8c0ff',
  peri2:      '#bbd0ff',
  bg:         '#09080f',
  card:       '#0f0d1a',
  surface:    '#130f20',
  active:     '#1a1535',
  borderDim:  '#1e1a30',
  borderMid:  '#2a2450',
} as const

// ── Constants ─────────────────────────────────────────────────────────────────

const PLATFORM_META: Record<Platform, { label: string; symbol: string; accent: string }> = {
  x:         { label: 'X (Twitter)', symbol: '𝕏',  accent: P.peri2 },
  instagram: { label: 'Instagram',   symbol: '✦',  accent: P.petalFrost },
  linkedin:  { label: 'LinkedIn',    symbol: 'in', accent: P.mauve2 },
}

const TONE_PRESETS = [
  'Casual & friendly',
  'Professional & authoritative',
  'Conversational',
  'Bold & direct',
  'Witty & playful',
]

// ── Types ─────────────────────────────────────────────────────────────────────

interface FormState {
  name:        string
  contentType: ContentType
  summary:     string
  numDays:     7 | 18 | 30
  platforms:   Platform[]
  style:       Style
  tone:        string
  customTone:  string
  audience:    string
  keywords:    string
  avoid:       string
}

const DEFAULT_FORM: FormState = {
  name:        '',
  contentType: 'personal',
  summary:     '',
  numDays:     7,
  platforms:   ['x', 'instagram', 'linkedin'],
  style:       'mixed',
  tone:        TONE_PRESETS[0],
  customTone:  '',
  audience:    '',
  keywords:    '',
  avoid:       '',
}

// ── Shared style atoms ────────────────────────────────────────────────────────

const inputCls = [
  'w-full text-sm px-3 py-2.5 rounded-lg border outline-none transition-colors',
  'bg-[#130f20] border-[#1e1a30] text-[#e7c6ff]',
  'placeholder:text-[#2a2450]',
  'focus:border-[#b8c0ff]',
].join(' ')

const labelCls = 'block text-[11px] font-semibold text-[#b8c0ff] uppercase tracking-widest mb-2'

// ── Sub-components ────────────────────────────────────────────────────────────

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false)
  return (
    <button
      onClick={async () => {
        await navigator.clipboard.writeText(text)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      }}
      style={{
        borderColor: copied ? P.mauve2 : P.borderMid,
        color:       copied ? P.mauve2 : P.peri,
      }}
      className="text-xs px-3 py-1 rounded-md border transition-colors hover:border-[#c8b6ff] hover:text-[#c8b6ff]"
    >
      {copied ? 'Copied!' : 'Copy'}
    </button>
  )
}

function ClearVSection({ clearv }: { clearv: GeneratedPost['clearv'] }) {
  const [open, setOpen] = useState(false)
  const rows: [string, string, string][] = [
    ['C', 'Capture',  clearv.capture],
    ['L', 'Lead',     clearv.lead],
    ['E', 'Educate',  clearv.educate],
    ['A', 'Activate', clearv.activate],
    ['R', 'Resonate', clearv.resonate],
    ['V', 'Visual',   clearv.visual],
  ]
  return (
    <div className="mt-3">
      <button
        onClick={() => setOpen((o) => !o)}
        style={{ color: P.borderMid }}
        className="text-xs flex items-center gap-1 transition-colors hover:text-[#b8c0ff]"
      >
        <span className={`transition-transform duration-150 ${open ? 'rotate-90' : ''}`}>▶</span>
        ClearV breakdown
      </button>
      {open && (
        <div className="mt-2 space-y-1.5 pl-3 border-l" style={{ borderColor: P.borderDim }}>
          {rows.map(([letter, label, value]) => (
            <p key={letter} className="text-xs leading-relaxed" style={{ color: P.peri }}>
              <span className="font-bold mr-1.5" style={{ color: P.mauve2 }}>{letter}</span>
              <span className="mr-1" style={{ color: P.borderMid }}>{label}:</span>
              {value}
            </p>
          ))}
        </div>
      )}
    </div>
  )
}

function PostCard({ post }: { post: GeneratedPost }) {
  const meta = PLATFORM_META[post.platform]
  return (
    <div
      className="flex flex-col rounded-xl p-4 transition-colors"
      style={{ background: P.card, border: `1px solid ${P.borderDim}` }}
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-semibold flex items-center gap-1.5" style={{ color: meta.accent }}>
          <span className="text-sm leading-none">{meta.symbol}</span>
          {meta.label}
        </span>
        <CopyButton text={post.full_post} />
      </div>

      <p className="text-sm whitespace-pre-wrap leading-relaxed flex-1" style={{ color: P.mauve }}>
        {post.full_post}
      </p>

      <div className="mt-3 pt-3 flex flex-wrap gap-1.5 items-center" style={{ borderTop: `1px solid ${P.borderDim}` }}>
        <span className="text-xs" style={{ color: P.borderMid }}>{post.char_count} chars</span>
        {post.hashtags.slice(0, 5).map((h) => (
          <span key={h} className="text-xs" style={{ color: P.borderMid }}>
            {h.startsWith('#') ? h : `#${h}`}
          </span>
        ))}
        {post.hashtags.length > 5 && (
          <span className="text-xs" style={{ color: P.borderDim }}>+{post.hashtags.length - 5}</span>
        )}
      </div>
      <ClearVSection clearv={post.clearv} />
    </div>
  )
}

// ── Pill toggle button ────────────────────────────────────────────────────────

function ToggleBtn({
  active, onClick, children, accent,
}: {
  active: boolean
  onClick: () => void
  children: React.ReactNode
  accent?: string
}) {
  return (
    <button
      onClick={onClick}
      className="text-sm px-4 py-2 rounded-lg border transition-colors"
      style={active
        ? { borderColor: accent ?? P.mauve2, background: P.active, color: accent ?? P.mauve }
        : { borderColor: P.borderDim, color: P.peri, background: 'transparent' }
      }
    >
      {children}
    </button>
  )
}

function SmallToggleBtn({
  active, onClick, children,
}: {
  active: boolean
  onClick: () => void
  children: React.ReactNode
}) {
  return (
    <button
      onClick={onClick}
      className="text-xs px-3 py-1.5 rounded-lg border transition-colors"
      style={active
        ? { borderColor: P.mauve2, background: P.active, color: P.mauve }
        : { borderColor: P.borderDim, color: P.peri, background: 'transparent' }
      }
    >
      {children}
    </button>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function Home() {
  const [apiKey, setApiKey]               = useState('')
  const [apiKeyInput, setApiKeyInput]     = useState('')
  const [showKeyForm, setShowKeyForm]     = useState(false)
  const [form, setForm]                   = useState<FormState>(DEFAULT_FORM)
  const [loading, setLoading]             = useState(false)
  const [error, setError]                 = useState('')
  const [posts, setPosts]                 = useState<GeneratedPost[]>([])
  const [isReturning, setIsReturning]     = useState(false)
  const [lastGeneratedAt, setLastGeneratedAt] = useState('')

  // Load all persisted state from localStorage on mount
  useEffect(() => {
    const savedKey = localStorage.getItem('ravah_api_key')
    if (savedKey) {
      setApiKey(savedKey)
      setApiKeyInput(savedKey)
    } else {
      setShowKeyForm(true)
    }

    try {
      const profile    = JSON.parse(localStorage.getItem('ravah_profile') ?? 'null') as Record<string, unknown> | null
      const session    = JSON.parse(localStorage.getItem('ravah_session') ?? 'null') as Record<string, unknown> | null
      const savedPosts = JSON.parse(localStorage.getItem('ravah_posts')   ?? 'null') as GeneratedPost[] | null

      if (profile || session) {
        setIsReturning(true)
        setForm((f) => ({
          ...f,
          ...(profile ? {
            name:        (profile.name        as string)      ?? f.name,
            contentType: (profile.contentType as ContentType) ?? f.contentType,
          } : {}),
          ...(session ? {
            summary:    (session.summary    as string)       ?? f.summary,
            numDays:    (session.numDays    as 7 | 18 | 30)  ?? f.numDays,
            platforms:  (session.platforms  as Platform[])   ?? f.platforms,
            style:      (session.style      as Style)        ?? f.style,
            tone:       (session.tone       as string)       ?? f.tone,
            customTone: (session.customTone as string)       ?? f.customTone,
            audience:   (session.audience   as string)       ?? f.audience,
            keywords:   (session.keywords   as string)       ?? f.keywords,
            avoid:      (session.avoid      as string)       ?? f.avoid,
          } : {}),
        }))
        if (session?.generatedAt) setLastGeneratedAt(session.generatedAt as string)
      }

      if (savedPosts?.length) setPosts(savedPosts)
    } catch { /* ignore malformed data */ }
  }, [])

  const saveApiKey = () => {
    const k = apiKeyInput.trim()
    if (!k) return
    localStorage.setItem('ravah_api_key', k)
    setApiKey(k)
    setShowKeyForm(false)
  }

  const clearApiKey = () => {
    localStorage.removeItem('ravah_api_key')
    setApiKey('')
    setApiKeyInput('')
    setShowKeyForm(true)
  }

  const clearMemory = () => {
    localStorage.removeItem('ravah_profile')
    localStorage.removeItem('ravah_session')
    localStorage.removeItem('ravah_posts')
    setIsReturning(false)
    setLastGeneratedAt('')
    setPosts([])
    setForm(DEFAULT_FORM)
  }

  const togglePlatform = (p: Platform) =>
    setForm((f) => ({
      ...f,
      platforms: f.platforms.includes(p)
        ? f.platforms.filter((x) => x !== p)
        : [...f.platforms, p],
    }))

  const effectiveTone = form.tone === 'Custom' ? form.customTone : form.tone
  const totalPosts    = form.numDays * form.platforms.length

  const generate = useCallback(async () => {
    if (!apiKey)                              { setError('Please save your Google API key first.'); return }
    if (!form.name.trim())                    { setError('Please enter your name.'); return }
    if (form.summary.trim().length < 15)      { setError('Please describe what you\'re building in more detail.'); return }
    if (!form.platforms.length)               { setError('Select at least one platform.'); return }
    if (form.tone === 'Custom' && !form.customTone.trim()) { setError('Please describe your custom tone.'); return }

    setError('')
    setLoading(true)
    setPosts([])

    try {
      const res  = await fetch('/api/generate', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({
          apiKey,
          name:        form.name.trim(),
          contentType: form.contentType,
          summary:     form.summary.trim(),
          numDays:     form.numDays,
          platforms:   form.platforms,
          style:       form.style,
          tone:        effectiveTone,
          audience:    form.audience.trim() || 'early adopters and founders',
          keywords:    form.keywords.trim(),
          avoid:       form.avoid.trim(),
        }),
      })
      const json = await res.json()

      if (!res.ok) { setError(json.error ?? 'Something went wrong.'); return }

      setPosts(json.posts)

      const generatedAt = new Date().toISOString()
      localStorage.setItem('ravah_profile', JSON.stringify({ name: form.name.trim(), contentType: form.contentType }))
      localStorage.setItem('ravah_session', JSON.stringify({
        summary: form.summary.trim(), numDays: form.numDays, platforms: form.platforms,
        style: form.style, tone: form.tone, customTone: form.customTone,
        audience: form.audience.trim(), keywords: form.keywords.trim(), avoid: form.avoid.trim(),
        generatedAt,
      }))
      try { localStorage.setItem('ravah_posts', JSON.stringify(json.posts)) } catch { /* quota */ }
      setLastGeneratedAt(generatedAt)
      setIsReturning(true)

      setTimeout(() => document.getElementById('results')?.scrollIntoView({ behavior: 'smooth' }), 100)
    } catch {
      setError('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [apiKey, form, effectiveTone])

  const exportMarkdown = () => {
    const md   = renderMarkdown(posts, { apiKey, name: form.name, contentType: form.contentType, summary: form.summary, numDays: form.numDays, platforms: form.platforms, style: form.style, tone: effectiveTone, audience: form.audience || 'early adopters and founders', keywords: form.keywords, avoid: form.avoid })
    const blob = new Blob([md], { type: 'text/markdown' })
    const a    = document.createElement('a')
    a.href     = URL.createObjectURL(blob)
    a.download = `ravah_${form.numDays}d_${Date.now()}.md`
    a.click()
  }

  // Group posts by day
  const days: Record<number, GeneratedPost[]> = {}
  for (const p of posts) { if (!days[p.day]) days[p.day] = []; days[p.day].push(p) }

  return (
    <main className="min-h-screen px-5 py-12 max-w-3xl mx-auto">

      {/* ── Header ── */}
      <header className="mb-12">
        <h1 className="text-4xl font-bold tracking-tight" style={{ color: P.petalFrost }}>Ravah</h1>
        <p className="mt-2 text-sm" style={{ color: P.peri }}>
          Turn what you ship into a full content calendar — powered by your Google AI key.
        </p>
      </header>

      {/* ── API Key ── */}
      <section
        className="mb-8 p-4 rounded-xl border"
        style={{ background: P.card, borderColor: P.borderDim }}
      >
        <div className="flex items-center justify-between mb-2">
          <p className={labelCls} style={{ marginBottom: 0 }}>Google AI API Key</p>
          {apiKey && !showKeyForm && (
            <button
              onClick={() => setShowKeyForm(true)}
              className="text-xs transition-colors"
              style={{ color: P.borderMid }}
            >
              Change
            </button>
          )}
        </div>

        {!showKeyForm && apiKey ? (
          <div className="flex items-center gap-3 mt-2">
            <span className="text-sm" style={{ color: P.mauve2 }}>✓ Key saved in browser</span>
            <button onClick={clearApiKey} className="text-xs transition-colors hover:text-[#ffd6ff]" style={{ color: P.borderMid }}>
              Clear
            </button>
          </div>
        ) : (
          <div className="space-y-2 mt-2">
            <div className="flex gap-2">
              <input
                type="password"
                value={apiKeyInput}
                onChange={(e) => setApiKeyInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && saveApiKey()}
                placeholder="AIza…"
                className={inputCls}
              />
              <button
                onClick={saveApiKey}
                className="px-4 py-2.5 rounded-lg text-sm font-semibold transition-colors shrink-0"
                style={{ background: P.mauve2, color: P.bg }}
                onMouseEnter={(e) => (e.currentTarget.style.background = P.mauve)}
                onMouseLeave={(e) => (e.currentTarget.style.background = P.mauve2)}
              >
                Save
              </button>
            </div>
            <p className="text-xs" style={{ color: P.borderMid }}>
              Get a free key at{' '}
              <a
                href="https://aistudio.google.com/app/apikey"
                target="_blank"
                rel="noopener noreferrer"
                className="underline transition-colors"
                style={{ color: P.peri }}
                onMouseEnter={(e) => (e.currentTarget.style.color = P.mauve)}
                onMouseLeave={(e) => (e.currentTarget.style.color = P.peri)}
              >
                aistudio.google.com
              </a>
              . Stored only in your browser — never sent to our servers.
            </p>
          </div>
        )}
      </section>

      {/* ── Welcome back ── */}
      {isReturning && (
        <div
          className="mb-8 px-4 py-3 rounded-xl border flex items-center justify-between"
          style={{ background: P.active, borderColor: P.borderMid }}
        >
          <div>
            <p className="text-sm font-medium" style={{ color: P.mauve }}>
              Welcome back{form.name ? `, ${form.name}` : ''}
              {lastGeneratedAt && (
                <span className="ml-2 text-xs font-normal" style={{ color: P.borderMid }}>
                  · Last run {new Date(lastGeneratedAt).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                </span>
              )}
            </p>
            <p className="text-xs mt-0.5" style={{ color: P.borderMid }}>Your previous inputs and results have been restored.</p>
          </div>
          <button
            onClick={clearMemory}
            className="text-xs ml-4 shrink-0 transition-colors"
            style={{ color: P.borderMid }}
            onMouseEnter={(e) => (e.currentTarget.style.color = P.petalFrost)}
            onMouseLeave={(e) => (e.currentTarget.style.color = P.borderMid)}
          >
            Start fresh
          </button>
        </div>
      )}

      {/* ── Form ── */}
      <section className="space-y-7">

        {/* Name */}
        <div>
          <label className={labelCls}>Your name</label>
          <input
            type="text"
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            placeholder="e.g. Alex"
            className={inputCls}
          />
        </div>

        {/* Content type */}
        <div>
          <label className={labelCls}>Creating content for</label>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
            {([
              ['personal',           'Myself — personal brand'],
              ['brand',              'A brand or product'],
              ['building_in_public', 'Building in public'],
            ] as [ContentType, string][]).map(([val, label]) => (
              <button
                key={val}
                onClick={() => setForm((f) => ({ ...f, contentType: val }))}
                className="text-left text-sm px-3 py-2.5 rounded-lg border transition-colors"
                style={form.contentType === val
                  ? { borderColor: P.mauve2, background: P.active, color: P.mauve }
                  : { borderColor: P.borderDim, color: P.peri, background: 'transparent' }
                }
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Summary */}
        <div>
          <label className={labelCls}>What are you building / shipping?</label>
          <p className="text-xs mb-2" style={{ color: P.borderMid }}>Be specific — the more detail, the better the posts.</p>
          <textarea
            value={form.summary}
            onChange={(e) => setForm((f) => ({ ...f, summary: e.target.value }))}
            rows={3}
            placeholder="e.g. I'm launching Ravah, an open-source CLI that turns founder updates into a week of social posts using Google Gemini and the ClearV framework…"
            className={`${inputCls} resize-none`}
          />
          <p className="text-xs mt-1" style={{ color: P.borderDim }}>
            {form.summary.length} chars
            {form.summary.length > 0 && form.summary.length < 15 && (
              <span style={{ color: P.petalFrost }}> — need at least 15</span>
            )}
          </p>
        </div>

        {/* Duration */}
        <div>
          <label className={labelCls}>Duration</label>
          <div className="flex gap-2">
            {([7, 18, 30] as const).map((d) => (
              <ToggleBtn key={d} active={form.numDays === d} onClick={() => setForm((f) => ({ ...f, numDays: d }))}>
                {d} days
              </ToggleBtn>
            ))}
          </div>
        </div>

        {/* Platforms */}
        <div>
          <label className={labelCls}>Platforms</label>
          <div className="flex flex-wrap gap-2">
            {(Object.entries(PLATFORM_META) as [Platform, typeof PLATFORM_META[Platform]][]).map(([p, meta]) => (
              <ToggleBtn
                key={p}
                active={form.platforms.includes(p)}
                accent={meta.accent}
                onClick={() => togglePlatform(p)}
              >
                <span className="mr-1.5">{meta.symbol}</span>{meta.label}
              </ToggleBtn>
            ))}
          </div>
        </div>

        {/* Style */}
        <div>
          <label className={labelCls}>Content style</label>
          <select
            value={form.style}
            onChange={(e) => setForm((f) => ({ ...f, style: e.target.value as Style }))}
            className={inputCls}
          >
            <option value="educational">Educational — teach something actionable</option>
            <option value="storytelling">Storytelling — narrative with a beginning, middle, and lesson</option>
            <option value="motivational">Motivational — inspire action or mindset shift</option>
            <option value="behind_the_scenes">Behind the scenes — raw, authentic, unfiltered</option>
            <option value="mixed">Mixed — rotate through styles across the days</option>
          </select>
        </div>

        {/* Tone */}
        <div>
          <label className={labelCls}>Tone</label>
          <div className="flex flex-wrap gap-2">
            {[...TONE_PRESETS, 'Custom'].map((t) => (
              <SmallToggleBtn key={t} active={form.tone === t} onClick={() => setForm((f) => ({ ...f, tone: t }))}>
                {t}
              </SmallToggleBtn>
            ))}
          </div>
          {form.tone === 'Custom' && (
            <input
              type="text"
              value={form.customTone}
              onChange={(e) => setForm((f) => ({ ...f, customTone: e.target.value }))}
              placeholder="Describe your tone (e.g. nerdy but approachable, like a senior engineer talking to a friend)"
              className={`${inputCls} mt-2`}
            />
          )}
        </div>

        {/* Audience */}
        <div>
          <label className={labelCls}>Target audience</label>
          <input
            type="text"
            value={form.audience}
            onChange={(e) => setForm((f) => ({ ...f, audience: e.target.value }))}
            placeholder="e.g. early-stage founders, indie hackers, SaaS builders"
            className={inputCls}
          />
        </div>

        {/* Optional */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={labelCls}>
              Keywords to include{' '}
              <span className="normal-case font-normal" style={{ color: P.borderMid }}>(optional)</span>
            </label>
            <input
              type="text"
              value={form.keywords}
              onChange={(e) => setForm((f) => ({ ...f, keywords: e.target.value }))}
              placeholder="e.g. #buildinpublic"
              className={inputCls}
            />
          </div>
          <div>
            <label className={labelCls}>
              Things to avoid{' '}
              <span className="normal-case font-normal" style={{ color: P.borderMid }}>(optional)</span>
            </label>
            <input
              type="text"
              value={form.avoid}
              onChange={(e) => setForm((f) => ({ ...f, avoid: e.target.value }))}
              placeholder="e.g. pricing talk"
              className={inputCls}
            />
          </div>
        </div>

        {/* Error */}
        {error && (
          <p
            className="text-sm px-4 py-3 rounded-lg border"
            style={{ color: P.petalFrost, background: '#1f0f1f', borderColor: '#3a1a3a' }}
          >
            {error}
          </p>
        )}

        {/* Generate */}
        <button
          onClick={generate}
          disabled={loading || !apiKey}
          className="w-full py-3.5 rounded-xl text-sm font-semibold transition-colors"
          style={loading || !apiKey
            ? { background: P.borderDim, color: P.borderMid, cursor: 'not-allowed' }
            : { background: P.mauve2,    color: P.bg }
          }
          onMouseEnter={(e) => { if (!loading && apiKey) e.currentTarget.style.background = P.mauve }}
          onMouseLeave={(e) => { if (!loading && apiKey) e.currentTarget.style.background = P.mauve2 }}
        >
          {loading ? `Writing ${totalPosts} posts with Gemini…` : `Generate ${totalPosts} post${totalPosts !== 1 ? 's' : ''}`}
        </button>

        {loading && (
          <p className="text-xs text-center animate-pulse" style={{ color: P.borderMid }}>
            This can take 15–45 seconds depending on how many posts you requested.
          </p>
        )}
      </section>

      {/* ── Results ── */}
      {posts.length > 0 && (
        <section id="results" className="mt-16">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-base font-semibold" style={{ color: P.mauve }}>
              {posts.length} posts · {form.numDays}-day calendar
            </h2>
            <button
              onClick={exportMarkdown}
              className="px-4 py-2 rounded-lg border text-xs transition-colors"
              style={{ borderColor: P.borderMid, color: P.peri }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = P.mauve2; e.currentTarget.style.color = P.mauve }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = P.borderMid; e.currentTarget.style.color = P.peri }}
            >
              Export Markdown
            </button>
          </div>

          <div className="space-y-12">
            {Object.keys(days).map(Number).sort((a, b) => a - b).map((day) => (
              <div key={day}>
                <div className="flex items-center gap-4 mb-5">
                  <span
                    className="text-xs font-semibold px-3 py-1 rounded-full border"
                    style={{ borderColor: P.borderMid, color: P.mauve2, background: P.active }}
                  >
                    Day {day}
                  </span>
                  <div className="flex-1 h-px" style={{ background: P.borderDim }} />
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {days[day].map((post, i) => <PostCard key={i} post={post} />)}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-12 pt-8 flex justify-center" style={{ borderTop: `1px solid ${P.borderDim}` }}>
            <button
              onClick={exportMarkdown}
              className="px-6 py-2.5 rounded-xl border text-sm transition-colors"
              style={{ borderColor: P.borderMid, color: P.peri }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = P.mauve2; e.currentTarget.style.color = P.mauve }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = P.borderMid; e.currentTarget.style.color = P.peri }}
            >
              Export all as Markdown
            </button>
          </div>
        </section>
      )}

      {/* ── Footer ── */}
      <footer className="mt-20 pt-6 text-center" style={{ borderTop: `1px solid ${P.borderDim}` }}>
        <p className="text-xs" style={{ color: P.borderMid }}>
          Ravah is open source.{' '}
          <a
            href="https://github.com/MuhammadTalhaKhan55/Ravah-App-OpenSource"
            target="_blank"
            rel="noopener noreferrer"
            className="underline transition-colors"
            style={{ color: P.borderMid }}
            onMouseEnter={(e) => (e.currentTarget.style.color = P.peri)}
            onMouseLeave={(e) => (e.currentTarget.style.color = P.borderMid)}
          >
            GitHub
          </a>
          {' '}&middot; Your API key never leaves your browser.
          {isReturning && (
            <>
              {' '}&middot;{' '}
              <button
                onClick={clearMemory}
                className="underline transition-colors"
                style={{ color: P.borderMid }}
                onMouseEnter={(e) => (e.currentTarget.style.color = P.petalFrost)}
                onMouseLeave={(e) => (e.currentTarget.style.color = P.borderMid)}
              >
                Clear memory
              </button>
            </>
          )}
        </p>
      </footer>
    </main>
  )
}
