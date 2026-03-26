from sqlalchemy import String, Float, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class StrataAssessment(Base):
    __tablename__ = "strata_assessments"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"), unique=True)

    convergence_reading: Mapped[float | None] = mapped_column(Float)   # mm
    convergence_rate: Mapped[float | None] = mapped_column(Float)      # mm/day
    roof_condition: Mapped[str | None] = mapped_column(String(20))     # good, fair, poor
    rib_condition: Mapped[str | None] = mapped_column(String(20))
    floor_condition: Mapped[str | None] = mapped_column(String(20))
    faulting_present: Mapped[bool | None] = mapped_column(Boolean, default=False)
    faulting_details: Mapped[str | None] = mapped_column(Text)
    support_condition: Mapped[str | None] = mapped_column(String(50))  # adequate, additional_required, damaged
    tarp_level: Mapped[str | None] = mapped_column(String(10))         # green, amber, red
    notes: Mapped[str | None] = mapped_column(Text)

    report = relationship("Report", back_populates="strata_assessment")
