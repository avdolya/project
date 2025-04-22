from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from my_package.core.database import db_helper
from my_package.crud_package.user import create_user, get_user
from my_package.api_v1.schemas.user import UserCreate, Users

router = APIRouter(prefix="/users", tags=["Users"])




async def get_db() -> AsyncSession:
    async with db_helper.session_factory() as session:
        yield session



@router.post("/", response_model=Users)
async def create_new_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_user(db, user_data.model_dump())

@router.get("/{user_id}", response_model=Users)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    db_user = await get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user



