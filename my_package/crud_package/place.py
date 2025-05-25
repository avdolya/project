from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from my_package.api_v1.endpoints import places
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
        page: int = 0,
        page_size: int = 2,
        type: str | None = None,
        return_total: bool = False
) -> list[Place] | tuple[list[Place], int]:
    # запрос для выбора всех записей из таблицы Place,
    # отсортированных по полю average_rating в порядке
    # убывания
    query = select(Place).order_by(Place.average_rating.desc())
    # если задан фильтр
    if type:
        query = query.where(Place.type == type)
    #  Метод execute выполняет запрос, при этом используется метод
    #  offset(skip) для пропуска первых skip записей
    #  и limit(limit) для ограничения количества
    #  возвращаемых записей до limit.
    result = await db.execute(query.offset(page).limit(page_size))
    places = list(result.scalars().all())
    if return_total:
        total_query = select(func.count(Place.id))
        if type:
            total_query = total_query.where(Place.type == type)
        total = (await db.execute(total_query)).scalar()
        return places, total

    return places


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

async def delete_place(db: AsyncSession, place_id: int) -> bool:
    result = await db.execute(
        select(Place)
        .where(Place.id == place_id)
    )
    place = result.scalar_one_or_none()

    if not place:
        return False

    await db.delete(place)
    await db.commit()
    return True


