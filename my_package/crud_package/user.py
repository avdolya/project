from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from my_package.core.models.user import User
from my_package.auth.utils import hash_password
from fastapi import HTTPException, status

async def create_user(db: AsyncSession, user_data: dict) -> User:
    existing_user = await db.execute(
        select(User).where(
            (User.username == user_data["username"]) |
            (User.email == user_data["email"])
        )
    )
    existing_user = existing_user.scalar_one_or_none()
    if existing_user:
        # Определяем, какое поле дублируется
        if existing_user.username == user_data["username"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким именем уже существует"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
    try:
        hashed_pwd = hash_password(user_data.pop('password'))  # Пароль хешируется
        db_user = User(**user_data, hashed_password=hashed_pwd)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Произошла ошибка при создании пользователя"
        )


'''async def get_user(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()'''

# ищем по айдишнику
async def get_user(db: AsyncSession, user_id: int) -> User | None:
# асинхронный метод, который ищет запись в
# таблице User по первичному ключу (user_id).
    return await db.get(User, user_id)

# ищем по ник нейму
async def get_user_by_name(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()

# db.get - ищет по первичному ключу
# db.execute универсальный запрос
# scalar_one_or_none none либо одна запись
