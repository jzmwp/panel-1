from sqlalchemy import String, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.models.base import TimestampMixin


class Location(TimestampMixin, Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    location_type: Mapped[str] = mapped_column(String(50), nullable=False)  # panel, cut-through, gate, return, intake
    panel: Mapped[str | None] = mapped_column(String(50))
    chainage_from: Mapped[float | None] = mapped_column(Float)
    chainage_to: Mapped[float | None] = mapped_column(Float)
    is_active: Mapped[bool] = mapped_column(default=True)

    reports = relationship("Report", back_populates="location")
