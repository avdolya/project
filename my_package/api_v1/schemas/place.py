from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class PlaceBase(BaseModel):
    name: str = Field(default=..., min_length=1, max_length=50, description="Название, от 1 до 50 символов")
    description: str = Field(default=..., max_length=500, description="Дополнительные заметки, не более 500 символов")
    type: str = Field(..., description="Тип места")

class PlaceCreate(PlaceBase):
    image_data: bytes = Field(None, description="Бинарные данные изображения")


class Places(PlaceBase):
    id: int
    average_rating: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True





