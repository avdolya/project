from enum import Enum
from fastapi import APIRouter, Request, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from yandexgptlite import YandexGPTLite
from my_package.core.database import db_helper
from my_package.crud_package.place import get_all_places_for_assistant, load_secrets
secrets = load_secrets()
templates = Jinja2Templates(directory="frontend/templates")
YANDEX_FOLDER_ID = secrets.get('YANDEX_FOLDER_ID')
YANDEX_API_KEY = secrets.get('YANDEX_API_KEY')
account= YandexGPTLite(YANDEX_FOLDER_ID, YANDEX_API_KEY)
router = APIRouter(prefix="/assistant", tags=["Assistant"])
async def get_db() -> AsyncSession:
    async with db_helper.session_factory() as session:
        yield session



CATEGORY_TRANSLATION = {
    "walk": "Прогулки",
    "theatre": "Театры",
    "museum": "Музеи",
    "food": "Рестораны"
}


@router.get("/recommend")
async def assistant_recommend(
        request: Request,
        type: str = Query(...),
        db: AsyncSession = Depends(get_db)
):
    places = await get_all_places_for_assistant(
        db,
        type,
        min_rating = 0.0,
    )

    if not places:
        return 'Мест по этой категории не найдено'

    places_info = "\n".join(
        [f"{p.id}: {p.name} (Рейтинг: {p.average_rating}) - {p.description[:100]}..."
         for p in places]
    )


    prompt = (
        f"Пользователь хочет посетить место в категории '{type}'. "
        f"Вот список мест с их ID, названиями и рейтингом:\n{places_info}\n\n"
        "Выбери ОДНО самое подходящее место для рекомендации обычному туристу. "
        "Ответь ТОЛЬКО ID этого места без каких-либо дополнительных слов."
    )


    try:
        gpt_response = account.create_completion(
            prompt,
            '0.6'
        )
        print(f"YandexGPT response: {gpt_response}")
        place_id = int(gpt_response.strip())
    except (ValueError, TypeError):
        place_id = places[0].id

    recommended_place = next((p for p in places if p.id == place_id), places[0])
    place_url = f"http://localhost:8000/places/{place_id}"
    russian_type = CATEGORY_TRANSLATION.get(type, type)

    description_prompt = (
        f"Создай краткое, увлекательное описание места '{recommended_place.name}' "
        f"для туриста. Основные особенности: {recommended_place.description[:200]}"
    )


    place_description = account.create_completion(
        description_prompt,
        '0.6'
    )


    html_content = f"""
        <div class="recommendation">
            <p style = "margin-top: 10px">В категории {russian_type} я рекомендую посетить:</p>
            <p>🏆 <strong>{recommended_place.name}</strong></p>
            <p>⭐ Рейтинг: {recommended_place.average_rating}</p>
            <div class="description">{place_description}</div>
            <a href="{place_url}" class="cta-btn">
                Перейти к месту
            </a>
        </div>
        """

    return HTMLResponse(html_content)
