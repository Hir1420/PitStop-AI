from datetime import datetime, date, time, timedelta
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.entities import Appointment, Mechanic, ServiceBay, WorkOrder, Workshop
from app.schemas.schemas import SlotOption

SERVICE_TO_SKILL_MAP = {
    "brake_service": "brakes",
    "oil_change": "general_maintenance",
    "engine_diagnostics": "diagnostics",
    "transmission_service": "transmission",
    "detailing_and_wash": "detailing",
    "suspension_and_tires": "suspension",
    "general_inspection": "general_maintenance"
}

SERVICE_TO_BAY_TYPE_MAP = {
    "brake_service": "heavy_repair",
    "oil_change": "quick_lube",
    "engine_diagnostics": "inspection",
    "transmission_service": "heavy_repair",
    "detailing_and_wash": "detailing",
    "suspension_and_tires": "heavy_repair",
    "general_inspection": "inspection"
}

def get_feasible_slots(
    db: Session,
    workshop_id: int,
    service_type: str,
    duration_minutes: int,
    target_date_str: str
) -> List[SlotOption]:
    """Computes deterministic non-conflicting appointment slots based on bay, mechanic skills, and business hours."""
    target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
    
    # 1. Fetch active mechanics with matching skills
    required_skill = SERVICE_TO_SKILL_MAP.get(service_type, "general_maintenance")
    mechanics = db.query(Mechanic).filter(
        Mechanic.workshop_id == workshop_id,
        Mechanic.active == True
    ).all()
    
    qualified_mechanics = [
        m for m in mechanics if required_skill in (m.skills or ["general_maintenance"])
    ]
    if not qualified_mechanics:
        # Fallback to all active mechanics if no exact skill filter matches
        qualified_mechanics = mechanics
        
    # 2. Fetch suitable service bays
    required_bay_type = SERVICE_TO_BAY_TYPE_MAP.get(service_type, "inspection")
    bays = db.query(ServiceBay).filter(
        ServiceBay.workshop_id == workshop_id,
        ServiceBay.active == True
    ).all()
    suitable_bays = [
        b for b in bays if required_bay_type in (b.supported_service_types or ["inspection"])
    ]
    if not suitable_bays:
        suitable_bays = bays

    if not qualified_mechanics or not suitable_bays:
        return []

    # 3. Fetch existing appointments for the day
    day_start = datetime.combine(target_date, time(0, 0, 0))
    day_end = datetime.combine(target_date, time(23, 59, 59))
    
    existing_appointments = db.query(Appointment).filter(
        Appointment.workshop_id == workshop_id,
        Appointment.status.notin_(["cancelled"]),
        Appointment.start_at >= day_start,
        Appointment.end_at <= day_end
    ).all()

    # 4. Generate candidate time slots throughout business day (e.g. 08:30 to 17:00)
    slot_hours = [
        (8, 30), (9, 30), (10, 30), (11, 30),
        (13, 0), (14, 0), (15, 0), (16, 0)
    ]
    
    feasible_slots: List[SlotOption] = []
    
    for h, m in slot_hours:
        slot_start = datetime.combine(target_date, time(h, m))
        slot_end = slot_start + timedelta(minutes=duration_minutes)
        
        # Check mechanic and bay combination
        assigned_mechanic = None
        assigned_bay = None
        conflict_found = False
        
        for mechanic in qualified_mechanics:
            # Check if mechanic is booked during this time
            mech_conflict = any(
                app.mechanic_id == mechanic.id and not (slot_end <= app.start_at or slot_start >= app.end_at)
                for app in existing_appointments
            )
            if not mech_conflict:
                assigned_mechanic = mechanic
                break
                
        for bay in suitable_bays:
            # Check if bay is booked during this time
            bay_conflict = any(
                app.bay_id == bay.id and not (slot_end <= app.start_at or slot_start >= app.end_at)
                for app in existing_appointments
            )
            if not bay_conflict:
                assigned_bay = bay
                break
                
        is_available = (assigned_mechanic is not None) and (assigned_bay is not None)
        
        if is_available:
            feasible_slots.append(SlotOption(
                start_at=slot_start.isoformat(),
                end_at=slot_end.isoformat(),
                bay_id=assigned_bay.id,
                bay_name=assigned_bay.name,
                mechanic_id=assigned_mechanic.id,
                mechanic_name=assigned_mechanic.name,
                available=True,
                reason=f"Certified for {service_type.replace('_', ' ').title()} in {assigned_bay.name}"
            ))
        else:
            # Add as unavailable slot with explanation
            fallback_bay = suitable_bays[0]
            fallback_mech = qualified_mechanics[0]
            feasible_slots.append(SlotOption(
                start_at=slot_start.isoformat(),
                end_at=slot_end.isoformat(),
                bay_id=fallback_bay.id,
                bay_name=fallback_bay.name,
                mechanic_id=fallback_mech.id,
                mechanic_name=fallback_mech.name,
                available=False,
                reason="Capacity reached: bay or qualified technician engaged with prior booking"
            ))

    return feasible_slots

