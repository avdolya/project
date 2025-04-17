from fastapi import APIRouter, Depends
from models import User
from users.schemas import Users, UserCreate
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from users.crud import create_user

router = APIRouter(prefix="/users",tags=["Users"])
@router.post("/", response_model=Users)
async def create_user(
        user: UserCreate,
        db: Session = Depends(get_db)) -> Users:
    return create_user(db=db, user_data=user)