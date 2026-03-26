from sqlalchemy import String, Float, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class TarpActivation(Base):
    __tablename__ = "tarp_activations"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"), unique=True)

    tarp_type: Mapped[str] = mapped_column(String(50), nullable=False)  # gas, strata, ventilation, outburst, spontaneous_combustion
    trigger_level: Mapped[str] = mapped_column(String(10), nullable=False)  # green, amber, red
    trigger_value: Mapped[float | None] = mapped_column(Float)
    trigger_description: Mapped[str | None] = mapped_column(Text)
    response_actions: Mapped[str] = mapped_column(Text, nullable=False)
    escalated: Mapped[bool | None] = mapped_column(default=False)
    resolved: Mapped[bool | None] = mapped_column(default=False)
    resolution_notes: Mapped[str | None] = mapped_column(Text)

    report = relationship("Report", back_populates="tarp_activation")
