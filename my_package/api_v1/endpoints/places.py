from fastapi import APIRouter, Depends, HTTPException, Request, Form, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import Response

from my_package.api_v1.schemas.place import Places, PlaceCreate
from my_package.core.database import db_helper
from pydantic import BaseModel
from typing import List, Optional
from my_package.crud_package.place import (
    create_place,
    get_place,
    get_all_places,
    update_place_rating
)
from my_package.core.models.place import Place

templates = Jinja2Templates(directory="frontend/templates")



router = APIRouter(prefix="/places", tags=["Places"])
async def get_db() -> AsyncSession:
    async with db_helper.session_factory() as session:
        yield session




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
    return await create_place(db, place_data.model_dump())





@router.get("/{place_id}", response_class=HTMLResponse)
async def read_place(
        request: Request,
        place_id: int,
        db: AsyncSession = Depends(get_db)
):
    db_place = await get_place(db, place_id)
    if not db_place:
        raise HTTPException(status_code=404, detail="Place not found")
    return templates.TemplateResponse(
        "place_card/place_card.html",  # Имя вашего шаблона
        {
            "request": request,
            "place": db_place,
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
    # Сортирует по рейтингу (order_by(Place.average_rating.desc())).
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
            "places": places,  # Переименовано в places для согласованности
            "pagination": pagination,
            "current_type": type  # Для сохранения фильтра в шаблоне
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
