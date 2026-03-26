from datetime import date, datetime
from pydantic import BaseModel


# --- Location ---
class LocationBase(BaseModel):
    name: str
    location_type: str
    panel: str | None = None
    chainage_from: float | None = None
    chainage_to: float | None = None

class LocationCreate(LocationBase):
    pass

class LocationOut(LocationBase):
    id: int
    is_active: bool
    model_config = {"from_attributes": True}


# --- Personnel ---
class PersonnelBase(BaseModel):
    name: str
    role: str
    employee_id: str | None = None

class PersonnelCreate(PersonnelBase):
    pass

class PersonnelOut(PersonnelBase):
    id: int
    is_active: bool
    model_config = {"from_attributes": True}


# --- Equipment ---
class EquipmentBase(BaseModel):
    name: str
    equipment_type: str
    asset_number: str | None = None

class EquipmentCreate(EquipmentBase):
    pass

class EquipmentOut(EquipmentBase):
    id: int
    is_active: bool
    model_config = {"from_attributes": True}


# --- Deputy Report ---
class DeputyReportData(BaseModel):
    ch4_general: float | None = None
    ch4_face: float | None = None
    co_reading: float | None = None
    co2_reading: float | None = None
    o2_reading: float | None = None
    roof_condition: str | None = None
    rib_condition: str | None = None
    floor_condition: str | None = None
    ventilation_adequate: bool | None = None
    ventilation_notes: str | None = None
    production_status: str | None = None
    metres_advanced: float | None = None
    hazards_identified: str | None = None
    actions_taken: str | None = None
    further_actions_required: str | None = None
    inspection_compliant: bool | None = True
    non_compliance_details: str | None = None

class DeputyReportOut(DeputyReportData):
    id: int
    report_id: int
    model_config = {"from_attributes": True}


# --- Shift Report ---
class ShiftReportData(BaseModel):
    shears: int | None = None
    metres: float | None = None
    tonnes: float | None = None
    delay_electrical_mins: int | None = 0
    delay_mechanical_mins: int | None = 0
    delay_operational_mins: int | None = 0
    delay_geological_mins: int | None = 0
    delay_other_mins: int | None = 0
    delay_notes: str | None = None
    shearer_status: str | None = None
    afc_status: str | None = None
    bsl_status: str | None = None
    shields_status: str | None = None
    handover_notes: str | None = None

class ShiftReportOut(ShiftReportData):
    id: int
    report_id: int
    model_config = {"from_attributes": True}


# --- Hazard Report ---
class HazardReportData(BaseModel):
    hazard_type: str
    description: str
    severity: str
    likelihood: str
    risk_rating: str | None = None
    initial_actions: str | None = None
    corrective_actions: str | None = None
    status: str = "open"

class HazardReportOut(HazardReportData):
    id: int
    report_id: int
    model_config = {"from_attributes": True}


# --- Ventilation Reading ---
class VentilationReadingData(BaseModel):
    reading_location: str | None = None
    air_velocity: float | None = None
    air_quantity: float | None = None
    dry_bulb_temp: float | None = None
    wet_bulb_temp: float | None = None
    dust_reading: float | None = None
    differential_pressure: float | None = None

class VentilationReadingOut(VentilationReadingData):
    id: int
    report_id: int
    model_config = {"from_attributes": True}


# --- Strata Assessment ---
class StrataAssessmentData(BaseModel):
    convergence_reading: float | None = None
    convergence_rate: float | None = None
    roof_condition: str | None = None
    rib_condition: str | None = None
    floor_condition: str | None = None
    faulting_present: bool | None = False
    faulting_details: str | None = None
    support_condition: str | None = None
    tarp_level: str | None = None
    notes: str | None = None

class StrataAssessmentOut(StrataAssessmentData):
    id: int
    report_id: int
    model_config = {"from_attributes": True}


# --- Gas Reading ---
class GasReadingData(BaseModel):
    reading_type: str
    reading_location: str | None = None
    ch4_percent: float | None = None
    co_ppm: float | None = None
    co2_percent: float | None = None
    o2_percent: float | None = None
    no2_ppm: float | None = None
    h2s_ppm: float | None = None
    ch4_exceedance: bool | None = False
    co_exceedance: bool | None = False
    o2_deficiency: bool | None = False

class GasReadingOut(GasReadingData):
    id: int
    report_id: int
    model_config = {"from_attributes": True}


# --- Equipment Log ---
class EquipmentLogData(BaseModel):
    equipment_id: int | None = None
    log_type: str
    description: str
    downtime_minutes: int | None = 0
    parts_used: str | None = None
    status: str = "open"

class EquipmentLogOut(EquipmentLogData):
    id: int
    report_id: int
    model_config = {"from_attributes": True}


# --- Incident Report ---
class IncidentReportData(BaseModel):
    incident_type: str
    description: str
    severity_actual: str
    severity_potential: str
    root_cause: str | None = None
    corrective_actions: str | None = None
    persons_involved: str | None = None
    notifiable: bool = False
    notifiable_details: str | None = None

class IncidentReportOut(IncidentReportData):
    id: int
    report_id: int
    model_config = {"from_attributes": True}


# --- TARP Activation ---
class TarpActivationData(BaseModel):
    tarp_type: str
    trigger_level: str
    trigger_value: float | None = None
    trigger_description: str | None = None
    response_actions: str
    escalated: bool | None = False
    resolved: bool | None = False
    resolution_notes: str | None = None

class TarpActivationOut(TarpActivationData):
    id: int
    report_id: int
    model_config = {"from_attributes": True}


# --- Prestart Checklist ---
class PrestartChecklistData(BaseModel):
    equipment_id: int | None = None
    checklist_items: dict | None = None
    overall_status: str = "pass"
    operator_name: str | None = None
    failure_notes: str | None = None

class PrestartChecklistOut(PrestartChecklistData):
    id: int
    report_id: int
    model_config = {"from_attributes": True}


# --- Report (parent) ---
class ReportBase(BaseModel):
    report_type: str
    report_date: date
    shift: str
    location_id: int | None = None
    panel: str | None = None
    submitted_by: str | None = None
    notes: str | None = None

class ReportCreate(ReportBase):
    deputy_report: DeputyReportData | None = None
    shift_report: ShiftReportData | None = None
    hazard_report: HazardReportData | None = None
    ventilation_readings: list[VentilationReadingData] | None = None
    strata_assessment: StrataAssessmentData | None = None
    gas_readings: list[GasReadingData] | None = None
    equipment_log: EquipmentLogData | None = None
    incident_report: IncidentReportData | None = None
    tarp_activation: TarpActivationData | None = None
    prestart_checklist: PrestartChecklistData | None = None

class ReportOut(ReportBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deputy_report: DeputyReportOut | None = None
    shift_report: ShiftReportOut | None = None
    hazard_report: HazardReportOut | None = None
    ventilation_readings: list[VentilationReadingOut] | None = None
    strata_assessment: StrataAssessmentOut | None = None
    gas_readings: list[GasReadingOut] | None = None
    equipment_log: EquipmentLogOut | None = None
    incident_report: IncidentReportOut | None = None
    tarp_activation: TarpActivationOut | None = None
    prestart_checklist: PrestartChecklistOut | None = None
    model_config = {"from_attributes": True}

class ReportListOut(ReportBase):
    id: int
    created_at: datetime
    model_config = {"from_attributes": True}
