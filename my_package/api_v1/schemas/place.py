from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class PlaceBase(BaseModel):
    name: str = Field(default=..., min_length=1, max_length=50)
    description: str = Field(default=..., max_length=500)
    type: str

class PlaceCreate(PlaceBase):
    image_data: bytes = Field(None)


class Places(PlaceBase):
    id: int
    average_rating: Optional[float] = 0.0
    created_at: datetime

    class Config:
        from_attributes = True





