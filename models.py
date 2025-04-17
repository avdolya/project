from pydantic import BaseModel
from pydantic_settings import BaseSettings
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from database import Base
from pathlib import Path
'''BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "db. sqlite3"'''

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, nullable=False)
    password = Column(String)
    role = Column(String)
    created_at = Column(DateTime)


class Place(Base):
    __tablename__ = "places"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    type = Column(String)
    average_rating = Column(Float, default=0.0)
    created_at = Column(DateTime)


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    place_id = Column(Integer)
    rating = Column(Integer)
    comment = Column(String)
    created_at = Column(DateTime)


class VisitedPlaces(Base):
    __tablename__ = "visited_places"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    place_id = Column(Integer)
    visited_at = Column(DateTime)

'''class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"


class Settings(BaseSettings):
    api_v1_prefix: str = "/api/v1"
    db: DbSettings = DbSettings ()
    auth_jwt: AuthJWT = AuthJWT()
    # db_echo: bool = True
settings = Settings()'''




