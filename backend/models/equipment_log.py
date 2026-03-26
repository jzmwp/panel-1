from sqlalchemy import String, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class EquipmentLog(Base):
    __tablename__ = "equipment_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"), unique=True)
    equipment_id: Mapped[int | None] = mapped_column(ForeignKey("equipment.id"))

    log_type: Mapped[str] = mapped_column(String(30), nullable=False)  # breakdown, maintenance, repair, inspection
    description: Mapped[str] = mapped_column(Text, nullable=False)
    downtime_minutes: Mapped[int | None] = mapped_column(Integer, default=0)
    parts_used: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="open")  # open, in_progress, resolved

    report = relationship("Report", back_populates="equipment_log")
