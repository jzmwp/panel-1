"""Seed script — populates the database with realistic sample data for an underground coal mine."""

import random
from datetime import date, timedelta

from sqlalchemy.orm import Session

from backend.database import engine, Base, SessionLocal
from backend.models import (
    Location, Personnel, Equipment, Report,
    DeputyReport, ShiftReport, HazardReport,
    VentilationReading, StrataAssessment, GasReading,
    EquipmentLog, IncidentReport, TarpActivation,
)


def seed_locations(db: Session):
    locations = [
        Location(name="LW101 Maingate", location_type="gate", panel="LW101"),
        Location(name="LW101 Tailgate", location_type="gate", panel="LW101"),
        Location(name="LW101 Face", location_type="face", panel="LW101"),
        Location(name="LW101 MG Return", location_type="return", panel="LW101"),
        Location(name="LW101 TG Return", location_type="return", panel="LW101"),
        Location(name="CT1", location_type="cut-through", panel="LW101", chainage_from=0, chainage_to=100),
        Location(name="CT5", location_type="cut-through", panel="LW101", chainage_from=400, chainage_to=500),
        Location(name="CT10", location_type="cut-through", panel="LW101", chainage_from=900, chainage_to=1000),
        Location(name="CT15", location_type="cut-through", panel="LW101", chainage_from=1400, chainage_to=1500),
        Location(name="CT20", location_type="cut-through", panel="LW101", chainage_from=1900, chainage_to=2000),
        Location(name="Main Intake", location_type="intake", panel=None),
        Location(name="Main Return", location_type="return", panel=None),
        Location(name="Pit Bottom", location_type="other", panel=None),
    ]
    db.add_all(locations)
    db.commit()
    return {loc.name: loc.id for loc in locations}


def seed_personnel(db: Session):
    personnel = [
        Personnel(name="Dave Mitchell", role="deputy", employee_id="D001"),
        Personnel(name="Steve Rogers", role="deputy", employee_id="D002"),
        Personnel(name="Mark Thompson", role="deputy", employee_id="D003"),
        Personnel(name="Craig Williams", role="undermanager", employee_id="UM001"),
        Personnel(name="Paul Anderson", role="ssm", employee_id="SSM001"),
        Personnel(name="Jason Brown", role="operator", employee_id="OP001"),
        Personnel(name="Luke Harris", role="operator", employee_id="OP002"),
        Personnel(name="Nathan Clarke", role="operator", employee_id="OP003"),
        Personnel(name="Ben Walker", role="electrician", employee_id="E001"),
        Personnel(name="Tom Jenkins", role="fitter", employee_id="F001"),
    ]
    db.add_all(personnel)
    db.commit()


def seed_equipment(db: Session):
    equipment = [
        Equipment(name="JOY 7LS8 Shearer", equipment_type="shearer", asset_number="SH001"),
        Equipment(name="AFC PF6/1242", equipment_type="afc", asset_number="AFC001"),
        Equipment(name="BSL PF6/1242", equipment_type="bsl", asset_number="BSL001"),
        Equipment(name="Shields 1-180", equipment_type="shields", asset_number="SHD001"),
        Equipment(name="12CM30 Continuous Miner", equipment_type="continuous_miner", asset_number="CM001"),
        Equipment(name="Shuttle Car 1", equipment_type="shuttle_car", asset_number="SC001"),
        Equipment(name="Shuttle Car 2", equipment_type="shuttle_car", asset_number="SC002"),
        Equipment(name="LHD Wagner ST14", equipment_type="lhd", asset_number="LHD001"),
        Equipment(name="Auxiliary Fan", equipment_type="ventilation", asset_number="FAN001"),
        Equipment(name="Monorail", equipment_type="transport", asset_number="MR001"),
    ]
    db.add_all(equipment)
    db.commit()