def book_appointment_deterministic(
    db: Session,
    workshop_id: int,
    work_order_id: int,
    bay_id: int,
    mechanic_id: int,
    start_at: datetime,
    idempotency_key: str
) -> Tuple[Appointment, bool]:
    """Books an appointment with strict pre-validation and idempotency key safety.
    Returns (appointment, is_newly_created).
    """
    # 1. Idempotency Check
    existing_by_key = db.query(Appointment).filter(
        Appointment.idempotency_key == idempotency_key
    ).first()
    if existing_by_key:
        return existing_by_key, False

    # 2. Check if work order exists
    work_order = db.query(WorkOrder).filter(
        WorkOrder.id == work_order_id,
        WorkOrder.workshop_id == workshop_id
    ).first()
    if not work_order:
        raise ValueError(f"Work order {work_order_id} does not exist.")

    # Check if an active appointment already exists for this work order (Reschedule scenario)
    existing_for_wo = db.query(Appointment).filter(
        Appointment.work_order_id == work_order_id,
        Appointment.workshop_id == workshop_id,
        Appointment.status.notin_(["cancelled"])
    ).first()

    # 3. Revalidate slot availability
    duration = work_order.estimated_duration_minutes or 60
    end_at = start_at + timedelta(minutes=duration)

    bay_collision_query = db.query(Appointment).filter(
        Appointment.workshop_id == workshop_id,
        Appointment.bay_id == bay_id,
        Appointment.status.notin_(["cancelled"]),
        Appointment.start_at < end_at,
        Appointment.end_at > start_at
    )
    if existing_for_wo:
        bay_collision_query = bay_collision_query.filter(Appointment.id != existing_for_wo.id)
    bay_collision = bay_collision_query.first()
    if bay_collision:
        raise ValueError(f"Conflict: Service bay {bay_id} was just booked by another service. Please pick another slot.")

    mech_collision_query = db.query(Appointment).filter(
        Appointment.workshop_id == workshop_id,
        Appointment.mechanic_id == mechanic_id,
        Appointment.status.notin_(["cancelled"]),
        Appointment.start_at < end_at,
        Appointment.end_at > start_at
    )
    if existing_for_wo:
        mech_collision_query = mech_collision_query.filter(Appointment.id != existing_for_wo.id)
    mech_collision = mech_collision_query.first()
    if mech_collision:
        raise ValueError(f"Conflict: Mechanic {mechanic_id} is unavailable for this timeslot.")

    # 4. Commit or Reschedule appointment
    if existing_for_wo:
        existing_for_wo.bay_id = bay_id
        existing_for_wo.mechanic_id = mechanic_id
        existing_for_wo.start_at = start_at
        existing_for_wo.end_at = end_at
        existing_for_wo.calendar_sync_status = "pending"
        existing_for_wo.status = "confirmed"
        existing_for_wo.idempotency_key = idempotency_key
        work_order.mechanic_id = mechanic_id
        work_order.status = "scheduled"
        db.commit()
        db.refresh(existing_for_wo)
        return existing_for_wo, True

    appointment = Appointment(
        workshop_id=workshop_id,
        work_order_id=work_order_id,
        bay_id=bay_id,
        mechanic_id=mechanic_id,
        start_at=start_at,
        end_at=end_at,
        calendar_sync_status="pending",
        status="confirmed",
        idempotency_key=idempotency_key,
        created_at=datetime.utcnow()
    )
    db.add(appointment)
    
    # Update work order
    work_order.mechanic_id = mechanic_id
    work_order.status = "scheduled"
    
    db.commit()
    db.refresh(appointment)
    return appointment, True
