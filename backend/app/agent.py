"""
Pydantic schemas for agent interaction.
"""

from pydantic import BaseModel, Field


class AgentQuery(BaseModel):
    """Schema for agent query request."""

    query: str = Field(..., min_length=1, max_length=1000, description="User query for the agent")
    context: dict | None = Field(None, description="Optional context for the query")


class AgentPlatformRule(BaseModel):
    platform: str
    tone: str
    max_caption_chars: int
    max_hook_chars: int


class AgentGeneratedPost(BaseModel):
    platform: str
    day: int
    theme: str
    hook: str
    caption: str
    hashtags: list[str]
    visual_prompt: str
    rule_applied: AgentPlatformRule
    hook_chars: int
    caption_chars: int


class AgentStructuredPayload(BaseModel):
    product_name: str
    short_description: str
    tone: str
    keywords: list[str]
    weekly_themes: list[str]
    posts: list[AgentGeneratedPost]


class AgentResponse(BaseModel):
    """Schema for agent response."""

    result: str = Field(..., description="Agent's response to the query")
    framework: str = Field(..., description="Agent framework used (crewai/agno/langchain)")
    structured: AgentStructuredPayload | None = Field(
        None,
        description="Structured founder-content output with platform-specific posts.",
    )
    metadata: dict | None = Field(None, description="Additional metadata about the response")


class AgentStatus(BaseModel):
    """Schema for agent status."""

    framework: str = Field(..., description="Current agent framework")
    available: bool = Field(..., description="Whether agent is available")
    mock_mode: bool = Field(..., description="Whether running in mock mode")
