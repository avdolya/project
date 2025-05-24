from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from my_package.auth.utils import decode_jwt
from my_package.core.database import db_helper
from my_package.crud_package.user import create_user, get_user, get_user_by_name
from my_package.api_v1.schemas.user import UserCreate, UsersResponse
templates = Jinja2Templates(directory="frontend/templates")
router = APIRouter(prefix="/users", tags=["Users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/jwt/login/")



async def get_db() -> AsyncSession:
    async with db_helper.session_factory() as session:
        yield session



@router.post("/", response_model=UsersResponse)
async def create_new_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    return await create_user(db, user_data.model_dump())



@router.get("/profile",response_class=HTMLResponse)
async def read_user(
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

        return templates.TemplateResponse(
            "/profile.html",  # Ваш шаблон
            {
                "request": request,
                "user": user
            }
        )
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")