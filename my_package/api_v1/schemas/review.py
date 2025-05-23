from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional



class ReviewBase(BaseModel):
    user_id: int
    place_id: int
    rating: float = Field(default=1, ge=1, le=5, description="Рейтинг от 1 до 5")
    comment: Optional[str] = Field(default=None, max_length=500, description="Комментарий")


class ReviewCreate(ReviewBase):
    pass


class Reviews(ReviewBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


