import { GoogleGenAI } from '@google/genai'
import { NextRequest, NextResponse } from 'next/server'
import { buildSystemPrompt, buildUserPrompt } from '@/lib/prompts'
import type { GenerationRequest, GeneratedPost, ClearVBreakdown } from '@/lib/types'

export const maxDuration = 60

export async function POST(req: NextRequest) {
  let body: GenerationRequest
  try {
    body = await req.json()
  } catch {
    return NextResponse.json({ error: 'Invalid request body' }, { status: 400 })
  }

  const { apiKey, name, contentType, summary, numDays, platforms, style, tone, audience, keywords, avoid } = body

  if (!apiKey?.trim()) {
    return NextResponse.json({ error: 'Google API key is required' }, { status: 400 })
  }
  if (!name?.trim()) {
    return NextResponse.json({ error: 'Name is required' }, { status: 400 })
  }
  if (!summary?.trim() || summary.trim().length < 15) {
    return NextResponse.json({ error: 'Please describe what you\'re building (at least 15 characters)' }, { status: 400 })
  }
  if (!platforms?.length) {
    return NextResponse.json({ error: 'Select at least one platform' }, { status: 400 })
  }

  try {
    const ai = new GoogleGenAI({ apiKey: apiKey.trim() })

    const systemPrompt = buildSystemPrompt(name)
    const userPrompt = buildUserPrompt({ apiKey, name, contentType, summary, numDays, platforms, style, tone, audience, keywords, avoid })

    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash-preview-04-17',
      config: {
        systemInstruction: systemPrompt,
        temperature: 0.85,
        topP: 0.95,
        maxOutputTokens: 8192,
        responseMimeType: 'application/json',
        thinkingConfig: { thinkingBudget: 1024 },
      },
      contents: userPrompt,
    })

    let raw = response.text?.trim() ?? ''
    raw = raw.replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/i, '')

    let data: unknown[]
    try {
      data = JSON.parse(raw)
    } catch {
      return NextResponse.json({ error: 'Gemini returned invalid JSON. Please try again.' }, { status: 502 })
    }

    if (!Array.isArray(data)) {
      return NextResponse.json({ error: 'Unexpected response format from Gemini.' }, { status: 502 })
    }

    const posts: GeneratedPost[] = data.map((raw: unknown) => {
      const item = raw as Record<string, unknown>
      const cv = (item.clearv ?? {}) as Record<string, string>
      return {
        day: item.day as number,
        platform: item.platform as GeneratedPost['platform'],
        clearv: {
          capture: cv.capture ?? '',
          lead: cv.lead ?? '',
          educate: cv.educate ?? '',
          activate: cv.activate ?? '',
          resonate: cv.resonate ?? '',
          visual: cv.visual ?? '',
        } as ClearVBreakdown,
        full_post: (item.full_post as string) ?? '',
        hashtags: (item.hashtags as string[]) ?? [],
        char_count: (item.char_count as number) ?? ((item.full_post as string)?.length ?? 0),
      }
    })

    return NextResponse.json({ posts })
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : 'Unknown error'
    if (message.includes('API_KEY') || message.includes('api key') || message.includes('401')) {
      return NextResponse.json({ error: 'Invalid API key. Check your Google AI Studio key and try again.' }, { status: 401 })
    }
    return NextResponse.json({ error: `Generation failed: ${message}` }, { status: 500 })
  }
}
