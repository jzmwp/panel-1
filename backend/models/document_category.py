from sqlalchemy import String, Integer, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base
from backend.models.base import TimestampMixin


class DocumentCategory(TimestampMixin, Base):
    __tablename__ = "document_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)  # e.g. "shift_statutory_report"
    label: Mapped[str] = mapped_column(String(200), nullable=False)  # e.g. "Shift Statutory Report"
    description: Mapped[str | None] = mapped_column(Text)
    field_schema: Mapped[dict] = mapped_column(JSON, nullable=False)  # canonical field definitions
    sample_count: Mapped[int] = mapped_column(Integer, default=0)
