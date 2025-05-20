from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import RedirectResponse, HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from my_package.core.database import db_helper
from my_package.auth.utils import decode_jwt
from fastapi.templating import Jinja2Templates
from my_package.crud_package.review import create_review, get_reviews_by_place, delete_review
from my_package.crud_package.place import update_place_rating
from my_package.api_v1.schemas.review import ReviewCreate, Reviews
from my_package.crud_package.user import get_user_by_name
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/jwt/login/")
router = APIRouter(prefix="/reviews", tags=["Reviews"])

templates = Jinja2Templates(directory="frontend/templates")
async def get_db() -> AsyncSession:
    async with db_helper.session_factory() as session:
        yield session

@router.post("/{place_id}/reviews")
async def create_review(
        place_id: int,
        rating: int = Form(...),  # Базовые параметры
        comment: str = Form(...),
        db: AsyncSession = Depends(get_db),
        token: str = Depends(oauth2_scheme)

):
    payload = decode_jwt(token)
    username = payload.get("sub")
    user = await get_user_by_name(db, username)
    review_data = ReviewCreate(
        user_id= user.id,
        place_id=place_id,
        rating=rating,
        comment=comment
    )
    return await create_review(db, review_data.dict())




@router.get("/place/{place_id}", response_class=HTMLResponse)
async def get_reviews_for_place(
        request: Request,
        place_id: int,
        db: AsyncSession = Depends(get_db)
):
    reviews = await get_reviews_by_place(db, place_id)
    if not reviews:
        raise HTTPException(
            status_code=404,
            detail="No reviews found for this place"
        )
    return templates.TemplateResponse(
        "place_card/place_card.html",  # Имя вашего шаблона
        {
            "request": request,
            "review": reviews,
        }
    )

@router.delete("/{review_id}")
async def delete_review_endpoint(
    review_id: int,
    db: AsyncSession = Depends(get_db)
):
    success = await delete_review(db, review_id)
    if not success:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": "Review deleted"}

