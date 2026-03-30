from datetime import date

from pydantic import BaseModel, Field

from .content_plan import ContentPlanResponse
from .content_post import ContentPostResponse


class GenerateContentPlanRequest(BaseModel):
    product_idea_id: int
    brand_profile_id: int | None = None
    week_start: date | None = None
    platforms: list[str] = Field(default_factory=lambda: ["linkedin", "x", "instagram"])


class GenerateContentPostsRequest(BaseModel):
    content_plan_id: int
    replace_existing: bool = True


class GenerateContentPostsResponse(BaseModel):
    content_plan: ContentPlanResponse
    posts: list[ContentPostResponse]
