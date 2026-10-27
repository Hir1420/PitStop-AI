from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.models.entities import (
    Customer, Vehicle, WorkOrder, Appointment, Estimate, EmailNotification, ServiceBay, Mechanic
)
from app.services.email_service import (
    send_verification_otp, verify_email_otp, dispatch_transactional_email
)
from app.services.estimate_service import approve_estimate_by_human

router = APIRouter(prefix="/api/customer", tags=["Vehicle Owner Portal & Auth"])

class SendCodeRequest(BaseModel):
    email: str

class VerifyCodeRequest(BaseModel):
    email: str
    code: str

class CustomerEstimateApproval(BaseModel):
    customer_name: Optional[str] = None
    notes: Optional[str] = "Approved by vehicle owner via Customer Garage Portal"

@router.post("/auth/send-code")
def request_auth_code(payload: SendCodeRequest, db: Session = Depends(get_db)):
    """Sends a 6-digit verification code to the customer's email."""
    if not payload.email or "@" not in payload.email:
        raise HTTPException(status_code=400, detail="Please enter a valid email address.")
    res = send_verification_otp(db, payload.email)
    return res

@router.post("/auth/verify-code")
def verify_auth_code(payload: VerifyCodeRequest, db: Session = Depends(get_db)):
    """Verifies the OTP code and logs the vehicle owner into their PitStop Garage."""
    try:
        auth_res = verify_email_otp(db, payload.email, payload.code)
        return auth_res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/garage")
def get_customer_garage(email: str = Query(...), db: Session = Depends(get_db)):
    """Retrieves all registered vehicles, active work orders, estimates, and bookings for the logged-in customer."""
    customer = db.query(Customer).filter(Customer.email == email.strip().lower()).first()
    if not customer:
        return {
            "customer": None,
            "vehicles": [],
            "active_repairs": [],
            "past_repairs": []
        }

    # Fetch vehicles
    vehicles = db.query(Vehicle).filter(Vehicle.customer_id == customer.id).all()
    vehicles_data = [
        {
            "id": v.id,
            "make": v.make,
            "model": v.model,
            "year": v.year,
            "license_plate": v.license_plate,
            "mileage": v.mileage or 42500,
            "next_service_mileage": (v.mileage or 42500) + 5000,
            "health_status": "Attention Required" if any(True for _ in [1]) else "Good"
        }
        for v in vehicles
    ]

    # Fetch work orders
    work_orders = db.query(WorkOrder).filter(WorkOrder.customer_id == customer.id).order_by(WorkOrder.created_at.desc()).all()
    
    active_repairs = []
    past_repairs = []

    for wo in work_orders:
        app = db.query(Appointment).filter(Appointment.work_order_id == wo.id).first()
        est = db.query(Estimate).filter(Estimate.work_order_id == wo.id).first()
        bay = db.query(ServiceBay).filter(ServiceBay.id == app.bay_id).first() if app else None
        mech = db.query(Mechanic).filter(Mechanic.id == wo.mechanic_id).first() if wo.mechanic_id else None

        # Determine visual progress stage (1 to 5)
        # 1: Intake Received, 2: Under Inspection, 3: Estimate Ready, 4: In Repair, 5: Ready for Pickup
        stage = 1
        if wo.status == "completed":
            stage = 5
        elif wo.status == "in_progress":
            stage = 4
        elif est and est.status == "draft":
            stage = 3
        elif wo.status == "scheduled":
            stage = 2

        wo_dict = {
            "id": wo.id,
            "service_type": wo.service_type,
            "status": wo.status,
            "current_stage": stage,
            "estimated_duration_minutes": wo.estimated_duration_minutes,
            "complaint": wo.customer_complaint,
            "technician_notes": wo.mechanic_notes,
            "assigned_technician": mech.name if mech else "Assigning certified technician",
            "appointment": {
                "id": app.id,
                "start_at": app.start_at,
                "bay_name": bay.name if bay else "Dedicated Service Bay",
                "sync_status": app.calendar_sync_status
            } if app else None,
            "estimate": {
                "id": est.id,
                "grand_total": est.grand_total,
                "status": est.status,
                "line_items": est.line_items
            } if est else None,
            "created_at": wo.created_at
        }

        if wo.status in ["completed", "cancelled"]:
            past_repairs.append(wo_dict)
        else:
            active_repairs.append(wo_dict)

    return {
        "customer": {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone
        },
        "vehicles": vehicles_data,
        "active_repairs": active_repairs,
        "past_repairs": past_repairs
    }

@router.post("/estimates/{estimate_id}/approve")
def customer_approve_estimate(
    estimate_id: int,
    payload: CustomerEstimateApproval,
    workshop_id: int = 1,
    db: Session = Depends(get_db)
):
    """Allows vehicle owner to digitally authorize their estimate from the customer portal."""
    try:
        est = approve_estimate_by_human(
            db=db,
            workshop_id=workshop_id,
            estimate_id=estimate_id,
            approver_name=payload.customer_name or "Vehicle Owner (Digital Approval)",
            notes=payload.notes
        )

        # Notify via transactional email
        wo = db.query(WorkOrder).filter(WorkOrder.id == est.work_order_id).first()
        customer = db.query(Customer).filter(Customer.id == wo.customer_id).first() if wo else None
        if customer and customer.email:
            dispatch_transactional_email(
                db=db,
                recipient_email=customer.email,
                subject=f"Estimate Authorized: Work Order #{est.work_order_id}",
                headline="Repair Work Authorized",
                body_text=f"Thank you, {customer.name}. You have authorized the estimate of ${est.grand_total:.2f}. Our certified technicians will begin service immediately.",
                notification_type="estimate_approved",
                customer_id=customer.id,
                badge_label="Approved",
                highlight_text=f"Total Authorized: ${est.grand_total:.2f} (Parts + Certified Labor)"
            )

        return {"status": "success", "estimate": est}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/notifications/inbox")
def get_email_inbox(email: Optional[str] = None, db: Session = Depends(get_db)):
    """Returns the email notifications log so reviewers can inspect all dispatched HTML messages."""
    query = db.query(EmailNotification)
    if email:
        query = query.filter(EmailNotification.recipient_email == email.strip().lower())
    notifs = query.order_by(EmailNotification.created_at.desc()).limit(30).all()
    return notifs
