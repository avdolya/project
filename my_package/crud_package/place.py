import secrets

import httpx
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




def load_secrets():
    secrets = {}
    try:
        with open('my_package/certs/.secret', 'r') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    secrets[key] = value
    except FileNotFoundError:
        pass
    return secrets


async def download_telegram_file(file_id: str) -> bytes:
    async with httpx.AsyncClient() as client:
        secrets = load_secrets()
        TELEGRAM_TOKEN = secrets.get('TELEGRAM_TOKEN')
        file_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}"
        file_path = (await client.get(file_url)).json()["result"]["file_path"]


        download_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
        response = await client.get(download_url)
        return response.content


async def get_all_places_for_assistant(
        db: AsyncSession,
        type: str,
        min_rating: float = 0.0,
) -> list[Place]:
    limit: int = 20
    query = (
        select(Place)
        .where(Place.type == type)
        .where(Place.average_rating >= min_rating)
        .order_by(Place.average_rating.desc())
        .limit(limit)
    )

    result = await db.execute(query)
    return list(result.scalars().all())





