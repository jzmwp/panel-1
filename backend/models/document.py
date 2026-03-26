from sqlalchemy import String, Float, Text, Integer, Date, JSON
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base
from backend.models.base import TimestampMixin

from datetime import date


class Document(TimestampMixin, Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    filepath: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str | None] = mapped_column(String(20))

    # Classification (set by Claude)
    report_category: Mapped[str | None] = mapped_column(String(100), index=True)  # e.g. "shift_statutory_report", "longwall_production", "strata_assessment"

    # Common fields pulled out for fast filtering
    report_date: Mapped[date | None] = mapped_column(Date, index=True)
    shift: Mapped[str | None] = mapped_column(String(20))
    panel: Mapped[str | None] = mapped_column(String(50))
    submitted_by: Mapped[str | None] = mapped_column(String(100))

    # The flexible payload — everything Claude extracted
    extracted_data: Mapped[dict | None] = mapped_column(JSON)
    raw_text: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[float | None] = mapped_column(Float)

    status: Mapped[str] = mapped_column(String(20), default="uploaded")  # uploaded, processing, processed, reviewed
