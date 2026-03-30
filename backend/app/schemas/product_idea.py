from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProductIdeaBase(BaseModel):
    product_name: str
    short_description: str
    problem_statement: str | None = None
    target_audience: str | None = None


class ProductIdeaCreate(ProductIdeaBase):
    pass


class ProductIdeaUpdate(BaseModel):
    product_name: str | None = None
    short_description: str | None = None
    problem_statement: str | None = None
    target_audience: str | None = None


class ProductIdeaResponse(ProductIdeaBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
