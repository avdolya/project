from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime

class UserBase(BaseModel):
    name: str = Field(default=..., min_length=1, max_length=50, description="Имя, от 1 до 50 символов")
    email: EmailStr = Field(default=..., description="Электронная почта")
    role: str


class UserCreate(UserBase):
    password: str = Field(default=..., min_length=8, max_length=12, description="Пароль от 8 до 12 символов")


class Users(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True)
    username: str
    password: bytes
    email: EmailStr | None = None
    active: bool = True


