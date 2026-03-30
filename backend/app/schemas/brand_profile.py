from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BrandProfileBase(BaseModel):
    tone: str | None = None
    keywords: list[str] = Field(default_factory=list)
    sample_post: str | None = None
    voice_guidelines: str | None = None


class BrandProfileCreate(BrandProfileBase):
    pass


class BrandProfileUpdate(BaseModel):
    tone: str | None = None
    keywords: list[str] | None = None
    sample_post: str | None = None
    voice_guidelines: str | None = None


class BrandProfileResponse(BrandProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
