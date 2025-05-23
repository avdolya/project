from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from my_package.core.models.visited_place import VisitedPlace

async def create_visited_place(
    db: AsyncSession,
    visited_data: dict
) -> VisitedPlace:
    new_visited = VisitedPlace(**visited_data)
    db.add(new_visited)
    await db.commit()
    await db.refresh(new_visited)
    return new_visited

async def get_user_visited_places(
    db: AsyncSession,
    user_id: int
) -> list[VisitedPlace]:
    result = await db.execute(
        select(VisitedPlace)
        .where(VisitedPlace.user_id == user_id)
    )
    return result.scalars().all()


async def check_visited_place(
    db: AsyncSession,
    user_id: int,
    place_id: int
) -> bool:
    query = select(VisitedPlace).where(
        (VisitedPlace.user_id == user_id) &
        (VisitedPlace.place_id == place_id)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none() is not None



