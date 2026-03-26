from sqlalchemy import String, Float, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class GasReading(Base):
    __tablename__ = "gas_readings"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"))

    reading_type: Mapped[str] = mapped_column(String(20), nullable=False)  # spot, continuous, tube_bundle
    reading_location: Mapped[str | None] = mapped_column(String(100))

    ch4_percent: Mapped[float | None] = mapped_column(Float)
    co_ppm: Mapped[float | None] = mapped_column(Float)
    co2_percent: Mapped[float | None] = mapped_column(Float)
    o2_percent: Mapped[float | None] = mapped_column(Float)
    no2_ppm: Mapped[float | None] = mapped_column(Float)
    h2s_ppm: Mapped[float | None] = mapped_column(Float)

    ch4_exceedance: Mapped[bool | None] = mapped_column(Boolean, default=False)
    co_exceedance: Mapped[bool | None] = mapped_column(Boolean, default=False)
    o2_deficiency: Mapped[bool | None] = mapped_column(Boolean, default=False)

    report = relationship("Report", back_populates="gas_readings")
