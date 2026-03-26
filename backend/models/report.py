from datetime import date

from sqlalchemy import String, Date, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.models.base import TimestampMixin


class Report(TimestampMixin, Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    report_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    shift: Mapped[str] = mapped_column(String(20), nullable=False)  # day, afternoon, night
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"))
    panel: Mapped[str | None] = mapped_column(String(50))
    submitted_by: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)

    location = relationship("Location", back_populates="reports")
    deputy_report = relationship("DeputyReport", back_populates="report", uselist=False, cascade="all, delete-orphan")
    shift_report = relationship("ShiftReport", back_populates="report", uselist=False, cascade="all, delete-orphan")
    hazard_report = relationship("HazardReport", back_populates="report", uselist=False, cascade="all, delete-orphan")
    ventilation_readings = relationship("VentilationReading", back_populates="report", cascade="all, delete-orphan")
    strata_assessment = relationship("StrataAssessment", back_populates="report", uselist=False, cascade="all, delete-orphan")
    gas_readings = relationship("GasReading", back_populates="report", cascade="all, delete-orphan")
    equipment_log = relationship("EquipmentLog", back_populates="report", uselist=False, cascade="all, delete-orphan")
    incident_report = relationship("IncidentReport", back_populates="report", uselist=False, cascade="all, delete-orphan")
    tarp_activation = relationship("TarpActivation", back_populates="report", uselist=False, cascade="all, delete-orphan")
    prestart_checklist = relationship("PrestartChecklist", back_populates="report", uselist=False, cascade="all, delete-orphan")
