from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, description="Имя, от 1 до 50 символов")
    email: EmailStr = Field(..., description="Электронная почта")


# валидация данных при регистрации
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=12, description="Пароль от 8 до 12 символов")

# данные которые видит клиент
class UsersResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True
        # более современный вариант???
        #model_config = ConfigDict(from_attributes=True)


# внутреннее представление пользователя
class UserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    hashed_password: bytes
    active: bool = True
    created_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