def seed_deputy_reports(db: Session, loc_ids: dict, days: int = 30):
    """Generate deputy reports for the last N days."""
    deputies = ["Dave Mitchell", "Steve Rogers", "Mark Thompson"]
    shifts = ["day", "afternoon", "night"]
    locations = ["LW101 Maingate", "LW101 Tailgate", "LW101 Face"]
    conditions = ["good", "fair", "poor"]
    statuses = ["producing", "producing", "producing", "standing", "maintenance"]

    today = date.today()
    for day_offset in range(days):
        report_date = today - timedelta(days=day_offset)
        for shift in shifts:
            loc_name = random.choice(locations)
            deputy = random.choice(deputies)

            # Realistic gas readings with occasional spikes
            ch4_base = random.uniform(0.1, 0.6)
            ch4_spike = random.random() < 0.05  # 5% chance of elevated reading
            ch4_gen = ch4_base + (random.uniform(0.5, 1.2) if ch4_spike else 0)
            ch4_face = ch4_gen + random.uniform(0, 0.3)

            co_base = random.uniform(1, 15)
            co_spike = random.random() < 0.03
            co_val = co_base + (random.uniform(20, 40) if co_spike else 0)

            report = Report(
                report_type="deputy",
                report_date=report_date,
                shift=shift,
                location_id=loc_ids.get(loc_name),
                panel="LW101",
                submitted_by=deputy,
            )
            db.add(report)
            db.flush()

            roof = random.choice(conditions[:2])  # mostly good/fair
            if random.random() < 0.1:
                roof = "poor"

            deputy_data = DeputyReport(
                report_id=report.id,
                ch4_general=round(ch4_gen, 2),
                ch4_face=round(ch4_face, 2),
                co_reading=round(co_val, 1),
                co2_reading=round(random.uniform(0.05, 0.4), 2),
                o2_reading=round(random.uniform(19.8, 20.9), 1),
                roof_condition=roof,
                rib_condition=random.choice(conditions[:2]),
                floor_condition=random.choice(conditions[:2]),
                ventilation_adequate=random.random() > 0.05,
                production_status=random.choice(statuses),
                metres_advanced=round(random.uniform(0, 15), 1) if random.random() > 0.3 else 0,
                hazards_identified="Rib spall observed near shield 45" if random.random() < 0.15 else None,
                actions_taken="Area barricaded, rib bolts installed" if random.random() < 0.1 else None,
                inspection_compliant=random.random() > 0.02,
            )
            db.add(deputy_data)

    db.commit()


def seed_shift_reports(db: Session, loc_ids: dict, days: int = 30):
    """Generate shift production reports."""
    shifts = ["day", "afternoon", "night"]
    today = date.today()

    for day_offset in range(days):
        report_date = today - timedelta(days=day_offset)
        for shift in shifts:
            shears = random.randint(0, 12)
            metres = round(shears * random.uniform(3.0, 3.5), 1)
            tonnes = round(metres * random.uniform(800, 1200), 0)

            report = Report(
                report_type="shift",
                report_date=report_date,
                shift=shift,
                location_id=loc_ids.get("LW101 Face"),
                panel="LW101",
                submitted_by="Craig Williams",
            )
            db.add(report)
            db.flush()

            shift_data = ShiftReport(
                report_id=report.id,
                shears=shears,
                metres=metres,
                tonnes=tonnes,
                delay_electrical_mins=random.choice([0, 0, 0, 15, 30, 45, 60]),
                delay_mechanical_mins=random.choice([0, 0, 0, 20, 40, 60, 90, 120]),
                delay_operational_mins=random.choice([0, 0, 10, 20, 30]),
                delay_geological_mins=random.choice([0, 0, 0, 0, 30, 60]),
                shearer_status=random.choice(["operational", "operational", "operational", "minor fault"]),
                afc_status="operational",
                bsl_status="operational",
                shields_status=random.choice(["operational", "operational", "shield 82 slow"]),
                handover_notes="Face at ch." + str(random.randint(800, 1500)) + "m. " +
                               random.choice(["Good conditions.", "Watch rib line near TG.", "Shearer picks need changing.", "All good."]),
            )
            db.add(shift_data)

    db.commit()


def seed_gas_readings(db: Session, loc_ids: dict, days: int = 30):
    """Generate gas monitoring readings."""
    reading_locations = ["LW101 TG Return", "LW101 MG Return", "LW101 Face", "Main Return"]
    today = date.today()

    for day_offset in range(days):
        report_date = today - timedelta(days=day_offset)
        for loc_name in reading_locations:
            report = Report(
                report_type="gas",
                report_date=report_date,
                shift="day",
                location_id=loc_ids.get(loc_name),
                panel="LW101",
                submitted_by="Dave Mitchell",
            )
            db.add(report)
            db.flush()

            ch4 = round(random.uniform(0.05, 0.8), 2)
            co = round(random.uniform(0, 20), 1)
            o2 = round(random.uniform(19.5, 20.9), 1)

            # Occasional exceedances
            if random.random() < 0.03:
                ch4 = round(random.uniform(1.0, 1.8), 2)
            if random.random() < 0.02:
                co = round(random.uniform(30, 55), 1)

            gas = GasReading(
                report_id=report.id,
                reading_type=random.choice(["spot", "continuous", "tube_bundle"]),
                reading_location=loc_name,
                ch4_percent=ch4,
                co_ppm=co,
                co2_percent=round(random.uniform(0.03, 0.3), 2),
                o2_percent=o2,
                ch4_exceedance=ch4 >= 1.25,
                co_exceedance=co >= 50,
                o2_deficiency=o2 < 19.5,
            )
            db.add(gas)

    db.commit()


