from enum import Enum
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime

class UserRole(str, Enum):
    user = "user"
    admin = "admin"

class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    role: UserRole = Field(default=UserRole.user)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=12)


# данные которые видит клиент
class UsersResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True


# внутреннее представление пользователя
class UserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    hashed_password: bytes
    active: bool = True
    role: str
    created_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True)


