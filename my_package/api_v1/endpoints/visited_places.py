from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from my_package.core.database import db_helper
from my_package.crud_package.visited_place import (
    create_visited_place,
    get_user_visited_places
)
from my_package.api_v1.schemas.visited_place import (
    VisitedPlaceCreate,
    VisitedPlace,
)

router = APIRouter(prefix="/visited-places", tags=["Visited Places"])
async def get_db() -> AsyncSession:
    async with db_helper.session_factory() as session:
        yield session

@router.post("/", response_model=VisitedPlace)
async def add_visited_place(
    visited_data: VisitedPlaceCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_visited_place(db, visited_data.dict())

@router.get("/user/{user_id}", response_model=list[VisitedPlace])
async def get_visited_places_for_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    visits = await get_user_visited_places(db, user_id)
    if not visits:
        raise HTTPException(
            status_code=404,
            detail="No visited places found"
        )
    return visits



