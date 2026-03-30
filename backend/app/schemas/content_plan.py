from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ContentPlanBase(BaseModel):
    product_idea_id: int
    brand_profile_id: int | None = None
    week_start: date
    platforms: list[str] = Field(default_factory=list)
    weekly_themes: list[str] = Field(default_factory=list)
    plan_notes: str | None = None
    status: str = "draft"


class ContentPlanCreate(ContentPlanBase):
    pass


class ContentPlanUpdate(BaseModel):
    product_idea_id: int | None = None
    brand_profile_id: int | None = None
    week_start: date | None = None
    platforms: list[str] | None = None
    weekly_themes: list[str] | None = None
    plan_notes: str | None = None
    status: str | None = None


class ContentPlanResponse(ContentPlanBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
