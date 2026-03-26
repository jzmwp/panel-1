from sqlalchemy import String, Float, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class ShiftReport(Base):
    __tablename__ = "shift_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"), unique=True)

    # Production
    shears: Mapped[int | None] = mapped_column(Integer)
    metres: Mapped[float | None] = mapped_column(Float)
    tonnes: Mapped[float | None] = mapped_column(Float)

    # Delays
    delay_electrical_mins: Mapped[int | None] = mapped_column(Integer, default=0)
    delay_mechanical_mins: Mapped[int | None] = mapped_column(Integer, default=0)
    delay_operational_mins: Mapped[int | None] = mapped_column(Integer, default=0)
    delay_geological_mins: Mapped[int | None] = mapped_column(Integer, default=0)
    delay_other_mins: Mapped[int | None] = mapped_column(Integer, default=0)
    delay_notes: Mapped[str | None] = mapped_column(Text)

    # Equipment status
    shearer_status: Mapped[str | None] = mapped_column(String(50))
    afc_status: Mapped[str | None] = mapped_column(String(50))
    bsl_status: Mapped[str | None] = mapped_column(String(50))
    shields_status: Mapped[str | None] = mapped_column(String(50))

    # Handover
    handover_notes: Mapped[str | None] = mapped_column(Text)

    report = relationship("Report", back_populates="shift_report")
