from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.entities import WorkOrder, ServiceRequest, Customer, Vehicle, Mechanic, Appointment, Estimate
from app.schemas.schemas import WorkOrderCreate, WorkOrderUpdate, WorkOrderResponse
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/api/work-orders", tags=["Work Orders"])

@router.post("", response_model=WorkOrderResponse)
def create_work_order(payload: WorkOrderCreate, db: Session = Depends(get_db)):
    """Converts a reviewed service request into a formal operational work order."""
    customer_id = payload.customer_id
    vehicle_id = payload.vehicle_id

    if payload.request_id:
        req = db.query(ServiceRequest).filter(ServiceRequest.id == payload.request_id).first()
        if req:
            customer_id = customer_id or req.customer_id
            vehicle_id = vehicle_id or req.vehicle_id
            req.status = "converted"

    wo = WorkOrder(
        workshop_id=payload.workshop_id,
        request_id=payload.request_id,
        customer_id=customer_id,
        vehicle_id=vehicle_id,
        mechanic_id=payload.mechanic_id,
        service_type=payload.service_type,
        status="pending_approval" if payload.mechanic_id is None else "scheduled",
        estimated_duration_minutes=payload.estimated_duration_minutes,
        customer_complaint=payload.customer_complaint,
        mechanic_notes=payload.mechanic_notes,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(wo)
    db.commit()
    db.refresh(wo)

    log_audit_event(
        db=db,
        workshop_id=payload.workshop_id,
        action="work_order_created",
        entity_type="work_order",
        entity_id=str(wo.id),
        actor_id="service_advisor",
        actor_role="coordinator",
        metadata={
            "service_type": wo.service_type,
            "request_id": payload.request_id,
            "estimated_duration": wo.estimated_duration_minutes
        }
    )

    return wo

@router.get("", response_model=List[WorkOrderResponse])
def list_work_orders(
    workshop_id: int = 1,
    status: Optional[str] = None,
    mechanic_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(WorkOrder).filter(WorkOrder.workshop_id == workshop_id)
    if status:
        query = query.filter(WorkOrder.status == status)
    if mechanic_id:
        query = query.filter(WorkOrder.mechanic_id == mechanic_id)
    return query.order_by(WorkOrder.created_at.desc()).all()

@router.get("/{work_order_id}")
def get_work_order_detail(work_order_id: int, db: Session = Depends(get_db)):
    wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")

    customer = db.query(Customer).filter(Customer.id == wo.customer_id).first() if wo.customer_id else None
    vehicle = db.query(Vehicle).filter(Vehicle.id == wo.vehicle_id).first() if wo.vehicle_id else None
    mechanic = db.query(Mechanic).filter(Mechanic.id == wo.mechanic_id).first() if wo.mechanic_id else None
    appointment = db.query(Appointment).filter(Appointment.work_order_id == wo.id).first()
    estimate = db.query(Estimate).filter(Estimate.work_order_id == wo.id).first()

    return {
        "id": wo.id,
        "workshop_id": wo.workshop_id,
        "request_id": wo.request_id,
        "service_type": wo.service_type,
        "status": wo.status,
        "estimated_duration_minutes": wo.estimated_duration_minutes,
        "actual_duration_minutes": wo.actual_duration_minutes,
        "customer_complaint": wo.customer_complaint,
        "mechanic_notes": wo.mechanic_notes,
        "created_at": wo.created_at,
        "updated_at": wo.updated_at,
        "customer": {"name": customer.name, "phone": customer.phone, "email": customer.email} if customer else None,
        "vehicle": {"make": vehicle.make, "model": vehicle.model, "year": vehicle.year} if vehicle else None,
        "mechanic": {"id": mechanic.id, "name": mechanic.name, "skills": mechanic.skills} if mechanic else None,
        "appointment": {
            "id": appointment.id,
            "start_at": appointment.start_at,
            "end_at": appointment.end_at,
            "status": appointment.status,
            "calendar_sync_status": appointment.calendar_sync_status,
            "bay_id": appointment.bay_id
        } if appointment else None,
        "estimate": {
            "id": estimate.id,
            "grand_total": estimate.grand_total,
            "status": estimate.status,
            "approver_name": estimate.approver_name,
            "line_items": estimate.line_items
        } if estimate else None
    }

@router.patch("/{work_order_id}", response_model=WorkOrderResponse)
def update_work_order(work_order_id: int, payload: WorkOrderUpdate, db: Session = Depends(get_db)):
    wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")

    old_status = wo.status
    if payload.status:
        wo.status = payload.status
    if payload.mechanic_id is not None:
        wo.mechanic_id = payload.mechanic_id
    if payload.mechanic_notes is not None:
        wo.mechanic_notes = payload.mechanic_notes
    if payload.actual_duration_minutes is not None:
        wo.actual_duration_minutes = payload.actual_duration_minutes

    wo.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(wo)

    if wo.status == "completed" and wo.customer_id:
        customer = db.query(Customer).filter(Customer.id == wo.customer_id).first()
        if customer and customer.email:
            from app.services.email_service import dispatch_transactional_email
            dispatch_transactional_email(
                db=db,
                recipient_email=customer.email,
                subject=f"Vehicle Ready for Pickup: Work Order #{wo.id}",
                headline=f"Your {wo.service_type.replace('_', ' ').title()} is Complete!",
                body_text="All service and quality inspection items have been successfully completed. You may collect your vehicle at our workshop during normal business hours.",
                notification_type="vehicle_ready",
                customer_id=customer.id,
                badge_label="Ready for Pickup",
                highlight_text=f"Technician Notes: {wo.mechanic_notes or 'All mechanical inspection points verified.'}"
            )

    log_audit_event(
        db=db,
        workshop_id=wo.workshop_id,
        action="work_order_updated",
        entity_type="work_order",
        entity_id=str(wo.id),
        actor_id="technician_or_advisor",
        actor_role="mechanic",
        metadata={
            "old_status": old_status,
            "new_status": wo.status,
            "mechanic_id": wo.mechanic_id
        }
    )

    return wo
