from fastapi import FastAPI, Depends,HTTPException
from typing import Optional, List, Annotated
from sqlalchemy.orm import Session
from models import Base, User, Place, Review, VisitedPlaces
from database import engine, session_local
from schemas import Reviews, ReviewCreate, VisitedPlaceCreate, VisitedPlace
from datetime import datetime
from sqlalchemy import func
import uvicorn
from database import get_db
from places_views import router as places_router
from users.views import router as users_router

app = FastAPI() # Создаем экземпляр приложения FastAPI
app.include_router(places_router)
app.include_router(users_router)
Base.metadata.create_all(bind=engine) # Создаем все таблицы в базе данных




# Cчитаем средний рейтинг
# Функция принимает идентификатор места и сессию базы данных
def calculate_average_rating(place_id: int, db: Session) -> float:
# query указывает, какие данные мы хотим извлечь из БД, func.avg(Review.rating) доступ к встроенный функциям sql, в данном случае для вычисления среднего значения
# Метод filter() фильтрует отзывы, чтобы оставить только те, которые относятся к конкретному месту, идентифицированному по `place_id`.
# scalar() выполняет запрос и возвращает единственное значение
    average_rating = db.query(func.avg(Review.rating)).filter(Review.place_id == place_id).scalar()
    return average_rating if average_rating is not None else 0.0


'''@app.post("/users/", response_model=Users)
async def create_user(user: Annotated[UserCreate, Depends()], db: Session = Depends(get_db)) -> Users:
    db_user = User(name=user.name, email=user.email, role=user.role, password=user.password, created_at=datetime.utcnow())
    db.add(db_user) # Добавляем место в сессию
    db.commit()
    db.refresh(db_user)
    return db_user'''




@app.post("/reviews/", response_model=Reviews)
async def add_review(review: Annotated[ReviewCreate, Depends()], db: Session = Depends(get_db)) -> Reviews:
    db_review = Review(user_id=review.user_id, place_id=review.place_id, rating=review.rating, comment=review.comment, created_at=datetime.utcnow())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
# Выполняет запрос к базе данных  получения объекта Place,
# соответствующего идентификатору места, указанному в отзыве.
# Метод first() возвращает первый найденный объект или None,
# если объект не найден.
    place = db.query(Place).filter(Place.id == review.place_id).first()
    place.average_rating = calculate_average_rating(review.place_id, db)
    db.commit()
    return db_review


@app.post("/visited_places/", response_model=VisitedPlace)
async def add_visited_place(visited_place: Annotated[VisitedPlaceCreate, Depends()], db: Session = Depends(get_db)) -> VisitedPlace:
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

@app.get("/")
def hello_index():
    return {
        "message": "Hello index!",
    }

if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)