def seed_hazard_reports(db: Session, loc_ids: dict):
    """Generate hazard reports."""
    hazards = [
        ("strata", "Rib spall at shield 45-50, approximately 2m high", "medium", "possible", "high"),
        ("gas", "Elevated CH4 reading of 1.3% at TG return", "high", "unlikely", "high"),
        ("mechanical", "Hydraulic leak on shield 82 leg", "medium", "likely", "high"),
        ("electrical", "Trailing cable damage near BSL drive", "high", "possible", "extreme"),
        ("strata", "Roof sag between shields 120-125", "high", "possible", "high"),
        ("environmental", "Water make increasing from floor at CT10", "low", "likely", "medium"),
        ("mechanical", "Shearer ranging arm slow to respond", "medium", "possible", "medium"),
        ("strata", "Convergence rate increasing at TG corner", "high", "likely", "extreme"),
    ]

    today = date.today()
    for i, (h_type, desc, sev, like, risk) in enumerate(hazards):
        report = Report(
            report_type="hazard",
            report_date=today - timedelta(days=random.randint(0, 20)),
            shift=random.choice(["day", "afternoon", "night"]),
            location_id=loc_ids.get("LW101 Face"),
            panel="LW101",
            submitted_by=random.choice(["Dave Mitchell", "Steve Rogers"]),
        )
        db.add(report)
        db.flush()

        hazard = HazardReport(
            report_id=report.id,
            hazard_type=h_type,
            description=desc,
            severity=sev,
            likelihood=like,
            risk_rating=risk,
            initial_actions="Area inspected, controls implemented",
            status=random.choice(["open", "open", "in_progress", "closed"]),
        )
        db.add(hazard)

    db.commit()


def seed_strata_assessments(db: Session, loc_ids: dict, days: int = 14):
    """Generate strata convergence data with a trend."""
    today = date.today()
    base_convergence = 150.0  # mm starting point
    locations = ["LW101 Face", "LW101 Maingate", "LW101 Tailgate"]

    for loc_name in locations:
        convergence = base_convergence
        for day_offset in range(days, -1, -1):
            report_date = today - timedelta(days=day_offset)
            rate = random.uniform(0.5, 4.0)
            if loc_name == "LW101 Tailgate":
                rate += 1.5  # TG has worse conditions
            convergence += rate

            report = Report(
                report_type="strata",
                report_date=report_date,
                shift="day",
                location_id=loc_ids.get(loc_name),
                panel="LW101",
                submitted_by="Dave Mitchell",
            )
            db.add(report)
            db.flush()

            tarp = "green"
            if rate > 2:
                tarp = "amber"
            if rate > 5:
                tarp = "red"

            strata = StrataAssessment(
                report_id=report.id,
                convergence_reading=round(convergence, 1),
                convergence_rate=round(rate, 2),
                roof_condition=random.choice(["good", "good", "fair"]) if tarp == "green" else "fair" if tarp == "amber" else "poor",
                rib_condition=random.choice(["good", "fair"]),
                floor_condition="good",
                faulting_present=random.random() < 0.1,
                support_condition="adequate" if tarp != "red" else "additional_required",
                tarp_level=tarp,
            )
            db.add(strata)

    db.commit()


def seed_ventilation_readings(db: Session, loc_ids: dict, days: int = 14):
    """Generate ventilation monitoring data."""
    vent_locations = [
        ("LW101 MG Return", 2.5, 35.0),
        ("LW101 TG Return", 2.0, 28.0),
        ("Main Intake", 3.0, 50.0),
        ("Main Return", 2.8, 45.0),
    ]

    today = date.today()
    for day_offset in range(days):
        report_date = today - timedelta(days=day_offset)
        for loc_name, base_vel, base_qty in vent_locations:
            report = Report(
                report_type="ventilation",
                report_date=report_date,
                shift="day",
                location_id=loc_ids.get(loc_name),
                panel="LW101",
                submitted_by="Dave Mitchell",
            )
            db.add(report)
            db.flush()

            vent = VentilationReading(
                report_id=report.id,
                reading_location=loc_name,
                air_velocity=round(base_vel + random.uniform(-0.3, 0.3), 2),
                air_quantity=round(base_qty + random.uniform(-3, 3), 1),
                dry_bulb_temp=round(random.uniform(26, 32), 1),
                wet_bulb_temp=round(random.uniform(22, 28), 1),
                dust_reading=round(random.uniform(0.1, 2.5), 2),
                differential_pressure=round(random.uniform(50, 200), 0),
            )
            db.add(vent)

    db.commit()


