from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class PrestartChecklist(Base):
    __tablename__ = "prestart_checklists"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"), unique=True)
    equipment_id: Mapped[int | None] = mapped_column(ForeignKey("equipment.id"))

    checklist_items: Mapped[dict | None] = mapped_column(JSON)  # [{item, checked, notes}, ...]
    overall_status: Mapped[str] = mapped_column(String(20), default="pass")  # pass, fail, conditional
    operator_name: Mapped[str | None] = mapped_column(String(100))
    failure_notes: Mapped[str | None] = mapped_column(String(500))

    report = relationship("Report", back_populates="prestart_checklist")
