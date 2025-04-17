from typing import Annotated, Optional,List
from fastapi import APIRouter, Depends, HTTPException
from models import Place
from schemas import Places, PlaceCreate
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db

router = APIRouter(prefix="/places", tags=["Places"])

@router.post("/", response_model=Places)
async def add_place(place: Annotated[PlaceCreate, Depends()], db: Session = Depends(get_db)) -> Places:
    db_place = Place(name=place.name, description=place.description, type=place.type, created_at=datetime.utcnow())
    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    return db_place

@router.get("/", response_model=List[Places])
async def get_places(skip: int = 0, limit: int = 3, type: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Place) # запрос к бд
    result = []
    if type:
        query = query.filter(Place.type == type)

    # сортировка по рейтингу в порядке убывания
    query = query.order_by(Place.average_rating.desc())
    places = query.offset(skip).limit(limit).all() # offset(skip) пропуск определенного количества записей, limit лимит данных, all выводит все данные

    if not places:
        raise HTTPException(status_code=404, detail="Места не найдены")

    for place in places:
        result.append({"id": place.id,
                       "name": place.name,
                       "description": place.description,
                       "type": place.type,
                       "average_rating": place.average_rating,
                       "created_at": place.created_at
        })
    return result

@router.get("/{place_id}", response_model=Places)
async def get_place(place_id: int, db: Session = Depends(get_db)):
    place = db.query(Place).filter(Place.id == place_id).first()
    if place is None:
        raise HTTPException(status_code=404, detail="Place not found")
    return place