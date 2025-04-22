from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from my_package.core.database import db_helper
from my_package.crud_package.review import create_review, get_reviews_by_place, delete_review
from my_package.crud_package.place import update_place_rating
from my_package.api_v1.schemas.review import ReviewCreate, Reviews

router = APIRouter(prefix="/reviews", tags=["Reviews"])
async def get_db() -> AsyncSession:
    async with db_helper.session_factory() as session:
        yield session

@router.post("/", response_model=Reviews)
async def create_new_review(
    review_data: ReviewCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_review(db, review_data.dict())

@router.get("/place/{place_id}", response_model=list[Reviews])
async def get_reviews_for_place(
    place_id: int,
    db: AsyncSession = Depends(get_db)
):
    reviews = await get_reviews_by_place(db, place_id)
    if not reviews:
        raise HTTPException(
            status_code=404,
            detail="No reviews found for this place"
        )
    return reviews

@router.delete("/{review_id}")
async def delete_review_endpoint(
    review_id: int,
    db: AsyncSession = Depends(get_db)
):
    success = await delete_review(db, review_id)
    if not success:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": "Review deleted"}

