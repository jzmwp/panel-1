from sqlalchemy import String, Float, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class DeputyReport(Base):
    __tablename__ = "deputy_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"), unique=True)

    # Gas readings at inspection point
    ch4_general: Mapped[float | None] = mapped_column(Float)  # % methane general body
    ch4_face: Mapped[float | None] = mapped_column(Float)     # % methane at face
    co_reading: Mapped[float | None] = mapped_column(Float)   # ppm CO
    co2_reading: Mapped[float | None] = mapped_column(Float)  # % CO2
    o2_reading: Mapped[float | None] = mapped_column(Float)   # % O2

    # Conditions
    roof_condition: Mapped[str | None] = mapped_column(String(20))  # good, fair, poor
    rib_condition: Mapped[str | None] = mapped_column(String(20))
    floor_condition: Mapped[str | None] = mapped_column(String(20))

    # Ventilation
    ventilation_adequate: Mapped[bool | None] = mapped_column(Boolean)
    ventilation_notes: Mapped[str | None] = mapped_column(Text)

    # Production
    production_status: Mapped[str | None] = mapped_column(String(50))  # producing, standing, maintenance, travelling
    metres_advanced: Mapped[float | None] = mapped_column(Float)

    # Hazards and actions
    hazards_identified: Mapped[str | None] = mapped_column(Text)
    actions_taken: Mapped[str | None] = mapped_column(Text)
    further_actions_required: Mapped[str | None] = mapped_column(Text)

    # Statutory compliance
    inspection_compliant: Mapped[bool | None] = mapped_column(Boolean, default=True)
    non_compliance_details: Mapped[str | None] = mapped_column(Text)

    report = relationship("Report", back_populates="deputy_report")
