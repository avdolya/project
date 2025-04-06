from fastapi import FastAPI, HTTPException, Path, Query, Body, Depends, APIRouter
from typing import Optional, List, Dict, Annotated
from sqlalchemy.orm import Session
from models import Base, User, Place, Review, VisitedPlaces
from database import engine, session_local
from schemas import UserCreate, Users, Places, PlaceCreate, Reviews, ReviewCreate, VisitedPlaceCreate, VisitedPlace
from datetime import datetime
from sqlalchemy import func




app = FastAPI()

Base.metadata.create_all(bind=engine)


def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()


def calculate_average_rating(place_id: int, db: Session) -> float:
    average_rating = db.query(func.avg(Review.rating)).filter(Review.place_id == place_id).scalar()
    return average_rating if average_rating is not None else 0.0



@app.post("/users/", response_model=Users)
async def create_user(user: UserCreate, db: Session = Depends(get_db)) -> Users:
    db_user = User(name=user.name, email=user.email, role=user.role, password=user.password, created_at=datetime.utcnow())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/places/", response_model=Places)
async def add_place(place: PlaceCreate, db: Session = Depends(get_db)) -> Places:
    db_place = Place(name=place.name, description=place.description, type=place.type, created_at=datetime.utcnow())
    db.add(db_place)
    db.commit()
    db.refresh(db_place)
    return db_place


@app.post("/reviews/", response_model=Reviews)
async def add_review(review: ReviewCreate, db: Session = Depends(get_db)) -> Reviews:
    db_review = Review(user_id=review.user_id, place_id=review.place_id, rating=review.rating, comment=review.comment, created_at=datetime.utcnow())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    place = db.query(Place).filter(Place.id == review.place_id).first()
    place.average_rating = calculate_average_rating(review.place_id, db)
    db.commit()
    return db_review

@app.get("/places/", response_model=List[Places])
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


@app.get("/places/{place_id}", response_model=Places)
async def get_place(place_id: int, db: Session = Depends(get_db)):
    place = db.query(Place).filter(Place.id == place_id).first()
    if place is None:
        raise HTTPException(status_code=404, detail="Place not found")
    return place

@app.post("/visited_places/", response_model=VisitedPlace)
async def add_visited_place(visited_place: VisitedPlaceCreate, db: Session = Depends(get_db)) -> VisitedPlace:
    db_visited_place = VisitedPlaces(user_id=visited_place.user_id, place_id=visited_place.place_id, visited_at=datetime.utcnow()
    )
    db.add(db_visited_place)
    db.commit()
    db.refresh(db_visited_place)
    return db_visited_place

@app.get("/users/{user_id}/visited_places", response_model=List[VisitedPlace])
async def get_visited_places(user_id: int, db: Session = Depends(get_db)):
    visited_places = db.query(VisitedPlaces).filter(VisitedPlaces.user_id == user_id).all()
    if not visited_places:
        raise HTTPException(status_code=404, detail="No visited places found for this user")
    return visited_places







