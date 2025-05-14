from sqlalchemy.ext.asyncio import AsyncSession
from  my_package.core.models.review  import Review

async def create_review(db: AsyncSession, review_data: dict) -> Review:
    new_review = Review(**review_data)
    db.add(new_review)
    await db.commit()
    await db.refresh(new_review)
    return new_review

async def get_reviews_by_place(
    db: AsyncSession,
    place_id: int
) -> list[Review]:
    result = await db.execute(
        select(Review)
        .where(Review.place_id == place_id)
    )
    return result.scalars().all()

async def delete_review(
    db: AsyncSession,
    review_id: int
) -> bool:
    result = await db.execute(
        delete(Review)
        .where(Review.id == review_id)
    )
    await db.commit()
    return result.rowcount > 0


