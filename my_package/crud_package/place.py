from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from my_package.core.models.place import Place
from  my_package.core.models.review import Review


async def create_place(db: AsyncSession, place_data: dict) -> Place:
    new_place = Place(**place_data)
    db.add(new_place)
    await db.commit()
    await db.refresh(new_place)
    return new_place


async def get_place(db: AsyncSession, place_id: int) -> Place | None:
    result = await db.execute(select(Place).where(Place.id == place_id))
    return result.scalar_one_or_none()


async def get_all_places(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 3,
        type_filter: str | None = None
) -> list[Place]:
    query = select(Place).order_by(Place.average_rating.desc())

    if type_filter:
        query = query.where(Place.type == type_filter)

    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


async def update_place_rating(db: AsyncSession, place_id: int):
    avg_rating = await db.execute(
        select(func.avg(Review.rating))
        .where(Review.place_id == place_id)
    )
    place = await get_place(db, place_id)
    if place:
        place.average_rating = avg_rating.scalar() or 0.0
        await db.commit()
        await db.refresh(place)
    return place


