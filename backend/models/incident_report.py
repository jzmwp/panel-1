from sqlalchemy import String, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class IncidentReport(Base):
    __tablename__ = "incident_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"), unique=True)

    incident_type: Mapped[str] = mapped_column(String(50), nullable=False)  # injury, near_miss, dangerous_occurrence, equipment_damage, environmental
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity_actual: Mapped[str] = mapped_column(String(20), nullable=False)  # none, minor, moderate, serious, fatal
    severity_potential: Mapped[str] = mapped_column(String(20), nullable=False)
    root_cause: Mapped[str | None] = mapped_column(Text)
    corrective_actions: Mapped[str | None] = mapped_column(Text)
    persons_involved: Mapped[str | None] = mapped_column(Text)
    notifiable: Mapped[bool] = mapped_column(Boolean, default=False)  # notifiable to regulator
    notifiable_details: Mapped[str | None] = mapped_column(Text)

    report = relationship("Report", back_populates="incident_report")
