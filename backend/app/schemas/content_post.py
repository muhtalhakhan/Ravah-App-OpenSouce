from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ContentPostBase(BaseModel):
    content_plan_id: int
    platform: str
    day_index: int
    post_order: int = 0
    hook: str | None = None
    caption: str
    hashtags: list[str] = Field(default_factory=list)
    visual_prompt: str | None = None
    status: str = "draft"


class ContentPostCreate(ContentPostBase):
    pass


class ContentPostUpdate(BaseModel):
    content_plan_id: int | None = None
    platform: str | None = None
    day_index: int | None = None
    post_order: int | None = None
    hook: str | None = None
    caption: str | None = None
    hashtags: list[str] | None = None
    visual_prompt: str | None = None
    status: str | None = None


class ContentPostResponse(ContentPostBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