def seed_incidents(db: Session, loc_ids: dict):
    """Generate a few incident reports."""
    incidents = [
        ("near_miss", "Rock fell from unsupported rib approximately 0.5m from operator", "none", "serious"),
        ("equipment_damage", "AFC chain broke during startup, debris ejected", "minor", "moderate"),
        ("injury", "Operator strained back while handling hydraulic hose", "minor", "minor"),
    ]

    today = date.today()
    for inc_type, desc, sev_actual, sev_potential in incidents:
        report = Report(
            report_type="incident",
            report_date=today - timedelta(days=random.randint(1, 25)),
            shift=random.choice(["day", "afternoon"]),
            location_id=loc_ids.get("LW101 Face"),
            panel="LW101",
            submitted_by="Craig Williams",
        )
        db.add(report)
        db.flush()

        incident = IncidentReport(
            report_id=report.id,
            incident_type=inc_type,
            description=desc,
            severity_actual=sev_actual,
            severity_potential=sev_potential,
            root_cause="Under investigation",
            notifiable=sev_potential in ("serious", "fatal"),
        )
        db.add(incident)

    db.commit()


def seed_tarp_activations(db: Session, loc_ids: dict):
    """Generate TARP activation records."""
    activations = [
        ("gas", "amber", 1.3, "CH4 at 1.3% in TG return", "Increased monitoring frequency, ventilation check"),
        ("strata", "amber", 3.5, "Convergence rate 3.5mm/day at face", "Additional support installed, monitoring increased"),
        ("strata", "red", 6.2, "Convergence rate 6.2mm/day at TG corner", "Personnel withdrawn, SSM notified, geotechnical review"),
    ]

    today = date.today()
    for tarp_type, level, value, desc, actions in activations:
        report = Report(
            report_type="tarp",
            report_date=today - timedelta(days=random.randint(0, 15)),
            shift="day",
            location_id=loc_ids.get("LW101 Face"),
            panel="LW101",
            submitted_by="Dave Mitchell",
        )
        db.add(report)
        db.flush()

        tarp = TarpActivation(
            report_id=report.id,
            tarp_type=tarp_type,
            trigger_level=level,
            trigger_value=value,
            trigger_description=desc,
            response_actions=actions,
            escalated=level == "red",
            resolved=random.random() > 0.3,
        )
        db.add(tarp)

    db.commit()


def run_seed():
    """Main seed function."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(Location).count() > 0:
            print("Database already seeded. Drop data/panel1.db to re-seed.")
            return

        print("Seeding locations...")
        loc_ids = seed_locations(db)

        print("Seeding personnel...")
        seed_personnel(db)

        print("Seeding equipment...")
        seed_equipment(db)

        print("Seeding deputy reports (30 days × 3 shifts)...")
        seed_deputy_reports(db, loc_ids, days=30)

        print("Seeding shift reports (30 days × 3 shifts)...")
        seed_shift_reports(db, loc_ids, days=30)

        print("Seeding gas readings (30 days × 4 locations)...")
        seed_gas_readings(db, loc_ids, days=30)

        print("Seeding hazard reports...")
        seed_hazard_reports(db, loc_ids)

        print("Seeding strata assessments (14 days × 3 locations)...")
        seed_strata_assessments(db, loc_ids, days=14)

        print("Seeding ventilation readings (14 days × 4 locations)...")
        seed_ventilation_readings(db, loc_ids, days=14)

        print("Seeding incidents...")
        seed_incidents(db, loc_ids)

        print("Seeding TARP activations...")
        seed_tarp_activations(db, loc_ids)

        total = db.query(Report).count()
        print(f"\nDone! Seeded {total} total reports.")
        print("Report breakdown:")
        from sqlalchemy import func
        for rtype, count in db.query(Report.report_type, func.count()).group_by(Report.report_type).all():
            print(f"  {rtype}: {count}")

    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
