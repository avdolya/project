import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Form, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import Response
from yandexgptlite import YandexGPTLite
from my_package.api_v1.schemas.place import Places, PlaceCreate
from my_package.core.database import db_helper
from pydantic import BaseModel
import re
from typing import List, Optional
import logging
logger = logging.getLogger(__name__)


from my_package.crud_package.place import (
    create_place,
    get_place,
    get_all_places,
    update_place_rating, delete_place, download_telegram_file, load_secrets
)
from my_package.core.models.place import Place
from my_package.crud_package.review import get_reviews_by_place



secrets = load_secrets()

TELEGRAM_TOKEN = secrets.get('TELEGRAM_TOKEN')
YOUR_SERVER_URL = secrets.get('YOUR_SERVER_URL')
YANDEX_FOLDER_ID = secrets.get('YANDEX_FOLDER_ID')
YANDEX_API_KEY = secrets.get('YANDEX_API_KEY')
account= YandexGPTLite(YANDEX_FOLDER_ID, YANDEX_API_KEY)
templates = Jinja2Templates(directory="frontend/templates")



router = APIRouter(prefix="/places", tags=["Places"])
async def get_db() -> AsyncSession:
    async with db_helper.session_factory() as session:
        yield session


@router.get("/set-webhook")
async def set_webhook():
    async with httpx.AsyncClient() as client:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={YOUR_SERVER_URL}/places/telegram-webhook"
        response = await client.get(url)
    return response.json()

@router.post("/telegram-webhook")
async def telegram_webhook(
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    try:
        data = await request.json()
        if "message" not in data:
            return {"status": "ignored", "reason": "not a message"}
        message = data.get("message", {})
        text = message.get("caption", "")


        # Парсинг текста
        name_match = re.search(r"Название:\s*(.*)", text)
        desc_match = re.search(r"Описание:\s*(.*)", text)
        type_match = re.search(r"Тип:\s*(.*)", text)
        print(name_match)
        print(desc_match)
        print(type_match)
        print(message)
        print(text)


        file_id = message["photo"][-1]["file_id"]
        image_data = await download_telegram_file(file_id)
        mapping_dict = {
            'музей': 'museum',
            'ресторан': 'food',
            'прогулка': 'walk',
            'театр': 'theatre',
        }
        type = mapping_dict.get(type_match.group(1).strip().lower())
        place_data = PlaceCreate(
            name = name_match.group(1).strip(),
            description = desc_match.group(1).strip(),
            type = type,
            image_data = image_data  # bytes или None
        )
        await create_place(db, place_data.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




@router.post("/", response_model=Places)
async def create_new_place(
    name: str = Form(...),
    description: str = Form(...),
    type: str = Form(...),
    image_data: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    image_bytes = await image_data.read()
    place_data = PlaceCreate(
        name=name,
        description=description,
        type=type,
        image_data=image_bytes,
    )
    new_place = await create_place(db, place_data.dict())






@router.get("/{place_id}", response_class=HTMLResponse)
async def read_place(
        request: Request,
        place_id: int,
        db: AsyncSession = Depends(get_db)
):
    reviews = await get_reviews_by_place(db, place_id)
    db_place = await get_place(db, place_id)
    if not reviews:
        summary = "Отзывов еще нет!"
    else:
        comments = " ".join(review.comment for review in reviews)
        summary = account.create_completion(
            comments,
            '0.6',
            system_prompt='распиши основные плюсы и минусы, выделив ключевые позиции отзывов, напиши не больше 5 пунктов для плюсов и минусов по отдельности если нет отзывов напиши: отзывов еще нет!'
        )
    if not db_place:
        raise HTTPException(status_code=404, detail="Place not found")
    return templates.TemplateResponse(
        "place_card/place_card.html",
        {
            "request": request,
            "place": db_place,
            "reviews": reviews,
            "summary": summary,
        }
    )




@router.get("/", response_class=HTMLResponse, name="list_places")
async def read_places(
        request: Request,
        type: str = Query(..., description="Тип места (museum, cafe, etc)"),
        page: int = Query(1, ge=1),
        page_size: int = Query(2, ge=1, le=15),
        db: AsyncSession = Depends(get_db)
):
    skip = (page - 1) * page_size
    # вызов CRUD-функции get_all_places, которая
    # фильтрует места по type (если передан).
    # сортирует по рейтингу (order_by(Place.average_rating.desc())).
    # применяет пагинацию

    places, total = await get_all_places(db, skip, page_size, type, return_total=True)
    pagination = {
        "current_page": page,
        "total_pages": (total + page_size - 1) // page_size,
        "has_prev": page > 1,
        "has_next": (page * page_size) < total
    }

    template_map = {
        "walk": "places_in_list/walk.html",
        "museum": "places_in_list/museums.html",
        "food": "places_in_list/food.html",
        "theatre": "places_in_list/theatres.html"
    }
    template_name = template_map.get(type, "/base.html")
    return templates.TemplateResponse(
        template_name,
        {
            "request": request,
            "places": places,
            "pagination": pagination,
            "current_type": type
        }
    )

@router.get("/{place_id}/image")
async def get_place_image(
    place_id: int,
    db: AsyncSession = Depends(get_db)
):
    place = await get_place(db, place_id)
    if not place or not place.image_data:
        raise HTTPException(status_code=404)
    return Response(
        content=place.image_data,
        media_type="image/jpeg",
        headers={"Content-Disposition": f"inline; filename={place.id}.jpg"})


@router.delete("/{place_id}")
async def delete_place_endpoint(
    place_id: int,
    db: AsyncSession = Depends(get_db)
):
    success = await delete_place(db, place_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Place not found or you don't have permissions"
        )

    return {"status": "success"}

