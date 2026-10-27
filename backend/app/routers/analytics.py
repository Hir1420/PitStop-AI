from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, time
from app.database import get_db
from app.models.entities import (
    ServiceRequest, WorkOrder, Appointment, Part, Estimate, AuditEvent, ServiceBay
)
from app.schemas.schemas import AnalyticsSummaryResponse

router = APIRouter(prefix="/api/analytics", tags=["Analytics & Reporting"])

@router.get("/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary(workshop_id: int = 1, db: Session = Depends(get_db)):
    """Computes comprehensive live operational metrics from persisted database records."""
    total_requests = db.query(ServiceRequest).filter(ServiceRequest.workshop_id == workshop_id).count()
    pending_requests = db.query(ServiceRequest).filter(
        ServiceRequest.workshop_id == workshop_id,
        ServiceRequest.status.in_(["under_review", "clarification_needed"])
    ).count()
    safety_escalations = db.query(ServiceRequest).filter(
        ServiceRequest.workshop_id == workshop_id,
        ServiceRequest.safety_escalation == True
    ).count()

    active_wo = db.query(WorkOrder).filter(
        WorkOrder.workshop_id == workshop_id,
        WorkOrder.status.in_(["scheduled", "in_progress", "awaiting_parts"])
    ).count()
    completed_wo = db.query(WorkOrder).filter(
        WorkOrder.workshop_id == workshop_id,
        WorkOrder.status == "completed"
    ).count()

    # Appointments scheduled for today
    today = datetime.utcnow().date()
    day_start = datetime.combine(today, time(0, 0, 0))
    day_end = datetime.combine(today, time(23, 59, 59))
    scheduled_today = db.query(Appointment).filter(
        Appointment.workshop_id == workshop_id,
        Appointment.start_at >= day_start,
        Appointment.end_at <= day_end,
        Appointment.status != "cancelled"
    ).count()

    # Bay utilization: active appointments today vs total bay slots (approx 8 slots per bay per day)
    total_bays = max(1, db.query(ServiceBay).filter(ServiceBay.workshop_id == workshop_id, ServiceBay.active == True).count())
    max_slots_today = total_bays * 8
    bay_utilization = round(min(1.0, scheduled_today / max_slots_today) * 100, 1)

    # Low stock parts
    low_stock = db.query(Part).filter(
        Part.workshop_id == workshop_id,
        Part.quantity_on_hand <= Part.reorder_threshold
    ).count()

    # Revenues
    total_est_rev = db.query(func.sum(Estimate.grand_total)).filter(
        Estimate.workshop_id == workshop_id
    ).scalar() or 0.0

    total_app_rev = db.query(func.sum(Estimate.grand_total)).filter(
        Estimate.workshop_id == workshop_id,
        Estimate.status == "approved"
    ).scalar() or 0.0

    audit_count = db.query(AuditEvent).filter(AuditEvent.workshop_id == workshop_id).count()

    return AnalyticsSummaryResponse(
        total_service_requests=total_requests,
        pending_review_requests=pending_requests,
        safety_escalations_count=safety_escalations,
        active_work_orders=active_wo,
        completed_work_orders=completed_wo,
        scheduled_appointments_today=scheduled_today,
        bay_utilization_rate=bay_utilization,
        low_stock_parts_count=low_stock,
        total_estimated_revenue=round(float(total_est_rev), 2),
        total_approved_revenue=round(float(total_app_rev), 2),
        audit_events_count=audit_count
    )
