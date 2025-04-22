from .base import Base
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime,Integer

class VisitedPlace(Base):
    __tablename__ = "visited_places"
    user_id: Mapped[int] = mapped_column(Integer)
    place_id: Mapped[int] = mapped_column(Integer)
    visited_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)



