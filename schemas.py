from pydantic import BaseModel, EmailStr, Field, field_validator, ValidationError
from datetime import datetime
from typing import Optional, List


'''class UserBase(BaseModel):
    name: str = Field(default=..., min_length=1, max_length=50, description="Имя, от 1 до 50 символов")
    email: EmailStr = Field(default=..., description="Электронная почта")
    role: str


class UserCreate(UserBase):
    password: str = Field(default=..., min_length=8, max_length=12, description="Пароль от 8 до 12 символов")


class Users(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True'''

class PlaceBase(BaseModel):
    name: str = Field(default=..., min_length=1, max_length=50, description="Название, от 1 до 50 символов")
    description: str = Field(default=None, max_length=500, description="Дополнительные заметки, не более 500 символов")
    type: str



class PlaceCreate(PlaceBase):
    pass


class Places(PlaceBase):
    id: int
    average_rating: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewBase(BaseModel):
    user_id: int
    place_id: int
    rating: int = Field(default=1, ge=1, le=10, description="Рейтинг от 1 до 10")
    comment: Optional[str] = Field(default=None, max_length=500, description="Комментарий")


class ReviewCreate(ReviewBase):
    pass


class Reviews(ReviewBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class VisitedPlaceBase(BaseModel):
    user_id: int
    place_id: int


class VisitedPlaceCreate(VisitedPlaceBase):
    pass


class VisitedPlace(VisitedPlaceBase):
    id: int
    visited_at: datetime

    class Config:
        from_attributes = True




