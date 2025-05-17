from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import base64

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


class PlacesResponse(BaseModel):
    data: List[Places]
    meta: dict


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





@router.get("/{place_id}", response_model=Places)
async def read_place(
    place_id: int,
    db: AsyncSession = Depends(get_db)
):
    db_place = await get_place(db, place_id)
    if not db_place:
        raise HTTPException(status_code=404, detail="Place not found")
    return db_place




@router.get("/", response_model=PlacesResponse)
async def read_places(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=15),
    type: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    skip = (page - 1) * page_size
    # вызов CRUD-функции get_all_places, которая
    # фильтрует места по type (если передан).
    # Сортирует по рейтингу (order_by(Place.average_rating.desc())).
    # применяет пагинацию

    places, total = await get_all_places(db, skip, page_size, type, return_total=True)
    encoded_places = []
    for place in places:
        encoded_places.append({
            "id": place.id,
            "name": place.name.encode('utf-8').decode('utf-8'),
            "description": place.description.encode('utf-8').decode('utf-8'),
            "type": place.type.encode('utf-8').decode('utf-8'),
            "average_rating": place.average_rating,
            "created_at": place.created_at
        })

    return JSONResponse(
        content={
            "data": jsonable_encoder(encoded_places),
            "meta": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "has_next": (page * page_size) < total
            }
        },
        media_type="application/json; charset=utf-8"
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
