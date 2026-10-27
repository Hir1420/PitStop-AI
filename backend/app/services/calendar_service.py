import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.entities import Appointment, IntegrationEvent, AutomationJob
from app.services.audit_service import log_audit_event
from app.config import settings

def sync_appointment_to_calendar(
    db: Session,
    workshop_id: int,
    appointment_id: int,
    force_failure: bool = False
) -> Dict[str, Any]:
    """Synchronizes appointment to Google Calendar or simulated provider with retry recording."""
    app = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.workshop_id == workshop_id
    ).first()
    if not app:
        raise ValueError(f"Appointment {appointment_id} not found.")

    if force_failure:
        # Simulate network timeout / 503 Service Unavailable for demonstration
        app.calendar_sync_status = "failed"
        
        event = IntegrationEvent(
            workshop_id=workshop_id,
            provider="google_calendar",
            operation="create_event",
            external_reference=None,
            status="failed",
            attempts=1,
            last_error="503 Service Unavailable: Remote calendar endpoint timed out.",
            created_at=datetime.utcnow()
        )
        db.add(event)

        # Queue bounded retry automation job
        retry_job = AutomationJob(
            workshop_id=workshop_id,
            job_type="calendar_retry",
            payload={"appointment_id": appointment_id, "retry_count": 1},
            status="pending",
            attempts=1,
            last_error_code="503_TIMEOUT",
            last_error_message="Remote calendar endpoint timed out.",
            created_at=datetime.utcnow()
        )
        db.add(retry_job)
        db.commit()

        log_audit_event(
            db=db,
            workshop_id=workshop_id,
            action="calendar_sync_failed",
            entity_type="appointment",
            entity_id=str(appointment_id),
            actor_id="system",
            metadata={"reason": "503 Service Unavailable (Injected failure scenario)"}
        )

        return {
            "success": False,
            "status": "failed",
            "message": "Calendar synchronization failed. Automated retry job queued.",
            "retry_job_id": retry_job.id
        }

    # Successful synchronization
    event_id = f"gcal_event_{uuid.uuid4().hex[:12]}"
    app.calendar_event_id = event_id
    app.calendar_sync_status = "synced"

    event = IntegrationEvent(
        workshop_id=workshop_id,
        provider="google_calendar",
        operation="create_event",
        external_reference=event_id,
        status="success",
        attempts=1,
        last_error=None,
        created_at=datetime.utcnow()
    )
    db.add(event)
    db.commit()

    log_audit_event(
        db=db,
        workshop_id=workshop_id,
        action="calendar_sync_succeeded",
        entity_type="appointment",
        entity_id=str(appointment_id),
        actor_id="system",
        metadata={"calendar_event_id": event_id}
    )

    return {
        "success": True,
        "status": "synced",
        "calendar_event_id": event_id,
        "message": "Appointment successfully synchronized with Google Calendar."
    }
