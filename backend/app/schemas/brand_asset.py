from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BrandAssetBase(BaseModel):
    brand_profile_id: int | None = None
    source_type: str = "manual"
    figma_file_url: str | None = None
    logo_url: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    typography: str | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class BrandAssetCreate(BrandAssetBase):
    pass


class BrandAssetUpdate(BaseModel):
    brand_profile_id: int | None = None
    source_type: str | None = None
    figma_file_url: str | None = None
    logo_url: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    typography: str | None = None
    metadata_json: dict[str, Any] | None = None


class BrandAssetResponse(BrandAssetBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
