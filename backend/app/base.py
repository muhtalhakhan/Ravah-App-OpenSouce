"""
Base agent interface that all agent frameworks must implement.
"""

from abc import ABC, abstractmethod
from hashlib import sha256

from app.agent import AgentGeneratedPost, AgentPlatformRule, AgentStructuredPayload
from app.mock_fixtures import MOCK_KEYWORDS_FALLBACK, MOCK_THEME_TEMPLATES

PLATFORM_RULES: dict[str, AgentPlatformRule] = {
    "linkedin": AgentPlatformRule(
        platform="linkedin",
        tone="professional, insight-led, credible",
        max_caption_chars=700,
        max_hook_chars=120,
    ),
    "x": AgentPlatformRule(
        platform="x",
        tone="punchy, concise, contrarian-friendly",
        max_caption_chars=280,
        max_hook_chars=70,
    ),
    "instagram": AgentPlatformRule(
        platform="instagram",
        tone="story-driven, visual-first, warm",
        max_caption_chars=600,
        max_hook_chars=100,
    ),
}


class BaseAgent(ABC):
    """
    Abstract base class for agent implementations.
    All agent frameworks (CrewAI, Agno, LangChain) must implement this interface.
    """

    def __init__(self, mock_mode: bool = True):
        """
        Initialize the agent.
        
        Args:
            mock_mode: If True, use mock responses instead of real API calls
        """
        self.mock_mode = mock_mode

    @abstractmethod
    def process_query(self, query: str, context: dict | None = None) -> dict:
        """
        Process a user query and return a response.
        
        Args:
            query: The user's query string
            context: Optional context dictionary
            
        Returns:
            Dictionary containing:
                - result: The agent's response string
                - metadata: Additional information about the processing
        """
        pass

    @abstractmethod
    def get_framework_name(self) -> str:
        """
        Get the name of the agent framework.
        
        Returns:
            Framework name (e.g., "crewai", "agno", "langchain")
        """
        pass

    def is_available(self) -> bool:
        """
        Check if the agent framework is available and properly configured.
        
        Returns:
            True if available, False otherwise
        """
        return True

    def build_structured_payload(self, query: str, context: dict | None = None) -> AgentStructuredPayload:
        """
        Deterministically generate founder-oriented content output.
        """
        safe_context = context or {}
        product_name = str(safe_context.get("product_name") or "Founder Product").strip()
        short_description = str(
            safe_context.get("short_description") or safe_context.get("problem_statement") or query
        ).strip()
        tone = str(safe_context.get("tone") or "clear, practical, founder-to-founder").strip()
        keywords = safe_context.get("keywords") or MOCK_KEYWORDS_FALLBACK
        if not isinstance(keywords, list):
            keywords = [str(keywords)]
        keywords = [str(k).strip() for k in keywords if str(k).strip()][:5]

        weekly_themes = self._build_weekly_themes(product_name, short_description, query)
        platforms = self._get_platforms(safe_context)

        posts: list[AgentGeneratedPost] = []
        for day_index, theme in enumerate(weekly_themes, start=1):
            for platform in platforms:
                post = self._build_post(
                    platform=platform,
                    day=day_index,
                    theme=theme,
                    product_name=product_name,
                    tone=tone,
                    keywords=keywords,
                )
                posts.append(post)

        return AgentStructuredPayload(
            product_name=product_name,
            short_description=short_description,
            tone=tone,
            keywords=keywords,
            weekly_themes=weekly_themes,
            posts=posts,
        )

    def build_prompt(self, query: str, context: dict | None = None) -> str:
        """
        Build a structured instruction prompt for founder-content generation.
        """
        safe_context = context or {}
        platforms = ", ".join(self._get_platforms(safe_context))
        product_name = safe_context.get("product_name", "Founder Product")
        tone = safe_context.get("tone", "clear, practical, founder-to-founder")
        keywords = safe_context.get("keywords", ["founder", "execution", "growth"])

        return (
            "You are a founder content strategist. "
            "Return a one-week content plan and platform-ready posts.\n"
            f"Product: {product_name}\n"
            f"User Query: {query}\n"
            f"Tone: {tone}\n"
            f"Keywords: {keywords}\n"
            f"Platforms: {platforms}\n"
            "Rules:\n"
            "- LinkedIn: professional and insight-led.\n"
            "- X: concise and punchy, keep caption under 280 chars.\n"
            "- Instagram: story-first and visual-forward.\n"
            "Output JSON-friendly structured fields: themes, posts, hashtags, visual_prompt."
        )

    def summarize_structured_payload(self, payload: AgentStructuredPayload) -> str:
        """
        Provide compact human-readable summary while preserving structured data separately.
        """
        return (
            f"Generated {len(payload.weekly_themes)} weekly themes and "
            f"{len(payload.posts)} platform posts for {payload.product_name}."
        )

    def _get_platforms(self, context: dict) -> list[str]:
        raw = context.get("platforms") or ["linkedin", "x", "instagram"]
        if not isinstance(raw, list):
            return ["linkedin", "x", "instagram"]

        normalized: list[str] = []
        for item in raw:
            key = str(item).strip().lower()
            if key in PLATFORM_RULES and key not in normalized:
                normalized.append(key)

        return normalized or ["linkedin", "x", "instagram"]

    def _build_weekly_themes(self, product_name: str, short_description: str, query: str) -> list[str]:
        seed = sha256(f"{product_name}|{short_description}|{query}".encode("utf-8")).hexdigest()
        offset = int(seed[:2], 16) % len(MOCK_THEME_TEMPLATES)
        ordered = MOCK_THEME_TEMPLATES[offset:] + MOCK_THEME_TEMPLATES[:offset]
        return [f"{product_name}: {item}" for item in ordered]

    def _build_post(
        self,
        platform: str,
        day: int,
        theme: str,
        product_name: str,
        tone: str,
        keywords: list[str],
    ) -> AgentGeneratedPost:
        rule = PLATFORM_RULES[platform]
        keyword_blob = " ".join(f"#{k.replace(' ', '')}" for k in keywords[:2])

        if platform == "x":
            hook = f"{theme[:60]}"
            caption = f"{theme}. {product_name} in build mode. {keyword_blob}".strip()
        elif platform == "instagram":
            hook = f"Day {day}: {theme[:88]}"
            caption = f"{theme}\n\nTone: {tone}\nWhat this means for founders this week."
        else:
            hook = f"{theme[:110]}"
            caption = f"{theme}. Practical takeaways for builders and operators this week."

        hook = self._fit_text(hook, rule.max_hook_chars)
        caption = self._fit_text(caption, rule.max_caption_chars)

        hashtags = [f"#{k.replace(' ', '')}" for k in keywords] + ["#buildinpublic", "#founder"]
        hashtags = hashtags[:6]

        return AgentGeneratedPost(
            platform=platform,
            day=day,
            theme=theme,
            hook=hook,
            caption=caption,
            hashtags=hashtags,
            visual_prompt=f"Create a minimal social card for '{theme}' with bold typography.",
            rule_applied=rule,
            hook_chars=len(hook),
            caption_chars=len(caption),
        )

    def _fit_text(self, value: str, max_chars: int) -> str:
        if len(value) <= max_chars:
            return value
        if max_chars <= 3:
            return value[:max_chars]
        return value[: max_chars - 3].rstrip() + "..."
