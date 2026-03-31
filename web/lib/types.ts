export type Platform = 'x' | 'instagram' | 'linkedin'
export type ContentType = 'personal' | 'brand' | 'building_in_public'
export type Style = 'educational' | 'storytelling' | 'motivational' | 'behind_the_scenes' | 'mixed'

export interface ClearVBreakdown {
  capture: string
  lead: string
  educate: string
  activate: string
  resonate: string
  visual: string
}

export interface GeneratedPost {
  day: number
  platform: Platform
  clearv: ClearVBreakdown
  full_post: string
  hashtags: string[]
  char_count: number
}

export interface GenerationRequest {
  apiKey: string
  name: string
  contentType: ContentType
  summary: string
  numDays: 7 | 18 | 30
  platforms: Platform[]
  style: Style
  tone: string
  audience: string
  keywords: string
  avoid: string
}
