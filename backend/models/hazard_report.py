from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class HazardReport(Base):
    __tablename__ = "hazard_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"), unique=True)

    hazard_type: Mapped[str] = mapped_column(String(50), nullable=False)  # strata, gas, electrical, mechanical, environmental, other
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)  # low, medium, high, critical
    likelihood: Mapped[str] = mapped_column(String(20), nullable=False)  # rare, unlikely, possible, likely, almost_certain
    risk_rating: Mapped[str | None] = mapped_column(String(20))  # low, medium, high, extreme
    initial_actions: Mapped[str | None] = mapped_column(Text)
    corrective_actions: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="open")  # open, in_progress, closed

    report = relationship("Report", back_populates="hazard_report")
