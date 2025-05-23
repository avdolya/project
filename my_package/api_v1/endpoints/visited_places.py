from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request
from starlette.responses import HTMLResponse

from my_package.auth.utils import decode_jwt
from fastapi.templating import Jinja2Templates
from my_package.core.database import db_helper

from my_package.crud_package.user import get_user_by_name
from my_package.crud_package.visited_place import (
    create_visited_place,
    get_user_visited_places
)
templates = Jinja2Templates(directory="frontend/templates")
from my_package.api_v1.schemas.visited_place import (
    VisitedPlaceCreate,
    VisitedPlace,
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/jwt/login/")

router = APIRouter(prefix="/visited-places", tags=["Visited Places"])
async def get_db() -> AsyncSession:
    async with db_helper.session_factory() as session:
        yield session

@router.post("/")
async def add_visited_place(
        place_id: int = Form(...),
        db: AsyncSession = Depends(get_db),
        token: str = Depends(oauth2_scheme)
):
    print(token)
    try:
        payload = decode_jwt(token)
        username = payload.get("sub")
        user = await get_user_by_name(db, username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        exists = await db.execute(
            text("SELECT 1 FROM visited_places WHERE user_id=:uid AND place_id=:pid"),
            {"uid": user.id, "pid": place_id})
        if exists.scalar():
            return {"detail": "Место уже добавлено в посещенные!"}
        else:
            visited_data = VisitedPlaceCreate(
                user_id=user.id,
                place_id=place_id,
            )
        await create_visited_place(db, visited_data.dict())
        return {"detail": "Место успешно добавлено в посещенные!"}
    except HTTPException as he:
        raise he
    except Exception as e:
        print("Error:", str(e))  # Логирование ошибки
        raise


@router.get("/my-places", response_class=HTMLResponse)
async def get_my_visited_places(
        request: Request,
        db: AsyncSession = Depends(get_db),
        token: str = Depends(oauth2_scheme)
):
    try:
        payload = decode_jwt(token)
        username = payload.get("sub")
        user = await get_user_by_name(db, username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Получаем места с JOIN
        query = text("""
            SELECT p.id, p.name, p.average_rating, p.image_data 
            FROM visited_places vp
            JOIN places p ON vp.place_id = p.id
            WHERE vp.user_id = :user_id
        """)
        result = await db.execute(query, {"user_id": user.id})
        places = result.mappings().all()

        return templates.TemplateResponse(
            "/place_list.html",  # Ваш шаблон
            {
                "request": request,
                "places": places,
                "user": user
            }
        )
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")