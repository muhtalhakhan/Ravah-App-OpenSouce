import type { Platform, ContentType, Style, GenerationRequest } from './types'

export const PLATFORM_SPECS: Record<Platform, { name: string; maxChars: number; hashtagCount: string; notes: string }> = {
  x: {
    name: 'X (Twitter)',
    maxChars: 280,
    hashtagCount: '2-3',
    notes:
      'Ultra-concise. The full_post must be ≤280 characters including hashtags. If the thought needs more space, write a numbered thread (1/, 2/, 3/) where each tweet is ≤280 chars. Hook is the first tweet.',
  },
  instagram: {
    name: 'Instagram',
    maxChars: 2200,
    hashtagCount: '10-15',
    notes:
      'Visual-first. Open with the hook, tell a short story, close with CTA. Use line breaks generously. Put hashtags in a separate block at the end.',
  },
  linkedin: {
    name: 'LinkedIn',
    maxChars: 3000,
    hashtagCount: '3-5',
    notes:
      'Professional thought leadership. Open with a bold one-liner, then short paragraphs. End with a question to drive comments.',
  },
}

export const CONTENT_TYPE_LABELS: Record<ContentType, string> = {
  personal: 'Personal brand — sharing expertise, opinions, and experiences as an individual',
  brand: 'Brand/product content — educating and building trust around a product or service',
  building_in_public: 'Building in public — openly sharing the founder journey, wins, failures, and lessons',
}

export const STYLE_LABELS: Record<Style, string> = {
  educational: 'Educational — teach something actionable',
  storytelling: 'Storytelling — narrative with a beginning, middle, and lesson',
  motivational: 'Motivational — inspire action or mindset shift',
  behind_the_scenes: 'Behind the Scenes — raw, authentic, unfiltered',
  mixed: 'Mixed — rotate through styles across the days',
}

export function buildSystemPrompt(name: string): string {
  return (
    `You are an elite social media strategist writing content for ${name}. ` +
    'You specialise in founder-led and creator content for X (Twitter), Instagram, and LinkedIn. ' +
    'Every post strictly follows the ClearV framework and is ready to publish — ' +
    'no placeholders, no brackets, no generic filler. Write in a human, natural voice. ' +
    'You always return valid JSON and nothing else.'
  )
}

export function buildUserPrompt(req: GenerationRequest): string {
  const platformSpecs = req.platforms
    .map((p) => {
      const s = PLATFORM_SPECS[p]
      return `- **${s.name}**: ${s.notes} Max ${s.maxChars} chars. Use ${s.hashtagCount} hashtags.`
    })
    .join('\n')

  let optionalLines = ''
  if (req.keywords.trim()) optionalLines += `\n- **Always include**: ${req.keywords}`
  if (req.avoid.trim()) optionalLines += `\n- **Never write**: ${req.avoid}`

  const totalPosts = req.numDays * req.platforms.length

  return `## Task
Generate a ${req.numDays}-day content calendar for ${req.name}.
Total posts: ${totalPosts} (${req.numDays} days × ${req.platforms.length} platforms).

## About ${req.name}
- **Content type**: ${CONTENT_TYPE_LABELS[req.contentType]}
- **What they're building / doing**: ${req.summary}
- **Target audience**: ${req.audience}
- **Style**: ${STYLE_LABELS[req.style]}
- **Tone**: ${req.tone}${optionalLines}

## ClearV Framework (every post must follow this)
- **C – Capture**: Scroll-stopping first line. Bold claim, surprising stat, or provocative question.
- **L – Lead**: The single core message. One sentence max.
- **E – Educate**: An insight, data point, mini-story, or relatable experience that backs up L.
- **A – Activate**: A specific call-to-action (comment, share, try something, follow up).
- **R – Resonate**: A closing line that is emotionally sticky or highly shareable.
- **V – Visual**: One sentence describing the ideal image or graphic for this post.

## Platform Specifications
${platformSpecs}

## Progression
Build a coherent narrative arc across the days — don't write isolated standalone posts.
Day 1 hooks attention. Middle days educate and build trust. Final days convert or inspire action.

## Output Format
Return a single raw JSON array — no markdown fences, no commentary.
Each object must match this schema exactly:

{
  "day": <integer 1-${req.numDays}>,
  "platform": "<x|instagram|linkedin>",
  "clearv": {
    "capture": "<string>",
    "lead": "<string>",
    "educate": "<string>",
    "activate": "<string>",
    "resonate": "<string>",
    "visual": "<string>"
  },
  "full_post": "<complete post text, copy-paste ready, hashtags included>",
  "hashtags": ["<tag>"],
  "char_count": <integer>
}

Produce exactly ${totalPosts} objects. Order: day 1 all platforms, day 2 all platforms, etc.`.trim()
}

export function renderMarkdown(posts: import('./types').GeneratedPost[], req: GenerationRequest): string {
  const platformNames: Record<Platform, string> = {
    x: 'X (Twitter)',
    instagram: 'Instagram',
    linkedin: 'LinkedIn',
  }

  const today = new Date().toISOString().split('T')[0]
  const lines: string[] = [
    `# ${req.name} — ${req.numDays}-Day Content Calendar`,
    '',
    `Generated: ${today}  `,
    `Type: ${CONTENT_TYPE_LABELS[req.contentType]}  `,
    `Summary: ${req.summary}  `,
    `Tone: ${req.tone}  `,
    `Platforms: ${req.platforms.map((p) => platformNames[p]).join(', ')}`,
    '',
    '---',
    '',
  ]

  const days: Record<number, typeof posts> = {}
  for (const post of posts) {
    if (!days[post.day]) days[post.day] = []
    days[post.day].push(post)
  }

  for (const dayNum of Object.keys(days)
    .map(Number)
    .sort((a, b) => a - b)) {
    lines.push(`## Day ${dayNum}`, '')
    for (const post of days[dayNum]) {
      const pname = platformNames[post.platform]
      lines.push(
        `### ${pname}`,
        '',
        `> **Hook:** ${post.clearv.capture}`,
        '',
        `**Lead:** ${post.clearv.lead}`,
        '',
        `**Educate:** ${post.clearv.educate}`,
        '',
        `**Activate:** ${post.clearv.activate}`,
        '',
        `**Resonate:** ${post.clearv.resonate}`,
        '',
        `**Visual:** _${post.clearv.visual}_`,
        '',
        '**Full post:**',
        '',
        '```',
        post.full_post,
        '```',
        '',
        `*${post.hashtags.join(' ')} — ${post.char_count} chars*`,
        '',
        '---',
        '',
      )
    }
  }

  return lines.join('\n')
}
