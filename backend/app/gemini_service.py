"""
Google Gemini integration for ClearV-structured social media post generation.

ClearV Framework
----------------
C – Capture   : Scroll-stopping first line (bold claim, question, or stat)
L – Lead      : The single core message / value proposition
E – Educate   : Insight, lesson, mini-story, or relatable experience
A – Activate  : Clear call-to-action — what should the reader do next?
R – Resonate  : Emotionally resonant closing line that begs to be shared
V – Visual    : Brief description of the ideal image/visual for this post
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Literal


Platform = Literal["x", "instagram", "linkedin"]
Mode = Literal["building_in_public", "product_content"]
Style = Literal["educational", "storytelling", "motivational", "behind_the_scenes", "mixed"]


# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class ClearVBreakdown:
    capture: str
    lead: str
    educate: str
    activate: str
    resonate: str
    visual: str


@dataclass
class GeneratedPost:
    day: int
    platform: Platform
    clearv: ClearVBreakdown
    full_post: str
    hashtags: list[str]
    char_count: int


@dataclass
class GenerationContext:
    mode: Mode
    summary: str
    num_days: int
    platforms: list[Platform]
    style: Style
    tone: str
    audience: str
    keywords: str = ""
    avoid: str = ""


# ── Platform specs ────────────────────────────────────────────────────────────

_PLATFORM_SPECS = {
    "x": {
        "name": "X (Twitter)",
        "max_chars": 280,
        "hashtag_count": "2-3",
        "notes": (
            "Ultra-concise. The full_post must be ≤280 characters including hashtags. "
            "If the thought needs more space, write a numbered thread (1/, 2/, 3/) "
            "where each tweet is ≤280 chars. Hook is the first tweet."
        ),
    },
    "instagram": {
        "name": "Instagram",
        "max_chars": 2200,
        "hashtag_count": "10-15",
        "notes": (
            "Visual-first. Open with the hook, tell a short story, close with CTA. "
            "Use line breaks generously. Put hashtags in a separate block at the end."
        ),
    },
    "linkedin": {
        "name": "LinkedIn",
        "max_chars": 3000,
        "hashtag_count": "3-5",
        "notes": (
            "Professional thought leadership. Open with a bold one-liner, "
            "then short paragraphs. End with a question to drive comments."
        ),
    },
}

_MODE_LABELS = {
    "building_in_public": "Building in Public (sharing the founder journey openly)",
    "product_content": "Product/Service Content (promoting and educating about the offering)",
}

_STYLE_LABELS = {
    "educational": "Educational — teach something actionable",
    "storytelling": "Storytelling — narrative with a beginning, middle, and lesson",
    "motivational": "Motivational — inspire action or mindset shift",
    "behind_the_scenes": "Behind the Scenes — raw, authentic, unfiltered",
    "mixed": "Mixed — rotate through styles across the days",
}


# ── Prompt builder ────────────────────────────────────────────────────────────

def _build_system_prompt() -> str:
    return (
        "You are an elite social media strategist and copywriter. "
        "You specialise in founder-led content for X (Twitter), Instagram, and LinkedIn. "
        "Every post you write strictly follows the ClearV framework and is ready to publish — "
        "no placeholders, no brackets, no generic filler. "
        "You always return valid JSON and nothing else."
    )


def _build_user_prompt(ctx: GenerationContext) -> str:
    platform_specs = "\n".join(
        f"- **{_PLATFORM_SPECS[p]['name']}**: {_PLATFORM_SPECS[p]['notes']} "
        f"Max {_PLATFORM_SPECS[p]['max_chars']} chars. "
        f"Use {_PLATFORM_SPECS[p]['hashtag_count']} hashtags."
        for p in ctx.platforms
    )

    avoid_line = f"\n- **Avoid**: {ctx.avoid}" if ctx.avoid.strip() else ""
    keywords_line = f"\n- **Always include keywords/topics**: {ctx.keywords}" if ctx.keywords.strip() else ""

    total_posts = ctx.num_days * len(ctx.platforms)

    return f"""
## Task
Generate a {ctx.num_days}-day content calendar with one post per day per platform.
Total posts required: {total_posts} ({ctx.num_days} days × {len(ctx.platforms)} platforms).

## Creator Profile
- **Mode**: {_MODE_LABELS[ctx.mode]}
- **What they're building / achieving**: {ctx.summary}
- **Target audience**: {ctx.audience}
- **Content style**: {_STYLE_LABELS[ctx.style]}
- **Tone**: {ctx.tone}{keywords_line}{avoid_line}

## ClearV Framework (mandatory for every post)
Each post MUST include all six components:
- **C – Capture**: A scroll-stopping first line. Bold claim, surprising stat, or provocative question.
- **L – Lead**: The single core message. One sentence max.
- **E – Educate**: An insight, data point, mini-story, or relatable experience that backs up L.
- **A – Activate**: A specific call-to-action (comment, share, try something, follow up).
- **R – Resonate**: A closing line that is emotionally sticky or highly shareable.
- **V – Visual**: One sentence describing the ideal image or graphic for this post.

