from pydantic import BaseModel
from datetime import datetime


class VisitedPlaceBase(BaseModel):
    user_id: int
    place_id: int


class VisitedPlaceCreate(VisitedPlaceBase):
    pass


class VisitedPlace(VisitedPlaceBase):
    id: int
    visited_at: datetime

    class Config:
        orm_mode = True


