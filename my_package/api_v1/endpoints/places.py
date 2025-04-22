from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from my_package.api_v1.schemas.place import Places, PlaceCreate
from my_package.core.database import db_helper
from my_package.crud_package.place import (
    create_place,
    get_place,
    get_all_places,
    update_place_rating
)

router = APIRouter(prefix="/places", tags=["Places"])
async def get_db() -> AsyncSession:
    async with db_helper.session_factory() as session:
        yield session

@router.post("/", response_model=Places)
async def create_new_place(
    place_data: PlaceCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_place(db, place_data.model_dump())

@router.get("/{place_id}", response_model=Places)
async def read_place(
    place_id: int,
    db: AsyncSession = Depends(get_db)
):
    db_place = await get_place(db, place_id)
    if not db_place:
        raise HTTPException(status_code=404, detail="Place not found")
    return db_place

@router.get("/", response_model=list[Places])
async def read_places(
    skip: int = 0,
    limit: int = 100,
    type: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    return await get_all_places(db, skip, limit, type)