## Platform Specifications
{platform_specs}

## Progression Rule
Days should build on each other thematically so the content feels like a coherent narrative arc, not random standalone posts. Day 1 should hook, mid-days should educate and deepen, and final days should convert or inspire action.

## Output Format
Return a single JSON array — no markdown fences, no commentary, just the raw JSON.
Each element must match this exact schema:

{{
  "day": <integer 1-{ctx.num_days}>,
  "platform": "<x|instagram|linkedin>",
  "clearv": {{
    "capture": "<string>",
    "lead": "<string>",
    "educate": "<string>",
    "activate": "<string>",
    "resonate": "<string>",
    "visual": "<string>"
  }},
  "full_post": "<complete post text, ready to copy-paste, including hashtags>",
  "hashtags": ["<tag1>", "<tag2>"],
  "char_count": <integer>
}}

Produce exactly {total_posts} objects. Order them: day 1 all platforms, day 2 all platforms, etc.
""".strip()


# ── Main generator ────────────────────────────────────────────────────────────

def generate_posts(ctx: GenerationContext, api_key: str, model: str = "gemini-2.5-flash-preview-04-17") -> list[GeneratedPost]:
    """
    Call the Gemini API and return a list of GeneratedPost objects.
    Uses the new google-genai SDK (google-genai package).
    Raises RuntimeError if the API key is missing or the call fails.
    """
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        raise RuntimeError(
            "google-genai is not installed. "
            "Run: pip install google-genai"
        )

    client = genai.Client(api_key=api_key)

    prompt = _build_user_prompt(ctx)

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=_build_system_prompt(),
            temperature=0.85,
            top_p=0.95,
            max_output_tokens=8192,
            response_mime_type="application/json",
            thinking_config=types.ThinkingConfig(thinking_budget=1024),
        ),
    )

    raw = response.text.strip()
    # Strip accidental markdown fences if the model adds them
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Gemini returned invalid JSON: {exc}\n\nRaw response:\n{raw[:500]}")

    posts: list[GeneratedPost] = []
    for item in data:
        cv = item.get("clearv", {})
        posts.append(
            GeneratedPost(
                day=item["day"],
                platform=item["platform"],
                clearv=ClearVBreakdown(
                    capture=cv.get("capture", ""),
                    lead=cv.get("lead", ""),
                    educate=cv.get("educate", ""),
                    activate=cv.get("activate", ""),
                    resonate=cv.get("resonate", ""),
                    visual=cv.get("visual", ""),
                ),
                full_post=item.get("full_post", ""),
                hashtags=item.get("hashtags", []),
                char_count=item.get("char_count", len(item.get("full_post", ""))),
            )
        )

    return posts


# ── Markdown renderer ─────────────────────────────────────────────────────────

def render_markdown(posts: list[GeneratedPost], ctx: GenerationContext) -> str:
    """Render posts into a clean, shareable Markdown document."""
    from datetime import date

    platform_names = {"x": "X (Twitter)", "instagram": "Instagram", "linkedin": "LinkedIn"}

    lines: list[str] = [
        f"# Content Calendar — {ctx.num_days} Days",
        f"",
        f"**Generated:** {date.today().isoformat()}  ",
        f"**Mode:** {_MODE_LABELS[ctx.mode]}  ",
        f"**Summary:** {ctx.summary}  ",
        f"**Audience:** {ctx.audience}  ",
        f"**Style:** {_STYLE_LABELS[ctx.style]}  ",
        f"**Tone:** {ctx.tone}  ",
        f"**Platforms:** {', '.join(platform_names.get(p, p) for p in ctx.platforms)}",
        f"",
        f"---",
        f"",
    ]

    # Group by day
    days: dict[int, list[GeneratedPost]] = {}
    for post in posts:
        days.setdefault(post.day, []).append(post)

    for day_num in sorted(days.keys()):
        lines.append(f"## Day {day_num}")
        lines.append("")

        for post in days[day_num]:
            pname = platform_names.get(post.platform, post.platform)
            lines += [
                f"### {pname}",
                "",
                f"> **Capture (hook):** {post.clearv.capture}",
                "",
                f"**Lead:** {post.clearv.lead}",
                "",
                f"**Educate:** {post.clearv.educate}",
                "",
                f"**Activate:** {post.clearv.activate}",
                "",
                f"**Resonate:** {post.clearv.resonate}",
                "",
                f"**Visual:** _{post.clearv.visual}_",
                "",
                "**Full post:**",
                "",
                "```",
                post.full_post,
                "```",
                "",
                f"*Hashtags: {' '.join(post.hashtags)} — {post.char_count} chars*",
                "",
                "---",
                "",
            ]

    return "\n".join(lines)
