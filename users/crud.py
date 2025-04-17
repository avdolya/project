from models import User
from sqlalchemy.orm import Session
from datetime import datetime
from users.schemas import Users, UserCreate

def create_user(db: Session, user_data: UserCreate) -> Users:
    db_user = User(
        name=user_data.name,
        email=user_data.email,
        role=user_data.role,
        password=user_data.password,
        created_at=datetime.utcnow())
    db.add(db_user) # Добавляем место в сессию
    db.commit()
    db.refresh(db_user)
    return db_user