from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from backend.database import get_db
from backend.models import (
    Report, DeputyReport, ShiftReport, HazardReport,
    VentilationReading, StrataAssessment, GasReading,
    EquipmentLog, IncidentReport, TarpActivation, PrestartChecklist,
    Location, Personnel, Equipment,
)
from backend.schemas.report import (
    ReportCreate, ReportOut, ReportListOut,
    LocationCreate, LocationOut,
    PersonnelCreate, PersonnelOut,
    EquipmentCreate, EquipmentOut,
)

router = APIRouter(prefix="/api", tags=["reports"])

# Mapping from report_type to sub-model class and relationship attribute
SUB_MODEL_MAP = {
    "deputy": (DeputyReport, "deputy_report"),
    "shift": (ShiftReport, "shift_report"),
    "hazard": (HazardReport, "hazard_report"),
    "ventilation": (VentilationReading, "ventilation_readings"),
    "strata": (StrataAssessment, "strata_assessment"),
    "gas": (GasReading, "gas_readings"),
    "equipment_log": (EquipmentLog, "equipment_log"),
    "incident": (IncidentReport, "incident_report"),
    "tarp": (TarpActivation, "tarp_activation"),
    "prestart": (PrestartChecklist, "prestart_checklist"),
}


def _eager_load(query):
    return query.options(
        joinedload(Report.deputy_report),
        joinedload(Report.shift_report),
        joinedload(Report.hazard_report),
        joinedload(Report.ventilation_readings),
        joinedload(Report.strata_assessment),
        joinedload(Report.gas_readings),
        joinedload(Report.equipment_log),
        joinedload(Report.incident_report),
        joinedload(Report.tarp_activation),
        joinedload(Report.prestart_checklist),
    )


# --- Reports CRUD ---

@router.post("/reports", response_model=ReportOut, status_code=201)
def create_report(data: ReportCreate, db: Session = Depends(get_db)):
    report = Report(
        report_type=data.report_type,
        report_date=data.report_date,
        shift=data.shift,
        location_id=data.location_id,
        panel=data.panel,
        submitted_by=data.submitted_by,
        notes=data.notes,
    )
    db.add(report)
    db.flush()  # get report.id

    # Create sub-report based on type
    sub_data_map = {
        "deputy": (DeputyReport, data.deputy_report),
        "shift": (ShiftReport, data.shift_report),
        "hazard": (HazardReport, data.hazard_report),
        "strata": (StrataAssessment, data.strata_assessment),
        "equipment_log": (EquipmentLog, data.equipment_log),
        "incident": (IncidentReport, data.incident_report),
        "tarp": (TarpActivation, data.tarp_activation),
        "prestart": (PrestartChecklist, data.prestart_checklist),
    }

    if data.report_type in sub_data_map:
        model_cls, sub_data = sub_data_map[data.report_type]
        if sub_data:
            sub = model_cls(report_id=report.id, **sub_data.model_dump())
            db.add(sub)

    # Handle list-type sub-reports
    if data.report_type == "ventilation" and data.ventilation_readings:
        for vr in data.ventilation_readings:
            db.add(VentilationReading(report_id=report.id, **vr.model_dump()))

    if data.report_type == "gas" and data.gas_readings:
        for gr in data.gas_readings:
            db.add(GasReading(report_id=report.id, **gr.model_dump()))

    db.commit()
    db.refresh(report)
    return _eager_load(db.query(Report).filter(Report.id == report.id)).first()


@router.get("/reports", response_model=list[ReportListOut])
def list_reports(
    report_type: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    panel: str | None = None,
    shift: str | None = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    q = db.query(Report)
    if report_type:
        q = q.filter(Report.report_type == report_type)
    if date_from:
        q = q.filter(Report.report_date >= date_from)
    if date_to:
        q = q.filter(Report.report_date <= date_to)
    if panel:
        q = q.filter(Report.panel == panel)
    if shift:
        q = q.filter(Report.shift == shift)
    return q.order_by(Report.report_date.desc(), Report.id.desc()).offset(offset).limit(limit).all()


@router.get("/reports/{report_id}", response_model=ReportOut)
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = _eager_load(db.query(Report).filter(Report.id == report_id)).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.delete("/reports/{report_id}", status_code=204)
def delete_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    db.delete(report)
    db.commit()


# --- Locations ---

@router.post("/locations", response_model=LocationOut, status_code=201)
def create_location(data: LocationCreate, db: Session = Depends(get_db)):
    loc = Location(**data.model_dump())
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return loc


@router.get("/locations", response_model=list[LocationOut])
def list_locations(db: Session = Depends(get_db)):
    return db.query(Location).filter(Location.is_active).all()


# --- Personnel ---

@router.post("/personnel", response_model=PersonnelOut, status_code=201)
def create_personnel(data: PersonnelCreate, db: Session = Depends(get_db)):
    person = Personnel(**data.model_dump())
    db.add(person)
    db.commit()
    db.refresh(person)
    return person


@router.get("/personnel", response_model=list[PersonnelOut])
def list_personnel(db: Session = Depends(get_db)):
    return db.query(Personnel).filter(Personnel.is_active).all()


# --- Equipment ---

@router.post("/equipment", response_model=EquipmentOut, status_code=201)
def create_equipment(data: EquipmentCreate, db: Session = Depends(get_db)):
    equip = Equipment(**data.model_dump())
    db.add(equip)
    db.commit()
    db.refresh(equip)
    return equip


@router.get("/equipment", response_model=list[EquipmentOut])
def list_equipment(db: Session = Depends(get_db)):
    return db.query(Equipment).filter(Equipment.is_active).all()
