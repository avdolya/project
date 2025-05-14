from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from my_package.core.database import db_helper
from fastapi import (
        APIRouter,
        Depends,
        Form,
        HTTPException,
        status,
        Request,
)
import time
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from pydantic import BaseModel
from .schemas.user import UserSchema
from my_package.auth import utils as auth_utils
from ..core.database import db_helper
from ..crud_package.user import get_user_by_name
from ..core.models.user import User



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/jwt/login/")

class TokenInfo(BaseModel):
    access_token: str
    token_type: str

router  = APIRouter(prefix="/jwt", tags=["JWT"])

async def get_db() -> AsyncSession:
    async with db_helper.session_factory() as session:
        yield session

async def validate_auth_user(
        username: str = Form(),
        password: str = Form(),
        db: AsyncSession = Depends(get_db),
):
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid name or password",
    )
    user = await get_user_by_name(db, username)
    # делаем проверку: проверяем логин и пароль
    if not user:
        raise unauthed_exc

    if not auth_utils.validate_password(
        password=password,
        hashed_password=user.hashed_password,
    ):
        raise unauthed_exc
    return  UserSchema.model_validate(user)

# получаем полезные данные из тела токена
# берем токен и декодим при помощи decode_jwt
# используем public_key для проверки валидности токена
#credentials: HTTPAuthorizationCredentials = Depends(http_bearer),


async def get_current_token_payload(
    token: str = Depends(oauth2_scheme),
) -> dict:
    try:
        payload = auth_utils.decode_jwt(
            token=token,
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token error {e}"
        )
    return payload

# берем
async def get_current_auth_user(
    # payload получаем из прошлой функции
    payload: dict = Depends(get_current_token_payload),
    db: AsyncSession = Depends(get_db),
) -> UserSchema:
    # если юзер есть, то мы его возвращаем
    username: str | None = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid (no name)",
        )
    user = await get_user_by_name(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid (user not found)",
        )

    return UserSchema.model_validate(user)

async def get_current_active_auth_user(
user: UserSchema = Depends(get_current_auth_user),
):
    if user.active:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="user inactive",
    )
    return user

@router.post("/login/", response_model=TokenInfo)
async def auth_user_issue_jwt(
        #user: UserSchema = Depends(validate_auth_user) # зависит от функции которая проверяет, прошел ли пользователь аутентификацию
        username: str = Form(...),
        password: str = Form(...),
        db: AsyncSession = Depends(get_db),
):
    user = await validate_auth_user(username, password, db)
    jwt_payload = {
        "sub": user.username,
        "username": user.username,
        "email": user.email,
        "iat": int(time.time()),

    }
    # если чел прошел проверку возвращаем токен
    token = auth_utils.encode_jwt(jwt_payload)
    return TokenInfo(
        access_token=token,
        token_type="Bearer" #тип который по умолчанию используем для токена
    )

# пользователь будет получать информацтю о себе по токену
@router.get("/users/me/")
async def auth_user_check_self_info(
        # пользователя получаем при помощи функциии get_current_active_auth_user
        payload: dict = Depends(get_current_token_payload),
        user: UserSchema = Depends(get_current_active_auth_user),
):
    iat = payload.get("iat")
    return {
        "username": user.username,
        "email": user.email,
        "logged_in_at": iat,
    }









