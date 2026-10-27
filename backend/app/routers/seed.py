from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models.entities import (
    Workshop, User, Customer, Vehicle, Mechanic, ServiceBay, Part,
    ServiceRequest, WorkOrder, Appointment, Estimate
)
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/api/seed", tags=["Demo Seeding"])

@router.post("")
def seed_database(db: Session = Depends(get_db)):
    """Seeds rich demonstration data including workshop, bays, certified technicians, inventory, and sample requests."""
    # 1. Workshop
    workshop = db.query(Workshop).filter(Workshop.id == 1).first()
    if not workshop:
        workshop = Workshop(
            id=1,
            name="PitStop Apex Workshop",
            timezone="America/Los_Angeles",
            hourly_labor_rate=95.0,
            created_at=datetime.utcnow()
        )
        db.add(workshop)
        db.commit()

    # 2. Staff Users & Mechanics
    mechanics_data = [
        {"name": "Marcus Vance", "skills": ["brakes", "suspension", "general_maintenance"]},
        {"name": "Sarah Chen", "skills": ["engine", "diagnostics", "general_maintenance"]},
        {"name": "Dave Miller", "skills": ["transmission", "heavy_repair", "brakes"]},
        {"name": "Elena Rostova", "skills": ["detailing", "quick_lube", "general_maintenance"]}
    ]
    for m_info in mechanics_data:
        existing_m = db.query(Mechanic).filter(Mechanic.workshop_id == 1, Mechanic.name == m_info["name"]).first()
        if not existing_m:
            m = Mechanic(
                workshop_id=1,
                name=m_info["name"],
                skills=m_info["skills"],
                active=True
            )
            db.add(m)

    # 3. Service Bays
    bays_data = [
        {"name": "Bay 1 - Heavy Hydraulic Lift", "types": ["heavy_repair", "brakes", "transmission"]},
        {"name": "Bay 2 - Precision Alignment & OBD Bay", "types": ["diagnostics", "suspension", "inspection"]},
        {"name": "Bay 3 - Express Lube & Fluids", "types": ["quick_lube", "general_maintenance"]},
        {"name": "Bay 4 - Detailing & Ceramic Studio", "types": ["detailing", "wash"]}
    ]
    for b_info in bays_data:
        existing_b = db.query(ServiceBay).filter(ServiceBay.workshop_id == 1, ServiceBay.name == b_info["name"]).first()
        if not existing_b:
            b = ServiceBay(
                workshop_id=1,
                name=b_info["name"],
                supported_service_types=b_info["types"],
                active=True
            )
            db.add(b)

    # 4. Parts Inventory
    parts_data = [
        {"sku": "BRK-PAD-01", "name": "Premium Ceramic Front Brake Pads", "category": "brakes", "qty": 14, "thresh": 5, "cost": 42.0, "price": 85.0},
        {"sku": "BRK-ROT-02", "name": "Vented Front Brake Rotors (Pair)", "category": "brakes", "qty": 6, "thresh": 4, "cost": 75.0, "price": 160.0},
        {"sku": "BRK-FLD-01", "name": "DOT4 High-Temp Brake Fluid (1L)", "category": "brakes", "qty": 2, "thresh": 5, "cost": 12.0, "price": 28.0}, # Low stock
        {"sku": "OIL-SYN-5W30", "name": "Full Synthetic 5W-30 Motor Oil (5 Qt)", "category": "maintenance", "qty": 28, "thresh": 8, "cost": 24.0, "price": 55.0},
        {"sku": "OIL-FLT-OEM", "name": "OEM Specification Spin-On Oil Filter", "category": "maintenance", "qty": 22, "thresh": 6, "cost": 6.5, "price": 18.0},
        {"sku": "ENG-SPK-IRID", "name": "Laser Iridium Spark Plugs (Set of 4)", "category": "engine", "qty": 3, "thresh": 4, "cost": 36.0, "price": 80.0}, # Low stock
        {"sku": "TRN-ATF-VI", "name": "Dexron VI Synthetic Transmission Fluid (4 Qt)", "category": "transmission", "qty": 12, "thresh": 4, "cost": 38.0, "price": 75.0},
        {"sku": "DET-CERAM-PRO", "name": "9H Ceramic Shield Coating Bottle", "category": "detailing", "qty": 8, "thresh": 3, "cost": 45.0, "price": 120.0}
    ]
    for p_info in parts_data:
        existing_p = db.query(Part).filter(Part.workshop_id == 1, Part.sku == p_info["sku"]).first()
        if not existing_p:
            p = Part(
                workshop_id=1,
                sku=p_info["sku"],
                name=p_info["name"],
                category=p_info["category"],
                quantity_on_hand=p_info["qty"],
                reorder_threshold=p_info["thresh"],
                unit_cost=p_info["cost"],
                unit_price=p_info["price"],
                created_at=datetime.utcnow()
            )
            db.add(p)

    db.commit()

    # 5. Sample Customer & Vehicle
    cust = db.query(Customer).filter(Customer.name == "Alex Mercer").first()
    if not cust:
        cust = Customer(
            workshop_id=1,
            name="Alex Mercer",
            phone="415-555-0199",
            email="alex.mercer@example.com"
        )
        db.add(cust)
        db.commit()
        db.refresh(cust)

        veh = Vehicle(
            workshop_id=1,
            customer_id=cust.id,
            make="Toyota",
            model="Camry",
            year=2021,
            license_plate="7XYZ890",
            mileage=42500
        )
        db.add(veh)
        db.commit()
        db.refresh(veh)

        # Seed the exact demonstration scenario from SRS Section 18
        req = ServiceRequest(
            workshop_id=1,
            customer_id=cust.id,
            vehicle_id=veh.id,
            original_message="Hi PitStop, my 2021 Toyota Camry has a weird grinding noise when I hit the brakes, and the pedal feels a little spongy today. Can I bring it in tomorrow morning?",
            structured_intake={
                "vehicle_make": "Toyota",
                "vehicle_model": "Camry",
                "vehicle_year": 2021,
                "symptoms": ["Brake grinding noise when slowing down", "Spongy brake pedal feel"],
                "proposed_service_type": "brake_service",
                "estimated_duration_minutes": 90,
                "urgency": "safety_critical",
                "safety_escalation": True,
                "safety_advisory": "SAFETY ADVISORY: The reported brake noise and spongy pedal indicate potential brake system degradation. Escalated for certified mechanic safety inspection.",
                "missing_fields": [],
                "clarification_questions": [
                    "Does the spongy sensation worsen at higher speeds or when pressing hard?"
                ],
                "recommended_parts": ["Premium Ceramic Front Brake Pads", "DOT4 High-Temp Brake Fluid (1L)"],
                "ai_confidence_score": 0.98,
                "ai_summary": "Intake for 2021 Toyota Camry indicating urgent Brake Service. Safety escalation active due to pedal loss."
            },
            priority="safety_critical",
            safety_escalation=True,
            status="under_review",
            created_at=datetime.utcnow()
        )
        db.add(req)
        db.commit()

        log_audit_event(
            db=db,
            workshop_id=1,
            action="seed_demonstration_scenario_loaded",
            entity_type="system",
            entity_id="init",
            actor_id="demo_seeder",
            actor_role="manager",
            metadata={"sample_request_id": req.id}
        )

    return {"status": "success", "message": "PitStop AI database successfully seeded with workshop operational data."}
