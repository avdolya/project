from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from my_package.core.models.user import User

async def create_user(db: AsyncSession, user_data: dict) -> User:
    new_user = User(**user_data)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def get_user(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalar_one_or_none()


