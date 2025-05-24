from .base import Base
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Float, DateTime, LargeBinary


class Place(Base):
    __tablename__ = "places"
    name: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[str] = mapped_column(String(500))
    type: Mapped[str] = mapped_column(String(30))
    image_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    average_rating:  Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


