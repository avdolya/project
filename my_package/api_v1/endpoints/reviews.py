from fastapi import APIRouter, Form, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from my_package.api_v1.schemas.review import ReviewCreate, Reviews
from my_package.auth.utils import decode_jwt
from my_package.core.database import db_helper
from my_package.crud_package.place import update_place_rating
from my_package.crud_package.user import get_user_by_name
from my_package.crud_package.visited_place import check_visited_place
from my_package.crud_package.review import create_review, delete_review, get_reviews_by_place

templates = Jinja2Templates(directory="frontend/templates")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/jwt/login/")
router = APIRouter(prefix="/reviews", tags=["Reviews"])
async def get_db() -> AsyncSession:
    async with db_helper.session_factory() as session:
        yield session

@router.post("/{place_id}/reviews")
async def add_review(
        place_id: int,
        rating: float = Form(...),
        comment: str = Form(...),
        db: AsyncSession = Depends(get_db),
        token: str = Depends(oauth2_scheme)
):

    try:
        payload = decode_jwt(token)
        username = payload.get("sub")
        user = await get_user_by_name(db, username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not await check_visited_place(db, user.id, place_id):
            return "Вы не можете оставить отзыв, так как не посещали это место"
        review_data = ReviewCreate(
            user_id=user.id,
            place_id=place_id,
            rating=rating,
            comment=comment,
        )
        new_review = await create_review(db, review_data.dict())
        await update_place_rating(db, place_id)
        return "Отзыв успешно добавлен"
    except HTTPException as he:
        raise he
    except Exception as e:
        raise


@router.delete("/{review_id}")
async def delete_review_endpoint(
    review_id: int,
    db: AsyncSession = Depends(get_db)
):
    success = await delete_review(db, review_id)
    if not success:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": "Review deleted"}




@router.get("/places/{place_id}", response_model=list[Reviews])
async def get_my_visited_places(
        place_id: int,
        db: AsyncSession = Depends(get_db)
):
    reviews = await get_reviews_by_place(db, place_id)
    if not reviews:
        raise HTTPException(status_code=404, detail="Review not found")
    return reviews

