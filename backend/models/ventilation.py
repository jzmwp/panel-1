from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class VentilationReading(Base):
    __tablename__ = "ventilation_readings"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_id: Mapped[int] = mapped_column(ForeignKey("reports.id", ondelete="CASCADE"))

    reading_location: Mapped[str | None] = mapped_column(String(100))
    air_velocity: Mapped[float | None] = mapped_column(Float)      # m/s
    air_quantity: Mapped[float | None] = mapped_column(Float)       # m³/s
    dry_bulb_temp: Mapped[float | None] = mapped_column(Float)     # °C
    wet_bulb_temp: Mapped[float | None] = mapped_column(Float)     # °C
    dust_reading: Mapped[float | None] = mapped_column(Float)      # mg/m³
    differential_pressure: Mapped[float | None] = mapped_column(Float)  # Pa

    report = relationship("Report", back_populates="ventilation_readings")
