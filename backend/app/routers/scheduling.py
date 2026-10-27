from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models.entities import Appointment, ServiceBay, Mechanic, WorkOrder
from app.schemas.schemas import SlotOption, AppointmentBookingRequest, AppointmentResponse
from app.services.scheduling_service import get_feasible_slots, book_appointment_deterministic
from app.services.calendar_service import sync_appointment_to_calendar
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="", tags=["Scheduling & Availability"])

@router.get("/api/availability", response_model=List[SlotOption])
def check_availability(
    workshop_id: int = 1,
    service_type: str = "brake_service",
    duration_minutes: int = 60,
    target_date: str = Query(..., description="Date YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """Calculates deterministic feasible appointment slots with capacity, skills, and bay validation."""
    slots = get_feasible_slots(
        db=db,
        workshop_id=workshop_id,
        service_type=service_type,
        duration_minutes=duration_minutes,
        target_date_str=target_date
    )
    return slots

@router.post("/api/appointments/confirm", response_model=AppointmentResponse)
def confirm_appointment_booking(
    payload: AppointmentBookingRequest,
    db: Session = Depends(get_db)
):
    """Explicitly confirms and commits an appointment slot with idempotency protection and calendar sync."""
    try:
        appointment, is_new = book_appointment_deterministic(
            db=db,
            workshop_id=payload.workshop_id,
            work_order_id=payload.work_order_id,
            bay_id=payload.bay_id,
            mechanic_id=payload.mechanic_id,
            start_at=payload.start_at,
            idempotency_key=payload.idempotency_key
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Booking error: {str(e)}")

    if is_new:
        # Trigger background calendar sync
        sync_res = sync_appointment_to_calendar(
            db=db,
            workshop_id=payload.workshop_id,
            appointment_id=appointment.id,
            force_failure=False
        )
        appointment.calendar_sync_status = sync_res.get("status", "synced")

        # Dispatch confirmation email to customer
        wo = db.query(WorkOrder).filter(WorkOrder.id == payload.work_order_id).first()
        from app.models.entities import Customer
        customer = db.query(Customer).filter(Customer.id == wo.customer_id).first() if wo and wo.customer_id else None
        if customer and customer.email:
            from app.services.email_service import dispatch_transactional_email
            dispatch_transactional_email(
                db=db,
                recipient_email=customer.email,
                subject=f"Appointment Confirmed: Work Order #{payload.work_order_id}",
                headline="Your Service Appointment is Confirmed!",
                body_text=f"Your appointment is set for {appointment.start_at.strftime('%A, %B %d at %I:%M %p')}. Our technicians will have your service bay prepared.",
                notification_type="appointment_confirmed",
                customer_id=customer.id,
                badge_label="Confirmed",
                highlight_text=f"Scheduled Time: {appointment.start_at.strftime('%Y-%m-%d %H:%M')} (Calendar Event Synced)"
            )

        log_audit_event(
            db=db,
            workshop_id=payload.workshop_id,
            action="appointment_booked_and_confirmed",
            entity_type="appointment",
            entity_id=str(appointment.id),
            actor_id="customer_or_coordinator",
            actor_role="coordinator",
            correlation_id=payload.idempotency_key,
            metadata={
                "work_order_id": payload.work_order_id,
                "bay_id": payload.bay_id,
                "mechanic_id": payload.mechanic_id,
                "start_at": payload.start_at.isoformat()
            }
        )

    return appointment

@router.get("/api/appointments")
def list_appointments(workshop_id: int = 1, db: Session = Depends(get_db)):
    apps = db.query(Appointment).filter(
        Appointment.workshop_id == workshop_id
    ).order_by(Appointment.start_at.asc()).all()
    
    results = []
    for a in apps:
        bay = db.query(ServiceBay).filter(ServiceBay.id == a.bay_id).first()
        mech = db.query(Mechanic).filter(Mechanic.id == a.mechanic_id).first()
        wo = db.query(WorkOrder).filter(WorkOrder.id == a.work_order_id).first()
        results.append({
            "id": a.id,
            "work_order_id": a.work_order_id,
            "service_type": wo.service_type if wo else "Unknown",
            "start_at": a.start_at,
            "end_at": a.end_at,
            "bay_id": a.bay_id,
            "bay_name": bay.name if bay else f"Bay #{a.bay_id}",
            "mechanic_id": a.mechanic_id,
            "mechanic_name": mech.name if mech else f"Mechanic #{a.mechanic_id}",
            "calendar_event_id": a.calendar_event_id,
            "calendar_sync_status": a.calendar_sync_status,
            "status": a.status,
            "idempotency_key": a.idempotency_key
        })
    return results
