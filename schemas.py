from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductOut(BaseModel):
    id: str
    name: str
    category: str
    price: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=60)
    price: float = Field(gt=0)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    category: str | None = Field(default=None, min_length=1, max_length=60)
    price: float | None = Field(default=None, gt=0)


class ProductPage(BaseModel):
    items: list[ProductOut]
    next_cursor: str | None
    limit: int
    category: str | None
